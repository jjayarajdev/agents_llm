from marshmallow import Schema, fields, validate

class EmailConfigSchema(Schema):
    smtp_server = fields.Str(required=True)
    smtp_port = fields.Int(required=True)
    smtp_username = fields.Str(required=True)
    smtp_password = fields.Str(required=True)

class DocSumConfigSchema(Schema):
    summarizer_setting = fields.Str(required=True)

class SFDCConfigSchema(Schema):
    sfdc_instance_url = fields.Str(required=True)
    sfdc_access_token = fields.Str(required=True)

class TenantSetupSchema(Schema):
    tenant_name = fields.Str(required=True, validate=validate.Length(min=1))
    email_config = fields.Nested(EmailConfigSchema, required=False)
    doc_sum_config = fields.Nested(DocSumConfigSchema, required=False)
    sfdc_config = fields.Nested(SFDCConfigSchema, required=False)
