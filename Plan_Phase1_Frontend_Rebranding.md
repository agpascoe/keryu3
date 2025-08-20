# Phase 1: Frontend Rebranding Plan - Keryu (Subjects → Yus, QR Codes → Kers)

## Overview
This phase focuses on **look and feel changes only** - updating all user-facing text from "Subjects" to "Yus" and "QR Codes" to "Kers" without modifying any backend logic, database schema, or model definitions.

**Risk Level:** Very Low (cosmetic changes only)  
**Estimated Time:** 9-14 hours  
**Rollback Strategy:** Simple text replacement in reverse  

## 1. Template Updates

### 1.1 Target Files
All user-facing text in HTML templates:

```
templates/subjects/
├── admin_subject_list.html
├── admin_subject_form.html
├── admin_subject_confirm_delete.html
├── subject_list.html
├── subject_form.html
├── subject_detail.html
├── subject_confirm_delete.html
├── qr_codes.html
├── print_qr.html
└── scan_form.html

templates/custodians/
├── dashboard.html
├── subject_list.html
├── subject_form.html
├── subject_detail.html
├── subject_qr_codes.html
└── register.html

templates/alarms/
├── alarm_list.html
├── alarm_detail.html
├── alarm_statistics.html
└── admin_dashboard.html

templates/
├── base.html (navigation menus)
└── home.html (landing page)
```

### 1.2 Text Replacements
**Primary terminology changes:**
- "Subject" → "Yu"
- "Subjects" → "Yus" 
- "QR Code" → "Ker"
- "QR Codes" → "Kers"

**Specific UI elements:**
- "Generate QR Code" → "Generate Ker"
- "Subject Management" → "Yu Management"
- "Add Subject" → "Add Yu"
- "Edit Subject" → "Edit Yu"
- "Subject Details" → "Yu Details"
- "QR Code Management" → "Ker Management"
- "Download QR" → "Download Ker"
- "Print QR Codes" → "Print Kers"
- "Active QR Code" → "Active Ker"
- "QR Code Status" → "Ker Status"

### 1.3 Navigation & Breadcrumbs
**Files:** `templates/base.html`
- Main navigation menu items
- Breadcrumb navigation
- Footer links (if any)
- Mobile menu items

### 1.4 Page Titles & Headers
Update all `<title>` tags and main headers:
- "Subject List" → "Yu List"
- "Create New Subject" → "Create New Yu"
- "QR Code Generator" → "Ker Generator"

**Estimated Time:** 4-6 hours

---

## 2. Form Labels & Help Text

### 2.1 Target Files
```
subjects/forms.py
custodians/forms.py
alarms/forms.py (if any references)
```

### 2.2 Changes Required
**Form field labels:**
```python
# Before
label="Subject Name"
label="Subject Photo"
help_text="Subject's medical conditions"

# After
label="Yu Name"
label="Yu Photo"
help_text="Yu's medical conditions"
```

**Form titles and descriptions:**
- Form class verbose names
- Field help text visible to users
- Validation error messages containing terminology

### 2.3 Specific Form Updates
- `SubjectForm` field labels (keeping class name for now)
- `SubjectQRForm` field labels
- Any custodian forms that reference subjects
- Error messages and validation text

**Estimated Time:** 1-2 hours

---

## 3. Admin Interface Display

### 3.1 Target Files
```
subjects/admin.py
custodians/admin.py
alarms/admin.py
```

### 3.2 Admin Configuration Updates
**Model Meta verbose names:**
```python
# In model Meta classes (display only)
verbose_name = "Yu"
verbose_name_plural = "Yus"
```

**Admin list displays:**
- Column headers in admin list views
- Filter option labels
- Search field descriptions
- Inline form titles

### 3.3 Admin Interface Elements
- Admin sidebar menu items
- Breadcrumb navigation in admin
- Action descriptions
- Help text for admin fields

**Estimated Time:** 1-2 hours

---

## 4. Static Files (CSS/JS)

### 4.1 Target Files
```
static/js/ (all JavaScript files)
static/css/ (any text content)
subjects/static/ (if exists)
```

### 4.2 JavaScript Updates
**Chart labels and data visualization:**
```javascript
// Before
"Subjects by Date"
"Total Subjects"
"QR Code Scans"

// After
"Yus by Date" 
"Total Yus"
"Ker Scans"
```

**User interaction messages:**
- Alert messages
- Confirmation dialogs
- Loading messages
- Error notifications
- Success messages

### 4.3 AJAX and Dynamic Content
- AJAX response messages
- Dynamic form labels
- Real-time update notifications
- Status messages

### 4.4 Console and Debug Messages (Optional)
- Console.log messages for debugging
- Error logging text
- Development helper messages

**Estimated Time:** 2-3 hours

---

## 5. API Documentation

### 5.1 Target Files
```
subjects/api/serializers.py (help_text only)
core/urls.py (API schema descriptions)
```

### 5.2 Swagger/OpenAPI Updates
**API endpoint descriptions:**
- Endpoint summaries and descriptions
- Parameter descriptions
- Response field documentation
- Example request/response text

**Field documentation:**
```python
# In serializers (help_text only)
help_text="Yu's full name"
help_text="Active Ker for this Yu"
```

### 5.3 API Schema Updates
- OpenAPI schema descriptions
- Field labels in API docs
- Example values and descriptions

**Estimated Time:** 1 hour

---

## Implementation Checklist

### Pre-Implementation
- [ ] Create feature branch: `feature/frontend-rebranding`
- [ ] Backup current templates (optional)
- [ ] Document current terminology for rollback

### Phase 1.1: Templates (4-6 hours)
- [ ] Update `templates/subjects/` directory
- [ ] Update `templates/custodians/` directory  
- [ ] Update `templates/alarms/` directory
- [ ] Update main templates (`base.html`, `home.html`)
- [ ] Test all pages render correctly
- [ ] Verify no broken links or missing content

### Phase 1.2: Forms (1-2 hours)
- [ ] Update `subjects/forms.py` labels and help_text
- [ ] Update `custodians/forms.py` references
- [ ] Update any alarm form references
- [ ] Test form rendering and validation

### Phase 1.3: Admin Interface (1-2 hours)
- [ ] Update admin.py verbose_name fields
- [ ] Update admin list display headers
- [ ] Update admin field help_text
- [ ] Test admin interface functionality

### Phase 1.4: Static Files (2-3 hours)
- [ ] Update JavaScript chart labels
- [ ] Update user interaction messages
- [ ] Update AJAX response text
- [ ] Test all JavaScript functionality

### Phase 1.5: API Documentation (1 hour)
- [ ] Update serializer help_text
- [ ] Update API schema descriptions
- [ ] Test Swagger documentation display

### Testing & Validation
- [ ] Full application walkthrough
- [ ] Test all forms and user interactions
- [ ] Verify admin interface works correctly
- [ ] Check API documentation display
- [ ] Mobile responsiveness check
- [ ] Cross-browser testing (if needed)

### Post-Implementation
- [ ] Collect user feedback on new terminology
- [ ] Document any issues or confusion
- [ ] Prepare for Phase 2 planning

---

## Quality Assurance

### Testing Strategy
1. **Manual Testing:**
   - Navigate through all pages
   - Fill out all forms
   - Check admin interface
   - Verify charts and statistics display

2. **Content Verification:**
   - Search for remaining "Subject" references
   - Search for remaining "QR" references
   - Verify consistent terminology usage

3. **User Experience Testing:**
   - Test with actual users (if possible)
   - Gather feedback on terminology clarity
   - Note any confusion or suggestions

### Search Commands for Verification
```bash
# Search for remaining old terminology in templates
grep -r "Subject" templates/
grep -r "QR Code" templates/
grep -r "QR" templates/ | grep -v "Ker"

# Search in static files
grep -r "Subject" static/
grep -r "QR Code" static/
```

---

## Rollback Plan

### If Issues Arise
1. **Quick Rollback:**
   ```bash
   git checkout main
   git branch -D feature/frontend-rebranding
   ```

2. **Partial Rollback:**
   - Reverse specific text changes
   - Use git to revert individual files
   - Restore from backup if needed

### Rollback Text Replacements
- "Yu" → "Subject"
- "Yus" → "Subjects"
- "Ker" → "QR Code"
- "Kers" → "QR Codes"

---

## Success Criteria

### Phase 1 Complete When:
- [ ] All user-facing text uses new terminology (Yu/Ker)
- [ ] No references to "Subject/QR Code" in UI
- [ ] All forms display correctly with new labels
- [ ] Admin interface shows new terminology
- [ ] Charts and statistics use new labels
- [ ] API documentation reflects new terminology
- [ ] No functionality is broken
- [ ] User feedback on terminology is collected

### Ready for Phase 2 When:
- [ ] All frontend changes are stable
- [ ] No critical issues reported
- [ ] User acceptance of new terminology
- [ ] All tests pass
- [ ] Code review completed

---

## Notes

### Important Considerations
- **No backend changes** in this phase
- **Database remains unchanged**
- **API endpoints remain the same**
- **Model names stay as Subject/SubjectQR**
- **URL patterns unchanged**

### What This Phase Does NOT Include
- Model class renaming
- Database schema changes
- URL pattern changes
- API endpoint changes
- File/directory renaming
- Python variable name changes

This phase focuses purely on the **user experience** and **visual terminology** to validate the rebranding concept before committing to structural changes in Phase 2.