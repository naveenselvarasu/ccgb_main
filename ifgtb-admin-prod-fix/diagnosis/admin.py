from django.contrib import admin
from diagnosis.models import *

# Register your models here.
admin.site.register(UserQuery)
admin.site.register(UserQueryImage)
admin.site.register(RecommendationImage)
admin.site.register(RecommendationLog)
admin.site.register(CircularLog)
