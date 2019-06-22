from django.contrib import admin

# Register your models here.


from .models import Contact, Employee, Billing, Intake, Address, Authorization, BillingName, Email, EmergencyContact, IntakeNote, IntakeServiceArea, OutsideAgency, Phone, Referral

admin.site.register(Contact)
admin.site.register(Employee)
admin.site.register(Billing)
admin.site.register(Intake)
admin.site.register(Address)
admin.site.register(Authorization)
admin.site.register(BillingName)
admin.site.register(Email)
admin.site.register(EmergencyContact)
admin.site.register(IntakeNote)
admin.site.register(IntakeServiceArea)
admin.site.register(OutsideAgency)
admin.site.register(Referral)
admin.site.register(Phone)
