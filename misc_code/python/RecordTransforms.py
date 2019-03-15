import datetime as dt
import json


class RecordTransforms(Exception):
    '''
    S3 Logs/Metrics/Events record transform functions
    All transforms take a dictionary and return transformed [dictionary]
    '''

    @staticmethod
    def entry_to_timestamp(dict, name):
        millis = dict.get(name, 0)
        return dt.datetime.fromtimestamp(millis).isoformat()

    @staticmethod
    def event_simple_flatten(dict_in):
        # flatten and retain only info needed for in-depth events V0 analysis
        data_as_dict = json.loads(dict_in.get('data', '{}'))
        dict_out = {
            'customerID': dict_in.get('customerID', 'unknown'),
            'service': dict_in.get('service', 'unknown'),

            'appid': data_as_dict.get('appid', ''),
            'correlationid': data_as_dict.get('correlationid', ''),
            'created': data_as_dict.get('created', 0),
            'data': data_as_dict.get('data', {}),
            'instanceid': data_as_dict.get('instanceid', ''),
            'type': data_as_dict.get('type', '')
        }
        return [dict_out]

    @staticmethod
    def log_simple_flatten(dict_in):
        # flatten and retain only info needed for in-depth metrics analysis
        data_as_dict = json.loads(dict_in.get('data', '{}'))
#        if 'message' in data_as_dict:

        message = data_as_dict.get('message', '{}')
        message_dict = json.loads(message) if '{' in message and '}' in message else {}  # watch malformed
        dict_out = {
            'customerID': dict_in.get('customerID', 'unknown'),
            'service': dict_in.get('service', 'unknown'),

            'cluster': data_as_dict.get('cluster', 'unknown'),
            'hostname': data_as_dict.get('hostname', 'unknown'),
            'log_timestamp': message_dict.get('time', '0'),
            'log_stream': message_dict.get('stream', ''),
            'log_message': message_dict.get('log', ''),
            'source': data_as_dict.get('source', ''),
            'tenant': data_as_dict.get('tenant', ''),
            'type': data_as_dict.get('type', '')
        }
        return [dict_out]


    @staticmethod
    def metric_simple_hierarchical(dict_in):
        dict_out = {
            'customerID': dict_in.get('customerID', 'unknown'),
            'service': dict_in.get('service', 'unknown'),
            'when_created': RecordTransforms.entry_to_timestamp(dict_in, 'createdTimestamp'),
            'when_arrived': RecordTransforms.entry_to_timestamp(dict_in, 'arrivalTimestamp'),
            'data': json.loads(dict_in['data'])
        }
        for elem in dict_out['data']:
            elem['timestamp'] = RecordTransforms.entry_to_timestamp(elem, 'timestamp')  # only need to xform this element; others ok
        return [dict_out]

    @staticmethod
    def metric_simple_flatten(dict_in):
        # flatten and retain only info needed for in-depth metrics analysis
        out = []
        dict_template = {
            'customerID': dict_in.get('customerID', 'unknown'),
            'service': dict_in.get('service', 'unknown')
        }
        for elem in json.loads(dict_in['data']):
            dict_out = dict_template.copy()
            dict_out['metric'] = elem.get('metric', 'unknown')
            dict_out['timestamp'] = RecordTransforms.entry_to_timestamp(elem, 'timestamp')
            dict_out['value'] = elem.get('value', 'unknown')
            dict_out['tags'] = elem.get('tags', None)
            out.append(dict_out)
        return out

    @staticmethod
    def pass_thru(dict_in):
        return dict_in
