# Keryu3 Development Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Directory Navigation Issues

#### Problem: "manage.py not found" Error
```
python: can't open file '/home/ubuntu/manage.py': [Errno 2] No such file or directory
```

**Root Cause**: Running commands from wrong directory (`/home/ubuntu` instead of `/home/ubuntu/keryu3`)

**Solutions**:
1. **Use Enhanced Script** (Recommended):
   ```bash
   ./dev_env.sh start
   ```
   The script will automatically navigate to the correct directory.

2. **Manual Navigation**:
   ```bash
   cd /home/ubuntu/keryu3
   python manage.py runserver
   ```

3. **Check Current Directory**:
   ```bash
   pwd
   ls -la manage.py
   ```

**Prevention**: Always use `./dev_env.sh` commands instead of direct Django commands.

---

### Server Issues

#### Problem: Port 8000 Already in Use
```
Error: That port is already in use.
```

**Solutions**:
1. **Use Enhanced Script** (Recommended):
   ```bash
   ./dev_env.sh restart
   ```

2. **Manual Port Check**:
   ```bash
   lsof -i :8000
   pkill -f "python manage.py runserver"
   ```

3. **Use Different Port**:
   ```bash
   python manage.py runserver 0.0.0.0:8001
   ```

#### Problem: Server Won't Start
```
Error starting server
```

**Diagnostic Steps**:
1. **Check Environment**:
   ```bash
   ./dev_env.sh status
   ```

2. **Check Django Configuration**:
   ```bash
   python manage.py check
   ```

3. **Check Logs**:
   ```bash
   ./dev_env.sh logs
   tail -f django.log
   ```

**Solutions**:
1. **Recreate Environment**:
   ```bash
   conda deactivate
   conda remove -n keryu --all
   conda create -n keryu python=3.11
   conda activate keryu
   pip install -r requirements.txt
   ```

2. **Reset Database**:
   ```bash
   python manage.py flush
   ```

---

### Environment Issues

#### Problem: Conda Environment Not Activated
```
conda: command not found
```

**Solutions**:
1. **Initialize Conda**:
   ```bash
   source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
   conda activate keryu
   ```

2. **Add to .bashrc**:
   ```bash
   echo 'source /home/ubuntu/miniconda3/etc/profile.d/conda.sh' >> ~/.bashrc
   source ~/.bashrc
   ```

#### Problem: Missing Dependencies
```
ModuleNotFoundError: No module named 'django'
```

**Solutions**:
1. **Reinstall Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Environment**:
   ```bash
   conda list
   pip list
   ```

3. **Force Reinstall**:
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

---

### Database Issues

#### Problem: Database Connection Error
```
django.db.utils.OperationalError: no such table
```

**Solutions**:
1. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Check Database**:
   ```bash
   python manage.py check --database default
   ```

3. **Reset Database** (Development Only):
   ```bash
   python manage.py flush
   ```

#### Problem: Migration Issues
```
django.db.utils.OperationalError: table already exists
```

**Solutions**:
1. **Fake Migrations**:
   ```bash
   python manage.py migrate --fake
   ```

2. **Reset Migrations**:
   ```bash
   python manage.py migrate subjects zero
   python manage.py migrate subjects
   ```

---

### Testing Issues

#### Problem: Tests Fail
```
AssertionError: Test failed
```

**Diagnostic Steps**:
1. **Run Tests Verbosely**:
   ```bash
   python manage.py test --verbosity=2
   ```

2. **Run Specific Test**:
   ```bash
   python manage.py test subjects.tests.TestSubject
   ```

3. **Check Test Data**:
   ```bash
   ./dev_env.sh data
   ```

**Solutions**:
1. **Reset Test Database**:
   ```bash
   python manage.py test --keepdb
   ```

2. **Check Test Configuration**:
   ```bash
   python manage.py check
   ```

---

### API Issues

#### Problem: API Endpoints Not Working
```
404 Not Found
```

**Solutions**:
1. **Check URL Configuration**:
   ```bash
   python manage.py show_urls
   ```

2. **Test API Endpoints**:
   ```bash
   curl http://localhost:8000/api/v1/subjects/
   ```

3. **Check Authentication**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'
   ```

---

### Static Files Issues

#### Problem: Static Files Not Loading
```
404 Not Found for CSS/JS files
```

**Solutions**:
1. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

2. **Check Static Settings**:
   ```bash
   python manage.py check
   ```

3. **Serve Static Files**:
   ```bash
   python manage.py runserver --insecure
   ```

---

### Log Issues

#### Problem: No Logs Generated
```
No log files found
```

**Solutions**:
1. **Check Log Configuration**:
   ```bash
   python manage.py check
   ```

2. **Create Log Directory**:
   ```bash
   mkdir -p logs
   ```

3. **Check File Permissions**:
   ```bash
   ls -la django.log
   chmod 666 django.log
   ```

---

### Performance Issues

#### Problem: Slow Development Server
```
Server response is slow
```

**Solutions**:
1. **Monitor Resources**:
   ```bash
   # Use development dashboard
   http://localhost:8000/dev/
   ```

2. **Check Database Queries**:
   ```bash
   python manage.py shell
   from django.db import connection
   connection.queries
   ```

3. **Optimize Settings**:
   ```bash
   # Check DEBUG setting
   python manage.py shell
   from django.conf import settings
   print(settings.DEBUG)
   ```

---

## 🔧 Diagnostic Commands

### System Health Check
```bash
# Comprehensive status check
./dev_env.sh status

# Check Django configuration
python manage.py check

# Check database
python manage.py check --database default

# Check static files
python manage.py check --deploy
```

### Process Management
```bash
# Check running processes
ps aux | grep python

# Kill Django processes
pkill -f "python manage.py runserver"

# Check port usage
lsof -i :8000
```

### Log Analysis
```bash
# View recent logs
./dev_env.sh logs

# Follow logs in real-time
tail -f django.log

# Search for errors
grep -i error django.log

# Search for specific patterns
grep -i "manage.py" django.log
```

### Environment Verification
```bash
# Check Python version
python --version

# Check Django version
python -c "import django; print(django.get_version())"

# Check conda environment
conda info

# Check installed packages
pip list
```

---

## 🚨 Emergency Procedures

### Complete Reset (Nuclear Option)
```bash
# Stop all processes
pkill -f "python manage.py runserver"

# Deactivate environment
conda deactivate

# Remove environment
conda remove -n keryu --all

# Recreate environment
conda create -n keryu python=3.11
conda activate keryu

# Reinstall dependencies
pip install -r requirements.txt

# Reset database
python manage.py flush

# Start fresh
./dev_env.sh start
```

### Database Recovery
```bash
# Backup current database
cp db.sqlite3 db.sqlite3.backup

# Reset database
python manage.py flush

# Restore from backup if needed
cp db.sqlite3.backup db.sqlite3
```

### File Permission Issues
```bash
# Fix permissions
chmod -R 755 .
chmod 666 django.log
chmod 666 db.sqlite3
```

---

## 📞 Getting Help

### Self-Help Resources
1. **Development Dashboard**: http://localhost:8000/dev/
2. **Django Documentation**: https://docs.djangoproject.com/
3. **Project Documentation**: Check `docs/` directory

### Debugging Tools
```bash
# Django debug toolbar
http://localhost:8000/__debug__/

# Development dashboard
http://localhost:8000/dev/

# API documentation
http://localhost:8000/swagger/
```

### Log Locations
- **Django Logs**: `django.log`
- **Development Logs**: `dev.log`
- **Test Logs**: `test_output.log`
- **Celery Logs**: `celery_worker.log`

### Useful Commands Summary
```bash
# Quick fixes
./dev_env.sh restart    # Restart everything
./dev_env.sh status     # Check status
./dev_env.sh logs       # View logs

# Manual fixes
python manage.py check  # Check Django
python manage.py migrate # Fix database
pkill -f "python manage.py runserver" # Kill server
```

---

## 🎯 Prevention Tips

### Best Practices
1. **Always use `./dev_env.sh`** instead of direct Django commands
2. **Check status regularly** with `./dev_env.sh status`
3. **Monitor logs** for early warning signs
4. **Keep environment clean** by regularly updating dependencies
5. **Use development dashboard** for real-time monitoring

### Regular Maintenance
```bash
# Daily
./dev_env.sh status

# Weekly
pip list --outdated
python manage.py check --deploy

# Monthly
conda update conda
pip install --upgrade -r requirements.txt
```

---

**Remember**: Most issues can be resolved by using the enhanced development script (`./dev_env.sh`) which includes automatic error handling and recovery procedures. 