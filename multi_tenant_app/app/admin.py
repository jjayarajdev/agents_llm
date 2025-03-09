from flask import Blueprint, request, jsonify
from app.models import Tenant, EmailAgentConfig, DocumentSummarizerConfig, SFDCConfig
from app import db
from app.schemas import TenantSetup
from pydantic import ValidationError
from flask_jwt_extended import jwt_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/setup_tenant', methods=['POST'])
@jwt_required()
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
        validated_data = TenantSetup.parse_obj(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.errors()}), 400

    tenant_name = validated_data.tenant_name
    
    # Check for an existing tenant
    existing_tenant = Tenant.query.filter_by(name=tenant_name).first()
    if existing_tenant:
        return jsonify({"error": "Tenant already exists"}), 400

    try:
        tenant = Tenant(name=tenant_name)
        db.session.add(tenant)
        db.session.commit()

        if validated_data.email_config:
            email_config = EmailAgentConfig(
                tenant_id=tenant.id,
                smtp_server=validated_data.email_config.smtp_server,
                smtp_port=validated_data.email_config.smtp_port,
                smtp_username=validated_data.email_config.smtp_username,
                smtp_password=validated_data.email_config.smtp_password
            )
            db.session.add(email_config)
            
        if validated_data.doc_sum_config:
            doc_config = DocumentSummarizerConfig(
                tenant_id=tenant.id,
                summarizer_setting=validated_data.doc_sum_config.summarizer_setting
            )
            db.session.add(doc_config)
            
        if validated_data.sfdc_config:
            sfdc_config = SFDCConfig(
                tenant_id=tenant.id,
                sfdc_instance_url=validated_data.sfdc_config.sfdc_instance_url,
                sfdc_access_token=validated_data.sfdc_config.sfdc_access_token
            )
            db.session.add(sfdc_config)
            
        db.session.commit()
        
        return jsonify({"message": "Tenant setup successfully", "tenant_id": tenant.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
