# Keryu - Subject Management System

## Project Overview
Keryu is a comprehensive subject management system designed to help track and manage subjects with their associated QR codes and alarms. The system provides features for both administrators and custodians to manage subjects, generate QR codes, and monitor alarms, with secure email verification for new accounts.

Example of one case (among others) where Keryu is helpful:
A parent of a child is letting them go to the zoo with their school mates (and teachers). If the child gets lost and someone finds them, that person can scan the QR code on the child's badge. The parent (custodian) immediately receives a WhatsApp message with the alarm details. From there, the parent can contact the teacher to check the situation.

To use the system, the parent needs to:
1. Sign up in Keryu
2. Create a subject record with their child's data
3. Generate and print the QR code
4. Attach the QR code to the child's badge or belongings

Examples of Subjects that can be tracked:
- Children
- Elderly people
- Persons with disabilities

## Core Features

### User Authentication and Security
- Email verification required for new accounts
- Development mode with instant verification
- Secure token-based verification system
- Role-based access control
- Staff/Admin separation from custodians

### Dashboard System
- Admin dashboard with real-time statistics
  - Total non-staff custodians count
  - Subject statistics
  - QR code tracking
  - Alarm monitoring
- Custodian dashboard with personalized views
  - Personal subject management
  - Individual QR code tracking
  - Personal alarm history

### Subject Management
- Create, read, update, and delete subjects
- Track subject details including:
  - Personal information (name, date of birth, gender)
  - Medical information (conditions, allergies, medications)
  - Doctor information (name, phone, specialty, address)
  - Photo upload capability
  - Active/Inactive status

### QR Code System
- Generate unique QR codes for each subject
- One active QR code per subject at a time
- QR code activation/deactivation functionality
- QR code download and printing
- Last used timestamp tracking
- UUID-based QR code identification
- Bulk printing capability
- **Recent Fixes and Improvements:**
  - Fixed buffer handling by resetting buffer position before saving images
  - Improved error handling with try/except blocks and proper error responses
  - Enhanced media handling using FileResponse and cache control headers
  - Added frontend resilience with error handlers and placeholder images
  - Implemented automatic retry mechanism with cache-busting
  - Improved logging with additional debug information and size tracking
  - Consolidated QR code generation with consistent parameters
  - Fixed file system permissions for staticfiles directory

### Alarm System
- Automatic alarm creation on QR code scanning
- Location tracking support (latitude/longitude)
- WhatsApp notification integration
- Alarm history tracking
- Notification status monitoring
- Retry mechanism for failed notifications

### User Roles and Permissions
- Admin users with full system access
- Custodian users with limited access to their subjects
- Staff-only access to certain features
- Role-based view filtering

### WhatsApp Integration
- Real-time notifications using Meta WhatsApp Business API
- Template-based messaging
- Delivery status tracking
- Error handling and retry logic
- Notification history

## Technical Stack

### Backend
- Django 5.0+
- Python 3.11+
- PostgreSQL database
- Redis for Celery tasks
- Celery for background processing

### Frontend
- Bootstrap 5
- JavaScript/jQuery
- Chart.js for visualizations
- QR code generation library

### External Services
- Meta WhatsApp Business Platform
- WhatsApp message templates

## Security Features
- Role-based access control
- Secure QR code generation with UUID
- Permission checks on all operations
- Staff-only access to sensitive features
- Secure file upload handling
- CSRF protection
- Secure password handling

## Project Status

### Completed ✅
1. Project setup and configuration
2. Environment setup
3. Frontend structure and templates
4. Authentication system
5. Subject management (CRUD)
6. QR code generation and management
7. WhatsApp integration
8. Alarm system
9. Notification tracking
10. Error handling and logging

### In Progress 🚧
1. Enhanced reporting features
2. Advanced search capabilities
3. Mobile responsiveness improvements
4. Documentation updates

### Planned 📋
1. API endpoints for external integration
2. Mobile application
3. Enhanced analytics
4. Batch operations for subjects
5. Advanced notification preferences

## Notes
- The system prioritizes user privacy and data security
- QR codes contain only UUIDs, no personal information
- WhatsApp notifications use approved message templates
- System is designed for scalability
- Error handling includes retry mechanisms
- All actions are logged for auditing

## Legend
- ✅ Completed
- 🚧 In Progress
- 📋 Planned
- 🔒 Security Feature

### User Roles and Access Levels

1. **Public Users**
   - Can scan QR codes
   - Can view emergency information when scanning valid QR codes
   - No login required

2. **Custodians**
   - Full management of their subjects
   - Generate and manage QR codes for their subjects
   - View alarm history for their subjects
   - Receive WhatsApp notifications when their subjects' QR codes are scanned
   - Access to statistics and reports for their subjects

3. **Admin Users**
   - Full system access
   - Manage all custodians and subjects
   - View system-wide statistics
   - Access to all QR codes and alarm history

### Core Features

1. **Subject Management**
   - Create, update, and delete subject profiles
   - Store medical information and emergency contacts
   - Upload and manage subject photos
   - Track subject status and history

2. **QR Code System**
   - Generate unique QR codes for subjects
   - One active QR code per subject at a time
   - QR code activation/deactivation
   - Download and print QR codes
   - QR codes contain only UUID (no personal data)

3. **Alarm System**
   - Record all QR code scans as alarms
   - Track scan location and timestamp
   - Automatic WhatsApp notifications to custodians
   - Alarm history and reporting
   - Statistics and analytics

4. **Security and Privacy**
   - Secure authentication system
   - Role-based access control
   - No personal information in QR codes
   - Encrypted data transmission
   - Activity logging

### Technical Requirements

1. **Backend**
   - Django framework
   - PostgreSQL database
   - REST API endpoints for QR scanning
   - WhatsApp API integration
   - Celery for async tasks
   - Redis for message broker and result backend
   - Process management via startup script
   - Single instance management for critical services

2. **Process Management**
   - Automated service startup and shutdown
   - Health checks for all services
   - Instance verification
   - Process cleanup
   - Conda environment management
   - Service dependency handling

3. **Services**
   - Redis server (message broker)
   - Celery worker (task processing)
   - Celery beat (scheduled tasks)
   - Django development server
   - All services managed via unified script

4. **Frontend**
   - Bootstrap-based responsive design
   - JavaScript for dynamic interactions
   - QR code generation and management
   - Charts and statistics visualization

5. **External Services**
   - WhatsApp Business API
   - QR code generation library
   - Geolocation services (optional)

### Out of Scope
- Mobile app development
- Custom QR scanner implementation
- Real-time video monitoring
- Payment processing
- Multi-language support (future enhancement)

### Success Criteria
1. Custodians can successfully manage QR codes
2. QR codes can be scanned with standard mobile phones
3. WhatsApp notifications are delivered within 1 minute of scanning
4. System maintains accurate alarm history
5. Statistics and reports are accurate and up-to-date
6. All services start and run reliably via startup script
7. No duplicate service instances running simultaneously

### User Registration and Authentication

1. **Custodian Registration Requirements**
   - Target Users:
     * Parents/Guardians of children
     * Caregivers for elderly
     * Support staff for persons with disabilities
   - Geographic Scope:
     * Initially Mexico only
     * Phone number validation for Mexican numbers
     * Future expansion planned for other regions

2. **Registration Process Scope**
   - User Information Collection:
     * Basic personal information
     * Contact details
     * Security credentials
   - Verification Requirements:
     * Two-factor authentication
     * WhatsApp verification
     * Email validation (future implementation)
   - Security Measures:
     * Password strength enforcement
     * Phone number validation
     * Duplicate account prevention

3. **WhatsApp Integration Scope**
   - Verification System:
     * Code generation and delivery
     * Attempt tracking
     * Expiration handling
   - Message Templates:
     * Verification code format
     * Welcome messages
     * Error notifications
   - Fallback Mechanisms:
     * Alternative verification methods
     * Error recovery procedures
     * Support contact options

4. **Data Management**
   - User Profile Data:
     * Required fields
     * Optional information
     * Privacy considerations
   - Verification Data:
     * Code storage and handling
     * Attempt tracking
     * Session management
   - Security Requirements:
     * Data encryption
     * Session handling
     * Access control

5. **Support and Maintenance**
   - Registration Support:
     * Error handling
     * User guidance
     * Problem resolution
   - System Monitoring:
     * Success rate tracking
     * Error logging
     * Performance metrics
   - Continuous Improvement:
     * User feedback integration
     * Process optimization
     * Security updates 