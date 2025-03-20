from django.core.mail.backends.base import BaseEmailBackend
from django.contrib import messages
from django.template.loader import render_to_string

class PopupEmailBackend(BaseEmailBackend):
    """Custom email backend that stores emails for popup display."""
    
    def send_messages(self, email_messages):
        """Store the email content in the request session for popup display."""
        if not email_messages:
            return 0

        # We only handle verification emails for now
        for message in email_messages:
            if 'Verify your Keryu account' in message.subject:
                # Store the verification URL from the email content
                if hasattr(message, 'alternatives') and message.alternatives:
                    html_content = message.alternatives[0][0]  # Get HTML content
                    # Store in the backend for retrieval
                    PopupEmailBackend.latest_verification_email = {
                        'to': message.to[0],
                        'subject': message.subject,
                        'content': html_content,
                    }
        
        return len(email_messages)

    @classmethod
    def get_verification_email(cls):
        """Get the latest verification email."""
        return getattr(cls, 'latest_verification_email', None) 