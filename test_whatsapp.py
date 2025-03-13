import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

def test_whatsapp_message(template_name, language_code="en_US", template_params=None):
    """
    Test sending a WhatsApp message using a specified template.
    
    Args:
        template_name (str): Name of the template to use
        language_code (str): Language code for the template (default: "en_US")
        template_params (dict): Parameters required by the template (default: None)
    """
    # Get credentials from environment variables
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    test_phone = "525591981815"  # Removed the "1" between "+52" and "55"
    
    print(f"Using Phone Number ID: {phone_number_id}")
    print(f"Access Token length: {len(access_token)}")
    print(f"Test phone number: {test_phone}")
    print(f"Template name: {template_name}")
    print(f"Language code: {language_code}")
    if template_params:
        print(f"Template parameters: {json.dumps(template_params, indent=2)}")
    
    # Prepare the API request
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Build template data
    template_data = {
        "name": template_name,
        "language": {
            "code": language_code
        }
    }
    
    # Add template parameters if provided
    if template_params:
        template_data["components"] = []
        for key, value in template_params.items():
            template_data["components"].append({
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": str(value)
                    }
                ]
            })
    
    data = {
        "messaging_product": "whatsapp",
        "to": test_phone,
        "type": "template",
        "template": template_data
    }
    
    try:
        print("\nSending request to WhatsApp API...")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        # Send the WhatsApp message
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\nMessage sent successfully!")
        else:
            print("\nFailed to send message.")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    # Test the qr_is_on template
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_params = {
        "Subject": "Test Subject",
        "Timestamp": current_time
    }
    
    test_whatsapp_message(
        template_name="qr_is_on",
        language_code="en_US",
        template_params=template_params
    ) 