import connexion
import logging as logger

from app.athena_dal import AthenaDAL
from app.models.error_response import ErrorResponse
from app.models.query_configuration import QueryConfiguration
from app.models.query_id import QueryId
from ..util import add_tenant_id

import http.client as http_client

@add_tenant_id
def query(queryconfig=None, X_TREBUCHET_TENANT_ID=None):
    """
    Submit the Athena SQL query
    
    :param X_TREBUCHET_TENANT_ID: 
    :type X_TREBUCHET_TENANT_ID: str
    :param query_config: query configuration
    :type query_config: dict | bytes

    :rtype: QueryId
    """

    http_client.HTTPConnection.debuglevel = 1

    # to get more detailed logging
#    logger.basicConfig()
#    logger.getLogger().setLevel(logger.DEBUG)
#    requests_log = logger.getLogger("requests.packages.urllib3")
#    requests_log.setLevel(logger.DEBUG)
#    requests_log.propagate = True

    log = logger.getLogger(__name__)

#    requests_log.info('$$$$$ request.get_json=' + str(connexion.request.get_json()))

    if connexion.request.is_json:
        query_config = QueryConfiguration.from_dict(connexion.request.get_json())
        # TODO: query_config.retention_minutes -- where is expiration handled???
        try:
            dal = AthenaDAL()
            query_res = dal.run_query(query_config.sql_query)
            query_id = query_res['QueryExecutionId']
            message = 'For query({q}, {t})="{i}"'.format(q=query_config.sql_query, t=X_TREBUCHET_TENANT_ID, i=query_id)
            log.info(message)
            return query_id
        except Exception as ex:
            return ErrorResponse('Trouble initiating query "{q}", X_TREBUCHET_TENANT_ID="{t}": {e}'
                                 .format(q=query_config.sql_query, t=X_TREBUCHET_TENANT_ID, e=ex))
