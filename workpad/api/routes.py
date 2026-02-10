from flask import Blueprint, request, jsonify, current_app
from ..models import EntryCreate, EntryUpdate, EntryFilter, ContextItemCreate
from ..service import WorkpadService
from ..storage.json_storage import JSONStorage

bp = Blueprint('api', __name__, url_prefix='/api/v1')

def get_service() -> WorkpadService:
    # In a real app, use dependency injection or g
    # For now, simple instantiation per request or global if stateless?
    # Service is stateless but storage is stateful (files).
    # We can rely on settings.
    from ..config import settings
    storage = JSONStorage(settings.DATA_PATH)
    # Optimization: storage.initialize() should be called once on app startup, 
    # but here safe to call or rely on it being idempotent.
    storage.initialize()
    return WorkpadService(storage)

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@bp.route('/entries', methods=['POST'])
def create_entry():
    service = get_service()
    data = request.get_json()
    # Pydantic validation
    entry_create = EntryCreate(**data)
    entry = service.create_entry(entry_create)
    return jsonify(entry.model_dump(mode='json')), 201

@bp.route('/entries', methods=['GET'])
def list_entries():
    service = get_service()
    # Parse query params to EntryFilter
    # This is a bit manual, ideally pydantic can parse dict from args
    # But request.args is ImmutableMultiDict.
    args = request.args.to_dict()
    # Handle list types for tags? request.args.getlist('tags')
    tags = request.args.getlist('tags')
    if tags:
        args['tags'] = tags
        
    filters = EntryFilter(**args)
    entries = service.list_entries(filters)
    return jsonify([e.model_dump(mode='json') for e in entries]), 200

@bp.route('/entries/<entry_id>', methods=['GET'])
def get_entry(entry_id):
    service = get_service()
    entry = service.get_entry(entry_id)
    return jsonify(entry.model_dump(mode='json')), 200

@bp.route('/entries/<entry_id>', methods=['PUT', 'PATCH'])
def update_entry(entry_id):
    service = get_service()
    data = request.get_json()
    update = EntryUpdate(**data)
    entry = service.update_entry(entry_id, update)
    return jsonify(entry.model_dump(mode='json')), 200

@bp.route('/entries/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    service = get_service()
    service.delete_entry(entry_id)
    return '', 204

# --- Context ---

@bp.route('/entries/<entry_id>/context', methods=['POST'])
def add_context(entry_id):
    service = get_service()
    data = request.get_json()
    ctx_create = ContextItemCreate(**data)
    item = service.add_context(entry_id, ctx_create)
    return jsonify(item.model_dump(mode='json')), 201

@bp.route('/entries/<entry_id>/context/<context_id>', methods=['DELETE'])
def remove_context(entry_id, context_id):
    service = get_service()
    if service.remove_context(entry_id, context_id):
        return '', 204
    else:
        return jsonify({"error": "Context item not found"}), 404

# --- Relations ---

@bp.route('/entries/<entry_id>/relations/<related_id>', methods=['POST'])
def add_relation(entry_id, related_id):
    service = get_service()
    service.add_relation(entry_id, related_id)
    return '', 201

@bp.route('/entries/<entry_id>/relations/<related_id>', methods=['DELETE'])
def remove_relation(entry_id, related_id):
    service = get_service()
    service.remove_relation(entry_id, related_id)
    return '', 204

# --- Stats ---

@bp.route('/stats', methods=['GET'])
def get_stats():
    service = get_service()
    return jsonify(service.get_stats()), 200
