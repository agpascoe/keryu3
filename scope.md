# Keryu3 Project Scope

## Overview
Keryu3 is a full-stack system for managing and monitoring vulnerable people (elderly and children, referred to as "subjects"). The system provides a comprehensive platform for custodians to register and monitor their subjects, with emergency alert capabilities through QR codes and WhatsApp integration.

## Core Features

### 1. Subject Management 🚧
- [x] Personal information storage
- [x] Medical history and conditions
- [x] Emergency contact details
- [ ] Hospital preferences
- [x] Custodian associations
- [ ] Document attachments (medical records, etc.)

### 2. Custodian System 🚧
- [x] User registration and authentication
- [x] Subject creation and management
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
- [x] Database models
- [x] Business logic

### Security 🚧
- [x] User authentication
- [ ] Data encryption
- [x] CSRF protection
- [ ] API security
- [ ] Privacy compliance

### Database Schema 🚧
- [x] Users/Custodians
- [x] Subjects
- [x] Medical Information
- [x] Emergency Contacts
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
9. Subject management system (CRUD)
10. Medical information storage

### In Progress 🚧
1. QR code system
2. WhatsApp integration setup
3. Alert system design

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