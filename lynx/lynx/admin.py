from django.contrib import admin

# Register your models here.


from .models import Contact, Employee, Billing, Intake, Address

admin.site.register(Contact)
admin.site.register(Employee)
admin.site.register(Billing)
admin.site.register(Intake)
admin.site.register(Address)