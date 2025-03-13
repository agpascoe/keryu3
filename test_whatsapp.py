import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_whatsapp_message():
    """
    Test sending a WhatsApp message using the hello_world template.
    """
    # Get credentials from environment variables
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    test_phone = "525591981815"  # Your test phone number without + prefix
    
    # Prepare the API request
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": test_phone,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    
    try:
        # Send the WhatsApp message
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_whatsapp_message() 