from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    category = models.CharField(max_length=50)

    def set_password(self, password):
        """Hash the password and store it."""
        self.password = make_password(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password(password, self.password)
    def __str__(self):
        return self.name