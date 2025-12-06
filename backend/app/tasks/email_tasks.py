import logging
from app.celery_app import celery_app
from app.utils.email import get_email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_email_task(
    self, to_email: str, subject: str, body: str, html_body: str = None
):
    """
    Send email asynchronously via MailHog.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body

    Returns:
        dict: Status and message
    """
    try:
        logger.info(f"Sending email to {to_email} with subject: {subject}")

        email_service = get_email_service()
        success = email_service.send_email(
            to_email=to_email, subject=subject, body=body, html_body=html_body
        )

        if success:
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "status": "success",
                "message": f"Email sent to {to_email}",
                "mailhog_ui": "http://localhost:8025",
            }
        else:
            raise Exception("Failed to send email")

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@celery_app.task
def send_welcome_email(user_id: int, email: str, name: str):
    """
    Send welcome email to new user.

    Args:
        user_id: User ID
        email: User email address
        name: User name
    """
    subject = "Welcome to Project Management System!"

    body = f"""
    Hello {name},

    Welcome to our Project Management System! We're excited to have you on board.

    Your account has been successfully created with the following details:
    - User ID: {user_id}
    - Email: {email}

    You can now log in and start managing your projects.

    Best regards,
    The Project Management Team
    """

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Welcome to Project Management System!</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>Welcome to our Project Management System! We're excited to have you on board.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Account Details:</strong></p>
                    <p style="margin: 5px 0;">User ID: {user_id}</p>
                    <p style="margin: 5px 0;">Email: {email}</p>
                </div>
                
                <p>You can now log in and start managing your projects.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>The Project Management Team</p>
            </div>
        </body>
    </html>
    """

    return send_email_task.delay(email, subject, body, html_body)


@celery_app.task
def send_password_reset_email(email: str, reset_token: str, user_name: str = "User"):
    """
    Send password reset email.

    Args:
        email: User email address
        reset_token: Password reset token
        user_name: User's name
    """
    subject = "Password Reset Request"

    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    body = f"""
    Hello {user_name},

    We received a request to reset your password.

    Reset Token: {reset_token}
    Reset Link: {reset_link}

    This token will expire in 1 hour.

    If you didn't request this, please ignore this email.

    Best regards,
    The Project Management Team
    """

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Password Reset Request</h2>
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>We received a request to reset your password.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 5px 0;"><strong>Reset Token:</strong> {reset_token}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">This token will expire in 1 hour.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>The Project Management Team</p>
            </div>
        </body>
    </html>
    """

    return send_email_task.delay(email, subject, body, html_body)


@celery_app.task
def send_project_assignment_email(
    email: str, user_name: str, project_name: str, project_id: str
):
    """
    Send email when user is assigned to a project.

    Args:
        email: User email address
        user_name: User's name
        project_name: Project name
        project_id: Project ID
    """
    subject = f"You've been assigned to project: {project_name}"

    body = f"""
    Hello {user_name},

    You have been assigned to a new project:
    
    Project Name: {project_name}
    Project ID: {project_id}

    You can view the project details in your dashboard.

    Best regards,
    The Project Management Team
    """

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">New Project Assignment</h2>
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>You have been assigned to a new project:</p>
                
                <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <p style="margin: 5px 0;"><strong>Project Name:</strong> {project_name}</p>
                    <p style="margin: 5px 0;"><strong>Project ID:</strong> {project_id}</p>
                </div>
                
                <p>You can view the project details in your dashboard.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>The Project Management Team</p>
            </div>
        </body>
    </html>
    """

    return send_email_task.delay(email, subject, body, html_body)


@celery_app.task
def send_requirement_update_email(
    email: str, user_name: str, requirement_id: str, project_name: str, status: str
):
    """
    Send email when requirement status is updated.

    Args:
        email: User email address
        user_name: User's name
        requirement_id: Requirement ID
        project_name: Project name
        status: New status
    """
    subject = f"Requirement Update: {requirement_id}"

    body = f"""
    Hello {user_name},

    A requirement has been updated:
    
    Requirement ID: {requirement_id}
    Project: {project_name}
    New Status: {status}

    Best regards,
    The Project Management Team
    """

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Requirement Update</h2>
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>A requirement has been updated:</p>
                
                <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <p style="margin: 5px 0;"><strong>Requirement ID:</strong> {requirement_id}</p>
                    <p style="margin: 5px 0;"><strong>Project:</strong> {project_name}</p>
                    <p style="margin: 5px 0;"><strong>New Status:</strong> {status}</p>
                </div>
                
                <p style="margin-top: 30px;">Best regards,<br>The Project Management Team</p>
            </div>
        </body>
    </html>
    """

    return send_email_task.delay(email, subject, body, html_body)
