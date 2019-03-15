#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import time
import os
import pprint
import logging
import json

# AWS Athena DAL

# TODO:
#
#   - watch out for multi-threading on requests
#   - need to limit concurrent queries (limits to 1 being submitted and 5 concurrent running per acct?)
#   - consider trying waiter and get_signed_url methods

"""
    Encapsulates possible AWS Athena exceptions.
"""


class AthenaDalException(Exception):
    def __init__(self, message, http_code):
        self.message = message
        self.http_code = http_code

    def __str__(self):
        return 'AthenaDalException occurred: Message="{m}", original http code={h}'.format(m=self.message, h=self.http_code)


"""
    Provides an API to query and get status and results from AWS Athena.
"""


class AthenaDAL(object):

    log = logging.getLogger(__name__)

    def __init__(self):

        # AWS env: trying to make it run in the same role locally as in production (under 'data_history_viewer_role')

        self.region = os.getenv("ATHENA_REGION", 'us-east-1')
        self.database = os.getenv("ATHENA_DATABASE", 'trebuchet_event_logs')
        self.s3_output_path = os.getenv("ATHENA_S3_OUTPUT_PATH", 's3://aws-athena-query-results-293135079892-us-east-1/')  # from us-east-1 Athena console Settings

        self.session = boto3.session.Session()  # new session per client thread (enables multi-threading)

        self.athena = self.session.client('athena', region_name=self.region)
        self.log.info('Initialized boto3 Athena client: %s', self.athena)

        self.glue = self.session.client('glue', region_name=self.region)
        self.log.debug('Initialized boto3 Glue client: %s', self.glue)

    def run_query(self, query):
        """
            Run the query, returning a unique queryId that is used for subsequent get_status and next requests.
        :param query: the SQL to be run on Athena
        :return: query_id that uniquely identifies this request
        """
        if not self._safe_query(query):
            raise AthenaDalException("Disallowed. Query does select from allowed tables (events_v0, metrics).", 400)

        try:
            res = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': self.database
                    },
                ResultConfiguration={
                    'OutputLocation': self.s3_output_path,
                    }
                )
            self.log.info('Athena query execution ID: %s', res['QueryExecutionId'])
            return res
        except ClientError as ce:
            raise AthenaDalException(ce.response, 400)

    def _safe_query(self, query):
        """
            Examine query to prevent SQL injection threats, etc.
            Look at table names after 'FROM' in SQL
        """
        return True


    def get_job_status(self, job_id):
        """
            Get the status of the query job. 'FINISHED' means it completed and results are ready.
        :param job_id: the unique id received upon the initial Athena submission
        :return: status as a string. Includes at least 'RUNNING', 'SUCCEEDED', 'FAILED' and possibly others.
        """

        try:
            res = self.athena.batch_get_query_execution(
                QueryExecutionIds=[job_id, ]
            )
            self.log.debug('For execution ID: {e}, status response={r}'.format(e=job_id, r=res))
            qexec = res['QueryExecutions'][0]
            qstat = qexec.get('Status', {})
            state = qstat.get('State', 'UNKNOWN')
            reason = qstat.get('StateChangeReason', '')
            query = qexec.get('Query', '?')
            self.log.debug('For query_id: %s for query "%s", state=%s, reason=%s', job_id, query, state, reason)
            if state == 'FAILED':
                message = "Failure getting status for query_id '{r}', query '{q}': status={s}, error='{e}'"\
                    .format(r=job_id, q=query, s=status, e=reason)
                raise AthenaDalException(message, 400)
            self.log.info('For execution ID: %s, status state/reason=%s/%s', job_id, state, reason)
            return state
        except ClientError as ce:
            message = "Client exception for request '{r}' query '{q}': status={s}, exception='{e}'" \
                .format(r=job_id, q=query, s=status, e=ce.response)
            raise AthenaDalException(message, 400)


    def get_query_results(self, job_id, results_per_request, paging_last_token):
        """
        Get the results of the Athena query in chunks of requests_per_result.
        :param job_id: the unique id received upon the initial Athena submission
        :param results_per_request: how many rows per request
        :param paging_last_token: previous token result set place-marker from last time that marks where this request resumes (not yet implemented)
        :return: result set of results_per_request rows

        Note: Athena max results_per_request is 1K
        """

        try:
            if paging_last_token is None:
                resp = self.athena.get_query_results(
                    QueryExecutionId=job_id,
                    MaxResults=results_per_request
                )
            else:
                resp = self.athena.get_query_results(
                    QueryExecutionId=job_id,
                    NextToken=paging_last_token,
                    MaxResults=results_per_request
                )
            next_token = resp.get('NextToken')
            raw_result_set = resp.get('ResultSet', {}).get('Rows')
            return self.build_results_json(raw_result_set, paging_last_token is None), next_token
        except ClientError as ce:
            raise self._build_results_exception(ce.response)


    def build_results_json(self, raw_res, have_headers):
        """
        Dynamically adjusts to number of columns and converts Athena results to a more classic JSON
        :param raw_res: raw JSON result set from Athena
        :param have_headers true if will have headers (first record, first time)
        :return:
        """
        json_id = "columns" if have_headers else "data"
        processed_rows = []
        for data_elem in raw_res:
            row = data_elem.get('Data')
            col_values = []
            for column in row:
                col_values.append(column.get('VarCharValue'))
            processed_rows.append({json_id: col_values})
            json_id = "data"
        return json.dumps(processed_rows)

    @staticmethod
    def _build_results_exception(resp):
        request = resp.get('ResponseMetadata', {}).get('RequestId')
        http = resp.get('ResponseMetadata', {}).get('HTTPStatusCode')
        code = resp.get('Error', {}).get('Code')
        err_msg = resp.get('Error', {}).get('Message')
        message = "Client exception for results request '{r}': code={c}, http_status={h}, message='{m}'".format(r=request, c=code, h=http, m=err_msg)
        return AthenaDalException(message, http)

    def get_databases(self):
        resp = self.glue.get_databases()
        return resp

    def get_tables(self):
        resp = self.glue.get_tables()
        return resp

    @staticmethod
    def _submit_query(query):
        response = dal.run_query(query)
        job_id = response['QueryExecutionId']
        print('job_id for Athena DAL query "{i}"= "{r}"'.format(i=query, r=job_id))
        return job_id


if __name__ == '__main__':

    dal = AthenaDAL()
    #query = 'select customerid, servicename, createdtimestamp, data from events_v0 LIMIT 11;'
    query = 'SELECT customerid, service, createdtimestamp, arrivaltimestamp, data FROM "trebuchet_event_logs"."metrics" limit 10;'
    #initial_query = 'select customerid, servicename, createdtimestamp, data from metrics LIMIT 5;'

    try:
        job_ids = []
        for x in range(0, 1):
            job_id = dal._submit_query(query)
            job_ids.append(job_id)

        databases = dal.get_databases()
        print('Glue databases: {d}'.format(d=databases))

        status = 'RUNNING'
        while status == 'RUNNING':
            status = dal.get_job_status(job_ids[0])
            print('Status of Athena DAL query job "{j}"={s}'.format(s=status, j=job_ids[0]))
            if status == 'RUNNING':
                time.sleep(0.1)
            else:
                print('Exiting busy loop for job {j} with status {s}'.format(s=status, j=job_id[0]))

        if status != 'FAILED':
            pp = pprint.PrettyPrinter()
            next_token = None
            while True:
                query_results, next_token = dal.get_query_results(job_ids[0], 5, next_token)
                #print('Results for job {j}: {r}'.format(j=job_ids[0], r=query_results))
                #pp.pprint(query_results)
                print("\nRESULTS:\n" + "" if query_results is None else pp.pprint(query_results))
                print("\nNEXT_TOKEN: " + ("None" if next_token is None else next_token))
                if next_token is None:
                    break
    except AthenaDalException as ade:
            print('Exception occurred: ' + str(ade))


