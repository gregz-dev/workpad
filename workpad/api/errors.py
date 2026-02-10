from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

from ..errors import WorkpadError, NotFoundError, ValidationError, StorageError

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(WorkpadError)
def handle_workpad_error(e):
    status_code = 500
    if isinstance(e, NotFoundError):
        status_code = 404
    elif isinstance(e, ValidationError):
        status_code = 400
    elif isinstance(e, StorageError):
        status_code = 500
        
    return jsonify({"error": str(e), "type": e.__class__.__name__}), status_code

@errors_bp.app_errorhandler(PydanticValidationError)
def handle_pydantic_error(e):
    return jsonify({"error": "Validation error", "details": e.errors()}), 400

@errors_bp.app_errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({"error": e.description, "type": e.name}), e.code

@errors_bp.app_errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
