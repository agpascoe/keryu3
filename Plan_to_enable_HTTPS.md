# Plan to Enable HTTPS for Keryu Application

## Objective
Enable HTTPS access for the Keryu application using the existing `keryu.mx` domain and Let's Encrypt SSL certificates.

## Current State Analysis
- Application is running on HTTP via IP address (18.217.144.210)
- Domain `keryu.mx` is pointing to the server
- Original HTTPS configuration exists but is disabled
- Django settings have HTTPS redirect disabled for testing

## Implementation Plan

### Phase 1: Verify Domain and SSL Certificate Status
1. **Check domain resolution**
   - Verify `keryu.mx` resolves to current server IP
   - Test domain accessibility

2. **Check SSL certificate status**
   - Verify Let's Encrypt certificates exist
   - Check certificate validity and expiration
   - Verify certificate paths in Nginx configuration

### Phase 2: Restore Original Nginx Configuration
1. **Backup current configuration**
   - Save current IP-based configuration
   - Document current working state

2. **Restore domain-based configuration**
   - Re-enable original `keryu.mx` configuration
   - Verify SSL certificate paths
   - Test Nginx configuration syntax

### Phase 3: Re-enable Django HTTPS Settings
1. **Update Django settings**
   - Re-enable `SECURE_SSL_REDIRECT = True`
   - Re-enable secure cookie settings
   - Maintain security headers

2. **Restart Django application**
   - Restart Gunicorn with new settings
   - Verify HTTPS redirect functionality

### Phase 4: Testing and Verification
1. **Test HTTPS functionality**
   - Verify HTTPS access via domain
   - Test HTTP to HTTPS redirect
   - Verify all endpoints work over HTTPS

2. **Security verification**
   - Check SSL certificate validity
   - Verify security headers
   - Test mixed content issues

## Success Criteria
- ✅ HTTPS accessible via `https://keryu.mx`
- ✅ HTTP redirects to HTTPS automatically
- ✅ All application endpoints work over HTTPS
- ✅ SSL certificate is valid and trusted
- ✅ No mixed content warnings
- ✅ Security headers properly configured

## Rollback Plan
- Keep IP-based configuration as backup
- Can quickly revert to HTTP-only if issues arise
- Document all changes for easy reversal

## Implementation Steps

### Step 1: Verify Domain and SSL Status
```bash
# Check domain resolution
nslookup keryu.mx
dig keryu.mx

# Check SSL certificate status
sudo certbot certificates
ls -la /etc/letsencrypt/live/keryu.mx/
```

### Step 2: Restore Original Nginx Configuration
```bash
# Backup current config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Restore original config
sudo cp /etc/nginx/sites-available/keryu.mx /etc/nginx/sites-available/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Re-enable Django HTTPS Settings
```bash
# Update settings.py
# Re-enable SECURE_SSL_REDIRECT and secure cookies

# Restart application
./startup.sh restart
```

### Step 4: Test HTTPS Functionality
```bash
# Test HTTPS access
curl -I https://keryu.mx/
curl -I http://keryu.mx/  # Should redirect to HTTPS

# Test application endpoints
curl -I https://keryu.mx/admin/
curl -I https://keryu.mx/custodians/register/
```

## Risk Assessment
- **Low Risk**: Original configuration exists and is tested
- **Mitigation**: Keep backup configuration for quick rollback
- **Testing**: Verify each step before proceeding to next

## Timeline
- **Phase 1**: 5 minutes (verification)
- **Phase 2**: 10 minutes (configuration)
- **Phase 3**: 5 minutes (Django settings)
- **Phase 4**: 10 minutes (testing)
- **Total**: ~30 minutes

## Notes
- Follow the plan step by step
- Test after each phase
- Keep backup configurations
- Document any issues encountered 