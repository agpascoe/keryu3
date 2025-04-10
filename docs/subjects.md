# Subject Management System

## Overview
The Subject Management System is a core component of Keryu that handles the creation, management, and tracking of subjects (children, elders, or persons with disabilities) through QR codes and associated information.

## Models

### Subject Model
```python
class Subject(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    custodian = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=100, blank=True)
    doctor_phone = PhoneNumberField(blank=True, null=True)
    doctor_address = models.TextField(blank=True)
    doctor_speciality = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='subject_photos/')
    is_active = models.BooleanField(default=True)
```

### SubjectQR Model
```python
class SubjectQR(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='qr_codes/')
```

## Features

### Subject Management
1. **Creation**
   - Basic information (name, DOB, gender)
   - Medical information (conditions, allergies, medications)
   - Doctor information (name, phone, address, specialty)
   - Photo upload
   - Active/Inactive status

2. **QR Code Management**
   - One active QR code per subject
   - Automatic deactivation of old codes
   - QR code image generation
   - Last used tracking
   - UUID-based identification

3. **Photo Management**
   - Image upload support
   - Storage in media directory
   - Automatic resizing
   - Format validation
   - Security checks

### Security Features
1. **Access Control**
   - Custodian-specific access
   - Staff access for all subjects
   - Permission-based views
   - Action restrictions

2. **Data Protection**
   - Input validation
   - XSS prevention
   - CSRF protection
   - File upload security

### API Endpoints

#### Subject Management
- `GET /api/subjects/` - List subjects
- `POST /api/subjects/` - Create subject
- `GET /api/subjects/{id}/` - Get subject details
- `PUT /api/subjects/{id}/` - Update subject
- `DELETE /api/subjects/{id}/` - Delete subject

#### QR Code Management
- `GET /api/subjects/{id}/qr-codes/` - List QR codes
- `POST /api/subjects/{id}/qr-codes/` - Generate QR code
- `PUT /api/qr-codes/{uuid}/` - Update QR code
- `DELETE /api/qr-codes/{uuid}/` - Delete QR code

## Views and Templates

### Subject Views
1. **List View**
   - Pagination
   - Filtering
   - Sorting
   - Search functionality

2. **Detail View**
   - Subject information
   - QR codes
   - Photo display
   - Action buttons

3. **Form Views**
   - Create form
   - Edit form
   - Photo upload
   - Validation

### QR Code Views
1. **Generation**
   - UUID generation
   - Image creation
   - Storage handling
   - Activation process

2. **Management**
   - List view
   - Status toggle
   - Image display
   - Download options

## Tasks and Background Jobs

### QR Code Generation
- Asynchronous processing
- Image optimization
- Storage management
- Cache handling

### Cleanup Tasks
- Old QR code cleanup
- Unused image removal
- Status updates
- Database maintenance

## Error Handling

### Validation Errors
- Form validation
- File validation
- Data integrity
- Permission checks

### Processing Errors
- Image generation
- Storage errors
- Database errors
- API errors

## Best Practices

### Data Management
1. **Subject Data**
   - Regular backups
   - Data validation
   - Update tracking
   - History logging

2. **QR Codes**
   - Unique identification
   - Status tracking
   - Usage monitoring
   - Cleanup procedures

### Performance
1. **Optimization**
   - Database indexing
   - Query optimization
   - Cache usage
   - Image optimization

2. **Monitoring**
   - Usage statistics
   - Error tracking
   - Performance metrics
   - Resource usage

## Testing

### Unit Tests
- Model tests
- View tests
- Form tests
- Task tests

### Integration Tests
- API tests
- File handling
- Database operations
- Cache operations

### Manual Testing
- UI testing
- QR code scanning
- Photo upload
- Permission checks 