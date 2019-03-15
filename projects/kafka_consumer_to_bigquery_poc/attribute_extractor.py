"""
Extract attributes from Kafka message payload, depending on tenant
"""

import json
import time_utils


def extract_attributes(entity_label, check_label):
    first_per_idx = entity_label.find('.')
    tenant = entity_label[first_per_idx + 1:]

    pre_per_str = entity_label[:first_per_idx] if first_per_idx != -1 else entity_label
    dash_tokens = pre_per_str.split('-')
    environ = dash_tokens[1] if len(dash_tokens) > 1 else tenant
    node = dash_tokens[0] if len(dash_tokens) > 0 else environ
    if len(dash_tokens) > 2 and len(dash_tokens[2]) > 0:
        environ += '-' + dash_tokens[2][0]
        node += dash_tokens[2][1:]

    first_ddash_idx = check_label.find("--")
    check = check_label[:first_ddash_idx] if first_ddash_idx != -1 else check_label
#        print('Labels (entity,check): ({e},{c})'.format(e=entity_label, c=check_label))
#        print('tenant={t},environ={e},node={n},check={c}'.format(t=tenant, e=environ, n=node, c=check))
    return tenant, environ, node, check

def summarize_fields(msg):
    fields = json.loads(msg)
    details = fields.get('details')
    alarm_label = fields.get('alarm', {}).get('label', 'NO_ALARM_LABEL')
    alarm_ddash_idx = alarm_label.find("--")
    entity_label = fields.get('entity', {}).get('label', 'NO_ENTITY_LABEL')
    check_label = fields.get('check', {}).get('label', 'NO_CHECK_LABEL')
    (tenant, environ, node, check) = extract_attributes(entity_label, check_label)
    tenant_id = fields.get('tenantId', 'NO_TENANT_ID')
    return tenant, {
        'tenant': tenant_id,
#            'tenant': tenant,
        'environ': environ,
        'node': node,
        'check': check,
        'timestamp': time_utils.micro_sec_to_std_time(details.get('timestamp', 0)),
        'state': details.get('state', 'NO_STATE'),
        'alarm': alarm_label[:alarm_ddash_idx]
    }


