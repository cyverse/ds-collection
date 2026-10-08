FROM ubuntu:22.04

RUN apt update && \
	apt upgrade --yes && \
	apt install --yes systemd

# systemd skips some units that would act on the host only when this is set; systemd.sh masks the
# rest.
ENV container=docker

# Molecule builds from the scenario directory, which can't reach systemd.sh, so the template embeds
# it.
RUN echo '{{ lookup("file", molecule_scenario_directory ~ "/../../testing/env/base/systemd.sh") | b64encode }}' | base64 --decode > /tmp/systemd.sh \
	&& bash /tmp/systemd.sh \
	&& rm /tmp/systemd.sh

CMD [ "/lib/systemd/systemd" ]
