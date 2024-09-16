from django.contrib import admin
from .models import InstagramUser,LeadSource,QualificationAlgorithm,Scheduler,Score
# Register your models here.

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(LeadSourceAdmin, self).get_form(request, obj, **kwargs)
        return form

@admin.register(QualificationAlgorithm)
class QualificationAlgorithmAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(QualificationAlgorithmAdmin, self).get_form(request, obj, **kwargs)
        return form
    
@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(SchedulerAdmin, self).get_form(request, obj, **kwargs)
        return form

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(ScoreAdmin, self).get_form(request, obj, **kwargs)
        return form
    

@admin.register(InstagramUser)
class InstagramUserAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(InstagramUserAdmin, self).get_form(request, obj, **kwargs)
        return form