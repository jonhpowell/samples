import sys
import traceback

from io import BytesIO
from gzip import GzipFile

import boto3
from botocore.exceptions import ClientError

from RecordFilters import *
from RecordProjections import *
from RecordTransforms import *

'''
Pull AWS S3 LME data and transform using simple Python record processor functions.

You may need to add your AWS secrets into your runtime environment to access S3.

Directions:
    a. Specify transformer (S3MetricsRecordTransform.X), filter (RecordFilters) and
        projector (RecordProjections) for S3RecordExtractor ctor.
    b. Specify data type and start/end dates on S3RecordExtractor.get_files -- see __main__ below.

'''

# TODO: read_s3_gzip_file() limitations, returns WHOLE file, nicer to chunk/stream it
# Limitation: only does range of dates, not pure timestamps due to S3 data partitioning and wildcard structure.
#   Could overcome by just getting ALL data spanned by dates or by post-filtering
#

class S3RecordExtractor(Exception):

    ROOT_BUCKET = 'oscar-ai-kubernetes'  # root bucket for LME data

    base_path = 'control-2.dev.us-west.trebuchet.ai/kafka-archive/raw_logs/partitioned/'
    types_to_location = {
        'events_v0': base_path + 'events.v0',
        'logs': base_path + 'logs',
        'metrics': base_path + 'metrics'
    }
    root_bucket = None
    data_type = None
    record_xform_func = None
    record_filter_func = None
    record_projector_func = None

    def __init__(self, data_type='metrics',
                 record_xform_func=RecordTransforms.pass_thru,
                 record_filter_func=RecordFilters.pass_thru,
                 record_projector_func=RecordProjections.pass_thru):
        self.s3 = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        self.root_bucket = self.s3_resource.Bucket(self.ROOT_BUCKET)

        self.data_type = data_type
        self.record_xform_func = record_xform_func
        self.record_filter_func = record_filter_func
        self.record_projector_func = record_projector_func

    def filter_for_date(self, data_location, date):
        date_as_str = "{y:02d}-{m:02d}-{d:02d}".format(y=date.year, m=date.month, d=date.day)
        filter_path = "/".join([data_location, date_as_str]) + "/"
        return filter_path

    def get_files(self, start_date, end_date):

        print('Retrieving S3 JSON {t} records from {s} to {e}:\n'.format(t=self.data_type, s=start_date, e=end_date))

        data_location = self.types_to_location.get(self.data_type, None)
        if not data_location:
            raise ValueError("Must supply supported data type: " + str(self.types_to_location.keys()))
        if start_date > end_date:
            raise ValueError("start_date ({s}) must be < end_date ({e})".format(s=start_date, e=end_date))

        # s3 time-partitioned key = /2017-12-08/14/45'  # date, hour, minute
        # can we use wildcards?

        date = start_date
        while date <= end_date:
            filter_path = self.filter_for_date(data_location, date)
            #print('date={d}: {f}'.format(d=date, f=filter_path))
            self.get_files_by_path(filter_path)
            date += dt.timedelta(days=1)
        return

    def process_line(self, line):
        #print("IN Line {}: {}".format(cnt, line.strip()))
        json_data = json.loads(line)
        proc_data = self.record_xform_func(json_data)
        #print("OUT Line {}: {}".format(cnt, proc_data))
        for rec in proc_data:
            if self.record_filter_func(rec):
                print(self.record_projector_func(rec))
        #pprint(proc_data)

    def process_file_lines(self, file_text):
        count = 0
        for line in file_text.splitlines():
            self.process_line(line)
            count += 1

    # better if chunked/streamed instead of entire file
    def read_s3_gzip_file(self, object_key):
        obj = self.s3.get_object(Bucket=self.ROOT_BUCKET, Key=object_key)
        bytestream = BytesIO(obj['Body'].read())
        return GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')

    def get_files_by_path(self, filter_path):

        bucket_objects = self.root_bucket.objects.filter(Prefix=filter_path)  # if blank prefix is given, return everything)

        #print('For path "{p}" files are:'.format(p=(self.ROOT_BUCKET + '/' + filter_path)))
        count = 0
        total_length = 0.0
        for object in bucket_objects:
            #abbrev_filename = object.key[len(filter_path):]
            abbrev_filename = object.key[len(self.base_path):]
            count += 1
            if count > 100:
                break
            try:
                file_text = self.read_s3_gzip_file(object.key)
                self.process_file_lines(file_text)
                length = len(file_text)/(1024.0*1024.0)
                total_length += length
                #print('{0}:gz_file {1} ({2:.2f} MiB unpacked)'.format(count, abbrev_filename, length))
                #print('{0}:gz_file {1}'.format(count, abbrev_filename))
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object '{o}' does not exist.".format(o=object.key))
                else:
                    traceback.print_exc()
            except Exception as ex:
                print('Exception reading S3 file "{f}": {e}'.format(f=object.key, e=str(ex)))
                traceback.print_exc()
                sys.exit(1)
        #print('Total length: {l} MiB'.format(l=total_length))

# move get_files 1st parm to CTOR

#import transforms.RecordTransforms.RecordTransforms as Transforms


if __name__ == '__main__':

    # specify record transformer, filter and projector
    m_xform = RecordTransforms.metric_simple_flatten
    m_filter = RecordFilters.include_telgraf_logfs_hydra_record
    m_projection = RecordProjections.hydra_memory_usage_vs_pod_to_csv
    extractor = S3RecordExtractor('metrics', m_xform, m_filter, m_projection)

#    e_xform = RecordTransforms.event_simple_flatten
#    e_filter = RecordFilters.include_user_service_record
#    e_projection = RecordProjections.user_service_created_email_to_csv
#    extractor = S3RecordExtractor('events_v0', e_xform, e_filter, e_projection)

#    l_xform = RecordTransforms.log_simple_flatten
#    l_filter = RecordFilters.log_stream_stderr_record
#    l_projection = RecordProjections.log_stderr_timestamp_message_to_psv
#    extractor = S3RecordExtractor('logs', l_xform, l_filter, l_projection)

    # process data in date range per Record Extractor parms...
    start_date_utc = dt.date(2017, 12, 9)
    end_date_utc = dt.date(2017, 12, 10)
    extractor.get_files(start_date_utc, end_date_utc)

