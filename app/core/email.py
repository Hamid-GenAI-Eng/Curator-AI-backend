import logging
from typing import Optional
from emails import Message
from emails.backend import SMTPBackend
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: dict = {},
) -> None:
    message = Message(
        subject=subject_template,
        html=html_template,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    
    # Check if SMTP is configured
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning("SMTP not fully configured. Email would have been sent to %s with subject: %s", email_to, subject_template)
        logger.info("Email content: %s", html_template)
        return

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "user": settings.SMTP_USER,
        "password": settings.SMTP_PASSWORD,
        "tls": True,
    }
    
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    
    if response.status_code != 250:
        logger.error("Failed to send email to %s: %s", email_to, response.status_text)
    else:
        logger.info("Email sent successfully to %s", email_to)

def send_reset_password_email(email_to: str, token: str) -> None:
    subject = f"{settings.APP_NAME} - Password Reset"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for your {settings.APP_NAME} account.</p>
        <p>Click the button below to reset your password. This link will expire in 2 hours.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">Reset Password</a>
        </div>
        <p>If you did not request this, please ignore this email.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #666;">This is an automated message, please do not reply.</p>
    </div>
    """
    
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content
    )
