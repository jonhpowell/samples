# coding: utf-8

from __future__ import absolute_import

from app.models.query_configuration import QueryConfiguration
from app.models.query_next_request import QueryNextRequest
from . import BaseTestCase
from flask import json
import time
import pprint
import re


class TestAllControllers(BaseTestCase):
    """ QueryController integration tests: run this to check everything """

    headers = [('X_TREBUCHET_TENANT_ID', 'X_TREBUCHET_TENANT_ID_example')]

    def _submit_query(self, query):
        query_config = QueryConfiguration(sql_query=query, retention_minutes=1000)
        response = self.client.open('/v0/lme_hist/query',
                                    method='POST',
                                    data=json.dumps(query_config),
                                    headers=self.headers,
                                    content_type='application/json')
        resp = response.data.decode('utf-8')
        query_id = re.sub('[\'\"\n]', '', resp)
        #print("### query submission response body is : " + query_id)
        self.assert200(response, "Submit response body is : " + resp)
        return query_id

    def _get_status(self, query_id):
        response = self.client.open('/v0/lme_hist/status/{queryId}'.format(queryId=query_id),
                                    method='GET',
                                    headers=self.headers,
                                    content_type='application/json')
        resp = response.data.decode('utf-8')
        #print("###get_status Response body is : " + resp)
        self.assert200(response, "Status response body is : " + resp)
        status = re.sub('[^A-Z]', '', resp)   # dangerous
        return status

    def _get_next(self, query_id, res_per_req, next_token):
        """
        Test case for get_next

        Iterator to get v0 event query result set in chunks given an Athena SQL query
        """
        next_request = QueryNextRequest(query_id=query_id, results_per_request=res_per_req, next_token=next_token)
        headers = [('X_TREBUCHET_TENANT_ID', 'X_TREBUCHET_TENANT_ID_example')]
        response = self.client.open('/v0/lme_hist/next',
                                    method='POST',
                                    data=json.dumps(next_request),
                                    headers=headers,
                                    content_type='application/json')
        print("###get_next response body is : " + response.data.decode('utf-8'))
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        return response

    def test_all(self):
        """
        Test case for query, status & getting results, the sample Use Case

        """
        sql_query = "select * from events_v0 LIMIT 15;"
        query_id = self._submit_query(sql_query)
        print('+++Job id for Athena query "{q}"={j}'.format(q=sql_query, j=query_id))
        print('+++ query_id={i}'.format(i=query_id))
        status = 'RUNNING'
        while status == 'RUNNING':
            status = self._get_status(query_id)
            print('+++Status of Athena DAL query job "{j}"={s}'.format(s=status, j=query_id))
            if status == 'RUNNING':
                time.sleep(0.1)
            else:
                print('Exiting busy loop for job {j} with status {s}'.format(s=status, j=query_id))

        pp = pprint.PrettyPrinter()
        res_per_req = 10
        next_token = None
        page = 1
        while True:
            resp = self._get_next(query_id, res_per_req, next_token)
            json = resp.json
            result_set = json['result_set']
            next_token = json.get('next_token', None)

            # print('Results for job {j}: {r}'.format(j=job_ids[0], r=query_results))
            # pp.pprint(query_results)
            print("\nPage {p} RESULTS:\n".format(p=page))
            print("" if result_set is None else pp.pprint(result_set))
            print("\nPage {p} NEXT_TOKEN: ".format(p=page))
            print("None (token)" if next_token is None else next_token)
            if next_token is None:
                break
            page += 1


if __name__ == '__main__':
    import unittest
    unittest.main()
