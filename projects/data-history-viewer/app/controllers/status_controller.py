import connexion
import logging as logger
from app.athena_dal import AthenaDAL
from app.models.error_response import ErrorResponse
from app.models.query_status import QueryStatus
from ..util import add_tenant_id


@add_tenant_id
def get_status(queryId, X_TREBUCHET_TENANT_ID=None):
    """
    get status of submitted Athena SQL query
    poll using this method until status == 'FINISHED';
    :param queryId: Returned query id from initial query call
    :type queryId: str
    :param X_TREBUCHET_TENANT_ID: 
    :type X_TREBUCHET_TENANT_ID: str

    :rtype: QueryStatus
    """

    log = logger.getLogger(__name__)
    try:
        dal = AthenaDAL()
        stat = dal.get_job_status(queryId)
        log.info('get_status(%s, %s)=%s', queryId, X_TREBUCHET_TENANT_ID, stat)
        return QueryStatus().from_dict({"status": stat})
    except Exception as ex:  # TODO: improve error handling with perhaps connexion custom exception
        return ErrorResponse('Trouble getting query status for queryId="{q}", X_TREBUCHET_TENANT_ID="{t}": {e}'
                             .format(q=queryId, t=X_TREBUCHET_TENANT_ID, e=ex))
