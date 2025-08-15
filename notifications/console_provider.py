"""
Console notification provider for development.
This provider logs messages to the console instead of sending them.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsoleNotificationProvider:
    """Console notification provider for development."""
    
    def __init__(self):
        self.name = "Console Provider"
        logger.info(f"Initialized {self.name}")
    
    def send_message(self, to_number, message_data):
        """Log the message to console instead of sending it."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format the message for console output
            if message_data.get('subject_name') and message_data.get('timestamp'):
                formatted_message = f"Alert: {message_data['subject_name']} has been located at {message_data['timestamp']}"
            else:
                formatted_message = str(message_data)
            
            # Log the message
            logger.info(f"[CONSOLE NOTIFICATION] {timestamp}")
            logger.info(f"To: {to_number}")
            logger.info(f"Message: {formatted_message}")
            logger.info(f"Raw data: {message_data}")
            logger.info("-" * 50)
            
            # Print to console for immediate visibility
            print(f"\n{'='*60}")
            print(f"📱 CONSOLE NOTIFICATION - {timestamp}")
            print(f"📞 To: {to_number}")
            print(f"💬 Message: {formatted_message}")
            print(f"📋 Raw data: {message_data}")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'message_id': f"console_{timestamp.replace(' ', '_').replace(':', '-')}",
                'status': 'SENT',
                'recipient': to_number,
                'provider': 'console'
            }
            
        except Exception as e:
            logger.error(f"Error in console notification: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'ERROR',
                'provider': 'console'
            }

def get_console_notification_service():
    """Get the console notification service."""
    return ConsoleNotificationProvider() 