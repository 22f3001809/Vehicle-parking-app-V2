from flask_mail import Message
from flask import current_app
import requests
import os

def send_email(subject, recipients, body, html=None, attachments=None, email_backend='mail'):
    """
    Send email via multiple backends
    """
    if email_backend == 'gchat':
        return _send_via_google_chat(subject, body, html)
    else:
        return _send_via_flask_mail(subject, recipients, body, html, attachments)


def _send_via_flask_mail(subject, recipients, body, html=None, attachments=None):
    """
    Send email via Flask-Mail.
    Uses current_app to get the mail extension configured in app.py.
    """
    try:
        mail = current_app.extensions.get('mail')
        
        if not mail:
            return {
                'status': 'error', 
                'error': 'Flask-Mail not initialized in app.py'
            }

        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=body,
            html=html
        )
        
        if attachments:
            for filename, content, mimetype in attachments:
                msg.attach(filename, mimetype, content)
        
        mail.send(msg)
        
        print(f"Sent via Flask-Mail to: {recipients}")
        return {
            'status': 'success',
            'method': 'flask-mail',
            'recipients': recipients if isinstance(recipients, list) else [recipients]
        }
    except Exception as e:
        return {
            'status': 'error',
            'method': 'flask-mail',
            'error': str(e)
        }


def _send_via_google_chat(subject, body, html=None):
    """Send message via Google Chat Webhook"""
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')
    
    if not webhook_url:
        print("GOOGLE_CHAT_WEBHOOK_URL not configured")
        return {'status': 'warning', 'message': 'Webhook URL not configured'}
    
    try:
        message = {"text": f"*{subject}*\n\n{body}"}
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        
        print(f"Sent via Google Chat")
        return {'status': 'success'}
    except Exception as e:
        print(f"Error sending via Google Chat: {e}")
        return {'status': 'error', 'error': str(e)}