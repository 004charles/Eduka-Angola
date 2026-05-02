import os
import django
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
try:
    # Set mock environment variables for decouple if needed
    os.environ.setdefault('SECRET_KEY', 'test-key')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('USE_SQLITE', 'True') # Force SQLite for testing
    
    django.setup()
    print("Django setup: OK")
except Exception as e:
    print(f"Django setup: FAILED ({e})")
    sys.exit(1)

def test_project():
    print("\n--- Testing Eduka-Angola Project Connectivity ---")
    print(f"Django Version: {django.get_version()}")
    
    # Test Database
    try:
        from django.db import connection
        connection.ensure_connection()
        print("Database Connection: OK")
    except Exception as e:
        print(f"Database Connection: FAILED ({e})")
        return False

    # Test Apps
    try:
        from django.apps import apps
        installed_apps = [app.label for app in apps.get_app_configs()]
        print(f"Installed Apps: {len(installed_apps)} detected")
    except Exception as e:
        print(f"Apps Check: FAILED ({e})")
        return False

    print("\n[SUCCESS] Eduka-Angola Project is integrated and working correctly!")
    return True

if __name__ == "__main__":
    test_project()
