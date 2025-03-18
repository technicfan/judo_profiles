from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Position)
admin.site.register(Technique)
admin.site.register(OwnTechnique)
admin.site.register(TechniqueRank)
admin.site.register(CombinationRank)
