import pytest
from workpad.models import EntryType

def test_health(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_create_entry(client):
    data = {
        "type": "note",
        "content": "API Test Entry",
        "tags": ["api", "test"]
    }
    response = client.post('/api/v1/entries', json=data)
    assert response.status_code == 201
    assert response.json['content'] == "API Test Entry"
    assert response.json['id'] is not None

def test_get_entry(client):
    # Create first
    data = {"type": "note", "content": "To Retrieve"}
    create_resp = client.post('/api/v1/entries', json=data)
    entry_id = create_resp.json['id']
    
    # Get
    response = client.get(f'/api/v1/entries/{entry_id}')
    assert response.status_code == 200
    assert response.json['content'] == "To Retrieve"

def test_get_entry_not_found(client):
    response = client.get('/api/v1/entries/non-existent-id')
    assert response.status_code == 404

def test_list_entries(client):
    client.post('/api/v1/entries', json={"type": "note", "content": "1"})
    client.post('/api/v1/entries', json={"type": "task", "content": "2"})
    
    response = client.get('/api/v1/entries')
    assert response.status_code == 200
    assert len(response.json) == 2
    
    # Filter
    response = client.get('/api/v1/entries?type=task')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['content'] == "2"

def test_update_entry(client):
    create_resp = client.post('/api/v1/entries', json={"type": "note", "content": "Original"})
    entry_id = create_resp.json['id']
    
    response = client.put(f'/api/v1/entries/{entry_id}', json={"content": "Updated"})
    assert response.status_code == 200
    assert response.json['content'] == "Updated"

def test_delete_entry(client):
    create_resp = client.post('/api/v1/entries', json={"type": "note", "content": "To Delete"})
    entry_id = create_resp.json['id']
    
    response = client.delete(f'/api/v1/entries/{entry_id}')
    assert response.status_code == 204
    
    # Verify gone
    get_resp = client.get(f'/api/v1/entries/{entry_id}')
    assert get_resp.status_code == 404

def test_add_context(client):
    create_resp = client.post('/api/v1/entries', json={"type": "note", "content": "With Context"})
    entry_id = create_resp.json['id']
    
    ctx_data = {
        "type": "note",
        "source": "api",
        "content": "Context Content"
    }
    response = client.post(f'/api/v1/entries/{entry_id}/context', json=ctx_data)
    assert response.status_code == 201
    
    # Verify in entry
    get_resp = client.get(f'/api/v1/entries/{entry_id}')
    assert len(get_resp.json['context_items']) == 1

def test_relations(client):
    e1 = client.post('/api/v1/entries', json={"type": "note", "content": "E1"}).json
    e2 = client.post('/api/v1/entries', json={"type": "note", "content": "E2"}).json
    
    # Link
    response = client.post(f"/api/v1/entries/{e1['id']}/relations/{e2['id']}")
    assert response.status_code == 201
    
    # Verify
    e1_get = client.get(f"/api/v1/entries/{e1['id']}").json
    assert e2['id'] in e1_get['related_entries']

def test_stats(client):
    client.post('/api/v1/entries', json={"type": "note", "content": "E1"})
    response = client.get('/api/v1/stats')
    assert response.status_code == 200
    assert response.json['total_entries'] >= 1
