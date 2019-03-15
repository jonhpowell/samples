# coding: utf-8

from __future__ import absolute_import
from . import BaseTestCase


class TestHealthController(BaseTestCase):
    """ HealthController integration test stubs """

    def test_get_health(self):
        """
        Test case for get_health

        Returns the health of the service
        """
        response = self.client.open('/v0/lme_hist/healthcheck',
                                    method='GET',
                                    content_type='application/json')
        #print('Health response={r}'.format(r=response.data.decode('utf-8')))
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
