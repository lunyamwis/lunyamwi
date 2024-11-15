from django.db import models

# Create your models here.
class DatabaseCred(models.Model):
    name = models.CharField(max_length=200)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name