# Keryu3 Project Scope

## Overview
Keryu3 is a comprehensive subject management system designed to help custodians and administrators manage subject information efficiently and securely.

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

## Core Features

### Authentication and Authorization
- User registration with email verification
- Secure login system
- Password reset functionality
- Role-based access control
- Session management

### Subject Management
- CRUD operations for subjects
- Comprehensive subject profiles including:
  - Personal information (name, date of birth, gender)
  - Medical information (conditions, allergies, medications)
  - Doctor's information (name, phone, speciality, address)
  - Photo upload capability
  - Active/inactive status tracking

### Admin Features
1. Subject List View
   - View all subjects across all custodians
   - Quick access to subject details
   - Filtering and sorting capabilities
   - Bulk operations support

2. Subject Statistics
   - Total subjects count
   - Gender distribution
   - Subjects per custodian
   - Active vs. inactive subjects
   - Visual charts and graphs

3. QR Code Management
   - Generate QR codes for subjects
   - Print QR codes individually or in bulk
   - QR code linking to subject profiles

4. Detailed Subject View
   - Complete subject information
   - Medical history
   - Doctor's contact details
   - Photo gallery
   - Edit and delete options

### Security Features
- CSRF protection
- Form validation
- Phone number format validation
- Secure file uploads
- Permission-based access control
- 403 Forbidden responses for unauthorized access

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