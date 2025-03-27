#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations dataexposure
python manage.py migrate

# Create a demo user if it doesn't exist
echo "Setting up demo user..."
# this is a mess but it works
echo "from django.contrib.auth.models import User; from dataexposure.models import UserData; demo_user = User.objects.filter(username='demo').exists() or User.objects.create_user('demo', 'demo@example.com', 'demopass'); user = User.objects.get(username='demo'); UserData.objects.filter(user=user).exists() or UserData.objects.create(user=user, credit_card='4111111111111111', ssn='123456789', api_key='demokey123456789')" | python manage.py shell

# TODO: need to add more test users to demo the API
# maybe add user1, user2, user3 with different data

# Create a superuser too (commented out by default)
# echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell

echo "✅ Setup complete! Starting server..."

# Start the main process
exec "$@"
