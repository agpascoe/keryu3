# WhatsApp Template Setup Guide

This guide explains how to set up and configure WhatsApp templates for the Keryu system.

## Prerequisites

1. Meta Developer Account
2. WhatsApp Business API access
3. Approved WhatsApp Business Account

## Template Configuration

### Template Details

- **Name**: qr_is_on
- **Language**: en_US
- **Category**: UTILITY
- **Body**: "Hello, the qr of {{Subject}} has been read at {{Timestamp}}"

### Variables

The template uses two variables:
1. `{{Subject}}`: The name or identifier of the subject
2. `{{Timestamp}}`: The date and time when the QR was scanned

## Setup Steps

1. **Access Meta Developer Console**
   - Log in to [Meta Developer Console](https://developers.facebook.com)
   - Navigate to your WhatsApp app

2. **Create Template**
   - Go to WhatsApp > Getting Started
   - Click "Create Template"
   - Select "UTILITY" as the category
   - Enter template name: "qr_is_on"
   - Select language: "English (US)"

3. **Configure Template Body**
   - Enter the template body text
   - Add variables using the variable button:
     - Add `{{Subject}}` for the subject name
     - Add `{{Timestamp}}` for the scan time

4. **Submit for Review**
   - Review the template
   - Submit for approval
   - Wait for approval (usually 24-48 hours)

## Testing

1. **Using Test Script**
   ```bash
   python test_whatsapp.py
   ```

2. **Verification**
   - Check the response status
   - Verify message delivery
   - Confirm variable replacement

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

3. **Approval Delays**
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

3. **Monitoring**
   - Monitor template usage
   - Track delivery rates
   - Review error logs

## Support

For additional support:
1. Check Meta's [WhatsApp Business Platform Documentation](https://developers.facebook.com/docs/whatsapp)
2. Review the [WhatsApp Template Guidelines](https://developers.facebook.com/docs/whatsapp/cloud-api/message-templates)
3. Contact Meta Developer Support 