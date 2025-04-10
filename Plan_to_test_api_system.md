# Plan to Test API System

## Overview
This document outlines a comprehensive testing strategy for the Keryu3 API system, covering all endpoints, authentication, authorization, and edge cases.

## Phase 1: Authentication Testing
1. Token-based Authentication
   - Test token generation
   - Test token validation
   - Test token expiration
   - Test token refresh
   - Test token revocation

2. Permission Testing
   - Test staff vs non-staff access
   - Test custodian access restrictions
   - Test unauthorized access attempts
   - Test role-based permissions

## Phase 2: Subjects API Testing
1. List Subjects Endpoint (`GET /api/v1/subjects/`)
   - Test staff access (all subjects)
   - Test custodian access (filtered subjects)
   - Test pagination
   - Test filtering
   - Test sorting

2. Create Subject Endpoint (`POST /api/v1/subjects/`)
   - Test valid subject creation
   - Test invalid data handling
   - Test required fields validation
   - Test custodian assignment
   - Test duplicate handling

3. Subject Detail Endpoint (`GET /api/v1/subjects/{id}/`)
   - Test staff access
   - Test custodian access
   - Test non-existent subject
   - Test unauthorized access

4. Update Subject Endpoint (`PUT /api/v1/subjects/{id}/`)
   - Test valid updates
   - Test invalid updates
   - Test custodian restriction
   - Test field validation

5. Delete Subject Endpoint (`DELETE /api/v1/subjects/{id}/`)
   - Test staff deletion
   - Test custodian deletion attempt
   - Test cascade effects
   - Test non-existent subject

## Phase 3: Alarms API Testing
1. List Alarms Endpoint (`GET /api/v1/alarms/`)
   - Test staff access
   - Test custodian access
   - Test filtering by date
   - Test filtering by status
   - Test pagination
   - Test sorting

2. Create Alarm Endpoint (`POST /api/v1/alarms/`)
   - Test valid alarm creation
   - Test invalid data handling
   - Test subject validation
   - Test QR code validation
   - Test notification triggering

3. Alarm Detail Endpoint (`GET /api/v1/alarms/{id}/`)
   - Test staff access
   - Test custodian access
   - Test non-existent alarm
   - Test unauthorized access

4. Update Alarm Endpoint (`PUT /api/v1/alarms/{id}/`)
   - Test valid updates
   - Test invalid updates
   - Test status transitions
   - Test notification updates

5. Delete Alarm Endpoint (`DELETE /api/v1/alarms/{id}/`)
   - Test staff deletion
   - Test custodian deletion attempt
   - Test cascade effects
   - Test non-existent alarm

6. Alarm Resolution Endpoint (`POST /api/v1/alarms/{id}/resolve/`)
   - Test valid resolution
   - Test invalid resolution
   - Test resolution notes
   - Test status updates

## Phase 4: Notification Testing
1. Notification Attempts
   - Test attempt creation
   - Test status updates
   - Test retry mechanism
   - Test error handling

2. WhatsApp Integration
   - Test message sending
   - Test delivery status
   - Test error handling
   - Test rate limiting

3. Notification Status
   - Test status transitions
   - Test status updates
   - Test status history
   - Test status validation

## Phase 5: Statistics API Testing
1. Alarm Statistics (`GET /api/v1/alarms/statistics/`)
   - Test date range filtering
   - Test subject statistics
   - Test notification statistics
   - Test time distribution
   - Test data aggregation

2. Subject Statistics
   - Test alarm frequency
   - Test notification success rate
   - Test time-based analysis
   - Test data filtering

## Phase 6: Error Handling Testing
1. Input Validation
   - Test invalid data types
   - Test missing required fields
   - Test field length limits
   - Test format validation

2. Error Responses
   - Test 400 Bad Request
   - Test 401 Unauthorized
   - Test 403 Forbidden
   - Test 404 Not Found
   - Test 500 Internal Server Error

3. Rate Limiting
   - Test request limits
   - Test time windows
   - Test blocking rules
   - Test exemption rules

## Phase 7: Performance Testing
1. Load Testing
   - Test concurrent requests
   - Test response times
   - Test resource usage
   - Test database performance

2. Stress Testing
   - Test system limits
   - Test recovery
   - Test error handling
   - Test resource cleanup

## Implementation Order
1. Authentication Testing (Phase 1)
   - Foundation for all other tests
   - Critical security component

2. Subjects API Testing (Phase 2)
   - Core functionality
   - Required for alarm testing

3. Alarms API Testing (Phase 3)
   - Main business logic
   - Complex interactions

4. Notification Testing (Phase 4)
   - External integrations
   - Async operations

5. Statistics API Testing (Phase 5)
   - Data aggregation
   - Complex queries

6. Error Handling Testing (Phase 6)
   - Edge cases
   - Security measures

7. Performance Testing (Phase 7)
   - System limits
   - Scalability

## Success Criteria
1. All endpoints tested
2. All error cases covered
3. All permission levels tested
4. All integrations tested
5. Performance metrics met
6. Security requirements met

## Timeline Estimation
- Phase 1: 1 day
- Phase 2: 2 days
- Phase 3: 2 days
- Phase 4: 2 days
- Phase 5: 1 day
- Phase 6: 1 day
- Phase 7: 1 day

Total estimated time: 10 days

## Risks and Mitigation
1. Integration Issues
   - Mitigation: Mock external services
   - Test in isolation
   - Document dependencies

2. Performance Issues
   - Mitigation: Monitor metrics
   - Test incrementally
   - Document baselines

3. Security Issues
   - Mitigation: Regular security reviews
   - Penetration testing
   - Access control verification

## Next Steps
1. Set up test environment
2. Create test data
3. Implement test cases
4. Run automated tests
5. Document results
6. Address issues
7. Review and approve 