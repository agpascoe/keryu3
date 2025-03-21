# WhatsApp Template Setup Guide

This guide explains how to set up and configure WhatsApp templates and messaging channels for the Keryu system.

## Prerequisites

1. Meta Developer Account
2. WhatsApp Business API access
3. Approved WhatsApp Business Account
4. Twilio Account (optional, for fallback channels)

## Messaging Channels

The system supports three messaging channels:

1. **Meta WhatsApp API (Primary)**
   - Default channel
   - Uses WhatsApp Business API
   - Requires template approval

2. **Twilio WhatsApp (Fallback)**
   - First fallback option
   - Uses Twilio's WhatsApp integration
   - Supports sandbox testing

3. **Twilio SMS (Fallback)**
   - Second fallback option
   - Traditional SMS messaging
   - No template requirements

### Channel Configuration

Set the active channel using the `SystemParameter` model:
```python
from core.models import SystemParameter

# Meta WhatsApp API (default)
SystemParameter.objects.get_or_create(
    parameter="channel",
    defaults={"value": "1"}
)

# Twilio WhatsApp
SystemParameter.objects.filter(parameter="channel").update(value="2")

# Twilio SMS
SystemParameter.objects.filter(parameter="channel").update(value="3")
```

## Template Configuration

### Template Details

- **Name**: qr_template_on_m
- **Language**: en_US
- **Category**: UTILITY
- **Body**: "Alert: {{1}} has been located at {{2}}"

### Variables

The template uses two variables:
1. `{{1}}`: Subject name
2. `{{2}}`: Timestamp

## Setup Steps

1. **Access Meta Developer Console**
   - Log in to [Meta Developer Console](https://developers.facebook.com)
   - Navigate to your WhatsApp app

2. **Create Template**
   - Go to WhatsApp > Getting Started
   - Click "Create Template"
   - Select "UTILITY" as the category
   - Enter template name: "qr_template_on_m"
   - Select language: "English (US)"

3. **Configure Template Body**
   - Enter the template body text
   - Add variables using the variable button:
     - Add `{{1}}` for the subject name
     - Add `{{2}}` for the scan time

4. **Submit for Review**
   - Review the template
   - Submit for approval
   - Wait for approval (usually 24-48 hours)

## Environment Configuration

1. **Meta WhatsApp API**
```env
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
```

2. **Twilio Configuration (Optional)**
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number
```

## Testing

1. **Using Test Script**
```bash
python test_whatsapp.py
```

2. **Running Test Suite**
```bash
python -m pytest tests/test_messaging.py -vv
```

3. **Verification**
   - Check response status
   - Verify message delivery
   - Confirm variable replacement
   - Test fallback channels

## Phone Number Formatting

Each channel has specific formatting requirements:

1. **Meta WhatsApp API**
   - Removes '+' prefix
   - Example: "+5212345678901" → "5212345678901"

2. **Twilio WhatsApp**
   - Adds 'whatsapp:' prefix
   - Formats Mexican numbers
   - Example: "+5212345678901" → "whatsapp:+5212345678901"

3. **Twilio SMS**
   - Formats Mexican numbers
   - Example: "+5212345678901" → "+5212345678901"

## Troubleshooting

### Common Issues

1. **Template Not Found**
   - Verify template name is correct
   - Check template approval status
   - Ensure language code matches

2. **Variable Issues**
   - Verify variable names match exactly
   - Check variable order
   - Ensure all required variables are provided

3. **Channel Issues**
   - Verify channel configuration
   - Check API credentials
   - Test fallback channels

4. **Approval Delays**
   - Template review typically takes 24-48 hours
   - Check template status in Meta Developer Console
   - Contact Meta support if delayed beyond 48 hours

## Best Practices

1. **Template Design**
   - Keep messages concise
   - Use clear variable names
   - Include all necessary information

2. **Testing**
   - Test with various variable combinations
   - Verify message formatting
   - Check delivery status
   - Test all channels

3. **Monitoring**
   - Monitor template usage
   - Track delivery rates
   - Review error logs
   - Monitor channel performance

4. **Channel Management**
   - Configure all channels properly
   - Test fallback scenarios
   - Monitor channel health
   - Update credentials as needed

## Support

For additional support:
1. Check Meta's [WhatsApp Business Platform Documentation](https://developers.facebook.com/docs/whatsapp)
2. Review the [WhatsApp Template Guidelines](https://developers.facebook.com/docs/whatsapp/cloud-api/message-templates)
3. Check Twilio's [WhatsApp API Documentation](https://www.twilio.com/docs/whatsapp/api)
4. Contact Meta or Twilio Developer Support 