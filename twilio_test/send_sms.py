import os
from twilio.rest import Client
from dotenv import load_dotenv

def send_sms(to_number: str, message: str) -> dict:
    """
    Send an SMS message using Twilio.
    
    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +1234567890)
        message (str): The message to send
        
    Returns:
        dict: Response from Twilio API containing message details
    """
    # Load environment variables
    load_dotenv()
    
    # Get Twilio credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Missing required Twilio credentials in environment variables")
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        # Send message
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return {
            'status': 'success',
            'message_sid': message.sid,
            'to': message.to,
            'from': message.from_,
            'body': message.body
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python send_sms.py <phone_number> <message>")
        print("Example: python send_sms.py +1234567890 'Hello from Twilio!'")
        sys.exit(1)
        
    to_number = sys.argv[1]
    message_text = sys.argv[2]
    
    result = send_sms(to_number, message_text)
    print(result) 