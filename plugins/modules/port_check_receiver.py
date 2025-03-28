#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An ansible module for listening on a set of ports. It's meant to work in
# tandem with port_check_sender to verify network routes are open.
#
# Module Name:
#  port_check_receiver
#
# Optional Variables:
#  tcp_ports     a list of TCP ports to listen on, default is []
#  udp_ports     a list of UDP ports to listen on, default is []
#  stop_command  the message to send the service to tell it to stop, default
#                'finished'
#  timeout       the number of seconds to wait before exiting, default is 300
#
# This module is meant to work with the port_check_sender module to check if a
# set of TCP and/or UDP ports on the host running port_check_receiver are
# reachable from a host running port_check_sender. It starts a service that
# listens on the set of ports on all interfaces. When it receives the
# stop_command message it stops listening and exits. When it receives any other
# message, it responds with 'pong'. If the message came over a TCP connection,
# it closes the connection.


import select
import socket
import struct
import traceback

from ansible.module_utils.basic import AnsibleModule


class SocketSet:

  def __init__(self):
    self.inputs = []
    self.outputs = []
    self.messengers = []

  def add_input(self, input):
    if input not in self.inputs:
      self.inputs.append(input)
    self.remove_messenger(input)
    self.remove_output(input)

  def add_messenger(self, messenger):
    if messenger not in self.messengers:
      self.messengers.append(messenger)
    self.remove_input(messenger)
    self.remove_output(messenger)

  def add_output(self, output):
    if output not in self.outputs:
      self.outputs.append(output)
    self.remove_input(output)
    self.remove_messenger(output)

  def closeall(self):
    for s in self.inputs + self.outputs + self.messengers:
      s.close()

  def get_messengers(self):
    return self.messengers

  def has_inputs(self):
    return self.inputs

  def remove(self, sock):
    self.remove_input(sock)
    self.remove_messenger(sock)
    self.remove_output(sock)

  def remove_input(self, input):
    if input in self.inputs:
      self.inputs.remove(input)

  def remove_messenger(self, messenger):
    if messenger in self.messengers:
      self.messengers.remove(messenger)

  def remove_output(self, output):
    if output in self.outputs:
      self.outputs.remove(output)

  def select(self, timeout):
    return select.select(self.inputs, self.outputs, self.inputs, timeout)


class TCPConnection:

  def __init__(self, sock):
    self._sock, _ = sock.accept()
    self._sock.setblocking(0)

  def close(self):
    self._sock.close()

  def fileno(self):
    return self._sock.fileno()

  def transition_readable(self, states):
    states.add_messenger(self)

  def transition_messenger(self, states):
    data = self._sock.recv(128)
    self._sock.send(b'pong')
    states.add_output(self)
    return data

  def transition_writable(self, states):
    states.remove_output(self)

  def transition_exceptional(self, states):
    self._sock.close()
    states.remove(self)


class TCPSocket(socket.socket):

  def __init__(self, port):
    super(TCPSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
    self.setblocking(0)
    self.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
    self.bind(("0.0.0.0", port))
    self.listen(5)

  def close(self):
    self.shutdown(socket.SHUT_RDWR)
    super(TCPSocket, self).close()

  def transition_readable(self, states):
    states.add_input(TCPConnection(self))

  def transition_exceptional(self, states):
    states.remove(self)
    self.close()


class UDPSocket(socket.socket):

  def __init__(self, port):
    super(UDPSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM)
    self.setblocking(0)
    self.bind(("0.0.0.0", port))

  def transition_readable(self, states):
    states.add_messenger(self)

  def transition_messenger(self, states):
    data, sender = self.recvfrom(128)
    self.sendto(b'pong', sender)
    states.add_input(self)
    return data

  def transition_exceptional(self, states):
    states.remove(self)
    self.close()


def receive(tcp_ports, udp_ports, stop_command, timeout):
  try:
    failures = []
    socks = SocketSet()

    for port in tcp_ports:
      try:
        socks.add_input(TCPSocket(port))
      except OSError:
        failures.append("port %s/tcp already in use" % (port))

    for port in udp_ports:
      try:
        socks.add_input(UDPSocket(port))
      except OSError:
        failures.append("port %s/tcp already in use" % (port))

    tearDown = bool(failures) or not socks.has_inputs()

    while not tearDown:
      readable, writable, exceptional = socks.select(timeout)

      if readable + writable + exceptional:
        for r in readable:
          r.transition_readable(socks)

        for w in writable:
          w.transition_writable(socks)

        for e in exceptional:
          e.transition_exceptional(socks)

        for m in socks.get_messengers():
          msg = m.transition_messenger(socks).decode('utf-8')
          if  msg == stop_command:
            tearDown = True

        if not socks.has_inputs():
          tearDown = True
      else:
        failures.append("receiver: timed out")
        tearDown = True

    socks.closeall()
    return failures
  except:
    return ["Unexpected error:"] + traceback.format_exc().splitlines()


def main():
  module_args = dict(
    tcp_ports = dict(type='list', default=[]),
    udp_ports = dict(type='list', default=[]),
    stop_command = dict(type='str', default="finished"),
    timeout = dict(type='int', default=300) )

  module = AnsibleModule(argument_spec=module_args)

  tcp_ports = module.params['tcp_ports']
  udp_ports = module.params['udp_ports']
  stop_command = module.params['stop_command']
  timeout = module.params['timeout']
  failures = receive(tcp_ports, udp_ports, stop_command, timeout)

  if failures:
    module.fail_json(msg='\n'.join(failures))
  else:
    module.exit_json()


if __name__ == '__main__':
  main()
