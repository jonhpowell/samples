import connexion
import logging as logger
from app.athena_dal import AthenaDAL
from app.models.error_response import ErrorResponse
from app.models.query_next_request import QueryNextRequest
from app.models.query_next_response import QueryNextResponse
from ..util import add_tenant_id


@add_tenant_id
def get_next(next_request=None, X_TREBUCHET_TENANT_ID=None):
    """
    Iterator to get v0 event query result set in chunks given an Athena SQL query
    
    :param X_TREBUCHET_TENANT_ID: 
    :type X_TREBUCHET_TENANT_ID: str
    :param next_request: query results chunk get specifier
    :type next_request: dict | bytes

    :rtype: QueryNextResponse
    """

    log = logger.getLogger(__name__)

    query_id = "unknown"
    try:
        dal = AthenaDAL()
        if connexion.request.is_json:
            query_next_req = QueryNextRequest.from_dict(connexion.request.get_json())
            query_id = query_next_req.query_id
            next_tok = query_next_req.next_token
            res_per_req = query_next_req.results_per_request
            result_set, next_token = dal.get_query_results(query_id, res_per_req, next_tok)
            log.info('get_next(%s, %s, %s)=%s', query_next_req.query_id, X_TREBUCHET_TENANT_ID, next_tok, result_set)
            return QueryNextResponse(result_set=result_set, next_token=next_token)
        else:
            return ErrorResponse('Exception getting query results for X_TREBUCHET_TENANT_ID="{t}": request is not JSON!'
                                 .format(t=X_TREBUCHET_TENANT_ID))
    except Exception as ex:
        return ErrorResponse('Exception getting query results for queryId="{q}", X_TREBUCHET_TENANT_ID="{t}": {e}'
                             .format(q=query_id, t=X_TREBUCHET_TENANT_ID, e=ex))

