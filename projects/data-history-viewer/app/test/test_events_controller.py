# coding: utf-8

from __future__ import absolute_import

from app.models.query_next_request import QueryNextRequest
from . import BaseTestCase
from flask import json


class TestEventsController(BaseTestCase):
    """ EventsController integration test stubs """

    def test_get_next(self):
        """
        Test case for get_next

        Iterator to get v0 event query result set in chunks given an Athena SQL query
        """
        next_request = QueryNextRequest()
        next_request.query_id = '8ea2dbf1-4956-44e5-be73-f4db846f6e04'
        next_request.results_per_request = 100
        next_request.next_token = None
        headers = [('X_TREBUCHET_TENANT_ID', 'X_TREBUCHET_TENANT_ID_example')]
        print("### data={d}".format(d=json.dumps(next_request)))
        response = self.client.open('/v0/lme_hist/next',
                                    method='POST',
                                    data=json.dumps(next_request),
                                    headers=headers,
                                    content_type='application/json')
        print("###get_next response body is : " + response.data.decode('utf-8'))
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
