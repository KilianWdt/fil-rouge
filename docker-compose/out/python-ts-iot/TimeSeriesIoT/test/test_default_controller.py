# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from TimeSeriesIoT.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_mean_sensor_id_get(self):
        """Test case for mean_sensor_id_get

        Calculer la moyenne d'un capteur entre deux dates
        """
        query_string = [('start_date', 56),
                        ('end_date', 56)]
        response = self.client.open(
            '/v1/mean/{sensorId}'.format(sensor_id='sensor_id_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
