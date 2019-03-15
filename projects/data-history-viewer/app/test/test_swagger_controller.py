# coding: utf-8

from __future__ import absolute_import
from . import BaseTestCase


class TestSwaggerController(BaseTestCase):
    """ SwaggerController integration test stubs """

    def test_get_swagger(self):
        """
        Test case for get_swagger

        Returns the swagger specification file
        """
        response = self.client.open('/v0/lme_hist/swagger',
                                    method='GET',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
