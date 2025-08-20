# Phase 2: Backend Rebranding Plan - Keryu (Subjects → Yus, QR Codes → Kers)

## Overview
This phase involves **structural changes** to models, database schema, business logic, and API endpoints. This transforms the application architecture to use the new terminology throughout the codebase.

**Risk Level:** High (structural changes)  
**Estimated Time:** 35-48 hours  
**Prerequisites:** Phase 1 must be completed successfully  
**Dependencies:** Database migration, comprehensive testing required

---

## 1. Database Migration Strategy

### 1.1 Pre-Migration Requirements
**Critical preparatory steps:**
- [ ] **Full database backup** (production and staging)
- [ ] Test migration on development copy
- [ ] Plan rollback strategy
- [ ] Schedule maintenance window
- [ ] Notify stakeholders of potential downtime

### 1.2 Migration Approach Options

#### Option A: Rename Existing Tables (Faster)
```sql
-- Advantages: Faster, preserves all data relationships
-- Disadvantages: Higher risk, harder to rollback

ALTER TABLE subjects_subject RENAME TO subjects_yu;
ALTER TABLE subjects_subjectqr RENAME TO subjects_yuker;

-- Update foreign key references
-- Update index names
-- Update constraint names
```

#### Option B: Create New Tables + Data Migration (Safer)
```sql
-- Advantages: Safer, easier rollback, can validate data
-- Disadvantages: Longer process, more complex

-- 1. Create new models alongside old ones
-- 2. Migrate data between tables
-- 3. Update all foreign key relationships
-- 4. Validate data integrity
-- 5. Drop old tables
```

**Recommended Approach:** Option B for production safety

### 1.3 Migration Files to Create
```
subjects/migrations/
├── XXXX_create_yu_model.py
├── XXXX_create_yuker_model.py
├── XXXX_migrate_subject_to_yu_data.py
├── XXXX_migrate_subjectqr_to_yuker_data.py
├── XXXX_update_foreign_keys.py
└── XXXX_remove_old_models.py
```

### 1.4 Data Integrity Validation
```python
# Validation checks in migrations
def validate_data_migration(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Yu = apps.get_model('subjects', 'Yu')
    
    assert Subject.objects.count() == Yu.objects.count()
    # Additional integrity checks
```

**Estimated Time:** 4-6 hours (including testing)

---

## 2. Model Class Definitions

### 2.1 Target Files
```
subjects/models.py
alarms/models.py
custodians/models.py
```

### 2.2 Primary Model Changes

#### subjects/models.py
```python
# Before
class Subject(models.Model):
    name = models.CharField(max_length=100)
    custodian = models.ForeignKey('custodians.Custodian', 
                                 on_delete=models.CASCADE, 
                                 related_name='subjects')

class SubjectQR(models.Model):
    subject = models.ForeignKey(Subject, 
                               on_delete=models.CASCADE,
                               related_name='qr_codes')

# After
class Yu(models.Model):
    name = models.CharField(max_length=100)
    custodian = models.ForeignKey('custodians.Custodian',
                                 on_delete=models.CASCADE,
                                 related_name='yus')
    
    class Meta:
        verbose_name = "Yu"
        verbose_name_plural = "Yus"
        db_table = 'subjects_yu'  # Custom table name

class YuKer(models.Model):
    yu = models.ForeignKey(Yu,
                          on_delete=models.CASCADE,
                          related_name='kers')
    
    class Meta:
        verbose_name = "Yu Ker"
        verbose_name_plural = "Yu Kers"
        db_table = 'subjects_yuker'
```

### 2.3 Related Model Updates

#### alarms/models.py
```python
# Update foreign key references
class Alarm(models.Model):
    yu = models.ForeignKey('subjects.Yu',  # Changed from 'subjects.Subject'
                          on_delete=models.CASCADE,
                          related_name='alarms')
    ker = models.ForeignKey('subjects.YuKer',  # Changed from 'subjects.SubjectQR'
                           on_delete=models.SET_NULL,
                           null=True,
                           related_name='alarms')
```

#### custodians/models.py
```python
# Update related name references where needed
# Check for any direct Subject model references
```

### 2.4 Method and Property Updates
```python
class Yu(models.Model):
    # Update method names and return values
    def __str__(self):
        return f"{self.name} (Custodian: {self.custodian})"
    
    # Update any custom methods
    def get_active_ker(self):  # was get_active_qr()
        return self.kers.filter(is_active=True).first()
```

**Estimated Time:** 6-8 hours

---

## 3. Views & Business Logic

### 3.1 Target Files
```
subjects/views.py
alarms/views.py
custodians/views.py
core/dev_dashboard.py
```

### 3.2 Function Name Updates

#### subjects/views.py
```python
# Function name changes
def subject_list(request):        → def yu_list(request):
def subject_create(request):      → def yu_create(request):
def subject_detail(request, pk):  → def yu_detail(request, pk):
def subject_edit(request, pk):    → def yu_edit(request, pk):
def subject_delete(request, pk):  → def yu_delete(request, pk):

# QR-related functions
def generate_qr_code(request):    → def generate_ker(request):
def toggle_qr_status(request):    → def toggle_ker_status(request):
def qr_codes_view(request):       → def kers_view(request):
```

### 3.3 Variable Name Updates
```python
# Variable and parameter changes
def yu_list(request):
    yus = Yu.objects.all()  # was: subjects = Subject.objects.all()
    
    context = {
        'yus': yus,         # was: 'subjects': subjects
        'total_yus': yus.count()  # was: 'total_subjects'
    }
    return render(request, 'subjects/yu_list.html', context)
```

### 3.4 Query Parameter Updates
```python
# URL parameter and form handling
def yu_detail(request, yu_id):  # was: subject_id
    yu = get_object_or_404(Yu, pk=yu_id)  # was: Subject
    kers = yu.kers.all()  # was: qr_codes
```

### 3.5 Context Variable Updates
```python
# Template context changes
context = {
    'yu': yu,                    # was: 'subject'
    'kers': kers,               # was: 'qr_codes'
    'active_ker': active_ker,   # was: 'active_qr'
    'yu_form': form,            # was: 'subject_form'
}
```

### 3.6 Related Views Updates

#### alarms/views.py
```python
# Update model references and filters
def alarm_list(request):
    alarms = Alarm.objects.select_related('yu', 'ker')  # was: 'subject', 'qr_code'
    
    # Filter updates
    yu_id = request.GET.get('yu')  # was: subject
    if yu_id:
        alarms = alarms.filter(yu_id=yu_id)  # was: subject_id
```

#### custodians/views.py
```python
# Dashboard statistics updates
def dashboard(request):
    yus = request.user.custodian.yus.all()  # was: subjects
    total_yus = yus.count()  # was: total_subjects
    active_kers = YuKer.objects.filter(yu__in=yus, is_active=True)  # was: SubjectQR
```

**Estimated Time:** 8-10 hours

---

## 4. URL Patterns & Routing

### 4.1 Target Files
```
subjects/urls.py
core/urls.py
subjects/api/urls.py
alarms/urls.py (references)
```

### 4.2 URL Pattern Name Updates

#### subjects/urls.py
```python
# URL pattern name changes
urlpatterns = [
    path('', views.yu_list, name='yu-list'),           # was: subject-list
    path('create/', views.yu_create, name='yu-create'), # was: subject-create
    path('<int:yu_id>/', views.yu_detail, name='yu-detail'), # was: subject_id
    path('<int:yu_id>/edit/', views.yu_edit, name='yu-edit'),
    path('<int:yu_id>/delete/', views.yu_delete, name='yu-delete'),
    
    # Ker-related URLs
    path('<int:yu_id>/kers/', views.kers_view, name='yu-kers'),  # was: qr-codes
    path('<int:yu_id>/generate-ker/', views.generate_ker, name='generate-ker'),
    path('ker/<uuid:uuid>/', views.ker_scan, name='ker-scan'),  # was: qr-scan
]
```

### 4.3 URL Parameter Updates
```python
# Parameter name changes in URL patterns
path('<int:yu_id>/', ...)     # was: <int:subject_id>
path('<uuid:ker_uuid>/', ...) # was: <uuid:qr_uuid>
```

### 4.4 Include Path Updates

#### core/urls.py
```python
# Check for any hardcoded URL references
urlpatterns = [
    path('yus/', include('subjects.urls')),  # Consider if this should change
    path('api/v1/yus/', include('subjects.api.urls')),  # API URL change
]
```

### 4.5 API URL Updates

#### subjects/api/urls.py
```python
urlpatterns = [
    path('yus/', views.yu_list_api, name='yu-list-api'),        # was: subjects
    path('yus/<int:yu_id>/', views.yu_detail_api, name='yu-detail-api'),
    path('kers/', views.ker_list_api, name='ker-list-api'),     # was: qr-codes
    path('kers/<uuid:ker_uuid>/', views.ker_detail_api, name='ker-detail-api'),
]
```

### 4.6 Reverse URL Updates
```python
# All reverse() calls need updating
redirect('subjects:yu-detail', yu_id=yu.id)  # was: subject-detail, subject_id
reverse('subjects:generate-ker', args=[yu.id])  # was: generate-qr
```

**Estimated Time:** 3-4 hours

---

## 5. API Layer Updates

### 5.1 Target Files
```
subjects/api/serializers.py
subjects/api/views.py
alarms/api/serializers.py
alarms/api/views.py
```

### 5.2 Serializer Class Updates

#### subjects/api/serializers.py
```python
# Serializer class name changes
class YuSerializer(serializers.ModelSerializer):  # was: SubjectSerializer
    class Meta:
        model = Yu  # was: Subject
        fields = '__all__'

class YuKerSerializer(serializers.ModelSerializer):  # was: SubjectQRSerializer
    class Meta:
        model = YuKer  # was: SubjectQR
        fields = '__all__'

# Nested serializer updates
class YuDetailSerializer(serializers.ModelSerializer):
    kers = YuKerSerializer(many=True, read_only=True)  # was: qr_codes
    active_ker = YuKerSerializer(read_only=True)       # was: active_qr
```

### 5.3 API View Updates

#### subjects/api/views.py
```python
# ViewSet class name changes
class YuViewSet(viewsets.ModelViewSet):  # was: SubjectViewSet
    serializer_class = YuSerializer      # was: SubjectSerializer
    queryset = Yu.objects.all()          # was: Subject
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Yu.objects.all()
        else:
            return Yu.objects.filter(custodian__user=self.request.user)

class YuKerViewSet(viewsets.ModelViewSet):  # was: SubjectQRViewSet
    serializer_class = YuKerSerializer
    queryset = YuKer.objects.all()
```

### 5.4 API Function Updates
```python
# Function-based API views
@api_view(['GET', 'POST'])
def yu_list_api(request):  # was: subject_list_api
    if request.method == 'GET':
        yus = Yu.objects.all()  # was: subjects = Subject.objects.all()
        serializer = YuSerializer(yus, many=True)
        return Response(serializer.data)
```

### 5.5 Related API Updates

#### alarms/api/serializers.py
```python
class AlarmSerializer(serializers.ModelSerializer):
    yu = YuSerializer(read_only=True)       # was: subject
    ker = YuKerSerializer(read_only=True)   # was: qr_code
    
    class Meta:
        model = Alarm
        fields = '__all__'
```

**Estimated Time:** 4-6 hours

---

## 6. Background Tasks & Celery

### 6.1 Target Files
```
subjects/tasks.py
alarms/tasks.py
core/celery.py
```

### 6.2 Task Function Updates

#### subjects/tasks.py
```python
# Task function name changes
@shared_task
def create_test_alarm_for_yu(yu_id):  # was: create_test_alarm_for_subject
    yu = Yu.objects.get(id=yu_id)     # was: Subject
    # Task logic updates

@shared_task
def generate_ker_image(yu_ker_id):    # was: generate_qr_image
    yu_ker = YuKer.objects.get(id=yu_ker_id)  # was: SubjectQR
```

#### alarms/tasks.py
```python
@shared_task
def send_whatsapp_notification(alarm_id):
    alarm = Alarm.objects.get(id=alarm_id)
    # Update message content
    message = f"Alert: {alarm.yu.name} has been located..."  # was: alarm.subject.name
    phone_str = str(alarm.yu.custodian.phone_number)         # was: alarm.subject.custodian
```

### 6.3 Celery Configuration Updates

#### core/celery.py
```python
# Task routing updates (if name-based)
CELERY_TASK_ROUTES = {
    'subjects.tasks.create_test_alarm_for_yu': {'queue': 'yus'},    # was: subjects
    'subjects.tasks.generate_ker_image': {'queue': 'kers'},         # was: qr_codes
}
```

### 6.4 Task Import Updates
```python
# Update all task imports
from subjects.tasks import create_test_alarm_for_yu  # was: create_test_alarm_for_subject
from subjects.tasks import generate_ker_image        # was: generate_qr_image
```

**Estimated Time:** 2-3 hours

---

## 7. Testing & Quality Assurance

### 7.1 Test File Updates
```
subjects/tests.py
alarms/tests.py
custodians/tests.py
tests/ (integration tests)
```

### 7.2 Model Test Updates

#### subjects/tests.py
```python
class YuModelTest(TestCase):  # was: SubjectModelTest
    def setUp(self):
        self.yu = Yu.objects.create(  # was: Subject
            name="Test Yu",
            custodian=self.custodian
        )
    
    def test_yu_creation(self):  # was: test_subject_creation
        self.assertEqual(self.yu.name, "Test Yu")
        self.assertTrue(isinstance(self.yu, Yu))

class YuKerModelTest(TestCase):  # was: SubjectQRModelTest
    def test_ker_generation(self):  # was: test_qr_generation
        ker = YuKer.objects.create(yu=self.yu)  # was: SubjectQR, subject
```

### 7.3 View Test Updates
```python
class YuViewTest(TestCase):  # was: SubjectViewTest
    def test_yu_list_view(self):  # was: test_subject_list_view
        response = self.client.get(reverse('subjects:yu-list'))  # was: subject-list
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.yu.name)
```

### 7.4 API Test Updates
```python
class YuAPITest(TestCase):  # was: SubjectAPITest
    def test_yu_api_list(self):  # was: test_subject_api_list
        url = reverse('subjects:yu-list-api')  # was: subject-list-api
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

### 7.5 Integration Test Updates
```python
class YuKerScanTest(TestCase):  # was: QRCodeScanTest
    def test_ker_scan_creates_alarm(self):  # was: test_qr_scan_creates_alarm
        ker = YuKer.objects.create(yu=self.yu, is_active=True)
        response = self.client.get(reverse('subjects:ker-scan', args=[ker.uuid]))
        
        # Verify alarm created
        alarm = Alarm.objects.first()
        self.assertEqual(alarm.yu, self.yu)     # was: alarm.subject
        self.assertEqual(alarm.ker, ker)        # was: alarm.qr_code
```

### 7.6 Test Data Factory Updates
```python
# If using factories (factory_boy)
class YuFactory(factory.django.DjangoModelFactory):  # was: SubjectFactory
    class Meta:
        model = Yu  # was: Subject
    
    name = factory.Faker('name')
    custodian = factory.SubFactory(CustodianFactory)

class YuKerFactory(factory.django.DjangoModelFactory):  # was: SubjectQRFactory
    class Meta:
        model = YuKer  # was: SubjectQR
    
    yu = factory.SubFactory(YuFactory)  # was: subject
```

### 7.7 Testing Requirements
**Critical test coverage:**
- [ ] All model operations (CRUD)
- [ ] All view responses (status codes, context)
- [ ] All API endpoints (serialization, permissions)
- [ ] All background tasks (execution, error handling)
- [ ] Database migration integrity
- [ ] Foreign key relationships
- [ ] Alarm creation workflow
- [ ] Notification sending
- [ ] User authentication and permissions

**Estimated Time:** 6-8 hours

---

## 8. Documentation Updates

### 8.1 Target Files
```
README.md
docs/scope.md
docs/technical_spec.md
docs/api.md
CLAUDE.md
```

### 8.2 Technical Documentation

#### README.md
- Update project description
- Update feature descriptions
- Update usage examples
- Update API endpoint documentation

#### docs/technical_spec.md
- Update architecture diagrams
- Update model relationship diagrams
- Update API endpoint specifications
- Update database schema documentation

#### docs/scope.md
- Update business terminology
- Update use case examples
- Update feature descriptions

### 8.3 Development Documentation

#### CLAUDE.md
- Update model names in examples
- Update common development tasks
- Update testing procedures
- Update deployment procedures

### 8.4 API Documentation
- Update OpenAPI/Swagger specifications
- Update endpoint descriptions
- Update request/response examples
- Update authentication documentation

**Estimated Time:** 2-3 hours

---

## Implementation Timeline

### Week 1: Migration Preparation
- **Day 1:** Database backup and migration strategy finalization
- **Day 2:** Migration script development and testing
- **Day 3:** Staging environment migration testing
- **Day 4:** Migration script refinement
- **Day 5:** Production migration planning and scheduling

### Week 2: Core Model Changes
- **Day 1:** Model class definition updates
- **Day 2:** Model relationship updates and testing
- **Day 3:** Database migration execution
- **Day 4:** Migration validation and rollback testing
- **Day 5:** Model method and property updates

### Week 3: Application Logic Updates
- **Day 1-2:** Views and business logic updates
- **Day 3:** URL pattern and routing updates
- **Day 4-5:** API layer updates and testing

### Week 4: Testing & Documentation
- **Day 1-2:** Background task updates
- **Day 3-4:** Comprehensive testing and bug fixes
- **Day 5:** Documentation updates and final validation

---

## Risk Mitigation

### High-Risk Areas

#### Database Migration Risks
- **Risk:** Data loss during migration
- **Mitigation:** 
  - Full database backup before migration
  - Test migration on staging environment
  - Use safe migration approach (Option B)
  - Have rollback plan ready

#### API Breaking Changes
- **Risk:** External API consumers affected
- **Mitigation:**
  - Version API endpoints (v1 → v2)
  - Deprecation notices for old endpoints
  - Maintain backward compatibility period
  - Document all breaking changes

#### Foreign Key Relationship Risks
- **Risk:** Broken relationships during migration
- **Mitigation:**
  - Comprehensive foreign key mapping
  - Data integrity validation scripts
  - Step-by-step migration with validation
  - Rollback capability at each step

### Testing Strategy
1. **Unit Tests:** All model operations and business logic
2. **Integration Tests:** End-to-end workflows
3. **API Tests:** All endpoint functionality
4. **Migration Tests:** Data integrity and rollback
5. **Performance Tests:** No degradation after changes

### Rollback Strategy

#### Emergency Rollback (if critical issues)
1. **Database Rollback:**
   ```bash
   # Restore from backup
   pg_restore --clean --if-exists -d keryu_db backup_before_migration.sql
   ```

2. **Code Rollback:**
   ```bash
   git checkout main
   git branch -D feature/backend-rebranding
   ```

#### Partial Rollback (if specific issues)
- Revert specific migration files
- Restore individual model changes
- Use git to selectively revert changes

---

## Success Criteria

### Phase 2 Complete When:
- [ ] All database tables use new names (Yu, YuKer)
- [ ] All Python code uses new model names
- [ ] All foreign key relationships work correctly
- [ ] All API endpoints use new terminology
- [ ] All background tasks function correctly
- [ ] All tests pass (100% test suite)
- [ ] No performance degradation
- [ ] Documentation is updated and accurate
- [ ] Migration can be rolled back if needed
- [ ] External API consumers can transition smoothly

### Production Deployment Ready When:
- [ ] Staging environment fully tested
- [ ] Migration scripts validated
- [ ] Rollback procedures tested
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Team training completed

---

## Post-Implementation Tasks

### Immediate (Week 1)
- [ ] Monitor application performance
- [ ] Track error rates and logs
- [ ] Validate data integrity
- [ ] Address any critical issues

### Short-term (Weeks 2-4)
- [ ] User feedback collection
- [ ] Performance optimization
- [ ] Bug fixes and refinements
- [ ] API consumer support

### Long-term (Months 1-3)
- [ ] Remove deprecated endpoints
- [ ] Clean up old migration files
- [ ] Performance analysis and optimization
- [ ] User adoption analysis

---

## Notes

### Critical Considerations
- **Backup is essential** - No migration without full backup
- **Test thoroughly** - Use staging environment extensively
- **Communicate changes** - Notify all stakeholders
- **Plan downtime** - Schedule maintenance window
- **Monitor closely** - Watch performance after deployment

### Dependencies
- Phase 1 must be completed successfully
- Database backup procedures must be in place
- Staging environment must be available
- Team must be trained on rollback procedures

This phase represents a fundamental transformation of the application architecture and should be approached with careful planning, thorough testing, and comprehensive backup strategies.