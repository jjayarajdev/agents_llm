from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal, Dict, Any

# Schemas for tenant setup

class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

class DocSumConfig(BaseModel):
    summarizer_setting: str

class SFDCConfig(BaseModel):
    sfdc_instance_url: str
    sfdc_access_token: str

class TenantSetup(BaseModel):
    tenant_name: constr(min_length=1)
    email_config: Optional[EmailConfig] = None
    doc_sum_config: Optional[DocSumConfig] = None
    sfdc_config: Optional[SFDCConfig] = None

# Schemas for agent chain configuration

class AgentChainStep(BaseModel):
    step_order: int
    agent_name: Literal['doc_sum', 'sfdc', 'email']
    condition: Optional[str] = None  # Optional condition as a string expression

class AgentChain(BaseModel):
    tenant_id: int
    name: str
    steps: List[AgentChainStep]

# Agent input/output schemas

class DocumentSummarizerInput(BaseModel):
    document_text: str

class DocumentSummarizerOutput(BaseModel):
    summary: str

class EmailAgentInput(BaseModel):
    recipient: str
    subject: str
    body: str

class EmailAgentOutput(BaseModel):
    status: str
    message: str

class SFDCInput(BaseModel):
    lead_data: Dict[str, Any]

class SFDCOutput(BaseModel):
    status: str
    message: str
