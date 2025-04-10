# Plan to Update Nginx Configuration

## Overview
This plan outlines the steps to safely update the Nginx configuration file using a combination of backup and secure file writing methods.

## Steps

### 1. Create Backup
```bash
sudo cp /etc/nginx/sites-available/keryu.mx /etc/nginx/sites-available/keryu.mx.backup.$(date +%Y%m%d)
```

### 2. Create Temporary File
```bash
sudo nano /tmp/keryu.mx.new
```
- Copy the new configuration content
- Save and exit

### 3. Validate Configuration
```bash
sudo nginx -t -c /tmp/keryu.mx.new
```

### 4. Apply New Configuration
```bash
sudo tee /etc/nginx/sites-available/keryu.mx < /tmp/keryu.mx.new
```

### 5. Set Proper Permissions
```bash
sudo chown root:root /etc/nginx/sites-available/keryu.mx
sudo chmod 644 /etc/nginx/sites-available/keryu.mx
```

### 6. Test and Reload
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Cleanup
```bash
sudo rm /tmp/keryu.mx.new
```

## Rollback Plan
If something goes wrong:
1. Restore from backup:
```bash
sudo cp /etc/nginx/sites-available/keryu.mx.backup.$(date +%Y%m%d) /etc/nginx/sites-available/keryu.mx
```
2. Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Verification
After applying changes:
1. Check Nginx status:
```bash
sudo systemctl status nginx
```
2. Verify SSL configuration:
```bash
curl -I https://keryu.mx
```
3. Check error logs:
```bash
sudo tail -f /var/log/nginx/keryu.mx.error.log
```

## Notes
- All commands require sudo privileges
- Keep backup files for at least 7 days
- Monitor logs after applying changes
- Test all critical functionality after update 