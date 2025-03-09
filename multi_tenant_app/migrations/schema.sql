-- Schema for multi_tenant_app (PostgreSQL example)

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE email_agent_config (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    smtp_server VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL,
    smtp_username VARCHAR(255) NOT NULL,
    smtp_password VARCHAR(255) NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE document_summarizer_config (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    summarizer_setting VARCHAR(255) NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE sfdc_config (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    sfdc_instance_url VARCHAR(255) NOT NULL,
    sfdc_access_token VARCHAR(255) NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
