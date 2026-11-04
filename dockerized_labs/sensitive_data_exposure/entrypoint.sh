#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations dataexposure
python manage.py migrate

# Create a demo user if it doesn't exist
echo "Setting up demo user..."

python manage.py shell << END
from django.contrib.auth.models import User
from dataexposure.models import UserData

user = [
    {"username1" : "user1", "password" : "pass123"}
    {"username2" : "user2", "password" : "pass123"}
    {"username3" : "user3", "password" : "pass123"}
]

for u in users : 
    user,created = User.objects.get_or_create(username=u["username"])
    if created:
    user.set_password(u["username"])
    user.save()

    UserData.objects.get_or_create(
    user=user,
    credit_card="3249873572365",
    ssn="42542524252"
    )

print("Demo users created")
END



# Create a superuser too (commented out by default)
# echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell

echo "✅ Setup complete! Starting server..."

# Start the main process
exec "$@"
