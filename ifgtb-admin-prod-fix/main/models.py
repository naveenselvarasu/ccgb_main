from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related
from diagnosis.models import *
from main.models import *

class MicroService(models.Model):
    name = models.CharField(max_length=250)  # farmer_ms, pages_ms
    is_active = models.BooleanField(default=True)


class MicroServiceAuthentication(models.Model):
    micro_service = models.OneToOneField(MicroService, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    base_url = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    expiry_time = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.micro_service.name)


class UserType(models.Model):
    name = models.CharField(max_length=50)
    notes = models.CharField(max_length=250)
    # Industry, Scientist, NPQL

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class Language(models.Model):
    name = models.CharField(max_length=50)
    # tamil, english

    def __str__(self):
        return '{}'.format(self.name)


class State(models.Model):
    name = models.CharField(max_length=30)


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)


class Block(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)


class RevenueVillage(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)


class CasteCv(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class CropCv(models.Model):
    name = models.CharField(max_length=25)
    # neem tree, jamun tree

    def __str__(self):
        return self.name

class Clone(models.Model):
    crop_cv = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    # 1182, local

    def __str__(self):
        return self.name


class CropGroupType(models.Model):   # purpose
    name = models.CharField(max_length=25)


class CropGroup(models.Model):
    type = models.ForeignKey(CropGroupType, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    # paper wood, timber, firewood


class CropGroupMap(models.Model):
    crop_cv = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    crop_group = models.ForeignKey(CropGroup, on_delete=models.CASCADE)


class OTP(models.Model):
    purpose = models.CharField(max_length=20)  # register , forgot_password
    mobile = models.CharField(max_length=13)
    otp = models.CharField(max_length=30)
    expiry_time = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class IdBank(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=50)
    prefix_code = models.CharField(max_length=10, blank=True, null=True)
    suffix_code = models.CharField(max_length=10, blank=True, null=True)
    last_count = models.IntegerField(default=0)
    last_count_length = models.IntegerField()
    # TN_TNJ_0001

    class Meta:
        unique_together = (("district", "purpose"),)

    def __str__(self):
        return self.district.name


class FarmerDataSource(models.Model):
    name = models.CharField(max_length=150)
    source_object_name = models.CharField(max_length=50, null=True, blank=True)
    contact_name = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=13, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)


def get_profile_photo_destination(instance, filename):
    return "profile_photo/{user_type}/{id}/{file}".format(user_type=instance.user_type.name,id=instance.id, file=filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="new_user", on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, related_name="superior_user", on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    mobile = models.BigIntegerField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    alternate_mobile = models.BigIntegerField(null=True, blank=True)
    language_preference = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    ms_farmer_code = models.CharField(max_length=32, unique=True, blank=True, null=True)
    photo = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_profile_photo_destination)


    
    def __str__(self):
        return '{} - {}'.format(self.id, self.user.username)


class Industry(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)


def get_industry_office_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


class IndustryOffice(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    is_head_office = models.BooleanField(default=False)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    revenue_village = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    street = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    image = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_industry_office_image)


class IndustryOfficial(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    industry_office = models.ForeignKey(IndustryOffice, on_delete=models.CASCADE)
    is_contact_person = models.BooleanField(default=False)

class WoodUse(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class IndustryOfficeCropMap(models.Model):
    industry_office = models.ForeignKey(IndustryOffice, on_delete=models.CASCADE)
    crop_cv = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    procurement_purpose = models.ForeignKey(WoodUse, on_delete=models.CASCADE, blank=True, null=True,)


class IndustryOfficeCropProcurementPriceLog(models.Model):
    industry_office_crop_map = models.ForeignKey(IndustryOfficeCropMap, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    from_date = models.DateTimeField()
    effective_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='industry_office_price_created_by', blank=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='industry_office_price_modified_by', blank=True, null=True)
    


class Institute(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)


def get_scientist_office_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)

class InstituteOffice(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    is_head_office = models.BooleanField(default=False)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    revenue_village = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    street = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    image = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_scientist_office_image)


class Expertise(models.Model):
    name = models.CharField(max_length=30)


class Scientist(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    institute_office = models.ForeignKey(InstituteOffice, on_delete=models.CASCADE)
    is_contact_person = models.BooleanField(default=False)
    designation = models.CharField(max_length=30)
    expertise = models.ManyToManyField(Expertise)
    display_ordinal = models.PositiveBigIntegerField(default=0)


class NurseryType(models.Model):
    name = models.CharField(max_length=100)
    # Private Nursery, QPM, Dept, E

class Nursery(models.Model):
    # user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    nursery_type = models.ForeignKey(NurseryType, on_delete=models.CASCADE)


def get_nursery_office_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)

class NurseryOffice(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE, blank=True, null=True)
    is_head_office = models.BooleanField(default=False)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    revenue_village = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    street = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    image = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_nursery_office_image)

class NurseryIncharge(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    nursery_office = models.ForeignKey(NurseryOffice, on_delete=models.CASCADE)
    is_contact_person = models.BooleanField(default=False)
    display_ordinal = models.PositiveBigIntegerField(default=0)


class NurseryOfficeCropMap(models.Model):
    nursery_office = models.ForeignKey(NurseryOffice, on_delete=models.CASCADE)
    clone = models.ForeignKey(Clone, on_delete=models.CASCADE)
    current_stock = models.PositiveIntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class NurseryOfficeCropPriceLog(models.Model):
    nursery_office_crop_map = models.ForeignKey(NurseryOfficeCropMap, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    from_date = models.DateTimeField()
    effective_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nursery_office_price_created_by', blank=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nursery_office_price_modified_by', blank=True, null=True)
    

class Gender(models.Model):
    name = models.CharField(max_length=11)


class OwnerShip(models.Model):
    name = models.CharField(max_length=50)
    display_ordinal = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.name)


class Farmer(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    farmer_code = models.CharField(max_length=15, unique=True)  # is needed 15 digit TN_CBE_1234567
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    # state = models.ForeignKey(State, on_delete=models.CASCADE)
    # district = models.ForeignKey(District, on_delete=models.CASCADE)
    district = models.CharField(max_length=100, blank=True, null=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    # block = models.ForeignKey(Block, on_delete=models.CASCADE)
    revenue_village = models.CharField(max_length=100, blank=True, null=True)
    # revenue_village = models.ForeignKey(RevenueVillage, on_delete=models.CASCADE)
    village = models.CharField(max_length=100, blank=True, null=True)
    street = models.TextField(null=True, blank=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    caste = models.ForeignKey(CasteCv, on_delete=models.SET_NULL, blank=True, null=True)
    farm_holding_size_in_acre = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    owner_ship = models.ForeignKey(OwnerShip, on_delete=models.SET_NULL, blank=True, null=True)

    # authentication
    aadhaar_number = models.CharField(max_length=18, blank=True, null=True)
    family_card_number = models.CharField(max_length=18, blank=True, null=True)
    pan_number = models.CharField(max_length=16, blank=True, null=True)  # no need
    voter_card_epic_number = models.CharField(max_length=16, blank=True, null=True)

    # profile status
    profile_complete = models.BooleanField(default=False)

    # verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    verified_on = models.DateTimeField(blank=True, null=True)

    # Created User details
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_created_by', blank=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_modified_by', blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Land(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    owner_ship = models.ForeignKey(OwnerShip, on_delete=models.SET_NULL, blank=True, null=True)
    area_in_acre = models.DecimalField(max_digits=10, decimal_places=3)
    revenue_village = models.ForeignKey(RevenueVillage, blank=True, null=True, on_delete=models.SET_NULL)
    village = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)


class LandGeoTag(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    data_source = models.ForeignKey(FarmerDataSource, on_delete=models.SET_NULL, blank=True, null=True)
    device_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class LandGeoFence(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    area_calculated_geo_fence_in_hectare = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    data_source = models.ForeignKey(FarmerDataSource, on_delete=models.SET_NULL, blank=True, null=True)
    device_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class LandGeoFenceDataPoint(models.Model):
    land_boundary_map = models.ForeignKey(LandGeoFence, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField()


class Crop(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    crop_cv = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    sowing_year = models.DateField()
    # water_type = models.ForeignKey(WaterType, on_delete=models.CASCADE)
    # water_source = models.ForeignKey(WaterSource, on_delete=models.CASCADE)
    # is_drip_irrigated = models.BooleanField(default=False)
    # soil_type = models.ForeignKey(WaterType, on_delete=models.CASCADE)
    area_in_acre = models.DecimalField(max_digits=10, decimal_places=3)
    is_active = models.BooleanField(default=True)
    is_harvested = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    verified_on = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CropGeoTag(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    data_source = models.ForeignKey(FarmerDataSource, on_delete=models.SET_NULL, blank=True, null=True)
    device_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CropGeoFence(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    data_source = models.ForeignKey(FarmerDataSource, on_delete=models.CASCADE)
    area_calculated_geo_fence_in_hectare = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    device_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CropGeoFenceDataPoint(models.Model):
    crop_boundary_map = models.ForeignKey(CropGeoFence, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField()


class LandSurveyNumber(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    survey_number = models.CharField(max_length=15)
    sub_division_number = models.CharField(max_length=25)
    patta_number = models.CharField(max_length=250)


class Scheme(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=200)
    description = models.TextField()
    is_geo_fence_needed = models.BooleanField(default=False)
    is_geo_tag_needed = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.id, self.short_name)


class CropSchemeMap(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)


class WaterType(models.Model):
    name = models.CharField(max_length=20)
    # good water, salt water


class WaterSource(models.Model):
    name = models.CharField(max_length=20)
    # well, canal


class WaterResource(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    water_source = models.ForeignKey(WaterSource, on_delete=models.CASCADE)
    water_type = models.ForeignKey(WaterType, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    water_resource_data_source = models.ForeignKey(FarmerDataSource, on_delete=models.SET_NULL, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ExpenseCV(models.Model):
    crop = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class ExpenseLog(models.Model):
    expense_cv = models.ForeignKey(ExpenseCV, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class OperationCV(models.Model):
    crop = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class OperationLog(models.Model):
    expense = models.ForeignKey(OperationCV, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class HarvestUnit(models.Model):
    instance_crop = models.ForeignKey(CropCv, on_delete=models.CASCADE)
    term = models.CharField(max_length=10)
    display_term = models.CharField(max_length=10)


class Harvest(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.IntegerField()
    unit = models.ForeignKey(HarvestUnit, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class QuestionType(models.Model):
    name = models.CharField(max_length=100)
    # text, password, number, email, text_area, checkbox, radio, dropdown, link, date

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class QuestionSection(models.Model):
    name = models.CharField(max_length=100)
    # farmer_property, field_visit_log, Crop

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class QuestionSectionFor(models.Model):
    name = models.CharField(max_length=100)
    # Farmer, Crop, Land

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class QuestionSectionForMap(models.Model):
    question_section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    section_for = models.ForeignKey(QuestionSectionFor, on_delete=models.CASCADE)
    # (farmer_property, farmer)


class QuestionSubSection(models.Model):
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    # animal_husbandry, personal

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.section.name, self.name)


class Question(models.Model):
    sub_section = models.ForeignKey(QuestionSubSection, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    ordinal = models.CharField(max_length=10)

    class Meta:
        ordering = ['ordinal']
        unique_together = (("sub_section", "text"),)

    def __str__(self):
        return '{} - {}'.format(self.id, self.text)


class QuestionAnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    ordinal = models.CharField(max_length=10)

    class Meta:
        ordering = ['ordinal']
        unique_together = (("question", "text"),)

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.question.text, self.text)


class QuestionConfig(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    required = models.BooleanField(default=False)
    create_new_answer_row_on_update = models.BooleanField(default=False)
    depends_on_question = models.ForeignKey(Question, related_name='depends_on_question', blank=True, null=True, on_delete=models.CASCADE)
    show_when_the_answer_is = models.ForeignKey(QuestionAnswerChoice, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.question.text, self.question_type.name)


class QuestionValidatorCv(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.name)


class QuestionValidationConfig(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    validator = models.ForeignKey(QuestionValidatorCv, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.question.text + self.value)


# SAVE DYNAMIC QUESTION ANSWER
class AnswerLogForRadio(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, related_name='radio_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AnswerLogForCheckbox(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, related_name='checkbox_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AnswerLogForDropDown(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, related_name='dropdown_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AnswerLogForTextInput(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    added_by = models.ForeignKey(User, related_name='text_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AnswerLogForPassword(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=128)
    added_by = models.ForeignKey(User, related_name='password_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AnswerLogForNumberInput(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    land = models.ForeignKey(Land, blank=True, null=True, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.DecimalField(max_digits=10, decimal_places=2)
    added_by = models.ForeignKey(User, related_name='number_answer_added_by', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class LanguageTerm(models.Model):
    name = models.TextField(unique=True)
#     Paddy, tomato

    def __str__(self):
        return '{}'.format(self.name)


class LanguageTransformTerm(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    language_term = models.ForeignKey(LanguageTerm, on_delete=models.CASCADE)
    name = models.TextField()

    class Meta:
        unique_together = (('language', 'language_term'))

    def __str__(self):
        return '{}-{}-{}'.format(self.language.name, self.name, self.language_term.name)


def get_tile_image_path(instance, filename):
    return "titles_image/{display_name}/{file}".format(display_name=instance.display_name, file=filename)


class Tile(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    route_url = models.CharField(max_length=70, blank=True, null=True)
    tab_name = models.CharField(max_length=70, blank=True, null=True)
    icon_path = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)



def get_display_image_destination(instance, filename):
    return "{user_type}/{id}/{file}".format(user_type=instance.user_type.name, id=instance.id, file=filename)


class UserTypeTilesMap(models.Model):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    css_class_name = models.CharField(max_length=100, blank=True, null=True)
    title_class_name = models.CharField(max_length=100, blank=True, null=True)
    icon_class_name = models.CharField(max_length=100, blank=True, null=True)
    column_size = models.PositiveIntegerField(blank=True, null=True)
    is_icon_available = models.BooleanField(default=True)
    language_preference = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    display_image = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_display_image_destination)
    display_ordinal = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Forest(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)


def get_forest_office_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


class ForestOffice(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    forest = models.ForeignKey(Forest, on_delete=models.CASCADE)
    is_head_office = models.BooleanField(default=False)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    revenue_village = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    street = models.TextField(null=True, blank=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    image = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_forest_office_image)


class ForestOfficial(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    forest_office = models.ForeignKey(ForestOffice, on_delete=models.CASCADE)
    is_contact_person = models.BooleanField(default=False)


class ForestOfficeCropMap(models.Model):
    forest_office = models.ForeignKey(ForestOffice, on_delete=models.CASCADE)
    clone = models.ForeignKey(Clone, on_delete=models.CASCADE)
    current_stock = models.PositiveIntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    

class ForestOfficeCropPriceLog(models.Model):
    forest_office_crop_map = models.ForeignKey(ForestOfficeCropMap, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    from_date = models.DateTimeField()
    effective_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forest_office_price_created_by', blank=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forest_office_price_modified_by', blank=True, null=True)
    

class MenuHeader(models.Model):
    display_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    ordinal = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class MenuHeaderPage(models.Model):
    menu_header = models.ForeignKey(MenuHeader, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    ordinal = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class MenuHeaderPermission(models.Model):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    menu_header = models.ForeignKey(MenuHeader, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


class MenuHeaderPagePermission(models.Model):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    menu_header_page = models.ForeignKey(MenuHeaderPage, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


def get_uploaded_excel_from_bank(instance, filename):
    return "farmer_bulk_upload/{date}/{file}".format(date=instance.uploaded_at, file=filename)

class FarmerBulkUploadLog(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField()
    uploaded_count = models.PositiveIntegerField()
    already_exists = models.PositiveIntegerField()
    excel_file = models.FileField(upload_to=get_uploaded_excel_from_bank, max_length = 100)
    file_name = models.CharField(max_length=100, blank=True, null=True)  
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class SurveyorOfficialMap(models.Model):
    surveyor = models.ForeignKey(User, on_delete=models.CASCADE)
    superior_user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    industry_office = models.ForeignKey(IndustryOffice, on_delete=models.CASCADE, blank=True, null=True)
    institute_office = models.ForeignKey(InstituteOffice, on_delete=models.CASCADE, blank=True, null=True)
    nursery_office = models.ForeignKey(NurseryOffice, on_delete=models.CASCADE, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class NotificationCv(models.Model):
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=100)
    background = models.CharField(max_length=100)

class NotificatiionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationCv, on_delete=models.CASCADE)
    is_sceen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_query = models.ForeignKey(UserQuery, on_delete=models.CASCADE, null=True, blank=True)
    recommendation = models.ForeignKey(RecommendationLog, on_delete=models.CASCADE,  null=True, blank=True)
    notification_text = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# models for journals
class JournalsCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{}'.format(self.name)


def get_uploaded_journals_path(instance, filename):
    return "ifgtb_journals/{file}".format(file=filename)

class Journal(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_on = models.DateTimeField()
    category = models.ForeignKey(JournalsCategory, on_delete=models.CASCADE)
    journal_file = models.FileField(upload_to=get_uploaded_journals_path, max_length = 100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.title)


class UsertypeWiseUserManual(models.Model):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50)
    tamil_manual_url = models.CharField(max_length=100)
    english_manual_url = models.CharField(max_length=100)
    display_ordinal = models.PositiveBigIntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)





