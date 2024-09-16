from django.contrib import admin
from .models import Scout,ScoutingMaster,Device
# Register your models here.

@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(ScoutAdmin, self).get_form(request, obj, **kwargs)
        return form

@admin.register(ScoutingMaster)
class ScoutingMasterAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(ScoutingMasterAdmin, self).get_form(request, obj, **kwargs)
        return form
    
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(DeviceAdmin, self).get_form(request, obj, **kwargs)
        return form
