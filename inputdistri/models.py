from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.fields import CharField, DateField
from instance.models import *
# Create your models here.

# Define Units
# Compare their relationship with base SI Units
# Will help in scaling up and down various Units (for eg Ton to Kg conversion)


class UpOrDown(models.Model):
    name = models.CharField(max_length=50)
    # up or down

    def __str__(self):
        return self.name


class UnitType(models.Model):
    name = models.CharField(max_length=50)
    # weight, Volume, count, Length

    def __str__(self):
        return self.name


class BaseUnit(models.Model):
    type = models.ForeignKey(UnitType)
    name = models.CharField(max_length=50)
    # kg, l , number, m

    def __str__(self):
        return '{} : {} ({})'.format(self.name, self.type.name, self.id)


class Unit(models.Model):
    type = models.ForeignKey(UnitType)
    name = models.CharField(max_length=50)
    base_unit = models.ForeignKey(BaseUnit)
    factor_to_base_si_unit = models.PositiveIntegerField()
    direction_to_base_si_unit = models.ForeignKey(UpOrDown)
    # kg, lit, metre, nos

    def __str__(self):
        return self.name


# Input Item Section
# Input Inventory Management

class StorageType(models.Model):
    name = models.CharField(max_length=100)


# Storage set up
class Storage(models.Model):
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=250)
    type = models.ForeignKey(StorageType)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
     # Created User details
    created_by = models.ForeignKey(User, related_name='storage_created_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)

class SubStorage(models.Model):
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=250)
    type = models.ForeignKey(StorageType)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
     # Created User details
    created_by = models.ForeignKey(User, related_name='sub_storage_created_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# type of input like seed, kit , agrochemical
class InputType(models.Model):
    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=50)
    display_ordinal = models.PositiveIntegerField(default=0)
    # seed, agrochemical, fertilizer

    def __str__(self):
        return self.name


class InputName(models.Model):
    input_type = models.ForeignKey(InputType)
    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class AreaCv(models.Model):
    display_name = models.CharField(max_length=50)
    quantity_in_acre = models.DecimalField(max_digits=5, decimal_places=2)
    # 1 ac,  half ac

    def __str__(self):
        return self.display_name

# input like seed 250 kg, seed 500 kg, kit, urea
class InputCombo(models.Model):
    business = models.ForeignKey(Business)
    name = models.CharField(max_length=50)
    area = models.ForeignKey(AreaCv)
    is_active = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    display_ordinal = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, related_name='input_item_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_item_modified_by_instance')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# contents of kit / components of input item
class InputPart(models.Model):
    name = models.ForeignKey(InputName)
    input_combo = models.ForeignKey(InputCombo)
    value = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.ForeignKey(Unit)
    created_by = models.ForeignKey(User, related_name='input_part_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_part_modified_by_instance')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} : {} ({})'.format(self.name.name, self.name, self.id)


class InputGoodsCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()
    input_type = models.ForeignKey(InputType)
    input_code_prefix = models.CharField(max_length=5) #IG

    #IG21S001


class Supplier(models.Model):
    name = models.CharField(max_length=50)


class InputGoods(models.Model):
    business = models.ForeignKey(Business)
    code = models.CharField(max_length=50)
    input_name = models.ForeignKey(InputName)
    number_of_units = models.PositiveIntegerField()
    unit = models.ForeignKey(Unit)
    season = models.ForeignKey(Season)
    unit_quantity = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_at_receipt = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now_time = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.ForeignKey(Supplier)
    date_of_receipt = models.DateField()
    date_of_manufacturing = models.DateField()
    date_of_expiry = models.DateField()
    created_by = models.ForeignKey(User, related_name='input_batch_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_batch_modified_by_instance')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}({})'.format(self.code, self.id)


class InputGoodsExpiryDateTrace(models.Model):
    input_goods = models.ForeignKey(InputGoods)
    date_of_expiry = models.DateField()
    changed_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class InputPacketInventoryCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()
    code_prefix = models.CharField(max_length=5) #IC

    #IC210001


class InputPacketInventory(models.Model):
    season = models.ForeignKey(Season)
    packet_code = models.CharField(max_length=10) # IC210001
    input_combo = models.ForeignKey(InputCombo)
    quantity_at_receipt = models.PositiveIntegerField()
    quantity_now = models.PositiveIntegerField()
    quantity_now_time = models.DateTimeField()
    unit = models.ForeignKey(Unit) #default :  nos
    price_per_packet = models.DecimalField(max_digits=10, decimal_places=2) # copy from main combo
    date_of_expiry = models.DateField()
    created_by = models.ForeignKey(User, related_name='input_item_input_batch_map_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_item_input_batch_modified_by_instance')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class InputPacketInventoryExpiryDateTrace(models.Model):
    input_packet_inventory = models.ForeignKey(InputPacketInventory)
    date_of_expiry = models.DateField()
    changed_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class InputPacketInventoryPart(models.Model):
    input_packet_inventory = models.ForeignKey(InputPacketInventory)
    part = models.ForeignKey(InputPart)
    input_goods = models.ForeignKey(InputGoods)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class InputPacketInventoryLabel(models.Model):
    input_packet_inventory = models.ForeignKey(InputPacketInventory)
    label_prefix = models.CharField(max_length=10)
    label_suffix = models.CharField(max_length=10)
    label_range_start_default = models.PositiveIntegerField()
    label_range_start = models.PositiveIntegerField()
    label_range_end = models.PositiveIntegerField()
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class InputStoreInventory(models.Model):
    season = models.ForeignKey(Season)
    input_packet_inventory = models.ForeignKey(InputPacketInventory)
    storage = models.ForeignKey(Storage)
    section = models.CharField(max_length=250, blank=True, null=True)
    sub_section = models.CharField(max_length=250, blank=True, null=True)
    date_of_receipt = models.DateField()
    quantity_at_receipt = models.PositiveIntegerField()
    quantity_now = models.PositiveIntegerField()
    quantity_now_time = models.DateTimeField()
    unit = models.ForeignKey(Unit)
    label_range_start = models.PositiveIntegerField()
    label_range_end = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, related_name='input_storage_location_map_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_storage_location_batch_modified_by_instance')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class InputStockStatus(models.Model):
    name = models.CharField(max_length=50)
    # issued, at_storage


class InputStoreInventoryPacketLabel(models.Model):
    input_store_inventory = models.ForeignKey(InputStoreInventory)
    label = models.CharField(max_length=50)
    stock_status = models.ForeignKey(InputStockStatus)
    received_date = models.DateTimeField()
    received_by = models.ForeignKey(User, related_name='input_batch_packet_labeled_recieved_by_instance')
    dispatched_date = models.DateTimeField(blank=True, null=True)
    dispatched_by = models.ForeignKey(User, related_name='input_batch_packet_labeled_dispatched_by_instance', blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

class SubStoreRequestStatus(models.Model):
    name = models.CharField(max_length=70)
    # approved, decline, issed

class SubStoreRequestCodeBank(models.Model):
    last_digit = models.PositiveIntegerField() 
    code_prefix = models.CharField(max_length=10)


class InputSubStoreInventory(models.Model):
    season = models.ForeignKey(Season)
    input_store_inventory = models.ForeignKey(InputStoreInventory)
    sub_storage = models.ForeignKey(SubStorage)
    section = models.CharField(max_length=250, blank=True, null=True)
    sub_section = models.CharField(max_length=250, blank=True, null=True)
    date_of_receipt = models.DateField()
    quantity_at_receipt = models.PositiveIntegerField()
    quantity_now = models.PositiveIntegerField()
    quantity_now_time = models.DateTimeField()
    unit = models.ForeignKey(Unit)
    label_range_start = models.CharField(max_length=50)
    label_range_end = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, related_name='input_sub_storage_location_map_created_by_instance')
    modified_by = models.ForeignKey(User, related_name='input_sub_storage_location_batch_modified_by_instance')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class InputSubStoreInventoryPacketLabel(models.Model):
    input_sub_store_inventory = models.ForeignKey(InputSubStoreInventory)
    label = models.CharField(max_length=50)
    stock_status = models.ForeignKey(InputStockStatus)
    received_date = models.DateTimeField()
    received_by = models.ForeignKey(User, related_name='input_sub_store_batch_packet_labeled_recieved_by_instance')
    dispatched_date = models.DateTimeField(blank=True, null=True)
    dispatched_by = models.ForeignKey(User, related_name='input_sub_store_batch_packet_labeled_dispatched_by_instance', blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class SubStoreRequestLog(models.Model):
    input_combo = models.ForeignKey(InputCombo)
    request_code = models.CharField(max_length=15) #req_21_00001
    storage = models.ForeignKey(SubStorage)
    section = models.CharField(max_length=250, blank=True, null=True)
    sub_section = models.CharField(max_length=250, blank=True, null=True)
    requested_quantity = models.PositiveIntegerField()
    unit = models.ForeignKey(Unit)
    requested_by = models.ForeignKey(User, related_name='requested_by')
    requested_at = models.DateTimeField()
    status = models.ForeignKey(SubStoreRequestStatus)
    input_sub_store_inventory = models.ManyToManyField(InputSubStoreInventory)
    responsed_by = models.ForeignKey(User, related_name='responsed_by', blank=True, null=True)
    responsed_at = models.DateTimeField(blank=True, null=True)
    declined_reason = models.TextField(blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

    
class MaxStatus(models.Model):
    name = models.CharField(max_length=70)
    # rised, approved by s super, approved aas, 

    
class MaxStatusForReturn(models.Model):
    name = models.CharField(max_length=70)
    # rised by s su, approved by as manage, agri offc iss, decline


class IssueRequestStatus(models.Model):
    name = models.CharField(max_length=70)
    # approved, decline, issed, parlicied


class ComboIssueRequestCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()
    input_combo  = models.ForeignKey(InputCombo)

class ShopType(models.Model):
    name = models.CharField(max_length=100)

class Shop(models.Model):
    name = models.CharField(max_length=250)
    contact_person = models.CharField(max_length=100)
    contact_person_mobile_number = models.CharField(max_length=13)
    shop_mobile = models.CharField(max_length=13)
    type = models.ForeignKey(ShopType)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='shop_created_by')
    time_created = models.DateTimeField(auto_now_add=True)


class ComboIssueRequest(models.Model):
    season = models.ForeignKey(Season)
    request_code = models.CharField(max_length=50)
    input_combo  = models.ForeignKey(InputCombo)
    quantity_in_numbers = models.PositiveIntegerField()
    quantity_for_area = models.DecimalField(max_digits=7, decimal_places=2)
    expected_date = models.DateTimeField()
    issue_rised_date = models.DateTimeField()
    max_status = models.ForeignKey(MaxStatus) 
    max_status_date = models.DateTimeField()
    supervisor = models.ForeignKey(User, related_name='supervisor_user_id')

    senior_supervisor = models.ForeignKey(User, related_name='senior_supervisor_user_id', blank=True, null=True)
    senior_supervisor_status = models.ForeignKey(IssueRequestStatus, related_name='senior_supervisor_status', blank=True, null=True) #approved, decline
    senior_supervisor_status_date = models.DateTimeField(blank=True, null=True)
    
    assitant_manager = models.ForeignKey(User, related_name='asst_manager_user_id', blank=True, null=True)
    assitant_manager_status = models.ForeignKey(IssueRequestStatus, related_name='assitant_manager_status', blank=True, null=True) #approved, decline
    assitant_manager_status_date =  models.DateTimeField(blank=True, null=True)

    agri_officer = models.ForeignKey(User, related_name='agri_offcier_user_id', blank=True, null=True)
    agri_officer_status = models.ForeignKey(IssueRequestStatus, related_name='agri_officer_status',  blank=True, null=True) 
    agri_officer_status_date =  models.DateTimeField(blank=True, null=True)

    gm = models.ForeignKey(User, related_name='gm_user_id', blank=True, null=True)
    gm_status = models.ForeignKey(IssueRequestStatus, related_name='gm_status',  blank=True, null=True) #approved, decline, issued, parlicied
    gm_status_date =  models.DateTimeField(blank=True, null=True)

    dispatched_by = models.ForeignKey(User, related_name='dispatched_by', blank=True, null=True)
    dispatch_status = models.ForeignKey(IssueRequestStatus, related_name='dispatch_status',  blank=True, null=True) #approved, decline, issued, parlicied
    dispatch_date =  models.DateTimeField(blank=True, null=True)

    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


def get_path_for_agent_issue_notice(instance, filename):
    return "agent_issue_notice/{agent_id}/{date}/{file}".format(agent_id=instance.agent.user.id, date=instance.time_created, file=filename)


class AgentIssueNoticeNumberCodeBank(models.Model):
    last_bill_number = models.PositiveIntegerField()


class ComboIssueRequestAgentMap(models.Model):
    combo_issue_request = models.ForeignKey(ComboIssueRequest)
    agent = models.ForeignKey(User, related_name='agent_user_id')
    max_status = models.ForeignKey(MaxStatus)
    shop = models.ForeignKey(Shop, blank=True, null=True)
    delivery_from = models.CharField(max_length=250, blank=True, null=True,)
    delivery_to = models.CharField(max_length=250, blank=True, null=True,)
    shop_modified_by = models.ForeignKey(User, related_name='shop_modified_by', blank=True, null=True)
    issue_rised_date = models.DateTimeField()
    quantity_in_numbers = models.PositiveIntegerField()
    issue_notice = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_path_for_agent_issue_notice)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

class ComboIssueDeleteAgentLog(models.Model):
    combo_issue_request = models.ForeignKey(ComboIssueRequest)
    agent = models.ForeignKey(User, related_name='deleted_agent_user_id')
    issue_raised_date = models.DateTimeField()
    quantity_in_numbers = models.PositiveIntegerField()
    removed_by = models.ForeignKey(User, related_name='deleted_by_user_id')
    time_created = models.DateTimeField(auto_now_add=True)


class ComboIssueRegisterAgentMap(models.Model):
    supervisor = models.ForeignKey(User, related_name='supervisor_user_id_for_request_register')
    input_combo  = models.ForeignKey(InputCombo)
    agent = models.ForeignKey(User, related_name='agent_user_id_for_request_register')
    quantity_in_numbers = models.PositiveIntegerField(default=0)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

class AgentInventoryCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()

class AgentInventory(models.Model):
    season = models.ForeignKey(Season)
    agent = models.ForeignKey(User) # agent user
    combo_issue_request = models.ForeignKey(ComboIssueRequest, blank=True, null=True)
    date_of_receipt = models.DateField()
    quantity_at_receipt = models.PositiveIntegerField()
    quantity_now = models.PositiveIntegerField()
    quantity_now_time = models.DateTimeField()
    unit = models.ForeignKey(Unit)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, related_name='inputitem_inputbatch_agent_inventory_created')
    modified_by = models.ForeignKey(User, related_name='inputitem_inputbatch_agent_inventory_modified')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class AgentInventoryStoreLabelRangeMap(models.Model):
    agent_inventory = models.ForeignKey(AgentInventory)
    input_sub_store_inventory = models.ForeignKey(InputSubStoreInventory)
    label_range_from = models.CharField(max_length=15)
    label_range_to = models.CharField(max_length=15, blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)
    

class AvailabilityStatus(models.Model):
    name = models.CharField(max_length=100)
    # issued, returned


class SubStoreIssueLabelAgentMap(models.Model):
    input_sub_store_inventory = models.ForeignKey(InputSubStoreInventory)
    agent = models.ForeignKey(User, related_name='agent_user')
    combo_issue_request_agent_map = models.ForeignKey(ComboIssueRequestAgentMap)
    agent_inventory = models.ForeignKey(AgentInventory)
    label = models.CharField(max_length=50)
    status = models.ForeignKey(AvailabilityStatus, related_name='availability_status', blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='store_issue_label_agent_created')
    modified_by = models.ForeignKey(User, related_name='store_issue_label_agent_modified')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)
    

class AgentReceiptBillNumberCodeBank(models.Model):
    last_bill_number = models.PositiveIntegerField()


def get_path_for_agent_receipt(instance, filename):
    return "agent_receipt/{agent_id}/{date}/{file}".format(agent_id=instance.agent_inventory.user.id, date=instance.time_created, file=filename)


class ComboIssueAgentInventoryReceipt(models.Model):
    combo_issue_request = models.ForeignKey(ComboIssueRequest)
    agent = models.ForeignKey(User)
    bill_number = models.CharField(max_length=10)
    file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_path_for_agent_receipt)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ReturnableComboItems(models.Model):
    season = models.ForeignKey(Season)
    input_combo  = models.ForeignKey(InputCombo)



class ComboReturnRequestCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()
    input_combo  = models.ForeignKey(InputCombo)

class ComboReturnRequest(models.Model):
    season = models.ForeignKey(Season)
    agent = models.ForeignKey(User, related_name='return_requested_agent')
    request_code = models.CharField(max_length=50)
    input_combo  = models.ForeignKey(InputCombo)
    request_raised_date = models.DateTimeField()
    max_status = models.ForeignKey(MaxStatusForReturn) 
    max_status_date = models.DateTimeField()

    senior_supervisor = models.ForeignKey(User, related_name='return_request_senior_supervisor_user_id', blank=True, null=True)
    senior_supervisor_remarks = models.TextField(blank=True, null=True)
    
    assitant_manager = models.ForeignKey(User, related_name='return_request_asst_manager_user_id', blank=True, null=True)
    assitant_manager_remarks = models.TextField(blank=True, null=True)
    assitant_manager_status = models.ForeignKey(IssueRequestStatus, related_name='return_request_assitant_manager_status', blank=True, null=True) #approved, decline
    assitant_manager_status_date =  models.DateTimeField(blank=True, null=True)

    agri_officer = models.ForeignKey(User, related_name='return_request_agri_officer_user_id', blank=True, null=True)
    agri_officer_remarks = models.TextField(blank=True, null=True)
    agri_officer_status = models.ForeignKey(IssueRequestStatus, related_name='return_request_agri_officer_status',  blank=True, null=True) #approved, decline, issued, parlicied
    agri_officer_status_date =  models.DateTimeField(blank=True, null=True)

    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class ComboReturnRequestLabelMap(models.Model):
    combo_return_request = models.ForeignKey(ComboReturnRequest)
    is_dispatchable = models.BooleanField()
    combo_remarks = models.TextField(blank=True, null=True)
    date_of_return = models.DateField()
    return_label = models.ForeignKey(SubStoreIssueLabelAgentMap)
    return_sub_store_inventory = models.ForeignKey(InputSubStoreInventory)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


#
# # ---------------------------------------
# # input return from agent to storage
# # ---------------------------------------
#
# class InputItemReturnLog(models.Model):
#     returned_from = models.ForeignKey(User)
#     item_batch_map = models.ForeignKey(InputItemInputPartBatchMap, blank=True, null=True)
#     quantity_returned = models.PositiveIntegerField()
#     unit = models.ForeignKey(Unit)
#     date_of_return = models.DateField()
#     return_data_stored_by = models.ForeignKey(User, related_name="return_data_stored_by")
#     label_range_from = models.CharField(max_length=15)
#     label_range_to = models.CharField(max_length=15)
#     time_modified = models.DateTimeField(auto_now=True)
#     time_created = models.DateTimeField(auto_now_add=True)


# --------------------------------------------------
# procurement
# --------------------------------------------------

class ProcurementProduce(models.Model):
    name = models.CharField(max_length=50)


class ProcurementTransportInchargeKyc(models.Model):
    aadhar_number = models.CharField(max_length=18)
    name = models.CharField(max_length=30)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class Paymentstatus(models.Model):
    name = models.CharField(max_length=20)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class ProcurementGroup(models.Model):
    agent = models.ForeignKey(User)
    procurement_date = models.DateField()
    procurement_produce = models.ForeignKey(ProcurementProduce)
    season = models.ForeignKey(Season)

    # end product quantity  after removing the gunny bag weight
    produce_net_weight = models.DecimalField(max_digits=10, decimal_places=2)

    # pricing
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit_for_pricing = models.ForeignKey(Unit, related_name="unit_per_for_price_calculation")

    # cost for net weight, net weight * unit price
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    agent_price_deduction = models.DecimalField(max_digits=10, decimal_places=2)

    # pricing / amount to agent wallet deduction
    payment_to_wallet = models.DecimalField(max_digits=10, decimal_places=2)

    # total price after detuction
    payment_to_agent = models.DecimalField(max_digits=10, decimal_places=2)

    created_by = models.ForeignKey(User, related_name='procurement_created_by')
    modified_by = models.ForeignKey(User, related_name='procurement_modified_by')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Procurement(models.Model):
    procurement_group = models.ForeignKey(ProcurementGroup)
    procurement_transaport_incharge_kyc = models.OneToOneField(ProcurementTransportInchargeKyc, on_delete=models.CASCADE)
    ticket_number =  models.CharField(max_length=30, unique=True)
    have_other_agent_farmer = models.BooleanField(default=False)
    # vehicle weight

    vehicle_number = models.CharField(max_length=30)
    vehicle_driver_name = models.CharField(max_length=50)

    # flower weight with gunny bags calculated from the agent
    str_weight = models.DecimalField(max_digits=10, decimal_places=2)
    str_weight_unit = models.ForeignKey(Unit, related_name='str_weight_unit')
    # it is noted when the str value is updated
    remark = models.CharField(max_length=250, blank=True, null=True)

    # in time of vehicle / tare wt
    empty_vehicle_timestamp = models.DateTimeField()
    empty_vehicle_weight_data_inputed = models.CharField(max_length=50, blank=True, null=True)
    empty_vehicle_weight = models.DecimalField(max_digits=10, decimal_places=2)

    # out time of loaded vehicle / gross
    loaded_vehicle_timestamp = models.DateTimeField()
    loaded_vehicle_weight_data_inputed = models.CharField(max_length=50, blank=True, null=True)
    loaded_vehicle_weight = models.DecimalField(max_digits=10, decimal_places=2)

    # gunny bag or exact weight loss model
    gunnybag_count = models.PositiveIntegerField()
    gunnybag_weight = models.DecimalField(max_digits=10, decimal_places=2)
    reason_for_weight_loss = models.CharField(max_length=250, blank=True, null=True)

    moisture = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    # total flower quantity with gunny bag weight
    produce_gross_weight = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(Unit)
    reason_for_payment_hold = models.CharField(max_length=250, blank=True, null=True)
    paymet_status = models.ForeignKey(Paymentstatus, blank=True, null=True)
    utr_number = models.CharField(max_length=30, blank=True, null=True)



# ----------------------------------------------
# agent wallet
# ----------------------------------------------
class AgentWallet(models.Model):
    agent = models.OneToOneField(User)
    current_balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='agent_wallet_modified_by')


# agent to wallet, ccgb to wallet
class TransactionDirection(models.Model):
    payment_from = models.CharField(max_length=50)
    payment_to = models.CharField(max_length=50)
    description = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
# ========================================================================================
# 1 - when buying inputs from ccgb => the amount should be in negative in agent wallet
# 2 - when procurement => one part of amount should be send to wallet for wallet deduction
# 3 - when procurement => one part of amount should be given to agent hand as commision
# 4 - when returning the inputs => the amount should be adjusted to the wallet
# =========================================================================================


# approved, declined, waiting
class TransactionApprovalStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


# cash, cheque
class TransactionMode(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# if transaction done thru check
class TransactionChequeDetails(models.Model):
    bank_name = models.CharField(max_length=150)
    branch_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    micr_code = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    date_of_issue = models.DateField()
    cheque_number = models.PositiveIntegerField()
    is_cleared = models.BooleanField(default=False)
    cheque_cleared_date = models.DateField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.cheque_number)


# transaction history
class AgentTransactionLog(models.Model):
    date = models.DateField()
    transaction_direction = models.ForeignKey(TransactionDirection)
    agent = models.ForeignKey(User, related_name='agent_id')
    data_entered_by = models.ForeignKey(User, related_name='transaction_initiated_user')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=20, null=True, blank=True)
    transaction_mode = models.ForeignKey(TransactionMode)
    transaction_approval_status = models.ForeignKey(TransactionApprovalStatus)
    wallet_balance_before_this_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_balance_after_this_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    cheque_detail = models.ForeignKey(TransactionChequeDetails, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='transaction_log_modified_by')


# procurement and transaction map
class ProcurementTransactionMap(models.Model):
    transaction_log = models.ForeignKey(AgentTransactionLog)
    procurement = models.ForeignKey(Procurement)


# # input distribution and transaction map
# class InputDistributionTransactionMap(models.Model):
#     transaction_log = models.ForeignKey(AgentTransactionLog)
#     input_item_sale = models.ForeignKey(InputItemInputBatchAgentInventory)
#
#
# # input return and transaction map
# class InputReturnTransactionMap(models.Model):
#     transaction_log = models.ForeignKey(AgentTransactionLog)
#     input_item_return = models.ForeignKey(InputItemReturnLog)



# --------------------------------------
# forecast
# --------------------------------------

# harvest 1 - 55 days, harvest 2 - 7 days
class HarvestLevel(models.Model):
    harvest_name = models.CharField(max_length=50)
    ordinal = models.PositiveSmallIntegerField()
    harvest_interval_duration_in_days = models.CharField(max_length=50)
    notice_period = models.CharField(max_length=10)


class YeildPrediction(models.Model):
    crop = models.ForeignKey(Crop)
    season = models.ForeignKey(Season)
    acre = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    expected_yeild_weight_in_kg = models.DecimalField(max_digits=10, decimal_places=2)
    harvest_range = models.ForeignKey(HarvestLevel)


class Harvest(models.Model):
    sowing = models.ForeignKey(Sowing)
    date_of_harvest = models.DateField()

    value = models.IntegerField()
    unit = models.ForeignKey(Unit)
    ticket_number = models.CharField(max_length=25)

    nth_harvest = models.ForeignKey(HarvestLevel, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    device_datacapture_datetime = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='harvest_created_by')
    modified_by = models.ForeignKey(User, related_name='harvest_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.value)

    class Meta:
        unique_together = ('sowing', 'date_of_harvest', 'value', 'ticket_number')


# grade, price,
class harvestPropertyName(models.Model):
    name = models.CharField(max_length=100)


class HarvestProperty(models.Model):
    harvest = models.ForeignKey(Harvest)
    property = models.ForeignKey(harvestPropertyName)
    value = models.CharField(max_length=100)


# pricing table for agents
class AgentProcurementPrice(models.Model):
    agent = models.ForeignKey(User)
    season = models.ForeignKey(Season)
    produce = models.ForeignKey(ProcurementProduce)
    default_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class AgentFarmerDistributionSowing(models.Model):
    sowing = models.ForeignKey(Sowing)
    season = models.ForeignKey(Season)
    agent = models.ForeignKey(User)
    input_combo  = models.ForeignKey(InputCombo)
    no_of_unit = models.PositiveIntegerField()
    acre = models.PositiveIntegerField()
    dispatched_date = models.DateTimeField(blank=True, null=True)


class AgentFarmerDistributionMap(models.Model):
    agent_farmer_distribution_sowing = models.ForeignKey(AgentFarmerDistributionSowing)
    label = models.ForeignKey(SubStoreIssueLabelAgentMap)
    created_by = models.ForeignKey(User, related_name='distribution_created_by')
    modified_by = models.ForeignKey(User, related_name='distribution_modified_by')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class AgentDistributionPrice(models.Model):
    agent = models.ForeignKey(User)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    updated_on = models.DateTimeField()
    season = models.ForeignKey(Season, blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class DistributionAgentPriceChangeRequestStatus(models.Model):
    name = models.CharField(max_length=100)


class  DistributionPriceChangeRequestCodeBank(models.Model):
    last_digit = models.PositiveIntegerField()


class AgentDistributionPriceChangeRequest(models.Model):
    request_code = models.CharField(max_length=100)
    requested_by = models.ForeignKey(User, related_name='requested_by_instance')
    requested_on = models.DateField()
    approved_by = models.ForeignKey(User, blank=True, null=True)
    status_date = models.DateField(blank=True, null=True)
    status = models.ForeignKey(DistributionAgentPriceChangeRequestStatus)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class DistributionPriceChangeAgentMap(models.Model):
    agent_price_change_request = models.ForeignKey(AgentDistributionPriceChangeRequest)
    agent = models.ForeignKey(User)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class AgentDistributionPriceChangeLog(models.Model):
    agent = models.ForeignKey(User)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    from_date = models.DateField()
    to_date = models.DateField()
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


def get_uploaded_excel_from_weigh_bridge_man(instance, filename):
    return "procurement/{date}/{file}".format(date=instance.uploaded_at, file=filename)

class ProcurementFileUpload(models.Model):
    season = models.ForeignKey(Season)
    uploaded_by = models.ForeignKey(User)
    uploaded_at = models.DateTimeField()
    uploaded_count = models.PositiveIntegerField()
    excel_file = models.FileField(upload_to=get_uploaded_excel_from_weigh_bridge_man, max_length = 200)
    file_name = models.CharField(max_length=100, blank=True, null=True)  
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class TempProcurement(models.Model):
    procurement_file_upload = models.ForeignKey(ProcurementFileUpload)
    ticket_number =  models.CharField(max_length=30, unique=True)
    id_company = models.CharField(max_length=30)
    customer_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=30)
    vehicle_driver_name = models.CharField(max_length=50)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2)
    gross_time = models.DateTimeField()
    tare_weight = models.DecimalField(max_digits=10, decimal_places=2)
    tare_time = models.DateTimeField()
    net_wt = models.DecimalField(max_digits=10, decimal_places=2)
    bag_number = models.PositiveIntegerField()
    bag_weight = models.DecimalField(max_digits=10, decimal_places=2)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    amount =  models.DecimalField(max_digits=10, decimal_places=2)
    gross_operator = models.CharField(max_length=30)
    is_uploaded = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    deduct = models.DecimalField(max_digits=10, decimal_places=2)
    moisture = models.DecimalField(max_digits=10, decimal_places=2)
    tare_operator = models.CharField(max_length=30)
    date = models.DateField()

# input distribution and transaction map
class InputDistributionTransactionMap(models.Model):
    agent_inventory = models.ForeignKey(AgentInventory)
    transaction_log = models.ForeignKey(AgentTransactionLog)

class InputReturnTransactionLog(models.Model):
    transaction_log = models.ForeignKey(AgentTransactionLog)
    combo_return_request = models.ForeignKey(ComboReturnRequest)

class InputProcurementTransactionLog(models.Model):
    transaction_log = models.ForeignKey(AgentTransactionLog)
    procurement = models.ForeignKey(Procurement)

class DeleteProcurementLog(models.Model):
    agent = models.ForeignKey(User)
    ticket_number =  models.CharField(max_length=30, unique=True)
    produce_net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    payment_to_wallet = models.DecimalField(max_digits=10, decimal_places=2)
    deleted_by = models.ForeignKey(User, related_name='delete_modified_by')

class DeleteTempProcurementTrack(models.Model):
    ticket_number =  models.CharField(max_length=30, unique=True)
    id_company = models.CharField(max_length=30)
    customer_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=30)
    vehicle_driver_name = models.CharField(max_length=50)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2)
    gross_time = models.DateTimeField()
    tare_weight = models.DecimalField(max_digits=10, decimal_places=2)
    tare_time = models.DateTimeField()
    net_wt = models.DecimalField(max_digits=10, decimal_places=2)
    bag_number = models.PositiveIntegerField()
    bag_weight = models.DecimalField(max_digits=10, decimal_places=2)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    amount =  models.DecimalField(max_digits=10, decimal_places=2)
    gross_operator = models.CharField(max_length=30)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    moisture = models.DecimalField(max_digits=10, decimal_places=2)
    tare_operator = models.CharField(max_length=30)
    date = models.DateField()

class InputDistributionOtherStoreTransactionMap(models.Model):
    combo_issue_request = models.ForeignKey(ComboIssueRequest)
    transaction_log = models.ForeignKey(AgentTransactionLog)

class AgentMergeloadEnable(models.Model):
    season = models.ForeignKey(Season)
    agent = models.ForeignKey(User)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, blank=True, null=True,related_name='Enabled_by')
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

#TDTA Travel and allowance
class AllowanceType(models.Model):
    name = models.CharField(max_length=20)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

class AllowanceExpenseType(models.Model):
    name = models.CharField(max_length=20)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

class UsertypewiseAllowanceCost(models.Model):
    expence_type = models.ForeignKey(AllowanceExpenseType, blank=True, null=True)
    user_type = models.ForeignKey(UserType)
    allowance_type = models.ForeignKey(AllowanceType)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    max_status = models.ForeignKey(MaxStatus, blank=True, null=True) 
    max_status_date = models.DateTimeField(blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


class AllowanceStatus(models.Model):
   name = models.CharField(max_length=70)
    # rised, approved, declined

class Allowance(models.Model):
    season = models.ForeignKey(Season)
    date = models.DateField()
    user = models.ForeignKey(User, related_name='allowance_created_for')
    allowance_type = models.ForeignKey(AllowanceType, blank=True, null=True)
    allowance_status = models.ForeignKey(AllowanceStatus, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_status = models.ForeignKey(MaxStatus, blank=True, null=True) 
    max_status_date = models.DateTimeField(blank=True, null=True)

    senior_supervisor = models.ForeignKey(User, related_name='senior_supervisor_userid', blank=True, null=True)
    senior_supervisor_status = models.ForeignKey(IssueRequestStatus, related_name='senior_supervisor_status_allowance', blank=True, null=True) #approved, decline
    senior_supervisor_status_date = models.DateTimeField(blank=True, null=True)
    
    assitant_manager = models.ForeignKey(User, related_name='asst_manager_userid', blank=True, null=True)
    assitant_manager_status = models.ForeignKey(IssueRequestStatus, related_name='assitant_manager_status_allowance', blank=True, null=True) #approved, decline
    assitant_manager_status_date =  models.DateTimeField(blank=True, null=True)

    agri_officer = models.ForeignKey(User, related_name='agri_offcier_userid', blank=True, null=True)
    agri_officer_status = models.ForeignKey(IssueRequestStatus, related_name='agri_officer_status_allowance',  blank=True, null=True) 
    agri_officer_status_date =  models.DateTimeField(blank=True, null=True)

    gm = models.ForeignKey(User, related_name='gm_userid', blank=True, null=True)
    gm_status = models.ForeignKey(IssueRequestStatus, related_name='gm_status_allowance',  blank=True, null=True) #approved, decline, issued, parlicied
    gm_status_date =  models.DateTimeField(blank=True, null=True)

    travelled_kilometre = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,)
    created_by = models.ForeignKey(User, related_name='allowance_created_by')
    description = models.TextField(blank=True, null=True)
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

def upload_from_kilometre(instance, filename):
    return "Allowance/from_kilometre_img/{user_id}/{date}/{file}".format(user_id=instance.allowance.user.id, date=instance.date, file=filename)

def upload_to_kilometre(instance, filename):
    return "Allowance/to_kilometreimg/{user_id}/{date}/{file}".format(user_id=instance.allowance.user.id, date=instance.date, file=filename)

class TravelAllowanceDetilas(models.Model):
    allowance = models.ForeignKey(Allowance)
    date = models.DateField()
    from_kilometre = models.DecimalField(max_digits=10, decimal_places=2)
    to_kilometre =  models.DecimalField(max_digits=10, decimal_places=2)
    from_captured_image = models.FileField(max_length=1000, blank=True, null=True, upload_to=upload_from_kilometre)
    to_captured_image = models.FileField(max_length=1000, blank=True, null=True, upload_to=upload_to_kilometre)





