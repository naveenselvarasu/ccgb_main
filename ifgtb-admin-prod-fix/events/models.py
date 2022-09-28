from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.

class EventType(models.Model):
    name = models.CharField(max_length=25, blank=True, null=True)
    notes = models.TextField()

    # Meeting, Traning

    def __str__(self):
        return self.name


def get_event_image_upload_destination(instance, filename):
    return "events/event_image/{event_date}_{event_title}/{file}".format(event_date=instance.date_from,
                                                                                 event_title='_'.join(
                                                                                     instance.title.split(' ')),
                                                                                 file=filename)


class Event(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the Event")
    description = models.TextField()
    event_image = models.ImageField(upload_to=get_event_image_upload_destination, max_length=1000, blank=True, null=True)
    link = models.URLField(null=True, blank=True, verbose_name="Event website", help_text="Prefix http://")
    event_type = models.ForeignKey(EventType, blank=True, null=True, verbose_name="Type of Event", on_delete=models.CASCADE)
    is_free = models.BooleanField(default=False, verbose_name="Free Event")
    all_day = models.BooleanField(default=False)
    date_from = models.DateField(verbose_name="From")
    date_to = models.DateField(verbose_name="To")
    time_from = models.TimeField(verbose_name="Time Starts on")
    time_to = models.TimeField(verbose_name="Time Ends on")
    contact_person = models.CharField(max_length=50, blank=True, null=True, verbose_name="Contact Person")
    contact_number = models.CharField(max_length=13, blank=True, null=True, verbose_name="Number")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    publish_from = models.DateTimeField(help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(help_text="With Published chosen, won't be shown after this time", verbose_name='Expires on')
    state = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    locality = models.CharField(max_length=50, verbose_name='Village/Town name', blank=True, null=True)
    city = models.CharField(max_length=50, verbose_name='city', blank=True, null=True)
    country = models.CharField(max_length=50, verbose_name='country', blank=True, null=True)
    inter_city = models.CharField(max_length=50, verbose_name='inter_city', blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.CharField(max_length=40, blank=True, null=True)
    longitude = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50)
    login_required = models.BooleanField(default=False, help_text='If checked, only logged in users can view this page')
    app_alert = models.BooleanField(default=False)
    user_created = models.ForeignKey(User, related_name='user_created', blank=True, null=True, editable=False, on_delete=models.CASCADE)
    user_modified = models.ForeignKey(User, related_name='user_modified', blank=True, null=True, editable=False, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    base64_type = models.CharField(max_length=150, blank=True, null=True)
    file_name = models.CharField(max_length=250, blank=True, null=True)
    mime_type = models.CharField(max_length=50, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


class News(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    journal = models.CharField(max_length=30, blank=True, null=True)
    news_link = models.URLField(
        verbose_name="News website", help_text="Prefix http://")
    publish_from = models.DateTimeField(
        help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(
        help_text="With Published chosen, won't be shown after this time", verbose_name='Expires on')
    app_alert = models.BooleanField(default=False)
    language = models.CharField(max_length=50)
    available_for_guest = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


def get_advertisement_image_upload_destination(instance, filename):
    return "event_and_news/advertisement_image/{publish_from}_to_{expires_on}/{file}".format(
        publish_from=datetime.datetime.strftime(
            instance.publish_from, '%Y-%m-%d'),
        expires_on=datetime.datetime.strftime(instance.expires_on, '%Y-%m-%d'), file=filename)


class Advertisement(models.Model):
    advertisement_image = models.ImageField(
        upload_to=get_advertisement_image_upload_destination, max_length=1000)
    link = models.URLField(verbose_name="Sponsor website",
                           help_text="Prefix http://", blank=True, null=True)
    publish_from = models.DateTimeField(
        help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(
        help_text="With Published chosen, won't be shown after this time", verbose_name='Expires on')
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)