-- Insert dummy tenants
INSERT INTO tenants (name) VALUES ('Tenant1');
INSERT INTO tenants (name) VALUES ('Tenant2');

-- Insert dummy email configurations
INSERT INTO email_agent_config (tenant_id, smtp_server, smtp_port, smtp_username, smtp_password)
VALUES
((SELECT id FROM tenants WHERE name = 'Tenant1'), 'smtp.tenant1.com', 587, 'user1@tenant1.com', 'pass1'),
((SELECT id FROM tenants WHERE name = 'Tenant2'), 'smtp.tenant2.com', 587, 'user2@tenant2.com', 'pass2');

-- Insert dummy document summarizer configurations
INSERT INTO document_summarizer_config (tenant_id, summarizer_setting)
VALUES
((SELECT id FROM tenants WHERE name = 'Tenant1'), 'advanced'),
((SELECT id FROM tenants WHERE name = 'Tenant2'), 'basic');

-- Insert dummy SFDC configurations
INSERT INTO sfdc_config (tenant_id, sfdc_instance_url, sfdc_access_token)
VALUES
((SELECT id FROM tenants WHERE name = 'Tenant1'), 'https://instance1.salesforce.com', 'token1'),
((SELECT id FROM tenants WHERE name = 'Tenant2'), 'https://instance2.salesforce.com', 'token2');
