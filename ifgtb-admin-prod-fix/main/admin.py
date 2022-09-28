from django.contrib import admin
from main.models import UserType, UserProfile, Language, Question, QuestionSection, QuestionSubSection, QuestionConfig
from main.models import QuestionAnswerChoice
from main.models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(UserType)
admin.site.register(Language)
admin.site.register(Question)
admin.site.register(QuestionSection)
admin.site.register(QuestionSubSection)
admin.site.register(QuestionConfig)
admin.site.register(QuestionAnswerChoice)
# admin.site.register(LanguageTerm)
admin.site.register(LanguageTransformTerm)
admin.site.register(CropCv)
admin.site.register(WaterSource)
admin.site.register(NurseryOffice)
admin.site.register(IndustryOffice)
admin.site.register(InstituteOffice)
admin.site.register(Tile)
admin.site.register(JournalsCategory)
admin.site.register(Journal)



class AppLanguageTerm(admin.TabularInline):
    model = LanguageTerm

class AppLanguageTransformTerm(admin.TabularInline):
    model = LanguageTransformTerm

class LanguageAdmin(admin.ModelAdmin):
    inlines = [
        # AppLanguageTerm,
        AppLanguageTransformTerm,
    ]

class LanguageTermAdmin(admin.ModelAdmin):
    inlines = [
        # AppLanguageTerm,
        AppLanguageTransformTerm,
    ]

# admin.site.register(Language, LanguageAdmin)
admin.site.register(LanguageTerm, LanguageTermAdmin)


# user type tiles
class UserTypeTileMapAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_type', 'tile', 'language_preference', 'display_image']


admin.site.register(UserTypeTilesMap, UserTypeTileMapAdmin)