# coding: utf-8

from __future__ import absolute_import
from . import BaseTestCase


class TestStatusController(BaseTestCase):
    """ StatusController integration test stubs """

    def test_get_status(self):
        """
        Test case for get_status

        get status of submitted Athena SQL query
        """
        headers = [('X_TREBUCHET_TENANT_ID', 'X_TREBUCHET_TENANT_ID_example')]
        response = self.client.open('/v0/lme_hist/status/{queryId}'.format(queryId='1b901b2d-0649-4c4f-9727-a3d7238b9d3a'),
                                    method='GET',
                                    headers=headers,
                                    content_type='application/json')
        print("###get_status Response body is : " + response.data.decode('utf-8'))
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
