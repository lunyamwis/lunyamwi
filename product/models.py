from django.db import models
from base.models import BaseModel
# Create your models here.

class Company(BaseModel):
    name = models.CharField(max_length=255)
    index = models.IntegerField(default=1)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.name

class GsheetSetting(BaseModel):
    name = models.CharField(max_length=255)
    spreadsheet_id = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                null=True, blank=True)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.name

    
class DatabaseCredential(BaseModel):
    engine = models.CharField(max_length=255)
    database = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                null=True, blank=True)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.database


class Product(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company,on_delete=models.CASCADE, 
                                      null=True, blank=True)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.name
    
    @property
    def steps(self):
        from prompt.models import Prompt
        return Prompt.objects.filter(
            product__id=self.id
        ).count()

      
class Problem(BaseModel):
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product,on_delete=models.CASCADE, 
                                      null=True, blank=True)
    gsheet_range = models.TextField()
    gsheet_formula = models.TextField()
    outsourced = models.JSONField(default=dict)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.name


class Solution(BaseModel):
    name = models.CharField(max_length=255)
    gsheet_range = models.TextField()
    gsheet_formula = models.TextField()
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE, 
                                      null=True, blank=True)
    class Meta:
      app_label='product'
    def __str__(self) -> str:
        return self.name
    
