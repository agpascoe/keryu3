import os
from twilio.rest import Client
from dotenv import load_dotenv

def send_whatsapp(to_number: str, message: str) -> dict:
    """
    Send a WhatsApp message using Twilio.
    
    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +1234567890)
                        Do not include 'whatsapp:' prefix, it will be added automatically
        message (str): The message to send
        
    Returns:
        dict: Response from Twilio API containing message details
    """
    # Load environment variables
    load_dotenv()
    
    # Get Twilio credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_WHATSAPP_NUMBER')  # Using the WhatsApp number
    
    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Missing required Twilio credentials in environment variables")
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        # Format numbers for WhatsApp
        # Note: The 'from' number must be a Twilio WhatsApp-enabled number
        wa_from = f"whatsapp:{from_number}"
        wa_to = f"whatsapp:{to_number}"
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=wa_from,
            to=wa_to
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
        print("Usage: python send_wa.py <phone_number> <message>")
        print("Example: python send_wa.py +1234567890 'Hello from WhatsApp!'")
        print("Note: Phone number should be in E.164 format (e.g., +1234567890)")
        print("      Do not include 'whatsapp:' prefix, it will be added automatically")
        print("\nFor trial accounts, first message must be a template:")
        print("'Your {{1}} code is {{2}}'")
        print("'Your Twilio verification code is: {{1}}'")
        print("'{{1}} is your Twilio login code'")
        sys.exit(1)
        
    to_number = sys.argv[1]
    message_text = sys.argv[2]
    
    result = send_whatsapp(to_number, message_text)
    print(result) 