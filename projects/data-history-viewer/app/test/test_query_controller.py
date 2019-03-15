# coding: utf-8

from __future__ import absolute_import

from app.models.query_configuration import QueryConfiguration
from . import BaseTestCase
from flask import json


class TestQueryController(BaseTestCase):
    """ QueryController integration test stubs """

    def test_query(self):
        """
        Test case for query

        Submit the Athena SQL query
        """
        query_config = QueryConfiguration(sql_query="select * from events_v0 LIMIT 100;", retention_minutes=1000)
        headers = [('X_TREBUCHET_TENANT_ID', 'X_TREBUCHET_TENANT_ID_example')]
        response = self.client.open('/v0/lme_hist/query',
                                    method='POST',
                                    data=json.dumps(query_config),
                                    headers=headers,
                                    content_type='application/json')
        print("### query response body is : " + response.data.decode('utf-8'))
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
