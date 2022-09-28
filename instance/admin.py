from django.contrib import admin
from instance.models import *
# Register your models here.

admin.site.register(Cluster)
admin.site.register(Business)
admin.site.register(BusinessType)
admin.site.register(UserProfile)
admin.site.register(UserType)
admin.site.register(EducationalQualificationCv)
admin.site.register(UserBankDetails)
admin.site.register(Farmer)
# admin.site.register(AgentOffice)

admin.site.register(QuestionSection)
admin.site.register(QuestionSubSection)
admin.site.register(Question)
admin.site.register(QuestionType)
admin.site.register(QuestionAnswerChoice)
admin.site.register(QuestionConfig)
admin.site.register(TempSeasonBasedGap)
admin.site.register(SeasonBasedGap)
admin.site.register(GapQuestionType)
admin.site.register(TempSeasonBasedGapQuestion)
admin.site.register(SeasonBasedGapQuestion)
 