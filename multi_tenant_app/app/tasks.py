import smtplib
from email.mime.text import MIMEText
import requests
import openai
from app import celery, db
from app.models import EmailAgentConfig, SFDCConfig
from flask import current_app

# Set the OpenAI API key from the app configuration
openai.api_key = current_app.config.get('OPENAI_API_KEY')

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, tenant_id, recipient, subject, body):
    try:
        config = EmailAgentConfig.query.filter_by(tenant_id=tenant_id).first()
        if not config:
            raise Exception("Email configuration not found for tenant")
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config.smtp_username
        msg['To'] = recipient

        server = smtplib.SMTP(config.smtp_server, config.smtp_port)
        server.starttls()
        server.login(config.smtp_username, config.smtp_password)
        server.send_message(msg)
        server.quit()
        return "Email sent successfully"
    except Exception as exc:
        self.retry(exc=exc)

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def summarize_document_task(self, tenant_id, document_text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following document:\n\n{document_text}",
            max_tokens=150,
            temperature=0.5,
        )
        summary = response.choices[0].text.strip()
        return summary
    except Exception as exc:
        self.retry(exc=exc)

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def create_lead_task(self, tenant_id, lead_data):
    try:
        from app.models import SFDCConfig  # Avoid circular import
        config = SFDCConfig.query.filter_by(tenant_id=tenant_id).first()
        if not config:
            raise Exception("SFDC configuration not found for tenant")
        
        url = f"{config.sfdc_instance_url}/services/data/vXX.X/sobjects/Lead/"
        headers = {
            'Authorization': f"Bearer {config.sfdc_access_token}",
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=lead_data, headers=headers)
        if response.status_code in (200, 201):
            return "Lead created successfully"
        else:
            raise Exception(f"Failed to create lead: {response.text}")
    except Exception as exc:
        self.retry(exc=exc)
