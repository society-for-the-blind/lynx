from django.contrib import admin
from django.db import models as dj_models
from . import models as lm

class ShowIDAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        fields = [field.name for field in self.model._meta.fields if field.name != 'id']
        return ['id'] + fields

for model in lm.__dict__.values():
    if (
        isinstance(model, type)
        and issubclass(model, dj_models.Model)
        and not getattr(model._meta, 'abstract', False)  # <-- skip abstract models
    ):
        try:
            admin.site.register(model, ShowIDAdmin)
        except admin.sites.AlreadyRegistered:
            pass