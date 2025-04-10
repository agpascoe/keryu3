# Plan to Improve Alarm System

## Overview
This document outlines the comprehensive plan to improve the alarm system by addressing documentation mismatches, model inconsistencies, and adding missing features.

## Phase 1: Documentation Update
1. Update `docs/alarms.md` to reflect current implementation
   - Remove outdated model definitions
   - Add current Alarm model structure
   - Update features section to match actual functionality
   - Add API documentation section

2. Create new documentation for notification system
   - Document current notification tracking mechanism
   - Add WhatsApp integration details
   - Document notification status flow

## Phase 2: Model Standardization
1. Standardize related names
   ```python
   # Change from:
   subject = models.ForeignKey('subjects.Subject', related_name='alarms')
   qr_code = models.ForeignKey('subjects.SubjectQR', related_name='alarms')
   
   # Add database indexes
   class Meta:
       indexes = [
           models.Index(fields=['timestamp'], name='alarms_timestamp_idx'),
           models.Index(fields=['notification_status'], name='alarms_status_idx'),
           models.Index(fields=['subject', 'timestamp'], name='alarms_subject_timestamp_idx'),
       ]
   ```

## Phase 3: Feature Enhancement
1. Add missing fields from documentation
   ```python
   resolved_at = models.DateTimeField(null=True, blank=True)
   resolution_notes = models.TextField(blank=True)
   scanned_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
   ```

2. Create NotificationAttempt model
   ```python
   class NotificationAttempt(models.Model):
       alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE)
       recipient = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE)
       channel = models.CharField(max_length=20)  # whatsapp, email, sms
       status = models.CharField(max_length=20, choices=NotificationStatus.CHOICES)
       sent_at = models.DateTimeField(null=True, blank=True)
       error_message = models.TextField(blank=True)
       retry_count = models.IntegerField(default=0)
   ```

## Phase 4: Migration Strategy
1. Create migration plan
   - Create backup of current data
   - Create new migrations for each change
   - Test migrations in development environment
   - Plan deployment strategy

2. Migration sequence
   ```python
   # 1. Add new fields
   # 2. Create NotificationAttempt model
   # 3. Update related names
   # 4. Add indexes
   ```

## Phase 5: Testing
1. Update existing tests
   - Modify AlarmTests to cover new fields
   - Add tests for notification attempts
   - Add tests for resolution workflow

2. Add new tests
   - Notification attempt creation
   - Status transitions
   - Resolution workflow
   - Index performance

## Phase 6: API Updates
1. Update serializers
   - Add new fields to AlarmSerializer
   - Create NotificationAttemptSerializer
   - Update API documentation

2. Update views
   - Add resolution endpoints
   - Add notification attempt endpoints
   - Update filtering options

## Phase 7: Frontend Updates
1. Update alarm list view
   - Add resolution status
   - Add notification attempt details
   - Update filters

2. Update alarm detail view
   - Add resolution section
   - Add notification history
   - Add resolution actions

## Implementation Order
1. Documentation Update (Phase 1)
   - Low risk, immediate value
   - Can be done without code changes

2. Model Standardization (Phase 2)
   - Foundation for other changes
   - Requires careful testing

3. Feature Enhancement (Phase 3)
   - Adds missing functionality
   - Requires database changes

4. Migration Strategy (Phase 4)
   - Ensures safe deployment
   - Requires careful planning

5. Testing (Phase 5)
   - Ensures reliability
   - Should be done in parallel with development

6. API Updates (Phase 6)
   - Exposes new functionality
   - Requires frontend coordination

7. Frontend Updates (Phase 7)
   - Completes the feature set
   - Requires UI/UX review

## Success Criteria
1. All documentation matches current implementation
2. No data loss during migrations
3. All tests passing
4. API endpoints working correctly
5. Frontend displaying all new information
6. Performance metrics maintained or improved

## Timeline Estimation
- Phase 1: 1 day
- Phase 2: 2 days
- Phase 3: 3 days
- Phase 4: 2 days
- Phase 5: 2 days
- Phase 6: 2 days
- Phase 7: 3 days

Total estimated time: 15 days

## Risks and Mitigation
1. Data Migration Risks
   - Mitigation: Thorough testing in development
   - Backup strategy
   - Rollback plan

2. Performance Impact
   - Mitigation: Monitor query performance
   - Add appropriate indexes
   - Test with large datasets

3. Integration Issues
   - Mitigation: Comprehensive testing
   - API versioning if needed
   - Clear documentation

## Next Steps
1. Review and approve plan
2. Set up development environment
3. Begin with Phase 1
4. Regular progress reviews
5. Continuous testing throughout implementation 