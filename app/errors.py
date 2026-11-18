"""Erreurs de l'API au format Problem Details (RFC 9457)."""
import logging
import uuid
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("api_catalogue")


class ApiError(Exception):
    def __init__(self, status: int, code: str, detail: str,
                 errors: list[dict] | None = None,
                 headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail
        self.errors = errors
        self.headers = headers


def problem(request: Request, status: int, code: str, detail: str,
             errors: list[dict] | None = None,
             headers: dict[str, str] | None = None) -> JSONResponse:
    corps = {
        "type": f"https://api-catalogue.example/errors#{code}",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "code": code,
        "detail": detail,
        "instance": request.url.path,
        "request_id": str(uuid.uuid4()),
    }
    if errors:
        corps["errors"] = errors
    return JSONResponse(corps, status_code=status, headers=headers,
                        media_type="application/problem+json")


def pointer(loc: tuple) -> str:
    return "/" + "/".join(str(chunks) for chunks in loc[1:])   # loc[0] : body, query ou path


def installer_gestionnaires(app: FastAPI) -> None:
    """
    Un gestionnaire d'exceptions capture et redéfinit les erreurs ciblées déclenchées par l'application.

    ApiError: erreur métier dans un gestionnaire de route (code métier)
    StarletteHTTPException: sous-jacente à l'exception HTTPException de FastAPI, erreur HTTP standard (404, 403, etc.)
    RequestValidationError: erreur de validation des paramètres de la requête 422 pydantic
    Exception: toute autre erreur non gérée
    """
    @app.exception_handler(ApiError)
    async def error_api(request: Request, exc: ApiError) -> JSONResponse:
        return problem(request, exc.status, exc.code, exc.detail, exc.errors, exc.headers)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return problem(request, exc.status_code, "http_error", str(exc.detail),
                        headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [{"pointer": pointer(e["loc"]), "code": e["type"], "detail": e["msg"]}
                   for e in exc.errors()]
        return problem(request, 422, "validation_failed",
                        "Certains champs ne sont pas valides.", errors)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erreur non gérée sur %s", request.url.path)
        return problem(request, 500, "internal_error", "Erreur interne du serveur.")
