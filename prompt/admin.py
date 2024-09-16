from django.contrib import admin
from .models import Prompt,Query, ToneOfVoice, Role,Department,Task,Agent,Tool,Baton, Endpoint
# Register your models here.

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(PromptAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(ToneOfVoice)
class ToneOfVoiceAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(ToneOfVoiceAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(RoleAdmin, self).get_form(request, obj, **kwargs)
        return form

@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(QueryAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(DepartmentAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name','get_tasks',)
    
    @admin.display(description='Tasks')
    def get_tasks(self, obj):
        return [task.name for task in obj.task_set.all()]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(AgentAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(TaskAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(ToolAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Baton)
class BatonAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(BatonAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(EndpointAdmin, self).get_form(request, obj, **kwargs)
        return form
