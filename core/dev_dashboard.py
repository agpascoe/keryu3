"""
Development Dashboard for Keryu3
Provides web-based interface for development tasks and monitoring
"""
import os
import sys
import subprocess
import json
import psutil
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line
from django.test import Client
from django.urls import reverse


def get_system_status():
    """Get comprehensive system status information"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Django processes
        django_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower() and 'manage.py' in ' '.join(proc.info['cmdline'] or []):
                    django_processes.append({
                        'pid': proc.info['pid'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'cmdline': ' '.join(proc.info['cmdline'] or [])
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Database status
        db_status = "Unknown"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "Connected"
        except Exception as e:
            db_status = f"Error: {str(e)}"
        
        # Django settings
        django_settings = {
            'DEBUG': getattr(settings, 'DEBUG', 'Unknown'),
            'DATABASE_ENGINE': getattr(settings, 'DATABASES', {}).get('default', {}).get('ENGINE', 'Unknown'),
            'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', []),
            'STATIC_URL': getattr(settings, 'STATIC_URL', 'Unknown'),
            'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'Unknown'),
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'disk_total': disk.total,
            },
            'django_processes': django_processes,
            'database_status': db_status,
            'django_settings': django_settings,
            'environment': {
                'python_version': sys.version,
                'django_version': getattr(settings, 'VERSION', 'Unknown'),
                'working_directory': os.getcwd(),
            }
        }
    except Exception as e:
        return {'error': str(e)}


def get_test_results():
    """Get recent test results"""
    try:
        # Check if test files exist
        test_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        # Try to run a quick test
        test_output = ""
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'test', '--verbosity=0'],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            test_output = "Test execution timed out"
        except Exception as e:
            test_output = f"Test execution failed: {str(e)}"
        
        return {
            'test_files': test_files,
            'last_test_output': test_output,
            'test_files_count': len(test_files)
        }
    except Exception as e:
        return {'error': str(e)}


def get_log_files():
    """Get available log files and their sizes"""
    try:
        log_files = []
        log_patterns = ['*.log', '*.txt']
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(file.endswith(pattern.replace('*', '')) for pattern in log_patterns):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                        log_files.append({
                            'name': file,
                            'path': file_path,
                            'size': size,
                            'size_mb': round(size / (1024 * 1024), 2),
                            'modified': modified.isoformat(),
                        })
                    except OSError:
                        pass
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        return []


@csrf_exempt
def dev_dashboard(request):
    """Main development dashboard view"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start_server':
            try:
                # Start development server
                subprocess.Popen([
                    'python', 'manage.py', 'runserver', '0.0.0.0:8000'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return JsonResponse({'status': 'success', 'message': 'Server started'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        elif action == 'stop_server':
            try:
                # Stop development server
                subprocess.run(['pkill', '-f', 'python manage.py runserver'])
                return JsonResponse({'status': 'success', 'message': 'Server stopped'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        elif action == 'run_tests':
            try:
                # Run tests
                result = subprocess.run(
                    ['python', 'manage.py', 'test'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return JsonResponse({
                    'status': 'success',
                    'output': result.stdout + result.stderr,
                    'return_code': result.returncode
                })
            except subprocess.TimeoutExpired:
                return JsonResponse({'status': 'error', 'message': 'Tests timed out'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        elif action == 'check_django':
            try:
                # Check Django configuration
                result = subprocess.run(
                    ['python', 'manage.py', 'check'],
                    capture_output=True,
                    text=True
                )
                return JsonResponse({
                    'status': 'success',
                    'output': result.stdout + result.stderr,
                    'return_code': result.returncode
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
    
    # GET request - show dashboard
    context = {
        'system_status': get_system_status(),
        'test_results': get_test_results(),
        'log_files': get_log_files(),
        'current_time': datetime.now().isoformat(),
    }
    
    return render(request, 'dev_dashboard.html', context)


@csrf_exempt
def dev_api_status(request):
    """API endpoint for system status"""
    return JsonResponse(get_system_status())


@csrf_exempt
def dev_api_tests(request):
    """API endpoint for test results"""
    return JsonResponse(get_test_results())


@csrf_exempt
def dev_api_logs(request):
    """API endpoint for log files"""
    return JsonResponse({'log_files': get_log_files()})


@csrf_exempt
def dev_api_log_content(request, log_file):
    """API endpoint for log file content"""
    try:
        # Security: only allow reading log files
        if not log_file.endswith('.log') and not log_file.endswith('.txt'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        
        # Find the log file
        log_path = None
        for root, dirs, files in os.walk('.'):
            if log_file in files:
                log_path = os.path.join(root, log_file)
                break
        
        if not log_path:
            return JsonResponse({'error': 'Log file not found'}, status=404)
        
        # Read last 100 lines
        with open(log_path, 'r') as f:
            lines = f.readlines()
            content = ''.join(lines[-100:])  # Last 100 lines
        
        return JsonResponse({
            'content': content,
            'file': log_file,
            'total_lines': len(lines)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def dev_api_qr_test(request):
    """API endpoint for QR code testing"""
    try:
        from subjects.models import Subject
        from subjects.utils import generate_qr_code
        
        # Get a test subject or create one
        subject, created = Subject.objects.get_or_create(
            name="Test Subject",
            defaults={
                'phone_number': '+1234567890',
                'emergency_contact': 'Test Emergency Contact',
                'emergency_phone': '+1234567891'
            }
        )
        
        # Generate QR code
        qr_data = generate_qr_code(subject)
        
        return JsonResponse({
            'subject_id': subject.id,
            'subject_name': subject.name,
            'qr_data': qr_data,
            'created': created
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def dev_api_notification_test(request):
    """API endpoint for notification testing"""
    try:
        from notifications.utils import send_notification
        
        # Test notification
        result = send_notification(
            phone_number='+1234567890',
            message='Test notification from development dashboard',
            subject_id=None
        )
        
        return JsonResponse({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 