# Twilio SMS Test Program

This is a simple Python program that demonstrates sending SMS messages using the Twilio API.

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

3. Sign up for a Twilio account at https://www.twilio.com if you haven't already.

4. Get your Twilio credentials:
   - Account SID
   - Auth Token
   - Twilio Phone Number

5. Update the `.env` file with your Twilio credentials.

## Usage

You can send an SMS message using the command line:

```bash
python send_sms.py "+1234567890" "Your message here"
```

Note: The phone number should be in E.164 format (e.g., +1234567890)

## Function Usage

You can also import the `send_sms` function in your Python code:

```python
from send_sms import send_sms

result = send_sms("+1234567890", "Your message here")
print(result)
```

The function returns a dictionary with either:
- Success: Contains message SID, to/from numbers, and message body
- Error: Contains error details if the message failed to send 