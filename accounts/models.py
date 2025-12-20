from django.db import models

# Create your models here.
class OTP(models.Model):
    email = models.CharField(max_length=100)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
