from django.contrib import admin

from .models import Link,ScrappedData

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("id",)
        form = super(LinkAdmin, self).get_form(request, obj, **kwargs)
        return form
    

admin.site.register(ScrappedData)