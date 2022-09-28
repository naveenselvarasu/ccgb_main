from instance.models import *
from inputdistri.models import *
import datetime
import pandas as pd
import numpy as np
from inputdistri.models import *
from decimal import *
from django.db.models import Sum
from collections import defaultdict, OrderedDict, Counter
import datetime
from pytz import timezone
import plivo

season_id=Season.objects.get(is_active=True).id

def test(args):
    f = open("../guru99.txt", "w+")
    for i in range(10):
        f.write("This is line %d\r\n" % (i + 1))
    f.close()

def check_test_cases():
    if not cluster_supervisor_count():
        result = 'Error_in_Function_1'
        send_message(result)
    elif not agent_count_in_cluster_and_supervisor():
        result = 'Error_in_Function_2'
        send_message(result)
    elif not total_cluster_and_superviosr_farmer_count():
        result = 'Error_in_Function_3'
        send_message(result)
    elif not check_individual_cluster_and_supervior_count():
        result = 'Error_in_Function_4'
        send_message(result)
    elif not check_individual_superviosr_and_agent_farmer_count():
        result = 'Error_in_Function_5'
        send_message(result)
    elif not check_agent_and_farmers_are_same_cluster():
        result = 'Error_in_Function_6'
        send_message(result)
    elif not check_superviosr_and_farmers_are_same_cluster():
        result = 'Error_in_Function_7'
        send_message(result)
    elif not check_both_agent_and_superviosr_same_cluster():
        result = 'Error_in_Function_8'
        send_message(result)
    elif not check_seasonal_farmer_code():
        result = 'Error_in_Function_9'
        send_message(result)
    elif not aadhaar_id_userprofile_count():
        result = 'Error_in_Function_11'
        send_message(result)
    elif not check_one_agent_in_multiple_cluster():
        result = 'Error_in_Function_12'
        send_message(result)
    elif not check_farmer_id_in_user_farmer_map():
        result = 'Error_in_Function_13'
        send_message(result)
    elif not check_farmer_id_in_agent_farmer_map():
        result = 'Error_in_Function_14'
        send_message(result)
    print('success')

def send_message(result):
    print(result)
    client = plivo.RestClient('MAZJZINTYZZTQ4MTG0MT','NWJkN2Q5MGM2OGI2Njc1MGM3NzMzMmMyZjQyYWIw')
    message_created = client.messages.create(
        src='+919500989012',
        # dst='+918610233729',
        dst='+919566558238',
        text=result)
        # send_message(result)

# 1. To check cluster and supervisor count
def cluster_supervisor_count():
    print('To check cluster and supervisor count')
    cluster_count = ClusterSeasonMap.objects.filter(season_id=season_id).count()
    superviosr_count = UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).count()
    if cluster_count != superviosr_count:
        result = False
    else:
        result = True
        
    return result

# 2. To check agent count in cluster and superviosr
def agent_count_in_cluster_and_supervisor():
    print('To check agent_count_in_cluster_and_supervisor')
    supervisor_ids = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id',flat=True))
    supervisor_ids

    for supervisor_id in supervisor_ids:
        superviosr_agent_count = AgentSupervisorSeasonMap.objects.filter(season_id=season_id, supervisor_id=supervisor_id).count()

        cluster_id = UserClusterMap.objects.get(season_id=season_id, user_id=supervisor_id).cluster_id
        cluster_agent_count = UserClusterMap.objects.filter(season_id=season_id, cluster_id=cluster_id, user__userprofile__user_type_id=6).count()
        
        if superviosr_agent_count != cluster_agent_count:
            return False
    return True


# 3. To check Total cluster and superviosr farmer count
def total_cluster_and_superviosr_farmer_count():
    print('To check Total cluster and superviosr farmer count')
    season_id =3

    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    superviosr_ids = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id', flat=True))

    total_cluster_farmer_count = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).count()
    total_superviosr_farmer_count = UserFarmerMap.objects.filter(farmer__season_id=season_id, officer_id__in=superviosr_ids).count()

    if total_cluster_farmer_count != total_superviosr_farmer_count:
        result = False
    else:
        result = True
    return result

# 4. To check individual cluster and supervior count
def check_individual_cluster_and_supervior_count():
    print('To check individual cluster and supervior count')
    season_id =3

    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    for cluster_id in cluster_ids:
        individual_cluster_farmer_count = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id=cluster_id).count()

        superviosr_id = UserClusterMap.objects.get(season_id=season_id, cluster_id=cluster_id, user__userprofile__user_type_id=5).user.id

        individual_superviosr_farmer_count = UserFarmerMap.objects.filter(farmer__season_id=season_id, officer_id=superviosr_id).count()

        mis_matched_farmer_count_differences = individual_cluster_farmer_count - individual_superviosr_farmer_count
        
        if mis_matched_farmer_count_differences != 0:
            return  False
    return True
        
# 5. To check individual superviosr and agent farmer count
def check_individual_superviosr_and_agent_farmer_count():
    print('To check individual superviosr and agent farmer count')

    superviosr_ids = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id', flat=True))
    for superviosr_id in superviosr_ids:
        individual_superviosr_farmer_count = UserFarmerMap.objects.filter(farmer__season_id=season_id, officer_id=superviosr_id).count()

        agent_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id, supervisor_id=superviosr_id).values_list('agent_id', flat=True))
        agent_farmer_count = AgentFarmerMap.objects.filter(farmer__season_id=season_id, agent_id__in=agent_ids).count()

        mis_matched_farmer_count_differences = individual_superviosr_farmer_count - agent_farmer_count
        if mis_matched_farmer_count_differences != 0:
            return False
    return True

#  6. To check agent and farmers are same cluster
def check_agent_and_farmers_are_same_cluster():
    print('To check agent and farmers are same cluster')
    agent_ids_obj = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=6).values_list('user_id', flat=True))
    temp_dict={}
    for agent in agent_ids_obj:
        agent_cluster = UserClusterMap.objects.get(season_id=season_id, user_id=agent).cluster_id
        farmer_ids_obj = list(AgentFarmerMap.objects.filter(agent_id=agent, farmer__season_id=season_id).values_list('farmer__farmer_id',flat=True))
        for farmer in farmer_ids_obj:
            farmer_cluster = FarmerClusterSeasonMap.objects.get(farmer_id=farmer, season_id=season_id).cluster_id
            if agent_cluster != farmer_cluster:
                return False
    return True

# 7. To check superviosr and farmers are same cluster
def check_superviosr_and_farmers_are_same_cluster():
    print('To check superviosr and farmers are same cluster')
    
    superviosr_ids_obj = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id', flat=True))
    temp_dict={}
    for superviosr in superviosr_ids_obj:
        superviosr_cluster = UserClusterMap.objects.get(season_id=season_id, user_id=superviosr).cluster_id
        farmer_ids_obj = list(UserFarmerMap.objects.filter(officer_id=superviosr, farmer__season_id=season_id).values_list('farmer__farmer_id',flat=True))
        for farmer in farmer_ids_obj:
            farmer_cluster = FarmerClusterSeasonMap.objects.get(farmer_id=farmer, season_id=season_id).cluster_id
            if superviosr_cluster != farmer_cluster:
                return False
    return True
    
# 8. To check both agent and superviosr same cluster
def check_both_agent_and_superviosr_same_cluster():
    print('To check both agent and superviosr same cluster')
    superviosr_ids_obj = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id', flat=True))
    temp_dict={}

    for superviosr in superviosr_ids_obj:
        superviosr_cluster = UserClusterMap.objects.get(season_id=season_id, user_id=superviosr).cluster_id
        agent_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id, supervisor_id=superviosr).values_list('agent_id', flat=True))
        for agent_id in agent_ids:
            agent_cluster = UserClusterMap.objects.get(season_id=season_id, user_id=agent_id).cluster_id
            if superviosr_cluster != agent_cluster:
                return False
    return True
 

# 9. To check_seasonal_farmer_code
def check_seasonal_farmer_code():
    print('to check_seasonal_farmer_code')
    farmer_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id)
    codes=[]
    master_dict={}
    for code in FarmerClusterSeasonMap.objects.filter(season_id=season_id):
        farmer_code = code.seasonal_farmer_code

        farmer_cluster_letter = FarmerClusterSeasonMap.objects.get(season_id=season_id, seasonal_farmer_code=farmer_code).cluster.name[:1]

        cluster_id = FarmerClusterSeasonMap.objects.get(season_id=season_id, seasonal_farmer_code=farmer_code).cluster.id
        farmer_supervisor_letter = UserClusterMap.objects.get(season=3, cluster_id=cluster_id, user__userprofile__user_type_id=5).user.username[:1]
        agent_id = AgentFarmerMap.objects.get(farmer__seasonal_farmer_code=farmer_code).agent_id

        farmer_unicode_letter = UserClusterMap.objects.get(season_id=season_id, user_id=agent_id).unique_code
        gen_farmer_code_letters = farmer_cluster_letter.upper() + farmer_supervisor_letter.upper() + farmer_unicode_letter.upper()

        split_from_farme_code = farmer_code[2:5]

        if not gen_farmer_code_letters==split_from_farme_code:
            return False
    return True

# 11. check aadhaar id profile matching
def aadhaar_id_userprofile_count():
    aadhaar_ids = list(UserProfile.objects.exclude(aadhaar_number__isnull=True).exclude(aadhaar_number='11111111111').exclude(aadhaar_number='111111111111').values_list('aadhaar_number', flat=True))
    aadhaar_dict={}
    for item in aadhaar_ids:
        aadhaar_dict[item] = []
        user_profile_obj = UserProfile.objects.filter(aadhaar_number=item)
        for id in user_profile_obj:
            aadhaar_dict[item].append(id.user.first_name)
    for agent_id in aadhaar_dict.keys():
        if len(aadhaar_dict[agent_id]) >= 2:
            return False
    return True

            
# 12. To check one agent in multiple cluster
def check_one_agent_in_multiple_cluster():
    print('To check one agent in multiple cluster')
    agent_ids = list(set(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=6).values_list('user_id', flat=True)))
    temp={}
    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    for agent_id in agent_ids:
        agent_count = UserClusterMap.objects.filter(season_id=season_id, user_id=agent_id, cluster_id__in=cluster_ids).count()
        if agent_count >= 2:
            return False
    return True


# 13. To check farmer id in UserFarmerMap
def check_farmer_id_in_user_farmer_map():
    print('To check farmer id in UserFarmerMap')
    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list('farmer_id', flat=True))
    for farmer_id in farmer_ids:
        if not UserFarmerMap.objects.filter(farmer__season_id=season_id, farmer__farmer_id=farmer_id).exists():
            return False
    return True            
            
# 14. To check farmer id in AgentFarmerMap
def check_farmer_id_in_agent_farmer_map():
    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list('farmer_id', flat=True))
    farmer_ids
    for farmer_id in farmer_ids:
        if not AgentFarmerMap.objects.filter(farmer__season_id=season_id, farmer__farmer_id=farmer_id).exists():
            return False
    return True

def run(*args):
    check_test_cases()

