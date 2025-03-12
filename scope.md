# Keryu3 Project Scope

## Overview
Keryu3 is a full-stack system for managing and monitoring vulnerable people (elderly and children, referred to as "subjects"). The system provides a comprehensive platform for custodians to register and monitor their subjects, with emergency alert capabilities through QR codes and WhatsApp integration.

## Core Features

### 1. Subject Management ⏳
- [ ] Personal information storage
- [ ] Medical history and conditions
- [ ] Emergency contact details
- [ ] Hospital preferences
- [ ] Custodian associations
- [ ] Document attachments (medical records, etc.)

### 2. Custodian System 🚧
- [x] User registration and authentication
- [ ] Subject creation and management
- [ ] Multiple custodians per subject
- [x] WhatsApp number verification setup
- [x] Dashboard with subject overview
- [ ] Notification preferences

### 3. QR Code System ⏳
- [ ] Unique QR code generation for each subject
- [ ] Printable credential generation
- [ ] QR code scanning and validation
- [ ] Emergency information display
- [ ] Access logging

### 4. Alert System ⏳
- [ ] QR code scan triggers
- [ ] WhatsApp notifications
- [ ] Email notifications (optional)
- [ ] Alert history
- [ ] Alert status tracking

### 5. API Integration ⏳
- [ ] RESTful API architecture
- [ ] WhatsApp Business API integration
- [ ] QR code generation API
- [ ] Emergency alert API endpoints

## Technical Implementation

### Frontend ✅
- [x] Django templates
- [x] Bootstrap 5 UI framework
- [x] Responsive design
- [x] Custom CSS styling
- [x] User-friendly forms

### Backend 🚧
- [x] Django 5.0 framework
- [x] REST API architecture
- [x] Authentication system
- [ ] Database models
- [ ] Business logic

### Security 🚧
- [x] User authentication
- [ ] Data encryption
- [x] CSRF protection
- [ ] API security
- [ ] Privacy compliance

### Database Schema 🚧
- [x] Users/Custodians
- [ ] Subjects
- [ ] Medical Information
- [ ] Emergency Contacts
- [ ] Alerts/Notifications
- [ ] Audit Logs

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

### In Progress 🚧
1. Database models design
2. Subject management system
3. Basic CRUD operations

### Pending 📋
1. QR code generation system
2. WhatsApp integration
3. Alert system
4. API endpoints
5. Testing
6. Documentation

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
- ⏳ In Progress/Pending
- 🔒 Security Feature
- 📋 To Do
- �� Under Construction 