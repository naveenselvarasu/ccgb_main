from django.db import models
from django.contrib.auth.models import User
import datetime

from django.db.models.fields.files import FileField


# requested, dispatched, answered, closed, expired
class UserQueryStatus(models.Model):
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


    def __str__(self):
        return '{}'.format(self.name)


# voice storing destination
def get_user_query_voice_upload_destination(instance, filename):
    return "diagnosis/user_query/{date}/user_{user_id}/query_{query_id}/{file}".format(
        date=str(datetime.datetime.now().date()), user_id=instance.user_id,
        query_id=instance.id, file=filename)


# Its a dummy model,  by default the general is considered
class ExpertTypeCv(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# map experts with the query type
class QueryCategoryExpertUserMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expert_type = models.ForeignKey(ExpertTypeCv, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.expert_type.name


# ask expert user query
class UserQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clone = models.ForeignKey('main.Clone', on_delete=models.CASCADE, blank=True, null=True)
    is_assigned = models.BooleanField(default=False)
    query_type = models.ForeignKey(ExpertTypeCv, on_delete=models.CASCADE)
    requested_date = models.DateField()
    age_in_month = models.PositiveIntegerField()
    age_in_year = models.PositiveIntegerField()
    area_in_acre = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    status = models.ForeignKey(UserQueryStatus, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    voice = models.FileField(blank=True, upload_to=get_user_query_voice_upload_destination, max_length=1000)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.user.first_name, self.requested_date)


def get_user_query_image_upload_destination(instance, filename):
    return "instance/user_query/{date}/user_{user_id}/query_{query_id}/{file}".format(
        date=str(datetime.datetime.now().date()), user_id=instance.user_query.user_id, query_id=instance.user_query.id,
        file=filename)


class UserQueryImage(models.Model):
    user_query = models.ForeignKey(UserQuery, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_user_query_image_upload_destination, max_length=1000)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_query.user.first_name + '-' + str(self.user_query_id)


# recommendation voice destination
def get_recommendation_voice_upload_destination(instance, filename):
    return "diagnosis/recommendation/{date}/user_{user_id}/recommendation_{recommendation_id}/{file}".format(
        date=str(datetime.datetime.now().date()), user_id=instance.user_query.user.id,
        recommendation_id=instance.id, file=filename)


class RecommendationStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{}'.format(self.name)


# recommendation for user query
class RecommendationLog(models.Model):
    user_query = models.ForeignKey(UserQuery, on_delete=models.CASCADE)
    voice = models.FileField(
        blank=True, null=True, upload_to=get_recommendation_voice_upload_destination, max_length=1000)
    notes = models.TextField()
    link = models.TextField(blank=True, null=True)
    recommended_by = models.ForeignKey(User, related_name='recommended_by_expert_user', on_delete=models.CASCADE)
    status = models.ForeignKey(RecommendationStatus, on_delete=models.CASCADE)
    review_by = models.ForeignKey(User, related_name='super_admin_reviewed', blank=True, null=True, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


    def __str__(self):
        return '{}'.format(self.user_query.user.first_name)


# recommendation image destination
def get_recommendation_image_upload_destination(instance, filename):
    return "instance/recommendation/{date}/user_{user_id}/recommendation_{recommendation_id}/{file}".format(
        date=str(datetime.datetime.now().date()), user_id=instance.recommendation.user_query.user.id,
        recommendation_id=instance.recommendation.id, file=filename)


class RecommendationImage(models.Model):
    recommendation = models.ForeignKey(RecommendationLog, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=get_recommendation_image_upload_destination, max_length=1000)

    # def __str__(self):
    #     return self.recommendation.user_query.user.first_name + '-' + str(self.recommendation.user_query_id)


# class RecommendationVideoUrl(models.Model):
#     recommendation = models.ForeignKey(RecommendationLog)
#     video_url = models.CharField(max_length=300, blank=True, null=True)
#
#     # def __str__(self):
#     #     return '{}'.format(self.user_query.user.first_name)
#
#
# class RecommendationTextUrl(models.Model):
#     recommendation = models.ForeignKey(RecommendationLog)
#     text_url = models.CharField(max_length=300, blank=True, null=True)


class QueryMediatorToggle(models.Model):
    is_system_assigned = models.BooleanField(default=True)


class QueryExpertAssignMap(models.Model):
    user_query = models.ForeignKey(UserQuery, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name="query_assigned_to_user", on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name="query_assigned_by_user", on_delete=models.CASCADE)
    assigned_on = models.DateTimeField(auto_now_add=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# publish files destination
def get_publish_file_upload_destination(instance, filename):
    return "diagnosis/publish/{date}/user_{user_id}/publish_{post_id}/{file}".format(
        date=str(datetime.datetime.now().date()), user_id=instance.posted_by.id,
        post_id=instance.id, file=filename)

class CircularCategory(models.Model):
    name = models.CharField(max_length=100)


class CircularLog(models.Model):
    posted_by = models.ForeignKey(User, related_name="posted_by", on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    circular_category = models.ForeignKey(CircularCategory, on_delete=models.CASCADE)
    description = models.TextField()
    file = models.FileField(upload_to=get_publish_file_upload_destination, blank=True, null=True)
    circular_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
