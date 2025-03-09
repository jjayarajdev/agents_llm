from app import db

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # One-to-one relationships with agent configurations
    email_config = db.relationship("EmailAgentConfig", backref="tenant", uselist=False)
    doc_sum_config = db.relationship("DocumentSummarizerConfig", backref="tenant", uselist=False)
    sfdc_config = db.relationship("SFDCConfig", backref="tenant", uselist=False)

class EmailAgentConfig(db.Model):
    __tablename__ = 'email_agent_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password = db.Column(db.String(255), nullable=False)

class DocumentSummarizerConfig(db.Model):
    __tablename__ = 'document_summarizer_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    summarizer_setting = db.Column(db.String(255), nullable=False)

class SFDCConfig(db.Model):
    __tablename__ = 'sfdc_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    sfdc_instance_url = db.Column(db.String(255), nullable=False)
    sfdc_access_token = db.Column(db.String(255), nullable=False)
