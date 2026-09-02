from django.contrib import admin
from .models import Appointment, MedicalReport

admin.site.register(Appointment)
admin.site.register(MedicalReport)