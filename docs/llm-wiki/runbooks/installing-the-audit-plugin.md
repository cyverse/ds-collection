---
type: Runbook
title: Installing the Audit Plugin
description: Manual procedure for auditing Data Store activity — OpenSearch in Docker, AMQP 1.0 on the RabbitMQ broker, a Logstash pipeline from RabbitMQ to OpenSearch, and the iRODS audit_amqp rule engine plugin on the catalog provider.
resource: /docs/install-audit.md
tags: [audit, opensearch, logstash, rabbitmq, amqp, irods, rule-engine-plugin]
timestamp: 2026-09-17T00:00:00Z
---

This procedure wires iRODS policy enforcement point (PEP) events into
OpenSearch: the iRODS audit plugin publishes to the broker's `irods` exchange
with topic `audit`, Logstash consumes them from RabbitMQ, and Logstash indexes
them into daily `irods-audit-YYYY.MM.dd` indexes. It is a manual procedure; no
playbook in the collection performs it. Shell variables such as
`$RABBITMQ_HOST`, `$DS_VHOST`, and the various usernames and passwords are
placeholders to fill in.

## 1. Install OpenSearch

For a native installation, the doc says OpenSearch needs Ubuntu 20.04.

1. Install Docker from Docker's apt repository:

   ```bash
   sudo apt install ca-certificates curl gnupg
   sudo install --directory --mode=0755 /etc/apt/keyrings
   curl --fail --location --show-error --silent https://download.docker.com/linux/ubuntu/gpg \
     | sudo gpg --dearmor --output /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   printf \
       'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu %s stable\n' \
       "$(dpkg --print-architecture)" \
       "$(. /etc/os-release && echo "$VERSION_CODENAME")" \
     | sudo tee /etc/apt/sources.list.d/docker.list \
     > /dev/null
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

2. Prepare the host: disable swap and raise `vm.max_map_count`:

   ```bash
   sudo swapoff --all
   echo vm.max_map_count=262144 | sudo tee --append /etc/sysctl.conf > /dev/null
   sudo sysctl --load
   ```

3. Fetch OpenSearch's all-in-one compose file and start it:

   ```bash
   wget \
     https://raw.githubusercontent.com/opensearch-project/documentation-website/2.9/assets/examples/docker-compose.yml
   sudo docker compose up --detach
   ```

## 2. Enable AMQP 1.0 on the Data Store broker

On the RabbitMQ host (see [AMQP Broker](/components/amqp-broker.md)):

```bash
sudo rabbitmq-plugins enable rabbitmq_amqp1_0

cat <<EOF | sudo tee --append /etc/rabbitmq/rabbitmq.conf > /dev/null
amqp1_0.default_vhost = $DS_VHOST
amqp1_0.convert_app_props_to_amqp091_headers = true
EOF

sudo systemctl restart rabbitmq-server
```

## 3. Install Logstash

1. Add Elastic's apt repository and install Logstash with the OpenSearch
   output and RabbitMQ input plugins:

   ```bash
   curl --fail --location --show-error --silent https://artifacts.elastic.co/GPG-KEY-elasticsearch \
     | sudo gpg --dearmor --output /usr/share/keyrings/elastic-keyring.gpg
   sudo apt install apt-transport-https
   echo \
       'deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' \
     | sudo tee --append /etc/apt/sources.list.d/elastic-8.x.list \
     > /dev/null
   sudo apt update
   sudo apt install logstash
   sudo /usr/share/logstash/bin/logstash-plugin install \
     logstash-output-opensearch logstash-input-rabbitmq
   ```

2. Write the pipeline to `/etc/logstash/conf.d/irods.conf`. It reads the
   `irods` exchange with routing key `audit` from `$DS_VHOST`, strips the AMQP
   1.0 header, parses the JSON message, takes `@timestamp` from the message's
   `@timestamp` (epoch milliseconds), converts `file_size`, `data_size`, and
   nameless `int`/`int__N` fields to integers, drops `ERROR`/`ERROR__N` fields,
   and writes to OpenSearch:

   ```
   input {
      rabbitmq {
         host => "$RABBITMQ_HOST"
         vhost => "$DS_VHOST"
         user => "$LOGSTASH_RABBITMQ_USERNAME"
         password => "$LOGSTASH_RABBITMQ_PASSWORD"
         exchange => "irods"
         key => "audit"
         codec => plain { charset => "ISO-8859-1" }
      }
   }

   filter {
      mutate { gsub => [ "message", "[^{]*(.*)", "\1" ] }
      json {
         source => "message"
         target => "message"
      }
      date { match => [ "[message][@timestamp]", "UNIX_MS" ] }
      mutate {
         convert => {
            "[message][file_size]" => "integer"
            "[message][data_size]" => "integer"
         }
      }
      ruby {
         code => '
            event.get("message").to_hash.each { |k, v|
               if ( k =~ /^int(__[0-9]+)?$/ )
                  event.set("[message][" + k + "]", v.to_i)
               elsif ( k =~ /^ERROR(__[0-9]+)?$/ )
                  event.remove("[message][" + k + "]")
               end
            }
         '
      }
   }

   output {
      opensearch {
         hosts => [ "https://${OPENSEARCH_HOST}:9200" ]
         user => "$LOGSTASH_OPENSEARCH_USERNAME"
         password => "$LOGSTASH_OPENSEARCH_PASSWORD"
         index => "irods-audit-%{+YYYY.MM.dd}"
      }
   }
   ```

   The original doc carries a TODO to verify which fields need integer
   conversion for iRODS 4.3.1. It writes the file with
   `sudo cat <<EOF | tee /etc/logstash/conf.d/irods.conf`, which runs `tee`
   without root; use `sudo tee` instead.

3. Start it:

   ```bash
   sudo systemctl enable logstash
   sudo systemctl start logstash
   ```

## 4. Add the audit plugin to the catalog service provider

On the [iRODS catalog service provider](/components/irods-catalog-provider.md):

1. Install the plugin:

   ```bash
   sudo apt install irods_rule-engine-plugin-audit-amqp
   ```

2. Prepend its configuration to the rule engine list in
   `/etc/irods/server_config.json`:

   ```bash
   jq --from-file /dev/stdin /etc/irods/server_config.json \
   <<JQ | sudo sponge /etc/irods/server_config.json
   .plugin_configuration.rule_engines =
      [
         {
            instance_name: "irods_rule_engine_plugin-audit_amqp-instance",
            plugin_name: "irods_rule_engine_plugin-audit_amqp",
            plugin_specific_configuration : {
               amqp_location:
                  "amqp://$IRODS_RABBITMQ_USERNAME:$IRODS_RABBITMQ_PASSWORD@$RABBITMQ_HOST:5672",
               amqp_topic: "/exchange/irods/audit",
               pep_regex_to_match: "pep_.+"
            }
         }
      ]
      + .plugin_configuration.rule_engines
   JQ
   ```

3. Restart iRODS:

   ```bash
   sudo systemctl restart irods
   ```

`server_config.json` is generated by the
[irods_cfg](/ansible-roles/irods-cfg.md) role, whose template emits only the
`irods_rule_language` and `cpp_default_policy` rule engines. Running a
playbook that applies the role (for example
[irods_catalog_provider](/ansible-playbooks/irods-catalog-provider.md) or
[irods_cfg](/ansible-playbooks/irods-cfg.md)) would therefore drop the
hand-added audit plugin entry.

# Citations

[1] `docs/install-audit.md` — the original procedure.
[2] `roles/irods_cfg/templates/server_config.json.j2`, `roles/irods_cfg/templates/macros.j2` — template that generates `server_config.json` and its rule engine list.
