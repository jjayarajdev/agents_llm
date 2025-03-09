from app import db

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Change to one-to-many for flexible configuration
    email_configs = db.relationship("EmailAgentConfig", backref="tenant", cascade="all, delete-orphan")
    doc_sum_configs = db.relationship("DocumentSummarizerConfig", backref="tenant", cascade="all, delete-orphan")
    sfdc_configs = db.relationship("SFDCConfig", backref="tenant", cascade="all, delete-orphan")
    
    # One-to-many relationship for agent chains
    agent_chains = db.relationship("AgentChain", backref="tenant", cascade="all, delete-orphan")

class EmailAgentConfig(db.Model):
    __tablename__ = 'email_agent_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)  # nullable for global configs
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password = db.Column(db.String(255), nullable=False)
    is_global = db.Column(db.Boolean, default=False)

class DocumentSummarizerConfig(db.Model):
    __tablename__ = 'document_summarizer_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    summarizer_setting = db.Column(db.String(255), nullable=False)
    is_global = db.Column(db.Boolean, default=False)

class SFDCConfig(db.Model):
    __tablename__ = 'sfdc_config'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    sfdc_instance_url = db.Column(db.String(255), nullable=False)
    sfdc_access_token = db.Column(db.String(255), nullable=False)
    is_global = db.Column(db.Boolean, default=False)

# Models for agent chain configuration

class AgentChain(db.Model):
    __tablename__ = 'agent_chain'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    steps = db.relationship('AgentChainStep', backref='chain', order_by='AgentChainStep.step_order', cascade="all, delete-orphan")

class AgentChainStep(db.Model):
    __tablename__ = 'agent_chain_step'
    id = db.Column(db.Integer, primary_key=True)
    agent_chain_id = db.Column(db.Integer, db.ForeignKey('agent_chain.id'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    agent_name = db.Column(db.String(50), nullable=False)  # 'doc_sum', 'sfdc', or 'email'
    condition = db.Column(db.String(255), nullable=True)   # Optional conditional expression
