# Copyright Security Onion Solutions LLC and/or licensed to Security Onion Solutions LLC under one
# or more contributor license agreements. Licensed under the Elastic License 2.0 as shown at 
# https://securityonion.net/license; you may not use this file except in compliance with the
# Elastic License 2.0.

{% from 'kafka/map.jinja' import KAFKAMERGED %}
{% from 'vars/globals.map.jinja' import GLOBALS %}

include:
{# Run kafka/nodes.sls before Kafka is enabled, so kafka nodes pillar is setup #}
{% if grains.role in ['so-manager','so-managersearch', 'so-standalone'] %}
  - kafka.nodes
{% endif %}
{% if GLOBALS.pipeline == "KAFKA" and KAFKAMERGED.enabled %}
  - kafka.enabled
{% else %}
  - kafka.disabled
{% endif %}
