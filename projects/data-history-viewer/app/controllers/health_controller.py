from app.models.health_status import HealthStatus


def get_health():
    """
    Returns the health of the service
    Returns information about the health of the service.

    :rtype: HealthStatus
    """
    resp = { 
        "healthy": "green",
        "message": "OK"
    }   

    return resp

