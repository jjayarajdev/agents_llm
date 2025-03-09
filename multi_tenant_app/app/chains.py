from flask import Blueprint, request, jsonify
from app.models import AgentChain, AgentChainStep
from app import db
from app.schemas import AgentChain as AgentChainSchema
from pydantic import ValidationError
from flask_jwt_extended import jwt_required

chain_bp = Blueprint('chain', __name__)

@chain_bp.route('/create', methods=['POST'])
@jwt_required()
def create_chain():
    """
    Creates a new agent chain configuration.
    Expected JSON payload:
    {
        "tenant_id": 1,
        "name": "My Chain",
        "steps": [
            {"step_order": 1, "agent_name": "doc_sum", "condition": "True"},
            {"step_order": 2, "agent_name": "sfdc", "condition": "input_data.get('summary') is not None"},
            {"step_order": 3, "agent_name": "email"}
        ]
    }
    """
    try:
        validated_data = AgentChainSchema.parse_obj(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.errors()}), 400

    try:
        new_chain = AgentChain(
            tenant_id=validated_data.tenant_id,
            name=validated_data.name
        )
        db.session.add(new_chain)
        db.session.commit()

        # Save chain steps
        for step in sorted(validated_data.steps, key=lambda x: x.step_order):
            chain_step = AgentChainStep(
                agent_chain_id=new_chain.id,
                step_order=step.step_order,
                agent_name=step.agent_name,
                condition=step.condition
            )
            db.session.add(chain_step)
        db.session.commit()

        return jsonify({"message": "Agent chain created", "chain_id": new_chain.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@chain_bp.route('/<int:chain_id>', methods=['GET'])
@jwt_required()
def get_chain(chain_id):
    chain = AgentChain.query.get(chain_id)
    if not chain:
        return jsonify({"error": "Chain not found"}), 404
    chain_data = {
        "chain_id": chain.id,
        "tenant_id": chain.tenant_id,
        "name": chain.name,
        "steps": [{"step_order": step.step_order, "agent_name": step.agent_name, "condition": step.condition} for step in chain.steps]
    }
    return jsonify(chain_data), 200

@chain_bp.route('/execute', methods=['POST'])
@jwt_required()
def execute_chain():
    """
    Executes a pre-configured agent chain for a tenant.
    Expected JSON payload:
    {
       "tenant_id": 1,
       "chain_id": 2,
       "input": {
            "document_text": "Text for summarization",
            "lead_data": { ... },
            "email_params": {
                "recipient": "example@domain.com",
                "subject": "Hello",
                "body": "Email body"
            }
       }
    }
    The chain steps are executed in order. If a summary is produced by the doc_sum agent,
    it is injected into the lead_data (as the "Description" field) for the sfdc agent.
    """
    data = request.get_json()
    tenant_id = data.get("tenant_id")
    chain_id = data.get("chain_id")
    input_data = data.get("input", {})

    if not tenant_id or not chain_id or not input_data:
        return jsonify({"error": "tenant_id, chain_id and input are required"}), 400

    from app.models import AgentChain
    from app.tasks import summarize_document_task, create_lead_task, send_email_task

    chain_config = AgentChain.query.filter_by(id=chain_id, tenant_id=tenant_id).first()
    if not chain_config:
        return jsonify({"error": "Agent chain configuration not found"}), 404

    result = {}
    try:
        for step in chain_config.steps:
            # Evaluate condition if provided
            if step.condition:
                # WARNING: using eval can be risky in production; ensure you use a secure method!
                if not eval(step.condition, {"input_data": input_data}):
                    continue

            if step.agent_name == "doc_sum":
                document_text = input_data.get("document_text")
                if not document_text:
                    return jsonify({"error": "document_text is required for document summarization"}), 400
                summary = summarize_document_task.delay(tenant_id, document_text).get(timeout=60)
                result["doc_sum"] = summary
                input_data["summary"] = summary
            elif step.agent_name == "sfdc":
                lead_data = input_data.get("lead_data")
                if not lead_data:
                    return jsonify({"error": "lead_data is required for SFDC lead creation"}), 400
                if "summary" in input_data:
                    lead_data["Description"] = input_data["summary"]
                sfdc_result = create_lead_task.delay(tenant_id, lead_data).get(timeout=60)
                result["sfdc"] = sfdc_result
            elif step.agent_name == "email":
                email_params = input_data.get("email_params")
                if not email_params:
                    return jsonify({"error": "email_params is required for sending email"}), 400
                email_result = send_email_task.delay(
                    tenant_id,
                    email_params.get("recipient"),
                    email_params.get("subject"),
                    email_params.get("body")
                ).get(timeout=60)
                result["email"] = email_result
        return jsonify({"message": "Chain executed successfully", "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
