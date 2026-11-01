import logging

from fastapi.responses import JSONResponse

from src.expections.service import ServiceError

logger = logging.getLogger(__name__)


def service_error_response(error: Exception) -> JSONResponse:
    """Return the API's standard successful-transport error envelope."""
    if isinstance(error, ServiceError):
        message = str(error)
    else:
        logger.exception("Unhandled service exception", exc_info=error)
        message = "Unable to process the request"

    return JSONResponse(
        status_code=200,
        content={"success": False, "message": message, "data": None},
    )
