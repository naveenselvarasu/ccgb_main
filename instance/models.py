from django.db import models
from django.contrib.auth.models import User
from knowledgebase.models import *


# -------------------------------------------
# Business section
# -------------------------------------------

class BusinessType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # pvt , govt, pvt ltd

    def __str__(self):
        return '{}-{}'.format(self.id, self.name)


class UserType(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    notes = models.CharField(max_length=250, blank=True, null=True)
    ordinal = models.PositiveSmallIntegerField()

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)
    # farmer, agent, supervisor, manager, Ass. Manager


class Business(models.Model):
    name = models.CharField(max_length=250, unique=True)
    shortname = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=13)
    pincode = models.IntegerField()
    state = models.ForeignKey('knowledgebase.State')
    district = models.ForeignKey('knowledgebase.District')
    taluk = models.ForeignKey('knowledgebase.Taluk')
    street = models.TextField()
    business_type = models.ForeignKey(BusinessType)

    def __str__(self):
        return '{}-{}'.format(self.id, self.shortname)

# -------------------------------------------
# authentication section
# -------------------------------------------


class TemporaryRegistration(models.Model):
    business = models.ForeignKey(Business)
    user_type = models.ForeignKey(UserType)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=30)
    mobile = models.CharField(max_length=13)
    email = models.CharField(max_length=30, blank=True, null=True)
    otp = models.CharField(max_length=30)
    time_created = models.DateTimeField(auto_now_add=True)


class SMSTrace(models.Model):
    business = models.ForeignKey(Business)
    receiver_user_id = models.PositiveIntegerField(blank=True, null=True)
    purpose = models.TextField()
    message = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)


class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User)
    otp = models.IntegerField()
    expiry_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)




class Cluster(models.Model):
    name = models.CharField(max_length=50)
    notes = models.CharField(max_length=1000)



class EducationalQualificationCv(models.Model):
    name = models.CharField(max_length=50)
    ordinal = models.PositiveSmallIntegerField()


def get_aadhar_document_destination(instance, filename):
    return "kyc/aadhaar_document/{username}/{file}".format(username=instance.user.username, file=filename)


def get_pan_document_destination(instance, filename):
    return "kyc/pan/{username}/{file}".format(username=instance.user.username, file=filename)


def get_agreement_document_destination(instance, filename):
    return "kyc/agreement_document/{username}/{file}".format(username=instance.user.username, file=filename)


def get_driving_licence_document_destination(instance, filename):
    return "kyc/driving_licence/{username}/{file}".format(username=instance.user.username, file=filename)


# ----------------------------------------
# Crop
# ----------------------------------------

class CropGroup(models.Model):
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    # vegitables, fruits, cerials

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.business.shortname, self.name)


class Crop(models.Model):
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=50)
    age_in_days = models.PositiveIntegerField()
    notes = models.TextField(default="Some crop")
    # sun flower

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.business.shortname, self.name)


class CropCropGroupMap(models.Model):
    crop = models.ForeignKey(Crop)
    crop_group = models.ForeignKey(CropGroup)

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.crop.name, self.crop_group.name)

# ----------------------------------------
# season
# ----------------------------------------


class Season(models.Model):
    name = models.CharField(max_length=25)
    year = models.DateField()
    crop = models.ForeignKey(Crop)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    ordinal = models.PositiveSmallIntegerField()
    created_by = models.ForeignKey(User, related_name='season_created_by_user')
    modified_by = models.ForeignKey(User, related_name='season_modifed_by_user')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)


class UserHierarchyMap(models.Model):
    superior_user_type = models.ForeignKey(UserType)
    season = models.ForeignKey(Season)
    superior = models.ForeignKey(User)
    subordinate = models.ManyToManyField(User, related_name='subordinate_user')
    subordinate_user_type = models.ForeignKey(UserType, related_name='subordinate_user_type')

    def __str__(self):
        return str(self.superior.username)

class UserProfileCodeBank(models.Model):
    business = models.ForeignKey(Business)
    season = models.ForeignKey(Season)
    user_type = models.ForeignKey(UserType)
    prefix_code = models.CharField(max_length=10, blank=True, null=True)
    suffix_code = models.CharField(max_length=10, blank=True, null=True)
    last_count = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("business", "season","user_type", "prefix_code"),)


class ClusterSeasonMap(models.Model):
    cluster = models.ForeignKey(Cluster)
    season = models.ForeignKey(Season)

class AgentSupervisorSeasonMap(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_for_supervisor_map')
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisor_for_supervisor_map')
    season = models.ForeignKey(Season)


    class Meta:
            unique_together = (("agent", "season"),)

# need to add the Graduation place and university at dynamic questions in educaton part
class UserProfile(models.Model):
    business = models.ForeignKey(Business)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=15, unique=True)
    user_type = models.ForeignKey(UserType)
    date_of_joining = models.DateField(blank=True, null=True)
    blood_group = models.ForeignKey(BloodGroup, blank=True, null=True)

    gender = models.ForeignKey('knowledgebase.Gender', blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    mobile = models.CharField(max_length=13)
    alternate_mobile = models.CharField(max_length=13, blank=True, null=True)
    emergency_number = models.CharField(max_length=13, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    state = models.ForeignKey('knowledgebase.State')
    district = models.ForeignKey('knowledgebase.District')
    taluk = models.ForeignKey('knowledgebase.Taluk')
    hobli = models.ForeignKey('knowledgebase.Hobli')
    village = models.ForeignKey('knowledgebase.Village', blank=True, null=True)
    pincode = models.IntegerField()

    # educational qualification
    educational_qualification = models.ForeignKey(EducationalQualificationCv, blank=True, null=True)
    institution_name = models.CharField(max_length=100, blank=True, null=True)
    university_name = models.CharField(max_length=100, blank=True, null=True)

    # KYC
    # aadhar
    aadhaar_number = models.CharField(max_length=18, blank=True, null=True)
    aadhaar_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_aadhar_document_destination)

    # pan card
    pan_number = models.CharField(max_length=16, blank=True, null=True)
    pan_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_pan_document_destination)

    # driving_licence_document
    driving_licence_number = models.CharField(max_length=18, blank=True, null=True)
    driving_licence_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_driving_licence_document_destination)

    # aggrement form
    agreement_number = models.CharField(max_length=18, blank=True, null=True)
    agreement_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agreement_document_destination)

    prior_experience_in_other_company = models.BooleanField(default=False)
    prior_experience_company_name = models.CharField(max_length=100, blank=True, null=True)
    prior_experience_duration = models.IntegerField(blank=True, null=True)

    latitude = models.CharField(max_length=40, blank=True, null=True)
    longitude = models.CharField(max_length=40, blank=True, null=True)

    created_by = models.ForeignKey(User, related_name='agent_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='agent_modifed_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.user.username)


def get_user_image_save_location(instance, filename):
    return "user_image/{username}/{file}".format(username=instance.user.username, file=filename)


class UserImage(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(max_length=1000, upload_to=get_user_image_save_location)
    uploaded_by = models.ForeignKey(User, related_name="user_image_uploaded_by")
    uploaded_on = models.DateTimeField(auto_now_add=True)


class Position(models.Model):
    name = models.CharField(max_length=10, unique=True)
    notes = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PositionPositionUserMap(models.Model):
    position = models.ForeignKey(Position)
    user = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PositionManUserMap(models.Model):
    position_user_map = models.ForeignKey(PositionPositionUserMap)
    user = models.ForeignKey(User)
    from_date = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PositionManUserMapTrace(models.Model):
    position_user_map = models.ForeignKey(PositionPositionUserMap)
    user = models.ForeignKey(User)
    from_date = models.DateField()
    to_date = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AgentOffice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=13)
    state = models.ForeignKey('knowledgebase.State', blank=True, null=True)
    district = models.ForeignKey('knowledgebase.District', blank=True, null=True)
    taluk = models.ForeignKey('knowledgebase.Taluk', blank=True, null=True)
    hobli = models.ForeignKey('knowledgebase.Hobli', blank=True, null=True)
    village = models.ForeignKey('knowledgebase.Village', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.IntegerField()
    # Created User details
    created_by = models.ForeignKey(User, related_name='agent_office_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='agent_office_modifed_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_post_dated_check_image(instance, filename):
    return "kyc/bank_passbook/cheque/{user_name}/{file}".format(user_name=instance.user.username, file=filename)


def get_bank__pass_book_document_destination(instance, filename):
    return "kyc/bank_passbook/{username}/{file}".format(username=instance.user.username, file=filename)


class UserBankDetails(models.Model):
    user = models.ForeignKey(User)
    bank = models.CharField(max_length=150)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    micr_code = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=True)
    bank_passbook_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_bank__pass_book_document_destination)
    post_cheque_number = models.PositiveIntegerField(blank=True, null=True)
    post_cheque_image = models.ImageField(max_length=1000, upload_to=get_post_dated_check_image, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="bank_details_created_by")
    modified_by = models.ForeignKey(User, related_name="bank_details_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

# -------------------------------------------
# Farmer section
# -------------------------------------------


class FarmHoldingSizeClassificationCv(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=5)
    lower_limit_in_ha = models.DecimalField(max_digits=6, decimal_places=2)
    upper_limit_in_ha = models.DecimalField(max_digits=6, decimal_places=2)
    area_range = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    # small, medium, marginal, big


class FarmerDataSource(models.Model):
    name = models.CharField(max_length=150)
    source_object_name = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=50)
    contact_mobile_number = models.CharField(max_length=13)
    notes = models.CharField(max_length=300)
    time_created = models.DateTimeField(auto_now_add=True)


def get_farmer_aadhar_document_destination(instance, filename):
    return "kyc/aadhaar_document/farmer/{username}/{file}".format(username=instance.mobile, file=filename)


def get_farmer_pan_document_destination(instance, filename):
    return "kyc/pan/farmer/{username}/{file}".format(username=instance.mobile, file=filename)


def get_farmer_agreement_document_destination(instance, filename):
    return "kyc/agreement_document/farmer/{username}/{file}".format(username=instance.mobile, file=filename)

class FarmerCodeBank(models.Model):
    business = models.ForeignKey(Business)
    prefix_code = models.CharField(max_length=10, blank=True, null=True)
    suffix_code = models.CharField(max_length=10, blank=True, null=True)
    last_count = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Farmer(models.Model):
    first_name = models.CharField(max_length=25)
    
    # father name
    last_name = models.CharField(max_length=25)
    code = models.CharField(max_length=10, unique=True)
    common_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    gender = models.ForeignKey(Gender, blank=True, null=True)
    business = models.ForeignKey(Business)

    # location
    pincode = models.IntegerField(blank=True, null=True)
    state = models.ForeignKey(State)
    district = models.ForeignKey(District)
    taluk = models.ForeignKey(Taluk)
    hobli = models.ForeignKey(Hobli)
    village = models.ForeignKey(Village)
    address = models.TextField(null=True, blank=True)

    # communication
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=13, blank=True, null=True)
    alternate_mobile = models.CharField(max_length=13, blank=True, null=True)
    communication_language = models.ForeignKey(Language, blank=True, null=True)

    # KYC
    # aadhar
    aadhaar_number = models.CharField(max_length=18, blank=True, null=True)
    aadhaar_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_farmer_aadhar_document_destination)

    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    # classifications
    land_rtc_number = models.CharField(max_length=50, blank=True, null=True)
    caste = models.ForeignKey(Caste, blank=True, null=True)
    farm_holding_size_classification = models.ForeignKey(FarmHoldingSizeClassificationCv, blank=True, null=True)
    farm_holding_size_in_acre = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    crop_under_cultivation = models.ForeignKey(Crop, blank=True, null=True)

    # agreement
    agreement_number = models.CharField(max_length=25, blank=True, null=True)
    agreement_date = models.DateField(max_length=25, blank=True, null=True)
    agreement_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_farmer_agreement_document_destination)
    cluster = models.ForeignKey(Cluster)
    cultivated_for_ccgb_since = models.DateField(blank=True, null=True)

    # profile status
    profile_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_future_farmer = models.BooleanField(default=False)
    is_demo_farmer = models.BooleanField(default=False)

    # verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, blank=True, null=True, related_name='farmer_entry_verified_by')
    verified_on = models.DateTimeField(blank=True, null=True)

    # farmer data source
    farmer_data_source = models.ForeignKey(FarmerDataSource)

    # Created User details
    created_by = models.ForeignKey(User, related_name='farmer_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='farmer_modified_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['village']

    def __str__(self):
        return '{} ({}), {}'.format(self.first_name, self.code, self.village)


def get_farmer_image_save_location(instance, filename):
    return "farmer_image/{farmer_name}/{file}".format(farmer_name=instance.farmer.id, file=filename)


class FarmerImage(models.Model):
    farmer = models.OneToOneField(Farmer)
    image = models.ImageField(max_length=1000, upload_to=get_farmer_image_save_location)
    uploaded_by = models.ForeignKey(User)
    uploaded_on = models.DateTimeField(auto_now_add=True)


def get_farmer_bank_pass_book_document_destination(instance, filename):
    return "kyc/bank_passbook/{username}/{file}".format(username=instance.farmer.mobile, file=filename)


class FarmerBankDetails(models.Model):
    farmer = models.ForeignKey(Farmer)
    bank = models.CharField(max_length=150)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    micr_code = models.CharField(max_length=100, blank=True, null=True)
    bank_passbook_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_farmer_bank_pass_book_document_destination)
    account_holder_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=True)
    remarks = models.CharField(max_length=150, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="farmer_bank_details_created_by")
    modified_by = models.ForeignKey(User, related_name="farmer_bank_details_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# -------------------------------------------------------
# user and cluster mapping
# -------------------------------------------------------

# mapping the farmer with season and cluster
class FarmerClusterSeasonMap(models.Model):
    farmer = models.ForeignKey(Farmer)
    season = models.ForeignKey(Season)
    seasonal_farmer_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    cluster = models.ForeignKey(Cluster)
    modified_by = models.ForeignKey(User, related_name="farmer_cluster_map_done_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# user farmer map
class UserFarmerMap(models.Model):
    officer = models.ForeignKey(User)  # position user (not man user)
    farmer = models.ForeignKey(FarmerClusterSeasonMap)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("officer", "farmer"),)

    def __str__(self):
        return str(self.officer.username)


# agent farmer map
class AgentFarmerMap(models.Model):
    agent = models.ForeignKey(User)
    farmer = models.ForeignKey(FarmerClusterSeasonMap)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("agent", "farmer"),)

    def __str__(self):
        return str(self.agent.username)


# maping the cluster with user
class UserClusterMap(models.Model):
    season = models.ForeignKey(Season)
    user = models.ForeignKey(User)
    cluster = models.ForeignKey(Cluster)
    unique_code = models.CharField(max_length=3)
    modified_by = models.ForeignKey(User, related_name="user_cluster_map_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class IdBank(models.Model):
    business = models.ForeignKey(Business)
    purpose = models.CharField(max_length=50)
    prefix_code = models.CharField(max_length=10, blank=True, null=True)
    suffix_code = models.CharField(max_length=10, blank=True, null=True)
    last_count = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.purpose


# -------------------------------------------
# Sowing section
# -------------------------------------------

class CultivationPhase(models.Model):
    name = models.CharField(max_length=50)
    # nursury type, main crop


class SoilType(models.Model):
    name = models.CharField(max_length=50)
    # black soil, red soil


class WaterSource(models.Model):
    name = models.CharField(max_length=50)
    # well, borewell, canal, rain, natural streams, tank/farm pond, scheme water


class WaterType(models.Model):
    name = models.CharField(max_length=50)
    # salt, good


class IrrigationMethod(models.Model):
    name = models.CharField(max_length=50)
    # canal, trip


class Sowing(models.Model):
    farmer = models.ForeignKey(Farmer)
    crop = models.ForeignKey(Crop)
    cultivation_phase = models.ForeignKey(CultivationPhase)
    sowing_date = models.DateField()
    area = models.FloatField(help_text="Area in Acre")
    season = models.ForeignKey(Season)

    water_source = models.ForeignKey(WaterSource)
    water_type = models.ForeignKey(WaterType ,blank=True, null=True)

    soil_type = models.ForeignKey(SoilType)
    irrigation_method = models.ForeignKey(IrrigationMethod ,blank=True, null=True)

    state = models.ForeignKey(State)
    district = models.ForeignKey(District)
    
    taluk = models.ForeignKey(Taluk)
    hobli = models.ForeignKey(Hobli)
    
    village = models.ForeignKey(Village)

    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    area_calculated_via_geo_fencing = models.FloatField(help_text="Area as per GPS", blank=True, null=True)
    is_geo_fencing_is_automatic = models.BooleanField(default=True)
    geo_fence_done_on = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    reason_for_inactive =  models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, blank=True, null=True)
    verified_on = models.DateTimeField(blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.farmer.first_name + '_' + self.instance_crop.name)


def get_sowing_image_save_location(instance, filename):
    return "sowings/{farmer_id}/{file}".format(farmer_id=instance.sowing.id, file=filename)


class SowingImage(models.Model):
    sowing = models.ForeignKey(Sowing)
    notes = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(max_length=1000, upload_to=get_sowing_image_save_location)
    uploaded_by = models.ForeignKey(User)
    uploaded_on = models.DateTimeField(auto_now_add=True)


class SowingBoundary(models.Model):
    sowing = models.ForeignKey(Sowing)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField()



class SowingBoundaryMap(models.Model):
    sowing = models.ForeignKey(Sowing)
    sowing_boundry = models.ManyToManyField(SowingBoundary)
    data_source = models.ForeignKey(FarmerDataSource)
    device_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    added_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class NurseryMainFieldMap(models.Model):
    sowing = models.ForeignKey(Sowing)
    sowing = models.ForeignKey(Sowing, related_name="sowing_which_is_from_nursery")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# -------------------------------------------
# Water source section
# -------------------------------------------


class WaterResource(models.Model):
    farmer = models.ForeignKey(Farmer)
    water_source = models.ForeignKey(WaterSource)
    water_type = models.ForeignKey(WaterType)
    irrigation_method = models.ForeignKey(IrrigationMethod)

    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    verified_by = models.ForeignKey(User, blank=True, null=True, related_name='water_resource_verified_by')
    verified_on = models.DateTimeField(blank=True, null=True)

    verified_latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    verified_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    device_datacapture_datetime = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(User, related_name='water_resource_created_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    #
    # def __str__(self):
    #     return '{}'.format(self.name)


class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    # text, password, number, email, text_area, checkbox, radio, dropdown, link, date

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class QuestionSection(models.Model):
    name = models.CharField(max_length=100)

    # farmerproperty, vield visit log,

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class QuestionSubSection(models.Model):
    section = models.ForeignKey(QuestionSection)
    name = models.CharField(max_length=50)
    business = models.ForeignKey(Business)

    # animal husbendary

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.section.name, self.name)


class Question(models.Model):
    subsection = models.ForeignKey(QuestionSubSection)
    text = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    ordinal = models.CharField(max_length=10)

    class Meta:
        ordering = ['ordinal']
        unique_together = (("subsection", "text"),)

    def __str__(self):
        return '{} - {}'.format(self.id, self.text)


class QuestionAnswerChoice(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=50)
    ordinal = models.CharField(max_length=10)

    class Meta:
        ordering = ['ordinal']
        unique_together = (("question", "text"),)

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.question.text, self.text)


class QuestionConfig(models.Model):
    question = models.OneToOneField(Question)
    question_type = models.ForeignKey(QuestionType)
    required = models.BooleanField(default=False)
    create_new_answer_row_on_update = models.BooleanField(default=False)
    depends_on_question = models.ForeignKey(
        Question, related_name='depends_on_question', blank=True, null=True)
    show_when_the_answer_is = models.ForeignKey(
        QuestionAnswerChoice, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.question.text, self.question_type.name)


class QuestionValidatorCv(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.name)


class QuestionValidationConfig(models.Model):
    question = models.ForeignKey(Question)
    validator = models.ForeignKey(QuestionValidatorCv)
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.question.text + self.value)


class AnswerLogForRadio(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(QuestionAnswerChoice)
    added_by = models.ForeignKey(User, related_name='radio_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question')


class AnswerLogForCheckbox(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(QuestionAnswerChoice)
    added_by = models.ForeignKey(User, related_name='checkbox_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question', 'answer')


class AnswerLogForDropDown(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(QuestionAnswerChoice)
    added_by = models.ForeignKey(User, related_name='dropdown_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question')


class AnswerLogForTextInput(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.TextField()
    added_by = models.ForeignKey(User, related_name='text_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question')


class AnswerLogForPassword(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=128)
    added_by = models.ForeignKey(User, related_name='password_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question')


class AnswerLogForNumberInput(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    farmer = models.ForeignKey(Farmer, null=True, blank=True)
    sowing = models.ForeignKey(Sowing, null=True, blank=True)
    water_resource = models.ForeignKey(WaterResource, null=True, blank=True)
    question = models.ForeignKey(Question)
    answer = models.DecimalField(max_digits=10, decimal_places=2)
    added_by = models.ForeignKey(User, related_name='number_answer_added_by')
    is_current = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('user', 'farmer', 'sowing', 'field', 'question')


# user based provision system

class OperationCv(models.Model):
    name = models.CharField(max_length=100)
    
    # edit, delete, create, view
    def __unicode__(self):
        return str(self.name)


class ActionModuleCv(models.Model):
    name = models.CharField(max_length=100)
    
    # sowing, farmer, water, procurement
    def __unicode__(self):
        return str(self.name)


class HardwareDevice(models.Model):
    name = models.CharField(max_length=100)
    
    # mobile, portal
    def __unicode__(self):
        return str(self.name)


class UsertypeBasedAccessControl(models.Model):
    user_type = models.ForeignKey(UserType)
    module = models.ForeignKey(ActionModuleCv)
    hardware_device = models.ForeignKey(HardwareDevice)
    operation = models.ForeignKey(OperationCv)
    access = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='created_by')
    modified_by = models.ForeignKey(User, related_name='modified_by')
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_type', 'module', 'operation', 'hardware_device')


def get_sowing_avtivity_image_save_location(instance, filename):
    return f"sowing_avtivity_image/{instance.sowing_id}/{filename}"

class ShowingActivityImages(models.Model):
    sowing = models.ForeignKey(Sowing)
    cultivation_phase = models.ForeignKey(CultivationPhase)
    image = models.ImageField(max_length=1000, upload_to=get_sowing_avtivity_image_save_location)


class GapGradeCv(models.Model):
    name = models.CharField(max_length=5)
    ordinal = models.IntegerField()

class SeasonBasedGap(models.Model):
    season = models.ForeignKey(Season)
    action_name = models.CharField(max_length=50)
    followup_date = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    ordinal = models.IntegerField()
    quantity = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='seasonbasedgap_created_by')
    modified_by = models.ForeignKey(User, related_name='seasonbasedgap_modified_by')
    time_modified = models.DateTimeField(auto_now=True)

class TempSeasonBasedGap(models.Model):
    season = models.ForeignKey(Season)
    action_name = models.CharField(max_length=50)
    followup_date = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    ordinal = models.IntegerField()
    quantity = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='tempseasonbasedgap_created_by')
    modified_by = models.ForeignKey(User, related_name='tempseasonbasedgap_modified_by')
    time_modified = models.DateTimeField(auto_now=True)


class SeasonBasesFarmerGpaLog(models.Model):
    season = models.ForeignKey(Season)
    gap = models.ForeignKey(SeasonBasedGap)
    sowing = models.ForeignKey(Sowing)
    tp_date = models.DateField(blank=True, null=True)
    expected_date = models.DateField(blank=True, null=True)
    actual_date = models.DateField(blank=True, null=True)
    variations = models.PositiveIntegerField(verbose_name="action_day_differences")
    grade = models.ForeignKey(GapGradeCv, blank=True, null=True)
    is_skip = models.IntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='seasonbasesfarmergpalog_created_by')
    modified_by = models.ForeignKey(User, related_name='seasonbasesfarmergpalog_modified_by')
    time_modified = models.DateTimeField(auto_now=True)


class GapQuestionType(models.Model):
    name = models.CharField(max_length=15)

class TempSeasonBasedGapQuestion(models.Model):
    gap = models.ForeignKey(TempSeasonBasedGap)
    questions = models.TextField(blank=True, null=True)
    question_type = models.ForeignKey(GapQuestionType)
    ordinal = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_manditory = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='temp_gapquestions_created_by')
    modified_by = models.ForeignKey(User, related_name='temp_gapquestions_modified_by')
    time_modified = models.DateTimeField(auto_now=True)
  
class SeasonBasedGapQuestion(models.Model):
    gap = models.ForeignKey(SeasonBasedGap)
    questions = models.TextField(blank=True, null=True)
    question_type = models.ForeignKey(GapQuestionType)
    ordinal = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_manditory = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='gapquestions_created_by')
    modified_by = models.ForeignKey(User, related_name='gapquestions_modified_by')
    time_modified = models.DateTimeField(auto_now=True)
  

class SeasonBasesFarmerGpaQuestionAnswerLog(models.Model):
    farmer_gap_log = models.ForeignKey(SeasonBasesFarmerGpaLog, blank=True, null=True)
    question = models.ForeignKey(SeasonBasedGapQuestion, blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    is_skipped = models.BooleanField(default=False)