#!/usr/bin/env python
"""
Manual Test Script for Keryu Messaging System
This script helps test the messaging functionality across different channels.
"""

import os
import django
import sys
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.messaging import MessageService, MessageChannel
from core.models import SystemParameter
from custodians.models import Custodian
from subjects.models import Subject, Alarm

def print_header(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def test_channel(channel_name, channel_value):
    print(f"\nTesting {channel_name}...")
    
    # Set the channel
    param, created = SystemParameter.objects.get_or_create(
        parameter='channel',
        defaults={'value': channel_value}
    )
    if not created:
        param.value = channel_value
        param.save()
    
    # Create message service
    service = MessageService()
    
    # Get test phone number
    phone_number = input(f"\nEnter test phone number (E.164 format, e.g., +5212345678901): ")
    
    # Send test message
    message = f"Test message from Keryu System via {channel_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"\nSending message: {message}")
    
    result = service.send_message(
        to_number=phone_number,
        message=message
    )
    
    print("\nResult:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Channel: {result.get('channel', 'unknown')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    if result.get('meta_result'):
        print(f"Meta API Result: {result['meta_result']}")
    
    return result

def main():
    print_header("Keryu Messaging System - Manual Test Script")
    
    while True:
        print("\nAvailable tests:")
        print("1. Test Meta WhatsApp API")
        print("2. Test Twilio WhatsApp")
        print("3. Test Twilio SMS")
        print("4. Test Channel Fallback")
        print("5. Test All Channels")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            test_channel("Meta WhatsApp API", MessageChannel.META_WHATSAPP.value)
        
        elif choice == '2':
            test_channel("Twilio WhatsApp", MessageChannel.TWILIO_WHATSAPP.value)
        
        elif choice == '3':
            test_channel("Twilio SMS", MessageChannel.TWILIO_SMS.value)
        
        elif choice == '4':
            print_header("Testing Channel Fallback")
            
            # Start with Meta WhatsApp
            result = test_channel("Meta WhatsApp API", MessageChannel.META_WHATSAPP.value)
            
            if result.get('status') == 'error':
                print("\nMeta WhatsApp failed. Falling back to Twilio WhatsApp...")
                result = test_channel("Twilio WhatsApp", MessageChannel.TWILIO_WHATSAPP.value)
                
                if result.get('status') == 'error':
                    print("\nTwilio WhatsApp failed. Falling back to Twilio SMS...")
                    test_channel("Twilio SMS", MessageChannel.TWILIO_SMS.value)
        
        elif choice == '5':
            print_header("Testing All Channels")
            test_channel("Meta WhatsApp API", MessageChannel.META_WHATSAPP.value)
            test_channel("Twilio WhatsApp", MessageChannel.TWILIO_WHATSAPP.value)
            test_channel("Twilio SMS", MessageChannel.TWILIO_SMS.value)
        
        elif choice == '6':
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest script interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
    finally:
        print("\nTest script completed.") 