from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    def is_staff_role(self):
        return self.role == self.Role.STAFF

    def is_student_role(self):
        return self.role == self.Role.STUDENT
