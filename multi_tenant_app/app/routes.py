from flask import Blueprint, request, jsonify
from app.tasks import send_email_task, summarize_document_task, create_lead_task
from celery.result import AsyncResult
from app import celery
from app.chroma import index_document, search_document

bp = Blueprint('api', __name__)

@bp.route('/send_email', methods=['POST'])
def api_send_email():
    """
    Expected JSON:
    {
        "tenant_id": 1,
        "recipient": "recipient@example.com",
        "subject": "Test Email",
        "body": "Email content here..."
    }
    """
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')
    task = send_email_task.delay(tenant_id, recipient, subject, body)
    return jsonify({'task_id': task.id}), 202

@bp.route('/summarize_document', methods=['POST'])
def api_summarize_document():
    """
    Expected JSON:
    {
        "tenant_id": 1,
        "document_text": "Your document text..."
    }
    """
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    document_text = data.get('document_text')
    task = summarize_document_task.delay(tenant_id, document_text)
    return jsonify({'task_id': task.id}), 202

@bp.route('/create_lead', methods=['POST'])
def api_create_lead():
    """
    Expected JSON:
    {
        "tenant_id": 1,
        "lead_data": {
            "FirstName": "John",
            "LastName": "Doe",
            "Company": "Example Inc."
        }
    }
    """
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    lead_data = data.get('lead_data')
    task = create_lead_task.delay(tenant_id, lead_data)
    return jsonify({'task_id': task.id}), 202

@bp.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    result = AsyncResult(task_id, app=celery)
    response = {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None
    }
    return jsonify(response)

@bp.route('/index_document', methods=['POST'])
def api_index_document():
    """
    Expected JSON:
    {
       "tenant_id": 1,
       "document_id": "doc1",
       "document_text": "This is the document text to index."
    }
    """
    data = request.get_json()
    tenant_id = data.get("tenant_id")
    document_id = data.get("document_id")
    document_text = data.get("document_text")
    result = index_document(tenant_id, document_id, document_text)
    return jsonify(result)

@bp.route('/search_document', methods=['POST'])
def api_search_document():
    """
    Expected JSON:
    {
       "tenant_id": 1,
       "query_text": "Query text to search for similar documents",
       "n_results": 3   // optional, defaults to 3 if not provided
    }
    """
    data = request.get_json()
    tenant_id = data.get("tenant_id")
    query_text = data.get("query_text")
    n_results = data.get("n_results", 3)
    result = search_document(tenant_id, query_text, n_results)
    return jsonify(result)
