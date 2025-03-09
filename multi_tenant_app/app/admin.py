from flask import Blueprint, request, jsonify
from app.models import Tenant, EmailAgentConfig, DocumentSummarizerConfig, SFDCConfig
from app import db
from app.schemas import TenantSetupSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/setup_tenant', methods=['POST'])
@jwt_required()  # Secures this endpoint
def setup_tenant():
    """
    Admin endpoint to set up a new tenant with optional configurations.
    
    Expected JSON payload:
    {
        "tenant_name": "TenantName",
        "email_config": { ... },
        "doc_sum_config": { ... },
        "sfdc_config": { ... }
    }
    """
    try:
        data = request.get_json()
        schema = TenantSetupSchema()
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    tenant_name = validated_data.get("tenant_name")
    
    # Check for an existing tenant
    existing_tenant = Tenant.query.filter_by(name=tenant_name).first()
    if existing_tenant:
        return jsonify({"error": "Tenant already exists"}), 400

    try:
        tenant = Tenant(name=tenant_name)
        db.session.add(tenant)
        db.session.commit()

        if "email_config" in validated_data:
            email_data = validated_data["email_config"]
            email_config = EmailAgentConfig(
                tenant_id=tenant.id,
                smtp_server=email_data.get("smtp_server"),
                smtp_port=email_data.get("smtp_port"),
                smtp_username=email_data.get("smtp_username"),
                smtp_password=email_data.get("smtp_password")
            )
            db.session.add(email_config)
            
        if "doc_sum_config" in validated_data:
            doc_data = validated_data["doc_sum_config"]
            doc_config = DocumentSummarizerConfig(
                tenant_id=tenant.id,
                summarizer_setting=doc_data.get("summarizer_setting")
            )
            db.session.add(doc_config)
            
        if "sfdc_config" in validated_data:
            sfdc_data = validated_data["sfdc_config"]
            sfdc_config = SFDCConfig(
                tenant_id=tenant.id,
                sfdc_instance_url=sfdc_data.get("sfdc_instance_url"),
                sfdc_access_token=sfdc_data.get("sfdc_access_token")
            )
            db.session.add(sfdc_config)
            
        db.session.commit()
        
        return jsonify({"message": "Tenant setup successfully", "tenant_id": tenant.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
