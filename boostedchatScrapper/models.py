from django.db import models
from api.helpers.models import BaseModel

class Link(BaseModel):
    url = models.URLField()
    pointer = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    


class ScrappedData(models.Model):
    name = models.CharField(max_length=255)
    inference_key =  models.CharField(max_length=255,null=True, blank=True)
    sitemap_key = models.CharField(max_length=255,null=True, blank=True,unique=True)
    response = models.JSONField()
    round_number = models.IntegerField(null=True, blank=True)
    

    def __str__(self) -> str:
        return self.name