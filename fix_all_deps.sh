#!/bin/bash

echo "🔧 Fixing all dependencies..."

# Deactivate and reactivate
deactivate 2>/dev/null
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Uninstall wrong Django version
pip uninstall Django -y 2>/dev/null

# Install correct versions
pip install Django==5.1.3
pip install djangorestframework==3.15.2
pip install django-filter==25.1
pip install django-cors-headers==4.4.0
pip install psycopg2-binary==2.9.10
pip install dj-database-url==3.1.2
pip install python-dotenv==1.0.1
pip install whitenoise==6.9.0
pip install gunicorn==23.0.0

echo ""
echo "✅ Installed packages:"
pip list | grep -E "Django|django-cors|psycopg|dj-database|whitenoise"

echo ""
echo "✅ Verifying imports..."
python -c "
import django
import corsheaders
import rest_framework
import django_filters
import whitenoise
print('All imports successful!')
print(f'Django version: {django.get_version()}')
"
