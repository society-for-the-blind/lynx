from django.contrib import admin

# Register your models here.


from .models import Contact,           \
                    Intake,            \
                    Address,           \
                    Authorization,     \
                    Email,             \
                    EmergencyContact,  \
                    SipPlan,           \
                    SipNote,           \
                    IntakeNote,        \
                    IntakeServiceArea, \
                    Phone,             \
                    ProgressReport,    \
                    LessonNote,        \
                    Assignment
#                   ServiceDeliveryType,
#                   ServiceDeliverySubType,
#                   Service

admin.site.register(Contact)
admin.site.register(Intake)
admin.site.register(Address)
admin.site.register(Authorization)
admin.site.register(SipPlan)
admin.site.register(SipNote)
admin.site.register(Email)
admin.site.register(EmergencyContact)
admin.site.register(IntakeNote)
admin.site.register(IntakeServiceArea)
# admin.site.register(OutsideAgency)
admin.site.register(Phone)
admin.site.register(ProgressReport)
admin.site.register(LessonNote)
# admin.site.register(Staff)
admin.site.register(Assignment)

# OIB RE-DESIGN MODELS
# admin.site.register(ServiceDeliveryType)
# admin.site.register(ServiceDeliverySubType)
# admin.site.register(Service)
