# Script Deprecation Notice

## 🚨 Deprecated Scripts

The following scripts have been **DEPRECATED** to avoid confusion and maintain consistency:

### Deprecated Files:
- `shutdown.sh` → Use `./startup.sh stop`
- `dev_startup.sh` → Use `./startup.sh dev`  
- `dev_env.sh` → Use `./startup.sh [command]`

## ✅ Single Entry Point: startup.sh

All service management is now handled through **`startup.sh`** with the following commands:

### Production Services:
```bash
./startup.sh start    # Start all production services (Gunicorn, Nginx, Redis, Celery)
./startup.sh stop     # Stop all services  
./startup.sh restart  # Restart all services
```

### Development:
```bash
./startup.sh dev      # Start development server
```

### Status:
```bash
./startup.sh status   # Show service status
```

### Help:
```bash
./startup.sh          # Show usage help
```

## 🔄 Automatic Redirection

The deprecated scripts now show a warning message and automatically redirect to the appropriate `startup.sh` command after 3 seconds.

## 📋 Benefits of Consolidation:

1. **Single Source of Truth**: One script to manage all services
2. **Consistent Interface**: Same command structure for all operations  
3. **Reduced Confusion**: No need to remember multiple script names
4. **Better Maintenance**: Easier to update and maintain one script
5. **Clear Documentation**: All commands documented in one place

## 🗑️ Future Cleanup

The deprecated script files can be safely deleted in the future once all team members are familiar with the new `startup.sh` workflow.

---

**Last Updated**: $(date)
**Status**: Active Deprecation Phase