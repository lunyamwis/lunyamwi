from django.db import models
from api.helpers.models import BaseModel

# Create your models here.
class ScoutingMaster(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name



class Scout(BaseModel):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=5)
    city = models.CharField(max_length=20)
    code = models.IntegerField()
    available = models.BooleanField(default=False)
    master = models.ForeignKey(ScoutingMaster,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self) -> str:
        return self.username
    
class Device(BaseModel):
    STATUS_CHOICES = (
        (0,'AVAILABLE'),
        (1,'ACTIVE'),
        (2,'CHALLLENGE REQUIRED')
    )
    app_version = models.CharField(max_length=25)
    android_version = models.IntegerField()
    android_release = models.CharField(max_length=20)
    dpi=models.CharField(max_length=27)
    resolution=models.CharField(max_length=20)
    manufacturer = models.CharField(max_length=30)
    device = models.CharField(max_length=22)
    model = models.CharField(max_length=22)
    cpu = models.CharField(max_length=20)
    version_code = models.CharField(max_length=22)
    status = models.IntegerField(choices=STATUS_CHOICES,default=0)
    scout = models.ForeignKey(Scout,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self) -> str:
        return f"{self.manufacturer}-{self.device}"
