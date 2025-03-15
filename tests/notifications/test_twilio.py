from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Twilio Account SID and Auth Token
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_FROM_NUMBER')
to_number = '+5215591981815'  # Updated with correct format
sandbox = os.getenv('TWILIO_WHATSAPP_SANDBOX', 'True').lower() == 'true'

# Create Twilio client
client = Client(account_sid, auth_token)

def send_test_message():
    try:
        # Format the numbers according to Twilio's WhatsApp requirements
        if sandbox:
            # In sandbox mode, both numbers need the 'whatsapp:' prefix
            from_number_formatted = f"whatsapp:{from_number}"
            to_number_formatted = f"whatsapp:{to_number}"
        else:
            # In production, only the from_number needs the prefix
            from_number_formatted = f"whatsapp:{from_number}"

        print(f"Sending message from {from_number_formatted} to {to_number_formatted}")
        
        # Send the message
        message = client.messages.create(
            body="This is a test message from Keryu using Twilio WhatsApp!",
            from_=from_number_formatted,
            to=to_number_formatted
        )
        
        print(f"Message sent successfully! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Twilio WhatsApp test...")
    print(f"Account SID: {account_sid}")
    print(f"From Number: {from_number}")
    print(f"To Number: {to_number}")
    print(f"Sandbox Mode: {sandbox}")
    
    success = send_test_message()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!") 