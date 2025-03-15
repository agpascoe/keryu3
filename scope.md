# Keryu - Subject Management System

## Project Overview
Keryu is a comprehensive subject management system designed to help track and manage subjects with their associated QR codes and alarms. The system provides features for both administrators and custodians to manage subjects, generate QR codes, and monitor alarms.

Example of one case (among others) where kareyu is helpful:
The parent of a child is leting him/her to go to the zoo with his/her school mates (and teachers). Suddenly this child is lost and a Person find him/her. This Person uses de QR that this child has(in his/her badge), and his/her parent (custodian), recieves a Whatsapp message with the alarm. From here the parent call the teacher to check the situation.
For doing this, the parent had to signup in keryu, create the subject record with his/her child data, see and print the QR that keryu gave him/her.

Example of Subjects are: children, elders, and especial persons with disabilities

## Core Features

### Subject Management
- Create, read, update, and delete subjects
- Track subject details including:
  - Personal information (name, date of birth, gender)
  - Medical information (conditions, allergies, medications)
  - Doctor information (name, phone, speciality, address)
  - Photo upload capability
  - Active/Inactive status

### QR Code System
- Generate unique QR codes for each subject
- Multiple QR codes per subject support
- QR code activation/deactivation functionality
- QR code download and image generation
- Last used timestamp tracking
- UUID-based QR code identification

### Alarm System
- Automatic alarm creation on QR code scanning
- Location tracking support (latitude/longitude)
- WhatsApp notification integration
- Alarm history tracking
- Notification status monitoring

### User Roles and Permissions
- Admin users with full system access
- Custodian users with limited access to their subjects
- Staff-only access to certain features
- Role-based view filtering

### Reporting and Statistics
- Subject statistics dashboard
- Gender distribution
- Custodian distribution
- Active/Inactive subject counts
- Export capabilities (Excel, PDF)

## Technical Stack
- Django 4.2+
- PostgreSQL database
- Redis for caching and Celery tasks
- Celery for background task processing
- QR code generation with qrcode library
- Report generation with reportlab and xlsxwriter
- Chart visualization with django-chartjs

## Security Features
- Role-based access control
- Secure QR code generation with UUID
- Permission checks on all operations
- Staff-only access to sensitive features
- Secure file upload handling

## Future Enhancements
- Enhanced location tracking
- Mobile application integration
- Advanced reporting features
- API endpoints for external integration
- Enhanced notification system
- Subject activity timeline
- Document management system

## User Roles and Access Levels

### Anonymous Users
- Can access public pages only
- Can register as a custodian
- Can log in if they have an account

### Custodians (Authenticated Users)
- Can manage their own profile information
- Can view and manage their assigned subjects
- Can access the dashboard with their subjects' information
- Cannot access admin features or other custodians' subjects

### Admin Users
- Full access to all system features
- Can manage all subjects across all custodians
- Access to administrative dashboard with statistics
- Can generate and manage QR codes for all subjects
- Can create, edit, and delete any subject
- Access to detailed statistics and reports

## Technical Implementation

### Models
- User (Django's built-in)
- Custodian (Profile model)
- Subject (Main data model)

### Forms
- Registration forms
- Subject management forms
- Profile update forms

### Views
- Public views
- Custodian views
- Admin views
- API endpoints (future)

### Templates
- Base templates
- Admin templates
- Subject management templates
- Error pages

## Testing Coverage
- Unit tests for all models
- Integration tests for workflows
- Access control tests
- Form validation tests
- Error handling tests

## Future Enhancements
- API implementation
- Mobile application
- Advanced reporting
- Batch operations
- Export/Import functionality
- Email notifications
- WhatsApp integration

## Technical Requirements
- Python 3.11+
- Django 5.0+
- PostgreSQL (production)
- Bootstrap 5
- Chart.js for visualizations
- Phone number field support
- File upload handling

## Project Progress

### Completed ✅
1. Project setup
2. Environment configuration
3. Basic frontend structure
4. Template system
5. Static files organization
6. Custodian authentication system
7. Registration and login forms
8. Dashboard template
9. Subject management system (CRUD)
10. Medical information storage
11. Admin interface configuration
12. Basic access control implementation

### In Progress 🚧
1. Enhanced access control for custodians
2. Subject-custodian relationship enforcement
3. QR code system
4. WhatsApp integration setup
5. Alert system design

### Pending 📋
1. WhatsApp integration
2. Alert system
3. API endpoints
4. Testing
5. Documentation

## Timeline
- Phase 1: Basic Setup and Structure ✅
- Phase 2: Core Features Development 🚧
- Phase 3: Integration and Testing ⏳
- Phase 4: Deployment and Documentation ⏳

## Notes
- The system prioritizes user privacy and data security
- WhatsApp integration requires Business API access
- QR codes should be easily printable and durable
- System should be scalable for future enhancements

## Legend
- ✅ Completed
- 🚧 In Progress
- ⏳ Pending
- 🔒 Security Feature
- 📋 To Do

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

2. **Frontend**
   - Bootstrap-based responsive design
   - JavaScript for dynamic interactions
   - QR code generation and management
   - Charts and statistics visualization

3. **External Services**
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