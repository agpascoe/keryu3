from twilio.rest import Client
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def send_whatsapp_message(to_number, message):
    """
    Send a WhatsApp message using Twilio.
    
    Args:
        to_number (str): The recipient's phone number (with country code)
        message (str): The message to send
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        sandbox = os.getenv('TWILIO_WHATSAPP_SANDBOX', 'True').lower() == 'true'
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("Missing required Twilio credentials")
            return False
            
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Format the numbers according to Twilio's WhatsApp requirements
        if sandbox:
            # In sandbox mode, both numbers need the 'whatsapp:' prefix
            from_number_formatted = f"whatsapp:{from_number}"
            to_number_formatted = f"whatsapp:{to_number}"
        else:
            # In production, only the from_number needs the prefix
            from_number_formatted = f"whatsapp:{from_number}"
            to_number_formatted = to_number
            
        logger.info(f"Sending message from {from_number_formatted} to {to_number_formatted}")
        
        # Send the message
        message = client.messages.create(
            body=message,
            from_=from_number_formatted,
            to=to_number_formatted
        )
        
        logger.info(f"Message sent successfully! SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the function
    test_number = '+5215591981815'  # Updated with correct format
    test_message = "This is a test message from Keryu using Twilio WhatsApp!"
    
    print("Starting WhatsApp message test...")
    print(f"Account SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
    print(f"From Number: {os.getenv('TWILIO_FROM_NUMBER')}")
    print(f"To Number: {test_number}")
    print(f"Sandbox Mode: {os.getenv('TWILIO_WHATSAPP_SANDBOX', 'True').lower() == 'true'}")
    
    success = send_whatsapp_message(test_number, test_message)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!") 