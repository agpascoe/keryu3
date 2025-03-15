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
    
    # Build template data with components inside
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": test_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }
    
    # Add template parameters if provided
    if template_params:
        data["template"]["components"] = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": str(value)
                    } for value in template_params.values()
                ]
            }
        ]
    
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
    # Override the access token for testing
    os.environ['WHATSAPP_ACCESS_TOKEN'] = "EAASvZCLmGU1YBO0YTpJthfbF6CMvzXn039EURHZCaOMsvZCHYdLzZB1NsGht9TKhZCivcuovz44im5mTmZAB9Ww9ZC40ZAJPsSHt9RxBySTwdtnpISZAbVYR0mNZCCkhkiZARVS1JyuF3ZAnTXubndp27hT51TTjneQ284vZBLXQJH9sZBemwrzY9mzCDlqQft0PZCZCQG7d0JZBkEurSOc9ZCVWQq1ZCJLPWsjNQ4ZD"
    
    # Test with parameters for the new template
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_params = {
        "subject_name": "Test Subject",  # This will be {{1}}
        "timestamp": current_time        # This will be {{2}}
    }
    
    test_whatsapp_message(
        template_name="qr_template_on_m",
        language_code="en_US",
        template_params=template_params
    ) 