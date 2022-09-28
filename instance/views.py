from sys import float_info, float_repr_style
# from turtle import position
from django.db.models.query import prefetch_related_objects
from django.shortcuts import render
from django.http import HttpResponse
# from reportlab.platypus.paragraph import S
from rest_framework.response import Response
from instance.models import *
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, logout, login
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from collections import defaultdict, OrderedDict, Counter
from base64 import b64encode, b64decode
from django.core.files.base import ContentFile
import datetime
import pandas as pd
import numpy as np
from inputdistri.models import *
from fcm_django.models import FCMDevice
from decimal import *   
# import plivo
from django.db.models import Sum
import random
import calendar

from instance.serializer import *
from django.db import transaction
import math
import os
# import tkinter

from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import operator
import re




color_list = ['#ED1056', '#EFEBD7', '#4FEF54', '#BFE9CF', '#AD9F04', '#7573D6', '#28A25F', '#0CD6E6', '#EACB9C', '#8029F3', '#B1D512', '#1B3B43', '#78AB64',
    '#0429C6', '#3AAC02', '#789B63', '#2F067F', '#3136C8', '#B1226A', '#0AB434', '#0CD820', '#C7604D', '#498F30', '#58A8F2', '#D123C7', '#40BDBD', '#8F40C1',
    '#CDFD43', '#BA2BC5', '#A61576', '#623A87', '#61FA8E', '#371664', '#A73933', '#26F94F', '#A1BBDA', '#3004F7', '#D1EBB7', '#C2A695', '#29B136', '#41E2F3', 
    '#2285A7', '#E95C2E', '#3ACE39', '#D51F30', '#365954', '#03112D', '#A6C0C2', '#9FE05A', '#2B27E7', '#32FB78', '#F865D4', '#1FC160', '#AE3477', '#5AD9D9',
    '#EBEBBF', '#AB6CD9', '#2CFE47', '#B49E61', '#241320', '#98358A', '#52171A', '#A0A1F9', '#0BFE32', '#445E37', '#DD52C7', '#FAA5D6', '#4A5C4A', '#DBFF90',
    '#D9E598', '#32880B', '#82DB54', '#8AA299', '#814342', '#691CD5', '#107ED7', '#B5ABEA', '#D73293', '#737986', '#C0B2F0', '#C27A35', '#3FE7C3', '#6A2EBC', 
    '#F23167', '#E1C80B', '#2D39C7', '#8904DF', '#D16B5D', '#BFC876', '#05FEE7', '#D40E35', '#BFE029', '#B3D8EC', '#E29955', '#4BAEAD', '#29B7DD', '#3936D3', 
    '#A1A39B', '#C52D98', '#5CA7C1'  ]

# Create your views here  decode of image from base64

auth_id = "MAZJZINTYZZTQ4MTG0MT"
auth_token = "NWJkN2Q5MGM2OGI2Njc1MGM3NzMzMmMyZjQyYWIw"


def decode_image(encoded_image, file_name=None):
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split("base64,")
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + ".jpeg")

def decode_image_pdf(encoded_image, file_name=None):
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split("base64,")
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + ".pdf")

def decode_excel_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.xlsx')


# encode of image to base64


def encode_image(image_path):
    image_path = "{}{}".format("static/media/", image_path)
    with open(image_path, "rb") as image_file:
        encoded_image = b64encode(image_file.read())
        image = "data:image/jpeg;base64," + encoded_image.decode("utf-8")
        return image


def encode_image_with_out_static(image_path):
    image_path = str(image_path)
    with open(image_path, "rb") as image_file:
        encoded_image = b64encode(image_file.read())
        image = "data:image/pdf;base64," + encoded_image.decode("utf-8")
        return image


# check user and serve token
@api_view(["POST"])
@permission_classes((AllowAny,))
def login_for_token(request):
    print("LOGIN FUNCTION")
    if User.objects.filter(username=request.data["user_name"],is_active=True).exists():
        user = authenticate(
            username=request.data["user_name"], password=request.data["password"]
        )
        print("---------user-----------")
        # print('user id = ', user.id)
        print("user = ", user)
        print("-------------------------")
        if user is not None:
            user_profile_obj = UserProfile.objects.get(user=user)
            if Token.objects.filter(user_id=user.id).exists():
                print("user already logged")
                Token.objects.filter(user_id=user.id).delete()
                print("previous token deleted")
            token = Token.objects.create(user=user)
            print("token created for user")
            user_dict = defaultdict(dict)
            user_dict['user_id'] = user.id
            user_dict["token"] = str(token)
            user_dict["user_type_id"] = user_profile_obj.user_type.id
            user_dict["user_type"] = user_profile_obj.user_type.name
            if PositionManUserMap.objects.filter(position_user_map_id__user_id=user).exists():
                user_dict["first_name"] = PositionManUserMap.objects.get(position_user_map_id__user_id=user).user.first_name
            else:
                user_dict["first_name"] = user_profile_obj.user.first_name
            return Response(user_dict)
        else:
            content = {"detail": "Incorrect User Name/Password!"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print("USER DOES NOT EXISTS")
        content = {"detail": "Incorrect User Name/Password!"}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


# check user and serve token
@api_view(["POST"])
@permission_classes((AllowAny,))
def login_for_token_for_mobile(request):
    print("LOGIN FUNCTION")
    if User.objects.filter(username=request.data["user_name"]).exists():
        user = authenticate(
            username=request.data["user_name"], password=request.data["password"]
        )
        print("---------user-----------")
        # print('user id = ', user.id)
        print("user = ", user)
        print("-------------------------")
        if user is not None:
            user_profile_obj = UserProfile.objects.get(user=user)
            if Token.objects.filter(user_id=user.id).exists():
                print("user already logged")
                Token.objects.filter(user_id=user.id).delete()
                print("previous token deleted")
            token = Token.objects.create(user=user)
            User.objects.filter(id=user.id).update(last_login=datetime.datetime.now())
            print("token created for user")
            user_dict = defaultdict(dict)
            user_dict["user_id"] = user.id
            user_dict["token"] = str(token)
            user_dict["user_type_id"] = user_profile_obj.user_type.id
            user_dict["user_type"] = user_profile_obj.user_type.name
            if PositionManUserMap.objects.filter(
                    position_user_map_id__user_id=user
            ).exists():
                user_dict["first_name"] = PositionManUserMap.objects.get(
                    position_user_map_id__user_id=user
                ).user.first_name
            else:
                user_dict["first_name"] = user_profile_obj.user.first_name
            return Response(user_dict)
        else:
            content = {"detail": "Incorrect User Name/Password!"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print("USER DOES NOT EXISTS")
        content = {"detail": "Incorrect User Name/Password!"}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


# state based district
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_state_based_district(request):
    state_list = {}
    for state in State.objects.all().order_by('name'):
        state_list[state.id] = []
        for dist in District.objects.filter(state=state.id):
            district_dict = {"name": dist.name, "id": dist.id}
            state_list[state.id].append(district_dict)
    return Response(data=state_list, status=status.HTTP_200_OK)


# district based taluk
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_district_based_taluk(request):
    district_dict = {}
    for district in District.objects.all().order_by('name'):
        district_dict[district.id] = []
        for taluk in Taluk.objects.filter(district=district.id):
            taluk_dict = {"name": taluk.name, "id": taluk.id}
            district_dict[district.id].append(taluk_dict)
    return Response(data=district_dict, status=status.HTTP_200_OK)


# taluk based hobli
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_taluk_based_hobli(request):
    taluk_dict = {}
    for hobli in Hobli.objects.all().order_by('name'):
        hobli_dict = {"name": hobli.name, "id": hobli.id}
        if not hobli.taluk.id in taluk_dict.keys():
            taluk_dict[hobli.taluk.id] = []
        taluk_dict[hobli.taluk.id].append(hobli_dict)
    return Response(data=taluk_dict, status=status.HTTP_200_OK)


# hobli based village
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_hobli_based_village(request):
    hobli_dict = {}
    for hobli in Hobli.objects.all():
        hobli_dict[hobli.id] = []
        village_objs = Village.objects.filter(hobli_id=hobli.id).order_by('name')
        for village in village_objs:
            village_dict = {"name": village.name, "id": village.id}
            hobli_dict[hobli.id].append(village_dict)
    return Response(data=hobli_dict, status=status.HTTP_200_OK)


# gender
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_gender(request):
    gender_list = []
    for gender in Gender.objects.all().order_by('name'):
        gender_dict = {"id": gender.id, "name": gender.name}
        gender_list.append(gender_dict)
    return Response(data=gender_list, status=status.HTTP_200_OK)


# state
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_state(request):
    state_list = []
    for state in State.objects.all():
        state_dict = {"name": state.name, "id": state.id}
        state_list.append(state_dict)
    return Response(data=state_list, status=status.HTTP_200_OK)


# state
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_caste(request):
    caste_list = []
    for caste in Caste.objects.all():
        state_dict = {"name": caste.name, "id": caste.id}
        caste_list.append(state_dict)
    return Response(data=caste_list, status=status.HTTP_200_OK)


# state
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_farm_size_classification(request):
    classification_list = []
    for classification in FarmHoldingSizeClassificationCv.objects.all():
        state_dict = {"name": classification.name, "id": classification.id}
        classification_list.append(state_dict)
    return Response(data=classification_list, status=status.HTTP_200_OK)


# state
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_language(request):
    lang_list = []
    for lang in Language.objects.all():
        lang_dict = {"name": lang.name, "id": lang.id}
        lang_list.append(lang_dict)
    return Response(data=lang_list, status=status.HTTP_200_OK)


# district based cluster
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_cluster(request):
    cluster_list = list(Cluster.objects.filter().values('id', 'name'))
    return Response(data=cluster_list, status=status.HTTP_200_OK)


# educationcv
@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_educational_qualification(request):
    eductaional_list = []
    for education in EducationalQualificationCv.objects.all():
        education_dic = {"name": education.name, "id": education.id}
        eductaional_list.append(education_dic)
    return Response(data=eductaional_list, status=status.HTTP_200_OK)


def generate_agent_code(user_type_id, season_id, cluster_id):
    print(UserProfileCodeBank.objects.get(season_id=season_id,user_type_id=user_type_id).last_count)
    print(UserProfileCodeBank.objects.get(season_id=season_id,user_type_id=user_type_id).prefix_code)
    print(Cluster.objects.get(id=cluster_id).name[:1])
    prefix = UserProfileCodeBank.objects.get(season_id=season_id,user_type_id=user_type_id).prefix_code
    if user_type_id == 6:
        prefix = prefix + str(Cluster.objects.get(id=cluster_id).name[:1])
    print('prefix: ', prefix)
    last_count =UserProfileCodeBank.objects.get(season_id=season_id,user_type_id=user_type_id).last_count
    generated_count = last_count + 1
    suffix = str(generated_count).zfill(3)
    code = str(prefix) + suffix
    UserProfileCodeBank.objects.filter(season_id=season_id,user_type_id=user_type_id).update(last_count=generated_count)
    print(code)
    return code

# agent save
@api_view(["POST"])
@permission_classes((AllowAny,))
def save_agent(request):
    season_id = get_active_season_id()
    data = {}
    # new user
    if request.data["agent_id"] == None:
        if User.objects.filter(username=request.data["mobile"]).exists():
            data["message"] = "This Agent already Register"
            print(data)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            # create user
            user_obj = User(
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                username=request.data["mobile"],
                password=make_password(1234),
            )
            if request.data["email"] != None:
                user_obj.email = request.data["email"]
            user_obj.save()
            print("user created success")
            # create user profile
            season_id = get_active_season_id()
            user_profile = UserProfile(
                business_id=1,
                user=user_obj,
                code=generate_agent_code(6,season_id, request.data["cluster_id"][0]),
                user_type_id=6,
                gender_id=request.data["gender_id"],
                blood_group_id=request.data["blood_group_id"],
                dob=request.data["dob"],
                mobile=request.data["mobile"],
                alternate_mobile=request.data["alternate_mobile"],
                emergency_number=request.data["emergency_number"],
                agreement_number=request.data["agreement_number"],
                driving_licence_number=request.data["licence_number"],
                state_id=request.data["state_id"],
                district_id=request.data["district_id"],
                taluk_id=request.data["taluk_id"],
                address=request.data["address"],
                pincode=request.data["pincode"],
                hobli_id=request.data["hobli_id"],
                village_id=request.data["village_id"],
                educational_qualification_id=request.data["educational_qualification"],
                institution_name=request.data["institution_name"],
                university_name=request.data["university_name"],
                aadhaar_number=request.data["aadhaar_number"],
                pan_number=request.data["pan_number"],
                prior_experience_in_other_company=request.data["have_prior_experience"],
                prior_experience_company_name=request.data["prior_experience_company_name"],
                prior_experience_duration=request.data["prior_experience_duration"],
                date_of_joining=request.data["collaborated_date"],
                created_by=request.user,
                modified_by=request.user,
            )
            if "image" in request.data:
                user_profile.aadhaar_document = decode_image(request.data["image"])

            if "pan_image" in request.data:
                user_profile.pan_document = decode_image_pdf(request.data["pan_image"])

            if "driving_licence_image" in request.data:
                user_profile.driving_licence_document = decode_image_pdf(request.data["driving_licence_image"])

            if ("agreement_image" in request.data and request.data["agreement_image"] != None):
                user_profile.agreement_document = decode_image_pdf(request.data["agreement_image"])

            user_profile.save()
            print("user profile saved")

            # # assign supervisor
            # if UserHierarchyMap.objects.filter(superior_id=request.data['supervisor_id']).exists():
            #     user_hierarchy_obj = UserHierarchyMap.objects.get(superior_id=request.data['supervisor_id'])
            #     user_hierarchy_obj.subordinate.add(user_obj)
            #     user_hierarchy_obj.save()
            # else:
            #     user_hierarchy_obj = UserHierarchyMap(superior_id=request.data['supervisor_id'],superior_user_type_id=5, subordinate_user_type_id=6)
            #     user_hierarchy_obj.save()
            #     user_hierarchy_obj.subordinate.add(user_obj)
            #     user_hierarchy_obj.save()

            AgentSupervisorSeasonMap.objects.create(
                supervisor_id=request.data['supervisor_id'],
                agent_id=user_obj.id,
                season_id=season_id
            )
            print('saved the supervisor map')
            for cluster_id in request.data["cluster_id"]:

                if cluster_id != None:
                    if not UserClusterMap.objects.filter(cluster_id=cluster_id, user=user_obj, season_id=season_id).exists():
                        user_cluster_obj = UserClusterMap(
                            cluster_id=cluster_id,
                            user=user_obj,
                            season_id=get_active_season_id(),
                            unique_code='',
                            modified_by=request.user,
                        )
                        user_cluster_obj.save()

            if "photo" in request.data:
                photo = decode_image(request.data["photo"])
                UserImage.objects.create(user=user_obj, image=photo, uploaded_by=request.user)

            AgentMergeloadEnable.objects.create(season_id=season_id, agent_id=user_obj.id)

            #agentwallet
            AgentWallet.objects.create(modified_by_id=request.user.id, agent_id=user_obj.id)
            
            data["message"] = "agent saved successfully"
            print("agent save success")
            print(data)
        return Response(data=data, status=status.HTTP_200_OK)

    # old user update
    elif request.data["agent_id"] != None:
        print(request.data)
        user_id = request.data["agent_id"]
        User.objects.filter(id=user_id).update(
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            email=request.data["email"],
        )

        UserProfile.objects.filter(user_id=user_id).update(
            gender_id=request.data["gender_id"],
            dob=request.data["dob"],
            mobile=request.data["mobile"],
            alternate_mobile=request.data["alternate_mobile"],
            state_id=request.data["state_id"],
            district_id=request.data["district_id"],
            taluk_id=request.data["taluk_id"],
            blood_group_id=request.data["blood_group_id"],
            address=request.data["address"],
            hobli_id=request.data["hobli_id"],
            pincode=request.data["pincode"],
            village_id=request.data["village_id"],
            educational_qualification_id=request.data["educational_qualification"],
            institution_name=request.data["institution_name"],
            university_name=request.data["university_name"],
            aadhaar_number=request.data["aadhaar_number"],
            pan_number=request.data["pan_number"],
            prior_experience_in_other_company=request.data["have_prior_experience"],
            prior_experience_company_name=request.data["prior_experience_company_name"],
            prior_experience_duration=request.data["prior_experience_duration"],
            date_of_joining=request.data["collaborated_date"],
            modified_by=request.user,
        )
        if "emergency_number" in request.data:
            UserProfile.objects.filter(user_id=user_id).update(request.data["emergency_number"])
        user_profile = UserProfile.objects.get(user_id=user_id)

        if "image" in request.data:
            user_profile.aadhaar_document = decode_image(request.data["image"])
        else:
            user_profile.aadhaar_document = None

        if "pan_image" in request.data:
            user_profile.pan_document = decode_image_pdf(request.data["pan_image"])
        else:
            user_profile.pan_document = None

        if "driving_licence_image" in request.data:
            user_profile.driving_licence_document = decode_image_pdf(request.data["driving_licence_image"])
        else:
            user_profile.driving_licence_document = None

        if ("agreement_image" in request.data and request.data["agreement_image"] != None):
            user_profile.agreement_document = decode_image_pdf(request.data["agreement_image"])
        else:
            user_profile.agreement_document = None

        user_profile.save()

        UserClusterMap.objects.filter(user_id=user_id, season_id=season_id).exclude(cluster_id__in=request.data["cluster_id"]).delete()

        user_obj = User.objects.get(id=user_id)
        # update supervisor
        AgentSupervisorSeasonMap.objects.filter(agent_id=user_id, season_id=season_id).update(
            supervisor_id=request.data['supervisor_id']
        )

        # if not UserHierarchyMap.objects.filter(superior_id=request.data['supervisor_id'], subordinate=user_obj).exists():
        #     if UserHierarchyMap.objects.filter(subordinate=user_obj).exists():
        #         user_hierarchy_obj = UserHierarchyMap.objects.get(subordinate=user_obj)
        #         user_hierarchy_obj.subordinate.remove(user_obj)
        #         user_hierarchy_obj.save()
        #     # assign supervisor
        #     if UserHierarchyMap.objects.filter(superior_id=request.data['supervisor_id'], ).exists():
        #         user_hierarchy_obj = UserHierarchyMap.objects.get(superior_id=request.data['supervisor_id'])
        #         user_hierarchy_obj.subordinate.add(user_obj)
        #         user_hierarchy_obj.save()
        #     else:
        #         user_hierarchy_obj = UserHierarchyMap(superior_id=request.data['supervisor_id'], superior_user_type_id=5, subordinate_user_type_id=6)
        #         user_hierarchy_obj.save()
        #         user_hierarchy_obj.subordinate.add(user_obj)
        #         user_hierarchy_obj.save()


        for cluster_id in request.data["cluster_id"]:
            if cluster_id == None:
                print("this value is none")
                UserClusterMap.objects.filter(user_id=user_id, season_id=season_id).delete()
            else:
                if not UserClusterMap.objects.filter(
                        cluster_id=cluster_id, user_id=user_id, season_id=season_id
                ).exists():
                    user_cluster_obj = UserClusterMap(
                        cluster_id=cluster_id,
                        user_id=user_id,
                        season_id=season_id,
                        unique_code='',
                        modified_by=request.user,
                    )
                    user_cluster_obj.save()

        if "photo" in request.data:
            photo = decode_image(request.data["photo"])
            if UserImage.objects.filter(user_id=user_id).exists():
                UserImage.objects.filter(user_id=user_id).update(
                    image=photo,
                )
            else:
                UserImage.objects.create(
                    image=photo, user_id=user_id, uploaded_by=request.user
                )
        print("employee image updated success")

        data["message"] = "agent updated success"
        return Response(data=data, status=status.HTTP_200_OK)

# change request season
# serve agent list
@api_view(["GET"])
def serve_agent(request):
    agents_user_id = UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
    user_profile_obj = UserProfile.objects.filter(user_type_id=6).order_by('code')
    agent_list = []
    season_id = get_active_season_id()
    # user
    user = User.objects.filter(id__in=agents_user_id).order_by("id")
    user_values = user.values_list("id", "first_name", "last_name", "first_name", "userhierarchymap__superior_id", 'userhierarchymap__season_id')
    user_columns = ["id", "first_name", "last_name", "name", 'superior_id', 'season_id']
    user_df = pd.DataFrame(list(user_values), columns=user_columns)
    # user_df = user_df[user_df['season_id']==season_id]

    # user hierarchy map
    # agents_user_id = UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
    # user_hier_list = list(UserHierarchyMap.objects.filter(subordinate__id__in=agents_user_id).values_list('superior_id','superior__username','subordinate', 'season_id'))
    # user_hier_col = ['super_id', 'supervisor_username', 'subordinate_id', 'season_id']
    # user_hier_df = pd.DataFrame(user_hier_list, columns=user_hier_col)
    # user_hier_df = user_hier_df[user_hier_df['season_id']==season_id]

    afs_user_ids = UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True)
    agent_afs = AgentSupervisorSeasonMap.objects.filter(season_id=season_id, supervisor_id__in=afs_user_ids).values_list('supervisor_id', 'supervisor__username','agent_id',  'season_id')
    agent_afs_col = ['supervisor_id', 'supervisor_username', 'agent_id',  'season_id']
    agent_afs_df = pd.DataFrame(agent_afs, columns=agent_afs_col)
    agent_afs_df = agent_afs_df[agent_afs_df['season_id']==season_id]

    # user profile
    user_profile_values = user_profile_obj.values_list("user_id", "id", "code", "user_type", "user_type__name", "dob",
                                                       "mobile", "alternate_mobile",
                                                       "user__email", "address", "state_id", "state__name", "hobli_id",
                                                       "hobli__name", "pincode",
                                                       "educational_qualification_id", "institution_name",
                                                       "university_name", "aadhaar_number",
                                                       "pan_number", "prior_experience_in_other_company",
                                                       "prior_experience_company_name", "prior_experience_duration",
                                                       "date_of_joining", "latitude", "longitude", )
    user_profile_columns = ["user_id", "id", "code", "user_type_id", "user_type", "dob", "mobile", "alternate_mobile",
                            "email", "address", "state_id", "state__name",
                            "hobli_id", "hobli_name", "pincode", "educational_qualification_id", "institution_name",
                            "university_name", "aadhaar_number", "pan_number",
                            "prior_experience_in_other_company", "prior_experience_company_name",
                            "prior_experience_duration", "collaborated_with_company_on", "latitude", "longitude"]
    user_profile_df = pd.DataFrame(list(user_profile_values), columns=user_profile_columns)
    user_profile_df = user_profile_df.fillna(0)

    user_hier_merge_user_df = pd.merge(user_df, agent_afs_df, left_on="id", right_on="agent_id", how="left")
    user_profile_merge = pd.merge(user_hier_merge_user_df, user_profile_df, left_on="id", right_on="user_id",how="left")

    user_profile_merge = user_profile_merge.fillna(0)

    print("crossed the line")
    user_bank_details = UserBankDetails.objects.filter(user_id__in=agents_user_id, is_active=True)
    agent_bank_values = user_bank_details.values_list("user_id", "bank", "branch", "ifsc_code", "micr_code",
                                                      "account_holder_name", "account_number", "post_cheque_number")

    agent_bank_columns = ["user_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name",
                          "account_number", "post_cheque_number"]
    agent_bank_df = pd.DataFrame(list(agent_bank_values), columns=agent_bank_columns)

    final_df = pd.merge(user_profile_merge, agent_bank_df, left_on="user_id", right_on="user_id", how="left", )
    final_df = final_df.fillna(0)

    user_cluster_map_values = UserClusterMap.objects.filter(season_id=season_id).values_list("id", "user_id", "cluster__name")
    user_cluster_map_columns = ["id", "user", "clusters"]
    user_cluster_map_df = pd.DataFrame(list(user_cluster_map_values), columns=user_cluster_map_columns)

    user_cluster_map_df = (user_cluster_map_df.groupby("user")["clusters"].apply(list).to_frame())
    cluster_merged_df = pd.merge(final_df, user_cluster_map_df, left_on="user_id", right_on="user", how="left")
    cluster_merged_df = cluster_merged_df.fillna(0)

    for index, row in cluster_merged_df.iterrows():
        if row["clusters"] != 0:
            cluster = ""
            cluster = str("(") + str(len(row["clusters"])) + ")" + " "
            for cluster_name in row["clusters"]:
                cluster = cluster + str(cluster_name) + "," + " "
            cluster_merged_df.at[index, "clusters"] = cluster[0:-2]
        # else:
        #     cluster_merged_df.at[index, 'clusters'] =  str('')

        if UserClusterMap.objects.filter(season_id=season_id, user_id=row["user_id"]).exists():
            cluster_merged_df.at[index, "seed_distributed_active_status"] = True
        else:
            cluster_merged_df.at[index, "seed_distributed_active_status"] = False

        # if InputItemInputBatchAgentInventory.objects.filter(agent_id=row["user_id"]).exists():
        #     cluster_merged_df.at[index, "total_bought_seeds"] = InputItemInputBatchAgentInventory.objects.filter(
        #         agent_id=row["user_id"]).count()
        # else:
        cluster_merged_df.at[index, "total_bought_seeds"] = 0

        if AgentFarmerMap.objects.filter(agent_id=row["user_id"], farmer__season_id=season_id).exists():
            cluster_merged_df.at[index, "total_farmer_count"] = AgentFarmerMap.objects.filter(agent_id=row["user_id"],
                                                                                              farmer__season_id=season_id).count()
        else:
            cluster_merged_df.at[index, "total_farmer_count"] = 0
    data = {}
    cluster_merged_df = cluster_merged_df[cluster_merged_df['season_id_y']==season_id]
    cluster_merged_df = cluster_merged_df.sort_values(by=['code'])
    data['data'] = cluster_merged_df.to_dict("r")
    excel_temp_df = cluster_merged_df
    excel_temp_df = excel_temp_df.drop(columns=['superior_id', 'agent_id', 'id_y', 'id_x', 'user_type_id', 'user_type', 'email', 'state_id', 'hobli_id', 'educational_qualification_id',
                                            'institution_name', 'university_name', 'prior_experience_in_other_company', 'prior_experience_company_name', 'prior_experience_duration', 'collaborated_with_company_on',
                                                'latitude', 'longitude', 'seed_distributed_active_status', 'total_bought_seeds','alternate_mobile', 'dob','user_id'
                                            ])
    # excel_temp_df.to_excel('agent_list.xlsx')
    writer = pd.ExcelWriter(str("static/media/") + "agents_list.xlsx", engine="xlsxwriter")
    final_df = excel_temp_df    
    # creating excel sheet with name
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:V1", "Agent List with Bank details " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "agents_list.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)

    return Response(data=data, status=status.HTTP_200_OK)

# change request season

# serve employees list  for only super visor and senior super visor
@api_view(["GET"])
def serve_super_visor(request):
    # user_id_list = [3, 5]
    user_id_list = [1, 2, 3, 5, 4, 16]
    supervisor_user_id = UserProfile.objects.filter(user_type_id__in=user_id_list).values_list("user_id", flat=True)
    supervisor_list = []
    # user
    poisition_user_id = list(PositionPositionUserMap.objects.all().values_list('user_id', flat=True))
    user = User.objects.filter(id__in=supervisor_user_id).exclude(id__in=poisition_user_id).order_by("id")
    user_values = user.values_list("id", "first_name", "last_name")
    user_columns = ["id", "first_name", "last_name"]
    user_df = pd.DataFrame(list(user_values), columns=user_columns)
    # user profile
    user_profile_obj = UserProfile.objects.filter(user_type_id__in=user_id_list)
    user_profile_values = user_profile_obj.values_list("user_id","id","code","user_type","user_type__name","dob","mobile","alternate_mobile","user__email","address","state_id","state__name","hobli_id","hobli__name","pincode","educational_qualification_id","institution_name","university_name","aadhaar_number","pan_number","prior_experience_in_other_company","prior_experience_company_name","prior_experience_duration","date_of_joining","latitude","longitude",'user__is_active')
    user_profile_columns = ["user_id","id","code","user_type_id","user_type","dob","mobile","alternate_mobile","email","address","state_id","state__name","hobli_id","hobli_name","pincode","educational_qualification_id","institution_name","university_name","aadhaar_number","pan_number","prior_experience_in_other_company","prior_experience_company_name","prior_experience_duration","collaborated_with_company_on","latitude","longitude",'is_active']
    user_profile_df = pd.DataFrame(list(user_profile_values), columns=user_profile_columns)
    season_id = get_active_season_id()
    user_profile_merge = pd.merge(user_df, user_profile_df, left_on="id", right_on="user_id", how="left")
    user_cluster_map_values = UserClusterMap.objects.filter(season_id=season_id).values_list("id", "user_id", "cluster__name")
    user_cluster_map_columns = ["id", "user", "clusters"]
    user_cluster_map_df = pd.DataFrame(list(user_cluster_map_values), columns=user_cluster_map_columns)

    user_cluster_map_df = (user_cluster_map_df.groupby("user")["clusters"].apply(list).to_frame())
    cluster_merged_df = pd.merge(user_profile_merge,user_cluster_map_df,left_on="user_id",right_on="user",how="left")
    cluster_merged_df = cluster_merged_df.fillna(0)

    for index, row in cluster_merged_df.iterrows():
        # print(row["user_id"])
        if PositionManUserMap.objects.filter(user_id=row["user_id"]).exists():
            cluster_merged_df.at[index, "position_role"] = PositionManUserMap.objects.get(user_id=row["user_id"]).position_user_map.position.name
            cluster_merged_df.at[index, "position_username"] = PositionManUserMap.objects.get(user_id=row["user_id"]).position_user_map.user.username
            cluster_merged_df.at[index, "farmer_count"] = UserFarmerMap.objects.filter(officer=PositionManUserMap.objects.get(user_id=row["user_id"]).position_user_map.user).count()

        if row["clusters"] != 0:
            cluster = ""
            cluster = str("(") + str(len(row["clusters"])) + ")" + " "
            for cluster_name in row["clusters"]:
                cluster = cluster + str(cluster_name) + "," + " "
            cluster_merged_df.at[index, "clusters"] = cluster[0:-2]
        # else:
    cluster_merged_df = cluster_merged_df.fillna(0)
    cluster_merged_df = cluster_merged_df.to_dict("r")
    return Response(data=cluster_merged_df, status=status.HTTP_200_OK)


# save supervisor
@api_view(["POST"])
@permission_classes((AllowAny,))
def save_super_visor(request):
    data = {}
    # new user
    if request.data["super_visor_id"] == None:
        if User.objects.filter(username=request.data["mobile"]).exists():
            data["message"] = "This Supervisor already Register"
            print(data)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:

            # create user
            user_obj = User(
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                username=request.data["mobile"],
                password=make_password(1234),
            )
            if request.data["email"] != None:
                user_obj.email = request.data["email"]
            user_obj.save()
            print("user created success")

            # create user profile
            user_profile = UserProfile(
                business_id=1,
                user=user_obj,
                code=user_obj.id,
                user_type_id=request.data["user_type_id"],
                gender_id=request.data["gender_id"],
                blood_group_id=request.data["blood_group_id"],
                dob=request.data["dob"],
                mobile=request.data["mobile"],
                address=request.data["address"],
                alternate_mobile=request.data["alternate_mobile"],
                state_id=request.data["state_id"],
                district_id=request.data["district_id"],
                taluk_id=request.data["taluk_id"],
                pincode=request.data["pincode"],
                hobli_id=request.data["hobli_id"],
                village_id=request.data["village_id"],
                educational_qualification_id=request.data["educational_qualification"],
                institution_name=request.data["institution_name"],
                university_name=request.data["university_name"],
                driving_licence_number=request.data["licence_number"],
                agreement_number=request.data["agreement_number"],
                aadhaar_number=request.data["aadhaar_number"],
                pan_number=request.data["pan_number"],
                prior_experience_in_other_company=request.data["have_prior_experience"],
                prior_experience_company_name=request.data["prior_experience_company_name"],
                prior_experience_duration=request.data["prior_experience_duration"],
                date_of_joining=request.data["collaborated_date"],
                created_by=request.user,
                modified_by=request.user,
            )

            if "image" in request.data:
                user_profile.aadhaar_document = decode_image(request.data["image"])

            if "pan_image" in request.data:
                user_profile.pan_document = decode_image(request.data["pan_image"])

            if "driving_licence_image" in request.data:
                user_profile.driving_licence_document = decode_image(
                    request.data["driving_licence_image"]
                )

            if (
                    "agreement_image" in request.data
                    and request.data["agreement_image"] != None
            ):
                user_profile.agreement_document = decode_image(
                    request.data["agreement_image"]
                )

            user_profile.save()
            print("user profile saved")

            #----------------------------------------------register position positoin user------------------

            # create user
            position_user_obj = User(
                first_name=request.data["first_name"] + user_profile.user_type.short_name,
                last_name=request.data["last_name"],
                username=request.data["first_name"] + user_profile.user_type.short_name,
                password=make_password(1234),
            )
            if request.data["email"] != None:
                position_user_obj.email = request.data["email"]
            position_user_obj.save()
            print("user created success")

            # create user profile
            position_user_profile = UserProfile(
                business_id=1,
                user=position_user_obj,
                code=position_user_obj.id,
                user_type_id=request.data["user_type_id"],
                gender_id=request.data["gender_id"],
                blood_group_id=request.data["blood_group_id"],
                dob=request.data["dob"],
                mobile=request.data["mobile"],
                address=request.data["address"],
                alternate_mobile=request.data["alternate_mobile"],
                state_id=request.data["state_id"],
                district_id=request.data["district_id"],
                taluk_id=request.data["taluk_id"],
                pincode=request.data["pincode"],
                hobli_id=request.data["hobli_id"],
                village_id=request.data["village_id"],
                educational_qualification_id=request.data["educational_qualification"],
                institution_name=request.data["institution_name"],
                university_name=request.data["university_name"],
                driving_licence_number=request.data["licence_number"],
                agreement_number=request.data["agreement_number"],
                aadhaar_number=request.data["aadhaar_number"],
                pan_number=request.data["pan_number"],
                prior_experience_in_other_company=request.data["have_prior_experience"],
                prior_experience_company_name=request.data["prior_experience_company_name"],
                prior_experience_duration=request.data["prior_experience_duration"],
                date_of_joining=request.data["collaborated_date"],
                created_by=request.user,
                modified_by=request.user,
            )

            if "image" in request.data:
                position_user_profile.aadhaar_document = decode_image(request.data["image"])

            if "pan_image" in request.data:
                position_user_profile.pan_document = decode_image(request.data["pan_image"])

            if "driving_licence_image" in request.data:
                position_user_profile.driving_licence_document = decode_image(
                    request.data["driving_licence_image"]
                )

            if (
                    "agreement_image" in request.data
                    and request.data["agreement_image"] != None
            ):
                position_user_profile.agreement_document = decode_image(
                    request.data["agreement_image"]
                )

            position_user_profile.save()
            print("user profile saved")

            #-----------------------------------------------------------------------------------------------

            if PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=position_user_profile.user_type_id).exists():
                last_position_name = PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=position_user_profile.user_type_id).order_by('-id').values_list('position__name', flat=True)[0]
                split_numbers_and_strings = re.match(r"([a-z]+)([0-9]+)", last_position_name, re.I)
                if split_numbers_and_strings:
                    items = list(split_numbers_and_strings.groups())
                    if items[-1][0] == '0':
                        current_position_name = items[0] + '0' + str(int(items[-1])+1)
                    else:
                        current_position_name = items[0] + str(int(items[-1])+1)
                else:
                    current_position_name = last_position_name + '02'
                print(current_position_name)
                position_obj = Position(name=current_position_name, notes=position_user_profile.user_type.name, is_active=True)
                position_obj.save()
                position_position_obj = PositionPositionUserMap.objects.create(position_id=position_obj.id, user_id=position_user_obj.id, is_active=True)
                PositionManUserMap.objects.create(position_user_map=position_position_obj, user_id=user_obj.id, from_date=datetime.datetime.now())
            else:
                position_obj = Position(name=position_user_profile.user_type.short_name+ '01', notes=position_user_profile.user_type.name, is_active=True)
                position_obj.save()
                position_position_obj = PositionPositionUserMap.objects.create(position_id=position_obj.id, user_id=position_user_obj.id, is_active=True)
                PositionManUserMap.objects.create(position_user_map=position_position_obj, user_id=user_obj.id, from_date=datetime.datetime.now())
            print('User Position Created')
                        # map the user with cluster
            # for cluster_id in request.data["cluster_id"]:
            #     if not UserClusterMap.objects.filter(
            #             cluster_id=cluster_id, user=user_obj, season_id=get_active_season_id()
            #     ).exists():
            #         user_cluster_obj = UserClusterMap(
            #             cluster_id=cluster_id,
            #             user=user_obj,
            #             season_id=get_active_season_id(),
            #             modified_by=request.user,
            #         )
            #         user_cluster_obj.save()

            if "photo" in request.data:
                photo = decode_image(request.data["photo"])
                UserImage.objects.create(
                    user=user_obj, image=photo, uploaded_by=request.user
                )
                print("employee image saved success")

            data["message"] = "supervisor saved successfully"
            print("supervisor save success")
            print(data)
            return Response(data=data, status=status.HTTP_200_OK)

    # update existsing
    elif request.data["super_visor_id"] != None:
        user_id = request.data["super_visor_id"]
        User.objects.filter(id=user_id).update(
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            email=request.data["email"],
        )

        UserProfile.objects.filter(user_id=user_id).update(
            gender_id=request.data["gender_id"],
            dob=request.data["dob"],
            mobile=request.data["mobile"],
            alternate_mobile=request.data["alternate_mobile"],
            state_id=request.data["state_id"],
            district_id=request.data["district_id"],
            user_type_id=request.data["user_type_id"],
            taluk_id=request.data["taluk_id"],
            address=request.data["address"],
            blood_group_id=request.data["blood_group_id"],
            hobli_id=request.data["hobli_id"],
            pincode=request.data["pincode"],
            village_id=request.data["village_id"],
            educational_qualification_id=request.data["educational_qualification"],
            institution_name=request.data["institution_name"],
            university_name=request.data["university_name"],
            aadhaar_number=request.data["aadhaar_number"],
            pan_number=request.data["pan_number"],
            driving_licence_number=request.data["licence_number"],
            agreement_number=request.data["agreement_number"],
            prior_experience_in_other_company=request.data["have_prior_experience"],
            prior_experience_company_name=request.data["prior_experience_company_name"],
            prior_experience_duration=request.data["prior_experience_duration"],
            date_of_joining=request.data["collaborated_date"],
            modified_by=request.user,
        )

        user_profile = UserProfile.objects.get(user_id=user_id)

        if "image" in request.data:
            user_profile.aadhaar_document = decode_image(request.data["image"])
        else:
            user_profile.aadhaar_document = None

        if "pan_image" in request.data:
            user_profile.pan_document = decode_image(request.data["pan_image"])
        else:
            user_profile.pan_document = None

        if "driving_licence_image" in request.data:
            user_profile.driving_licence_document = decode_image(request.data["driving_licence_image"])
        else:
            user_profile.driving_licence_document = None

        if ("agreement_image" in request.data and request.data["agreement_image"] != None):
            user_profile.agreement_document = decode_image(request.data["agreement_image"])
        else:
            user_profile.agreement_document = None

        user_profile.save()

        if "photo" in request.data:
            photo = decode_image(request.data["photo"])
            if UserImage.objects.filter(user_id=user_id).exists():
                UserImage.objects.filter(user_id=user_id).update(image=photo,)
            else:
                UserImage.objects.create(image=photo, user_id=user_id, uploaded_by=request.user)
            print("employee image updated success")

        for cluster_id in request.data["cluster_id"]:
            if not UserClusterMap.objects.filter(cluster_id=cluster_id, user_id=user_id, season_id=request.data["season_id"]).exists():
                user_cluster_obj = UserClusterMap(
                    cluster_id=cluster_id,
                    user_id=user_id,
                    season_id=request.data["season_id"],
                    modified_by=request.user,
                )
                user_cluster_obj.save()

        # UserBankDetails.objects.filter(user_id=user_id).update(
        #     bank=request.data['bank_name'],
        #     branch=request.data['branch_name'],
        #     ifsc_code=request.data['ifsc_code'],
        #     micr_code=request.data['micr_code'],
        #     account_holder_name=request.data['account_holder_name'],
        #     account_number=request.data['account_number'],
        #     post_cheque_number=request.data['cheque_number'],
        #     modified_by=request.user
        # )

        # agent_bank_details = UserBankDetails.objects.get(user_id=user_id)
        # if 'cheque_image' in request.data:
        #     agent_bank_details.post_cheque_image = decode_image(
        #         request.data['cheque_image'])

        # if 'passbook_document' in request.data:
        #     agent_bank_details.bank_passbook_document = decode_image(
        #         request.data['passbook_document'])

        # agent_bank_details.save()
        data["message"] = "agent updated success"
        return Response(data=data, status=status.HTTP_200_OK)


#sesonal_farmer_code
def generate_farmer_code(cluster_id, agent_id, officer_id, season_id):
    season = Season.objects.get(id=season_id).year
    season_name = str(season.strftime("%y"))
    cluster_name = Cluster.objects.get(id=cluster_id).name.upper()
    region_name = Cluster.objects.get(id=cluster_id).notes.upper()
    agent_name = UserClusterMap.objects.get(user_id=agent_id, season_id=season_id).unique_code.upper()
    officer_name = User.objects.get(id=officer_id).username[0:1].upper()
    # print(cluster_name)
    # print(agent_name)
    # print(officer_name)
    # print(region_name)
    prefix = season_name + region_name[0] + cluster_name[0] + agent_name[0]
    print(prefix)
    if IdBank.objects.filter(purpose="farmer", prefix_code=prefix).exists():
        last_code = IdBank.objects.get(purpose="farmer", prefix_code=prefix).last_count
        IdBank.objects.filter(purpose="farmer", prefix_code=prefix).update(last_count=last_code + 1)
    else:
        print('new')
        last_code = 0
        id_bank_obj = IdBank(purpose="farmer", prefix_code=prefix, last_count=1, business_id=1)
        id_bank_obj.save()
    generated_code_number = last_code + 1
    suffix = str(generated_code_number).zfill(3)
    code = str(prefix) + suffix
    return code

#common_farmer_code
def farmer_code_generation(last_count, prefix):
    char = prefix
    last_num = last_count
    if not last_count == 9999:
        code = 'F'+str(char)+str(last_num).zfill(4)
    else:
        last_num = 0
        char = chr(ord(char)+1)
#         print('char incremted')
        code = 'F'+str(char)+str(last_num).zfill(4)
    last_num = last_num+1
    FarmerCodeBank.objects.filter(id=1).update(
        last_count=last_num,
        prefix_code=char
    )
    return code


# save farmer with bank details
@api_view(["POST"])
@permission_classes((AllowAny,))
def save_farmer(request):
    data = {}
    print(request.data)
    season_id=get_active_season_id()
    if request.data["farmer_id"] == None:
        if Farmer.objects.filter(mobile=request.data["mobile"]).exists():
            data["message"] = "This Farmer already Register"
            print(data)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            # create user profile
            # farmer

            if request.data["from"] == "mobile":
                officer_id = request.user.id
            else:
                officer_id = request.data["officer_id"]
            season_id = get_active_season_id()
            code_bank_obj = FarmerCodeBank.objects.get(id=1)
            last_count = code_bank_obj.last_count
            prefix = code_bank_obj.prefix_code
            common_code = farmer_code_generation(last_count, prefix)
            code = generate_farmer_code(request.data["cluster_id"], request.data["agent_id"], officer_id, season_id,)
            farmer_obj = Farmer(
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                code=code,
                common_code=common_code,
                gender_id=request.data["gender_id"],
                business_id=1,
                pincode=request.data["pincode"],
                state_id=request.data["state_id"],
                district_id=request.data["district_id"],
                taluk_id=request.data["taluk_id"],
                hobli_id=request.data["hobli_id"],
                village_id=request.data["village_id"],
                address=request.data["address"],
                email=request.data["email"],
                mobile=request.data["mobile"],
                alternate_mobile=request.data["alternate_mobile"],
                communication_language_id=request.data["communication_language_id"],
                caste_id=request.data["caste_id"],
                farm_holding_size_classification_id=request.data["farm_classification_id"],
                farm_holding_size_in_acre=request.data["farm_area"],
                cultivated_for_ccgb_since=request.data["collaborated_date"],
                cluster_id=request.data["cluster_id"],
                is_verified=True,
                verified_by=request.user,
                verified_on=datetime.datetime.today(),
                farmer_data_source_id=2,
                created_by=request.user,
                modified_by=request.user,
                is_demo_farmer = request.data["is_demo_farmer"]
            )
            if 'aadhaar_number' in request.data:
                farmer_obj.aadhaar_number = request.data['aadhaar_number']
            if 'agreement_date' in request.data:
                farmer_obj.agreement_date = request.data['agreement_date']
            if 'land_rtc_number' in request.data:
                farmer_obj.land_rtc_number = request.data['land_rtc_number']
            if 'agreement_number' in request.data:
                farmer_obj.agreement_number = request.data['agreement_number']

            if request.data["crop_under_cultivation_id"] is not None:
                farmer_obj.crop_under_cultivation_id = request.data["crop_under_cultivation_id"]
            farmer_obj.save()

            # cluster
            
            farmer_cluster_obj = FarmerClusterSeasonMap(
                farmer=farmer_obj,
                season_id=season_id,
                seasonal_farmer_code=code,
                cluster_id=request.data["cluster_id"],
                modified_by=request.user,
            )
            farmer_cluster_obj.save()

            # agent farmer
            agent_farmer_map_obj = AgentFarmerMap(
                agent_id=request.data["agent_id"],
                farmer=farmer_cluster_obj,
            )
            agent_farmer_map_obj.save()

            if request.data["from"] == "mobile":
                if 'aadhaar_document' in request.data:
                    if request.data["aadhaar_document"] is not None:
                        farmer_obj.aadhaar_document = decode_image(request.data["aadhaar_document"])
                if 'agreement_document' in request.data:
                    if request.data["agreement_document"] is not None:
                        farmer_obj.aadhaar_document = decode_image(request.data["agreement_document"])
                if request.data["latitude"] is not None:
                    farmer_obj.latitude = request.data["latitude"]
                    farmer_obj.longitude = request.data["longitude"]
                farmer_obj.save()
                user_farmer_obj = UserFarmerMap(
                    farmer=farmer_cluster_obj,
                    officer=request.user,
                )
                user_farmer_obj.save()
                print(user_farmer_obj.id)
                print("link created")

            else:
                if "image" in request.data:
                    farmer_obj.aadhaar_document = decode_image(request.data["image"])

                if ("agreement_image" in request.data and request.data["agreement_image"] != None):
                    farmer_obj.agreement_document = decode_image(request.data["agreement_image"])

                print("user profile saved")

                user_farmer_map_obj = UserFarmerMap(farmer=farmer_cluster_obj,officer_id=request.data["officer_id"],)
                user_farmer_map_obj.save()
                print(user_farmer_map_obj.id)
                print("created")

            data["message"] = "farmer saved successfully"
            data["farmer_id"] = farmer_obj.id
            print("farmer save success")
            return Response(data=data, status=status.HTTP_200_OK)
    # update
    else:
        user_id = request.data["farmer_id"]
        Farmer.objects.filter(id=user_id).update(
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            gender_id=request.data["gender_id"],
            business_id=1,
            pincode=request.data["pincode"],
            state_id=request.data["state_id"],
            district_id=request.data["district_id"],
            taluk_id=request.data["taluk_id"],
            hobli_id=request.data["hobli_id"],
            village_id=request.data["village_id"],
            address=request.data["address"],
            email=request.data["email"],
            mobile=request.data["mobile"],
            alternate_mobile=request.data["alternate_mobile"],
            communication_language_id=request.data["communication_language_id"],
            aadhaar_number=request.data["aadhaar_number"],
            caste_id=request.data["caste_id"],
            farm_holding_size_classification_id=request.data["farm_classification_id"],
            farm_holding_size_in_acre=request.data["farm_area"],
            cultivated_for_ccgb_since=request.data["collaborated_date"],
            cluster_id=request.data["cluster_id"],
            modified_by=request.user,
        )
        farmer_obj = Farmer.objects.get(id=user_id)
        if FarmerClusterSeasonMap.objects.filter(farmer=farmer_obj, season_id=season_id).exists():
            FarmerClusterSeasonMap.objects.filter(farmer=farmer_obj, season_id=season_id).update(cluster_id=request.data["cluster_id"], modified_by=request.user)
        else:
            FarmerClusterSeasonMap.objects.create(
                cluster_id=request.data["cluster_id"],
                modified_by=request.user,
                farmer=farmer_obj,
                seasonal_farmer_code=generate_farmer_code(request.data["cluster_id"], request.data["agent_id"], request.data['officer_id'], season_id,),
                season_id=season_id,
            )
        AgentFarmerMap.objects.filter(farmer__farmer_id=user_id).update(agent_id=request.data["agent_id"],)

        if "image" in request.data:
            farmer_obj.aadhaar_document = decode_image(request.data["image"])

        if ("agreement_image" in request.data and request.data["agreement_image"] != None):
            farmer_obj.agreement_document = decode_image(request.data["agreement_image"])

        farmer_obj.save()

        data["message"] = "farmer updated success"
        data["farmer_id"] = user_id
        return Response(data=data, status=status.HTTP_200_OK)


def find_main_crop_area(farmer_id, season_id):
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id).exists():
        area = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id).aggregate(Sum("area"))["area__sum"]
    else:
        area = 0
    return area


def find_nursury_crop_area(farmer_id, season_id):
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id).exists():
        area = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id).aggregate(Sum("area"))["area__sum"]
    else:
        area = 0
    return area


def find_nursury_age_list(farmer_id, season_id):
    age_list = ""
    today = datetime.date.today()
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id).exists():
        sowings = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id)
        for sowing in sowings:
            diff = today - sowing.sowing_date
            age_list = str(diff.days) + ", " + age_list
    else:
        age_list = "-"
    return age_list


def find_main_age_list(farmer_id, season_id):
    age_list = ""
    today = datetime.date.today()
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id).exists():
        sowings = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id)
        for sowing in sowings:
            diff = today - sowing.sowing_date
            age_list = str(diff.days) + ", " + age_list
    else:
        age_list = "-"
    return age_list


def get_gps_status(farmer_id, season_id):
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id).exists():
        sowings = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id)
        data = 1
        for sowing in sowings:
            if not SowingBoundary.objects.filter(sowing_id=sowing.id).exists():
                data = 2
    else:
        data = 3
    return data


def get_harvest_area(farmer_id, season_id):
    area = 0
    if Harvest.objects.filter(sowing__farmer__id=farmer_id, sowing__season__id=season_id).exists():
        unique_harvest = (Harvest.objects.filter(sowing__farmer__id=farmer_id, sowing__season__id=season_id).distinct("ticket_number").values_list("id"))
        if (Harvest.objects.filter(id__in=unique_harvest, sowing__season__id=season_id).aggregate(Sum("sowing__area"))["sowing__area__sum"] != None):
            area = Harvest.objects.filter(id__in=unique_harvest, sowing__season__id=season_id).aggregate(Sum("sowing__area"))["sowing__area__sum"]
    return area


def get_harvest_qty(farmer_id, season_id):
    area = 0
    if Harvest.objects.filter(sowing__farmer__id=farmer_id, sowing__season__id=season_id).exists():
        area = Harvest.objects.filter(sowing__farmer__id=farmer_id, sowing__season__id=season_id).aggregate(Sum("value"))["value__sum"]
        area = area / 1000
    return area


# serve_farmers list
@api_view(["GET"])
def serve_farmers(request):
    print(request.user.id)
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user=user_id).user_type_id
    season_id = get_active_season_id()
    user_id = request.user.id
    farmer_ids = []
    # season_id=request.data['season_id']
    print("superior id:", user_id)
    user_type_id = UserProfile.objects.get(user=user_id).user_type_id
    if user_type_id == 5:
        print()
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('supervisor_id', flat=True))
    elif user_type_id == 3:
        if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
            subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
            subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
            print("one")
            print(subordinate_user_ids)
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('supervisor_id',flat=True))
            print(len(subordinate_user_ids))
    elif user_type_id == 6:
        farmer_ids = list(AgentFarmerMap.objects.filter(farmer__season_id=season_id, agent_id=user_id).values_list("farmer__farmer_id", flat=True))
    else:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('supervisor_id',flat=True))
    if len(farmer_ids) == 0:
        farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
    farmer_objs = Farmer.objects.filter(id__in=farmer_ids)
    farmer_values = farmer_objs.values_list("id", "first_name", "last_name", "mobile", "alternate_mobile", "email", "address", "state_id", "state__name", "hobli_id", "hobli__name", "pincode", "aadhaar_number", "cultivated_for_ccgb_since", "latitude", "longitude", "district_id", "district__name", "taluk_id", "taluk__name", "village_id", "village__name", "latitude", "longitude")
    farmer_columns = [ "farmer_id", "first_name", "last_name", "mobile", "alternate_mobile", "email", "street", "state_id", "state__name", "hobli_id", "hobli_name", "pincode", "aadhaar_number", "collaborated_with_company_on", "latitude", "longitude", "district_id", "district_name", "taluk_id", "taluk_name", "village_id", "village_name", "latitude", "longitude",]
    farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)

    #  farmer cluster
    farmer_cluster_map_values = FarmerClusterSeasonMap.objects.filter(season_id=season_id).order_by("seasonal_farmer_code").values_list("id", "farmer_id", "seasonal_farmer_code", 'cluster_id', 'cluster__name')
    farmer_cluster_columns = ["farmer_cluster_map_id", "farmer_id","code", "cluster_id", "cluster_name"]
    farmer_cluster_df = pd.DataFrame(list(farmer_cluster_map_values), columns=farmer_cluster_columns)

    # agent farmer map
    agent_farmer_map_values = AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id", "farmer__farmer_id", "agent__first_name", "farmer__season__name", "agent_id","agent__userprofile__mobile")
    agent_farmer_columns = [ "agent_farmer_map_id", "farmer_id", "agent_first_name", "season_name", "agent_id", "agent_mobile"]
    agent_farmer_df = pd.DataFrame(list(agent_farmer_map_values), columns=agent_farmer_columns)

    # merge farmer with agent
    merged_df = pd.merge( farmer_df, agent_farmer_df, left_on="farmer_id", right_on="farmer_id", how="left",)

    # merge farmer with cluster
    season_id = get_active_season_id()
    farmer_cluster_merged_df = pd.merge( merged_df, farmer_cluster_df, left_on="farmer_id", right_on="farmer_id", how="left",)
    farmer_cluster_merged_df["total_main_crop_area"] = farmer_cluster_merged_df.apply(lambda x: find_main_crop_area(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["yeild"] = 0
    farmer_cluster_merged_df["total_nursury_crop_area"] = farmer_cluster_merged_df.apply(lambda x: find_nursury_crop_area(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["nursury_crop_age_list"] = farmer_cluster_merged_df.apply(lambda x: find_nursury_age_list(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["main_crop_age_list"] = farmer_cluster_merged_df.apply(lambda x: find_main_age_list(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["harvest_area"] = farmer_cluster_merged_df.apply(lambda x: get_harvest_area(x['farmer_id'], season_id), axis=1)
    farmer_cluster_merged_df["harvest_qty"] = farmer_cluster_merged_df.apply(lambda x: get_harvest_qty(x['farmer_id'], season_id), axis=1)
    farmer_cluster_merged_df["transplanting_gps_status"] = farmer_cluster_merged_df.apply(lambda x: get_gps_status(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["transplanting_gps_tag_status"] = farmer_cluster_merged_df.apply(lambda x: get_gps_tag_status(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["sowing_gps_status"] = farmer_cluster_merged_df.apply(lambda x: get_sowing_gps_status(x["farmer_id"], season_id), axis=1)
    farmer_cluster_merged_df["have_bank_account"] = farmer_cluster_merged_df.apply(lambda x: check_bank_details_available(x["farmer_id"]), axis=1)
    farmer_cluster_merged_df["input_distributed"] = farmer_cluster_merged_df.apply(lambda x: get_input_distribution_details(x["farmer_id"], season_id), axis=1)
    
    sowing_values = Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list("id","farmer_id","crop__name","cultivation_phase_id","cultivation_phase__name","sowing_date",)
    sowing_columns = [ "sowing_id", "farmer_id", "crop_name", "cultivation_phase_id", "cultivation_phase__name", "sowing_date",]
    sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)
    today = datetime.date.today()
    sowing_df["crop_age_list"] = today - sowing_df["sowing_date"]
    sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype("timedelta64[D]")
    sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype(int)

    # sowing_area_df = (sowing_df.groupby("farmer_id")["crop_age_list"].apply(list).to_frame())
    cultivation_phase_merge = (sowing_df.groupby("farmer_id")["cultivation_phase_id"].apply(list).to_frame())

    area_merge = pd.merge(farmer_cluster_merged_df,sowing_df,left_on="farmer_id",right_on="farmer_id",how="left",)
    phase_merge = pd.merge(area_merge,cultivation_phase_merge,left_on="farmer_id",right_on="farmer_id",how="left",)
    phase_merge = phase_merge.drop_duplicates(['farmer_id','code'])
    final_df = phase_merge.fillna(0)
    final_df = final_df.rename(columns={"cultivation_phase_id_y": "cultivation_phase_id"})
    final_df = final_df.sort_values('code')
    final_df = final_df.to_dict("r")

    return Response(data=final_df, status=status.HTTP_200_OK)


def check_bank_details_available(farmer_id):
    if FarmerBankDetails.objects.filter(farmer_id=farmer_id, is_active=True).exists():
        return True
    else:
        return False

def get_input_distribution_details(farmer_id, season_id):
    if Sowing.objects.filter(farmer_id=farmer_id, season_id=season_id).exists():
        sowing_ids = list(Sowing.objects.filter(farmer_id=farmer_id, season_id=season_id).values_list('id',flat=True))
        if AgentFarmerDistributionSowing.objects.filter(sowing_id__in=sowing_ids).exists():
            return AgentFarmerDistributionSowing.objects.filter(sowing_id__in=sowing_ids).count()
        else:
            return False
    else:
        return False


def get_sowing_gps_status(farmer_id, season_id):
    data = ''
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id).exists():
        data = 1
        if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1, season_id=season_id, longitude__isnull=True).exists():
            data = 2
    else:
        data = 3
    return data

def get_gps_tag_status(farmer_id, season_id):
    data = ''
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id).exists():
        data = 1
        if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2, season_id=season_id, longitude__isnull=True).exists():
            data = 2
    else:
        data = 3
    return data

def getImageObjAsImageFile(image_obj):
    try:
        with open("static/media/" + str(image_obj), "rb") as image_file:
            encoded_image1 = b64encode(image_file.read())
            return "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
    except Exception as err:
        print(err)
        return None


@api_view(["POST"])
def serve_selected_farmer_details(request):
    farmer_objs = Farmer.objects.filter(id=request.data["farmer_id"])
    farmer_values = farmer_objs.values_list(
        "id",
        "first_name",
        "last_name",
        "code",
        "gender",
        "gender__name",
        "mobile",
        "alternate_mobile",
        "email",
        "address",
        "state_id",
        "state__name",
        "hobli_id",
        "hobli__name",
        "pincode",
        "aadhaar_number",
        "aadhaar_document",
        "cultivated_for_ccgb_since",
        "cluster__name",
        "latitude",
        "longitude",
        "district_id",
        "district__name",
        "taluk_id",
        "taluk__name",
        "village_id",
        "village__name",
        "alternate_mobile",
        "communication_language",
        "communication_language__name",
        "caste",
        "caste__name",
        "farm_holding_size_classification",
        "farm_holding_size_classification__name",
        "farm_holding_size_in_acre",
        "crop_under_cultivation_id",
        "crop_under_cultivation__name",
        "agreement_number",
        "agreement_document",
        "cluster_id",
        "cluster__name",
        "cultivated_for_ccgb_since",
    )
    farmer_columns = [
        "farmer_id",
        "first_name",
        "last_name",
        "code",
        "gender",
        "gender_name",
        "mobile",
        "alternate_mobile",
        "email",
        "address",
        "state_id",
        "state_name",
        "hobli_id",
        "hobli_name",
        "pincode",
        "aadhaar_number",
        "aadhaar_document",
        "collaborated_with_company_on",
        "cluster_name",
        "latitude",
        "longitude",
        "district_id",
        "district_name",
        "taluk_id",
        "taluk_name",
        "village_id",
        "village_name",
        "alternate_mobile",
        "communication_language_id",
        "communication_language_name",
        "caste",
        "caste_name",
        "farm_holding_size_classification_id",
        "farm_holding_size_classification_name",
        "farm_holding_size_in_acre",
        "crop_under_cultivation_id",
        "crop_under_cultivation__name",
        "agreement_number",
        "agreement_document",
        "cluster_id",
        "cluster_name",
        "cultivated_for_ccgb_since",
    ]
    farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)
    farmer_df["aadhaar_document"] = farmer_df.apply(
        lambda x: getImageObjAsImageFile(x["aadhaar_document"]), axis=1
    )
    farmer_df["agreement_document"] = farmer_df.apply(
        lambda x: getImageObjAsImageFile(x["agreement_document"]), axis=1
    )
    farmer_df = farmer_df.to_dict("r")[0]
    return Response(data=farmer_df, status=status.HTTP_200_OK)


# serving data for uploading agent and view
@api_view(["POST"])
def serve_agent_data_for_update(request):
    print(request.data)
    season_id = get_active_season_id()
    user_id = request.data["user_id"]
    user_obj = User.objects.get(id=user_id)
    user_profile_obj = UserProfile.objects.get(user_id=user_id)
    # agent_office_obj = AgentOffice.objects.get(user_id=user_id)
    # agent_bank_obj = UserBankDetails.objects.get(user_id=user_id)
    # cluster_obj = UserClusterMap.objects.filter(user_id=user_id)[0]
    if UserHierarchyMap.objects.filter(subordinate__id=user_id, season_id=season_id).exists():
        supervisor_id = UserHierarchyMap.objects.get(subordinate__id=user_id, season_id=season_id).superior.id
    else:
        supervisor_id = None
    data_dict = {
        "id": user_id,
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "gender_id": user_profile_obj.gender_id,
        "dob": user_profile_obj.dob,
        "mobile": user_profile_obj.mobile,
        "alternate_mobile": user_profile_obj.alternate_mobile,
        "email": user_obj.email,
        "cluster_id": list(
            UserClusterMap.objects.filter(user_id=user_id, season_id=2).values_list(
                "cluster_id", flat=True
            )
        ),
        "state_id": user_profile_obj.state_id,
        "district_id": user_profile_obj.district_id,
        "taluk_id": user_profile_obj.taluk_id,
        "hobli_id": user_profile_obj.hobli_id,
        "blood_group_id": user_profile_obj.blood_group_id,
        "village_id": user_profile_obj.village_id,
        "address": user_profile_obj.address,
        "pincode": user_profile_obj.pincode,
        "educational_qualification": user_profile_obj.educational_qualification_id,
        "institution_name": user_profile_obj.institution_name,
        "university_name": user_profile_obj.university_name,
        "aadhaar_number": user_profile_obj.aadhaar_number,
        "pan_number": user_profile_obj.pan_number,
        "have_prior_experience": user_profile_obj.prior_experience_in_other_company,
        "prior_experience_company_name": user_profile_obj.prior_experience_company_name,
        "prior_experience_duration": user_profile_obj.prior_experience_duration,
        "collaborated_date": user_profile_obj.date_of_joining,
        "supervisor_id":supervisor_id
    }
    # checking file fields whether exists or not
    try:
        with open(
                "static/media/" + str(user_profile_obj.aadhaar_document), "rb"
        ) as image_file:
            encoded_image1 = b64encode(image_file.read())
            data_dict["image"] = "data:image/jpeg;base64," + encoded_image1.decode(
                "utf-8"
            )
    except Exception as err:
        print(err)
        data_dict["image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.pan_document), "rb"
        ) as image_file:
            encoded_image2 = b64encode(image_file.read())
            data_dict["pan_image"] = "data:image/jpeg;base64," + encoded_image2.decode(
                "utf-8"
            )
    except Exception as err:
        print(err)
        data_dict["pan_image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.driving_licence_document), "rb"
        ) as image_file:
            encoded_image3 = b64encode(image_file.read())
            data_dict[
                "driving_licence_image"
            ] = "data:image/jpeg;base64," + encoded_image3.decode("utf-8")
    except Exception as err:
        print(err)
        data_dict["driving_licence_image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.agreement_document), "rb"
        ) as image_file:
            encoded_image4 = b64encode(image_file.read())
            data_dict[
                "agreement_image"
            ] = "data:image/jpeg;base64," + encoded_image4.decode("utf-8")
    except Exception as err:
        print(err)
        data_dict["agreement_image"] = "no-image"

    if UserImage.objects.filter(user_id=user_id).exists():
        profile_image = UserImage.objects.get(user_id=user_id).image
        try:
            with open("static/media/" + str(profile_image), "rb") as image_file:
                encoded_image6 = b64encode(image_file.read())
                data_dict["photo"] = "data:image/jpeg;base64," + encoded_image6.decode(
                    "utf-8"
                )
        except Exception as err:
            print(err)
            data_dict["photo"] = "no-image"
    return Response(data=data_dict, status=status.HTTP_200_OK)


# serve employee data for update
@api_view(["POST"])
def serve_super_visor_data_for_update(request):
    print(request.data)
    user_id = request.data["user_id"]
    user_obj = User.objects.get(id=user_id)
    user_profile_obj = UserProfile.objects.get(user_id=user_id)
    data_dict = {
        "id": user_id,
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "gender_id": user_profile_obj.gender.id,
        "dob": user_profile_obj.dob,
        "user_type_id": user_profile_obj.user_type.id,
        "mobile": user_profile_obj.mobile,
        "alternate_mobile": user_profile_obj.alternate_mobile,
        "cluster_id": list(
            UserClusterMap.objects.filter(user_id=user_id, season_id=2).values_list(
                "cluster_id", flat=True
            )
        ),
        "email": user_obj.email,
        "state_id": user_profile_obj.state.id,
        "district_id": user_profile_obj.district.id,
        "taluk_id": user_profile_obj.taluk.id,
        "hobli_id": user_profile_obj.hobli.id,
        "village_id": user_profile_obj.village.id,
        "address": user_profile_obj.address,
        "pincode": user_profile_obj.pincode,
        "educational_qualification": user_profile_obj.educational_qualification_id,
        "institution_name": user_profile_obj.institution_name,
        "university_name": user_profile_obj.university_name,
        "aadhaar_number": user_profile_obj.aadhaar_number,
        "pan_number": user_profile_obj.pan_number,
        "have_prior_experience": user_profile_obj.prior_experience_in_other_company,
        "prior_experience_company_name": user_profile_obj.prior_experience_company_name,
        "prior_experience_duration": user_profile_obj.prior_experience_duration,
        "collaborated_date": user_profile_obj.date_of_joining,
        "agreement_number": user_profile_obj.agreement_number,
        "driving_licence_number": user_profile_obj.driving_licence_number,
        "blood_group_id": user_profile_obj.blood_group_id,
    }

    try:
        with open(
                "static/media/" + str(user_profile_obj.aadhaar_document), "rb"
        ) as image_file:
            encoded_image1 = b64encode(image_file.read())
            data_dict["image"] = "data:image/jpeg;base64," + encoded_image1.decode(
                "utf-8"
            )
    except Exception as err:
        print(err)
        data_dict["image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.pan_document), "rb"
        ) as image_file:
            encoded_image2 = b64encode(image_file.read())
            data_dict["pan_image"] = "data:image/jpeg;base64," + encoded_image2.decode(
                "utf-8"
            )
    except Exception as err:
        print(err)
        data_dict["pan_image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.driving_licence_document), "rb"
        ) as image_file:
            encoded_image3 = b64encode(image_file.read())
            data_dict[
                "driving_licence_image"
            ] = "data:image/jpeg;base64," + encoded_image3.decode("utf-8")
    except Exception as err:
        print(err)
        data_dict["driving_licence_image"] = "no-image"

    try:
        with open(
                "static/media/" + str(user_profile_obj.agreement_document), "rb"
        ) as image_file:
            encoded_image4 = b64encode(image_file.read())
            data_dict[
                "agreement_image"
            ] = "data:image/jpeg;base64," + encoded_image4.decode("utf-8")
    except Exception as err:
        print(err)
        data_dict["agreement_image"] = "no-image"

    if UserImage.objects.filter(user_id=user_id).exists():
        profile_image = UserImage.objects.get(user_id=user_id).image
        try:
            with open("static/media/" + str(profile_image), "rb") as image_file:
                encoded_image6 = b64encode(image_file.read())
                data_dict["photo"] = "data:image/jpeg;base64," + encoded_image6.decode(
                    "utf-8"
                )
        except Exception as err:
            print(err)
            data_dict["photo"] = "no-image"

    return Response(data=data_dict, status=status.HTTP_200_OK)


# serve farmer data for update and view
@api_view(["POST"])
def serve_farmer_data_for_update(request):
    print(request.data)
    user_id = request.data["user_id"]
    farmer_obj = Farmer.objects.get(id=user_id)

    data_dict = {
        "id": user_id,
        "first_name": farmer_obj.first_name,
        "last_name": farmer_obj.last_name,
        "mobile": farmer_obj.mobile,
        "alternate_mobile": farmer_obj.alternate_mobile,
        "email": farmer_obj.email,
        "state_id": farmer_obj.state.id,
        "district_id": farmer_obj.district.id,
        "taluk_id": farmer_obj.taluk.id,
        "hobli_id": farmer_obj.hobli.id,
        "village_id": farmer_obj.village.id,
        "gender_id": farmer_obj.gender_id,
        "address": farmer_obj.address,
        "pincode": farmer_obj.pincode,
        "caste_id": farmer_obj.caste_id,
        "communication_language_id": farmer_obj.communication_language_id,
        "farm_area": farmer_obj.farm_holding_size_in_acre,
        "farm_classification_id": farmer_obj.farm_holding_size_classification_id,
        "aadhaar_number": farmer_obj.aadhaar_number,
        "collaborated_date": farmer_obj.cultivated_for_ccgb_since,
        # "cluster_id": farmer_obj.cluster_id,
        "cluster_id": FarmerClusterSeasonMap.objects.get(farmer_id=farmer_obj, season_id=get_active_season_id()).cluster_id,
        "officer_id": UserFarmerMap.objects.filter(farmer__farmer=farmer_obj)[
            0
        ].officer.id,
        "agent_id": AgentFarmerMap.objects.filter(farmer__farmer=farmer_obj)[
            0
        ].agent.id,
    }

    try:
        with open(
                "static/media/" + str(farmer_obj.aadhaar_document), "rb"
        ) as image_file:
            encoded_image1 = b64encode(image_file.read())
            data_dict["image"] = "data:image/jpeg;base64," + encoded_image1.decode(
                "utf-8"
            )
    except Exception as err:
        print(err)
        data_dict["image"] = "no-image"

    try:
        with open(
                "static/media/" + str(farmer_obj.agreement_document), "rb"
        ) as image_file:
            encoded_image4 = b64encode(image_file.read())
            data_dict[
                "agreement_image"
            ] = "data:image/jpeg;base64," + encoded_image4.decode("utf-8")
    except Exception as err:
        print(err)
        data_dict["agreement_image"] = "no-image"

    return Response(data=data_dict, status=status.HTTP_200_OK)


# get all taluks
@api_view(["GET"])
def serve_taluk(request):
    taluk_values = Taluk.objects.all().values_list(
        "id", "district_id", "district__name", "name"
    )
    taluk_columns = ["id", "district_id", "district_name", "name"]
    taluk_df = pd.DataFrame(list(taluk_values), columns=taluk_columns)
    taluk_data = taluk_df.to_dict("r")
    return Response(data=taluk_data, status=status.HTTP_200_OK)


# save_taluk
@api_view(["POST"])
def save_hobli(request):
    data = {}
    if Hobli.objects.filter(
            name__iexact=request.data["name"], taluk_id=request.data["taluk_id"]
    ).exists():
        data["message"] = "taluk already present"
    else:

        hobli_obj = Hobli(name=request.data["name"], taluk_id=request.data["taluk_id"])
        hobli_obj.save()
        data["message"] = "Hobli register success"
        data["hobli_id"] = hobli_obj.id
    return Response(data=data, status=status.HTTP_200_OK)


# get all taluk
@api_view(["GET"])
def serve_all_hoblis(request):
    hobli_values = Hobli.objects.all().values_list("id", "name")
    hobli_columns = ["id", "name"]
    hobli_df = pd.DataFrame(list(hobli_values), columns=hobli_columns)
    hobli_data = hobli_df.to_dict("r")
    return Response(data=hobli_data, status=status.HTTP_200_OK)


# save_village
@api_view(["POST"])
def save_village(request):
    data = {}
    print(request.data)
    if Village.objects.filter(
            name__iexact=request.data["name"], hobli_id=request.data["hobli_id"]
    ).exists():
        data["message"] = "hobli already present"
    else:
        village_obj = Village(
            name=request.data["name"], hobli_id=request.data["hobli_id"]
        )
        village_obj.save()
        data["message"] = "Village register success"
        data["village_id"] = village_obj.id
    return Response(data=data, status=status.HTTP_200_OK)


# serve user types
@api_view(["GET"])
def serve_user_types(request):
    # user_type_values = UserType.objects.filter(id__in=[3, 5]).values_list('id', 'name')
    user_type_values = UserType.objects.filter().values_list("id", "name")
    # user_type_values = UserType.objects.filter().values_list('id', 'name')
    user_type_columns = ["id", "name"]
    user_type_df = pd.DataFrame(list(user_type_values), columns=user_type_columns)
    user_type_data = user_type_df.to_dict("r")
    return Response(data=user_type_data, status=status.HTTP_200_OK)


# serve user types
@api_view(["GET"])
def serve_user_types_for_employee_registration(request):
    # user_type_values = UserType.objects.filter(id__in=[3, 5]).values_list('id', 'name')
    user_type_values = list(UserType.objects.all().exclude(id__in=[6,7,8,10]).values_list("id", "name"))
    # user_type_values = UserType.objects.filter().values_list('id', 'name')
    user_type_columns = ["id", "name"]
    user_type_df = pd.DataFrame(user_type_values, columns=user_type_columns)
    user_type_data = user_type_df.to_dict("r")
    print(user_type_data)
    return Response(data=user_type_data, status=status.HTTP_200_OK)


# serve storage_type
@api_view(["GET"])
def serve_storage_types(request):
    storage_type_values = StorageType.objects.filter().values_list("id", "name")
    storage_type_columns = ["id", "name"]
    storage_type_df = pd.DataFrame(
        list(storage_type_values), columns=storage_type_columns
    )
    storage_type_data = storage_type_df.to_dict("r")
    return Response(data=storage_type_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_input_batches(request):
    # input item input batch map
    # input_item_input_batch_values = InputItemInputPartBatchMap.objects.all().values_list(
    #     "id",
    #     "code",
    #     "quantity_at_receipt",
    #     "quantity_now",
    #     "quantity_now_time",
    #     "unit_id",
    #     "unit__name",
    #     "item_id",
    #     "item__name",
    #     "item__value",
    #     "price",
    # )
    # input_item_input_batch_columns = [
    #     "input_item_input_batch_map_id",
    #     "input_item_input_batch_map_code",
    #     "input_item_input_batch_map_quantity_at_receipt",
    #     "input_item_input_batch_map_quantity_now",
    #     "input_item_input_batch_map_quantity_now_time",
    #     "input_item_input_batch_map_unit_id",
    #     "input_item_input_batch_map_unit__name",
    #     "item_input_id",
    #     "item_input_name",
    #     "item_value",
    #     "price",
    # ]
    # input_item_input_batch_df = pd.DataFrame(
    #     list(input_item_input_batch_values), columns=input_item_input_batch_columns
    # )

    # # input batch lables
    # input_batch_label_values = InputBatchLabel.objects.all().values_list(
    #     "input_item_input_batch",
    #     "label_prefix",
    #     "label_suffix",
    #     "label_range_start",
    #     "label_range_end",
    # )
    # input_batch_label_columns = [
    #     "input_item_input_batch",
    #     "label_prefix",
    #     "label_suffix",
    #     "label_range_start",
    #     "label_range_end",
    # ]
    # input_batch_label_df = pd.DataFrame(
    #     list(input_batch_label_values), columns=input_batch_label_columns
    # )
    # # merge input item merged df with label
    # final_df = pd.merge(
    #     input_item_input_batch_values,
    #     input_batch_label_df,
    #     left_on="input_item_input_batch_map_id",
    #     right_on="input_item_input_batch",
    #     how="left",
    # )
    # final_df = final_df.fillna(0)
    return Response(data=[], status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_storages(request):
    storage_values = Storage.objects.filter().values_list("id", "name", "type__name")
    storage_columns = ["id", "name", "storage_type_name"]
    storage_df = pd.DataFrame(list(storage_values), columns=storage_columns)
    storage_data = storage_df.to_dict("r")
    return Response(data=storage_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_input_items_into_storage(request):
    data = {}

    # # save input items into  stroage location
    # input_item_input_batch_storage_location_obj = InputItemInputBatchStorageLocation(
    #     item_batch_map_id=request.data["input_item_batch_id"],
    #     storage_id=request.data["storage_id"],
    #     date_of_receipt=datetime.datetime.now(),
    #     quantity_at_receipt=request.data["packet_count"],
    #     quantity_now=request.data["packet_count"],
    #     quantity_now_time=datetime.datetime.now(),
    #     unit_id=request.data["quantity_unit"],
    #     created_by=request.user,
    #     modified_by=request.user,
    # )

    # input_item_input_batch_storage_location_obj.save()
    # print("saved the storage batch location success")

    # input_item_input_batch_map = InputItemInputBatchMap.objects.get(
    #     id=request.data["input_item_batch_id"]
    # )

    # # update the  current quantity in InputItemInputBatchMap
    # input_item_input_batch_map.quantity_now = (
    #         input_item_input_batch_map.quantity_now - int(request.data["packet_count"])
    # )
    # input_item_input_batch_map.quantity_now_time = datetime.datetime.now()
    # input_item_input_batch_map.save()

    # product_value = input_item_input_batch_map.item.value
    # print("product_value", product_value)
    # print("packet_count", request.data["packet_count"])
    # updated_weight = product_value * Decimal(request.data["packet_count"])

    # input_batch = InputBatch.objects.get(id=input_item_input_batch_map.batch.id)
    # print("input_batch_quantity : ", input_batch.quantity_now)
    # print("updated_weight : ", updated_weight)
    # input_batch.quantity_now = Decimal(input_batch.quantity_now) - updated_weight
    # input_batch.quantity_now_time = datetime.datetime.now()
    # input_batch.save()

    # # individual label store
    # label_no = request.data["label_from"]
    # for i in range(0, int(request.data["packet_count"])):
    #     label = str(request.data["prefix"]) + str(label_no).zfill(4)
    #     print(label)
    #     input_packet_label_obj = InputItemInputBatchStorageLocationPacketLabel(
    #         item_batch_storage_map=input_item_input_batch_storage_location_obj,
    #         label=label,
    #         stock_status_id=1,  # at_storage
    #         recieved_date=datetime.datetime.now(),
    #         recieved_by=request.user,
    #     )
    #     input_packet_label_obj.save()
    #     label_no = int(label_no) + 1

    data["message"] = "items labeled and stored successfully"
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_input_items_input_batch_storage(request):
    # input_item_input_batch_storage_location_values = (
    #     InputItemInputBatchStorageLocation.objects.all().values_list(
    #         "id",
    #         "item_batch_map__batch__code",
    #         "item_batch_map_id",
    #         "item_batch_map__code",
    #         "item_batch_map__price",
    #         "item_batch_map__item__name",
    #         "item_batch_map__item__value",
    #         "item_batch_map__batch_id",
    #         "storage_id",
    #         "storage__name",
    #         "storage__type__name",
    #         "section",
    #         "sub_section",
    #         "date_of_receipt",
    #         "quantity_at_receipt",
    #         "quantity_now",
    #         "quantity_now_time",
    #         "unit",
    #         "unit__name",
    #     )
    # )
    # input_item_input_batch_storage_location_columns = [
    #     "id",
    #     "batch_code",
    #     "item_batch_map_id",
    #     "item_batch_map_code",
    #     "item_batch_map_price",
    #     "item_batch_map_item_name",
    #     "item_batch_map_item_value",
    #     "item_batch_map_batch_id",
    #     "storage_id",
    #     "storage_name",
    #     "storage_type_name",
    #     "section",
    #     "sub_section",
    #     "date_of_receipt",
    #     "quantity_at_receipt",
    #     "quantity_now",
    #     "quantity_now_time",
    #     "unit",
    #     "unit_name",
    # ]
    # input_item_input_batch_storage_location_df = pd.DataFrame(
    #     list(input_item_input_batch_storage_location_values),
    #     columns=input_item_input_batch_storage_location_columns,
    # )
    # input_item_input_batch_storage_location_df.groupby("item_batch_map_id").apply(
    #     lambda x: x.to_dict("r")
    # ).to_dict()

    # input_item_input_batch_storage_location_df[
    #     "calculated_sum_quantity_at_receipt"
    # ] = input_item_input_batch_storage_location_df.groupby(
    #     ["item_batch_map_id", "storage_id"]
    # )[
    #     "quantity_at_receipt"
    # ].transform(
    #     "sum"
    # )
    # input_item_input_batch_storage_location_df[
    #     "calculatedsum_quanitity_now"
    # ] = input_item_input_batch_storage_location_df.groupby(
    #     ["item_batch_map_id", "storage_id"]
    # )[
    #     "quantity_now"
    # ].transform(
    #     "sum"
    # )

    # input_item_input_batch_storage_location_df.drop_duplicates(subset=["item_batch_map_id", "quantity_now"],
    #                                                            keep="first", inplace=True
    #                                                            )
    # data = (
    #     input_item_input_batch_storage_location_df.groupby("storage_name")
    #         .apply(lambda x: x.to_dict("r"))
    #         .to_dict()
    # )
    data = []
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_agent_list(request):
    agent_values = UserProfile.objects.filter(user_type_id=6).values_list(
        "user_id", "user__first_name", "user__last_name", "user__username", "code"
    )
    agent_columns = ["user_id", "first_name", "last_name", "username", "code"]
    agent_df = pd.DataFrame(list(agent_values), columns=agent_columns)
    return Response(agent_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def save_storage_to_agent_seed_distribution(request):
    data = {}
    # activating the agent by adding agent to UserClusterMap
    # for cluster_id in request.data["cluster_ids"]:
    #     if UserClusterMap.objects.filter(
    #             user_id=request.data["agent_id"], cluster_id=cluster_id, season_id=2
    #     ).exists():
    #         continue
    #     else:
    #         user_cluster_map_obj = UserClusterMap(
    #             user_id=request.data["agent_id"],
    #             cluster_id=cluster_id,
    #             season_id=2,
    #             modified_by=request.user,
    #         )
    #         user_cluster_map_obj.save()

    # # updating the storage location by subrsating the dispatched qunaity in quantity now
    # input_storage_obj = InputItemInputBatchStorageLocation.objects.get(
    #     id=request.data["input_item_input_batch_storage_id"]
    # )
    # input_storage_obj.quantity_now = input_storage_obj.quantity_now - int(
    #     request.data["packet_count"]
    # )
    # input_storage_obj.quantity_now_time = datetime.datetime.now()
    # input_storage_obj.save()

    # # getting the label value to update the status from at_storage to displattched
    # label_no = request.data["label_from"]
    # prefix = InputBatchLabel.objects.get(
    #     input_item_input_batch_id=input_storage_obj.item_batch_map.id
    # ).label_prefix
    # # print('input_storage_obj.item_batch_map_id',input_storage_obj.item_batch_map_id)
    # input_item_input_batch_agent_inventory_obj = InputItemInputBatchAgentInventory(
    #     item_batch_map_id=input_storage_obj.item_batch_map_id,
    #     agent_id=request.data["agent_id"],
    #     date_of_receipt=request.data["receipt_date"],
    #     quantity_at_receipt=request.data["packet_count"],
    #     quantity_now=request.data["packet_count"],
    #     quantity_now_time=request.data["receipt_date"],
    #     price_per_item=request.data["agent_price"],
    #     unit_id=input_storage_obj.unit_id,
    #     created_by=request.user,
    #     modified_by=request.user,
    # )
    # input_item_input_batch_agent_inventory_obj.save()

    # # print('input saved for inventory')
    # # looping the packet counts to change the status and create a log on farmer packet label
    # for index in range(0, int(request.data["packet_count"])):
    #     label = str(prefix) + str(label_no).zfill(4)
    #     # print('label :', label)
    #     InputItemInputBatchStorageLocationPacketLabel.objects.filter(
    #         item_batch_storage_map=request.data["input_item_input_batch_storage_id"],
    #         label=label,
    #     ).update(
    #         stock_status_id=2,
    #         dispatched_date=request.data["receipt_date"],
    #         dispatched_by=request.user,
    #     )
    #     # print('input_item_input_batch_agent_inventory_obj', input_item_input_batch_agent_inventory_obj.id)
    #     agent_packet_label = AgentPacketLabel(
    #         inputitem_inputbatch_agent_inventory_id_id=input_item_input_batch_agent_inventory_obj.id,
    #         label=label,
    #         stock_status_id=1,
    #         recieved_date=request.data["receipt_date"],
    #     )
    #     agent_packet_label.save()

    #     label_no = int(label_no) + 1

    # # update agent wallet
    # total_amount = int(request.data["agent_price"]) * int(request.data["packet_count"])
    # # no  wallet
    # if not AgentWallet.objects.filter(agent_id=request.data["agent_id"]).exists():
    #     updated_amount = 0 - Decimal(total_amount)
    #     old_balance = 0
    #     print("type : ", updated_amount)
    #     AgentWallet.objects.create(
    #         agent_id=request.data["agent_id"],
    #         current_balance=updated_amount,
    #         modified_by=request.user,
    #     )
    #     new_balance = updated_amount

    # # existing wallet
    # else:
    #     old_balance = AgentWallet.objects.get(
    #         agent_id=request.data["agent_id"]
    #     ).current_balance
    #     updated_amount = old_balance - int(total_amount)
    #     AgentWallet.objects.filter(agent_id=request.data["agent_id"]).update(
    #         current_balance=Decimal(updated_amount), modified_by=request.user
    #     )
    #     new_balance = updated_amount

    # # add transaction log for money reducing in wallet
    # agent_transaction_log = AgentTransactionLog(
    #     date=request.data["receipt_date"],
    #     transaction_direction_id=2,  # ccgb to wallet for money reduction for input buying
    #     agent_id=request.data["agent_id"],
    #     data_entered_by=request.user,
    #     amount=total_amount,
    #     transaction_id=request.data["receipt_no"],
    #     transaction_mode_id=1,
    #     transaction_approval_status_id=1,
    #     wallet_balance_before_this_transaction=old_balance,
    #     wallet_balance_after_this_transaction=new_balance,
    #     description="money deduction from wallet - money reduction from wallet(negative)",
    #     modified_by=request.user,
    # )
    # agent_transaction_log.save()

    # # mapping wallet adjustment for buying input with transaction log
    # InputDistributionTransactionMap.objects.create(
    #     transaction_log=agent_transaction_log,
    #     input_item_sale=input_item_input_batch_agent_inventory_obj,
    # )

    data["message"] = "seed dispatched to agent"
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_cluster_for_selected_agent(request):
    print(request.data)
    if UserClusterMap.objects.filter(
            season_id=2, user_id=request.data["agent_id"]
    ).exists():
        cluster_id_list = list(
            UserClusterMap.objects.filter(
                season_id=2, user_id=request.data["agent_id"]
            ).values_list("cluster_id", flat=True)
        )
    else:
        cluster_id_list = []
    return Response(cluster_id_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_seed_distribution_history(request):
    # print(request.data)
    # values = InputItemInputBatchAgentInventory.objects.filter(
    #     agent_id=request.data["agent_user_id"]
    # ).values_list(
    #     "id",
    #     "agent__first_name",
    #     "agent__last_name",
    #     "item_batch_map__item__name",
    #     "item_batch_map__code",
    #     "agent",
    #     "date_of_receipt",
    #     "quantity_at_receipt",
    #     "quantity_now",
    #     "quantity_now_time",
    #     "unit",
    #     "unit__name",
    # )
    # columns = [
    #     "id",
    #     "first_name",
    #     "last_name",
    #     "name",
    #     "code",
    #     "agent",
    #     "date_of_receipt",
    #     "quantity_at_receipt",
    #     "quantity_now",
    #     "quantity_now_time",
    #     "unit",
    #     "unit_name",
    # ]
    # df = pd.DataFrame(list(values), columns=columns)
    # df = df.to_dict("r")

    return Response(df=[], status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_inputs_for_pop_storage(request):
    # input_values = InputItemInputBatchStorageLocation.objects.filter(
    #     quantity_now__gt=0
    # ).values_list(
    #     "id",
    #     "item_batch_map__item__name",
    #     "quantity_now",
    #     "storage__name",
    #     "item_batch_map__price",
    # )
    # input_columns = ["id", "name", "quantity_now", "storage", "item_batch_map_price"]
    # input_df = pd.DataFrame(list(input_values), columns=input_columns)
    return Response(data=[], status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_role_users(request):
    user_id_list = list(PositionPositionUserMap.objects.all().values_list("user_id", flat=True))
    # user
    user = User.objects.filter(id__in=user_id_list)
    user_values = user.values_list("id", "first_name", "last_name")
    user_columns = ["id", "first_name", "last_name"]
    user_df = pd.DataFrame(list(user_values), columns=user_columns)
    # user profile
    user_profile_obj = UserProfile.objects.filter(user_id__in=user_id_list).order_by('-code')
    user_profile_values = user_profile_obj.values_list( "user_id", "id", "code", "user_type", "user_type__name", "dob", "mobile", "alternate_mobile", "user__email", "address", "state_id", "state__name", "hobli_id", "hobli__name", "pincode", "educational_qualification_id", "institution_name", "university_name", "aadhaar_number", "pan_number", "prior_experience_in_other_company", "prior_experience_company_name", "prior_experience_duration", "date_of_joining", "latitude", "longitude",)
    user_profile_columns = [ "user_id", "id", "code", "user_type_id", "user_type", "dob", "mobile", "alternate_mobile", "email", "address", "state_id", "state__name", "hobli_id", "hobli_name", "pincode", "educational_qualification_id", "institution_name", "university_name", "aadhaar_number", "pan_number", "prior_experience_in_other_company", "prior_experience_company_name", "prior_experience_duration", "collaborated_with_company_on", "latitude", "longitude",]
    user_profile_df = pd.DataFrame(list(user_profile_values), columns=user_profile_columns)
    user_profile_merge = pd.merge(user_df, user_profile_df, left_on="id", right_on="user_id", how="inner")
    user_profile_merge = user_profile_merge.fillna(0)

    user_cluster_map_values = UserClusterMap.objects.filter(season_id=1).values_list("id", "user_id", "cluster__name")
    user_cluster_map_columns = ["id", "user", "clusters"]
    user_cluster_map_df = pd.DataFrame(list(user_cluster_map_values), columns=user_cluster_map_columns)

    user_cluster_map_df = (user_cluster_map_df.groupby("user")["clusters"].apply(list).to_frame())
    cluster_merged_df = pd.merge(user_profile_merge,user_cluster_map_df,left_on="user_id",right_on="user",how="left",)
    cluster_merged_df = cluster_merged_df.fillna(0)

    for index, row in cluster_merged_df.iterrows():
        if PositionManUserMap.objects.filter(position_user_map__user_id=row["user_id"]).exists():
            cluster_merged_df.at[index, "code"] = PositionManUserMap.objects.get(position_user_map__user_id=row["user_id"]).position_user_map.position.name
            cluster_merged_df.at[index, "man_username"] = PositionManUserMap.objects.get(position_user_map__user_id=row["user_id"]).user.first_name
        else:
            cluster_merged_df.at[index, "code"] = "-"
            cluster_merged_df.at[index, "man_username"] = "-"
        cluster_merged_df.at[index, "farmer_count"] = UserFarmerMap.objects.filter(officer=row["user_id"]).count()
        if row["clusters"] != 0:
            cluster = ""
            cluster = str("(") + str(len(row["clusters"])) + ")" + " "
            for cluster_name in row["clusters"]:
                cluster = cluster + str(cluster_name) + "," + " "
            cluster_merged_df.at[index, "clusters"] = cluster[0:-2]
    cluster_merged_df = cluster_merged_df.sort_values(by=['code'])
    final_df = cluster_merged_df.to_dict("r")
    return Response(final_df, status=status.HTTP_200_OK)


# **************************mobile codes starts here****************************
# for password reset
def generate_otp():
    return str(random.randint(1000, 9999))


def add_to_phone_number(number):
    cleaned_number = number
    length = len(str(number))

    if length == 12 and str(number)[:2] == "91":
        user = User()
        cleaned_number = number
    elif length == 10:
        cleaned_number = "91" + str(number)
    else:
        cleaned_number = "91" + str(number)
    print("cleaned number: %s" % cleaned_number)
    return int(cleaned_number)


def send_message(to, message, purpose, user_id=None):
    """
    Send message to a single phone number via plivo service 0.0037 USD/sms; only outgoing
    :return:
    """
    try:
        print("original to:%s" % to)
        to_good = add_to_phone_number(to)
        print("91 added to:%s" % to_good)
        client = plivo.RestClient(auth_id=auth_id, auth_token=auth_token)
        message_created = client.messages.create(
            src="919500989012", dst=to_good, text=message
        )
        obj = SMSTrace(
            business_id=1,
            message=message,
            receiver_user_id=user_id,
            purpose="Password reset",
        )
        obj.save()
        if user_id is not None:
            sms_trace_obj = SMSTrace(
                business_id=1, receiver_user_id=user_id, purpose=purpose, message=message
            )
            sms_trace_obj.save()
            print("SMS Trace is saved")
        else:
            sms_trace_obj = SMSTrace(business_id=1, purpose=purpose, message=message)
            sms_trace_obj.save()
            print("SMS Trace is saved")
        # params = {'src': '919500989012', 'method': 'POST', 'dst': '918940341505', 'text': 'messgae'}
        params = {'src': '919500989012', 'method': 'POST', 'dst': to_good, 'text': message}

        # response = p.send_message(params)
        print("response = {}".format(message_created))
    except Exception as e:
        print("=====ERROR====")
        print(e)



# check wheather a valid user for password reset
@api_view(["POST"])
@permission_classes((AllowAny,))
def username_validation(request):
    print(request.data)
    if User.objects.filter(username=request.data["user_name"]).exists():
        user = User.objects.get(username=request.data["user_name"])
        user_obj = UserProfile.objects.get(user=user)
        print(user_obj.mobile)
        if user_obj.mobile == None:
            data = {"message": "Phone number does not Exists!"}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
        otp = generate_otp()
        now = datetime.datetime.now()
        expiry_time = now + datetime.timedelta(minutes=30)
        purpose = "Password reset"
        print(otp)
        msg = "OTP for password reset your ccgb account is " + otp
        print('opt', otp)
        print(user_obj.mobile)
        send_message(user_obj.mobile, msg, purpose, user.id)
    


        password_reset_obj = PasswordResetRequest(
            user=user,
            otp=otp,
            expiry_time=expiry_time,
        )
        password_reset_obj.save()
        print(otp)
        user_details = {
            "user_id": user.id,
            "user_name": user.username,
            "mobile": user_obj.mobile,
        }
        return Response(data=user_details, status=status.HTTP_200_OK)
    else:
        data = {"message": "User does not Exists!"}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
@permission_classes((AllowAny,))
def otp_validation(request):
    if PasswordResetRequest.objects.filter(user=request.data["user_id"], expiry_time__gte=datetime.datetime.now()).exists():
        password_reset_obj = PasswordResetRequest.objects.filter(user=request.data["user_id"], expiry_time__gte=datetime.datetime.now()).order_by("-id")[0]
        print(password_reset_obj.otp)
        if request.data["otp"] == password_reset_obj.otp:
            return Response(data="Correct otp", status=status.HTTP_200_OK)
        else:
            data = {"message": "OTP does Not Match"}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        data = {"message": "Please Try After Some Time"}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
@permission_classes((AllowAny,))
def reset_password(request):
    print(request.data)
    if User.objects.filter(id=request.data["user_id"]).exists():
        user_obj = User.objects.get(id=request.data["user_id"])
        user_obj.password = make_password(request.data["raw_password"])
        user_obj.save()
        print("password is updated")
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_crops_based_on_crop_group(request):
    crop_group_list = []
    crop_group_based_crop = {}
    for crop_group in CropGroup.objects.all():
        crop_group_dict = {}
        crop_group_dict["name"] = crop_group.name
        crop_group_dict["id"] = crop_group.id
        crop_group_dict["short_name"] = crop_group.short_name
        crop_group_list.append(crop_group_dict)
        crop_group_based_crop[crop_group.id] = []
        for crop_group_map in CropCropGroupMap.objects.filter(crop_group=crop_group):
            crop_dict = {"name": crop_group_map.crop.name, "id": crop_group_map.crop.id}
            crop_group_based_crop[crop_group.id].append(crop_dict)
    master_dict = {
        "crop_group_list": crop_group_list,
        "crop_list": crop_group_based_crop,
    }
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_seasons(request):
    season_list = []
    for season in Season.objects.all():
        season_dict = {
            "name": season.crop.name + str("-") + str(season.year.year),
            "id": season.id,
        }
        season_list.append(season_dict)
    return Response(season_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_soil_types(request):
    soil_types = SoilType.objects.all()
    soil_type_vlaues = soil_types.values_list("id", "name")
    soil_type_coloumns = ["id", "name"]
    data = pd.DataFrame(list(soil_type_vlaues), columns=soil_type_coloumns).to_dict("r")
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_irrigation_methods(request):
    irrigation_method = IrrigationMethod.objects.all()
    irrigation_method_values = irrigation_method.values_list("id", "name")
    irrigation_method_columns = ["id", "name"]
    data = pd.DataFrame(
        list(irrigation_method_values), columns=irrigation_method_columns
    ).to_dict("r")
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_cultivation_phase(request):
    phase_list = []
    for phase in CultivationPhase.objects.all():
        phase_dict = {"name": phase.name, "id": phase.id}
        phase_list.append(phase_dict)
    return Response(phase_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_water_resource(request):
    source_list = []
    for source in WaterSource.objects.all():
        source_dict = {"name": source.name, "id": source.id}
        source_list.append(source_dict)
    return Response(source_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_water_types(request):
    water_type_list = []
    for water_type in WaterType.objects.all():
        water_type_dict = {"name": water_type.name, "id": water_type.id}
        water_type_list.append(water_type_dict)
    return Response(water_type_list, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def register_sowing(request):
    data = {}
    req_data = request.data["form_data"]
    if req_data["sowing_id"] == None:
        if not Sowing.objects.filter( farmer_id=req_data["farmer_id"], crop_id=req_data["crop_id"], sowing_date=req_data["sowing_date_proposed"], area=req_data["area"],).exists():
            if req_data["cultivation_phase_id"] == 2:
                if Sowing.objects.filter(season_id=req_data["season_id"], farmer_id=req_data["farmer_id"], cultivation_phase_id=1).exists():
                    if not Sowing.objects.filter(cultivation_phase_id=2).exists():
                        sowing_obj = Sowing(
                            farmer_id=req_data["farmer_id"],
                            crop_id=req_data["crop_id"],
                            sowing_date=req_data["sowing_date_proposed"],
                            area=req_data["area"],
                            season_id=req_data["season_id"],
                            state_id=req_data["state_id"],
                            district_id=req_data["district_id"],
                            taluk_id=req_data["taluk_id"],
                            hobli_id=req_data["hobli_id"],
                            village_id=req_data["village_id"],
                            cultivation_phase_id=req_data["cultivation_phase_id"],
                            soil_type_id=req_data["soil_type_id"],
                            irrigation_method_id=req_data["irrigation_method_id"],
                            water_type_id=req_data["water_type_id"],
                            water_source_id=req_data["water_source_id"],
                        )
                        sowing_obj.save()
                        data["message"] = "transpalnted saved success"

                    else:
                        data["message"] = "sowing already saved"

                else:
                    data["message"] = "No nursery is registered"
            else:
                sowing_obj = Sowing(
                        farmer_id=req_data["farmer_id"],
                        crop_id=req_data["crop_id"],
                        sowing_date=req_data["sowing_date_proposed"],
                        area=req_data["area"],
                        season_id=req_data["season_id"],
                        state_id=req_data["state_id"],
                        district_id=req_data["district_id"],
                        taluk_id=req_data["taluk_id"],
                        hobli_id=req_data["hobli_id"],
                        village_id=req_data["village_id"],
                        cultivation_phase_id=req_data["cultivation_phase_id"],
                        soil_type_id=req_data["soil_type_id"],
                        irrigation_method_id=req_data["irrigation_method_id"],
                        water_type_id=req_data["water_type_id"],
                        water_source_id=req_data["water_source_id"],
                )
                sowing_obj.save()
                data["message"] = "sowing saved success"
        else:
            data["message"] = "sowing already saved"

    else:
        Sowing.objects.filter(id=req_data["sowing_id"]).update(
            farmer_id=req_data["farmer_id"],
            crop_id=req_data["crop_id"],
            sowing_date=req_data["sowing_date_proposed"],
            area=req_data["area"],
            season_id=req_data["season_id"],
            state_id=req_data["state_id"],
            district_id=req_data["district_id"],
            taluk_id=req_data["taluk_id"],
            hobli_id=req_data["hobli_id"],
            village_id=req_data["village_id"],
            cultivation_phase_id=req_data["cultivation_phase_id"],
            soil_type_id=req_data["soil_type_id"],
            irrigation_method_id=req_data["irrigation_method_id"],
            water_source_id=req_data["water_source_id"],
        )
        data["message"] = "Updated"
    return Response(data, status=status.HTTP_200_OK)


def get_expected_yield(sowing_id):
    data = 0
    if AnswerLogForTextInput.objects.filter(sowing_id=sowing_id,question_id=35).exists():
        if AnswerLogForTextInput.objects.filter(sowing_id=sowing_id, question_id=36).exists():
            if AnswerLogForTextInput.objects.filter(sowing_id=sowing_id, question_id=37).exists():
                print(int(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=35).answer))
                print(int(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=36).answer))
                print(type(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=37).answer))
                data = (int(float(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=35).answer))* int(float(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=36).answer))* int(float(AnswerLogForTextInput.objects.get(sowing_id=sowing_id, question_id=37).answer)))
    return data


def get_harvest_count(sowing_id):
    if Harvest.objects.filter(sowing_id=sowing_id).exists():
        count = Harvest.objects.filter(sowing_id=sowing_id).count()
    else:
        count = 0
    return count

def check_for_completed_of_gap(sowing_id, season_id):

    if SeasonBasedGap.objects.filter(season=season_id).exists():
        print('exists')
        season_based_gap_count = SeasonBasedGap.objects.filter(season=season_id).count()
        if SeasonBasesFarmerGpaLog.objects.filter(sowing_id=sowing_id).exists():
            print('have log')
            completed_count = SeasonBasesFarmerGpaLog.objects.filter(sowing_id=sowing_id).count()
            if completed_count == season_based_gap_count:
                return 1
            else:
                return 2
        else:
            return 2
    else:
        return 3



@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_sowings(request):
    farmer_id = request.data["farmer_id"]
    season_id = get_active_season_id()
    print(farmer_id)
    if Sowing.objects.filter(farmer_id=farmer_id, season_id=season_id).exists():
        sowing_values = Sowing.objects.filter(farmer_id=farmer_id, season_id=season_id).values_list( "id", "farmer_id", "crop_id", "crop__name", "cultivation_phase_id", "cultivation_phase__name", "sowing_date", "area", "season", "season__name", "water_source_id", "water_source__name", "water_type_id", "water_type__name", "soil_type", "soil_type__name", "irrigation_method", "irrigation_method__name", "state", "district", "taluk", "hobli", "village", "latitude", "longitude", "is_verified", "is_active", "is_geo_fencing_is_automatic", "geo_fence_done_on", "area_calculated_via_geo_fencing")
        sowing_columns = [ "id", "farmer_id", "crop_id", "crop_name", "cultivation_phase_id", "cultivation_phase_name", "sowing_date", "area", "season_id", "season_name", "water_source_id", "water_source_name", "water_type_id", "water_type_name", "soil_type_id", "soil_type_name", "irrigation_method_id", "irrigation_method_name", "state_id", "district_id", "taluk_id", "hobli_id", "village_id", "latitude", "longitude", "is_verified", "is_active", "is_geo_fencing_is_automatic", "geo_fence_done_on", "area_calculated",]
        sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)

        harvest_values = (Harvest.objects.filter(sowing__cultivation_phase_id=2,sowing__season_id=season_id,sowing__farmer_id=farmer_id,).order_by("sowing_id", "date_of_harvest").values_list("sowing_id","sowing__farmer_id","date_of_harvest","value","unit__name","sowing__sowing_date",))
        harvest_columns = ["sowing_id","h_farmer_id","date_of_harvest","value","unit","h_sowing_date",]
        harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)
        if Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id, sowing__farmer_id=farmer_id).exists():
            harvest_df["harvest_days"] = (harvest_df["date_of_harvest"] - harvest_df["h_sowing_date"]).dt.days
        merged_df = pd.merge(sowing_df, harvest_df, left_on="id", right_on="sowing_id", how="left")
        merged_df["harvest_value"] = merged_df.groupby(["id"])["value"].transform("sum")
        merged_df = merged_df.drop_duplicates(subset="id", keep="first", inplace=False)
        merged_df["expected_yield"] = merged_df.apply(lambda x: get_expected_yield(x["id"]), axis=1)
        merged_df["harvest_count"] = merged_df.apply(lambda x: get_harvest_count(x["id"]), axis=1)
        merged_df["completed_gap_status"] = merged_df.apply(lambda x: check_for_completed_of_gap(x["id"], season_id), axis=1)

        merged_df = merged_df.fillna(0)
        data = merged_df.to_dict("r")
    else:
        data = []
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def register_water_resource(request):
    data = {}
    req_data = request.data["form_data"]
    if req_data["water_resource_id"] == None:
        water_resource_obj = WaterResource(
            farmer_id=req_data["farmer_id"],
            irrigation_method_id=req_data["irrigation_method_id"],
            water_type_id=req_data["water_type_id"],
            water_source_id=req_data["water_source_id"],
            created_by=request.user,
        )
        water_resource_obj.save()

        data["message"] = "water resource saved success"
    else:
        WaterResource.objects.filter(id=req_data["water_resource_id"]).update(
            farmer_id=req_data["farmer_id"],
            irrigation_method_id=req_data["irrigation_method_id"],
            water_type_id=req_data["water_type_id"],
            water_source_id=req_data["water_source_id"],
        )
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_water_resources(request):
    farmer_id = request.data["farmer_id"]
    water_resource_values = WaterResource.objects.filter(farmer_id=farmer_id).values_list("id","farmer_id","water_source_id","water_source__name","water_type_id","water_type__name","irrigation_method_id","irrigation_method__name","latitude","longitude","is_verified",)
    water_resource_coulmns = ["id","farmer_id","water_source_id","water_source_name","water_type_id","water_type_name","irrigation_method_id","irrigation_method_name","latitude","longitude","is_verified",]
    water_resource_df = pd.DataFrame(list(water_resource_values), columns=water_resource_coulmns)
    return Response(water_resource_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def verify_sowing(request):
    print(request.data)
    sowing_obj = Sowing.objects.get(id=request.data["sowing_id"])
    sowing_obj.is_verified = True
    sowing_obj.verified_by = request.user
    sowing_obj.verified_on = datetime.datetime.now()
    sowing_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def verify_water_resource(request):
    print(request.data)
    water_obj = WaterResource.objects.get(id=request.data["water_resource_id"])
    water_obj.is_verified = True
    water_obj.verified_by = request.user
    water_obj.verified_on = datetime.datetime.now()
    water_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def update_geo_location(request):
    print(request.data)
    purpose = request.data["purpose"]
    if purpose == "Crops":
        sowing_obj = Sowing.objects.get(id=request.data["source_id"])
        sowing_obj.latitude = request.data["latitude"]
        sowing_obj.longitude = request.data["longitude"]
        sowing_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif purpose == "Water Resource":
        water_resource_obj = WaterResource.objects.get(id=request.data["source_id"])
        water_resource_obj.latitude = request.data["latitude"]
        water_resource_obj.longitude = request.data["longitude"]
        water_resource_obj.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_geo_fence_data_for_sowing(request):
    print(request.data["sowing_or_water_id"])
    if request.data["purpose"] == "Crops":
        final_dict = {}
        if SowingBoundary.objects.filter(
                sowing_id=request.data["sowing_or_water_id"]
        ).exists():
            sowing_boundary_obj = SowingBoundary.objects.filter(
                sowing_id=request.data["sowing_or_water_id"]
            )
            sowing_boundary_list = list(
                sowing_boundary_obj.values_list("latitude", "longitude")
            )
            sowing_boundary_column = ["lat", "lng"]
            sowing_boundary_df = pd.DataFrame(
                sowing_boundary_list, columns=sowing_boundary_column
            )
            final_dict["is_data_available"] = True
            final_dict["gps_data"] = sowing_boundary_df.to_dict("r")
            return Response(data=final_dict, status=status.HTTP_200_OK)
        else:
            final_dict["is_data_available"] = False
            return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def upload_geo_fence_gps_data(request):
    print(request.data)
    if request.data["purpose"] == "Crops":
        sowing_id = request.data["sowing_or_water_id"]
        if SowingBoundary.objects.filter(sowing_id=sowing_id).exists():
            SowingBoundary.objects.filter(sowing_id=sowing_id).delete()
        for boundary in request.data["gps_data"]:
            obj = SowingBoundary(
                sowing_id=sowing_id,
                latitude=boundary["lat"],
                longitude=boundary["lng"],
                timestamp=datetime.datetime.now(),
            )
            obj.save()
            print("GEo fence data updated")
        farmer_sowing = Sowing.objects.get(id=sowing_id)
        farmer_sowing.area_calculated_via_geo_fencing = request.data["calculated_area"]
        farmer_sowing.is_geo_fencing_is_automatic = True
        farmer_sowing.geo_fence_done_on = datetime.datetime.now().date()
        farmer_sowing.save()
        print("Famer scheme data updated")
        return Response(status=status.HTTP_200_OK)


def create_complete_image(encoded_image, file_name=None):
    print("Convert string to image file(Decode)")
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split("base64,")
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + ".jpeg")


@api_view(["POST"])
def save_sowing_images(request):
    print(request.data)
    for image in request.data["images"]:
        complete_image = create_complete_image(image)
        sowing_image_obj = SowingImage(
            sowing_id=request.data["sowing_id"],
            image=complete_image,
            uploaded_by=request.user,
            notes=request.data["notes"],
        )
        sowing_image_obj.save()
        print("saved")
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_crops(request):
    crop_list = []
    for crop in Crop.objects.all():
        tem_dict = {"id": crop.id, "name": crop.name}
        crop_list.append(tem_dict)
    return Response(data=crop_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_sowing_images(request):
    print(request.data)
    sowing_id = request.data["sowing_id"]
    if SowingImage.objects.filter(sowing_id=sowing_id).exists():
        image_objs = SowingImage.objects.filter(sowing_id=sowing_id)
        image_list = []
        for image in image_objs:
            image_dict = {}
            try:
                with open("static/media/" + str(image.image), "rb") as image_file:
                    encoded_image1 = b64encode(image_file.read())
                    image_dict["image"] = "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
            except Exception as err:
                print(err)
                pass
            if image.notes != None:
                image_dict["notes"] = image.notes
            else:
                image_dict["notes"] = ""
            image_dict["id"] = image.id
            image_list.append(image_dict)
    else:
        image_list = "no_image"
    return Response(image_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_farmer_data_for_mobile_app(request):
    print(request.data)
    business_id = Business.objects.filter()[0].id
    data = serve_dynamic_question(request.data["section_name"], business_id)
    return Response(data=data, status=status.HTTP_200_OK)


def serve_dynamic_question(section_name, business_id):
    unique_Sub_section_ids = QuestionSubSection.objects.filter(
        business_id=business_id, section__name=section_name
    ).values_list("id", flat=True)

    # get question group by wise
    question_list = []
    questions = Question.objects.filter(subsection_id__in=unique_Sub_section_ids)
    sub_sections = QuestionSubSection.objects.filter(id__in=unique_Sub_section_ids)
    for sub_section in sub_sections:
        # print('with in groupby loop')
        temp_sub_section = QuestionSubSectionSerializerSimple(sub_section).data
        temp_sub_section["questions"] = []
        # temp_sub_section['questions'] = OrderedDict()
        sub_section_questions = questions.filter(subsection=sub_section).order_by(
            "ordinal"
        )
        for question in sub_section_questions:
            # print('with in question loop')
            question_dict = QuestionSerializer(question).data
            question_dict["sub_question_ids"] = QuestionConfig.objects.filter(
                depends_on_question=question
            ).values_list("question_id", flat=True)
            question_dict["default_answers"] = []
            # question_dict['default_answers'] = {}
            defalult_answers = question.questionanswerchoice_set.all().order_by(
                "ordinal"
            )
            for defalult_answer in defalult_answers:
                # print(defalult_answer.id)
                # print('with in default answer loop')
                temp_default_answer = QuestionsAnswerSerializer(defalult_answer).data
                question_dict["default_answers"].append(temp_default_answer)
                # question_dict['default_answers'][temp_default_answer['id']] = temp_default_answer
            try:
                question_dict["configuration"] = QuestionConfigSerializer(
                    question.questionconfig
                ).data
                if question.questionconfig.depends_on_question is not None:
                    question_dict["configuration"][
                        "parent_question_type"
                    ] = (
                        question.questionconfig.depends_on_question.questionconfig.question_type.name
                    )
            except Exception as e:
                print(e)
            question_dict["validators"] = question.questionvalidationconfig_set.all()
            temp_sub_section["questions"].append(question_dict)
            # temp_sub_section['questions'][str('id-' + str(question_dict['id']))] = question_dict

        question_list.append(temp_sub_section)
    return question_list


@api_view(["POST"])
def serve_farmer_dynamic_questions_answers(request):
    """
    serve dynamic question id and its answer based on farmer
    :param request:
    :return:
    """
    try:
        print("GATHER ANSWERS FUNCTION")
        data = {"text": {}, "dropdown": {}, "radio": {}, "number": {}, "checkbox": {}}
        id = request.data["id"]
        print(request.data)
        print(id)
        print(request.data["for"])

        if request.data["for"] == "farmer's":
            print("ANSWER GATHER FOR FARMER")
            text_answers = AnswerLogForTextInput.objects.filter(
                farmer_id=id, is_current=True
            )
            number_answers = AnswerLogForNumberInput.objects.filter(
                farmer_id=id, is_current=True
            )
            radio_answers = AnswerLogForRadio.objects.filter(
                farmer_id=id, is_current=True
            )
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                farmer_id=id, is_current=True
            )
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                farmer_id=id, is_current=True
            )

        if request.data["for"] == "sowing":
            print("ANSWER GATHER FOR SOWING")
            text_answers = AnswerLogForTextInput.objects.filter(
                sowing_id=id, is_current=True
            )
            number_answers = AnswerLogForNumberInput.objects.filter(
                sowing_id=id, is_current=True
            )
            radio_answers = AnswerLogForRadio.objects.filter(
                sowing_id=id, is_current=True
            )
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                sowing_id=id, is_current=True
            )
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                sowing_id=id, is_current=True
            )

        if request.data["for"] == "farmer_field":
            print("ANSWER GATHER FOR FARMER FIELD")
            text_answers = AnswerLogForTextInput.objects.filter(
                farmer_field_id=id, is_current=True
            )
            number_answers = AnswerLogForNumberInput.objects.filter(
                farmer_field_id=id, is_current=True
            )
            radio_answers = AnswerLogForRadio.objects.filter(
                farmer_field_id=id, is_current=True
            )
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                farmer_field_id=id, is_current=True
            )
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                farmer_field_id=id, is_current=True
            )

        if request.data["for"] == "water":
            print("ANSWER GATHER FOR WATER RESOURCE")
            text_answers = AnswerLogForTextInput.objects.filter(
                water_resource_id=id, is_current=True
            )
            number_answers = AnswerLogForNumberInput.objects.filter(
                water_resource_id=id, is_current=True
            )
            radio_answers = AnswerLogForRadio.objects.filter(
                water_resource_id=id, is_current=True
            )
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                water_resource_id=id, is_current=True
            )
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                water_resource_id=id, is_current=True
            )

        if request.data["for"] == "scheme":
            print("ANSWER GATHER FOR WATER RESOURCE")
            text_answers = AnswerLogForTextInput.objects.filter(
                farmer_scheme_map_id=id, is_current=True
            )
            number_answers = AnswerLogForNumberInput.objects.filter(
                farmer_scheme_map_id=id, is_current=True
            )
            radio_answers = AnswerLogForRadio.objects.filter(
                farmer_scheme_map_id=id, is_current=True
            )
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                farmer_scheme_map_id=id, is_current=True
            )
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                farmer_scheme_map_id=id, is_current=True
            )

        # text answers
        print(text_answers)
        text_answer_values = text_answers.values_list("question", "answer")
        text_answer_columns = ["id", "answer"]
        text_df = pd.DataFrame(list(text_answer_values), columns=text_answer_columns)
        data["text"] = pd.Series(text_df.answer.values, index=text_df.id).to_dict()

        # DROPDOWN
        dropdown_answer_values = dropdown_answers.values_list("question", "answer")
        dropdown_answer_columns = ["id", "answer"]
        dropdown_df = pd.DataFrame(
            list(dropdown_answer_values), columns=dropdown_answer_columns
        )
        data["dropdown"] = pd.Series(
            dropdown_df.answer.values, index=dropdown_df.id
        ).to_dict()

        # RADIO
        radio_answer_values = radio_answers.values_list("question", "answer")
        radio_answer_columns = ["id", "answer"]
        radio_df = pd.DataFrame(list(radio_answer_values), columns=radio_answer_columns)
        data["radio"] = pd.Series(radio_df.answer.values, index=radio_df.id).to_dict()

        # NUMBER
        number_answer_values = number_answers.values_list("question", "answer")
        number_answer_columns = ["id", "answer"]
        number_df = pd.DataFrame(
            list(number_answer_values), columns=number_answer_columns
        )
        data["number"] = pd.Series(
            number_df.answer.values, index=number_df.id
        ).to_dict()

        # CHECKBOX
        checkbox_answer_values = checkbox_answers.values_list("question", "answer")
        checkbox_answer_columns = ["id", "answer"]
        checkbox_df = pd.DataFrame(
            list(checkbox_answer_values), columns=checkbox_answer_columns
        )
        checkbox_df = checkbox_df.groupby("id")["answer"].apply(list)
        print(checkbox_df)
        # data['checkbox'] = checkbox_df.groupby('id').apply(lambda x: x.set_index('id').to_dict('r')).to_list()
        data["checkbox"] = checkbox_df.to_dict()
        return Response(data=data, status=status.HTTP_200_OK)

    except Exception as e:
        print("ERROR - {}".format(e))
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
def save_dynamic_questions_answers(request):
    print(request.data)
    # farmer_id = request.data['id']
    print(request.data["text"])
    farmer_id = None
    sowing_id = None
    water_resource_id = None
    if request.data["for"] == "farmer's":
        farmer_id = request.data["id"]
        print("FOR FARMER")
    elif request.data["for"] == "sowing":
        print("FOR SOWING")
        sowing_id = request.data["id"]
        farmer_id = Sowing.objects.get(id=request.data["id"]).farmer_id
    elif request.data["for"] == "water":
        print("FOR WATER RESOURCE")
        water_resource_id = request.data["id"]
        farmer_id = WaterResource.objects.get(id=request.data["id"]).farmer_id

    # save text type answers
    save_dynamic_question_text_answer(
        request.data["text"],
        request.data["for"],
        request.user.id,
        farmer_id,
        sowing_id,
        water_resource_id,
    )
    # save_dynamic_question_number_answer(request.data['checkbox'], farmer_id)

    # # save number type answers
    save_dynamic_question_number_answer(
        request.data["number"],
        request.data["for"],
        request.user.id,
        farmer_id,
        sowing_id,
        water_resource_id,
    )
    #
    # # save checkbox type answers
    save_dynamic_question_checkbox_answer(
        request.data["checkbox"],
        request.data["for"],
        request.user.id,
        farmer_id,
        sowing_id,
        water_resource_id,
    )
    #
    # # save dropdown type answers
    save_dynamic_question_dropdown_answer(
        request.data["dropdown"],
        request.data["for"],
        request.user.id,
        farmer_id,
        sowing_id,
        water_resource_id,
    )
    #
    # # save radio type answers
    save_dynamic_question_radio_answer(
        request.data["radio"],
        request.data["for"],
        request.user.id,
        farmer_id,
        sowing_id,
        water_resource_id,
    )
    return Response(status=status.HTTP_202_ACCEPTED)


def save_dynamic_question_text_answer(
        question_answers,
        answer_save_for,
        added_by_id,
        farmer_id,
        sowing_id,
        water_resource_id,
):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == "farmer's":

        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(
                    question_id=question_id, farmer_id=farmer_id, is_current=True
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(
                    farmer_id=farmer_id, question_id=question_id, is_current=True
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForTextInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == "sowing":

        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(
                    question_id=question_id,
                    farmer_id=farmer_id,
                    sowing_id=sowing_id,
                    is_current=True,
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                    sowing_id=sowing_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(
                    farmer_id=farmer_id,
                    sowing_id=sowing_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForTextInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                        sowing_id=sowing_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == "water":

        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(
                    question_id=question_id,
                    farmer_id=farmer_id,
                    water_resource_id=water_resource_id,
                    is_current=True,
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(
                    farmer_id=farmer_id,
                    water_resource_id=water_resource_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForTextInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    return True


def save_dynamic_question_number_answer(
        question_answers,
        answer_save_for,
        added_by_id,
        farmer_id,
        sowing_id,
        water_resource_id,
):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == "farmer's":
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(
                    question_id=question_id, farmer_id=farmer_id, is_current=True
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(
                    farmer_id=farmer_id, question_id=question_id, is_current=True
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForNumberInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == "sowing":
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(
                    question_id=question_id,
                    sowing_id=sowing_id,
                    farmer_id=farmer_id,
                    is_current=True,
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                    sowing_id=sowing_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(
                    farmer_id=farmer_id,
                    sowing_id=sowing_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForNumberInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                        sowing_id=sowing_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == "water":
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(
                    question_id=question_id,
                    water_resource_id=water_resource_id,
                    farmer_id=farmer_id,
                    is_current=True,
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(
                    farmer_id=farmer_id,
                    water_resource_id=water_resource_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForNumberInput(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer=answer,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    return True


def save_dynamic_question_radio_answer(
        question_answers,
        answer_save_for,
        added_by_id,
        farmer_id,
        sowing_id,
        water_resource_id,
):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == "sowing":
        print("with in sowing")
        print(question_answers)
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(
                    question_id=question_id, sowing_id=sowing_id, farmer_id=farmer_id
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                    sowing_id=sowing_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(
                    farmer_id=farmer_id,
                    sowing_id=sowing_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForRadio(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        sowing_id=sowing_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    if answer_save_for == "water":
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(
                    question_id=question_id,
                    water_resource_id=water_resource_id,
                    farmer_id=farmer_id,
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(
                    farmer_id=farmer_id,
                    water_resource_id=water_resource_id,
                    question_id=question_id,
                    is_current=True,
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForRadio(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    if answer_save_for == "farmer's":
        for question_id, answer in question_answers.items():
            print("{} - {}".format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(
                    question_id=question_id, farmer_id=farmer_id
            ).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(
                    farmer_id=farmer_id, question_id=question_id, is_current=True
                )

                if question.questionconfig.create_new_answer_row_on_update:
                    # this question want to multiple entry(historical question)

                    # make previous answer as not current
                    previous_answer_obj.is_current = False
                    previous_answer_obj.save()

                    # create new entry for question
                    answer_log_obj = AnswerLogForRadio(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    return True


def save_dynamic_question_checkbox_answer(
        question_answers,
        answer_save_for,
        added_by_id,
        farmer_id,
        sowing_id,
        water_resource_id,
):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == "sowing":
        for question_id, answer_ids in question_answers.items():
            print("{} - {}".format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(
                        farmer_id=farmer_id,
                        sowing_id=sowing_id,
                        question_id=question_id,
                        answer_id=answer_id,
                ).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                        sowing_id=sowing_id,
                    )
                    answer_log_obj.save()

    if answer_save_for == "water":
        for question_id, answer_ids in question_answers.items():
            print("{} - {}".format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(
                        farmer_id=farmer_id,
                        water_resource_id=water_resource_id,
                        question_id=question_id,
                        answer_id=answer_id,
                ).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id,
                    )
                    answer_log_obj.save()

    if answer_save_for == "farmer's":
        for question_id, answer_ids in question_answers.items():
            print("{} - {}".format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(
                        farmer_id=farmer_id, question_id=question_id, answer_id=answer_id
                ).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
    return True


def save_dynamic_question_dropdown_answer(
        question_answers,
        answer_save_for,
        added_by_id,
        farmer_id,
        sowing_id,
        water_resource_id,
):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    for question_id, answer in question_answers.items():
        print("{} - {}".format(question_id, answer))
        try:
            if answer_save_for == "sowing":
                if not AnswerLogForDropDown.objects.filter(
                        question_id=question_id, farmer_id=farmer_id, sowing_id=sowing_id
                ).exists():
                    print("new entry")
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        sowing_id=sowing_id,
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print("already answer logged")
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        sowing_id=sowing_id,
                    )

                    if question.questionconfig.create_new_answer_row_on_update:
                        print("create new entry")
                        # this question want to multiple entry(historical question)

                        # make previous answer as not current
                        previous_answer_obj.is_current = False
                        previous_answer_obj.save()

                        # create new entry for question
                        answer_log_obj = AnswerLogForDropDown(
                            farmer_id=farmer_id,
                            question_id=question_id,
                            answer_id=answer,
                            added_by_id=added_by_id,
                            sowing_id=sowing_id,
                        )
                        answer_log_obj.save()
                    else:
                        print("replace answer")
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

            if answer_save_for == "water":
                if not AnswerLogForDropDown.objects.filter(
                        question_id=question_id,
                        farmer_id=farmer_id,
                        water_resource_id=water_resource_id,
                ).exists():
                    print("new entry")
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id,
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print("already answer logged")
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        water_resource_id=water_resource_id,
                    )

                    if question.questionconfig.create_new_answer_row_on_update:
                        print("create new entry")
                        # this question want to multiple entry(historical question)

                        # make previous answer as not current
                        previous_answer_obj.is_current = False
                        previous_answer_obj.save()

                        # create new entry for question
                        answer_log_obj = AnswerLogForDropDown(
                            farmer_id=farmer_id,
                            question_id=question_id,
                            answer_id=answer,
                            added_by_id=added_by_id,
                            water_resource_id=water_resource_id,
                        )
                        answer_log_obj.save()
                    else:
                        print("replace answer")
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

            if answer_save_for == "farmer's":
                if not AnswerLogForDropDown.objects.filter(
                        question_id=question_id, farmer_id=farmer_id
                ).exists():
                    print("new entry")
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print("already answer logged")
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(
                        farmer_id=farmer_id, question_id=question_id
                    )

                    if question.questionconfig.create_new_answer_row_on_update:
                        print("create new entry")
                        # this question want to multiple entry(historical question)

                        # make previous answer as not current
                        previous_answer_obj.is_current = False
                        previous_answer_obj.save()

                        # create new entry for question
                        answer_log_obj = AnswerLogForDropDown(
                            farmer_id=farmer_id,
                            question_id=question_id,
                            answer_id=answer,
                            added_by_id=added_by_id,
                        )
                        answer_log_obj.save()
                    else:
                        print("replace answer")
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

        except Exception as error:
            print("dropdown ANSWER SAVE ERROR {}".format(error))
    return True


@api_view(["POST"])
def remove_sowing_images(request):
    SowingImage.objects.filter(id=request.data["sowing_image_id"]).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def save_bank(request):
    req_data = request.data["form_data"]
    if not 'farmer_id' in request.data:
        farmer_id = request.data['form_data']['farmer_id']
    else:
        farmer_id = request.data['farmer_id']
    req_data = request.data['form_data']

    if not Bank.objects.filter(ifsc_code=req_data["ifsc_code"]).exists():
        bank_obj = Bank(
                name=req_data["bank_name"],
                branch=req_data["branch_name"],
                ifsc_code=req_data["ifsc_code"],
                micr_code=req_data["micr_code"]
                )
        bank_obj.save()
    if req_data["bank_id"] == None:
        if not FarmerBankDetails.objects.filter(account_number=req_data["account_number"]).exists():
            farmer_bank_details = FarmerBankDetails(
                farmer_id=farmer_id,
                bank=req_data["bank_name"],
                branch=req_data["branch_name"],
                ifsc_code=req_data["ifsc_code"],
                micr_code=req_data["micr_code"],
                account_holder_name=req_data["account_holder_name"],
                account_number=req_data["account_number"],
                created_by=request.user,
                modified_by=request.user,
            )
            print(request.user)
            if 'remarks' in req_data:
                farmer_bank_details.remarks = req_data['remarks']
            if FarmerBankDetails.objects.filter(farmer_id=req_data["farmer_id"]).exists():
                farmer_bank_details.is_primary = False
            if "passbook_image" in request.data:
                farmer_bank_details.bank_passbook_document = create_complete_image(request.data["passbook_image"])
            farmer_bank_details.save()
            print("saved")
    else:
        FarmerBankDetails.objects.filter(id=req_data["bank_id"]).update(
            farmer_id=farmer_id,
            bank=req_data["bank_name"],
            branch=req_data["branch_name"],
            ifsc_code=req_data["ifsc_code"],
            micr_code=req_data["micr_code"],
            account_holder_name=req_data["account_holder_name"],
            account_number=req_data["account_number"],
            created_by=request.user,
            modified_by=request.user,
        )

        if 'remarks' in req_data:
             FarmerBankDetails.objects.filter(id=req_data["bank_id"]).update(
                remarks = req_data['remarks'])

        if "passbook_image" in request.data:
            FarmerBankDetails.objects.filter(id=req_data["bank_id"]).update(
                bank_passbook_document=create_complete_image(
                    request.data["passbook_image"]
                )
            )

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_bank(request):
    bank_values = (FarmerBankDetails.objects.filter(farmer_id=request.data["farmer_id"], is_active=True).order_by("-is_primary") .values_list( "id", "farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name", "account_number", "bank_passbook_document", 'farmer__aadhaar_document', "is_primary", "remarks"))
    bank_columns = [ "id", "farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name", "account_number", "bank_passbook_document","aadhar_img", "is_primary", "remarks"]
    bank_df = pd.DataFrame(list(bank_values), columns=bank_columns)
    for index, row in bank_df.iterrows():
        if row["bank_passbook_document"] != None:
            try:
                with open("static/media/" + str(row["bank_passbook_document"]), "rb") as image_file:
                    encoded_image1 = b64encode(image_file.read())
                    bank_df.at[index, "image"] = "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
                    print('passbook_img_done')
            except Exception as err:
                print(err)
                print('erorr')
                bank_df.at[index, "image"] = 0
                pass
        if row["aadhar_img"] != None:
            try:
                with open("static/media/" + str(row["aadhar_img"]), "rb") as image_file1:
                    encoded_image1 = b64encode(image_file1.read())
                    bank_df.at[index, "aadhar_image"] = "data:aadhar_image/jpeg;base64," + encoded_image1.decode("utf-8")
                    print('aadhar_img_done')
            except Exception as err:
                print(err)
                print('erorr')
                bank_df.at[index, "aadhar_image"] = 0
                pass
        else:
            print('No_img')
            bank_df.at[index, "aadhar_image"] = 0
    bank_df = bank_df.fillna(0)
    return Response(bank_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def remove_bank(request):
    FarmerBankDetails.objects.filter(id=request.data["id"]).update(is_active=False)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_lat_lng_for_sowing(request):
    data_dict = {}
    if request.data["purpose"] == "Crops":
        sowing_obj = Sowing.objects.get(id=request.data["sowing_or_water_id"])
        data_dict["latitude"] = sowing_obj.latitude
        data_dict["longitude"] = sowing_obj.longitude
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif request.data["purpose"] == "Water Resource":
        water_resource_obj = WaterResource.objects.get(
            id=request.data["sowing_or_water_id"]
        )
        data_dict["latitude"] = water_resource_obj.latitude
        data_dict["longitude"] = water_resource_obj.longitude
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_all_hobli(request):
    data_list = []
    for hobli in Hobli.objects.all():
        data_dict = {"id": hobli.id, "name": hobli.name}
        data_list.append(data_dict)
    return Response(data=data_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_state_district_based_on_hobli(request):
    hobli_obj = Hobli.objects.get(id=request.data["hobli_id"])
    data_dict = {"state": {}, "district": {}, "taluk": {}, "hobli": {}}
    data_dict["taluk"]["id"] = hobli_obj.taluk.id
    data_dict["taluk"]["name"] = hobli_obj.taluk.name
    data_dict["district"]["id"] = hobli_obj.taluk.district.id
    data_dict["district"]["name"] = hobli_obj.taluk.district.name
    data_dict["state"]["id"] = hobli_obj.taluk.district.state.id
    data_dict["state"]["name"] = hobli_obj.taluk.district.state.name
    data_dict["hobli"]["name"] = hobli_obj.name
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_based_on_cluser(request):
    season_id = get_active_season_id()
    user_list = list(UserClusterMap.objects.filter(cluster_id=request.data["cluster_id"], season_id=get_active_season_id()).values_list("user", flat=True))
    user_profile_obj = UserProfile.objects.filter(user_id__in=user_list, user_type_id=6)
    user_profile_list = list(user_profile_obj.values_list("user", "user__first_name"))
    user_profile_column = ["id", "name"]
    user_df = pd.DataFrame(user_profile_list, columns=user_profile_column)
    return Response(data=user_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def upload_user_profile_picture(request):
    if FarmerImage.objects.filter(farmer_id=request.data["id"]).exists():

        farmer_image_obj = FarmerImage.objects.get(farmer_id=request.data["id"])
        complete_image = create_complete_image(request.data["picture"])
        print("***********************decoded********************")
        print(complete_image)
        print("**************************************************")
        farmer_image_obj.image = complete_image
        farmer_image_obj.save()
        return Response(status=status.HTTP_200_OK)
    else:
        new_farmer_image_obj = FarmerImage(
            farmer_id=request.data["id"], uploaded_by_id=request.user.id
        )
        complete_image = create_complete_image(request.data["picture"])
        user_profile = UserProfile.objects.get(user=request.user)
        new_farmer_image_obj.image = complete_image
        new_farmer_image_obj.save()

        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def get_farmer_image(request):
    if FarmerImage.objects.filter(farmer_id=request.data["farmer_id"]).exists():
        farmer_image = FarmerImage.objects.get(farmer_id=request.data["farmer_id"])
        try:
            image_path = "static/media/" + str(farmer_image.image)
            print(image_path)
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                return Response(
                    {
                        "farmer_image": "data:image/jpeg;base64,"
                                        + encoded_image.decode("utf-8")
                    }
                )

        except Exception as error:
            print(error)
            return Response(error, status=status.HTTP_409_CONFLICT)

    else:
        error_message = {"error": "Image Not Available"}
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def check_farmer_exists(request):
    if Farmer.objects.filter(mobile=request.data["mobile_number"]).exists():
        return Response(data=True, status=status.HTTP_200_OK)
    else:
        return Response(data=False, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_blood_groups(request):
    blood_group_list = list(BloodGroup.objects.all().values_list("id", "name"))
    blood_group_columns = ["id", "name"]
    blood_group_df = pd.DataFrame(blood_group_list, columns=blood_group_columns)
    return Response(data=blood_group_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["GET"])
def get_cluster_based_agents(request):
    cluster_based_agent = {}
    agent_user_ids = list(
        UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
    )
    for cluster in UserClusterMap.objects.filter(user_id__in=agent_user_ids):
        if cluster.cluster.id not in cluster_based_agent:
            cluster_based_agent[cluster.cluster.id] = []

        cluster_based_agent[cluster.cluster.id].append(
            {
                "name": cluster.user.first_name,
                "id": cluster.user.id,
                "first_name": cluster.user.first_name,
                "last_name": cluster.user.last_name,
                "user_id": cluster.user.id,
            }
        )
    # print(cluster_based_agent)
    return Response(cluster_based_agent, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_cluster_and_agent_for_farmer(request):
    # updating farmer info
    print(request.data)
    if Farmer.objects.filter(mobile=request.data['mobile']).exclude(id=request.data['farmer_id']).exists():
        print('farmer exists')
        data['message'] = 'Farmer already exists with the mobile number'
        data['status'] = False
        return Response(data, status=status.HTTP_200_OK)
    else:
        # farmer cluster with season maping
        print(request.data)
        Farmer.objects.filter(id=request.data['farmer_id']).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            mobile=request.data['mobile'],
            hobli_id=request.data['hobli_id'],
            taluk_id=request.data['taluk_id'],
            district_id=request.data['district_id'],
            state_id=request.data['state_id'],
            village_id=request.data['village_id'],
        )
        if request.data["officer_id"] == "same_user":
            officer_id = request.user.id
        else:
            officer_id = request.data["officer_id"]
        season_id = get_active_season_id()

        if FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id=request.data["farmer_id"]).exists():
            farmer_cluster_obj = FarmerClusterSeasonMap.objects.get(season_id=season_id, farmer_id=request.data["farmer_id"])
            farmer_cluster_obj.cluster_id = request.data["cluster_id"]
            farmer_cluster_obj.modified_by = request.user
            farmer_cluster_obj.seasonal_farmer_code = generate_farmer_code(request.data["cluster_id"], request.data["agent_id"], officer_id, season_id)
            farmer_cluster_obj.save()
        else:
            farmer_cluster_obj = FarmerClusterSeasonMap(
                season_id=season_id,
                farmer_id=request.data["farmer_id"],
                cluster_id=request.data["cluster_id"],
                seasonal_farmer_code=generate_farmer_code(request.data["cluster_id"], request.data["agent_id"], officer_id, season_id),
                modified_by=request.user)
            print("created")
            farmer_cluster_obj.save()

        # farmer maping with agent
        if AgentFarmerMap.objects.filter(farmer__season_id=season_id, farmer=farmer_cluster_obj).exists():
            AgentFarmerMap.objects.filter(farmer__season_id=season_id, farmer=farmer_cluster_obj).update(agent_id=request.data["agent_id"])
            print("exists")
        else:
            AgentFarmerMap.objects.create(farmer=farmer_cluster_obj,agent_id=request.data["agent_id"])
            print("created")
        # farmer_maping_with_role
        if UserFarmerMap.objects.filter(farmer__season_id=season_id, farmer=farmer_cluster_obj).exists():
            UserFarmerMap.objects.filter(farmer__season_id=season_id, farmer=farmer_cluster_obj).update(officer_id=officer_id)
            print("exists")
        else:
            UserFarmerMap.objects.create(farmer=farmer_cluster_obj,officer_id=officer_id,)
            print("created")

        data = {
            "agent_name": AgentFarmerMap.objects.get(farmer__season_id=season_id, farmer=farmer_cluster_obj).agent.first_name,
            "cluster_name": FarmerClusterSeasonMap.objects.get(season_id=season_id, farmer_id=request.data["farmer_id"]).cluster.name,
            "data": True
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_role_list(request):
    print("data")
    positions_users = list(PositionPositionUserMap.objects.all().values_list("user_id", flat=True))
    user_ids = list(UserProfile.objects.filter(user_id__in=positions_users, user_type_id=5).values_list("user_id", flat=True))
    user_list = list(User.objects.filter(id__in=user_ids).order_by("username").values_list("id", "first_name", "username"))
    user_column = ["id", "name", "username"]
    user_df = pd.DataFrame(user_list, columns=user_column)
    return Response(user_df.to_dict("r"), status=status.HTTP_200_OK)


# serve_unassinged_farmer list
@api_view(["GET"])
def serve_unassigned_farmers(request):
    active_season_id= get_active_season_id()
    assigned_farmer_ids = list(UserFarmerMap.objects.filter(farmer__season_id=active_season_id).values_list("farmer__farmer_id", flat=True))
    print(len(assigned_farmer_ids))
    farmer_objs = Farmer.objects.exclude(id__in=assigned_farmer_ids).order_by("first_name")
    farmer_values = farmer_objs.values_list( "id", "first_name", "last_name", "code", "mobile", "alternate_mobile", "email", "address", "state_id", "state__name", "hobli_id", "hobli__name", "pincode", "aadhaar_number", "cultivated_for_ccgb_since", "cluster__name", "cluster_id", "latitude", "longitude", "district_id", "district__name", "taluk_id", "taluk__name", "village_id", "village__name", "latitude", "longitude",)
    farmer_columns = ["farmer_id", "first_name", "last_name", "code", "mobile", "alternate_mobile", "email", "street", "state_id", "state__name", "hobli_id", "hobli_name", "pincode", "aadhaar_number", "collaborated_with_company_on", "cluster_name", "cluster_id", "latitude", "longitude", "district_id", "district_name", "taluk_id", "taluk_name", "village_id", "village_name", "latitude", "longitude",]
    farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)

    farmer_cluster_map_values = UserFarmerMap.objects.filter().values_list("id", "farmer__farmer_id")
    farmer_cluster_columns = ["farmer_cluster_map_id", "farmer_id"]
    farmer_cluster_df = pd.DataFrame(list(farmer_cluster_map_values), columns=farmer_cluster_columns)

    agent_cluster_map_values = AgentFarmerMap.objects.filter().values_list("id","farmer__farmer_id","agent__first_name","farmer__season__name","agent_id",)
    agent_cluster_columns = ["id","farmer_id","agent_first_name","season_name","agent_id",]
    agent_cluster_df = pd.DataFrame(list(agent_cluster_map_values), columns=agent_cluster_columns)

    agent_user_profile_values = UserProfile.objects.filter(user_type_id=6).values_list("id", "user_id", "mobile")
    agent_user_profile_columns = ["id", "user_id", "agent_mobile"]
    agent_user_profile_df = pd.DataFrame(list(agent_user_profile_values), columns=agent_user_profile_columns)
    user_profile_dict = pd.merge(agent_cluster_df,agent_user_profile_df,left_on="agent_id",right_on="user_id",how="left",)

    merged_df = pd.merge(farmer_df,user_profile_dict,left_on="farmer_id",right_on="farmer_id",how="left",)
    farmer_cluster_merged_df = pd.merge( merged_df, farmer_cluster_df, left_on="farmer_id", right_on="farmer_id", how="left",    )
    final_df = farmer_cluster_merged_df.fillna("")
    final_df = final_df.to_dict("r")
    return Response(data=final_df, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_role_employee_list(request):
    position_values = Position.objects.all().values_list("id", "name")
    position_columns = ["position_id", "position_name"]
    position_df = pd.DataFrame(list(position_values), columns=position_columns)
    position_position_user_map_values = (PositionPositionUserMap.objects.all().values_list("id", "user_id", "user__first_name", "position_id"))
    position_position_user_map_columns = ["position_position_user_map_id","role_user_id","role_first_name","position_id",]
    position_position_user_map_df = pd.DataFrame(list(position_position_user_map_values),columns=position_position_user_map_columns,)
    position_man_user_map_values = PositionManUserMap.objects.all().values_list("id", "position_user_map_id", "user_id", "user__first_name")
    position_man_user_map_columns = ["position_man_user_map","position_position_user_map_id","officer_user_id","officer_user_first_name",]
    position_man_user_map_df = pd.DataFrame(list(position_man_user_map_values), columns=position_man_user_map_columns)
    merged_df = pd.merge(position_df,position_position_user_map_df,left_on="position_id",right_on="position_id",how="left",)
    final_df = pd.merge(merged_df,position_man_user_map_df,left_on="position_position_user_map_id",right_on="position_position_user_map_id",how="left",)
    final_df = final_df.fillna("-")
    return Response(data=final_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_employee_list(request):
    position_users = list(
        PositionPositionUserMap.objects.all().values_list("user_id", flat=True)
    )
    user_list = list(
        UserProfile.objects.filter(user_type_id__in=[1, 2, 3, 4, 5, 9, 10])
            .exclude(user_id__in=position_users)
            .values_list("id", "user_id", "user__first_name")
    )
    user_column = ["id", "user_id", "name"]
    user_df = pd.DataFrame(user_list, columns=user_column)
    return Response(data=user_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def check_for_exists_of_role(request):
    if PositionManUserMap.objects.filter(user_id=request.data["employee_id"]).exists():
        name = PositionManUserMap.objects.get(
            user_id=request.data["employee_id"]
        ).position_user_map.position.name
    else:
        name = "new"
    return Response(data=name, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_position(request):
    print('id::', request.data["role_id"])
    print('off_id', request.data["officer_id"])
    position_map_id = PositionPositionUserMap.objects.get(user_id=request.data["role_id"]).id
    print('position_map_id', position_map_id)
    if PositionManUserMap.objects.filter(position_user_map_id=position_map_id).exists():
        print("if")
        old_role = PositionManUserMap.objects.get(position_user_map_id=position_map_id)
        PositionManUserMapTrace.objects.create(
            from_date=old_role.from_date,
            to_date=datetime.datetime.now(),
            position_user_map=position_map_id,
            user_id=old_role.user_id,
        )
        old_role.user_id = request.data["officer_id"]
        if PositionManUserMap.objects.filter(user_id=request.data["officer_id"]).exists():
            PositionManUserMap.objects.filter(user_id=request.data["officer_id"]).delete()
        old_role.save()
        user_obj = User.objects.get(id=request.data["officer_id"])
        user_obj.is_active = False
        user_obj.save()
    else:
        print("else")
        if PositionManUserMap.objects.filter(user_id=request.data["officer_id"]).exists():
            PositionManUserMap.objects.filter(user_id=request.data["officer_id"]).delete()
        position_user_map_obj = PositionManUserMap(position_user_map_id=position_map_id,
                                user_id=request.data["officer_id"],
                                from_date=datetime.datetime.now())
        position_user_map_obj.save()   
        print('position_saved')             
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def remove_employee(request):
    old_role = PositionManUserMap.objects.get(user_id=request.data["officer_id"])
    PositionManUserMapTrace.objects.create(from_date=old_role.from_date,to_date=datetime.datetime.now(),position_user_map_id=old_role.position_user_map_id,user_id=old_role.user_id,)
    old_role.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_user_banks(request):
    print(request.data)
    bank_values = (
        UserBankDetails.objects.filter(user_id=request.data["user_id"], is_active=True)
            .order_by("-is_primary")
            .values_list(
            "id",
            "user_id",
            "bank",
            "branch",
            "ifsc_code",
            "micr_code",
            "account_holder_name",
            "account_number",
            "bank_passbook_document",
            "post_cheque_image",
            "post_cheque_number",
            "is_primary",
        )
    )
    bank_columns = [
        "id",
        "user_id",
        "bank",
        "branch",
        "ifsc_code",
        "micr_code",
        "account_holder_name",
        "account_number",
        "bank_passbook_document",
        "post_cheque_image",
        "post_cheque_number",
        "is_primary",
    ]
    bank_df = pd.DataFrame(list(bank_values), columns=bank_columns)
    for index, row in bank_df.iterrows():
        try:
            with open(
                    "static/media/" + str(row["bank_passbook_document"]), "rb"
            ) as image_file:
                encoded_image1 = b64encode(image_file.read())
                bank_df.at[
                    index, "image"
                ] = "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
        except Exception as err:
            print(err)
            bank_df.at[index, "image"] = 0
            pass
        if row["post_cheque_image"] != 0:
            try:
                with open(
                        "static/media/" + str(row["post_cheque_image"]), "rb"
                ) as image_file:
                    encoded_image = b64encode(image_file.read())
                    bank_df.at[
                        index, "cheque_image"
                    ] = "data:image/jpeg;base64," + encoded_image.decode("utf-8")
            except Exception as err:
                print(err)
                bank_df.at[index, "cheque_image"] = 0
                pass
    bank_df = bank_df.fillna(0)
    return Response(bank_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def save_user_bank(request):
    req_data = request.data["form_data"]
    if req_data["bank_id"] == None:
    # if UserBankDetails.objects.filter(account_number=req_data["account_number"]).exists():
        user_bank_details = UserBankDetails(
            user_id=request.data["user_id"],
            bank=req_data["bank_name"],
            branch=req_data["branch_name"],
            ifsc_code=req_data["ifsc_code"],
            micr_code=req_data["micr_code"],
            account_holder_name=req_data["account_holder_name"],
            account_number=req_data["account_number"],
            post_cheque_number=req_data["post_dated_check_number"],
            created_by=request.user,
            modified_by=request.user,
        )

        if "passbook_image" in request.data:
            user_bank_details.bank_passbook_document = decode_image(
                request.data["passbook_image"]
            )
        if "cheque_image" in request.data:
            user_bank_details.post_cheque_image = decode_image(
                request.data["cheque_image"]
            )

        if UserBankDetails.objects.filter(user_id=request.data["user_id"]).exists():
            user_bank_details.is_primary = False

        user_bank_details.save()
        print("saved")
    else:
        UserBankDetails.objects.filter(id=req_data["bank_id"]).update(
            bank=req_data["bank_name"],
            branch=req_data["branch_name"],
            ifsc_code=req_data["ifsc_code"],
            micr_code=req_data["micr_code"],
            account_holder_name=req_data["account_holder_name"],
            account_number=req_data["account_number"],
            post_cheque_number=req_data["post_dated_check_number"],
            modified_by=request.user,
        )

        if "passbook_image" in request.data:
            UserBankDetails.objects.filter(id=req_data["bank_id"]).update(
                bank_passbook_document=decode_image(request.data["passbook_image"])
            )

        if "cheque_image" in request.data:
            UserBankDetails.objects.filter(id=req_data["bank_id"]).update(
                post_cheque_image=decode_image(request.data["cheque_image"])
            )
    
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def activate_bank(request):
    UserBankDetails.objects.filter(
        user_id=request.data["user_id"], is_primary=True
    ).update(is_primary=False)
    UserBankDetails.objects.filter(id=request.data["bank_id"]).update(is_primary=True)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def activate_farmer_bank(request):
    FarmerBankDetails.objects.filter(
        farmer_id=request.data["farmer_id"], is_primary=True
    ).update(is_primary=False)
    FarmerBankDetails.objects.filter(id=request.data["bank_id"]).update(is_primary=True)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def delete_user_bank(request):
    print(request.data)
    UserBankDetails.objects.filter(id=request.data["id"]).update(is_active=False)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_user_based_cluster(request):
    season_id = get_active_season_id()
    if UserProfile.objects.get(user=request.user).user_type_id != 5:
        active_season_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_season_cluster_ids).order_by("id")
    else:
        available_cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list("cluster_id", flat=True))
        available_cluster = Cluster.objects.filter(id__in=available_cluster_ids).order_by("id")
        print(available_cluster_ids)

    cluster_values = list(available_cluster.values_list("id", "name"))
    cluster_column = ["id", "name"]
    
    cluster_df = pd.DataFrame(cluster_values, columns=cluster_column)
    return Response(cluster_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_week_report_for_new_farmer_enrollment(request):
    season_id = request.data['season_id']

    season_id = request.data['season_id']
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        available_cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list("cluster_id", flat=True))
        available_cluster = Cluster.objects.filter(id__in=available_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=available_cluster_ids, season_id=season_id).order_by("id")
    elif user_type_id == 3:
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id)
    elif user_type_id == 6:
        farmer_ids = list(AgentFarmerMap.objects.filter(agent_id=user_id, farmer__season_id=season_id).values_list('farmer_id', flat=True))
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id, id__in=farmer_ids)
        print(farmer_ids)
        print(farmer_cluster_map)
    else:
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id)

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=28)
    last_date = start_date + datetime.timedelta(days=7)

    master_dict = {}
    for i in range(0, 5):
        #     print(start_date)
        master_dict[str(start_date)] = {}
        for cluster in available_cluster:
            master_dict[str(start_date)][cluster.name] = {}
            master_dict[str(start_date)][cluster.name]["new_farmer"] = farmer_cluster_map.filter(cluster_id=cluster.id, farmer__time_created__lte=start_date).count()
        start_date = start_date + datetime.timedelta(days=7)

    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_week_report_for_old_farmer_activated(request):
    
    season_id = request.data['season_id']
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        available_cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list("cluster_id", flat=True))
        available_cluster = Cluster.objects.filter(id__in=available_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=available_cluster_ids, season_id=season_id).order_by("id")
    elif user_type_id == 3:
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id)
    elif user_type_id == 6:
        farmer_ids = list(AgentFarmerMap.objects.filter(agent_id=user_id, farmer__season_id=season_id).values_list('farmer_id', flat=True))
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id, id__in=farmer_ids)
        print(farmer_ids)
        print(farmer_cluster_map)
    else:
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        available_cluster = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(cluster_id__in=active_cluster_ids, season_id=season_id)
        
    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=28)
    last_date = start_date + datetime.timedelta(days=7)
    master_dict = {}
    for i in range(0, 5):
        master_dict[str(start_date)] = {}
        for cluster in available_cluster:
            master_dict[str(start_date)][cluster.name] = {}
            master_dict[str(start_date)][cluster.name]["total_farmer"] = farmer_cluster_map.filter(season_id=season_id,cluster_id=cluster.id, time_created__lte=start_date).count()

        start_date = start_date + datetime.timedelta(days=7)
        last_date = start_date + datetime.timedelta(days=7)
    print(master_dict)
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_harvest_report(request):
    user_id = request.user.id
    season_id = request.data['season_id']
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        available_cluster_ids = list(UserClusterMap.objects.filter(user=request.user, season_id=season_id).values_list("cluster_id", flat=True))
        sorted_available_clusters = Cluster.objects.filter(id__in=available_cluster_ids).order_by("id")
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
                active_cluster_ids = list(UserClusterMap.objects.filter(user_id__in=subordinate_user_ids, season_id=season_id).values_list('cluster_id',flat=True))
                sorted_available_clusters = Cluster.objects.filter(id__in=active_cluster_ids).order_by("id")
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
            active_season_clusters = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id')
            sorted_available_clusters = Cluster.objects.filter(id__in=active_season_clusters).order_by("id")

    master_dict = {}
    master_dict["total_farmer"] = 0
    master_dict["total_harvest_area"] = 0
    for cluster in sorted_available_clusters:
        master_dict[cluster.name] = {}
        farmer_ids = FarmerClusterSeasonMap.objects.filter(cluster_id=cluster, season_id=season_id).values_list("farmer_id", flat=True)
        master_dict["total_farmer"] += len(farmer_ids)
        print(cluster.name)
        print(farmer_ids.count())
        master_dict[cluster.name]["farmer_count"] = len(farmer_ids)
        master_dict[cluster.name]["seed_ac"] = "-"
        master_dict[cluster.name]["nursery_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1).aggregate(Sum("area"))["area__sum"]
        master_dict[cluster.name]["main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
        if Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id,).aggregate(Sum("sowing__area"))["sowing__area__sum"] != None:
            harvest_obj = Harvest.objects.filter(sowing__farmer__id__in=farmer_ids, sowing__season_id=season_id,)
            master_dict["total_harvest_area"] += (harvest_obj.aggregate(Sum("value"))["value__sum"]/ 1000)
            master_dict[cluster.name]["harvest_area"] = (harvest_obj.aggregate(Sum("value"))["value__sum"] / 1000)
    sorted_available_clusters_ids = sorted_available_clusters.values_list("id", flat=True)
    filter_farm_ids = list(FarmerClusterSeasonMap.objects.filter(cluster_id__in=sorted_available_clusters_ids,season_id=season_id).values_list("farmer_id", flat=True))

    master_dict["total_nursery_area"] = Sowing.objects.filter(farmer_id__in=filter_farm_ids, cultivation_phase_id=1, season_id=season_id).aggregate(Sum("area"))["area__sum"]
    master_dict["total_main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=filter_farm_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
    master_dict["total_seed_ac"] = "-"
    master_dict["season"] = Season.objects.get(id=season_id).name

    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_farmer_filter_variable_list(request):
    # District section
    agent_list = []
    agents = UserProfile.objects.filter(user_type_id=6)
    for agent in agents:
        agent_dict = {
            "name": agent.user.first_name,
            "id": agent.user.id,
        }
        agent_list.append(agent_dict)

    hobli_list = []
    hoblis = Hobli.objects.all()
    for hobli in hoblis:
        hobli_dict = {
            "name": hobli.name,
            "id": hobli.id,
        }
        hobli_list.append(hobli_dict)

    village_list = []
    villages = Village.objects.all()
    for village in villages:
        village_dict = {
            "name": village.name,
            "id": village.id,
        }
        village_list.append(village_dict)

    cluster_list = []
    clusters = Cluster.objects.all()
    for cluster in clusters:
        cluster_dict = {
            "name": cluster.name,
            "id": cluster.id,
        }
        cluster_list.append(cluster_dict)

    phase_list = []
    phases = CultivationPhase.objects.all()
    for phase in phases:
        phase_dict = {
            "name": phase.name,
            "id": phase.id,
        }
        phase_list.append(phase_dict)

    master_dict = {}
    master_dict["agents"] = agent_list
    master_dict["hoblis"] = hobli_list
    master_dict["villages"] = village_list
    master_dict["clusters"] = cluster_list
    master_dict["cultivation_phase"] = phase_list

    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_batch_list(request):
    data_dict = {}
    input_type_obj = InputType.objects.all().order_by('display_ordinal')
    input_type_list = list(input_type_obj.values_list('id', 'name'))
    input_type_column = ['id', 'name']
    input_type_df = pd.DataFrame(input_type_list, columns=input_type_column)
    data_dict['input_list'] = input_type_df.to_dict('r')
    input_goods_obj = InputGoods.objects.filter(season_id=get_active_season_id()).order_by('id')
    input_goods_list = list(
        input_goods_obj.values_list('id', 'code', 'input_name__input_type', 'input_name__name','quantity_now', 'quantity_at_receipt',
                                    'number_of_units', 'date_of_expiry', 'date_of_manufacturing', 'date_of_receipt',
                                    'supplier__name', 'cost', 'unit__name'))
    input_goods_column = ['id', 'code', 'input_type_id', 'name_of_good', 'total_qty', 'received_qty', 'number_of_units',
                          'date_of_expiry', 'date_of_manufacture', 'date_of_receipt', 'supplier_name', 'cost', 'unit_name']
    input_goods_df = pd.DataFrame(input_goods_list, columns=input_goods_column)
    input_goods_df['is_goods_taken'] = False
    input_goods_df.loc[input_goods_df['total_qty'] != input_goods_df['received_qty'], 'is_goods_taken'] = True
    data_dict['goods_dict'] = input_goods_df.groupby('input_type_id').apply(lambda x: x.to_dict('r')).to_dict()
    # print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_input_types(request):
    input_item_values = list(InputType.objects.all().values_list("id", "name")).order_by('display_ordinal')
    input_type_columns = ["id", "name"]
    df = pd.DataFrame(input_item_values, columns=input_type_columns)
    return Response(df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_units(request):
    unit_values = list(Unit.objects.all().values_list("id", "name"))
    unit_columns = ["id", "name"]
    df = pd.DataFrame(unit_values, columns=unit_columns)
    return Response(df.to_dict("r"), status=status.HTTP_200_OK)


def generate_batch_code(input_type_id):
    input_short_code = InputType.objects.get(id=input_type_id).short_code
    batch_code_bank_obj = InputGoodsCodeBank.objects.filter(input_type_id=input_type_id)[0]
    last_digit_code = batch_code_bank_obj.last_digit
    new_last_digit_code = last_digit_code + 1
    batch_code = str(batch_code_bank_obj.input_code_prefix) + str(datetime.datetime.now().year)[2:4] + '_' +str(input_short_code) + str(new_last_digit_code).zfill(4)
    batch_code_bank_obj.last_digit = new_last_digit_code
    batch_code_bank_obj.save()
    return batch_code


@api_view(['POST'])
def serve_supplier_and_input_name(request):
    data_dict = {}
    supplier_obj = Supplier.objects.all()
    supplier_list = list(supplier_obj.values_list('id', 'name'))
    supplier_column = ['id', 'name']
    supplier_df = pd.DataFrame(supplier_list, columns=supplier_column)
    data_dict['supplier_list'] = supplier_df.to_dict('r')

    input_name_obj = InputName.objects.filter(input_type_id=request.data['input_type_id'])
    input_name_list = list(input_name_obj.values_list('id', 'name'))
    input_name_column = ['id', 'name']
    input_name_df = pd.DataFrame(input_name_list, columns=input_name_column)
    data_dict['input_name_list'] = input_name_df.to_dict('r')
    user_obj = UserProfile.objects.filter(user_type_id__in=[1, 2, 3, 4]).exclude(user_id__in=[94, 116, 115])
    user_list = list(user_obj.values_list('user', 'user__username', 'user__first_name'))
    user_column = ['id', 'user_name', 'first_name']
    user_df = pd.DataFrame(user_list, columns=user_column)
    data_dict['user_list'] = user_df.to_dict('r')
    data_dict['logged_user_id'] = request.user.id
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_input_goods_expiry_date(request):
    input_goods_obj = InputGoods.objects.get(id=request.data['goods_id'])
    input_goods_obj.date_of_expiry = request.data['date_of_expiry']
    input_goods_obj.save()
    if not InputGoodsExpiryDateTrace.objects.filter(input_goods_id=input_goods_obj.id, date_of_expiry=request.data['date_of_expiry']).exists():
        input_goods_expiry_data_obj = InputGoodsExpiryDateTrace(input_goods_id=input_goods_obj.id,
                                                                date_of_expiry=request.data['date_of_expiry'],
                                                                changed_by_id=request.user.id)
        input_goods_expiry_data_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def update_input_packet_inventory_expiry_date(request):
    input_packet_obj = InputPacketInventory.objects.get(id=request.data['packet_inventory_id'])
    input_packet_obj.date_of_expiry = request.data['date_of_expiry']
    input_packet_obj.save()
    if not InputPacketInventoryExpiryDateTrace.objects.filter(input_packet_inventory_id=input_packet_obj.id, date_of_expiry=request.data['date_of_expiry']).exists():
        input_packet_expiry_data_obj = InputPacketInventoryExpiryDateTrace(input_packet_inventory_id=input_packet_obj.id,
                                                                date_of_expiry=request.data['date_of_expiry'],
                                                                changed_by_id=request.user.id)
        input_packet_expiry_data_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def register_batch(request):
    data = {}
    if not InputGoods.objects.filter(date_of_receipt=request.data["date_of_receipt"], input_name_id=request.data["input_name_id"], quantity_at_receipt=request.data["total_quantity"]).exists():
        input_type_id = InputName.objects.get(id=request.data["input_name_id"]).input_type.id
        InputGoods.objects.create(
            business_id=1,
            code=generate_batch_code(input_type_id),
            season_id=get_active_season_id(),
            input_name_id=request.data["input_name_id"],
            number_of_units=request.data["number_of_units"],
            unit_id=request.data["unit"]['id'],
            unit_quantity=request.data["unit_quantity"],
            quantity_at_receipt=request.data["total_quantity"],
            quantity_now=request.data["total_quantity"],
            cost=request.data["total_cost"],
            quantity_now_time=datetime.datetime.now(),
            supplier_id=request.data["supplier_id"],
            date_of_manufacturing=request.data["date_of_manufacture"],
            date_of_expiry=request.data["date_of_expiry"],
            date_of_receipt=request.data["date_of_receipt"],
            created_by_id=request.data["received_by_id"],
            modified_by_id=request.data["received_by_id"],
        )
        data["message"] = "Goods added Successfully"
        data['status'] = True
    else:
        data["message"] = "Goods already exists"
        data['status'] = False

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_new_supplier(request):
    print(request.data)
    if not Supplier.objects.filter(name=request.data['name']).exists():
        supplier_obj = Supplier(name=request.data['name'])
        supplier_obj.save()
    else:
        supplier_obj = Supplier.objects.filter(name=request.data['name'])[0]
    data_dict = {
        'id': supplier_obj.id,
        'name': supplier_obj.name
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def input_part_list_for_kit(request):
    data_dict = {}
    kit_id = request.data['kit_id']
    input_part_obj = InputPart.objects.filter(input_combo_id=kit_id)
    input_name_ids = list(input_part_obj.values_list('name', flat=True))
    input_part_list = list(input_part_obj.values_list('id', 'name', 'name__name', 'value', 'unit__name', 'unit_id'))
    input_part_column = ['part_id', 'name_id', 'name', 'part_qty', 'unit_name', 'unit_id']
    input_part_df = pd.DataFrame(input_part_list, columns=input_part_column)
    input_part_df['input_part_base_unit_qty'] = input_part_df.apply(
        lambda x: find_base_unit_quantity(x['unit_id'], x['part_qty']), axis=1)
    data_dict['input_part_list'] = input_part_df.to_dict('r')

    input_goods_obj = InputGoods.objects.filter(input_name_id__in=input_name_ids)
    input_goods_list = list(
        input_goods_obj.values_list('id', 'code', 'date_of_expiry', 'input_name', 'unit', 'quantity_now'))
    input_goods_column = ['goods_id', 'code', 'date_of_expiry', 'input_name_id', 'goods_unit_id', 'goods_qty']
    input_goods_df = pd.DataFrame(input_goods_list, columns=input_goods_column)
    input_goods_df['input_goods_base_unit_qty'] = input_goods_df.apply(
        lambda x: find_base_unit_quantity(x['goods_unit_id'], x['goods_qty']), axis=1)
    merge_df = input_goods_df.merge(input_part_df, how='left', left_on='input_name_id', right_on='name_id')
    merge_df['max_limit'] = np.floor(merge_df['goods_qty'] / merge_df['input_part_base_unit_qty'])
    data_dict['input_part_goods_dict'] = merge_df.groupby('input_name_id').apply(lambda x:x.to_dict('r')).to_dict()

    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_label_from_for_packet_inventory(request):
    input_packet_obj = InputPacketInventoryLabel.objects.get(input_packet_inventory_id=request.data['packet_inventory_id'])
    data_dict = {
        'label_range_start': input_packet_obj.label_range_start
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def register_store_inventory(request):
    sid = transaction.savepoint()
    try:
        #input store inventory entry
        input_store_obj = InputStoreInventory(input_packet_inventory_id=request.data['packet_inventory_id'],
                                            storage_id=request.data['storage_id'],
                                            section=request.data['section'],
                                            sub_section=request.data['sub_section'],
                                            season_id=get_active_season_id(),
                                            date_of_receipt=request.data['date_of_receipt'],
                                            quantity_at_receipt=request.data['total_qty'],
                                            quantity_now=request.data['total_qty'],
                                            quantity_now_time=datetime.datetime.now(),
                                            unit_id=4,
                                            label_range_start=request.data['label_from'],
                                            label_range_end=request.data['label_to'],
                                            created_by_id=request.user.id,
                                            modified_by_id=request.user.id,
                                            )
        input_store_obj.save()

        #get label prefix and suffix from packet inventory label
        input_batch_label_obj = InputPacketInventoryLabel.objects.get(input_packet_inventory_id=request.data['packet_inventory_id'])
        label_from = request.data['label_from']
        label_to = request.data['label_to']

        #create label based on total qty
        for i in range(label_from, label_to+1):
            label = str(input_batch_label_obj.label_prefix) + str(i) + str(input_batch_label_obj.label_suffix)
            input_store_label_obj = InputStoreInventoryPacketLabel(input_store_inventory_id=input_store_obj.id,
                                                                label=label,
                                                                stock_status_id=1,
                                                                received_date=datetime.datetime.now(),
                                                                received_by_id=request.user.id)
            input_store_label_obj.save()

        #update the label to . to the packet inventory label so next label will start from that
        input_batch_label_obj.label_range_start = label_to + 1
        input_batch_label_obj.save()

        #adjust the total qty in packet inventory
        input_packet_obj = InputPacketInventory.objects.get(id=request.data['packet_inventory_id'])
        quantity_now = input_packet_obj.quantity_now
        input_packet_obj.quantity_now = quantity_now - request.data['total_qty']
        input_packet_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes((AllowAny, ))
def get_input_type_based_batch(request):
    print(request.data)
    data_dict = {}
    master_dict = {

    }
    master_list = []
    # if request.data['input_type_group_id'] == 1:
    #     input_batches = InputBatch.objects.filter(input_type_id=request.data['input_type_id'])
    # else:
    #     input_batches = InputBatch.objects.filter()
    # for input_batch in input_batches:
    #     base_batch_value = find_base_unit_quantity(input_batch.unit.id, input_batch.quantity_now)
    #     input_batch_part_map_obj = InputPartInputBatchMap.objects.filter(batch_id=input_batch.id)
    #     final_value = 0
    #     for part in input_batch_part_map_obj:
    #         if InputItemInputPartBatchMap.objects.filter(input_part_batch_map=part.id).exists():
    #             input_part_base_value = find_base_unit_quantity(part.input_part.unit.id, part.input_part.value)
    #             input_item_quantity_now = InputItemInputPartBatchMap.objects.get(
    #                 input_part_batch_map=part.id).quantity_now
    #             final_value += input_item_quantity_now * input_part_base_value
    #     available_qty = base_batch_value - final_value
    #     if not input_batch.id in master_dict:
    #         master_dict[input_batch.id] = {
    #             'value': available_qty,
    #             'unit_id': input_batch.unit.id,
    #             'unit_name': input_batch.unit.name,
    #             'base_unit': input_batch.unit.base_unit.id,
    #             'base_unit_name': input_batch.unit.base_unit.name
    #         }
    #     temp_dict = {}
    #     temp_dict["id"] = input_batch.id
    #     temp_dict["name"] = input_batch.source + "-" + str(input_batch.code)
    #     master_list.append(temp_dict)
    # data_dict['master_dict'] = master_dict
    # data_dict['master_list'] = master_list
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_unit_based_on_base_unit(request):
    unit_obj = Unit.objects.all()
    unit_list = list(unit_obj.values_list('id', 'name', 'base_unit'))
    unit_column = ['id', 'name', 'base_unit_id']
    unit_df = pd.DataFrame(unit_list, columns=unit_column)
    final_dict = unit_df.groupby('base_unit_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny, ))
def get_input_type_based_input_item(request):
    master_dict = {}
    # input_items = InputItem.objects.all()
    # for input_type in InputType.objects.all().order_by('display_ordinal'):
    #     if not input_type.id in master_dict:
    #         master_dict[input_type.id] = []
    # for input_item in input_items:
    #     temp_dict = {}
    #     temp_dict["id"] = input_item.id
    #     temp_dict["price"] = InputPart.objects.filter(input_id=input_item.id)[0].price
    #     temp_dict["name"] = (
    #             input_item.name
    #             + " - "
    #             + str(input_item.value) + ' ' + str(input_item.unit.name)
    #     )
    #     input_part_batch_obj = InputPartInputBatchMap.objects.filter(input_part__input_id=input_item.id)
    #     temp_dict["input_part_batch_ids"] = []
    #     input_batch_list = []
    #     for input_part_batch_map in input_part_batch_obj:
    #         input_batch_dict = {}
    #         input_batch_dict['max_qty'] = input_part_batch_map.max_value
    #         input_batch_dict[
    #             'available_qty_in_batch'] = str(input_part_batch_map.max_value * input_part_batch_map.input_part.value)  + ' ' + str(input_part_batch_map.batch.unit.base_unit.name)
    #         input_batch_dict['batch_code'] = input_part_batch_map.batch.code
    #         input_batch_dict['input_type_name'] = input_part_batch_map.batch.input_type.name
    #         input_batch_dict['item_name'] = input_part_batch_map.input_part.name
    #         input_batch_dict['value'] = str(input_part_batch_map.input_part.value) + ' ' + str(input_part_batch_map.input_part.unit.name)
    #         input_batch_list.append(input_batch_dict)
    #         temp_dict["input_part_batch_ids"].append(input_part_batch_map.id)
    #     temp_dict['input_batch_dict'] = input_batch_list
    #     master_dict[input_item.type.id].append(temp_dict)
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_quantity_available_in_batch(request):
    # quantity = request.data['quantity']
    # input_part_batch_ids = request.data['input_item']['input_part_batch_ids']
    # input_part_batch_obj = InputPartInputBatchMap.objects.filter(id__in=input_part_batch_ids)
    # temp_data_dict = {}
    # is_quantity_available = True
    # for input_part_batch in input_part_batch_obj:
    #     if quantity > input_part_batch.max_value:
    #         is_quantity_available = False
    #         temp_data_dict = {
    #             'available_quantity': input_part_batch.max_value * input_part_batch.input_part.value,
    #             'requested_quantity': quantity,
    #             'input_part_value': input_part_batch.input_part.value,
    #             'batch_name': input_part_batch.batch.code,
    #             'input_part_name': input_part_batch.input_part.name,
    #             'max_value': input_part_batch.max_value,
    #             'unit_name': input_part_batch.input_part.unit.name
    #         }
    #         break
    data_dict = {}
    # if is_quantity_available:
    #     data_dict['status'] = True
    # else:
    #     data_dict['status'] = False
    #     data_dict['data'] = temp_data_dict
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def register_input_item_batch_map(request):
    # print(request.data)
    # sid = transaction.savepoint()
    # try:
    #     input_item = request.data['input_item']
    #     input_item_batch_map = InputItemInputPartBatchMap(item_id=input_item['id'],
    #                                                       quantity_at_receipt=request.data['value'],
    #                                                       quantity_now=request.data['value'],
    #                                                       quantity_now_time=datetime.datetime.now(),
    #                                                       unit_id=request.data['unit_id'],
    #                                                       code=request.data['code'],
    #                                                       price_per_packet=request.data['price_per_packet'],
    #                                                       created_by_id=request.user.id,
    #                                                       modified_by_id=request.user.id
    #                                                       )
    #     input_item_batch_map.save()

    #     # add input part batch map obj to input batch map
    #     input_part_batch_obj = InputPartInputBatchMap.objects.filter(id__in=input_item['input_part_batch_ids'])
    #     for input_part_batch_map in input_part_batch_obj:
    #         input_item_batch_map.input_part_batch_map.add(input_part_batch_map)
    #     input_item_batch_map.save()

    #     # create label for the input item batch map
    #     input_batch_label_obj = InputBatchLabel(input_item_input_batch_id=input_item_batch_map.id,
    #                                             label_prefix=request.data['label_prefix'],
    #                                             label_suffix=request.data['label_suffix'],
    #                                             label_range_start=request.data['label_start'],
    #                                             label_range_end=request.data['label_end'],
    #                                             )
    #     input_batch_label_obj.save()
    #     for input_part_batch_map in input_part_batch_obj:
    #         part_value = input_part_batch_map.input_part.value
    #         max_value = input_part_batch_map.max_value
    #         input_part_batch_map.max_value = max_value - request.data['value']
    #         input_part_batch_map.save()
    #         available_qty = part_value * input_part_batch_map.max_value
    #         if InputPartInputBatchMap.objects.filter(batch_id=input_part_batch_map.batch.id).exclude(id=input_part_batch_map.id).exists():
    #             other_input_part_batch_map = InputPartInputBatchMap.objects.filter(batch_id=input_part_batch_map.batch.id).exclude(id=input_part_batch_map.id)
    #             for other_input_part in other_input_part_batch_map:
    #                 if not available_qty == 0:
    #                     current_available_quantity = available_qty / other_input_part.input_part.value
    #                     other_input_part.max_value = current_available_quantity
    #                     other_input_part.save()
    #                 else:
    #                     other_input_part.max_value = 0
    #                     other_input_part.save()
    #     data_dict = {
    #         'status': True,
    #         'message': 'Main Inventory Added Successfully'
    #     }
    #     transaction.savepoint_commit(sid)
    #     return Response(data=data_dict, status=status.HTTP_200_OK)
    # except Exception as e:
    #     print('error on {}'.format(e))
    #     data_dict = {
    #         'status': False,
    #         'message': 'Error While Creating Main Inventory'
    #     }
    #     transaction.savepoint_rollback(sid)
        return Response(data={}, status=status.HTTP_200_OK)


def get_available_qty_in_batch(batch_id):
    # input_batch = InputBatch.objects.get(id=batch_id)
    # base_batch_value = find_base_unit_quantity(input_batch.unit.id, input_batch.quantity_now)
    # input_batch_part_map_obj = InputPartInputBatchMap.objects.filter(batch_id=input_batch.id)
    # final_value = 0
    # for part in input_batch_part_map_obj:
    #     if InputItemInputPartBatchMap.objects.filter(input_part_batch_map=part.id).exists():
    #         input_part_base_value = find_base_unit_quantity(part.input_part.unit.id, part.input_part.value)
    #         input_item_quantity_now = InputItemInputPartBatchMap.objects.get(input_part_batch_map=part.id).quantity_now
    #         final_value += input_item_quantity_now * input_part_base_value
    # available_qty = base_batch_value - final_value
    available_qty = 0
    return available_qty

    
@api_view(['GET'])
def serve_packet_inventory_list(request):
    data_dict = {}
    season_id = get_active_season_id()
    input_combo_obj = InputCombo.objects.filter().order_by('display_ordinal')
    input_combo_list = list(input_combo_obj.values_list('id', 'name', 'price'))
    input_combo_column = ['id', 'name', 'cost']
    input_combo_df = pd.DataFrame(input_combo_list, columns=input_combo_column)
    data_list = []
    for index, row in input_combo_df.iterrows():
        temp_dict = {
            'id': row['id'],
            'name': row['name'],
            'label_start_from': 1,
            'cost': row['cost'],
            'input_part': []
        }
        input_part_obj = InputPart.objects.filter(input_combo_id=row['id'])
        input_part_list = list(input_part_obj.values_list('id', 'name__name', 'value', 'unit__name'))
        input_part_column = ['id', 'name', 'value', 'unit_name']
        input_part_df = pd.DataFrame(input_part_list, columns=input_part_column)
        temp_dict['input_part'] = input_part_df.to_dict('r')
        if InputPacketInventoryLabel.objects.filter(input_packet_inventory__input_combo_id=row['id'],  input_packet_inventory__season_id=season_id).exists():
            latest_label_obj = InputPacketInventoryLabel.objects.filter(input_packet_inventory__input_combo_id=row['id'], input_packet_inventory__season_id=season_id).order_by('-id')[0]
            temp_dict['label_start_from'] = latest_label_obj.label_range_end + 1
        data_list.append(temp_dict)
    data_dict['kit_list'] = data_list

    input_packet_obj = InputPacketInventory.objects.filter(season_id=season_id).order_by('id')
    input_packey_ids = list(input_packet_obj.values_list('id', flat=True))
    input_packet_list = list(
        input_packet_obj.values_list('id', 'input_combo', 'input_combo__name', 'packet_code', 'quantity_at_receipt', 'quantity_now',
                                     'date_of_expiry', 'inputpacketinventorylabel__label_range_start_default',
                                     'inputpacketinventorylabel__label_range_end', 'price_per_packet'))
    input_packet_column = ['id', 'input_combo_id', 'combo_name', 'packet_code', 'total_qty', 'available_qty', 'date_of_expiry',
                           'label_range_start', 'label_range_end', 'price']
    input_packet_df = pd.DataFrame(input_packet_list, columns=input_packet_column)
    input_packet_df['is_full_stock_given_to_store'] = False
    input_packet_df.loc[input_packet_df['total_qty'] != input_packet_df['available_qty'], 'is_full_stock_given_to_store'] = True
    input_store_obj = InputStoreInventory.objects.filter(input_packet_inventory_id__in=input_packey_ids, season_id=season_id).order_by('id')
    input_store_list = list(
        input_store_obj.values_list('id', 'input_packet_inventory_id', 'storage__name', 'quantity_at_receipt','quantity_now', 'section', 'sub_section', 'label_range_start', 'label_range_end'))
    input_store_column = ['store_id', 'input_packet_inventory_id', 'storage_name', 'total_qty_in_store', 'available_qty_in_store', 'section', 'sub_section', 'label_range_start', 'label_range_end']
    input_store_df = pd.DataFrame(input_store_list, columns=input_store_column)

    if not input_store_df.empty:
        input_store_df = input_store_df.groupby('input_packet_inventory_id').apply(
            lambda x: x.to_dict('r')).to_frame()
    final_df = input_packet_df.merge(input_store_df, how='left', left_on='id',
                                     right_on='input_packet_inventory_id')
    final_df = final_df.rename(columns={0: 'storage_list'})
    final_df = final_df.fillna(0)

    #sub store list
    input_sub_store_obj = InputSubStoreInventory.objects.filter(input_store_inventory__input_packet_inventory_id__in=input_packey_ids, season_id=season_id).order_by('id')
    input_sub_store_list = list(
        input_sub_store_obj.values_list('id', 'input_store_inventory__input_packet_inventory_id', 'sub_storage__name', 'quantity_at_receipt',
                                    'quantity_now', 'section', 'sub_section', 'label_range_start', 'label_range_end', 'substorerequestlog__request_code'))
    input_sub_store_column = ['store_id', 'input_packet_inventory_id', 'storage_name', 'total_qty_in_store', 'available_qty_in_store', 'section', 'sub_section', 'label_range_start', 'label_range_end', 'sub_store_request_code']
    input_sub_store_df = pd.DataFrame(input_sub_store_list, columns=input_sub_store_column)


    if not input_sub_store_df.empty:
        input_sub_store_df = input_sub_store_df.groupby('input_packet_inventory_id').apply(
            lambda x: x.to_dict('r')).to_frame()
    final_df = final_df.merge(input_sub_store_df, how='left', left_on='id',
                                    right_on='input_packet_inventory_id')
    final_df = final_df.rename(columns={0: 'sub_storage_list'})
    final_df = final_df.fillna(0)
    data_dict['packet_inventory_dict'] = final_df.groupby('input_combo_id').apply(lambda x: x.to_dict('r')).to_dict()

    #sub store request
    request_rise_obj = SubStoreRequestLog.objects.filter(status_id=1)
    request_rise_list = list(request_rise_obj.values_list('id', 'request_code', 'input_combo_id', 'storage_id', 'section', 'sub_section', 'requested_quantity', 'unit__name', 'requested_by__username', 'requested_at'))
    request_rise_column = ['id', 'request_code', 'requested_input_combo_id', 'sub_store_id', 'sub_storage_section', 'sub_storage_sub_section', 'requested_quantity', 'unit_name', 'requested_by', 'requested_at']
    request_rise_df = pd.DataFrame(request_rise_list, columns=request_rise_column)
    request_rise_dict = request_rise_df.groupby('requested_input_combo_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict['sub_store_request'] = request_rise_dict

    return Response(data=data_dict, status=status.HTTP_200_OK)


def find_base_unit_quantity(unit_id, value):
    unit_obj = Unit.objects.get(id=unit_id)
    if unit_obj.base_unit_id == 1:
        if unit_obj.id == 1:
            final_value = value
        elif unit_obj.id == 5:
            final_value = value / 1000
    elif unit_obj.base_unit_id == 2:
        if unit_obj.id == 6:
            final_value = value / 1000
        else:
            final_value = value
    else:
        final_value = value
    return final_value
 

@api_view(['POST'])
@transaction.atomic
def register_input_item_and_part_map(request):
    sid = transaction.savepoint()
    try:
        print('data')
        # input_item = request.data['input_item']
        # input_part_data = request.data['input_part']
        # data = {}
        # if not InputItem.objects.filter(value=input_item['value'], unit=input_item['unit_id'], type_id=input_item['input_type_id']).exists():
        #     input_item_obj = InputItem(business_id=1,
        #                                season_id=Season.objects.get(is_active=True).id,
        #                                name=input_item['name'],
        #                                value=input_item['value'],
        #                                unit_id=input_item['unit_id'],
        #                                type_id=input_item['input_type_id'],
        #                                created_by_id=request.user.id,
        #                                modified_by_id=request.user.id)
        #     if input_item['input_type_group_id'] == 2:
        #         input_item_obj.is_combo = True
        #     input_item_obj.save()
        #     for input_part in input_part_data:
        #         input_part_obj = InputPart(name=input_part['name'],
        #                                    input_id=input_item_obj.id,
        #                                    value=input_part['value'],
        #                                    unit_id=input_part['unit_id'],
        #                                    price=input_part['price'],
        #                                    modified_by_id=request.user.id,
        #                                    created_by_id=request.user.id)
        #         input_part_obj.save()
        #         # map input part with input batch

        #         input_batch = InputBatch.objects.get(id=input_part['batch_id'])
        #         base_batch_value = find_base_unit_quantity(input_batch.unit.id, input_batch.quantity_now)
        #         input_batch_part_map_obj = InputPartInputBatchMap.objects.filter(batch_id=input_batch.id)
        #         final_value = 0
        #         for part in input_batch_part_map_obj:
        #             if InputItemInputPartBatchMap.objects.filter(input_part_batch_map=part.id).exists():
        #                 input_part_base_value = find_base_unit_quantity(part.input_part.unit.id, part.input_part.value)
        #                 input_item_quantity_now = InputItemInputPartBatchMap.objects.get(
        #                     input_part_batch_map=part.id).quantity_now
        #                 final_value += input_item_quantity_now * input_part_base_value
        #         input_base_value = base_batch_value - final_value

        #         input_part_base_value = find_base_unit_quantity(input_part_obj.unit.id, input_part_obj.value)
        #         max_value = math.floor(int(input_base_value) / input_part_base_value)
        #         input_part_batch_map_obj = InputPartInputBatchMap(input_part_id=input_part_obj.id,
        #                                                           batch_id=input_part['batch_id'],
        #                                                           max_value=max_value)
        #         input_part_batch_map_obj.save()
        #     data['status'] = True
        #     data['message'] = 'Created Successfully'
        #     temp_dict = {}
        #     temp_dict["id"] = input_item_obj.id
        #     temp_dict["name"] = (
        #             input_item_obj.name
        #             + " - "
        #             + str(input_item_obj.value) + ' ' + str(input_item_obj.unit.name)
        #     )
        #     input_part_batch_obj = InputPartInputBatchMap.objects.filter(input_part__input_id=input_item_obj.id)
        #     temp_dict["input_part_batch_ids"] = []
        #     for input_part_batch_map in input_part_batch_obj:
        #         temp_dict["input_part_batch_ids"].append(input_part_batch_map.id)
        #     data['item_data'] = temp_dict
        transaction.savepoint_commit(sid)
        # else:
        #     data['status'] = False
        #     data['message'] = 'Item Already Exists !!!'
        return Response(data={}, status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
    return Response(status=status.HTTP_404_NOT_FOUND)


def generate_packet_inventory_code():
    code_bank_obj = InputPacketInventoryCodeBank.objects.filter()[0]
    last_digit_code = code_bank_obj.last_digit
    new_last_digit_code = last_digit_code + 1
    code = str(code_bank_obj.code_prefix) + str(datetime.datetime.now().year)[2:4] + str(new_last_digit_code).zfill(3)
    code_bank_obj.last_digit = new_last_digit_code
    code_bank_obj.save()
    return code


@api_view(["POST"])
@transaction.atomic
def register_packet_inventory(request):
    sid = transaction.savepoint()
    try:
        input_combo_obj = InputCombo.objects.get(id=request.data['kit_id'])
        input_packet_obj = InputPacketInventory(packet_code=generate_packet_inventory_code(),
                                                season_id=get_active_season_id(),
                                                input_combo_id=request.data['kit_id'],
                                                quantity_at_receipt=request.data['total_qty'],
                                                quantity_now=request.data['total_qty'],
                                                quantity_now_time=datetime.datetime.now(),
                                                unit_id=4,
                                                price_per_packet=input_combo_obj.price,
                                                date_of_expiry=request.data['date_of_expiry'],
                                                created_by_id=request.user.id,
                                                modified_by_id=request.user.id
                                                )

        input_packet_obj.save()
        part_goods_dict = request.data['part_goods_dict']
        for key in part_goods_dict:
            if part_goods_dict[key] != None:
                input_packet_part_obj = InputPacketInventoryPart(input_packet_inventory_id=input_packet_obj.id,
                                                                part_id=key,
                                                                input_goods_id=part_goods_dict[key])
                input_packet_part_obj.save()
                part_obj = InputPart.objects.get(id=key)
                input_goods_obj = InputGoods.objects.get(id=part_goods_dict[key])
                part_base_unit_value = find_base_unit_quantity(part_obj.unit_id, part_obj.value)
                taken_quantity = request.data['total_qty'] * part_base_unit_value
                quantity_now = input_goods_obj.quantity_now - taken_quantity
                input_goods_obj.quantity_now = quantity_now
                input_goods_obj.save()
        input_packet_label_obj = InputPacketInventoryLabel(input_packet_inventory_id=input_packet_obj.id,
                                                           label_prefix=request.data['label_prefix'],
                                                           label_suffix=request.data['label_suffix'],
                                                           label_range_start=request.data['label_range_start'],
                                                           label_range_start_default=request.data['label_range_start'],
                                                           label_range_end=request.data['label_range_end'],
                                                           )
        input_packet_label_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def register_input_items(request):
    data = {}
    # if request.data["input_item_id"] == None:
    #     if not InputItem.objects.filter(
    #             name__iexact=request.data["name"], value=request.data["value"]
    #     ).exists():
    #         input_item_obj = InputItem(
    #             name=request.data["name"],
    #             business_id=1,
    #             season_id=1,
    #             value=request.data["value"],
    #             unit_id=request.data["unit_id"],
    #             type_id=request.data["input_type_id"],
    #             is_active=True,
    #             created_by=request.user,
    #             modified_by=request.user,
    #         )
    #         input_item_obj.save()
    #         print("saved")
    #         data["input_item_id"] = input_item_obj.id
    #     else:
    #         input_item_obj = InputItem.objects.get(
    #             name__iexact=request.data["name"], value=request.data["value"]
    #         )
    #         print("item exists")
    #         data["input_item_id"] = input_item_obj.id
    return Response(data, status=status.HTTP_200_OK)




# @api_view(['POST'])
# def move_main_inventory_to_store_inventory(request):
#     store_inventory_obj = InputItemInputBatchStorageLocation(item_batch_map_id=request.data['input_item_batch_id'],
#                                                             storage_id=request.data['storage_id'],
#                                                             section=request.data['section'],
#                                                             sub_section=request.data['sub_section'],
#                                                             date_of_receipt=request.data['date_of_receipt'],
#                                                             quantity_at_receipt=request.data['value'],
#                                                             quantity_now=request.data['value'],
#                                                             unit_id=request.data['unit_id'],
#                                                             created_by_id=request.user.id,
#                                                             modified_by_id=request.user.id,
#                                                             )
#     store_inventory_obj.save()
#     input_item_batch_obj = InputItemInputPartBatchMap.objects.get(id=request.data['input_item_batch_id'])
#     input_batch_label_obj = InputBatchLabel.objects.get(input_item_input_batch_id=input_item_batch_obj.item)
#     label_from = request.data['label_from']
#     label_to = request.data['label_to']
#     for i in range(label_from, label_to+1):




@api_view(["GET"])
def get_agent_stocks(request):
    # input_item_input_batch_agent_values = (
    #     InputItemInputBatchAgentInventory.objects.all().values_list(
    #         "id",
    #         "agent_id",
    #         "agent__first_name",
    #         "item_batch_map__batch__code",
    #         "item_batch_map_id",
    #         "item_batch_map__code",
    #         "item_batch_map__item__name",
    #         "item_batch_map__item__value",
    #         "item_batch_map__batch_id",
    #         "date_of_receipt",
    #         "quantity_at_receipt",
    #         "quantity_now",
    #         "quantity_now_time",
    #         "unit",
    #         "unit__name",
    #     )
    # )
    # input_item_input_batch_agent_columns = [
    #     "id",
    #     "agent_id",
    #     "agent_name",
    #     "batch_code",
    #     "item_batch_map_id",
    #     "item_batch_map_code",
    #     "item_batch_map_item_name",
    #     "item_batch_map_item_value",
    #     "item_batch_map_batch_id",
    #     "date_of_receipt",
    #     "calculated_sum_quantity_at_receipt",
    #     "calculatedsum_quanitity_now",
    #     "quantity_now_time",
    #     "unit",
    #     "unit_name",
    # ]
    # input_item_input_batch_storage_location_df = pd.DataFrame(
    #     list(input_item_input_batch_agent_values),
    #     columns=input_item_input_batch_agent_columns,
    # )
    # # input_item_input_batch_storage_location_df.groupby('item_batch_map_id').apply(lambda x: x.to_dict('r')).to_dict()

    # # input_item_input_batch_storage_location_df['calculated_sum_quantity_at_receipt'] = input_item_input_batch_storage_location_df.groupby(['item_batch_map_id'])['quantity_at_receipt'].transform('sum')
    # # input_item_input_batch_storage_location_df['calculatedsum_quanitity_now'] = input_item_input_batch_storage_location_df.groupby(['item_batch_map_id'])['quantity_now'].transform('sum')

    # data = (
    #     input_item_input_batch_storage_location_df.groupby(["agent_name"])
    #         .apply(lambda x: x.to_dict("r"))
    #         .to_dict()
    # )

    return Response(data={}, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_profile(request):
    user_id = request.data["user_id"]
    user_obj = User.objects.get(id=user_id)
    user_profile_obj = UserProfile.objects.get(user_id=user_id)

    agent_profile_dict = {}
    agent_profile_dict["name"] = user_obj.first_name + " " + user_obj.last_name
    agent_profile_dict["code"] = user_profile_obj.code
    agent_profile_dict["date_of_joining"] = user_profile_obj.date_of_joining
    agent_profile_dict["gender"] = user_profile_obj.gender.name
    agent_profile_dict["dob"] = user_profile_obj.dob
    agent_profile_dict["mobile"] = user_profile_obj.mobile
    agent_profile_dict["alternate_mobile"] = user_profile_obj.alternate_mobile
    agent_profile_dict["emergency_number"] = user_profile_obj.emergency_number
    agent_profile_dict["address"] = user_profile_obj.address
    agent_profile_dict["state"] = user_profile_obj.state.name
    agent_profile_dict["district"] = user_profile_obj.district.name
    agent_profile_dict["taluk"] = user_profile_obj.taluk.name
    agent_profile_dict["hobli"] = user_profile_obj.hobli.name
    agent_profile_dict["village"] = user_profile_obj.village.name
    agent_profile_dict["pincode"] = user_profile_obj.pincode
    agent_profile_dict["aadhaar_number"] = user_profile_obj.aadhaar_number
    agent_profile_dict["pan_number"] = user_profile_obj.pan_number
    agent_profile_dict[
        "driving_licence_number"
    ] = user_profile_obj.driving_licence_number
    agent_profile_dict["agreement_number"] = user_profile_obj.agreement_number

    if AgentFarmerMap.objects.filter(agent_id=user_id).exists():
        agent_profile_dict["have_farmers"] = True
        agent_profile_dict["total_farmers"] = AgentFarmerMap.objects.filter(
            agent_id=user_id
        ).count()
        agent_profile_dict["active_season_farmer"] = AgentFarmerMap.objects.filter(
            agent_id=user_id, farmer__season_id=2
        ).count()
        farmer_ids = list(
            AgentFarmerMap.objects.filter(
                agent_id=user_id, farmer__season_id=2
            ).values_list("farmer__farmer_id", flat=True)
        )
        agent_profile_dict["total_land_area"] = Sowing.objects.filter(
            farmer_id__in=farmer_ids, season_id=2
        ).aggregate(Sum("area"))["area__sum"]
    else:
        agent_profile_dict["have_farmers"] = False

    # if InputItemInputBatchAgentInventory.objects.filter(agent_id=user_id).exists():
    #     agent_profile_dict["have_seed_transaction"] = True
    #     agent_profile_dict["total_seeds_bought"] = AgentPacketLabel.objects.filter(
    #         inputitem_inputbatch_agent_inventory_id_id__in=list(
    #             InputItemInputBatchAgentInventory.objects.filter(
    #                 agent_id=user_id
    #             ).values_list("id", flat=True)
    #         )
    #     ).count()

    # else:
    agent_profile_dict["have_seed_transaction"] = False
    return Response(agent_profile_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_agent_list_for_mobile(request):
    print(request.data)
    user_type_id = UserProfile.objects.get(user_id=request.user.id).user_type_id
    user_id = request.user.id
    season_id = get_active_season_id()
    print('user_id',user_id)
    subordinate_user_ids = []
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=get_active_season_id()).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=get_active_season_id()).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=get_active_season_id()).values_list('agent_id',flat=True))
    print(len(subordinate_user_ids))
    values = UserProfile.objects.filter(user_type_id=6, user_id__in=subordinate_user_ids).values_list("user_id", "user__username", "user__first_name","user__last_name","code","mobile", "village__name", "hobli__name")
    agent_columns = ["id","username","first_name","last_name","code","mobile","village","hobli",]
    agents_df = pd.DataFrame(list(values), columns=agent_columns)
    agents_df = agents_df.fillna(0)
    return Response(agents_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_data_for_agent_info(request):
    agent_dict = {}
    print(request.data)
    user_obj = User.objects.get(id=request.data["agent_user_id"])
    user_profile_obj = UserProfile.objects.get(user=user_obj)
    agent_dict["first_name"] = user_obj.first_name
    agent_dict["last_name"] = user_obj.last_name
    agent_dict["mobile"] = user_profile_obj.mobile
    agent_dict["code"] = user_profile_obj.code
    agent_dict["address"] = user_profile_obj.address
    agent_dict["district"] = user_profile_obj.district.name
    agent_dict["taluk"] = user_profile_obj.taluk.name
    agent_dict["hobli"] = user_profile_obj.hobli.name
    agent_dict["state"] = user_profile_obj.state.name
    agent_dict["pincode"] = user_profile_obj.pincode
    agent_dict["village"] = user_profile_obj.village.name
    agent_dict["latitude"] = user_profile_obj.latitude
    agent_dict["longitude"] = user_profile_obj.longitude

    # agreement
    if user_profile_obj.agreement_document != None:
        try:
            with open("static/media/" + str(user_profile_obj.agreement_document), "rb") as image_file:
                encoded_image1 = b64encode(image_file.read())
                agent_dict["agreement"] = "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
        except Exception as err:
            print(err)
            agent_dict["agreement"] = "no-image"
            pass
    # farmer
    season_id = get_active_season_id()
    if AgentFarmerMap.objects.filter(agent=user_obj, farmer__season_id=season_id).exists():
        agent_dict["farmer_count"] = AgentFarmerMap.objects.filter(agent=user_obj, farmer__season_id=season_id).count()
        farmer_list = list(AgentFarmerMap.objects.filter(agent=user_obj, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        if Sowing.objects.filter(farmer_id__in=farmer_list, season_id=season_id).exists():
            agent_dict["total_area"] = Sowing.objects.filter(farmer_id__in=farmer_list, season_id=season_id, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
        else:
            agent_dict["total_area"] = 0
    else:
        agent_dict["farmer_count"] = 0

    # seed transaction
    
    agent_dict["total_seeds_bought"] = 0
    agent_dict["balance_seeds"] = 0

    agent_dict["total_seeds_returned"] = 0

    # profile pic
    if UserImage.objects.filter(user=user_obj).exists():
        user_image = UserImage.objects.get(user=user_obj)
        try:
            with open("static/media/" + str(user_image["image"]), "rb") as image_file:
                encoded_image1 = b64encode(image_file.read())
                agent_dict["image"] = "data:image/jpeg;base64," + encoded_image1.decode("utf-8")
        except Exception as err:
            print(err)
            agent_dict["image"] = "no-image"
            pass

    # clusters
    if UserClusterMap.objects.filter(season_id=season_id, user=user_obj).exists():
        agent_dict["cluster"] = UserClusterMap.objects.filter(season_id=season_id, user=user_obj)[0].cluster.name
    else:
        agent_dict["cluster"] = "-"

    # procurement
    if ProcurementGroup.objects.filter(agent=user_obj,season_id=season_id).exists():
        agent_dict["total_procured_weight"] = ProcurementGroup.objects.filter(agent=user_obj, season_id=season_id).aggregate(Sum("produce_net_weight"))["produce_net_weight__sum"]/1000
        agent_dict["total_procured_cost"] = ProcurementGroup.objects.filter(agent=user_obj, season_id=season_id).aggregate(Sum("cost"))["cost__sum"]
    else:
        agent_dict["total_procured_weight"] = 0
        agent_dict["total_procured_cost"] = 0

    # agent wallet balance
    if AgentWallet.objects.filter(agent=user_obj).exists():
        agent_dict["wallet_balance"] = AgentWallet.objects.get(agent=user_obj).current_balance
    else:
        agent_dict["wallet_balance"] = 0

    return Response(agent_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_transaction_history_data_for_agent_date(request):
    date_list = list(set(list(InputDistributionTransactionMap.objects.filter(transaction_log__agent_id=request.data['agent_id']).values_list('transaction_log__date', flat=True))))
    return Response(date_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_transaction_history_data_for_agent(request):
    agent_inventry_list = list(InputDistributionTransactionMap.objects.filter(transaction_log__agent_id=request.data['agent_id'], transaction_log__date=request.data['date']).values_list(
        'agent_inventory__combo_issue_request__input_combo__name', 'agent_inventory__combo_issue_request__input_combo__price', 'agent_inventory__combo_issue_request__quantity_in_numbers', 'transaction_log__amount','agent_inventory__combo_issue_request__request_code', 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__wallet_balance_after_this_transaction'))
    agent_inventry_column = ['input_combo_name', 'input_combo_price', 'quantity', 'transaction_amount', 'request_code', 'wallet_before', 'wallet_after']
    agent_inventry_df = pd.DataFrame(agent_inventry_list, columns=agent_inventry_column)
    data = agent_inventry_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_farmers_under_agent(request):
    season_id = get_active_season_id()
    if AgentFarmerMap.objects.filter(agent_id=request.data["agent_id"], farmer__season_id=season_id).exists():
        farmer_ids = list(AgentFarmerMap.objects.filter(agent_id=request.data["agent_id"], farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        farmer_objs = Farmer.objects.filter(id__in=farmer_ids).order_by("first_name")
        farmer_values = farmer_objs.values_list("id","first_name","last_name","mobile","alternate_mobile","email","address","state_id","state__name","hobli_id","hobli__name","pincode","aadhaar_number","cultivated_for_ccgb_since","latitude","longitude","district_id","district__name","taluk_id","taluk__name","village_id","village__name","latitude","longitude",)
        farmer_columns = ["farmer_id","first_name","last_name","mobile","alternate_mobile","email","street","state_id","state__name","hobli_id","hobli_name","pincode","aadhaar_number","collaborated_with_company_on","latitude","longitude","district_id","district_name","taluk_id","taluk_name","village_id","village_name","latitude","longitude",]
        farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)
        #  farmer cluster
        farmer_cluster_map_values = FarmerClusterSeasonMap.objects.filter(season_id=season_id).values_list("id", "farmer_id", "seasonal_farmer_code", "cluster_id", "cluster__name")
        farmer_cluster_columns = ["farmer_cluster_map_id", "farmer_id", "code", "cluster_id", "cluster_name"]
        farmer_cluster_df = pd.DataFrame(list(farmer_cluster_map_values), columns=farmer_cluster_columns)
        # agent farmer map
        agent_farmer_map_values = AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id","farmer__farmer_id","agent__first_name","farmer__season__name","agent_id",)
        agent_farmer_columns = ["agent_farmer_map_id","farmer_id","agent_first_name","season_name","agent_id",]
        agent_farmer_df = pd.DataFrame(list(agent_farmer_map_values), columns=agent_farmer_columns)
        # agent profile
        agent_user_profile_values = UserProfile.objects.filter(user_type_id=6).values_list("id", "user_id", "mobile")
        agent_user_profile_columns = ["agent_user_profile_id", "user_id", "agent_mobile",]
        agent_user_profile_df = pd.DataFrame(list(agent_user_profile_values), columns=agent_user_profile_columns)

        # merge agent with agent profile
        user_profile_dict = pd.merge(agent_farmer_df,agent_user_profile_df,left_on="agent_id",right_on="user_id",how="left",)
        # merge farmer with agent
        merged_df = pd.merge(farmer_df,user_profile_dict,left_on="farmer_id",right_on="farmer_id",how="left",)
        # merge farmer with cluster
        
        farmer_cluster_merged_df = pd.merge(merged_df,farmer_cluster_df,left_on="farmer_id",right_on="farmer_id",how="left",)
        farmer_cluster_merged_df["total_main_crop_area"] = farmer_cluster_merged_df.apply(lambda x: find_main_crop_area(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["nursury_crop_age_list"] = farmer_cluster_merged_df.apply(lambda x: find_nursury_age_list(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["main_crop_age_list"] = farmer_cluster_merged_df.apply(lambda x: find_main_age_list(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["harvest_area"] = farmer_cluster_merged_df.apply(lambda x: get_harvest_area(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["harvest_qty"] = farmer_cluster_merged_df.apply(lambda x: get_harvest_qty(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["transplanting_gps_status"] = farmer_cluster_merged_df.apply(lambda x: get_gps_status(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["transplanting_gps_tag_status"] = farmer_cluster_merged_df.apply(lambda x: get_gps_tag_status(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["sowing_gps_status"] = farmer_cluster_merged_df.apply(lambda x: get_sowing_gps_status(x["farmer_id"], season_id), axis=1)
        farmer_cluster_merged_df["have_bank_account"] = farmer_cluster_merged_df.apply(lambda x: check_bank_details_available(x["farmer_id"]), axis=1)
        farmer_cluster_merged_df["input_distributed"] = farmer_cluster_merged_df.apply(lambda x: get_input_distribution_details(x["farmer_id"], season_id), axis=1)
        sowing_values = Sowing.objects.filter(farmer_id__in=farmer_ids).values_list("id","farmer_id","crop__name","cultivation_phase_id","cultivation_phase__name","sowing_date",)
        sowing_columns = ["sowing_id", "farmer_id", "crop_name", "cultivation_phase_id", "cultivation_phase__name", "sowing_date"]
        sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)
        today = datetime.date.today()
 
        sowing_df["crop_age_list"] = today - sowing_df["sowing_date"]
        sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype("timedelta64[D]")
        sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype(int)

        sowing_area_df = (sowing_df.groupby("farmer_id")["crop_age_list"].apply(list).to_frame())
        cultivation_phase_merge = (sowing_df.groupby("farmer_id")["cultivation_phase_id"].apply(list).to_frame())

        area_merge = pd.merge(farmer_cluster_merged_df,sowing_area_df,left_on="farmer_id",right_on="farmer_id",how="left",)
        phase_merge = pd.merge(area_merge,cultivation_phase_merge,left_on="farmer_id",right_on="farmer_id",how="left",)

        final_df = phase_merge.fillna(0)
        final_df = final_df.sort_values('code')
        final_df = final_df.to_dict("r")
    else:
        final_df = []

    return Response(final_df, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_agent_inventory_balance_combo_list(request):
    agent_id = request.data["agent_id"]
    sub_store_list = list(SubStoreIssueLabelAgentMap.objects.filter(agent_id=agent_id).values_list('agent_inventory__combo_issue_request__input_combo__name', 'agent_inventory__combo_issue_request__input_combo_id'))
    sub_store_column = ['combo_name', 'combo_id']
    sub_store_df = pd.DataFrame(sub_store_list, columns=sub_store_column)
    sub_store_df = sub_store_df.drop_duplicates()
    master_dict = sub_store_df.to_dict('r')
    return Response(master_dict, status=status.HTTP_200_OK)

@api_view(["POST"])
def get_agent_inventory_balance(request):
    agent_id = request.data["agent_id"]
    combo_id = request.data["combo_id"]
    sub_store_list = list(SubStoreIssueLabelAgentMap.objects.filter(agent_id=agent_id, agent_inventory__combo_issue_request__input_combo_id=combo_id).values_list('agent_id', 'label', 'label', 'agent_inventory__combo_issue_request__input_combo__area__quantity_in_acre'))
    sub_store_column = ['agent_id', 'lable', 'lable_count', 'area']
    sub_store_df = pd.DataFrame(sub_store_list, columns=sub_store_column)
    sub_store_df = sub_store_df.drop_duplicates()
    sub_store_df = sub_store_df.groupby('agent_id').agg({'lable':list, 'lable_count':'count', 'area':sum}).reset_index()
    master_dict = sub_store_df.to_dict('r')
    return Response(master_dict, status=status.HTTP_200_OK)


# remove sowing
@api_view(["POST"])
def remove_sowing(request):
    Sowing.objects.filter(id=request.data["sowing_id"]).delete()
    return Response(status=status.HTTP_200_OK)


# deactive the farmer from current season
@api_view(["POST"])
def deactivate_farmer(request):
    FarmerClusterSeasonMap.objects.filter(
        farmer_id=request.data["farmer_id"], season_id=2
    ).delete()
    return Response(status=status.HTTP_200_OK)


# serving farmers list for portal
def find_main_crop_area_portal(farmer_id, option):
    if option == "all":
        sowing_objs = Sowing.objects.filter()
    else:
        sowing_objs = Sowing.objects.filter(season_id=2)

    if sowing_objs.filter(farmer_id=farmer_id, cultivation_phase_id=2).exists():
        area = Sowing.objects.filter(
            farmer_id=farmer_id, cultivation_phase_id=2
        ).aggregate(Sum("area"))["area__sum"]
    else:
        area = 0
    return area


def find_nursury_crop_area_portal(farmer_id, option):
    if option == "all":
        sowing_objs = Sowing.objects.filter()
    else:
        sowing_objs = Sowing.objects.filter(season_id=2)

    if sowing_objs.filter(farmer_id=farmer_id, cultivation_phase_id=1).exists():
        area = sowing_objs.filter(
            farmer_id=farmer_id, cultivation_phase_id=1
        ).aggregate(Sum("area"))["area__sum"]
    else:
        area = 0
    return area


def find_nursury_age_list_portal(farmer_id, option):
    age_list = ""
    today = datetime.date.today()
    if option == "all":
        sowing_objs = Sowing.objects.filter()
    else:
        sowing_objs = Sowing.objects.filter(season_id=2)
    if sowing_objs.filter(farmer_id=farmer_id, cultivation_phase_id=1).exists():
        sowings = sowing_objs.filter(farmer_id=farmer_id, cultivation_phase_id=1)
        for sowing in sowings:
            diff = today - sowing.sowing_date
            age_list = str(diff.days) + ", " + age_list
    else:
        age_list = "-"
    return age_list


def find_main_age_list_portal(farmer_id, option):
    age_list = ""
    today = datetime.date.today()
    if option == "all":
        sowing_objs = Sowing.objects.filter()
    else:
        sowing_objs = Sowing.objects.filter(season_id=2)
    if sowing_objs.filter(farmer_id=farmer_id, cultivation_phase_id=2).exists():
        sowings = Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=2)
        for sowing in sowings:
            diff = today - sowing.sowing_date
            age_list = str(diff.days) + ", " + age_list
    else:
        age_list = "-"
    return age_list


# serve_farmers list
@api_view(["POST"])
def serve_farmers_for_portal(request):
    s_time = datetime.datetime.now()
    user_id = request.user.id
    season_id=request.data['season_id']
    print("superior id:", user_id)
    user_type_id = UserProfile.objects.get(user=user_id).user_type_id
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('supervisor_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('supervisor_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('supervisor_id',flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))
    subordinate_user_ids = list(UserProfile.objects.filter(user_id__in=subordinate_user_ids, user_type_id=5).values_list("user_id", flat=True))

    if UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids,farmer__season_id=season_id).exists():
        print('farmers found')
        # farmer
        print(subordinate_user_ids)
        if request.data["filter"] == "all":
            user_farmer_map_objs = UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids, farmer__season_id=season_id)
            farmer_season_map_objs = FarmerClusterSeasonMap.objects.filter()
            agent_farmer_map = AgentFarmerMap.objects.all()
            farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids).values_list("farmer__farmer_id", flat=True))
            sowings = Sowing.objects.filter()
        else:
            farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids, farmer__season_id=season_id,farmer__cluster_id__in=request.data["cluster_ids"],).values_list("farmer__farmer_id", flat=True))
            user_farmer_map_objs = UserFarmerMap.objects.filter(officer_id__in=subordinate_user_ids, farmer__cluster_id__in=request.data["cluster_ids"],farmer__season_id=season_id,)
            farmer_season_map_objs = FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer__cluster_id__in=request.data["cluster_ids"])
            agent_farmer_map = AgentFarmerMap.objects.filter(farmer__season_id=season_id, farmer__cluster_id__in=request.data["cluster_ids"])
            sowings = Sowing.objects.filter(season_id=season_id)

        farmer_objs = Farmer.objects.filter(id__in=farmer_ids).order_by("code")
        farmer_values = farmer_objs.values_list("id","first_name","last_name","mobile","village_id","village__name",)
        farmer_columns = ["farmer_id","first_name","last_name","mobile","village_id","village_name",]
        farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)

        #  farmer cluster
        # farmer_cluster_map_values = farmer_season_map_objs.values_list("id", "farmer_id", "seasonal_farmer_code", )
        # farmer_cluster_columns = ["farmer_cluster_map_id", "farmer_id", "code", "cluster_id", "cluster_name" ]
        # farmer_cluster_df = pd.DataFrame(list(farmer_cluster_map_values), columns=farmer_cluster_columns)

        # agent farmer map
        agent_farmer_map_values = agent_farmer_map.values_list("id","farmer__farmer_id","agent__first_name","farmer__season__name","agent_id","farmer__seasonal_farmer_code", "farmer__cluster_id", "farmer__cluster__name")
        agent_farmer_columns = ["agent_farmer_map_id", "farmer_id", "agent_first_name", "season_name", "agent_id","code", "cluster_id", "cluster_name"]
        agent_farmer_df = pd.DataFrame(list(agent_farmer_map_values), columns=agent_farmer_columns)

        # merge farmer with cluster

        farmer_cluster_merged_df = pd.merge( farmer_df, agent_farmer_df, left_on="farmer_id", right_on="farmer_id", how="left",)

        farmer_cluster_merged_df.assign(**{"total_main_crop_area": None, "total_nursury_crop_area": None})

        # farmer_cluster_merged_df['total_main_crop_area'] = farmer_cluster_merged_df.apply(lambda x:find_main_crop_area_portal(x['farmer_id'], request.data['filter']), axis=1)

        sowing_values = sowings.values_list("id", "farmer_id", "cultivation_phase_id", "area", "water_source__name")
        sowing_columns = ["id", "farmer_id", "cultivation_phase_id", "area", "water_resource_name"]
        sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)

        for index, row in farmer_cluster_merged_df.iterrows():
            main_area = sowing_df[(sowing_df["farmer_id"] == row["farmer_id"]) & (sowing_df["cultivation_phase_id"] == 2)]["area"].sum()
            farmer_cluster_merged_df.loc[index, "total_main_crop_area"] = main_area
            nursury_area = sowing_df[(sowing_df["farmer_id"] == row["farmer_id"]) & (sowing_df["cultivation_phase_id"] == 1)]["area"].sum()
            farmer_cluster_merged_df.loc[index, "total_nursury_crop_area"] = nursury_area
        farmer_cluster_merged_df["have_bank_account"] = farmer_cluster_merged_df.apply(lambda x: check_bank_details_available(x["farmer_id"]), axis=1)

        data = {}
        final_df = farmer_cluster_merged_df.fillna(0)
        farmer_bank_details = FarmerBankDetails.objects.filter(farmer_id__in=farmer_ids, is_active=True)
        farmer_bank_values = farmer_bank_details.values_list("farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name", "account_number")

        farmer_bank_columns = ["farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name",
                            "account_number"]
        farmer_bank_df = pd.DataFrame(list(farmer_bank_values), columns=farmer_bank_columns)
      

        transplant_sowing_values = Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2).values_list("id", "farmer_id", "cultivation_phase_id", "area", "water_source__name")
        transplant_sowing_columns = ["id", "farmer_id", "cultivation_phase_id", "area", "main_crop_water_resource_name"]
        transplant_sowing_df = pd.DataFrame(list(transplant_sowing_values), columns=transplant_sowing_columns)

        excel_df = pd.merge(final_df, transplant_sowing_df, left_on="farmer_id", right_on="farmer_id", how="left")
        excel_df = pd.merge(excel_df, farmer_bank_df, left_on="farmer_id", right_on="farmer_id", how="left")
        season_id = get_active_season_id()
        # excel_df['total_harvest'] = excel_df.apply(lambda x: get_harvest_qty(x['farmer_id'], season_id), axis=1) 
        excel_df= excel_df.drop(columns=['id','cultivation_phase_id', 'area'])
        excel_df= excel_df.fillna(0)
        excel_df
        # final_df = final_df.head(5)
        data["data"] = final_df.to_dict("r")
        # initializing excel
        writer = pd.ExcelWriter(str("static/media/") + "farmers_list.xlsx", engine="xlsxwriter")
        # creating excel sheet with name
        excel_df = excel_df.drop(columns=['farmer_id', 'village_id', 'agent_id','agent_farmer_map_id', 'cluster_id'])
        excel_df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)
        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:R1", "List Farmers with bank details" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 17, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(excel_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "farmers_list.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
    else:
        excel_df = []
        data = {"date": [], "excel": ""}
    return Response(data=data, status=status.HTTP_200_OK)


# serving stock data of agent for return input form
@api_view(["POST"])
def get_agent_stock_for_return(request):
    stock_dict = {}
    # agent_id = request.data["agent_id"]
    # print("agent_id :", agent_id)
    # if InputItemInputBatchAgentInventory.objects.filter(
    #         agent_id=agent_id, quantity_now__gt=0
    # ).exists():
    #     agent_stocks = InputItemInputBatchAgentInventory.objects.filter(
    #         agent_id=agent_id, quantity_now__gt=0
    #     )
    #     for stock in agent_stocks:
    #         if stock.item_batch_map.code not in stock_dict:
    #             stock_dict[stock.item_batch_map.code] = {}
    #             stock_dict[stock.item_batch_map.code]["quantity"] = 0
    #         stock_dict[stock.item_batch_map.code][
    #             "item_batch_map_id"
    #         ] = stock.item_batch_map.id
    #         stock_dict[stock.item_batch_map.code]["quantity"] += stock.quantity_now
    #         stock_dict[stock.item_batch_map.code]["unit_id"] = stock.unit.id
    return Response(stock_dict, status=status.HTTP_200_OK)


# save return log with adjusting storage
@api_view(["POST"])
def save_return_item(request):
    # adding a log on return data
    # input_item_return_log = InputItemReturnLog(
    #     returned_from_id=request.data["agent_id"],
    #     item_batch_map_id=request.data["item_batch_map_id"],
    #     quantity_returned=request.data["packet_count"],
    #     unit_id=request.data["unit_id"],
    #     date_of_return=request.data["return_date"],
    #     return_data_stored_by=request.user,
    #     label_range_from=request.data["label_from"],
    #     label_range_to=request.data["label_to"],
    # )
    # input_item_return_log.save()
    # print("return log created")

    # # adjust in agent inventory storage

    # agent_inventory = InputItemInputBatchAgentInventory.objects.filter(
    #     agent_id=request.data["agent_id"],
    #     quantity_now__gt=0,
    #     item_batch_map_id=request.data["item_batch_map_id"],
    # ).order_by("quantity_now")
    # return_packet_count = int(request.data["packet_count"])
    # amount_to_be_added_to_wallet = 0
    # for inventory in agent_inventory:
    #     if return_packet_count > 0:
    #         available_stock = agent_inventory.get(id=inventory.id).quantity_now
    #         if return_packet_count >= available_stock:
    #             return_packet_count = return_packet_count - available_stock
    #             # calcualting price to adjust wallet of agent
    #             input_amt = (
    #                     agent_inventory.get(id=inventory.id).price_per_item
    #                     * available_stock
    #             )
    #             print(
    #                 "if :",
    #                 input_amt,
    #                 agent_inventory.get(id=inventory.id).price_per_item,
    #             )
    #             amount_to_be_added_to_wallet += input_amt

    #             agent_inventory.filter(id=inventory.id).update(
    #                 quantity_now=0,
    #                 quantity_now_time=request.data["return_date"],
    #                 modified_by=request.user,
    #             )
    #             for label in AgentPacketLabel.objects.filter(
    #                     inputitem_inputbatch_agent_inventory_id=inventory.id,
    #                     stock_status_id=1,
    #             )[0:available_stock]:
    #                 AgentPacketLabel.objects.filter(id=label.id).update(
    #                     stock_status_id=3
    #                 )
    #         elif return_packet_count < available_stock:
    #             updated_available_quantity = available_stock - return_packet_count
    #             # calcualting price to adjust wallet of agent
    #             input_amt = (
    #                     agent_inventory.get(id=inventory.id).price_per_item
    #                     * return_packet_count
    #             )
    #             print(
    #                 "else :",
    #                 input_amt,
    #                 agent_inventory.get(id=inventory.id).price_per_item,
    #             )
    #             amount_to_be_added_to_wallet += input_amt
    #             return_packet_count = 0
    #             agent_inventory.filter(id=inventory.id).update(
    #                 quantity_now=updated_available_quantity,
    #                 quantity_now_time=request.data["return_date"],
    #                 modified_by=request.user,
    #             )
    #             for label in AgentPacketLabel.objects.filter(
    #                     inputitem_inputbatch_agent_inventory_id=inventory.id,
    #                     stock_status_id=1,
    #             )[0:updated_available_quantity]:
    #                 AgentPacketLabel.objects.filter(id=label.id).update(
    #                     stock_status_id=3
    #                 )
    #     else:
    #         print("agent inventory adjusted")

    # # adding in storage
    # storage_id = InputItemInputBatchStorageLocation.objects.filter(
    #     item_batch_map_id=request.data["item_batch_map_id"]
    # )[0].storage_id
    # quantity_now = InputItemInputBatchStorageLocation.objects.get(
    #     item_batch_map_id=request.data["item_batch_map_id"], storage_id=storage_id
    # ).quantity_now
    # InputItemInputBatchStorageLocation.objects.filter(
    #     item_batch_map_id=request.data["item_batch_map_id"], storage_id=storage_id
    # ).update(quantity_now=quantity_now + int(request.data["packet_count"]))

    # # adjust wallet of agent
    # agent_wallet = AgentWallet.objects.get(agent_id=request.data["agent_id"])
    # before_transaction_balance = agent_wallet.current_balance
    # agent_wallet.current_balance = (
    #         before_transaction_balance + amount_to_be_added_to_wallet
    # )
    # print(amount_to_be_added_to_wallet)
    # agent_wallet.save()

    # # add transaction log
    # agent_transaction_log_obj = AgentTransactionLog.objects.create(
    #     date=request.data["return_date"],
    #     transaction_direction_id=3,
    #     agent_id=request.data["agent_id"],
    #     data_entered_by=request.user,
    #     amount=amount_to_be_added_to_wallet,
    #     transaction_id="return" + str(input_item_return_log.id),
    #     transaction_mode_id=1,
    #     transaction_approval_status_id=1,
    #     wallet_balance_before_this_transaction=before_transaction_balance,
    #     wallet_balance_after_this_transaction=before_transaction_balance
    #                                           + amount_to_be_added_to_wallet,
    #     modified_by=request.user,
    # )
    # agent_transaction_log_obj.save()

    # # transaction and retrun maping
    # InputReturnTransactionMap.objects.create(
    #     transaction_log=agent_transaction_log_obj,
    #     input_item_return=input_item_return_log,
    # )
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_return_history_date(request):
    date_list = list(set(list(InputReturnTransactionLog.objects.filter(transaction_log__agent_id=request.data['agent_id']).values_list('transaction_log__date', flat=True))))
    return Response(date_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_return_history(request):
    input_retutn_list = list(InputReturnTransactionLog.objects.filter(transaction_log__agent_id=request.data['agent_id'], transaction_log__date=request.data['date']).values_list('combo_return_request_id', 'combo_return_request__input_combo__name', 'combo_return_request__comboreturnrequestlabelmap__return_label__label', 'combo_return_request__comboreturnrequestlabelmap__return_label__label', 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__wallet_balance_after_this_transaction', 'transaction_log__amount'))
    input_retutn_column = ['return_request_id', 'input_combo', 'quantity', 'label', 'wallet_before', 'wallet_after', 'amount']
    input_retutn_df = pd.DataFrame(input_retutn_list, columns=input_retutn_column)
    input_retutn_df = input_retutn_df.groupby('return_request_id').agg({'input_combo': 'first', 'wallet_before':'first', 'wallet_after': 'first', 'amount': 'first', 'label':list, 'quantity':'count'}).reset_index()
    input_retutn_df['label'] = input_retutn_df['label'].astype(str)
    master_list = input_retutn_df.to_dict('r')
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_procurement(request):
    print('agentttttttttttt', request.data["agent_id"])
    season_id = get_active_season_id()
    procurement_group_obj = ProcurementGroup(
        agent_id=request.data["agent_id"],
        procurement_date=request.data["procurement_date"],
        procurement_produce_id=request.data["produce_id"],
        season_id=season_id,
        produce_net_weight=request.data["produce_net_weight"],
        price_per_unit=request.data["price_per_unit"],
        unit_for_pricing_id=1,
        cost=request.data["cost"],
        payment_to_wallet=request.data["payment_to_wallet"],
        payment_to_agent=request.data["payment_to_agent"],
        agent_price_deduction=request.data["deduction_percentage"],
        created_by=request.user,
        modified_by=request.user,
    )
    print('user_idddddd',request.user.id)
    user_id = request.user.id
    procurement_group_obj.save()
   
    print("procurement grp saved")
    procurement_transport_incharge_kyc_obj = ProcurementTransportInchargeKyc(aadhar_number=request.data["aadhar_number"])

    procurement_transport_incharge_kyc_obj.save()
    print("kyc added")

    if not Procurement.objects.filter(ticket_number=request.data["ticket_number"]).exists():
        try:
            procurement_obj = Procurement(
                procurement_group=procurement_group_obj,
                procurement_transaport_incharge_kyc=procurement_transport_incharge_kyc_obj,
                ticket_number=request.data["ticket_number"],
                vehicle_number=request.data["vehicle_number"],
                vehicle_driver_name=request.data["driver_name"],
                empty_vehicle_timestamp=request.data["empty_vehicle_timestamp"],
                empty_vehicle_weight=request.data["empty_vehicle_weight"],
                empty_vehicle_weight_data_inputed=request.data[
                    "empty_vehicle_operated_by"
                ],
                loaded_vehicle_weight_data_inputed=request.data[
                    "loaded_vehicle_operated_by"
                ],
                moisture=request.data["moisture"],
                loaded_vehicle_timestamp=request.data["loaded_vehicle_timestamp"],
                loaded_vehicle_weight=request.data["loaded_vehicle_weight"],
                str_weight=request.data["str_weight"],
                str_weight_unit_id=request.data["str_weight_unit_id"],
                gunnybag_count=request.data["gunnybag_count"],
                gunnybag_weight=request.data["gunnybag_weight"],
                produce_gross_weight=request.data["produce_gross_weight"],
                unit_id=request.data["unit"],
                other_deduction=request.data["other_deduction"],
                paymet_status_id = 1    #initialy payment_status_id is 1(received)
            )
            if not AgentMergeloadEnable.objects.filter(season_id=get_active_season_id(), agent_id=request.data["agent_id"]).exists():
                agent_merge_obj = AgentMergeloadEnable(season_id=get_active_season_id(),
                                                       agent_id=request.data["agent_id"])
                agent_merge_obj.save()

            have_other_agent_farmer=AgentMergeloadEnable.objects.get(season_id=get_active_season_id(), agent_id=request.data["agent_id"]).is_active
            
            if "reason_for_weight_loss" in request.data:
                procurement_obj.reason_for_weight_loss = request.data["reason_for_weight_loss"]

            procurement_obj.save()
            print("procurement process saved")
            # print('have_other_agent_farmer:',AgentMergeloadEnable.objects.get(season_id=get_active_season_id(), agent_id=request.data["agent_id"]).is_active)
        
             #TempProcurement
            print(procurement_obj.ticket_number)
            temp_procurment_obj = TempProcurement.objects.get(ticket_number=procurement_obj.ticket_number)
            temp_procurment_obj.is_uploaded = True
            temp_procurment_obj.save()
            print('id:::', procurement_obj.id)
            agent_procurement_transaction_log(procurement_obj.id, user_id)
            print('agent_log_transaction_ok')
            # # agent wallet adjustment
            # if not AgentWallet.objects.filter(agent_id=request.data["agent_id"]).exists():
            #     updated_amount = request.data["payment_to_wallet"]
            #     old_balance = 0
            #     print("type : ", updated_amount)
            #     AgentWallet.objects.create(
            #         agent_id=request.data["agent_id"],
            #         current_balance=updated_amount,
            #         modified_by=request.user,
            #     )
            #     new_balance = updated_amount

            # # existing wallet
            # else:
            #     old_balance = AgentWallet.objects.get(agent_id=request.data["agent_id"]).current_balance
            #     updated_amount = old_balance + request.data["payment_to_wallet"]
            #     AgentWallet.objects.filter(agent_id=request.data["agent_id"]).update(current_balance=Decimal(updated_amount), modified_by=request.user)
            #     new_balance = updated_amount

            # # add transaction log for money deposit to wallet
            # # trans 1     
            # # add transaction log for wallet adjustment
            # agent_transaction_log = AgentTransactionLog(
            #     date=request.data["procurement_date"],
            #     transaction_direction_id=2,  # ccgb to agent wallet when wallet adjustment - positive
            #     agent_id=request.data["agent_id"],
            #     data_entered_by=request.user,
            #     amount=request.data["payment_to_wallet"],
            #     transaction_id="1234",
            #     transaction_mode_id=1,
            #     transaction_approval_status_id=1,
            #     wallet_balance_before_this_transaction=old_balance,
            #     wallet_balance_after_this_transaction=new_balance,
            #     description="it will be added as a positive amount in agent wallet as a commision for wallet adjustment",
            #     modified_by=request.user,
            # )
            # agent_transaction_log.save()
            # # mapping procurement log with the transaction log
            # procurement_obj = Procurement.objects.get(id=request.data['id'])
            # ProcurementTransactionMap.objects.create(transaction_log=agent_transaction_log, procurement=procurement_obj)
            
            # # trans 2
            # # add transaction log for agent commission
            # agent_transaction_log = AgentTransactionLog(
            #     date=request.data["procurement_date"],
            #     transaction_direction_id=3,  # after the wallet adjustment , remaining money to agent hand 
            #     agent_id=request.data["agent_id"],
            #     data_entered_by=request.user,
            #     amount=request.data["payment_to_agent"],
            #     transaction_id="1234",
            #     transaction_mode_id=1,
            #     transaction_approval_status_id=1,
            #     wallet_balance_before_this_transaction=old_balance,
            #     wallet_balance_after_this_transaction=new_balance,
            #     description="it will be given to agent hand after the wallet adjustment",
            #     modified_by=request.user,
            # )
            # agent_transaction_log.save()
            # # mapping procurement log with the transaction log
            # # procurement_obj = Procurement.objects.get(id=row['id'])
            # ProcurementTransactionMap.objects.create(transaction_log=agent_transaction_log, procurement=procurement_obj)
        except Exception as err:
            print(err)
            pass
        
    else:
        print("already added")
    return Response(status=status.HTTP_200_OK)


def get_all_procurement_list(procurement_group_id):
    procurement_objs = Procurement.objects.filter(procurement_group_id=procurement_group_id)
    procurement_list = list(procurement_objs.values_list("id", "procurement_transaport_incharge_kyc__aadhar_number", "procurement_transaport_incharge_kyc__name", "empty_vehicle_weight", "loaded_vehicle_weight", "gunnybag_count", "gunnybag_weight", "produce_gross_weight", "unit__id", "unit__name",))
    procurement_columns = ["procurement_id","transaport_incharge_kyc_aadhar_number","transaport_incharge_kyc_name","empty_vehicle_weight","loaded_vehicle_weight","gunnybag_count","gunnybag_weight","produce_gross_weight","unit_id","unit_name",]
    procurement_df = pd.DataFrame(procurement_list, columns=procurement_columns)
    procurement_list = procurement_df.to_dict("r")
    return procurement_list


@api_view(["POST"])
def serve_procurement_transaction_date(request):
    procurement_group_objs = InputProcurementTransactionLog.objects.filter(procurement__procurement_group__agent_id=request.data["agent_id"])
    procurement_group_list = list(set(list(procurement_group_objs.values_list("procurement__procurement_group__procurement_date", flat=True))))
    procurement_group_list = sorted(procurement_group_list, reverse=True)
    return Response(procurement_group_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_procurement_transaction(request):
    procurement_group_objs = InputProcurementTransactionLog.objects.filter(procurement__procurement_group__agent_id=request.data["agent_id"], procurement__procurement_group__procurement_date=request.data['date']).order_by('-procurement__procurement_group__procurement_date')
    procurement_group_list = procurement_group_objs.values_list("procurement__procurement_group_id","procurement__procurement_group__procurement_date","procurement__procurement_group__produce_net_weight","procurement__procurement_group__cost","procurement__procurement_group__payment_to_wallet","procurement__procurement_group__payment_to_agent","procurement__procurement_group__price_per_unit", 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__wallet_balance_after_this_transaction')
    procurement_group_columns = ["procurement_group_id","procurement_date","produce_net_weight","cost","payment_to_wallet","payment_to_agent","price_per_unit", "wallet_before", "wallet_after"]
    procurement_group_df = pd.DataFrame(list(procurement_group_list), columns=procurement_group_columns)
    procurement_group_df = procurement_group_df.drop_duplicates()
    procurement_group_df["procurement_list"] = procurement_group_df.apply(lambda x: get_all_procurement_list(x["procurement_group_id"]), axis=1)
    data = procurement_group_df.to_dict('r')
    print(data)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_yeild_forecast_data_one(request):
    season_id = get_active_season_id()

    print(request.data)
    # cluster
    if len(request.data["cluster_ids"]) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list("id", flat=True))
    # super_visor
    if len(request.data["super_visor_ids"]) == 0:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True))
    else:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5, user_id__in=request.data["super_visor_ids"]).values_list("user_id", flat=True))
    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    else:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6, user_id__in=request.data["agent_ids"]).values_list("user_id", flat=True))

    #  farmer cluster
    cluster_based_farmers_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list("farmer_id", flat=True))

    # supervisor_based
    user_farmer_ids = list(
        UserFarmerMap.objects.filter(
            officer_id__in=supervisor_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=cluster_based_farmers_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # agent farmer map
    farmer_ids = list(
        AgentFarmerMap.objects.filter(
            agent_id__in=agent_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=user_farmer_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # sowing modules
    nursery_sowing_values = Sowing.objects.filter(
        farmer_id__in=farmer_ids, cultivation_phase_id=1
    ).values_list(
        "id",
        "area",
        "farmer_id",
        "crop__name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    )
    nursery_sowing_columns = [
        "sowing_id",
        "area",
        "farmer_id",
        "crop_name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    ]
    nursery_sowing_df = pd.DataFrame(
        list(nursery_sowing_values), columns=nursery_sowing_columns
    )

    # calculate the age of sowing from today date
    converted_today = datetime.datetime.strptime(
        request.data["selected_date"], "%Y-%m-%d"
    )
    today = converted_today.date()

    #
    nursery_sowing_df["crop_age_list"] = today - nursery_sowing_df["sowing_date"]
    nursery_sowing_df["crop_age_list"] = nursery_sowing_df["crop_age_list"].astype(
        "timedelta64[D]"
    )
    nursery_sowing_df["crop_age_list"] = nursery_sowing_df["crop_age_list"].astype(int)

    nursery_predict_dict = {}
    for i in range(1, 201):
        if i not in nursery_predict_dict:
            nursery_predict_dict[i] = nursery_sowing_df[
                nursery_sowing_df["crop_age_list"] == i
                ]["area"].sum()

    # area wise
    nursery_harvest_dict = {}
    for harvest in HarvestLevel.objects.all():
        notice_period = harvest.notice_period
        calculated_acre = 0
        expected_range = YeildPrediction.objects.get(
            harvest_range_id=harvest.harvest_name
        ).expected_yeild_weight_in_kg
        # for j in range(1,int(notice_period)+1):
        #     calculated_acre +=  nursery_predict_dict[int(harvest.harvest_interval_duration_in_days) + j]
        #     calculated_acre +=  nursery_predict_dict[int(harvest.harvest_interval_duration_in_days) - j]
        calculated_acre += nursery_predict_dict[
            int(harvest.harvest_interval_duration_in_days)
        ]
        nursery_harvest_dict[
            harvest.harvest_interval_duration_in_days
        ] = calculated_acre
        # harvest_dict[harvest.harvest_interval_duration_in_days] = str(calculated_acre) + '(' + str(Decimal(calculated_acre) * expected_range) + ')'

    # quantity wise
    nursery_harvest_qty_dict = {}
    for harvest in HarvestLevel.objects.all():
        notice_period = harvest.notice_period
        calculated_acre = 0
        expected_range = YeildPrediction.objects.get(
            harvest_range_id=harvest.harvest_name
        ).expected_yeild_weight_in_kg
        # for j in range(1,int(notice_period)+1):
        #     calculated_acre +=  nursery_predict_dict[int(harvest.harvest_interval_duration_in_days) + j]
        #     calculated_acre +=  nursery_predict_dict[int(harvest.harvest_interval_duration_in_days) - j]
        calculated_acre += nursery_predict_dict[
            int(harvest.harvest_interval_duration_in_days)
        ]
        nursery_harvest_qty_dict[harvest.harvest_interval_duration_in_days] = (
                                                                                      Decimal(
                                                                                          calculated_acre) * expected_range
                                                                              ) / 1000
        # print('------------------')

    #  transplanted module prediction
    # sowing modules
    transplanted_sowing_values = Sowing.objects.filter(
        farmer_id__in=farmer_ids, cultivation_phase_id=2
    ).values_list(
        "id",
        "area",
        "farmer_id",
        "crop__name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    )
    transplanted_sowing_columns = [
        "sowing_id",
        "area",
        "farmer_id",
        "crop_name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    ]
    transplanted_sowing_df = pd.DataFrame(
        list(transplanted_sowing_values), columns=transplanted_sowing_columns
    )

    # calculate the age of sowing from today date
    transplanted_sowing_df["crop_age_list"] = (
            today - transplanted_sowing_df["sowing_date"]
    ).days
    # transplanted_sowing_df['crop_age_list'] = transplanted_sowing_df['crop_age_list'].astype('timedelta64[D]')
    # transplanted_sowing_df['crop_age_list'] = transplanted_sowing_df['crop_age_list'].astype(int)

    harvest_levels = HarvestLevel.objects.filter().values_list(
        "harvest_interval_duration_in_days", flat=True
    )
    transplanted_predict_dict = {}
    for i in harvest_levels:
        transplanted_predict_dict[i] = transplanted_sowing_df[
            transplanted_sowing_df["crop_age_list"] == i
            ]["area"].sum()

    # area wise
    total_area = 0
    transplanted_harvest_dict = {}
    for harvest in HarvestLevel.objects.all():
        notice_period = harvest.notice_period
        calculated_acre = 0
        expected_range = YeildPrediction.objects.get(
            harvest_range_id=harvest.harvest_name
        ).expected_yeild_weight_in_kg
        # for j in range(1,int(notice_period)+1):
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) + j]
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) - j]
        calculated_acre += transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days)]
        transplanted_harvest_dict[
            harvest.harvest_interval_duration_in_days
        ] = calculated_acre
        total_area += calculated_acre

        # harvest_dict[harvest.harvest_interval_duration_in_days] = str(calculated_acre) + '(' + str(Decimal(calculated_acre) * expected_range) + ')'

    # quantity wise
    total_harvest = 0
    transplanted_harvest_qty_dict = {}
    for harvest in HarvestLevel.objects.all():
        notice_period = harvest.notice_period
        calculated_acre = 0
        expected_range = YeildPrediction.objects.get(
            harvest_range_id=harvest.harvest_name
        ).expected_yeild_weight_in_kg
        # for j in range(1,int(notice_period)+1):
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) + j]
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) - j]
        # print(int(harvest.harvest_interval_duration_in_days))
        calculated_acre += transplanted_predict_dict[
            int(harvest.harvest_interval_duration_in_days)
        ]
        transplanted_harvest_qty_dict[harvest.harvest_interval_duration_in_days] = (
                                                                                           Decimal(
                                                                                               calculated_acre) * expected_range
                                                                                   ) / 1000
        total_harvest += (Decimal(calculated_acre) * expected_range) / 1000

        # print('------------------')

    master_dict = {
        "prediction": nursery_predict_dict,
        "nursery_area_wise": nursery_harvest_dict,
        "nursery_quantity_wise": nursery_harvest_qty_dict,
        "transplanted_area_wise": transplanted_harvest_dict,
        "transplanted_quantity_wise": transplanted_harvest_qty_dict,
        "total_transplanted_area": total_area,
        "total_transplanted_qty": total_harvest,
    }
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_farmer_nursery_data(request):
    print(request.data["farmer_id"])
    farmer_id = request.data["farmer_id"]
    if Sowing.objects.filter(farmer_id=farmer_id, cultivation_phase_id=1).exists():
        nursery_sowing_obj = Sowing.objects.filter(
            farmer_id=farmer_id, cultivation_phase_id=1
        )[0]
        data = {}
        data["water_source_id"] = nursery_sowing_obj.water_source_id
        data["irrigation_method_id"] = nursery_sowing_obj.irrigation_method_id
        data["water_type_id"] = nursery_sowing_obj.water_type_id
        data["soil_type_id"] = nursery_sowing_obj.soil_type_id
    else:
        data = "no_nursery_sowing"
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_by_aadhar_number(request):
    if UserProfile.objects.filter(aadhaar_number=request.data["aadhaar_number"]).exists():
        agent_id = UserProfile.objects.get(aadhaar_number=request.data["aadhaar_number"]).user.id
    else:
        agent_id = "not_found"
    data = {"agent_id": agent_id,}
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_produce_list(request):
    produces = Crop.objects.all()
    produces_list = []
    for produce in produces:
        produce_dict = {}
        produce_dict["name"] = produce.name
        produce_dict["id"] = produce.id
        produces_list.append(produce_dict)
    return Response(produces_list, status=status.HTTP_200_OK)


def get_total(date):
    total_value = ProcurementGroup.objects.filter(procurement_date=date).aggregate(
        Sum("produce_net_weight")
    )["produce_net_weight__sum"]
    return total_value


def get_harvest_list(ticket_number, date):
    data = []
    if Harvest.objects.filter(ticket_number=ticket_number).exists():
        harvest_values = list(
            Harvest.objects.filter(ticket_number=ticket_number).order_by("date_of_harvest").values_list("id","sowing__farmer__first_name","sowing__farmer__id","date_of_harvest","value","unit__name","ticket_number",))
        harvest_columns = ["harvest_id","farmer_name","farmer_id","date_of_harvest","value","unit_name","ticket_number",]
        harvest_df = pd.DataFrame(harvest_values, columns=harvest_columns)
        filtered_farmers_id = list(Harvest.objects.filter(ticket_number=ticket_number).values_list('sowing__farmer__id', flat=True))
        season_id=get_active_season_id()
        season_farmer_df = pd.DataFrame(FarmerClusterSeasonMap.objects.filter(farmer__id__in=filtered_farmers_id, season_id=season_id).values())
        merged_df = pd.merge(harvest_df,season_farmer_df, how="left", left_on="farmer_id", right_on="farmer_id")
        merged_df = merged_df.rename(columns={"seasonal_farmer_code": "farmer_code"})
        data = merged_df.to_dict("r")
    return data


def get_harvest_status(ticket_number, str):
    data = False
    if Harvest.objects.filter(ticket_number=ticket_number).exists():
        harvest_total = Harvest.objects.filter(ticket_number=ticket_number).aggregate(
            Sum("value")
        )["value__sum"]
        if harvest_total == str:
            data = True
    return data


@api_view(["GET"])
def serve_procurement_log(request):
    season_id = get_active_season_id()
    data = list(set(list(Procurement.objects.filter(procurement_group__season_id=season_id).order_by("procurement_group__procurement_date").values_list("procurement_group__procurement_date", flat=True))))
    # print(data)
    data = sorted(data, reverse=True)
    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
def serve_procurement_hold_log(request):
    season_id = get_active_season_id()
    data = list(set(list(Procurement.objects.filter(procurement_group__season_id=season_id, paymet_status_id=2).order_by("procurement_group__procurement_date").values_list("procurement_group__procurement_date", flat=True))))
    # print(data)
    data = sorted(data, reverse=True)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_utr_number_log(request):
    season_id = get_active_season_id()
    data = list(set(list(Procurement.objects.filter(procurement_group__season_id=season_id).exclude(utr_number=None).order_by("procurement_group__procurement_date").values_list("procurement_group__procurement_date", flat=True))))
    # print(data)
    data = sorted(data, reverse=True)
    return Response(data, status=status.HTTP_200_OK)



@api_view(["POST"])
def get_procurement_date_wise(request):
    print(request.data)
    if 'not_hold' in request.data:
        if "procurement_date" in request.data["procurement_date"]:
            date = request.data["procurement_date"]['procurement_date']
        else:
            date = request.data["procurement_date"]
            print(date)
        print('not hold data')
        Procurement_obj = Procurement.objects.filter(procurement_group__procurement_date=date).exclude(paymet_status_id=2)
    elif 'hold' in request.data:   #it will show only hold dates
        print('hold_data')
        season_id = get_active_season_id()
        if "procurement_date" in request.data["procurement_date"]:
            date = request.data["procurement_date"]['procurement_date']
        else:
            date = request.data["procurement_date"]
        Procurement_obj = Procurement.objects.filter(paymet_status_id=2, procurement_group__procurement_date=date)
        print(Procurement_obj)
    elif 'utr' in request.data:
        print('utr_data')
        if "procurement_date" in request.data["procurement_date"]:
            date = request.data["procurement_date"]['procurement_date']
        else:
            date = request.data["procurement_date"]
        Procurement_obj = Procurement.objects.filter(procurement_group__procurement_date=date).exclude(utr_number__isnull=True)
        print(Procurement_obj.count())
    procurement_values = list(Procurement_obj.values_list("id", "ticket_number", "vehicle_number", "vehicle_driver_name", "str_weight",
                                    "str_weight_unit__name",
                                    "remark", "empty_vehicle_timestamp", "empty_vehicle_weight_data_inputed",
                                    "empty_vehicle_weight", "loaded_vehicle_timestamp",
                                    "loaded_vehicle_weight_data_inputed", "loaded_vehicle_weight", "gunnybag_count",
                                    "gunnybag_weight", "moisture", "produce_gross_weight",
                                    "unit__name", "procurement_group_id", "procurement_group__agent_id",
                                    "procurement_group__agent__first_name", "procurement_group__procurement_date",
                                    "procurement_group__procurement_produce__name",
                                    "procurement_group__procurement_produce__id", "procurement_group__season_id",
                                    "procurement_group__produce_net_weight", "procurement_group__price_per_unit",
                                    "procurement_group__unit_for_pricing", "procurement_group__cost",
                                    "procurement_group__payment_to_wallet", "procurement_group__payment_to_agent",
                                    "procurement_group__agent_price_deduction", "have_other_agent_farmer", "reason_for_payment_hold", "utr_number"))

    procurement_columns = ["procurement_id", "ticket_number", "vehicle_number", "vehicle_driver_name", "str_weight",
                           "str_weight_unit_name", "remark", "empty_vehicle_timestamp",
                           "empty_vehicle_weight_data_inputed", "empty_vehicle_weight", "loaded_vehicle_timestamp",
                           "loaded_vehicle_weight_data_inputed", "loaded_vehicle_weight", "gunnybag_count",
                           "gunnybag_weight", "moisture", "produce_gross_weight", "unit_name", "procurement_group_id",
                           "agent_id", "agent_username", "procurement_date", "procurement_produce_name",
                           "procurement_produce_id", "season_id", "produce_net_weight", "price_per_unit",
                           "unit_for_pricing", "cost", "payment_to_wallet", "payment_to_agent", "agent_price_deduction",
                           "have_other_agent_farmer", "hold_reason", "utr_number"]
    procurement_df = pd.DataFrame(procurement_values, columns=procurement_columns)
    procurement_df = procurement_df.fillna('-')
    if not procurement_df.empty:
        procurement_df["ticket_number"] = procurement_df["ticket_number"].astype("|S")
        procurement_df["total_day_net_value"] = procurement_df.apply(lambda x: get_total(x["procurement_date"]), axis=1)
        procurement_df["harvest_list"] = procurement_df.apply(lambda x: get_harvest_list(x["ticket_number"], x["procurement_date"]), axis=1)
        procurement_df["harvest_completed"] = procurement_df.apply(lambda x: get_harvest_status(x["ticket_number"], x["str_weight"]), axis=1)
        procurement_df.sort_values(by=["procurement_date"], inplace=True)
        # if data_dict_from_interface['get_only_pending']:
        #     procurement_df = procurement_df[procurement_df['harvest_completed'] == False]
        data = {}
        # data["data"] = procurement_df.to_dict("r")
        data["data_available"] = True
        
        data["total_weight_for_selected_date"] = Procurement.objects.filter(procurement_group__procurement_date=date).aggregate(Sum("procurement_group__produce_net_weight"))["procurement_group__produce_net_weight__sum"]
        data['data'] = procurement_df.to_dict('r')
    else:
        data = {}
        data["data_available"] = False
        data["data"] = 'no data found for selected filters'
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def check_for_procurement_exists(request):
    received_ticket_list = request.data
    print(received_ticket_list["tickets"])
    data_dict = {}
    for ticket in received_ticket_list["tickets"]:
        if Procurement.objects.filter(ticket_number=ticket).exists():
            data_dict[ticket] = True
        else:
            data_dict[ticket] = False
    print(data_dict[ticket])
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def serve_procurement_summary(request):
    # master dict
    data_dict = {}
    user_id = request.user.id
    season_id= get_active_season_id()
    print("superior id:", user_id)
    user_type_id = UserProfile.objects.get(user=user_id).user_type_id
    if user_type_id == 5:
        users_cluster_ids = list(set(list(UserClusterMap.objects.filter(user_id=user_id, season_id=season_id).values_list('cluster_id', flat=True))))
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=user_id, season_id=season_id).values_list('agent_id', flat=True))
        print('subordinate_user_ids:', subordinate_user_ids)
    elif user_type_id == 3:
        if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
            subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
            subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
            print("one")
            subordinate_user_ids = list(set(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True)))
            users_cluster_ids = list(set(list(UserClusterMap.objects.filter(user_id__in=subordinate_user_ids, season_id=season_id).values_list('cluster_id', flat=True))))
    else:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
        users_cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))

    Procurement_obj = Procurement.objects.filter(procurement_group__season_id=season_id, procurement_group__agent_id__in=subordinate_user_ids)
    procurement_values = list(
        Procurement_obj.values_list("id", "ticket_number", "vehicle_number", "vehicle_driver_name", "str_weight",
                                    "str_weight_unit__name",
                                    "remark", "empty_vehicle_timestamp", "empty_vehicle_weight_data_inputed",
                                    "empty_vehicle_weight", "loaded_vehicle_timestamp",
                                    "loaded_vehicle_weight_data_inputed", "loaded_vehicle_weight", "gunnybag_count",
                                    "gunnybag_weight", "moisture", "produce_gross_weight",
                                    "unit__name", "procurement_group_id", "procurement_group__agent_id",
                                    "procurement_group__agent__first_name", "procurement_group__procurement_date",
                                    "procurement_group__procurement_produce__name",
                                    "procurement_group__procurement_produce__id", "procurement_group__season_id",
                                    "procurement_group__produce_net_weight", "procurement_group__price_per_unit",
                                    "procurement_group__unit_for_pricing", "procurement_group__cost",
                                    "procurement_group__payment_to_wallet", "procurement_group__payment_to_agent",
                                    "procurement_group__agent_price_deduction", "have_other_agent_farmer"))
    procurement_columns = ["procurement_id", "ticket_number", "vehicle_number", "vehicle_driver_name", "str_weight",
                        "str_weight_unit_name", "remark", "empty_vehicle_timestamp",
                        "empty_vehicle_weight_data_inputed", "empty_vehicle_weight", "loaded_vehicle_timestamp",
                        "loaded_vehicle_weight_data_inputed", "loaded_vehicle_weight",
                        "gunnybag_count", "gunnybag_weight", "moisture", "produce_gross_weight", "unit_name",
                        "procurement_group_id", "agent_id", "agent_username", "procurement_date",
                        "procurement_produce_name", "procurement_produce_id", "season_id", "produce_net_weight",
                        "price_per_unit", "unit_for_pricing", "cost", "payment_to_wallet",
                        "payment_to_agent", "agent_price_deduction", "have_other_agent_farmer", ]
    procurement_df = pd.DataFrame(procurement_values, columns=procurement_columns)
    
    user_cluster_obj = list(UserClusterMap.objects.filter(season_id=season_id, user_id__in=subordinate_user_ids).values_list('user_id', 'cluster_id', 'cluster__name'))
    user_cluster_columns = ['agent_id', 'cluster_id', 'cluster_name']
    user_cluster_df = pd.DataFrame(user_cluster_obj, columns=user_cluster_columns)
    
    procurement_cluster_map = procurement_df.merge(user_cluster_df, left_on="agent_id", right_on="agent_id", how="left")
    
    # overall season net total procurement quantity
    total_season_procurement_weight = ProcurementGroup.objects.filter(season_id=season_id).aggregate(Sum("produce_net_weight"))["produce_net_weight__sum"]
    data_dict["overall_season_total_weight"] = round(procurement_df['produce_net_weight'].sum() / 1000, 3)
    data_dict["overall_season_total_weight"] = procurement_df['produce_net_weight'].sum()


    procurement_cluster_map = procurement_cluster_map.drop_duplicates(subset='procurement_id', keep="last")

    procurement_cluster_map = procurement_cluster_map.fillna(0)
#     display(HTML(procurement_cluster_map.to_html()))
    start_date = ProcurementGroup.objects.filter(season_id=season_id, agent_id__in=subordinate_user_ids).order_by('procurement_date')[0].procurement_date
    first_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
    today = datetime.datetime.now()
    week_data_dict = {}
    while today > first_date:
        second_date = first_date + datetime.timedelta(days=7)
        if not procurement_cluster_map[(procurement_cluster_map['procurement_date'] > first_date.date()) & (
                procurement_cluster_map['procurement_date'] < second_date.date())].empty:
            week_value = round(procurement_cluster_map[
                                (procurement_cluster_map['procurement_date'] >= first_date.date()) & (
                                        procurement_cluster_map['procurement_date'] <= second_date.date())][
                                'produce_net_weight'].sum() / 1000)
        else:
            week_value = 0
        week_data_dict[str(first_date.strftime("%b %d")) + "-" + str(second_date.strftime("%d"))] = week_value
        first_date = second_date + datetime.timedelta(days=1)
    data_dict["weekwise_data"] = week_data_dict
    week_data_dict
    print(data_dict)
    
    # individual agent wise
    agent_wise_dict = {}
    agent_username_dict = {}
    users = User.objects.filter(id__in=subordinate_user_ids)
    for user in users:
        agent_name = user.first_name
        str_agent_id = str(user.id)
        agent_username_dict[str_agent_id] = agent_name

        if not procurement_cluster_map[procurement_cluster_map['agent_id'] == user.id].empty:
            agent_wise_dict[str_agent_id] = round(
                procurement_cluster_map[procurement_cluster_map['agent_id'] == user.id]['produce_net_weight'].sum() / 1000,3)
        else:
            agent_wise_dict[str_agent_id] = 0

    data_dict["agentwise_data"] = agent_wise_dict
    data_dict["agent_name_list"] = agent_username_dict

    # cluster wise
    # agent_ids = UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
    cluster_objs = Cluster.objects.filter(id__in=users_cluster_ids)
    cluster_based_agent_list = {}
    for cluster in cluster_objs:
        if not procurement_cluster_map[procurement_cluster_map['cluster_id'] == cluster.id].empty:
            cluster_based_agent_list[cluster.name] = \
                procurement_cluster_map[procurement_cluster_map['cluster_id'] == cluster.id][
                    'produce_net_weight'].sum() / 1000
        else:
            cluster_based_agent_list[cluster.name] = 0
    data_dict["cluster_wise_data"] = cluster_based_agent_list
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_default_procurement_price_for_agent(request):
    season_id =get_active_season_id()
    if AgentDistributionPrice.objects.filter(agent_id=request.data["agent_id"],season_id=season_id).exists():
        default_Price = AgentDistributionPrice.objects.get(
            agent_id=request.data["agent_id"],
            season_id=season_id
        ).price
    else:
        default_Price = 0
    data = {"default_price": default_Price}
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_sowing_data_for_prediction(request):
    print(request.data)

    season_id = request.data['season_id']
    # cluster
    if len(request.data["cluster_ids"]) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(
            Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list(
                "id", flat=True
            )
        )
    # super_visor
    if len(request.data["super_visor_ids"]) == 0:
        supervisor_ids = list(
            UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True)
        )
    else:
        supervisor_ids = list(
            UserProfile.objects.filter(
                user_type_id=5, user_id__in=request.data["super_visor_ids"]
            ).values_list("user_id", flat=True)
        )
    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(
            UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
        )
    else:
        agent_ids = list(
            UserProfile.objects.filter(
                user_type_id=6, user_id__in=request.data["agent_ids"]
            ).values_list("user_id", flat=True)
        )

    #  farmer cluster
    cluster_based_farmers_ids = list(
        FarmerClusterSeasonMap.objects.filter(
            season_id=season_id, cluster_id__in=cluster_ids
        ).values_list("farmer_id", flat=True)
    )

    # supervisor_based
    user_farmer_ids = list(
        UserFarmerMap.objects.filter(
            officer_id__in=supervisor_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=cluster_based_farmers_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # agent farmer map
    farmer_ids = list(
        AgentFarmerMap.objects.filter(
            agent_id__in=agent_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=user_farmer_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # sowing modules
    nursery_sowing_values = Sowing.objects.filter(
        farmer_id__in=farmer_ids, cultivation_phase_id=2
    ).values_list(
        "id",
        "area",
        "farmer_id",
        "crop__name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    )
    nursery_sowing_columns = [
        "sowing_id",
        "area",
        "farmer_id",
        "crop_name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    ]
    nursery_sowing_df = pd.DataFrame(
        list(nursery_sowing_values), columns=nursery_sowing_columns
    )

    # calculate the age of sowing from today date
    converted_today = datetime.datetime.strptime(
        request.data["selected_date"], "%Y-%m-%d"
    )
    print(datetime.date.today())
    today = converted_today.date()
    print(converted_today.date())
    nursery_sowing_df["crop_age_list"] = today - nursery_sowing_df["sowing_date"]
    nursery_sowing_df["crop_age_list"] = nursery_sowing_df["crop_age_list"].astype(
        "timedelta64[D]"
    )
    nursery_sowing_df["crop_age_list"] = nursery_sowing_df["crop_age_list"].astype(int)
    recieved_crop_age = request.data["crop_age"]
    print(nursery_sowing_df)
    print(recieved_crop_age)
    new_df = nursery_sowing_df[
        nursery_sowing_df["crop_age_list"] == int(recieved_crop_age)
        ]
    farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(season_id=season_id)
    agent_farmer_cluster_map = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
    master_list = []
    print(new_df)
    for index, row in new_df.iterrows():
        master_dict = {}
        farmer_cluster = farmer_cluster_map.get(farmer_id=row["farmer_id"])
        master_dict["farmer_name"] = farmer_cluster.farmer.first_name
        master_dict["cluster_name"] = farmer_cluster_map.get(
            farmer_id=row["farmer_id"]
        ).cluster.name
        master_dict["area"] = row["area"]
        master_dict["percentage"] = 0
        master_dict["agent_name"] = agent_farmer_cluster_map.get(
            farmer_id=farmer_cluster
        ).agent.first_name
        days = int(recieved_crop_age)
        sowing_area = row["area"]
        harvest_level_id = HarvestLevel.objects.get(
            harvest_interval_duration_in_days=days
        ).id
        yeild_expected_in_acre = YeildPrediction.objects.get(
            harvest_range=harvest_level_id
        ).expected_yeild_weight_in_kg
        total_yeild = YeildPrediction.objects.all().aggregate(
            Sum("expected_yeild_weight_in_kg")
        )["expected_yeild_weight_in_kg__sum"]
        calculated_as_per_sowing = yeild_expected_in_acre * Decimal(sowing_area)
        calculated_percentage = (calculated_as_per_sowing / total_yeild) * 100
        rounded_calculated_percentage = round(calculated_percentage, 1)
        master_dict["percentage"] = rounded_calculated_percentage
        master_dict["yeild_mt"] = calculated_as_per_sowing
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def upload_harvest(request):
    print(request.data)
    farmer_id = Farmer.objects.get(code=request.data["farmer code"]).id
    converted_date = datetime.datetime.strptime(request.data["date"], "%d/%m/%Y")
    if Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id).exists():
        sowing_id = Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id)[
            0
        ].id
        if not Harvest.objects.filter(
                sowing_id=sowing_id,
                date_of_harvest=converted_date,
                ticket_number=request.data["ticket number"],
                value=request.data["weight in kg"],
        ).exists():
            harvest_obj = Harvest(
                sowing_id=sowing_id,
                date_of_harvest=converted_date,
                value=request.data["weight in kg"],
                unit_id=1,
                ticket_number=request.data["ticket number"],
            )
            harvest_obj.save()
        data = True
    else:
        data = (
                "no sowing available for farmer ("
                + request.data["farmer code"]
                + ") check the farmer code"
        )
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def check_farmer_code_valid(request):
    if Farmer.objects.filter(code=request.data["farmer_code"]).exists():
        data = True
    else:
        data = False
    print(data)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def check_for_harvest_duplication(request):
    data = {}
    for item in request.data:
        if item["date"] != "Total":
            data[item["farmer code"]] = False
            print(item)
            if Farmer.objects.filter(code=item["farmer code"]).exists():
                farmer_id = Farmer.objects.get(code=item["farmer code"]).id
                converted_date = datetime.datetime.strptime(item["date"], "%d/%m/%Y")
                if Sowing.objects.filter(
                        cultivation_phase_id=2, farmer_id=farmer_id
                ).exists():
                    sowing_id = Sowing.objects.filter(
                        cultivation_phase_id=2, farmer_id=farmer_id
                    )[0].id
                    if Harvest.objects.filter(
                            sowing_id=sowing_id,
                            date_of_harvest=converted_date,
                            ticket_number=item["ticket number"],
                            value=item["weight in kg"],
                    ).exists():
                        data[item["farmer code"]] = True
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def store_manual_bulk_harvest(request):
    error_farmer_code_list = []
    print('request.data:::', request.data)
    input_data = request.data["data"]
    data = []
    error = ""
    season_id = get_active_season_id()
    for data in input_data:
        if data["farmer_code"] != None and data["quantity"] != None:
            if FarmerClusterSeasonMap.objects.filter(seasonal_farmer_code=data["farmer_code"]).exists():
                farmer_id = FarmerClusterSeasonMap.objects.get(seasonal_farmer_code=data["farmer_code"]).farmer.id
                # if it is not accepting all farmers then check for availbe inside the agent
                if not Procurement.objects.get(ticket_number=request.data["ticket_number"]).have_other_agent_farmer:
                    if AgentFarmerMap.objects.filter(farmer__farmer_id=farmer_id, agent_id=request.data["agent_id"], farmer__season_id=season_id).exists():
                        # print(AgentFarmerMap.objects.get(farmer__farmer_id=farmer_id,agent_id=request.data["agent_id"],).agent.first_name)
                        if Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id, season_id=season_id).exists():
                            sowing_id = (Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id, season_id=season_id).order_by("sowing_date")[0].id)
                            if not Harvest.objects.filter(sowing__farmer_id=farmer_id, ticket_number=request.data["ticket_number"], sowing__season_id=season_id).exists():
                                if not Harvest.objects.filter(
                                        sowing_id=sowing_id,
                                        date_of_harvest=request.data["date"],
                                        ticket_number=request.data["ticket_number"],
                                        value=data["quantity"],
                                    ).exists():
                                    try:
                                        harvest_obj = Harvest(
                                            sowing_id=sowing_id,
                                            date_of_harvest=request.data["date"],
                                            value=data["quantity"],
                                            unit_id=1,
                                            ticket_number=request.data["ticket_number"],
                                            created_by=request.user,
                                            modified_by=request.user,
                                        )
                                        harvest_obj.save()
                                        print("saved harvest")
                                    except Exception as err:
                                        print(err)
                                        pass
                            else:
                                error_farmer_code_list.append(data["farmer_code"])
                                error = (str(data["farmer_code"]) + "have already harvested for this ticket number. " + error)
                        else:
                            error_farmer_code_list.append(data["farmer_code"])
                            error = (str(data["farmer_code"]) + "have no sowing. " + error)

                    else:
                        error_farmer_code_list.append(data["farmer_code"])
                        error = (str(data["farmer_code"]) + "is not under selected agent. " + error)
                # if it is accepting all farmers means check it is out of the correct farmers
                else:
                    # if not AgentFarmerMap.objects.filter(farmer__farmer_id=farmer_id,farmer__season_id=season_id,
                    #                                      agent_id=request.data["agent_id"]).exists():
                    if Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id, season_id=season_id).exists():
                        sowing_id = (Sowing.objects.filter(cultivation_phase_id=2,season_id=season_id,
                                                            farmer_id=farmer_id).order_by("sowing_date")[0].id)
                        if not Harvest.objects.filter(sowing__farmer_id=farmer_id, ticket_number=request.data["ticket_number"], sowing__season_id=season_id).exists():
                            if not Harvest.objects.filter(
                                    sowing__season_id=season_id,
                                    sowing_id=sowing_id,date_of_harvest=request.data["date"],
                                                            ticket_number=request.data["ticket_number"],
                                                            value=data["quantity"],).exists():
                                try:
                                    harvest_obj = Harvest(
                                        sowing_id=sowing_id,
                                        date_of_harvest=request.data["date"],
                                        value=data["quantity"],
                                        unit_id=1,
                                        ticket_number=request.data["ticket_number"],
                                        created_by=request.user,
                                        modified_by=request.user,
                                    )
                                    harvest_obj.save()
                                    print("saved harvest")
                                except Exception as err:
                                    print(err)
                                    pass
                        else:
                            error_farmer_code_list.append(data["farmer_code"])
                            error = (str(data["farmer_code"]) + "have already harvested for this ticket number. " + error)
                    else:
                        error_farmer_code_list.append(data["farmer_code"])
                        error = (str(data["farmer_code"]) + "have no sowing. " + error)
                    # else:
                    #     error_farmer_code_list.append(data["farmer_code"])
                    #     error = (str(data["farmer_code"]) + "is under current agent" + error)
            else:
                error_farmer_code_list.append(data["farmer_code"])
                error = str(data["farmer_code"]) + " code is invalid. " + error
        else:
            error_farmer_code_list.append(data["farmer_code"])
            error = str(data["quantity"]) + "have no farmer code. " + error
    print(error_farmer_code_list)
    data = {"error_farmer_code_list": error_farmer_code_list, "message": error}
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_geo_tag(request):
    sowing = Sowing.objects.get(id=request.data["sowing_id"])
    data = False
    if sowing.latitude == None:
        return Response(data, status=status.HTTP_200_OK)
    else:
        data = {}
        data["lat"] = sowing.latitude
        data["lng"] = sowing.longitude
        return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_yeild_analysis(request):
    data = {}
    print(request.data)
    # cluster
    if len(request.data["cluster_ids"]) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list("id", flat=True))
    # super_visor
    if len(request.data["super_visor_ids"]) == 0:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True))
    else:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5, user_id__in=request.data["super_visor_ids"]).values_list("user_id", flat=True))
    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    else:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6, user_id__in=request.data["agent_ids"]).values_list("user_id", flat=True))

    converted_today = datetime.datetime.strptime(request.data["selected_date"], "%Y-%m-%d")
    today = converted_today.date()
    #  farmer cluster
    cluster_based_farmers_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=request.data["season_id"], cluster_id__in=cluster_ids).values_list("farmer_id", flat=True))

    # supervisor_based
    user_farmer_ids = list(UserFarmerMap.objects.filter(
            officer_id__in=supervisor_ids,
            farmer__season_id=request.data["season_id"],
            farmer__farmer__id__in=cluster_based_farmers_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # agent farmer map
    farmer_ids = list(
        AgentFarmerMap.objects.filter(
            agent_id__in=agent_ids,
            farmer__season_id=request.data["season_id"],
            farmer__farmer__id__in=user_farmer_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # harvest modules
    harvest_values = Harvest.objects.filter(
        sowing__farmer_id__in=farmer_ids,
        sowing__cultivation_phase_id=2,
        date_of_harvest=today,
    ).values_list("id", "sowing__id", "sowing__farmer_id", "sowing__sowing_date", "date_of_harvest", "value", "unit__name", "ticket_number",)
    harvest_columns = ["harvest_id", "sowing_id", "farmer_id", "sowing_date", "date_of_harvest", "value", "unit_name", "ticket_number",]
    harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)

    # date conversion
    # calculate the age of sowing from today date

    # ---expected yeild ----
    transplanted_sowing_values = Sowing.objects.filter(
        farmer_id__in=farmer_ids, cultivation_phase_id=2,is_active=True
    ).values_list(
        "id",
        "area",
        "farmer_id",
        "crop__name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    )
    transplanted_sowing_columns = [
        "sowing_id",
        "area",
        "farmer_id",
        "crop_name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    ]
    transplanted_sowing_df = pd.DataFrame(
        list(transplanted_sowing_values), columns=transplanted_sowing_columns
    )

    # calculate the age of sowing from today date
    transplanted_sowing_df["crop_age_list"] = (
            today - transplanted_sowing_df["sowing_date"]
    )
    transplanted_sowing_df["crop_age_list"] = transplanted_sowing_df[
        "crop_age_list"
    ].astype("timedelta64[D]")
    transplanted_sowing_df["crop_age_list"] = transplanted_sowing_df[
        "crop_age_list"
    ].astype(int)

    transplanted_predict_dict = {}
    for i in range(1, 201):
        if i not in transplanted_predict_dict:
            transplanted_predict_dict[i] = transplanted_sowing_df[
                transplanted_sowing_df["crop_age_list"] == i
                ]["area"].sum()

    total_harvest = 0
    transplanted_harvest_qty_dict = {}
    for harvest in HarvestLevel.objects.all():
        notice_period = harvest.notice_period
        calculated_acre = 0
        expected_range = YeildPrediction.objects.get(
            harvest_range_id=harvest.harvest_name
        ).expected_yeild_weight_in_kg
        # for j in range(1,int(notice_period)+1):
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) + j]
        #     calculated_acre +=  transplanted_predict_dict[int(harvest.harvest_interval_duration_in_days) - j]
        # print(int(harvest.harvest_interval_duration_in_days))
        calculated_acre += transplanted_predict_dict[
            int(harvest.harvest_interval_duration_in_days)
        ]
        print("calculated_acre", expected_range)
        transplanted_harvest_qty_dict[harvest.harvest_interval_duration_in_days] = (
                                                                                           Decimal(
                                                                                               calculated_acre) * expected_range
                                                                                   ) / 1000
        total_harvest += (Decimal(calculated_acre) * expected_range) / 1000
    # ---actual yeild------
    # harvest modules
    harvest_values = Harvest.objects.filter(
        sowing__farmer_id__in=farmer_ids,
        sowing__cultivation_phase_id=2,
        date_of_harvest=today,
    ).values_list(
        "id",
        "sowing__id",
        "sowing__farmer_id",
        "sowing__sowing_date",
        "date_of_harvest",
        "value",
        "unit__name",
        "ticket_number",
    )
    harvest_columns = [
        "harvest_id",
        "sowing_id",
        "farmer_id",
        "sowing_date",
        "date_of_harvest",
        "value",
        "unit_name",
        "ticket_number",
    ]
    harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)
    harvest_df["crop_age_list"] = today - harvest_df["sowing_date"]
    harvest_df["crop_age_list"] = harvest_df["crop_age_list"].astype("timedelta64[D]")
    harvest_df["crop_age_list"] = harvest_df["crop_age_list"].astype(int)
    harvest_df
    actual_dict = {}
    for i in range(1, 150):
        actual_dict[i] = harvest_df[harvest_df["crop_age_list"] == i]["value"].sum()
    actual_dict
    # calucation the yeild
    actual_harvest_dict = {}
    actual = 0
    for harvest_level in HarvestLevel.objects.all():
        actual_harvest_dict[harvest_level.harvest_interval_duration_in_days] = 0
        day = int(harvest_level.harvest_interval_duration_in_days)
        total = actual_dict[day]
        actual_harvest_dict[harvest_level.harvest_interval_duration_in_days] = (total / 1000)
        actual += total / 1000
    data["expected_weight"] = transplanted_harvest_qty_dict
    data["actual_weight"] = actual_harvest_dict
    data["total_expected_weight"] = total_harvest
    data["total_actual_weight"] = actual
    return Response(data, status=status.HTTP_200_OK)


def calculate_actual_yield(farmer_id, recieved_crop_age, today):
    # harvest modules
    harvest_values = Harvest.objects.filter(
        date_of_harvest=today,
        sowing__farmer_id=farmer_id,
        sowing__cultivation_phase_id=2,
        sowing__season_id=2,
    ).values_list(
        "id",
        "sowing__id",
        "sowing__farmer_id",
        "sowing__sowing_date",
        "date_of_harvest",
        "value",
        "unit__name",
        "ticket_number",
    )
    harvest_columns = [
        "harvest_id",
        "sowing_id",
        "farmer_id",
        "sowing_date",
        "date_of_harvest",
        "value",
        "unit_name",
        "ticket_number",
    ]
    harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)

    harvest_df["crop_age_list"] = today - harvest_df["sowing_date"]
    harvest_df["crop_age_list"] = harvest_df["crop_age_list"].astype("timedelta64[D]")
    harvest_df["crop_age_list"] = harvest_df["crop_age_list"].astype(int)

    actual_dict = {}
    total = 0
    for i in range(1, 150):
        actual_dict[i] = harvest_df[harvest_df["crop_age_list"] == i]["value"].sum()
    #     print(actual_dict)
    day = recieved_crop_age
    total = actual_dict[int(day)]
    total = total / 1000
    # for j in range(1,8):
    #     total += actual_dict[int(day)]
    #     day = int(recieved_crop_age) +  j
    # print('----------------')
    return total


@api_view(["POST"])
def serve_farmer_wise_analysis(request):
    # cluster
    season_id = request.data['season_id']
    if len(request.data["cluster_ids"]) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(
            Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list(
                "id", flat=True
            )
        )
    # super_visor
    if len(request.data["super_visor_ids"]) == 0:
        supervisor_ids = list(
            UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True)
        )
    else:
        supervisor_ids = list(
            UserProfile.objects.filter(
                user_type_id=5, user_id__in=request.data["super_visor_ids"]
            ).values_list("user_id", flat=True)
        )
    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(
            UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
        )
    else:
        agent_ids = list(
            UserProfile.objects.filter(
                user_type_id=6, user_id__in=request.data["agent_ids"]
            ).values_list("user_id", flat=True)
        )

    #  farmer cluster
    cluster_based_farmers_ids = list(
        FarmerClusterSeasonMap.objects.filter(
            season_id=season_id, cluster_id__in=cluster_ids
        ).values_list("farmer_id", flat=True)
    )

    # supervisor_based
    user_farmer_ids = list(
        UserFarmerMap.objects.filter(
            officer_id__in=supervisor_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=cluster_based_farmers_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # agent farmer map
    farmer_ids = list(
        AgentFarmerMap.objects.filter(
            agent_id__in=agent_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=user_farmer_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )
    converted_today = datetime.datetime.strptime(
        request.data["selected_date"], "%Y-%m-%d"
    )
    today = converted_today.date()
    recieved_crop_age = request.data["crop_age"]
    sowing_values = Sowing.objects.filter(
        farmer_id__in=farmer_ids, cultivation_phase_id=2
    ).values_list(
        "id",
        "area",
        "farmer_id",
        "crop__name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    )
    sowing_columns = [
        "sowing_id",
        "area",
        "farmer_id",
        "crop_name",
        "cultivation_phase_id",
        "cultivation_phase__name",
        "sowing_date",
    ]
    sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)
    sowing_df["crop_age_list"] = today - sowing_df["sowing_date"]
    sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype("timedelta64[D]")
    sowing_df["crop_age_list"] = sowing_df["crop_age_list"].astype(int)
    new_df = sowing_df[sowing_df["crop_age_list"] == int(recieved_crop_age)]

    farmer_cluster_map = FarmerClusterSeasonMap.objects.filter(season_id=season_id)
    agent_farmer_cluster_map = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
    master_list = []

    for index, row in new_df.iterrows():
        master_dict = {}
        farmer_cluster = farmer_cluster_map.get(farmer_id=row["farmer_id"])
        master_dict["farmer_name"] = farmer_cluster.farmer.first_name
        master_dict["farmer_id"] = row["farmer_id"]
        master_dict["cluster_name"] = farmer_cluster_map.get(
            farmer_id=row["farmer_id"]
        ).cluster.name
        master_dict["area"] = row["area"]
        master_dict["percentage"] = 0
        master_dict["agent_name"] = agent_farmer_cluster_map.get(
            farmer_id=farmer_cluster
        ).agent.first_name
        days = int(recieved_crop_age)
        sowing_area = row["area"]
        harvest_level_id = HarvestLevel.objects.get(
            harvest_interval_duration_in_days=days
        ).id
        yeild_expected_in_acre = YeildPrediction.objects.get(
            harvest_range=harvest_level_id
        ).expected_yeild_weight_in_kg
        total_yeild = YeildPrediction.objects.all().aggregate(
            Sum("expected_yeild_weight_in_kg")
        )["expected_yeild_weight_in_kg__sum"]
        calculated_as_per_sowing = yeild_expected_in_acre * Decimal(sowing_area)
        calculated_percentage = (calculated_as_per_sowing / total_yeild) * 100
        rounded_calculated_percentage = round(calculated_percentage, 1)
        master_dict["percentage"] = rounded_calculated_percentage
        master_dict["yeild_mt"] = calculated_as_per_sowing
        master_dict["actual_yeild"] = calculate_actual_yield(
            row["farmer_id"], days, today
        )
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def check_farmer_code_valid_and_sowing_and_status(request):
    result = 2
    print("came for check")
    if Farmer.objects.filter(code=request.data["farmer_code"]).exists():
        farmer_id = Farmer.objects.get(code=request.data["farmer_code"])
        if AgentFarmerMap.objects.filter(
                farmer__farmer_id=farmer_id, agent_id=request.data["agent_id"]
        ).exists():
            print(
                AgentFarmerMap.objects.get(
                    farmer__farmer_id=farmer_id, agent_id=request.data["agent_id"]
                ).agent.user_profile.first_name
            )
            if Sowing.objects.filter(
                    cultivation_phase_id=2, farmer_id=farmer_id, is_active=True
            ).exists():
                result = 1
    print(result)
    return Response(data=result, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_agent_cluster(request):
    print(request.data)
    season_id = get_active_season_id()
    cluster_name = UserClusterMap.objects.get(user_id=request.data["agent_id"], season_id=season_id).cluster.name
    data = {"cluster_name": cluster_name}
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_overall_gps_report(request):
    user_id = request.user.id
    season_id = request.data['season_id']
    if UserProfile.objects.get(user_id=user_id).user_type_id == 5:
        print('afs logins')
        cluster_ids = list(UserClusterMap.objects.filter(user_id=user_id,season_id=season_id).values_list('cluster_id', flat=True))
        farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list('farmer_id', flat=True))
        sowing_obj = Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id)
        cluster_objs = Cluster.objects.filter(id__in=cluster_ids)
        farmer_cluster_season_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids)
    else:
        sowing_obj = Sowing.objects.filter( season_id=season_id)
        active_cluster_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True)
        cluster_objs = Cluster.objects.filter(id__in=active_cluster_ids)
        farmer_cluster_season_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id)

    sowing_values = list(sowing_obj.filter(cultivation_phase_id=2).values_list("id","farmer_id","cultivation_phase__name","sowing_date","area","season_id","area_calculated_via_geo_fencing","latitude","longitude",))
    sowing_columns = [ "id", "farmer_id", "cultivation_phase__name", "sowing_date", "area", "season_id", "area_calculated_via_geo_fencing", "latitude", "longitude"]
    sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)
    sowing_df
    # farmer cluster
    farmer_cluster_values = list(farmer_cluster_season_obj.filter(season_id=season_id).values_list("id", "farmer_id", "cluster_id", "cluster__name"))
    farmer_cluster_column = ["id", "farmer_id", "cluster_id", "cluster_name"]
    farmer_cluster_df = pd.DataFrame(farmer_cluster_values, columns=farmer_cluster_column)
    farmer_cluster_df

    merged_df = pd.merge(sowing_df, farmer_cluster_df, left_on="farmer_id", right_on="farmer_id", how="left",)
    merged_df = merged_df.fillna(0)
    merged_df

    master_list = []
    total_dict = {}

    total_dict["Cluster"] = "Total"
    total_dict["Farmer count"] = 0
    total_dict["Farmer TP area"] = 0
    total_dict["Gps area"] = 0
    total_dict["TP Acres"] = 0
    total_dict["Farmer count gps"] = 0
    total_dict["Ratio GPS to TP"] = 0

    for cluster in cluster_objs:
        filtered_rows = merged_df[merged_df["cluster_id"] == cluster.id]
        temp_dict = {}
        temp_dict["Cluster"] = cluster.name
        temp_dict["Farmer count"] = len(filtered_rows["farmer_id"].unique())
        temp_dict["Farmer TP area"] = round(filtered_rows["area"].sum(), 2)
        temp_dict["Gps area"] = round(merged_df[merged_df["cluster_id"] == cluster.id]["area_calculated_via_geo_fencing"].sum(),2,)
        empty_rows = filtered_rows[filtered_rows["area_calculated_via_geo_fencing"] != 0]
        temp_dict["TP Acres"] = round(empty_rows[empty_rows["cluster_id"] == cluster.id]["area"].sum(), 2)
        temp_dict["Farmer count gps"] = len(empty_rows["farmer_id"].unique())
    #     print(temp_dict)
        if temp_dict["TP Acres"] != 0:
            temp_dict["Ratio GPS to TP"] = round(temp_dict["Gps area"] / temp_dict["TP Acres"], 2)
        else:
            temp_dict["Ratio GPS to TP"] = 0
        total_dict["Farmer count"] = round(total_dict["Farmer count"] + temp_dict["Farmer count"], 2)
        total_dict["Gps area"] = round(total_dict["Gps area"] + temp_dict["Gps area"], 2)
        total_dict["Farmer TP area"] = round(total_dict["Farmer TP area"] + temp_dict["Farmer TP area"], 2)
        total_dict["TP Acres"] = round(total_dict["TP Acres"] + temp_dict["TP Acres"], 2)
        total_dict["Farmer count gps"] = round(total_dict["Farmer count gps"] + temp_dict["Farmer count gps"], 2)
        if total_dict['TP Acres'] != 0:
            total_dict["Ratio GPS to TP"] = round(total_dict["Ratio GPS to TP"]+ total_dict["Gps area"] / total_dict["TP Acres"],2,)
        else:
            total_dict["Ratio GPS to TP"] = 0
        master_list.append(temp_dict)

    master_list.append(total_dict)
    df = pd.DataFrame(master_list)
    df_mean = df.head(len(master_list)-1)
    line_no = len(master_list)
    # print(line_no)
    # dict(df_mean.mean(axis=0))
    master_list.append(dict(round(df_mean.mean(axis=0))))
    df = pd.DataFrame(master_list)
    df = df.fillna(0)
    df.loc[line_no,'Cluster'] = 'Average' 
    df

    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "overall_gps.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:G1", "OVERALL GPS REPORT " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "overall_gps.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = df.to_dict("r")
    return Response(document, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_date_wise_gps_report(request):
    # selected_date = request.data["date"]
    season_id = request.data['season_id']
    # date = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
    #timestamp__date=date, 
    sowing_boundary = list(SowingBoundary.objects.filter(sowing__season_id=season_id, sowing__cultivation_phase_id=2).values_list("id","sowing_id","sowing__area_calculated_via_geo_fencing","sowing__farmer__id","sowing__area",))
    sowing_values = ["id", "sowing_id", "geo_fence_area", "farmer_id", "area"]
    sowing_df = pd.DataFrame(sowing_boundary, columns=sowing_values)
    sowing_df = sowing_df.drop_duplicates(subset="sowing_id", keep="first", inplace=False)
    # farmer cluster
    farmer_cluster_values = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id).values_list("id", "farmer_id", "cluster_id", "cluster__name"))
    farmer_cluster_column = ["id", "farmer_id", "cluster_id", "cluster_name"]
    farmer_cluster_df = pd.DataFrame(farmer_cluster_values, columns=farmer_cluster_column)

    merged_df = pd.merge(
        sowing_df,
        farmer_cluster_df,
        left_on="farmer_id",
        right_on="farmer_id",
        how="left",
    )
    merged_df = merged_df.fillna(0)
    master_list = []
    total_dict = {}
    total_dict["Cluster"] = "Total"
    total_dict["Farmer count"] = 0
    total_dict["Farmer TP area"] = 0
    total_dict["Gps area"] = 0
    total_dict["TP Acres"] = 0
    total_dict["Farmer count gps"] = 0
    total_dict["Ratio GPS to TP"] = 0

    for cluster in Cluster.objects.filter():
        filtered_rows = merged_df[merged_df["cluster_id"] == cluster.id]
        temp_dict = {}
        # cluster name
        temp_dict["Cluster"] = cluster.name
        # farmer count for gps marked on that date
        temp_dict["Farmer count"] = len(filtered_rows["farmer_id"].unique())
        # area of tp on selected date
        temp_dict["Farmer TP area"] = round(filtered_rows["area"].sum(), 2)
        # fenced area of selected date
        temp_dict["Gps area"] = round(merged_df[merged_df["cluster_id"] == cluster.id]["geo_fence_area"].sum(), 2
        )

        empty_rows = filtered_rows[filtered_rows["geo_fence_area"] != 0]
        temp_dict["TP Acres"] = round(
            empty_rows[empty_rows["cluster_id"] == cluster.id]["area"].sum(), 2
        )
        temp_dict["Farmer count gps"] = len(empty_rows["farmer_id"].unique())
        if temp_dict["Gps area"] == 0:
            temp_dict["Ratio GPS to TP"] = 0
        else:
            temp_dict["Ratio GPS to TP"] = round(
                temp_dict["Gps area"] / temp_dict["TP Acres"], 2
            )
        total_dict["Farmer count"] = round(
            total_dict["Farmer count"] + temp_dict["Farmer count"], 2
        )
        total_dict["Farmer TP area"] = round(
            total_dict["Farmer TP area"] + temp_dict["Farmer TP area"], 2
        )
        total_dict["Gps area"] = round(
            total_dict["Gps area"] + temp_dict["Gps area"], 2
        )
        total_dict["TP Acres"] = round(
            total_dict["TP Acres"] + temp_dict["TP Acres"], 2
        )
        total_dict["Farmer count gps"] = round(
            total_dict["Farmer count gps"] + temp_dict["Farmer count gps"], 2
        )
        total_dict["Ratio GPS to TP"] = round(
            total_dict["Ratio GPS to TP"] + temp_dict["Ratio GPS to TP"], 2
        )
        master_list.append(temp_dict)
    master_list.append(total_dict)
    df = pd.DataFrame(master_list)
    df_mean = df.head(len(master_list)-1)
    line_no = len(master_list)
    print(line_no)
    # dict(df_mean.mean(axis=0))
    master_list.append(dict(round(df_mean.mean(axis=0))))
    df = pd.DataFrame(master_list)
    df = df.fillna(0)
    df.loc[line_no,'Cluster'] = 'Average' 
    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "day_wise.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:H1", "DAYWISE " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "day_wise.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = df.to_dict("r")
    return Response(document, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_farmer_wise_gps(request):
    print(request.data)
    season_id = request.data['season_id']
    date = request.data['date']
    if date is not None:
        sowing_objs = list(Sowing.objects.filter(season_id=season_id, sowing_date=date, cultivation_phase_id=2).values_list( "id", "sowing_date", "area", "area_calculated_via_geo_fencing", "farmer_id", "farmer__first_name",))
    else:
        sowing_objs = list(Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2).values_list( "id", "sowing_date", "area", "area_calculated_via_geo_fencing", "farmer_id", "farmer__first_name",))
    # print(sowing_objs)
    sowing_columns = ["id", "sowing_date", "area", "area_calculated_via_geo_fencing", "farmer_id", "farmer_first_name",]
    sowing_df = pd.DataFrame(sowing_objs, columns=sowing_columns)
    farmer_ids = list(set(list(Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2).values_list("farmer_id", flat=True))))
    farmer_cluster_values = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id__in=farmer_ids).values_list("id", "cluster__name", "cluster_id", "farmer_id", "seasonal_farmer_code"))
    farmer_cluster_columns = ["id", "cluster__name", "cluster_id", "farmer_id", "farmer_code"]
    farmer_cluster_df = pd.DataFrame(farmer_cluster_values, columns=farmer_cluster_columns)

    farmer_agent_values = list(AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id", "farmer_id__farmer_id", "agent__first_name"))
    farmer_agent_columns = ["id", "farmer_id", "agent_name"]
    farmer_agent_df = pd.DataFrame(farmer_agent_values, columns=farmer_agent_columns)

    merged_df = pd.merge(sowing_df, farmer_cluster_df, left_on="farmer_id", right_on="farmer_id", how="left",)
    agent_merged_df = pd.merge(merged_df, farmer_agent_df, left_on="farmer_id", right_on="farmer_id", how="left",)
    df = agent_merged_df.fillna(0)
    df = df.drop(["id_x", "id", "farmer_id", "id_y", "cluster_id"], axis=1)

    gps_made_farmers = df[df["area_calculated_via_geo_fencing"] != 0]
    without_gps_made_farmers = df[df["area_calculated_via_geo_fencing"] == 0]

    # excel convert
    writer = pd.ExcelWriter(str("static/media/") + "farmer_gps_report.xlsx", engine="xlsxwriter")
    gps_made_farmers.to_excel(writer, sheet_name="GPS", startrow=1)
    without_gps_made_farmers.to_excel(writer, sheet_name="WITHOUT GPS", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book

    worksheet = writer.sheets["GPS"]
    worksheet1 = writer.sheets["WITHOUT GPS"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    worksheet.merge_range("A1:H1", "Farmer with gps marked", merge_format)
    worksheet1.merge_range("A1:H1", "Farmer without gps marked", merge_format)
    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 8, 20)

    # Set the column width and format.
    worksheet1.set_column("B:B", 18, format1)
    worksheet1.set_column(0, 8, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
        worksheet1.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "farmer_gps_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = df.to_dict("r")
    return Response(document, status=status.HTTP_200_OK)


def convert_decimal(value):
    return round(value)

def round_decimal(value):
    val = value
    x = 0

    if (float(val) % 1) >= 0.5:
        value = math.ceil(val)
    else:
        value = round(val)
    return value


@api_view(["POST"])
def serve_datewise_procurement_report(request):
    print("procuremnt report")
    print(request.data)
    start_date = request.data["start_date"]
    end_date = request.data["end_date"]
    season_id = get_active_season_id()
    document = {}

    if Procurement.objects.filter(procurement_group__procurement_date__range=[start_date, end_date]).exists():

        procurement_objs = (Procurement.objects.filter(procurement_group__procurement_date__range=[start_date, end_date])
                .order_by("procurement_group__procurement_date")
                .values_list( "procurement_group__procurement_date", "ticket_number", "procurement_transaport_incharge_kyc__aadhar_number", 
                "procurement_group__agent__id", "procurement_group__agent__first_name", "vehicle_number", "loaded_vehicle_weight", 
                "empty_vehicle_weight", "produce_gross_weight", "gunnybag_count", "gunnybag_weight", "moisture", "other_deduction", 
                "str_weight", "procurement_group__produce_net_weight", "procurement_group__price_per_unit", 
                "procurement_group__agent_price_deduction", "procurement_group__payment_to_wallet", "procurement_group__payment_to_agent"))

        procurement_columns = [ "Date", "Ticket No", "ID/Company", "agent_id", "Agent Name", "Vehicle No", "Gross Wt/kg", "Tare Wt/kg", 
        "Net Wt/kg", "Bag No", "Bag Deduct", "moisture Deduct", "other_deduction", "str_weight", "Final Weight", "Total prices/Per kg", 
        "Deduction Price/kg", "Deduction/kg","payment_to_agent"]
        procurement_df = pd.DataFrame(procurement_objs, columns=procurement_columns)

        agent_cluster = UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=6).values_list('user_id', 'cluster__name')
        agent_cluster_col = ['agent_id', 'cluster_name']
        agent_cluster_df = pd.DataFrame(agent_cluster, columns=agent_cluster_col)
        agent_cluster_df

        procurement_cluster_df = pd.merge(procurement_df, agent_cluster_df, left_on='agent_id', right_on='agent_id', how='left')
        procurement_cluster_df

        procurement_df = procurement_cluster_df

        procurement_df["Bag weight Deduction/ Per kg"] = procurement_df.apply(lambda x: "0.2", axis=1)
        procurement_df["Quality Weight"] = procurement_df.apply(lambda x: "0", axis=1)
        procurement_df["avg bag weight"] = procurement_df.apply(lambda x: round(x["Net Wt/kg"] / x["Bag No"], 2), axis=1)

        procurement_df["Payment Price/kg"] = procurement_df.apply(lambda x: (x["Total prices/Per kg"] - x["Deduction Price/kg"]), axis=1)
        
        procurement_df['loss'] = ((procurement_df['str_weight'] - procurement_df['Final Weight']) / procurement_df['str_weight']) * 100
        procurement_df['loss'] = procurement_df['loss'].astype(float).round(2)
        
        bank_details = UserBankDetails.objects.filter(is_primary=True).values_list("user_id","bank","branch","ifsc_code","account_holder_name","account_number",)
        bank_columns = [ "user_id", "Bank name", "Branch", "IFSC Code", "BankAccount", "BankNumber",]
        bank_df = pd.DataFrame(bank_details, columns=bank_columns)

        df = pd.merge(procurement_df, bank_df, left_on="agent_id", right_on="user_id", how="left")
        df = df.drop(["agent_id", "user_id"], axis=1)

        df = df.fillna("-")
        # df.value1 = df.value1.round()
        # df['Gross Wt/kg'] = df['column'].apply(lambda x: round(x, decimals))
        # df[['Gross Wt/kg','Tare Wt/kg','Net Wt/kg','Bag Deduct','str_weight','Final Weight','Total Amount/kg','Deduction/kg','Payment Amount/per kg']].apply(pd.Series.round)
        df["Gross Wt/kg"] = df.apply(lambda x: convert_decimal(x["Gross Wt/kg"]), axis=1)
        df["Tare Wt/kg"] = df.apply(lambda x: convert_decimal(x["Tare Wt/kg"]), axis=1)
        df["Net Wt/kg"] = df.apply(lambda x: convert_decimal(x["Net Wt/kg"]), axis=1)
        df['Bag Deduct']=df.apply(lambda x: convert_decimal(x['Bag Deduct']), axis=1)
        df["str_weight"] = df.apply(lambda x: convert_decimal(x["str_weight"]), axis=1)
        df["Final Weight"] = df.apply(lambda x: convert_decimal(x["Final Weight"]), axis=1)
        # s
        df["Total Amount/kg"] = df.apply(lambda x: (x["Final Weight"] * x["Total prices/Per kg"]), axis=1)
        df[["Total Amount/kg", "Deduction/kg"]]=df[["Total Amount/kg", "Deduction/kg"]].astype(float)
        df["Payment Amount/per kg"] = df.apply(lambda x: get_total_value(x["Total Amount/kg"],x["Deduction/kg"]), axis=1)
        df["Payment Amount/per kg"] = df['Payment Amount/per kg'].astype(float)
        # w
        # df["Payment Amount/per kg"] = df.apply(lambda x: round_decimal(x["Payment Amount/per kg"]), axis=1)

        # df['unrounded_total_amount']= df.apply(lambda x: (x["Final Weight"] * x["Total prices/Per kg"]), axis=1)
        # df["Total Amount/kg"] = df.apply(lambda x: convert_decimal(x["Total Amount/kg"]), axis=1)
        # df['Payment Price/kg']= df.apply(lambda x: str(round((x['Payment Price/kg'], 2))), axis=1)
        # df["unrounded_deduction/kg"] = df.apply(lambda x: x["Deduction/kg"], axis=1)
        # u
        # df["Deduction/kg"] = df.apply(lambda x: convert_decimal(x["Deduction/kg"]), axis=1)
        df["Deduction/kg"]=df["Deduction/kg"].astype(float)
        # df["Payment Amount/per kg"]=df["Payment Amount/per kg"].astype(float)
        df["Payment Amount/per kg"] = df.apply(lambda x: round_decimal(x["Total Amount/kg"]-x["Deduction/kg"]), axis=1)


        df = df[["Date","Ticket No","ID/Company","Agent Name","cluster_name","Vehicle No", "Gross Wt/kg", "Tare Wt/kg", "Net Wt/kg", "Bag No", "Bag weight Deduction/ Per kg", "Bag Deduct", "Quality Weight", "moisture Deduct", "other_deduction", "str_weight", "Final Weight", "Total prices/Per kg", "Total Amount/kg", "Deduction Price/kg", "Deduction/kg", "Payment Price/kg", "Payment Amount/per kg", "BankAccount", "Bank name", "Branch", "BankNumber", "IFSC Code", "avg bag weight","loss"]]
        
        df['avg bag weight'] = df['avg bag weight'].astype(float)
        df['Payment Price/kg'] = df['Payment Price/kg'].astype(float)
        df['Deduction Price/kg'] = df['Deduction Price/kg'].astype(float)
        df['Total prices/Per kg'] = df['Total prices/Per kg'].astype(float)
        df['other_deduction'] = df['other_deduction'].astype(float)
        df['Bag weight Deduction/ Per kg'] = df['Bag weight Deduction/ Per kg'].astype(float)
        df['Quality Weight'] = df['Quality Weight'].astype(float)
        df['moisture Deduct'] = df['moisture Deduct'].astype(float)

        df = df.rename(columns={"cluster_name" : 'Cluster Name' , "moisture Deduct" : 'Moisture Deduct' , "other_deduction" : 'Other Deduction' , "str_weight" : 'Str Weight' , "avg bag weight" : 'Avg Bag Weight' , "loss" : 'Loss' ,})
        
        document["data"] = df.to_dict("r")

        df.index += 1
        total = df.sum(numeric_only=True)
        total.name = 'Total'
        df = df.append(total.transpose())
        # initializing excel
        # procurement_df.apply(lambda x: convert_decimal(x['ticket_number']), axis=1)
        writer = pd.ExcelWriter("static/media" + "/procurement_report.xlsx", engine="xlsxwriter")
        # creating excel sheet with name

        df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range(
            "A1:AE1",
            "Total Flower Puchase 2020 ( " + start_date + " - " + end_date + " )",
            merge_format,
        )

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:AE", 18, format1)
        worksheet.set_column(0, 7, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        
        try:
            image_path = str("static/media/") + "procurement_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                document["excel"] = encoded_image
        except Exception as err:
            print(err)
        
    else:
        document["excel"] = "no-data"
    return Response(document, status=status.HTTP_200_OK)

def get_total_value(total_amount, deducted):
    value = total_amount - deducted
    return value 


@api_view(["POST"])
def check_for_access(request):
    user_type_id = request.data["user_type_id"]
    module_id = request.data["module_id"]
    hardware_device_id = request.data["hardware_device_id"]
    operation_id = request.data["operation_id"]
    data = {}
    if UsertypeBasedAccessControl.objects.filter(
            user_type_id=user_type_id,
            module_id=module_id,
            hardware_device_id=hardware_device_id,
            operation_id=operation_id,
    ).exists():
        data["access"] = UsertypeBasedAccessControl.objects.get(
            user_type_id=user_type_id,
            module_id=module_id,
            hardware_device_id=hardware_device_id,
            operation_id=operation_id,
        ).access
    else:
        data["access"] = False
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_access_controls(request):
    user_type_id = request.data["user_type_id"]
    hardware_device_id = request.data["hardware_device_id"]
    control_values = UsertypeBasedAccessControl.objects.filter(
        user_type_id=user_type_id, hardware_device_id=hardware_device_id
    ).values_list(
        "id",
        "user_type_id",
        "module__name",
        "module_id",
        "hardware_device__id",
        "hardware_device__name",
        "operation_id",
        "operation__name",
        "access",
    )
    control_columns = [
        "id",
        "user_type_id",
        "module_name",
        "module_id",
        "hardware_device_id",
        "hardware_device_name",
        "operation_id",
        "operation_name",
        "access",
    ]
    control_df = pd.DataFrame(list(control_values), columns=control_columns)
    # data = control_df.groupby('module_name').apply(lambda x: x.to_dict('r')).to_dict()
    master_dict = {}
    for index, row in control_df.iterrows():
        if row["module_name"] not in master_dict:
            master_dict[row["module_name"]] = {}
        master_dict[row["module_name"]][row["operation_name"]] = {}
        master_dict[row["module_name"]][row["operation_name"]]["id"] = row["id"]
        master_dict[row["module_name"]][row["operation_name"]]["access"] = row["access"]
    data = master_dict
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_hardware_devices(request):
    divice_list = []
    for device in HardwareDevice.objects.all():
        divice_dict = {}
        divice_dict["id"] = device.id
        divice_dict["name"] = device.name
        divice_list.append(divice_dict)
    return Response(divice_list, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_access_option(request):
    action_list = []
    for action in OperationCv.objects.all():
        action_dict = {}
        action_dict["id"] = action.id
        action_dict["name"] = action.name
        action_list.append(action_dict)
    return Response(action_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_access(request):
    print("access changed")
    print(request.data)
    user_type_access = UsertypeBasedAccessControl.objects.get(id=request.data["access_id"]["id"])
    user_type_access.access = not user_type_access.access
    user_type_access.save()
    print("access changed sucess")
    return Response(status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def get_non_supplied_farmer_list(request):
    document = {}
    season_id = request.data['season_id']
    data_dict_from_interface = request.data
    print('data_dict_from_interface', data_dict_from_interface)
    print('idzzz:',request.data)
    user_type_id = UserProfile.objects.get(user=request.user).user_type.id
    print(user_type_id)
    user_id = request.user.id
    print(user_id)
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))
    # subordinate_user_ids = list(UserProfile.objects.filter(user_id__in=subordinate_user_ids, user_type_id=user_type_id).values_list("user_id", flat=True))

    if AgentFarmerMap.objects.filter(agent_id__in=subordinate_user_ids, farmer__season_id=season_id).exists():
        print('exetessoko')
        filter_farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=subordinate_user_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        farmer_ids = Harvest.objects.filter(sowing__season_id=season_id).values_list("sowing__farmer__id", flat=True)
        filtered_farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id__in=filter_farmer_ids).exclude(farmer_id__in=farmer_ids).values_list("farmer__id", flat=True))
        
        # filter only the cluster value deducted

        if "selected_cluster_ids" in data_dict_from_interface:
            print('yesssss')
            cluster_farmer_obj = FarmerClusterSeasonMap.objects.filter(cluster_id__in=data_dict_from_interface['selected_cluster_ids'], season_id=season_id)
        else:
            cluster_farmer_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id)

        cluster_farmer_values = list(cluster_farmer_obj.filter(farmer_id__in=filter_farmer_ids, season_id=season_id).exclude(farmer_id__in=farmer_ids).values_list("id","cluster__name", "cluster__id", "farmer_id", "farmer__first_name", "farmer__last_name", "farmer__village__name", "seasonal_farmer_code",))
        cluster_farmer_columns = ["id","cluster_name","cluster_id","farmer_id","farmer_first_name","farmer_last_name","farmer_village_name","farmer_code",]
        cluster_farmer_df = pd.DataFrame(cluster_farmer_values, columns=cluster_farmer_columns)
        # filtering sowing objs based on option selected
        sowing_obj = Sowing.objects.filter(season_id=season_id)

    #     # if 'date_greater' in data_dict_from_interface:
    #     #     sowing_obj = sowing_obj.filter(sowing_date__gte=data_dict_from_interface['date_greater'])
    #     # if 'date_lesser' in data_dict_from_interface:
    #     #     sowing_obj = sowing_obj.filter(sowing_date__lte=data_dict_from_interface['date_lesser'])

        sowing_values = list(sowing_obj.filter(farmer_id__in=filtered_farmer_ids, season_id=season_id, cultivation_phase_id=2).values_list("id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase__name",))
        sowing_columns = ["sowing_id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase_name"]
        sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)

        # converted_today = datetime.datetime.strptime(, '%Y-%m-%d')
        today = datetime.datetime.now().date()
        sowing_df["crop_age"] = today - sowing_df["sowing_date"]
        sowing_df["crop_age"] = sowing_df["crop_age"].astype("timedelta64[D]")
        sowing_df["crop_age"] = sowing_df["crop_age"].astype(int)
        farmer_sowing_merged_df = pd.merge(cluster_farmer_df,sowing_df,left_on="farmer_id",right_on="farmer_id",how="left")

        if "age_greater_than" in data_dict_from_interface:
            farmer_sowing_merged_df = farmer_sowing_merged_df[farmer_sowing_merged_df["crop_age"] >= int(data_dict_from_interface["age_greater_than"])]

        if "age_lesser_than" in data_dict_from_interface:
            farmer_sowing_merged_df = farmer_sowing_merged_df[farmer_sowing_merged_df["crop_age"]<= int(data_dict_from_interface["age_lesser_than"])]

        farmer_cluster_map_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id).exclude(farmer_id__in=farmer_ids).values_list("id", flat=True))
        agent_farmer_map_values = list(AgentFarmerMap.objects.filter(farmer_id__in=farmer_cluster_map_ids).values_list("id", "farmer__farmer_id", "agent__first_name", "agent__last_name"))
        agent_farmer_map_columns = [ "agent_map_id", "farmer_id", "agent_first_name", "agent_last_name",]
        agent_farmer_map_df = pd.DataFrame(agent_farmer_map_values, columns=agent_farmer_map_columns)

        df = pd.merge(farmer_sowing_merged_df,agent_farmer_map_df,left_on="farmer_id",right_on="farmer_id",how="left",)
        df = df.drop(["id","cluster_id","farmer_id","sowing_id","cultivation_phase_id","agent_map_id",], axis=1,)
        df = df.rename(columns = {'cluster_name' : 'Cluster Name', 'farmer_first_name' : 'Farmer First Name', 'farmer_last_name' : 'Farmer Last Name',
       'farmer_village_name' : 'Farmer Village Name', 'farmer_code' : 'Farmer Code', 'sowing_date' : 'Sowing Date', 'area' : 'Area',
       'cultivation_phase_name' : 'Cultivation Phase Name', 'crop_age' : 'Crop Age', 'agent_first_name' : 'Agent First Name',
       'agent_last_name' : 'Agent Last Name'})
        df = df.fillna(0)
        print("===========================", df)
        writer = pd.ExcelWriter(str("static/media/") + "Non_supplied_farmers.xlsx", engine="xlsxwriter")

        # assigning that sheet to obj
        workbook = writer.book

        merge_format = workbook.add_format({
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        header_format = workbook.add_format({"fg_color": "#D7E4BC"})
        format1 = workbook.add_format({"num_format": "#,##0.00"})
        if user_type_id == 5:
            subordinate_user_ids = [user_id]
            clusters = UserClusterMap.objects.filter(user_id=user_id).values_list("cluster__name", flat=True)
            df = df[df["Cluster Name"].isin(clusters)]
        for cluster in df["Cluster Name"].unique():
            cluster_based_df = df[df["Cluster Name"] == cluster]
            cluster_based_age_based_df = cluster_based_df[cluster_based_df["Crop Age"] > 35]
            cluster_based_age_based_df.to_excel(writer, sheet_name=str(cluster), startrow=1)
            cluster = writer.sheets[str(cluster)]
            cluster.merge_range("A1:L1", "farmers", merge_format)
            format1 = workbook.add_format({"num_format": "#,##0.00"})
            cluster.set_column("B:B", 18, format1)
            cluster.set_column(0, 11, 20)

            # Write the column headers with the defined format.
            for col_num, value in enumerate(df.columns.values):
                cluster.write(0, col_num + 1, value, header_format)
        writer.save()
        print('ok...')
        try:
            image_path = str("static/media/") + "Non_supplied_farmers.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                document["excel"] = encoded_image
        except Exception as err:
            print(err)
        document["data"] = df.to_dict("r")
    return Response(document, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_date_wise_gps_report_based_on_cluster_for_mobile(request):
    selected_date = request.data["date"]
    selected_user = request.user
    user_type_id = UserProfile.objects.get(user=request.user).user_type_id
    user_id = request.user.id
    season_id=request.data['season_id']
    if user_type_id == 5:
        user_clusters_ids = list(UserClusterMap.objects.filter(user=request.user, season_id=season_id).values_list("cluster_id", flat=True))
        sorted_available_cluster = Cluster.objects.filter(id__in=user_clusters_ids)
        sub_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    elif user_type_id == 3:
        if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
            subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
            subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
            user_clusters_ids = list(UserClusterMap.objects.filter(user_id__in=subordinate_user_ids, season_id=season_id).values_list("cluster_id", flat=True))
            sorted_available_cluster = Cluster.objects.filter(id__in=user_clusters_ids)
            sub_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id', flat=True))
    elif user_type_id == 6:
        sub_ids = [user_id]
        activated_clusters = UserClusterMap.objects.filter(season_id=season_id, user_id=user_id).values_list('cluster_id', flat=True)
        user_clusters_ids = list(Cluster.objects.filter(id__in=activated_clusters).values_list("id", flat=True))
        sorted_available_cluster = Cluster.objects.filter(id__in=activated_clusters)
    else:
        sub_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
        activated_clusters = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True)
        user_clusters_ids = list(Cluster.objects.filter(id__in=activated_clusters).values_list("id", flat=True))
        sorted_available_cluster = Cluster.objects.filter(id__in=activated_clusters)

    farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=sub_ids, farmer__cluster_id__in=user_clusters_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
    date = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
    sowing_boundary = list(SowingBoundary.objects.filter(timestamp__date=date,sowing__cultivation_phase_id=2,sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).values_list("id","sowing_id","sowing__area_calculated_via_geo_fencing","sowing__farmer__id","sowing__area",))
    sowing_values = ["id", "sowing_id", "geo_fence_area", "farmer_id", "area"]
    sowing_df = pd.DataFrame(sowing_boundary, columns=sowing_values)
    sowing_df = sowing_df.drop_duplicates(subset="sowing_id", keep="first", inplace=False)
        # farmer cluster
    farmer_cluster_values = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster__in=user_clusters_ids).values_list("id", "farmer_id", "cluster_id", "cluster__name"))    
    farmer_cluster_column = ["id", "farmer_id", "cluster_id", "cluster_name"]
    farmer_cluster_df = pd.DataFrame(farmer_cluster_values, columns=farmer_cluster_column)
    merged_df = pd.merge(sowing_df,farmer_cluster_df,left_on="farmer_id",right_on="farmer_id",how="left",)
    merged_df = merged_df.fillna(0)
    master_list = []
    total_dict = {}
    total_dict["Cluster"] = "Total"
    total_dict["Farmer count"] = 0
    total_dict["Farmer TP area"] = 0
    total_dict["Gps area"] = 0
    total_dict["TP Acres"] = 0
    total_dict["Farmer count gps"] = 0
    total_dict["Ratio GPS to TP"] = 0

    for cluster in sorted_available_cluster:
        filtered_rows = merged_df[merged_df["cluster_id"] == cluster.id]
        temp_dict = {}
        temp_dict["Cluster"] = cluster.name
        temp_dict["Farmer count"] = len(filtered_rows["farmer_id"].unique())
        temp_dict["Farmer TP area"] = round(filtered_rows["area"].sum(), 2)
        temp_dict["Gps area"] = round(merged_df[merged_df["cluster_id"] == cluster.id]["geo_fence_area"].sum(), 2)
        empty_rows = filtered_rows[filtered_rows["geo_fence_area"] != 0]
        temp_dict["TP Acres"] = round(empty_rows[empty_rows["cluster_id"] == cluster.id]["area"].sum(), 2)
        temp_dict["Farmer count gps"] = len(empty_rows["farmer_id"].unique())
        if temp_dict["Gps area"] == 0:
            temp_dict["Ratio GPS to TP"] = 0
        else:
            temp_dict["Ratio GPS to TP"] = round(temp_dict["Gps area"] / temp_dict["TP Acres"], 2)
        total_dict["Farmer count"] = round(total_dict["Farmer count"] + temp_dict["Farmer count"], 2)
        total_dict["Farmer TP area"] = round(total_dict["Farmer TP area"] + temp_dict["Farmer TP area"], 2)
        total_dict["Gps area"] = round(total_dict["Gps area"] + temp_dict["Gps area"], 2)
        total_dict["TP Acres"] = round(total_dict["TP Acres"] + temp_dict["TP Acres"], 2)
        total_dict["Farmer count gps"] = round(total_dict["Farmer count gps"] + temp_dict["Farmer count gps"], 2)
        total_dict["Ratio GPS to TP"] = round(total_dict["Ratio GPS to TP"] + temp_dict["Ratio GPS to TP"], 2)
        master_list.append(temp_dict)
    master_list.append(total_dict)
    df = pd.DataFrame(master_list)
    df = df.fillna(0)
    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "agent_day_wise.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:G1", "DAYWISE " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "agent_day_wise.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = df.to_dict("r")
    return Response(document, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_procurement_str_value(request):
    print(request.data)
    Procurement.objects.filter(id=request.data["procurement_id"]).update(
        str_weight=request.data["str_weight"], remark=request.data["description"]
    )
    print(Procurement.objects.get(id=request.data["procurement_id"]).str_weight)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
def serve_harvest_forcast_for_date(request):
    # print(request.data)
    # request_data
    print("forcast ")
    sowing_lifespan_days = 118
    forcast_date = datetime.datetime.now().date()
    minimum_sowing_date = forcast_date - datetime.timedelta(days=sowing_lifespan_days)
    first_harvest_sowing_date = forcast_date - datetime.timedelta(days=145)

    # step 1
    harvest_values = (
        Harvest.objects.filter(sowing__sowing_date__gte=minimum_sowing_date)
            .order_by("-date_of_harvest")
            .values_list(
            "id",
            "sowing_id",
            "sowing__area",
            "sowing__crop_id",
            "date_of_harvest",
            "nth_harvest__harvest_name",
        )
    )
    harvest_columns = [
        "harvest_id",
        "sowing_id",
        "area",
        "crop_id",
        "date_of_harvest",
        "nth_harvest",
    ]
    harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)

    # step 2
    sowing_id_with_cound_df = (
        harvest_df.groupby("sowing_id").size().reset_index(name="count")
    )

    # step 3
    harvest_df = harvest_df.drop_duplicates(subset=["sowing_id"], keep="first")

    harvest_df = harvest_df.merge(
        sowing_id_with_cound_df, how="left", left_on="sowing_id", right_on="sowing_id"
    )
    harvest_df = harvest_df[harvest_df["count"] < 10]
    harvest_df["next_harvest"] = (
            pd.to_datetime(harvest_df["date_of_harvest"], format="%Y-%m-%d")
            + datetime.timedelta(days=7)
    ).dt.date
    harvest_df["count"] = harvest_df["count"] + 1
    harvest_df[harvest_df["next_harvest"] == datetime.datetime.now().date()]

    # find firt harvest sowing
    harvest_df[harvest_df["next_harvest"] == datetime.datetime.now().date()]
    sowing_values = Sowing.objects.filter(
        sowing_date=first_harvest_sowing_date
    ).values_list("id", "sowing_date", "area", "crop_id")
    sowing_columns = ["sowing_id", "sowing_date", "area", "crop_id"]
    sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)
    sowing_df = sowing_df.assign(
        **{
            "date_of_harvest": forcast_date,
            "nth_harvest": None,
            "count": 1,
            "harvest_id": np.nan,
        }
    )
    harvest_df["predicted_harvest_weight_in_kg"] = harvest_df.apply(
        lambda row: predict_yield(row["crop_id"], str(row["count"]), row["area"]),
        axis=1,
    )
    sowing_df["predicted_harvest_weight_in_kg"] = sowing_df.apply(
        lambda row: predict_yield(row["crop_id"], str(row["count"]), row["area"]),
        axis=1,
    )
    total = (
            harvest_df.head()["predicted_harvest_weight_in_kg"].sum()
            + sowing_df["predicted_harvest_weight_in_kg"].sum()
    )
    return Response(data={"total": total}, status=status.HTTP_200_OK)


def predict_yield(crop_id, harvest_level_name, area):
    return YeildPrediction.objects.get(
        crop_id=crop_id, harvest_range__harvest_name=harvest_level_name
    ).expected_yeild_weight_in_kg * Decimal(area)


@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
def serve_yeild_forecast_data(request):
    print(request.data)
    season_id = request.data['season_id']
    # cluster
    if len(request.data["cluster_ids"]) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list("id", flat=True))
    # super_visor
    if len(request.data["super_visor_ids"]) == 0:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True))
    else:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5, user_id__in=request.data["super_visor_ids"]).values_list("user_id", flat=True))
    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    else:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6, user_id__in=request.data["agent_ids"]).values_list("user_id", flat=True))

    #  farmer cluster
    cluster_based_farmers_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list("farmer_id", flat=True))

    # supervisor_based
    user_farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=supervisor_ids,farmer__season_id=season_id,
                                                        farmer__farmer__id__in=cluster_based_farmers_ids)
                           .values_list("farmer__farmer_id", flat=True))

    # agent farmer map
    farmer_ids = list(
        AgentFarmerMap.objects.filter(
            agent_id__in=agent_ids,
            farmer__season_id=season_id,
            farmer__farmer__id__in=user_farmer_ids,
        ).values_list("farmer__farmer_id", flat=True)
    )

    # make sowing df
    values = (Sowing.objects.filter(cultivation_phase_id=2, season_id=season_id, farmer_id__in=farmer_ids, is_active=True)
            .values_list("id", "sowing_date").values_list("id", "sowing_date", "area", "crop_id"))
    columns = ["id", "sowing_date", "area", "crop_id"]
    df = pd.DataFrame(list(values), columns=columns)

    # df['sowing_date'] = pd.to_datetime(df['sowing_date'], format="%Y-%m-%d")
    forecast_date = datetime.datetime.strptime(request.data["selected_date"], "%Y-%m-%d").date()

    df["forecast_date"] = forecast_date

    df['forecast_date'] = pd.to_datetime(df['forecast_date'], format="%Y-%m-%d", errors='coerce')
    df['sowing_date'] = pd.to_datetime(df['sowing_date'], format="%Y-%m-%d", errors='coerce')

    # find sowing age baseed on forecast date
    df["date_diff"] = (df["forecast_date"] - df["sowing_date"]).dt.days
    print(df)

    # make dict for loop purpose {'harvest_Count': 'harvest_days'} eg: {'1': 55}
    harvest_levels = dict(HarvestLevel.objects.filter().values_list("harvest_name", "harvest_interval_duration_in_days"))

    print(harvest_levels)

    # make df only harvest sowing for forecast date
    df = df[df["date_diff"].isin(harvest_levels.values())]
    print(df)
    # sort df by harvest days
    df = df.sort_values(by=["date_diff"])

    # create 'harvest_count' column
    df.assign(**{"harvest_count": None})
    data = {"transplanted_area_wise": {}, "transplanted_quantity_wise": {}}

    # find and apply harvest count for forecast date
    if not df.empty:
        for harvest_count in harvest_levels:
            df.loc[df["date_diff"] == int(harvest_levels[harvest_count]), "harvest_count"] = harvest_count

        # find yield for every sowing
        df["yield_in_kg"] = df.apply(lambda row: predict_yield(row["crop_id"], row["harvest_count"], row["area"]),axis=1,)

        for harvest_count in df["date_diff"].unique():
            data["transplanted_area_wise"][str(harvest_count)] = df[df["date_diff"] == harvest_count]["area"].sum()
            data["transplanted_quantity_wise"][str(harvest_count)] = round(df[df["date_diff"] == harvest_count]["yield_in_kg"].sum() / 1000,2)

        data["total_transplanted_area"] = round(df["area"].sum(), 2)
        data["total_transplanted_qty"] = round(df["yield_in_kg"].sum() / 1000, 2)

    else:
        data = "empty"
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_static_harvest_forecast_for_date_range(request):
    season_id = request.data['season_id']
    cluster_ids = request.data['cluster_ids']
    agent_ids = request.data["agent_ids"]
    supervisor_ids = request.data["super_visor_ids"]
    from_date = request.data["date_from"]
    to_date = request.data["date_to"]
    # cluster
    if len(cluster_ids) == 0:
        cluster_ids = list(Cluster.objects.all().values_list("id", flat=True))
    else:
        cluster_ids = list(Cluster.objects.filter(id__in=cluster_ids).values_list("id", flat=True))
    # super_visor
    if len(supervisor_ids) == 0:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True))
    else:
        supervisor_ids = list(UserProfile.objects.filter(user_type_id=5, user_id__in=supervisor_ids).values_list("user_id", flat=True))
    # agent
    if len(agent_ids) == 0:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    else:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6, user_id__in=agent_ids).values_list("user_id", flat=True))

    #  farmer cluster
    cluster_based_farmers_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list("farmer_id", flat=True))

    # supervisor_based
    user_farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=supervisor_ids,farmer__season_id=season_id,farmer__farmer__id__in=cluster_based_farmers_ids,).values_list("farmer__farmer_id", flat=True))

    # agent farmer map
    farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=agent_ids,farmer__season_id=season_id,farmer__farmer__id__in=user_farmer_ids,).values_list("farmer__farmer_id", flat=True))

    sowing_values = (Sowing.objects.filter(cultivation_phase_id=2, season_id=season_id, farmer_id__in=farmer_ids,is_active=True).values_list("id", "sowing_date").values_list("id", "sowing_date", "area", "crop_id"))
    sowing_columns = ["id", "sowing_date", "area", "crop_id"]
    sowing_df = pd.DataFrame(list(sowing_values), columns=sowing_columns)

    date_from = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    date_to = datetime.datetime.strptime(to_date, "%Y-%m-%d")

    date_range_difference = (date_to - date_from).days
    forecast_dates = pd.date_range(date_from, periods=date_range_difference, freq="D")

    harvest_levels = HarvestLevel.objects.filter()
    
    harvest_interval = harvest_levels.values_list("harvest_interval_duration_in_days", flat=True)
    harvest_key_pair = dict(harvest_levels.values_list("harvest_name", "harvest_interval_duration_in_days"))
    data = defaultdict(dict)

    for forecast_date in forecast_dates:
        print(forecast_date)
        harvest_availabel_df = sowing_df.copy()
        harvest_availabel_df["forecast_date"] = forecast_date.date()
        harvest_availabel_df["date_diff"] = (harvest_availabel_df["forecast_date"] - harvest_availabel_df["sowing_date"]).dt.days
        harvest_availabel_df = harvest_availabel_df[harvest_availabel_df["date_diff"].isin(harvest_interval)]
        harvest_availabel_df = harvest_availabel_df.sort_values(by=["date_diff"])
        harvest_availabel_df.assign(**{"harvest_count": None})

        print(harvest_availabel_df)
        if not harvest_availabel_df.empty:
            # assign harvest count for sowing
            for level in harvest_key_pair:
                print("for in level")
                harvest_availabel_df.loc[harvest_availabel_df["date_diff"] == int(harvest_key_pair[level]),"harvest_count",] = level

            harvest_availabel_df["yield_in_kg"] = harvest_availabel_df.apply(lambda row: predict_yield(row["crop_id"], row["harvest_count"], row["area"]),axis=1,)
            data[str(forecast_date.date())] = {
                "total_yield": (round(harvest_availabel_df["yield_in_kg"].sum(), 2) / 1000),
                "total_area": round(harvest_availabel_df["area"].sum()),
            }
            print("for done ")
            print(data)
    df = pd.DataFrame(list(data.items()), columns=["Date", "Value"])
    df = pd.DataFrame(data)
    df_t = df.T
    df_t.loc['Total']= df_t.sum()
    df_t = df_t.reset_index()
    data = df_t.groupby('index').apply(lambda x:x.to_dict('r')[0]).to_dict()
    print(df_t.to_dict('r'))

    if df_t.empty:
        document = {
            'data_avaliable' : False,
            'aleart' : "No Data Avaliable !!!",
            'data' : ''
        }
        return Response(data=document, status=status.HTTP_200_OK)
    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "date_range_wise_forecast.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df_t.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:C1","Date range forecast report for  " + str(date_from) + " " + str(date_to),merge_format,)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {
        'data_avaliable' : True,
        'aleart' : "Data Avaliable !!!",
        'data' : ''
    }
    try:
        image_path = str("static/media/") + "date_range_wise_forecast.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = data
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_crop_age_based_report(request):
    # farmer
    season_id = request.data['season_id']
    # cluster
    if len(request.data["cluster_ids"]) == 0:
        active_season_ids = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True)
        cluster_ids = list(Cluster.objects.filter(id__in=active_season_ids).values_list("id", flat=True))
    else:
        cluster_ids = list(Cluster.objects.filter(id__in=request.data["cluster_ids"]).values_list("id", flat=True))
        print("cluster filter")
    # super_visor
    supervisor_ids = list(UserProfile.objects.filter(user_type_id=5).values_list("user_id", flat=True))

    # agent
    if len(request.data["agent_ids"]) == 0:
        agent_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    else:
        print("agent filter")
        agent_ids = list(UserProfile.objects.filter(user_type_id=6, user_id__in=request.data["agent_ids"]).values_list("user_id", flat=True))

    #  farmer cluster
    cluster_based_farmers_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids).values_list("farmer_id", flat=True))

    # supervisor_based
    user_farmer_ids = list(UserFarmerMap.objects.filter(officer_id__in=supervisor_ids,farmer__season_id=season_id,farmer__farmer__id__in=cluster_based_farmers_ids,).values_list("farmer__farmer_id", flat=True))


    # agent farmer map
    farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=agent_ids,farmer__season_id=season_id,farmer__farmer__id__in=user_farmer_ids,).values_list("farmer__farmer_id", flat=True))

    # farmer_ids = Harvest.objects.filter(sowing__season_id=2).values_list('sowing__farmer__id', flat=True)
    filtered_farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id__in=farmer_ids).values_list("farmer__id", flat=True))

    
    sowing_obj = Sowing.objects.filter(farmer_id__in=filtered_farmer_ids, season_id=season_id, cultivation_phase_id=request.data['selected_cultivation_phase_ids'])
    
    # if len(request.data['selected_cultivation_phase_ids']) != 0:
    #   else:
    #     sowing_obj = Sowing.objects.filter(farmer_id__in=filtered_farmer_ids, season_id=season_id)

    sowing_values = list(sowing_obj.values_list("id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase__name",))
    sowing_columns = [ "sowing_id", "farmer_id", "sowing_date", "area", "cultivation_phase_id", "cultivation_phase_name"]
    sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)
    today = datetime.datetime.now().date()

    sowing_df["crop_age"] = today - sowing_df["sowing_date"]
    sowing_df["crop_age"] = sowing_df["crop_age"].astype("timedelta64[D]")
    sowing_df["crop_age"] = sowing_df["crop_age"].astype(int)
    if request.data['selected_cultivation_phase_ids'] == 1:
        range_list = [ "5-10","11-15","16-20", "21-25", "26-30", "31-35", "35-40", "40-135"]    
    else:
        range_list = [ "0-54", "55-61", "62-68", "69-75", "76-82", "83-89", "90-96", "97-103", "104-110", "111-117", "118-124"]
    master_dict = {}
    total = 0
    for row in range_list:
        above_sowing_df = sowing_df[(sowing_df["crop_age"] >= int(row.split("-")[0]))]
        below_sowing_df = above_sowing_df[(above_sowing_df["crop_age"] <= int(row.split("-")[1]))]
        master_dict[row] = below_sowing_df["area"].sum()
        total = total + below_sowing_df["area"].sum()
    above_sowing_df = sowing_df[(sowing_df["crop_age"] >= int(row.split("-")[0]))]
    master_dict["125 +"] = above_sowing_df["area"].sum()
    master_dict["total"] = total + above_sowing_df["area"].sum()
    df = pd.DataFrame(list(master_dict.items()), columns=["Age range in days", "Total Area"])
    # df =  pd.DataFrame(master_dict)

    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "sowing_age_wise_report.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:C1", "Sowing Age wise report", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "sowing_age_wise_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = master_dict
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_access_controll(request):
    user_type = UserProfile.objects.get(user=request.user).user_type
    module_ids = (
        UsertypeBasedAccessControl.objects.filter(
            hardware_device_id=request.data["device_id"], user_type=user_type, access=True
        )
            .distinct("module_id")
            .values_list("module_id", flat=True)
    )
    data = {"module_ids": module_ids}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_farmer_harvest_count_wise(request):
    document = {}
    try:
        image_path = str("static/media/") + "harvest_wise_reports.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    # data = fine_df.to_dict('r')
    return Response(data=document, status=status.HTTP_200_OK)



@api_view(["POST"])
def agent_wise_harvest_report_for_mobile(request):
    user_type_id = UserProfile.objects.get(user=request.user).user_type_id
    user_id = request.user.id
    season_id= request.data['season_id']
    if user_type_id == 5:
        sub_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                sub_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            sub_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))

    master_dict = {}
    master_dict["total_farmer"] = 0
    master_dict["total_harvest_area"] = 0
    master_dict["agents"] = {}
    sub_ids = list(UserProfile.objects.filter(user_id__in=sub_ids, user_type_id=6).order_by('user__first_name').values_list("user_id", flat=True))
    for agent_user_id in sub_ids:
        agent_name = (str(User.objects.get(id=agent_user_id).first_name) + " " + str(User.objects.get(id=agent_user_id).last_name))
        master_dict["agents"][agent_name] = {}
        farmer_ids = list(AgentFarmerMap.objects.filter(agent_id=agent_user_id, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        master_dict["agents"][agent_name]["farmer_count"] = len(farmer_ids)
        master_dict["agents"][agent_name]["seed_ac"] = "-"
        master_dict["agents"][agent_name]["nursery_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1).aggregate(Sum("area"))["area__sum"]
        master_dict["agents"][agent_name]["main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
        if Harvest.objects.filter(sowing__farmer__id__in=farmer_ids, sowing__season_id=season_id).exists():
            master_dict["agents"][agent_name]["harvest_area"] = (Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id,).aggregate(Sum("value"))["value__sum"]) / 1000
            master_dict["total_farmer"] += len(farmer_ids)
            if Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).aggregate(Sum("value"))["value__sum"] != None:
                master_dict["total_harvest_area"] = master_dict["total_harvest_area"] + (Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).aggregate(Sum("value"))["value__sum"] / 1000)
        else:
            master_dict["agents"][agent_name]["harvest_area"] = Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).aggregate(Sum("value"))["value__sum"]
            master_dict["total_farmer"] += len(farmer_ids)
    filter_farm_ids = list(AgentFarmerMap.objects.filter(agent_id__in=sub_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
    master_dict["total_nursery_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=filter_farm_ids, cultivation_phase_id=1).aggregate(Sum("area"))["area__sum"]
    master_dict["total_main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=filter_farm_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
    master_dict["total_seed_ac"] = "-"
    master_dict["season"] = Season.objects.get(id=season_id).name
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_sowing_active_status(request):
    print(request.data)
    sowing_obj = Sowing.objects.get(id=request.data["sowing_id"])
    if request.data["selected_casue"] == 2:
        sowing_obj.is_active = False 
        sowing_obj.reason_for_inactive=request.data["reason"]
    if request.data["selected_casue"] == 1:
        sowing_obj.is_active = False 
        sowing_obj.reason_for_inactive="Reached maximum harvest count"
    sowing_obj.save()
    
    if 'uploaded_images' in request.data:
        for image in request.data['uploaded_images']:
            ShowingActivityImages.objects.create(
                sowing=sowing_obj,
                cultivation_phase_id=request.data["selected_casue"],
                image=create_complete_image(image)
            )
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def afs_wise_harvest_report_for_mobile(request):
    print("afs wise ---")
    season_id = request.data['season_id']
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        available_cluster_ids = list(UserClusterMap.objects.filter(user=request.user, season_id=season_id).values_list("cluster_id", flat=True))
        sub_ids = [request.user.id]
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                sub_ids = list(subordinates.values_list("subordinate", flat=True))
        else:
            sub_ids = list(UserClusterMap.objects.filter(user__userprofile__user_type_id=5, season_id=season_id).values_list('user_id', flat=True))
            active_season_clusters = ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id')

    master_dict = {}
    master_dict["total_farmer"] = 0
    master_dict["total_harvest_area"] = 0
    master_dict["afs"] = {}
    sub_ids = list(UserProfile.objects.filter(user_id__in=sub_ids, user_type_id=5).values_list("user_id", flat=True))
    for afs_user_id in sub_ids:
        afs_name = str(User.objects.get(id=afs_user_id).username)
        master_dict["afs"][afs_name] = {}
        farmer_ids = list(UserFarmerMap.objects.filter(officer_id=afs_user_id, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        master_dict["afs"][afs_name]["farmer_count"] = len(farmer_ids)
        master_dict["afs"][afs_name]["seed_ac"] = "-"
        master_dict["afs"][afs_name]["nursery_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1).aggregate(Sum("area"))["area__sum"]
        master_dict["afs"][afs_name]["main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
        master_dict["total_farmer"] += len(farmer_ids)
        if Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).aggregate(Sum("value"))["value__sum"] != None:
            master_dict["total_harvest_area"] += (Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id).aggregate(Sum("value"))["value__sum"] / 1000)
            master_dict["afs"][afs_name]["harvest_area"] = (Harvest.objects.filter(sowing__farmer__id__in=farmer_ids,sowing__season_id=season_id,).aggregate(Sum("value"))["value__sum"] / 1000)
    filter_farm_ids = list(UserFarmerMap.objects.filter(officer__in=sub_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
    master_dict["total_nursery_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=filter_farm_ids, cultivation_phase_id=1).aggregate(Sum("area"))["area__sum"]
    master_dict["total_main_area"] = Sowing.objects.filter(season_id=season_id, farmer_id__in=filter_farm_ids, cultivation_phase_id=2).aggregate(Sum("area"))["area__sum"]
    master_dict["total_seed_ac"] = "-"
    master_dict["season"] = Season.objects.get(id=season_id).name
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def validate_farmer_code_with_sowing_status(request):
    print(request.data)
    result = {}
    result['status'] = 2
    print("came for check")
    season_id =get_active_season_id()
    if FarmerClusterSeasonMap.objects.filter(seasonal_farmer_code=request.data["farmer_code"]).exists():
        farmer = FarmerClusterSeasonMap.objects.get(seasonal_farmer_code=request.data["farmer_code"]).farmer
        farmer_id = farmer.id
        print('farmer_id:', farmer_id)
        print('other_Agent', Procurement.objects.get(ticket_number=request.data["ticket_number"]).have_other_agent_farmer)
        # not accepting other agent farmers means check wheather this farmer exists inside the correct agent
        if not Procurement.objects.get(ticket_number=request.data["ticket_number"]).have_other_agent_farmer:
            if AgentFarmerMap.objects.filter(farmer__farmer_id=farmer_id, agent_id=request.data["agent_id"], farmer__season_id=season_id).exists():
                if Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id, is_active=True, season_id=season_id).exists():
                    result['status'] = 1
                    result['farmer_name'] = farmer.first_name
        # if accepting means is should be other agents farmers only
        else:
            # if not AgentFarmerMap.objects.filter(farmer__farmer_id=farmer_id, agent_id=request.data["agent_id"], farmer__season_id=season_id).exists():
            if Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer_id, is_active=True, season_id=season_id).exists():
                result['status'] = 1
                result['farmer_name'] = farmer.first_name
                print('else' ,result)
    print(result)
    return Response(result, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_cluster_based_on_loged_user(request):
    user_type_id = UserProfile.objects.get(user_id=request.user.id).user_type_id
    user_id = request.user.id
    season_id= get_active_season_id()
    subordinate_user_ids = []
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=get_active_season_id()).values_list('supervisor_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=get_active_season_id()).values_list('supervisor_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinates = UserHierarchyMap.objects.filter(superior_user_type_id=3, season_id=season_id)
            subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))
    subordinate_user_ids = list(UserProfile.objects.filter(user_id__in=subordinate_user_ids, user_type_id=5).values_list("user_id", flat=True))

    sub_ids = UserProfile.objects.filter(user_id__in=subordinate_user_ids, user_type_id=5).values_list("user_id", flat=True)
    print(sub_ids)

    cluster_ids = set(list(UserClusterMap.objects.filter(user_id__in=sub_ids,season_id=get_active_season_id()).values_list("cluster_id", flat=True)))
    clusters = []

    for cluster in Cluster.objects.filter(id__in=cluster_ids):
        cluster_dict = {}
        cluster_dict["name"] = cluster.name
        cluster_dict["id"] = cluster.id
        clusters.append(cluster_dict)

    return Response(clusters, status=status.HTTP_200_OK)


# maunal gps fencing
@api_view(["POST"])
def save_manual_entry(request):
    print(request.data)
    Sowing.objects.filter(id=request.data["sowing_id"]).update(
        is_geo_fencing_is_automatic=False,
        area_calculated_via_geo_fencing=request.data["area"],
        geo_fence_done_on=datetime.datetime.now().date(),
    )
    data = Sowing.objects.get(
        id=request.data["sowing_id"]
    ).area_calculated_via_geo_fencing
    return Response(data, status=status.HTTP_200_OK)


# access and revoke for adding other agent farmers in harvest records
@api_view(["POST"])
def change_action_for_adding_other_agent_farmer_to_harvest(request):
    procurement_obj = Procurement.objects.get(ticket_number=request.data["ticket_number"])
    p_status = procurement_obj.have_other_agent_farmer
    print(not p_status)
    procurement_obj.have_other_agent_farmer = not p_status
    procurement_obj.save()
    data = "success"
    return Response(data, status=status.HTTP_200_OK)


# remove harvest entries
@api_view(["POST"])
def remove_harvest(request):
    Harvest.objects.filter(id=request.data["harvest_id"]).delete()
    data = {}
    data["message"] = "Harvest removed success !"
    return Response(data, status=status.HTTP_200_OK)


# remove procuremnet, adjut agent wallet, transaction logs
@api_view(["POST"])
def remove_procurement(request):
    procurement_obj = Procurement.objects.get(id=request.data["procurement_id"])
    procurement_group_id = procurement_obj.procurement_group_id
    procurement_group_obj = ProcurementGroup.objects.get(id=procurement_group_id)
    agent_id = procurement_obj.procurement_group.agent_id
    wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
    wallet_amount = wallet_obj.current_balance
    updated_wallet_amount = wallet_amount - procurement_group_obj.payment_to_wallet
    wallet_obj.current_balance = updated_wallet_amount
    wallet_obj.save()
    print("wallet updated")
    transaction_log_ids = ProcurementTransactionMap.objects.filter(
        procurement=procurement_obj
    ).values_list("transaction_log", flat=True)
    AgentTransactionLog.objects.filter(id__in=transaction_log_ids).delete()
    print("agent transaction deleted")
    ticket_number = procurement_obj.ticket_number
    if Harvest.objects.filter(ticket_number=ticket_number).exists():
        Harvest.objects.filter(ticket_number=ticket_number).delete()
        print("harvest removed")
    procurement_group_obj.delete()
    print("procurement and procurement group and transactions deleted")
    return Response(status=status.HTTP_200_OK)


# remove harvest entries
@api_view(["POST"])
@permission_classes((AllowAny,))
def get_pending_harvest_report(request):
    master_list = []
    season_id = request.data['selected_season_id']
    print('season_id:',season_id)
    for row in Procurement.objects.filter(procurement_group__season_id=season_id):
        if not Harvest.objects.filter(ticket_number=row.ticket_number).exists():
            master = {}
            master["Ticket Number"] = row.ticket_number
            master["Date"] = row.procurement_group.procurement_date
            master["Agent"] = row.procurement_group.agent.first_name
            master_list.append(master)
    master_list
    df = pd.DataFrame(master_list)
    writer = pd.ExcelWriter(
        str("static/media/") + "non_harvested_procurement.xlsx", engine="xlsxwriter"
    )
    # creating excel sheet with name

    df.to_excel(writer, index=False, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range(
        "A1:D1", "NON HARVESTED PROCUREMENT " + str(date), merge_format
    )

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "non_harvested_procurement.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    # data = fine_df.to_dict('r')
    return Response(data=document, status=status.HTTP_200_OK)


# remove harvest entries
@api_view(["POST"])
def get_dual_agent_load_report(request):
    season_id = request.data['selected_season_id']
    print('season_id:', season_id)
    harvest_list = list(Harvest.objects.filter(sowing__season_id=season_id).values_list("id","sowing__farmer_id","ticket_number","date_of_harvest","value",))
    harvest_columns = ["id","farmer_id","ticket_number","date","value",]
    harvest_df = pd.DataFrame(harvest_list, columns=harvest_columns)

    procurement_list = list(Procurement.objects.filter(procurement_group__season_id=season_id).values_list("ticket_number", "procurement_group__agent_id", "procurement_group__agent__first_name",))
    procurement_columns = ["ticket_number","procurement_agent_id","procurement_agent_first_name",]
    procurement_df = pd.DataFrame(procurement_list, columns=procurement_columns)

    agent_farmer_map_list = list(AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("agent_id", "agent__first_name", "farmer__seasonal_farmer_code", "farmer__farmer_id"))
    agent_farmer_columns = ["mapped_agent_id", "agent_first_name", "farmer_code","farmer_id",]
    agent_df = pd.DataFrame(agent_farmer_map_list, columns=agent_farmer_columns)

    procurement_harvest_merged = pd.merge(harvest_df,procurement_df,left_on="ticket_number",right_on="ticket_number",how="left",)
    procurement_harvest_agent_merged = pd.merge( agent_df, procurement_harvest_merged, left_on="farmer_id", right_on="farmer_id", how="left",)

    procurement_harvest_agent_merged = procurement_harvest_agent_merged.fillna(0)
    procurement_harvest_agent_merged["procurement_agent_id"] = procurement_harvest_agent_merged["procurement_agent_id"].astype(int)

    new_df = procurement_harvest_agent_merged[procurement_harvest_agent_merged["mapped_agent_id"] != procurement_harvest_agent_merged["procurement_agent_id"]]

    df = new_df[new_df["ticket_number"] != 0]

    df = df.drop(["mapped_agent_id", "farmer_id", "id",  "procurement_agent_id"],axis=1,)
    # initializing excel
    writer = pd.ExcelWriter(str("static/media/") + "mismatch_harvest.xlsx", engine="xlsxwriter")

    df.to_excel(writer, index=False, sheet_name="Sheet1", startrow=1)
    print(df.columns)
    df = df.rename(columns={'agent_first_name' : 'Agent First Name', 'farmer_code' : 'Farmer Code', 'ticket_number' : 'Ticket Number', 'date' : 'Date', 'value' : 'Value',
       'procurement_agent_first_name' : 'Procurement Agent First Name',})
    # creating excel sheet with name
    df.to_excel(writer, index=False, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format({"bold": 1,"border": 1,"align": "center","valign": "vcenter","fg_color": "yellow",})

    # Merge 3 cells.
    worksheet.merge_range("A1:G1", "Dual agent load Report", merge_format)
    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 27, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "mismatch_harvest.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    print("dual")
    return Response(data=document, status=status.HTTP_200_OK)


# remove harvest entries
@api_view(["POST"])
def serve_farmer_harvest_report(request):
    document = {}
    season_id = request.data['selected_season_id']
    print('season_id:', season_id)
    harvest_list = list(Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).values_list("id", "sowing__farmer__id","sowing__farmer__village__name", "sowing__farmer__first_name","sowing__farmer__last_name", 
                                                                                       "sowing__area","sowing__sowing_date", "date_of_harvest", "value","ticket_number"))
    harvest_columns = ["harvest_id", "farmer_id", "farmer_village_name", "farmer_first_name","farmer_last_name", "sowing_area", "date_of_sowing", "date_of_harvest", "harvested_value","ticket_number"]
    harvest_df = pd.DataFrame(harvest_list, columns=harvest_columns)
    

    procurement_list = list(Procurement.objects.filter(ticket_number__in=harvest_df['ticket_number'], procurement_group__season_id=season_id).values_list('ticket_number','vehicle_number'))
    procurement_columns = ['ticket_number', 'vehicle_number']
    procurement_df = pd.DataFrame(procurement_list, columns=procurement_columns)

    farmer_ids = list(set(list(Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).values_list("sowing__farmer_id", flat=True))))

    farmer_cluster_season_map_list = list(FarmerClusterSeasonMap.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list("id", "seasonal_farmer_code","cluster_id", "cluster__name","farmer_id"))
    farmer_cluster_season_map_columns = ["farmer_cluster_map_id", "farmer_code","cluster_id", "cluster_name", "farmer_id", ]
    farmer_cluster_season_map_df = pd.DataFrame(farmer_cluster_season_map_list, columns=farmer_cluster_season_map_columns)
    

    # agent farmer map df
    farmer_cluster_season_map_ids = list(FarmerClusterSeasonMap.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list("id", flat=True))

    agent_farmer_list = list(AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id", "agent__first_name", "agent__id", "farmer__farmer_id"))
    agent_farmer_columns = ["agent_farmer_id", "agent_name", "agent_id", "farmer_id"]
    agent_df = pd.DataFrame(agent_farmer_list, columns=agent_farmer_columns)
    

    # user farmer map df
    user_farmer_list = list(UserFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id", "officer__username", "officer__id", "farmer__farmer_id"))
    user_farmer_columns = ["user_farmer_id", "supervisor_name", "supervisor_id", "farmer_id"]
    user_df = pd.DataFrame(user_farmer_list, columns=user_farmer_columns)
    

    # merging harvest and farmer cluster map
    procurement_harvest_map = pd.merge(harvest_df, procurement_df, left_on="ticket_number", right_on="ticket_number",how="left")

    harvest_cluster_map = pd.merge(procurement_harvest_map, farmer_cluster_season_map_df, left_on="farmer_id", right_on="farmer_id",how="left")

    # agent map with harvest_cluster_map
    agent_harvest_cluster_map = pd.merge(harvest_cluster_map, agent_df, left_on="farmer_id", right_on="farmer_id",how="left")

    # supervisor map with harvest_cluster_map
    df = pd.merge(agent_harvest_cluster_map, user_df, left_on="farmer_id", right_on="farmer_id", how="left", )

    df = df.drop(["harvest_id", "farmer_id", "farmer_cluster_map_id", "cluster_id", "agent_id", "user_farmer_id","supervisor_id", ], axis=1, )
    df = df[["farmer_code", "farmer_first_name", "farmer_last_name", "farmer_village_name", "cluster_name","date_of_sowing", "date_of_harvest", "ticket_number","vehicle_number",
            "sowing_area","harvested_value","agent_name","supervisor_name",]]
    

    # writer = pd.ExcelWriter(str("static/media/") + "farmers_harvest_report.xlsx", engine="xlsxwriter")

    writer = pd.ExcelWriter(str("static/media/") + "farmers_harvest_report.xlsx", engine="xlsxwriter")
    final_df = df 
    print(final_df.columns)
    final_df = final_df.rename(columns={'farmer_code' : 'Farmer Code', 'farmer_first_name' : 'farmer First Name', 'farmer_last_name' : 'Farmer Nast Name',
       'farmer_village_name' : 'farmer Village Name', 'cluster_name' : 'Cluster Name', 'date_of_sowing' : 'Date Of Sowing',
       'date_of_harvest' : 'Date Of Harvest', 'ticket_number' : 'Ticket Number', 'vehicle_number' : 'Vehicle Number', 'sowing_area' : 'Sowing Area',
       'harvested_value' : 'Harvested Value', 'agent_name' : 'Agent Name', 'supervisor_name' : 'Supervisor Name',})

    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())
    # creating excel sheet with name
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:N1", "farmers_harvest_report" + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    print('ok...')
    try:
        image_path = str("static/media/") + "farmers_harvest_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


    # assigning that sheet to obj
    # workbook = writer.book

    # merge_format = workbook.add_format(
    #     {
    #         "bold": 1,
    #         "border": 1,
    #         "align": "center",
    #         "valign": "vcenter",
    #         "fg_color": "yellow",
    #     }
    # )

    # header_format = workbook.add_format({"fg_color": "#D7E4BC"})
    # format1 = workbook.add_format({"num_format": "#,##0.00"})

    # for cluster in Cluster.objects.all():
    #     cluster_based_df = df[df["cluster_name"] == cluster.name]
    #     cluster_based_df.to_excel(
    #         writer, sheet_name=str(cluster.name), index=False, startrow=1
    #     )
    #     cluster = writer.sheets[str(cluster.name)]
    #     cluster.merge_range("A1:N1", "farmers harvest data report", merge_format)
    #     format1 = workbook.add_format({"num_format": "#,##0.00"})
    #     cluster.set_column("B:B", 18, format1)
    #     cluster.set_column(0, 11, 20)

    #     # Write the column headers with the defined format.
    #     for col_num, value in enumerate(df.columns.values):
    #         cluster.write(0, col_num + 1, value, header_format)
    # writer.save()
    # document = {}
    # try:
    #     image_path = str("static/media/") + "farmers_harvest_report.xlsx"
    #     with open(image_path, "rb") as image_file:
    #         encoded_image = b64encode(image_file.read())
    #         document["excel"] = encoded_image
    # except Exception as err:
    #     print(err)
# farmer_consolidated_report
@api_view(["POST"])
def farmer_consolidated_report(request):
    # famer_data
    season_id = request.data['season_id']
    harvest_table_list = list(Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).values_list("sowing__farmer__code","sowing__farmer__first_name","sowing__farmer__last_name","sowing__farmer__village__name","sowing__season__name",
                                                                "value","date_of_harvest","sowing__area","sowing__farmer__cluster__name"))
    column_list = ["farmer_code","farmer_first_name","farmer_last_name","farmer_village","season","yeald","date_of_harvest","area","cluster_name"]
    harvest_data_frame = pd.DataFrame(harvest_table_list, columns=column_list)

    # agent_data
    agent_farmer_list = list(AgentFarmerMap.objects.filter(farmer__farmer__code__in=harvest_data_frame["farmer_code"], farmer__season_id=season_id).values_list("farmer__farmer__code", "agent__first_name"))
    agent_farmer_columns = ["farmer_code", "agent_name"]
    agent_farmer_df = pd.DataFrame(agent_farmer_list, columns=agent_farmer_columns)

    # supervisor_data
    supervisor_farmer_list = list(UserFarmerMap.objects.filter(farmer__farmer__code__in=harvest_data_frame["farmer_code"], farmer__season_id=season_id).values_list("farmer__farmer__code", "officer__username"))
    supervisor_farmer_colums = ["farmer_code", "supervisor_name"]
    supervisor_farmer_df = pd.DataFrame(supervisor_farmer_list, columns=supervisor_farmer_colums)

    # merged_data
    farmer_agent_map_df = pd.merge(harvest_data_frame,agent_farmer_df,left_on="farmer_code",right_on="farmer_code", how="left")
    supervisor_fatmer_agent_map_df = pd.merge(farmer_agent_map_df,supervisor_farmer_df,left_on="farmer_code",right_on="farmer_code" , how="left")

    # sum yeald and find last harvest date finally merge with supervisor_fatmer_agent_map_df
    grouped_df = (supervisor_fatmer_agent_map_df.groupby(["farmer_code"]).agg({"yeald": "sum", "date_of_harvest": "max"}).rename(columns={"yeald": "total_yeild", "date_of_harvest": "last_harvest_date"}))

    final_supervisor_fatmer_agent_map_df = pd.merge(supervisor_fatmer_agent_map_df,grouped_df,left_on="farmer_code",right_index=True, how="left")
    final_supervisor_fatmer_agent_map_df = final_supervisor_fatmer_agent_map_df.drop(columns=["yeald", "date_of_harvest"])
    final_supervisor_fatmer_agent_map_df = (final_supervisor_fatmer_agent_map_df.drop_duplicates())

    # final_df
    df = final_supervisor_fatmer_agent_map_df.reindex(columns=["farmer_code","farmer_first_name","farmer_last_name","farmer_village","cluster_name","agent_name","supervisor_name","last_harvest_date","area","total_yeild",])
    df = df.drop_duplicates('farmer_code')

    df = df.rename(columns = {"farmer_code" : 'Farmer Code' ,"farmer_first_name" : 'Farmer First Name' ,'farmer_last_name' : "Farmer Last Name" ,"farmer_village" : 'Farmer Village' ,"cluster_name" : 'Cluster Name' ,"agent_name" : 'Agent Name' ,"supervisor_name" : 'Supervisor Name' ,"last_harvest_date" : 'Last Harvest Date' ,"area" : 'Area' ,"total_yeild" : 'Total Yeild' })
    df.index += 1
    total = df.sum(numeric_only=True)
    total.name = 'Total'
    df = df.append(total.transpose())
    writer = pd.ExcelWriter(
        str("static/media/") + "farmer_wise_consolidated_yeild.xlsx",
        engine="xlsxwriter",
    )

    # creating excel sheet with name
    df.to_excel(writer, index=False, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    # Merge 3 cells.
    worksheet.merge_range(
        "A1:K1", "Farmer Wise Consolidated Yeild Report", merge_format
    )
    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 27, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "farmer_wise_consolidated_yeild.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    print("dual")
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_geo_fence_for_map_visualization(request):
    # request_data
    print(request.data)
    data_dict = request.data

    # data_dict = request.data

    sowing_geo_fence_map_obj = SowingBoundaryMap.objects.filter()

    if len(data_dict["selected_data_source_ids"]) != 0:
        sowing_geo_fence_map_obj = sowing_geo_fence_map_obj.filter(data_source_id__in=data_dict["selected_data_source_ids"])

    if len(data_dict["selected_agent_ids"]) != 0:
        sowing_geo_fence_map_obj = sowing_geo_fence_map_obj.filter(sowing__farmer__farmerclusterseasonmap__agentfarmermap__agent_id__in=data_dict["selected_agent_ids"])

    sowing_boundry_ids = sowing_geo_fence_map_obj.values_list("sowing_boundry", flat=True)
    field_ids = sowing_geo_fence_map_obj.values_list("sowing_id", flat=True)

    farmer_ids = list(set(list(sowing_geo_fence_map_obj.values_list("sowing__farmer_id", flat=True))))

    sowing_geo_fence_map_list = list(
        sowing_geo_fence_map_obj.values_list( "sowing__farmer_id", "sowing_id", "sowing__area_calculated_via_geo_fencing", "data_source", "data_source__name", "sowing__farmer__first_name",
         "sowing__farmer__last_name", "sowing__farmer__village__name", "sowing__farmer__created_by__username", "sowing__farmer__created_by_id")
    )

    sowing_geo_fence_map_column = [ "farmer_id", "sowing_id", "area_in_acre", "data_source", "data_source_name", "first_name", "last_name", "farmer_village", "created_by_name", "created_by_id",]
    sowing_geo_fence_map_df = pd.DataFrame(sowing_geo_fence_map_list, columns=sowing_geo_fence_map_column)

    if data_dict["selected_cluster_ids"]:
        print("cluster filter applied")
        farmer_cluster_season_map = FarmerClusterSeasonMap.objects.filter(farmer_id__in=farmer_ids, cluster_id__in=request.data["selected_cluster_ids"],)
    else:
        farmer_cluster_season_map = FarmerClusterSeasonMap.objects.filter(farmer_id__in=farmer_ids)

    cluster_farmer_list = list(farmer_cluster_season_map.values_list("farmer_id", "cluster_id", "cluster__name"))
    cluster_farmer_columns = ["farmer_id", "cluster_id", "cluster_name"]
    cluster_df = pd.DataFrame(cluster_farmer_list, columns=cluster_farmer_columns)

    farmer_cluster_season_map_df = pd.merge(sowing_geo_fence_map_df, cluster_df, how="left")

    agent_farmer_map = list(AgentFarmerMap.objects.filter(farmer__in=farmer_cluster_season_map).values_list('farmer__farmer_id', 'agent__first_name', 'agent_id'))
    agent_columns = ['farmer_id', 'agent_name', 'agent_id']
    agent_df = pd.DataFrame(agent_farmer_map, columns=agent_columns)

    farmer_cluster_season_map_df = pd.merge(farmer_cluster_season_map_df, agent_df, left_on="farmer_id", right_on="farmer_id", how="left")

    sowing_boundry_obj = SowingBoundary.objects.filter(id__in=sowing_boundry_ids).order_by("id")

    sowing_boundry_list = list(sowing_boundry_obj.values_list("sowing_id", "latitude", "longitude"))
    sowing_boundry_column = ["sowing_id", "lat", "lng"]
    sowing_boundry_df = pd.DataFrame(sowing_boundry_list, columns=sowing_boundry_column)

    if not sowing_boundry_df.empty:
        sowing_boundry_series = (sowing_boundry_df.groupby("sowing_id").apply(lambda x: x.to_dict("r")).to_frame())
    else:
        sowing_boundry_series = sowing_boundry_df

    final_df = farmer_cluster_season_map_df.merge(sowing_boundry_series, how="left", left_on="sowing_id", right_on="sowing_id")

    if len(data_dict["selected_cluster_ids"]) != 0:
        print("cluster filter applied")
        final_df = final_df[
            final_df["cluster_id"].isin(request.data["selected_cluster_ids"])
        ]

    final_df["fillColor"] = "#14b806"
    final_df["strokeColor"] = "#14b806"


    # # fill color / bg color
    filtered_clusters = request.data["border_color_schemes"].keys()
    for index, cluster in enumerate(filtered_clusters):
        print(cluster)
        final_df.loc[final_df.cluster_name == cluster, "strokeColor"] = request.data["border_color_schemes"][cluster]
    final_df.rename(columns={0: "paths"}, inplace=True)
    final_df = final_df.fillna(0)


    # # fill color / bg color
    filtered_agents = request.data["bg_color_schemes"].keys()
    for index, agent in enumerate(filtered_agents):
        print(agent)
        final_df.loc[final_df.agent_name == agent, "fillColor"] = request.data["bg_color_schemes"][agent]

    data_dict = {
        "fence_data": final_df.to_dict("r"),
        "total_area": final_df["area_in_acre"].sum(),
        "is_data_available": final_df.empty,
    }
    final_df
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_data_source_list(request):
    data = list(FarmerDataSource.objects.filter().values("id", "name"))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_officer_list(request):
    position_users = list(PositionPositionUserMap.objects.all().values_list("user_id", flat=True))
    data = list(UserProfile.objects.filter(user_type_id__in=[5], user_id__in=position_users).values("user_id", "user__username"))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def color_picker(request):
    color_dict = {
        "border_color": ["#edf8b1","#7fcdbb","#fee8c8","#fdbb84","#fde0dd","#fa9fb5","#ef8a62","#91cf60","#bebada","#8dd3c7"],
        "bg_color": color_list
        }
    return Response(data=color_dict, status=status.HTTP_200_OK)

@api_view(["GET"])
def agent_wise_cultivation_report(request):
    agent_farmer_map_list = list(AgentFarmerMap.objects.filter(farmer__season_id=2).order_by('agent_id').values_list('agent_id', 'agent__first_name', 'farmer__farmer__code', 'farmer__farmer__sowing__cultivation_phase', 'farmer__farmer__sowing__area'))
    agent_farmer_columns = ['agent_id', 'agent_name', 'farmer_code', 'cultivation_phase', 'area']
    agent_farmer_df = pd.DataFrame(agent_farmer_map_list, columns=agent_farmer_columns).drop_duplicates()
                                
    #seprating_cultivation_phase
    df_pase1 = agent_farmer_df[agent_farmer_df['cultivation_phase']==1]
    df_pase2 = agent_farmer_df[agent_farmer_df['cultivation_phase']==2]
                                
    farmer_cultivetion_phase_df = pd.merge(df_pase1, df_pase2, left_on='farmer_code', right_on='farmer_code', how='left')
    farmer_cultivetion_phase_df = farmer_cultivetion_phase_df.rename(columns={'area_x':'naursery', 'area_y':'tp'})
    farmer_cultivetion_phase_df = farmer_cultivetion_phase_df.fillna(0)
    farmer_cultivetion_phase_df["total_area"] = farmer_cultivetion_phase_df["naursery"] + farmer_cultivetion_phase_df["tp"]

    farmer_cultivetion_phase_df = farmer_cultivetion_phase_df.drop(columns=['agent_name_y', 'agent_id_y', 'cultivation_phase_x', 'cultivation_phase_y', ])

    grouped_df = farmer_cultivetion_phase_df.groupby(['agent_id_x','agent_name_x']).agg({'farmer_code': 'unique', 'naursery': 'sum', 'tp': 'sum', 'total_area': 'sum'})
    grouped_df['farmer_count'] = grouped_df['farmer_code'].str.len()
    grouped_df = grouped_df.reset_index().reindex(columns=['agent_name_x', 'farmer_count', 'naursery', 'tp', 'total_area']).rename(columns={'agent_name_x':'agent_name','naursery':'sowing' })

    df = grouped_df
    data_dict = df.to_dict('r')
    # initializing excel
    writer = pd.ExcelWriter(
        str("static/media/") + "agent_wise_cultivation_report.xlsx", engine="xlsxwriter")
    # creating excel sheet with name

    df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:F1", "Agent Wise Cultivation Report", merge_format)

    # format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    # worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 7, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str("static/media/") + "agent_wise_cultivation_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            document["excel"] = encoded_image
    except Exception as err:
        print(err)
    document["data"] = data_dict
    return Response(data=document, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_agent_based_on_cluster(request):
    cluster_based_agent = {}
    agent_user_ids = list(
        UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True)
    )
    for cluster in UserClusterMap.objects.filter(user_id__in=agent_user_ids):
        if cluster.cluster.id not in cluster_based_agent:
            cluster_based_agent[cluster.cluster.id] = []

        cluster_based_agent[cluster.cluster.id].append(
            {
                "name": cluster.user.first_name,
                "id_y": cluster.user.id,
                "first_name": cluster.user.first_name,
                "last_name": cluster.user.last_name,
            }
        )
    print(cluster_based_agent)
    return Response(data=cluster_based_agent, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_data_for_yeild_vs_land_holding(request):
    season_id =request.data['season_id']
    document = {
        "have_data": False
    }
    print(season_id)
    # sowing dataframe
    sowing_df = pd.DataFrame(list(Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2).values()))
    print(sowing_df)

    if not sowing_df.empty:
        document['have_data'] = True
        # grouping with area and cound the farmer 
        df = sowing_df.groupby(["area"]).agg({"farmer_id": "count"}).reset_index()

        # total area in each acre size
        df['area_value'] = df['area'] * df['farmer_id']

        # harvest to take flower count
        harvest_list = list(Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).values_list('sowing__area', 'value'))
        harvest_col =['sowing_area', 'value']
        harvest_df = pd.DataFrame(harvest_list, columns=harvest_col)

        # group by area
        harvest_df = harvest_df.groupby(["sowing_area"]).agg({"value": "sum"}).reset_index()
        merge_df = pd.merge(df, harvest_df, left_on="area", right_on="sowing_area", how="left")

        # merging sowing with harvest to get link the flower qty
        merge_df = merge_df.drop(columns=['sowing_area'])

        # renaming
        merge_df = merge_df.rename(columns={"farmer_id": "No of farmers", "value": "Flower supplied", "area":"Land Holding", "area_value":"Total acre"})

        # converting to ton
        merge_df['Flower supplied'] = round(merge_df['Flower supplied'] / 1000,2)

        # calculating the yeild per acre
        merge_df['Yield / acre'] = merge_df['Flower supplied'] / merge_df['Total acre']

        # replacing all unknown with 0
        merge_df = merge_df.replace([np.inf, -np.inf], 0)
        merge_df = merge_df.fillna(0)
        merge_df['Yield / acre'] = round(merge_df['Yield / acre'], 2)

        # sorting
        df = merge_df.sort_values(by=['Land Holding'])
        
        # converting to dict
        data_dict = df.to_dict('r')
        # initializing excel
        writer = pd.ExcelWriter(str("static/media/") + "yeild_acre_vs_land_holding.xlsx", engine="xlsxwriter")
        # creating excel sheet with name

        df.index += 1
        total = df.sum(numeric_only=True)
        total.name = 'Total'
        df = df.append(total.transpose())
        df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:F1", "Yield / Acre VS Land Holding", merge_format)

        # format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        # worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 7, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "yeild_acre_vs_land_holding.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                document["excel"] = encoded_image
        except Exception as err:
            print(err)
        document["data"] = data_dict
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_ideal_sowing_period_impact(request):
    print(request.data)
    season_id = request.data['season_id']
    # initialize the dict
    data_dict = {"Month_data": {},
                "Grand_total": {}}
    data_dict["Grand_total"] = {"farmer_count": 0, "acre": 0, "quanity": 0, "avg": 0}

    # find active year and find the start date and end date
    active_season_date = Season.objects.get(id=season_id).year
    start_date = active_season_date.replace(month=active_season_date.month+2)
    end_date = active_season_date.replace(month=active_season_date.month+5, day=30)
    print("start_date : {}  end date : {}".format(start_date,end_date))

    # loop thru the weeks and fill the date
    # since there are 12 weeks for three months we consider it as 12 loops as 12 weeks
    week_number = 0
    start = active_season_date.replace(month=active_season_date.month+2)
    monthly_farmer_count = 0
    monthly_acre = 0
    monthly_quantity = 0
    monthly_average = 0

    grand_farmer_count = 0
    grand_acre = 0
    grand_quantity = 0
    grand_average = 0

    sowing_objs = Sowing.objects.filter(season_id=season_id)
    harvest_objs = Harvest.objects.filter(sowing__season_id=season_id)
    if request.data['filter_applied']:
        if len(request.data['cluster_ids'])!=0 and len(request.data['agent_ids'])==0:
            print('only cluster')
            farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=request.data['cluster_ids']).values_list('farmer_id'))
            sowing_objs = Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id)
            sowing_ids = list(Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list('id'))
            harvest_objs = Harvest.objects.filter(sowing_id__in=sowing_ids, sowing__season_id=season_id)
        if len(request.data['agent_ids'])!=0 and len(request.data['cluster_ids'])!=0:
            print('both cluster')
            farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=request.data['agent_ids'],  farmer__cluster_id__in=request.data['cluster_ids'], farmer__season_id=season_id).values_list('farmer__farmer_id'))
            sowing_objs = Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id)
            sowing_ids = list(Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list('id'))
            harvest_objs = Harvest.objects.filter(sowing_id__in=sowing_ids, sowing__season_id=season_id) 
        if len(request.data['cluster_ids'])==0 and len(request.data['agent_ids'])!=0:
            print('only agent')        
            farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=request.data['agent_ids'],farmer__season_id=season_id).values_list('farmer__farmer_id'))
            sowing_objs = Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id)
            sowing_ids = list(Sowing.objects.filter(farmer_id__in=farmer_ids, season_id=season_id).values_list('id'))
            harvest_objs = Harvest.objects.filter(sowing_id__in=sowing_ids, sowing__season_id=season_id) 

    for x in range(16):
        focus_month = start.strftime("%B")
        if focus_month not in data_dict["Month_data"]:
            print(focus_month)
            data_dict["Month_data"][focus_month] = {}
            data_dict["Month_data"][focus_month]['weeks'] = []
            data_dict["Month_data"][focus_month]['total'] = {}
        week_number = week_number + 1
        if week_number == 5:
            monthly_farmer_count = 0
            monthly_acre = 0
            monthly_quantity = 0
            monthly_average = 0
            week_number = 1
        #   focus_month = focus_month +1
        if week_number == 4:
            year = active_season_date.year
            month = start.month
            last_date_of_month = calendar.monthrange(year, month)[1]
            end = start.replace(day=last_date_of_month)
        else:
            end = start + datetime.timedelta(days=6)
        farmer_count = len(set(list(sowing_objs.filter(cultivation_phase_id=2, season_id=season_id, sowing_date__gte=start, sowing_date__lte=end).values_list('farmer_id'))))
        if harvest_objs.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id, sowing__sowing_date__gte=start, sowing__sowing_date__lte=end).exists():
            harvest_total = round(harvest_objs.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id, sowing__sowing_date__gte=start, sowing__sowing_date__lte=end).aggregate(Sum('value'))['value__sum']/1000,2)
            
        else:
            harvest_total = 0
        if sowing_objs.filter(cultivation_phase_id=2, season_id=season_id, sowing_date__gte=start, sowing_date__lte=end).exists():
            acre = sowing_objs.filter(cultivation_phase_id=2, season_id=season_id, sowing_date__gte=start, sowing_date__lte=end).aggregate(Sum('area'))['area__sum']
        else:
            acre = 0
            
        if harvest_total != 0 and acre != 0:
            avg = round(harvest_total / acre, 2)
        else:
            avg = 0
        temp_dict = {
                    "week_number": week_number,
                    "farmer_count": farmer_count,
                    "acre": acre,
                    "quanity": harvest_total,
                    "avg": avg,
        }
        monthly_farmer_count = monthly_farmer_count + farmer_count
        monthly_acre = monthly_acre +acre
        monthly_quantity = monthly_quantity +harvest_total
        monthly_average = monthly_average + avg

        data_dict["Month_data"][focus_month]['total'] = {  
                    "farmer_count": monthly_farmer_count,
                    "acre": monthly_acre,
                    "quanity": round(monthly_quantity, 2),}
        if monthly_acre != 0:
            data_dict["Month_data"][focus_month]['total']["avg"] = round(round(monthly_quantity, 2) /monthly_acre,2)
        else:
            data_dict["Month_data"][focus_month]['total']["avg"] = 0
        data_dict["Month_data"][focus_month]['weeks'].append(temp_dict)
        data_dict["Grand_total"]["farmer_count"] = round(data_dict["Grand_total"]["farmer_count"] + farmer_count, 2)
        data_dict["Grand_total"]["acre"]= round(data_dict["Grand_total"]["acre"] + acre, 2)
        data_dict["Grand_total"]["quanity"] = round(data_dict["Grand_total"]["quanity"] + harvest_total,2 )
        if data_dict["Grand_total"]["acre"] != 0: 
            data_dict["Grand_total"]["avg"] = round(data_dict["Grand_total"]["quanity"] / data_dict["Grand_total"]["acre"],2)
        else:
            data_dict["Grand_total"]["avg"] = 0
        start = end + datetime.timedelta(days=1)
    data_dict['headings'] = ['week_number','farmer_count','acre','quanity','avg']
    data_dict['top_headers'] = ['farmer_count','acre','quanity','avg']
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_mobile_number_exists_on_farmer_register(request):
    data = {}
    season_id = get_active_season_id()
    print(request.data)
    if FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer__mobile=request.data["mobile_number"]).exists():
        print('mobile exists')
        data["message"] = "This Farmer already Registered in this season"
        data["available"] = True
        data["farmer_code"] = Farmer.objects.filter(mobile=request.data["mobile_number"])[0].code
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    if request.data["aadhar_number"] != None:
        if FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer__aadhaar_number=request.data["aadhar_number"]).exists():
            print('aadhar exists')
            data["message"] = "This Farmer already Registered in this season"
            data["available"] = True
            data["farmer_code"] = Farmer.objects.filter(aadhaar_number=request.data["aadhar_number"])[0].code
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    print('not found')
    data["available"] = False
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_water_resource_based_farmer_report(request):
    data = {}
    print(request.data)
    season_id = request.data['season_id']
    cluster_id = request.data['cluster_id']
    farmer_cluster_seaon_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_id)
    farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_id).values_list('farmer_id', flat=True))
    farmer_cluster_seaon_values = list(farmer_cluster_seaon_obj.values_list('farmer_id', 'cluster__name', 'seasonal_farmer_code'))
    farmer_cluster_seaon_columns = ["farmer_id", 'cluster_name', 'farmer__code']
    farmer_cluster_df = pd.DataFrame(farmer_cluster_seaon_values, columns=farmer_cluster_seaon_columns)
    
    sowing_objs = Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2, water_source_id=request.data['water_resource_id'], farmer_id__in=farmer_ids)
    sowing_values = list(sowing_objs.values_list('farmer_id','farmer__first_name','farmer__last_name', 'area', 'water_source__name'))
    sowing_columns = ['farmer_id','farmer__first_name','farmer__last_name','area', 'water_source']
    sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)
    
    agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__farmer_id__in =farmer_ids, farmer__season_id=season_id)
    agent_farmer_values = list(agent_farmer_obj.values_list( 'agent__first_name','agent__last_name', 'farmer__farmer_id'))
    agent_farmer_columns = ['agent__first_name','agent__last_name', 'farmer_id']
    agent_df = pd.DataFrame(agent_farmer_values, columns=agent_farmer_columns)

    sowing_agent_df = pd.merge(sowing_df, agent_df, how='left', left_on='farmer_id', right_on='farmer_id')
    final_df = pd.merge(sowing_agent_df, farmer_cluster_df, how="left", left_on='farmer_id', right_on='farmer_id')

    final_df = final_df.rename(columns={'farmer_id' : "Farmer Id" , 'farmer__first_name' : "Farmer First Name" , 'farmer__last_name' : "Farmer Last Name" , 'farmer__code' : "Farmer Code" ,
       'area' : "Area" , 'water_source' : "Water Source" , 'agent__first_name' : "Agent First Name" , 'agent__last_name' : "Agent Last Name" , 'cluster_name' : "Cluster Name"})
    final_df = final_df.drop(columns=['Farmer Id'])
    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())

    writer = pd.ExcelWriter(str("static/media/") + "water_source_farmer_report.xlsx", engine="xlsxwriter")

    # creating excel sheet with name
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)
    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )
    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:J1", "Water source based farmer report ", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 9, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "water_source_farmer_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_based_on_cluster_ids(request):
    season_id=get_active_season_id()
    user_list = list(UserClusterMap.objects.filter(cluster_id__in=request.data["cluster_ids"], season_id=season_id).values_list("user", flat=True))
    user_profile_obj = UserProfile.objects.filter(user_id__in=user_list, user_type_id=6)
    user_profile_list = list(user_profile_obj.values_list("user", "user__first_name"))
    user_profile_column = ["id", "name"]
    user_df = pd.DataFrame(user_profile_list, columns=user_profile_column)
    return Response(data=user_df.to_dict("r"), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_input_combo_list(request):
    input_combo_ids = list(InputPart.objects.filter().values_list('input_combo_id',flat=True))
    input_combo_obj = InputCombo.objects.filter(id__in=input_combo_ids).order_by('display_ordinal')
    input_combo_list = list(input_combo_obj.values_list('id', 'name', 'area__quantity_in_acre'))
    input_combo_column = ['id', 'name', 'quantity_in_acre']
    input_combo_df = pd.DataFrame(input_combo_list, columns=input_combo_column)
    return Response(data=input_combo_df.to_dict('r'), status=status.HTTP_200_OK)


def generate_request_code(input_combo_id):
    code_bank_obj = ComboIssueRequestCodeBank.objects.filter(input_combo_id=input_combo_id)[0]
    last_digit_code = code_bank_obj.last_digit
    new_code = last_digit_code + 1
    value = str(code_bank_obj.input_combo.name) + str(new_code).zfill(3)
    code_bank_obj.last_digit = new_code
    code_bank_obj.save()
    return value


@api_view(['POST'])
@transaction.atomic
def register_combo_issue_request(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        input_combo_obj = InputCombo.objects.get(id=request.data['input_combo_id'])
        combo_request_obj = ComboIssueRequest(request_code=generate_request_code(request.data['input_combo_id']),
                                            season_id=get_active_season_id(),
                                            input_combo_id=request.data['input_combo_id'],
                                            quantity_in_numbers=0,
                                            quantity_for_area=0,
                                            expected_date=request.data['date_of_expected'],
                                            issue_rised_date=datetime.datetime.now(),
                                            max_status_id=2,
                                            max_status_date=datetime.datetime.now(),
                                            supervisor_id=request.user.id)
        combo_request_obj.save()
        total_qty = 0
        for agent in request.data['agents_list']:
            if agent['status']:
                combo_issue_register_agent_obj = ComboIssueRegisterAgentMap.objects.get(supervisor_id=request.user.id, input_combo_id=request.data['input_combo_id'],  agent_id=agent['agent_user_id'])
                if agent['qty'] > combo_issue_register_agent_obj.quantity_in_numbers:
                    combo_issue_register_agent_obj.quantity_in_numbers = 0
                else:
                    registered_qty = combo_issue_register_agent_obj.quantity_in_numbers  - agent['qty']
                    combo_issue_register_agent_obj.quantity_in_numbers =  registered_qty
                combo_issue_register_agent_obj.save()
                total_qty += agent['qty']
                combo_request_agent_obj = ComboIssueRequestAgentMap(combo_issue_request_id=combo_request_obj.id,
                                                                    agent_id=agent['agent_user_id'], 
                                                                    issue_rised_date=datetime.datetime.now(),
                                                                    quantity_in_numbers=agent['qty'],
                                                                    max_status_id=2)
                
                combo_request_agent_obj.save()
        print(total_qty)
        total_acre = total_qty * input_combo_obj.area.quantity_in_acre
        combo_request_obj.quantity_in_numbers = total_qty
        combo_request_obj.quantity_for_area = total_acre
        combo_request_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def serve_combo_issue_request_list_for_sernior_supervisor(request):
    print(request.user.id)
    season_id = get_active_season_id()
    if UserProfile.objects.get(user_id=request.user.id).user_type_id==3:
        subordinates = UserHierarchyMap.objects.filter(superior_id=request.user.id, season_id=season_id)
        subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
        combo_issue_request_obj = ComboIssueRequest.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).order_by('issue_rised_date')
    else:
        combo_issue_request_obj = ComboIssueRequest.objects.filter(season_id=season_id).order_by('issue_rised_date')
    combo_issue_request_list = list(combo_issue_request_obj.values_list('id', 'supervisor__username', 'issue_rised_date', 'input_combo__name', 'quantity_for_area', 'expected_date', 'quantity_in_numbers', 'max_status',  'senior_supervisor__username', 'senior_supervisor_status', 'senior_supervisor_status__name', 'senior_supervisor_status_date', 'assitant_manager__username', 'assitant_manager_status', 'assitant_manager_status__name', 'assitant_manager_status_date', 'agri_officer__username', 'agri_officer_status', 'agri_officer_status__name', 'agri_officer_status_date', 'gm__username', 'gm_status_date', 'gm_status__name', 'dispatched_by__username', 'dispatch_status__name', 'dispatch_date', 'time_created'))
    combo_issue_request_column = ['id', 'supervisor_name', 'issue_raised_date', 'input_combo_name', 'area_qty', 'date_of_expected', 'total_qty', 'max_status_id', 'senior_supervisor_name', 'senior_supervisor_status_id', 'senior_supervisor_status_name','senior_supervisor_date', 'assitant_manager_name', 'assitant_manager_status_id', 'assitant_manager_status_name','assitant_manager_date', 'agri_officer_name', 'agri_officer_status_id', 'agri_officer_status_name','agri_officer_date', 'gm_name', 'gm_status_date','gm_status_name', 'dispatched_by_username', 'dispatch_status_name', 'dispatch_date', 'time_created']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_list, columns=combo_issue_request_column)

    # combo_issue_request_df = combo_issue_request_df.fillna('0')
    combo_issue_request_df['senior_supervisor_date'] = pd.to_datetime(combo_issue_request_df['senior_supervisor_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['assitant_manager_date'] = pd.to_datetime(combo_issue_request_df['assitant_manager_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['agri_officer_date'] = pd.to_datetime(combo_issue_request_df['agri_officer_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['gm_status_date'] = pd.to_datetime(combo_issue_request_df['gm_status_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['dispatch_date'] = pd.to_datetime(combo_issue_request_df['dispatch_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')

    combo_issue_request_df = combo_issue_request_df.fillna(0)


    combo_issue_request_df['senior_supervisor_status_text'] = combo_issue_request_df['senior_supervisor_name'].astype(str) +' '+ combo_issue_request_df['senior_supervisor_status_name'].astype(str) + ' on ' + combo_issue_request_df['senior_supervisor_date'].astype(str)
    combo_issue_request_df['assitant_manager_status_text'] = combo_issue_request_df['assitant_manager_name'].astype(str) +' '+ combo_issue_request_df['assitant_manager_status_name'].astype(str) + ' on ' + combo_issue_request_df['assitant_manager_date'].astype(str)
    combo_issue_request_df['agri_officer_status_text'] = combo_issue_request_df['agri_officer_name'].astype(str) +' '+ combo_issue_request_df['agri_officer_status_name'].astype(str) + ' on ' + combo_issue_request_df['agri_officer_date'].astype(str)
    combo_issue_request_df['gm_status_text'] = combo_issue_request_df['gm_name'].astype(str) +' '+ combo_issue_request_df['gm_status_name'].astype(str) + ' on ' + combo_issue_request_df['gm_status_date'].astype(str)
    combo_issue_request_df['dispatch_status_text'] = combo_issue_request_df['dispatched_by_username'].astype(str) +' '+ combo_issue_request_df['dispatch_status_name'].astype(str) + ' on ' + combo_issue_request_df['dispatch_date'].astype(str)


    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(max_status_id=2, combo_issue_request__season_id=season_id)
    combo_issue_request_agent_list = list(combo_issue_request_agent_obj.values_list('id', 'combo_issue_request_id', 'agent', 'agent__userclustermap__cluster__name'))
    combo_issue_request_agent_column = ['agent_map_id', 'combo_issue_request_id', 'agent_user_id', 'cluster_name']
    combo_issue_request_agent_df = pd.DataFrame(combo_issue_request_agent_list, columns=combo_issue_request_agent_column)

    grouped_df = combo_issue_request_agent_df.groupby(['combo_issue_request_id']).agg({'agent_user_id': 'count', 'cluster_name': 'min'}).reset_index()
    final_df = combo_issue_request_df.merge(grouped_df, how='left', left_on='id', right_on='combo_issue_request_id')
    final_df = final_df.rename(columns={'agent_user_id': 'agent_count'})
    final_df = final_df.fillna(0)
    final_df = final_df.sort_values(by=['time_created'])
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_combo_issue_request_list_for_supervisor(request):
    season_id = get_active_season_id()
    combo_issue_request_obj = ComboIssueRequest.objects.filter(supervisor_id=request.user.id, season_id=season_id).order_by('issue_rised_date')
    combo_issue_request_list = list(combo_issue_request_obj.values_list('id', 'supervisor__username', 'issue_rised_date', 'input_combo__name', 'quantity_for_area', 'expected_date', 'quantity_in_numbers', 'max_status',  'senior_supervisor__username', 'senior_supervisor_status', 'senior_supervisor_status__name', 'senior_supervisor_status_date', 'assitant_manager__username', 'assitant_manager_status', 'assitant_manager_status__name', 'assitant_manager_status_date', 'agri_officer__username', 'agri_officer_status', 'agri_officer_status__name', 'agri_officer_status_date', 'gm__username', 'gm_status_date', 'gm_status__name', 'dispatched_by__username', 'dispatch_status__name', 'dispatch_date'))
    combo_issue_request_column = ['id', 'supervisor_name', 'issue_raised_date', 'input_combo_name', 'area_qty', 'date_of_expected', 'total_qty', 'max_status_id', 'senior_supervisor_name', 'senior_supervisor_status_id', 'senior_supervisor_status_name','senior_supervisor_date', 'assitant_manager_name', 'assitant_manager_status_id', 'assitant_manager_status_name','assitant_manager_date', 'agri_officer_name', 'agri_officer_status_id', 'agri_officer_status_name','agri_officer_date', 'gm_name', 'gm_status_date','gm_status_name', 'dispatched_by_username', 'dispatch_status_name', 'dispatch_date']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_list, columns=combo_issue_request_column)
    # combo_issue_request_df = combo_issue_request_df.fillna('0')
    combo_issue_request_df['senior_supervisor_date'] = pd.to_datetime(combo_issue_request_df['senior_supervisor_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['assitant_manager_date'] = pd.to_datetime(combo_issue_request_df['assitant_manager_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['agri_officer_date'] = pd.to_datetime(combo_issue_request_df['agri_officer_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['gm_status_date'] = pd.to_datetime(combo_issue_request_df['gm_status_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['dispatch_date'] = pd.to_datetime(combo_issue_request_df['dispatch_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')

    combo_issue_request_df = combo_issue_request_df.fillna(0)


    combo_issue_request_df['senior_supervisor_status_text'] = combo_issue_request_df['senior_supervisor_name'].astype(str) +' '+ combo_issue_request_df['senior_supervisor_status_name'].astype(str) + ' on ' + combo_issue_request_df['senior_supervisor_date'].astype(str)
    combo_issue_request_df['assitant_manager_status_text'] = combo_issue_request_df['assitant_manager_name'].astype(str) +' '+ combo_issue_request_df['assitant_manager_status_name'].astype(str) + ' on ' + combo_issue_request_df['assitant_manager_date'].astype(str)
    combo_issue_request_df['agri_officer_status_text'] = combo_issue_request_df['agri_officer_name'].astype(str) +' '+ combo_issue_request_df['agri_officer_status_name'].astype(str) + ' on ' + combo_issue_request_df['agri_officer_date'].astype(str)
    combo_issue_request_df['gm_status_text'] = combo_issue_request_df['gm_name'].astype(str) +' '+ combo_issue_request_df['gm_status_name'].astype(str) + ' on ' + combo_issue_request_df['gm_status_date'].astype(str)
    combo_issue_request_df['dispatch_status_text'] = combo_issue_request_df['dispatched_by_username'].astype(str) +' '+ combo_issue_request_df['dispatch_status_name'].astype(str) + ' on ' + combo_issue_request_df['dispatch_date'].astype(str)
    


    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(max_status_id=2, combo_issue_request__season_id=season_id)
    combo_issue_request_agent_list = list(combo_issue_request_agent_obj.values_list('id', 'combo_issue_request_id', 'agent', 'agent__userclustermap__cluster__name'))
    combo_issue_request_agent_column = ['agent_map_id', 'combo_issue_request_id', 'agent_user_id', 'cluster_name']
    combo_issue_request_agent_df = pd.DataFrame(combo_issue_request_agent_list, columns=combo_issue_request_agent_column)
    grouped_df = combo_issue_request_agent_df.groupby(['combo_issue_request_id']).agg({'agent_user_id': 'count', 'cluster_name': 'min'}).reset_index()
    # combo_issue_request_agent_df.groupby('combo_issue_request_id')['cluster_name'].apply(set).to_frame().reset_index()
    final_df = combo_issue_request_df.merge(grouped_df, how='left', left_on='id', right_on='combo_issue_request_id')
    final_df = final_df.rename(columns={'agent_user_id': 'agent_count'})
    final_df = final_df.fillna(0)
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
def approve_or_decline_combo_issure(request):
    print(request.data)
    combo_issue_request_obj = ComboIssueRequest.objects.get(id=request.data['id'])
    user_type_id = UserProfile.objects.get(user_id=request.user.id).user_type_id
    username = ''
    if request.data['status'] == 1:
        status_name = 'Approved'
    else:
        status_name = 'Declined'

    if user_type_id == 3:
        if request.data['max_status_id'] == 2:
            if request.data['status'] == 1:
                combo_issue_request_obj.max_status_id = 3
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
                 
            else:
                combo_issue_request_obj.max_status_id = 7
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
            combo_issue_request_obj.senior_supervisor_id = request.user.id
            combo_issue_request_obj.senior_supervisor_status_id = request.data['status']
            combo_issue_request_obj.senior_supervisor_status_date = datetime.datetime.now()
            title = "New Request for approval : " + str(combo_issue_request_obj.request_code)
            body = request.user.username + ' have ' + status_name + ' the request - ' + str(combo_issue_request_obj.request_code)
            user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=2).values_list('user_id',flat=True))
            send_notification(title,body,user_ids)
            combo_issue_request_obj.save()
    elif user_type_id == 2:
        if request.data['max_status_id'] == 3:
            if request.data['status'] == 1:
                combo_issue_request_obj.max_status_id = 4
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
            else:
                combo_issue_request_obj.max_status_id = 7
                combo_issue_request_obj.max_status_date = datetime.datetime.now()

            combo_issue_request_obj.assitant_manager_id = request.user.id
            combo_issue_request_obj.assitant_manager_status_id = request.data['status']
            combo_issue_request_obj.assitant_manager_status_date = datetime.datetime.now()
            combo_issue_request_obj.save()
           
    elif user_type_id == 4:
        if request.data['max_status_id'] == 4:
            if request.data['status'] == 1:
                combo_issue_request_obj.max_status_id = 5
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
            else:
                combo_issue_request_obj.max_status_id = 7
                combo_issue_request_obj.max_status_date = datetime.datetime.now()

            combo_issue_request_obj.agri_officer_id = request.user.id
            combo_issue_request_obj.agri_officer_status_id = request.data['status']
            combo_issue_request_obj.agri_officer_status_date = datetime.datetime.now()
            combo_issue_request_obj.save()
            title = "New Request for approval : " + str(combo_issue_request_obj.request_code)
            body = request.user.username + ' have ' + status_name + ' the request - ' + str(combo_issue_request_obj.request_code)
            user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=1).values_list('user_id',flat=True))
            send_notification(title,body,user_ids)
    elif user_type_id == 1:  
        if request.data['max_status_id'] == 5:
            if request.data['status'] == 1:
                combo_issue_request_obj.max_status_id = 6
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
            else:
                combo_issue_request_obj.max_status_id = 7
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
            combo_issue_request_obj.gm_id = request.user.id
            combo_issue_request_obj.gm_status_id = request.data['status']
            combo_issue_request_obj.gm_status_date = datetime.datetime.now()
            combo_issue_request_obj.save()
    
    print(request.user.username + ' have ' + status_name + ' the request - ' + str(combo_issue_request_obj.request_code))
    title = "Request Status for " + str(combo_issue_request_obj.request_code)
    body = request.user.username + ' have ' + status_name + ' the request - ' + str(combo_issue_request_obj.request_code)
    user_ids = [combo_issue_request_obj.supervisor.id]
    send_notification(title,body,user_ids)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_combo_issue_request_input_combo_wise(request):
    combo_issue_request_obj = ComboIssueRequest.objects.filter(quantity_in_numbers__gt=0, season_id=get_active_season_id()).exclude(max_status_id__in=[7,8,9]).order_by('issue_rised_date')
    combo_issue_request_list = list(combo_issue_request_obj.values_list('id', 'supervisor__username', 'issue_rised_date', 'input_combo_id','input_combo__name',
     'quantity_for_area', 'expected_date', 'quantity_in_numbers', 'max_status',  'senior_supervisor__username', 'senior_supervisor_status', 'senior_supervisor_status__name',
      'senior_supervisor_status_date', 'assitant_manager__username', 'assitant_manager_status', 'assitant_manager_status__name', 'assitant_manager_status_date', 
      'agri_officer__username', 'agri_officer_status', 'agri_officer_status__name', 'agri_officer_status_date', 'gm__username', 'gm_status_date', 'gm_status__name', 
      'dispatched_by__username', 'dispatch_status__name', 'dispatch_date', 'request_code'))
    combo_issue_request_column = ['id', 'supervisor_name', 'issue_raised_date', 'input_combo_id','input_combo_name', 'area_qty', 'date_of_expected', 'total_qty',
     'max_status_id', 'senior_supervisor_name', 'senior_supervisor_status_id', 'senior_supervisor_status_name','senior_supervisor_date', 'assitant_manager_name',
      'assitant_manager_status_id', 'assitant_manager_status_name','assitant_manager_date', 'agri_officer_name', 'agri_officer_status_id', 'agri_officer_status_name',
      'agri_officer_date', 'gm_name', 'gm_status_date','gm_status_name', 'dispatched_by_username', 'dispatch_status_name', 'dispatch_date', 'request_code']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_list, columns=combo_issue_request_column)

    # combo_issue_request_df = combo_issue_request_df.fillna('0')
    combo_issue_request_df['senior_supervisor_date'] = pd.to_datetime(combo_issue_request_df['senior_supervisor_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['assitant_manager_date'] = pd.to_datetime(combo_issue_request_df['assitant_manager_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['agri_officer_date'] = pd.to_datetime(combo_issue_request_df['agri_officer_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['gm_status_date'] = pd.to_datetime(combo_issue_request_df['gm_status_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['dispatch_date'] = pd.to_datetime(combo_issue_request_df['dispatch_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    
    combo_issue_request_df = combo_issue_request_df.fillna(0)
    
    combo_issue_request_df['senior_supervisor_status_text'] = combo_issue_request_df['senior_supervisor_name'].astype(str) +' '+ combo_issue_request_df['senior_supervisor_status_name'].astype(str) + ' on ' + combo_issue_request_df['senior_supervisor_date'].astype(str)
    combo_issue_request_df['assitant_manager_status_text'] = combo_issue_request_df['assitant_manager_name'].astype(str) +' '+ combo_issue_request_df['assitant_manager_status_name'].astype(str) + ' on ' + combo_issue_request_df['assitant_manager_date'].astype(str)
    combo_issue_request_df['agri_officer_status_text'] = combo_issue_request_df['agri_officer_name'].astype(str) +' '+ combo_issue_request_df['agri_officer_status_name'].astype(str) + ' on ' + combo_issue_request_df['agri_officer_date'].astype(str)
    combo_issue_request_df['gm_status_text'] = combo_issue_request_df['gm_name'].astype(str) +' '+ combo_issue_request_df['gm_status_name'].astype(str) + ' on ' + combo_issue_request_df['gm_status_date'].astype(str)
    combo_issue_request_df['dispatch_status_text'] = combo_issue_request_df['dispatched_by_username'].astype(str) +' '+ combo_issue_request_df['dispatch_status_name'].astype(str) + ' on ' + combo_issue_request_df['dispatch_date'].astype(str)

    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(max_status_id=2, combo_issue_request__season_id=get_active_season_id())
    combo_issue_request_agent_list = list(combo_issue_request_agent_obj.values_list('id', 'combo_issue_request_id', 'agent', 'agent__userclustermap__cluster__name'))
    combo_issue_request_agent_column = ['agent_map_id', 'combo_issue_request_id', 'agent_user_id', 'cluster_name']
    combo_issue_request_agent_df = pd.DataFrame(combo_issue_request_agent_list, columns=combo_issue_request_agent_column)

    grouped_df = combo_issue_request_agent_df.groupby(['combo_issue_request_id']).agg({'agent_user_id': 'count', 'cluster_name': 'min'}).reset_index()

    # combo_issue_request_agent_df.groupby('combo_issue_request_id')['cluster_name'].apply(set).to_frame().reset_index()
    final_df = combo_issue_request_df.merge(grouped_df, how='left', left_on='id', right_on='combo_issue_request_id')
    final_df = final_df.rename(columns={'agent_user_id': 'agent_count'})
    final_df = final_df.fillna(0)
    final_dict = final_df.groupby('input_combo_id').apply(lambda x: x.to_dict('r')).to_dict()
    
    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_store_inventory_under_input_combo(request):
    print(request.data)
    input_combo_id = request.data['input_combo_id']
    input_store_obj = InputStoreInventory.objects.filter(input_packet_inventory__input_combo_id=input_combo_id).exclude(quantity_now=0)
    input_store_list = list(input_store_obj.values_list('id', 'storage__name', 'quantity_now'))
    input_store_column = ['id', 'storage_name', 'available_qty']
    input_store_df = pd.DataFrame(input_store_list, columns=input_store_column)

    return Response(data=input_store_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_sub_store_inventory_under_input_combo(request):
    print(request.data)
    input_combo_id = request.data['input_combo_id']
    input_sub_store_obj = InputSubStoreInventory.objects.filter(input_store_inventory__input_packet_inventory__input_combo_id=input_combo_id).exclude(quantity_now=0).order_by('id')
    input_sub_store_list = list(input_sub_store_obj.values_list('id', 'sub_storage__name', 'quantity_now', 'section', 'sub_section', 'label_range_start', 'label_range_end', 'input_store_inventory__input_packet_inventory__packet_code'))
    input_sub_store_column = ['id', 'storage_name', 'available_qty', 'section', 'sub_section', 'label_range_start', 'label_range_end', 'lot_name']
    input_sub_store_df = pd.DataFrame(input_sub_store_list, columns=input_sub_store_column)

    sub_store_ids = list(input_sub_store_obj.values_list('id', flat=True))
    sub_store_packet_label_obj = InputSubStoreInventoryPacketLabel.objects.filter(input_sub_store_inventory_id__in=sub_store_ids, stock_status_id=3)
    sub_store_packet_label_list = list(sub_store_packet_label_obj.values_list('input_sub_store_inventory_id', 'label'))
    sub_store_packet_label_column = ['input_sub_store_inventory_id', 'return_label']
    sub_store_packet_label_df = pd.DataFrame(sub_store_packet_label_list, columns=sub_store_packet_label_column)
    sub_store_packet_label_list = sub_store_packet_label_df.groupby('input_sub_store_inventory_id')['return_label'].apply(list)
    input_sub_store_df = input_sub_store_df.merge(sub_store_packet_label_list, how='left', left_on='id', right_on='input_sub_store_inventory_id').fillna(0)

    return Response(data=input_sub_store_df.to_dict('r'), status=status.HTTP_200_OK)

def get_active_season_id():
    season_obj = Season.objects.get(is_active=True)
    return season_obj.id

@api_view(['POST'])
@transaction.atomic
def register_agent_inventory(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        storage_list = request.data['storage_list']
        for storage in storage_list:
            if storage['entered_qty'] != '':
                store_quantity = int(storage['entered_qty'])
                storage_obj = InputSubStoreInventory.objects.get(id=storage['id'])
                available_qty = storage_obj.quantity_now
                storage_obj.quantity_now = available_qty - int(storage['entered_qty'])
                storage_obj.quantity_now_time = datetime.datetime.now()

                storage_obj.save()
                combo_issue_request_obj = ComboIssueRequest.objects.get(id=request.data['combo_issue_request_id'])
                agents = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['combo_issue_request_id'])
                for agent_combo in agents:
                    if store_quantity == 0:
                        break
                    if SubStoreIssueLabelAgentMap.objects.filter(agent_id=agent_combo.agent.id, combo_issue_request_agent_map_id=agent_combo.id).exists():
                        label_qty = SubStoreIssueLabelAgentMap.objects.filter(agent_id=agent_combo.agent.id, combo_issue_request_agent_map_id=agent_combo.id).count()
                    else:
                        label_qty = 0
                    if agent_combo.quantity_in_numbers == label_qty:
                        print('more')
                    else:
                        print('agent_combo.quantity_in_numbers :', agent_combo.quantity_in_numbers)
                        print('label_qty :', label_qty)
                        required_qty = agent_combo.quantity_in_numbers - label_qty
                        print('required_qty 1 :', required_qty)
                        if required_qty > store_quantity:
                            required_qty = store_quantity
                        if not AgentInventory.objects.filter(combo_issue_request_id=request.data['combo_issue_request_id'], agent_id=agent_combo.agent.id).exists():
                            agent_inventory_obj = AgentInventory(
                                season_id=get_active_season_id(),
                                combo_issue_request_id=request.data['combo_issue_request_id'],
                                agent_id=agent_combo.agent.id,
                                date_of_receipt=datetime.datetime.now(),
                                quantity_at_receipt=agent_combo.quantity_in_numbers,
                                quantity_now=agent_combo.quantity_in_numbers,
                                quantity_now_time=datetime.datetime.now(),
                                unit_id=4,
                                price_per_item=10,
                                created_by_id=request.user.id,
                                modified_by_id=request.user.id,
                            )
                            agent_inventory_obj.save()
                            agent_distribution_trasaction_log(agent_inventory_obj.id, request.user.id)
                        else:
                            agent_inventory_obj = AgentInventory.objects.get(combo_issue_request_id=request.data['combo_issue_request_id'], agent_id=agent_combo.agent.id)
                        label_from = InputSubStoreInventoryPacketLabel.objects.filter(input_sub_store_inventory_id=storage_obj.id, stock_status_id__in=[1,3]).order_by('id')[0].label
                        if not AgentInventoryStoreLabelRangeMap.objects.filter(agent_inventory_id=agent_inventory_obj.id, input_sub_store_inventory_id=storage_obj.id).exists():
                            agent_inventory_store_lable_map_obj = AgentInventoryStoreLabelRangeMap(agent_inventory_id=agent_inventory_obj.id,
                                                                                                input_sub_store_inventory_id=storage_obj.id,
                                                                                                label_range_from=label_from)
                            agent_inventory_store_lable_map_obj.save()
                        else:
                            agent_inventory_store_lable_map_obj = AgentInventoryStoreLabelRangeMap.objects.get(agent_inventory_id=agent_inventory_obj.id, input_sub_store_inventory_id=storage_obj.id)
                        print('required_qty :', required_qty)
                        for i in range(1, required_qty+1):
                            agent_invent_label_obj = InputSubStoreInventoryPacketLabel.objects.filter(input_sub_store_inventory_id=storage_obj.id, stock_status_id__in=[1,3]).order_by('id')[0]
                            agent_invent_label_obj.stock_status_id=2
                            agent_invent_label_obj.save()
                            new_table_obj = SubStoreIssueLabelAgentMap(input_sub_store_inventory_id=storage_obj.id,
                                                                    agent_id=agent_combo.agent.id,
                                                                    combo_issue_request_agent_map_id=agent_combo.id,
                                                                    agent_inventory_id=agent_inventory_obj.id,
                                                                    label=agent_invent_label_obj.label,
                                                                    status_id=1,
                                                                    created_by_id=request.user.id,
                                                                    modified_by_id=request.user.id)
                            new_table_obj.save()
                            label_to = agent_invent_label_obj.label
                        agent_inventory_store_lable_map_obj.label_range_to = label_to
                        agent_inventory_store_lable_map_obj.save()
                        store_quantity -= required_qty
                
                if storage_obj.quantity_now == 0:
                    storage_obj.label_range_start = '0'
                    storage_obj.label_range_end = '0'
                else:
                    label_from = InputSubStoreInventoryPacketLabel.objects.filter(input_sub_store_inventory_id=storage_obj.id, stock_status_id=1).order_by('id')[0].label
                    storage_obj.label_range_start = label_from
                storage_obj.save()
                combo_issue_request_obj.max_status_id = 8
                combo_issue_request_obj.max_status_date = datetime.datetime.now()
                combo_issue_request_obj.dispatched_by_id = request.user.id
                combo_issue_request_obj.dispatch_status_id = 3
                combo_issue_request_obj.dispatch_date = request.data['dispatch_date']
                combo_issue_request_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def serve_agent_under_supervisor_for_issue_register(request):
    subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=get_active_season_id()).values_list('agent_id', flat=True))
    user_profile_obj = UserProfile.objects.filter(user_type_id=6, user_id__in=subordinate_user_ids)
    user_profile_list = list(user_profile_obj.values_list('user', 'user__first_name'))
    user_profile_column = ['agent_user_id', 'name']
    user_profile_df = pd.DataFrame(user_profile_list, columns=user_profile_column)
    combo_issue_register_agent_obj = ComboIssueRegisterAgentMap.objects.filter(supervisor_id=request.user.id, input_combo_id=request.data['input_combo_id'])
    combo_issue_register_agent_list = list(combo_issue_register_agent_obj.values_list('agent', 'quantity_in_numbers'))
    combo_issue_register_agent_column = ['id', 'qty']
    combo_issue_register_agent_df = pd.DataFrame(combo_issue_register_agent_list, columns=combo_issue_register_agent_column)
    merge_df = user_profile_df.merge(combo_issue_register_agent_df, how='left', left_on='agent_user_id', right_on='id')
    merge_df = merge_df.fillna(0)
    merge_df['status'] = False
    return Response(data=merge_df.to_dict('r'), status=status.HTTP_200_OK)



@api_view(['POST'])
def issue_register_for_supervisor_request(request):
    if not ComboIssueRegisterAgentMap.objects.filter(supervisor_id=request.user.id, input_combo_id=request.data['input_combo_id'],  agent_id=request.data['agent_user_id']).exists():

        combo_issue_register_agent_obj = ComboIssueRegisterAgentMap(supervisor_id=request.user.id,
                                                                    input_combo_id=request.data['input_combo_id'],
                                                                    quantity_in_numbers=request.data['qty'],
                                                                    agent_id=request.data['agent_user_id'])
        combo_issue_register_agent_obj.save()
    else:
        combo_issue_register_agent_obj = ComboIssueRegisterAgentMap.objects.get(supervisor_id=request.user.id, input_combo_id=request.data['input_combo_id'],  agent_id=request.data['agent_user_id'])
        combo_issue_register_agent_obj.quantity_in_numbers = request.data['qty']
        combo_issue_register_agent_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_sub_storage(request):
    sub_store_obj = SubStorage.objects.all()
    sub_store_list = list(sub_store_obj.values_list('id', 'name'))
    sub_store_column = ['id', 'name']
    sub_store_df = pd.DataFrame(sub_store_list, columns=sub_store_column)
    return Response(data=sub_store_df.to_dict('r'), status=status.HTTP_200_OK)


def generate_request_code_for_sub_store():
    code_bank_obj = SubStoreRequestCodeBank.objects.filter()[0]
    last_digit_code = code_bank_obj.last_digit
    new_code = last_digit_code + 1
    value = str(code_bank_obj.code_prefix) + '_' +str(datetime.datetime.now().year)[2:4] + '_' + str(new_code).zfill(5)
    code_bank_obj.last_digit = new_code
    code_bank_obj.save()
    return value


@api_view(['POST'])
def register_request_for_sub_storage(request):
    print(request.data)
    sub_store_request_log_obj = SubStoreRequestLog(input_combo_id=request.data['input_combo_id'],
                                                  storage_id=request.data['store_id'],
                                                  section=request.data['section'],
                                                  sub_section=request.data['sub_section'],
                                                  request_code=generate_request_code_for_sub_store(),
                                                  requested_quantity=request.data['qty'],
                                                  unit_id=4,
                                                  requested_by_id=request.user.id,
                                                  requested_at=datetime.datetime.now(),
                                                  status_id=1,
                                                  )
    sub_store_request_log_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def move_qty_from_main_to_sub_store(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        request_obj = SubStoreRequestLog.objects.get(id=request.data['request_id'])
        storage_list = request.data['storage_list']
        for storage in storage_list:
            entered_qty = int(storage['entered_qty'])
            storage_obj = InputStoreInventory.objects.get(id=storage['id'])
            available_qty = storage_obj.quantity_now
            storage_obj.quantity_now = available_qty - entered_qty
            storage_obj.quantity_now_time = datetime.datetime.now()
            if storage_obj.quantity_now == 0:
                storage_obj.label_range_start = 0
                storage_obj.label_range_end = 0
            else:
                label_range_start = storage_obj.label_range_start
                storage_obj.label_range_start = label_range_start + entered_qty
            storage_obj.save()
            input_sub_store_obj = InputSubStoreInventory(input_store_inventory_id=storage_obj.id,
                                                        sub_storage_id=request_obj.storage.id,
                                                        section=request_obj.section,
                                                        season_id=get_active_season_id(),
                                                        sub_section=request_obj.sub_section,
                                                        date_of_receipt=datetime.datetime.now(),
                                                        quantity_at_receipt=entered_qty,
                                                        quantity_now=entered_qty,
                                                        quantity_now_time=datetime.datetime.now(),
                                                        unit_id=4,
                                                        label_range_start=1,
                                                        label_range_end=1,
                                                        created_by_id=request.user.id,
                                                        modified_by_id=request.user.id
                                                        )
            input_sub_store_obj.save()
            label_from = InputStoreInventoryPacketLabel.objects.filter(input_store_inventory_id=storage_obj.id, stock_status_id=1).order_by('id')[0].label
            for i in range(1, entered_qty+1):
                input_store_label_obj = InputStoreInventoryPacketLabel.objects.filter(input_store_inventory_id=storage_obj.id, stock_status_id=1).order_by('id')[0]
                input_store_label_obj.stock_status_id=2
                input_store_label_obj.save()
                input_sub_store_lable_obj = InputSubStoreInventoryPacketLabel(input_sub_store_inventory_id=input_sub_store_obj.id,
                                                                            label=input_store_label_obj.label,
                                                                            stock_status_id=1,
                                                                            received_date=datetime.datetime.now(),
                                                                            received_by_id=request.user.id)
                input_sub_store_lable_obj.save()
                label_to = input_store_label_obj.label
            input_sub_store_obj.label_range_start = label_from
            input_sub_store_obj.label_range_end = label_to
            input_sub_store_obj.save()
            request_obj.input_sub_store_inventory.add(input_sub_store_obj)
            request_obj.status_id = 2
            request_obj.responsed_by_id = request.user.id
            request_obj.responsed_at = datetime.datetime.now()
            request_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def decline_sub_store_request(request):
    request_obj = SubStoreRequestLog.objects.get(id=request.data['request_id'])
    request_obj.status_id = 3
    request_obj.responsed_by_id = request.user.id
    request_obj.responsed_at = datetime.datetime.now()
    request_obj.declined_reason = request.data['declined_reason']
    request_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_agent_wise_combo_issue_request(request):
    data_dict = {}
    selected_agent_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=request.data['season_id'], supervisor_id=request.data['supervisor_id']).values_list('agent_id', flat=True))
    
    combo_requested_agent_obj = ComboIssueRequestAgentMap.objects.filter(agent_id__in=selected_agent_ids, combo_issue_request__season_id=get_active_season_id()).exclude(combo_issue_request__max_status_id=7).order_by('-combo_issue_request__max_status').order_by('agent_id')
    combo_requested_agent_list = list(combo_requested_agent_obj.values_list('id', 'agent_id', 'agent__first_name', 'agent__userprofile__code', 'combo_issue_request_id', 'combo_issue_request__supervisor__username', 'combo_issue_request__issue_rised_date', 'combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'quantity_in_numbers', 'combo_issue_request__expected_date', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__max_status',  'combo_issue_request__senior_supervisor__username', 'combo_issue_request__senior_supervisor_status', 'combo_issue_request__senior_supervisor_status__name', 'combo_issue_request__senior_supervisor_status_date', 'combo_issue_request__assitant_manager__username', 'combo_issue_request__assitant_manager_status', 'combo_issue_request__assitant_manager_status__name', 'combo_issue_request__assitant_manager_status_date', 'combo_issue_request__agri_officer__username', 'combo_issue_request__agri_officer_status', 'combo_issue_request__agri_officer_status__name', 'combo_issue_request__agri_officer_status_date', 'combo_issue_request__gm__username', 'combo_issue_request__gm_status_date', 'combo_issue_request__gm_status__name', 'combo_issue_request__dispatched_by__username', 'combo_issue_request__dispatch_date', 'combo_issue_request__dispatch_status__name'))
    combo_requested_agent_column = ['id', 'agent_id', 'agent_first_name', 'agent_code', 'combo_reques_id', 'supervisor_name', 'issue_raised_date', 'input_combo_id','input_combo_name', 'area_qty', 'date_of_expected', 'total_qty', 'max_status_id', 'senior_supervisor_name', 'senior_supervisor_status_id', 'senior_supervisor_status_name','senior_supervisor_date', 'assitant_manager_name', 'assitant_manager_status_id', 'assitant_manager_status_name','assitant_manager_date', 'agri_officer_name', 'agri_officer_status_id', 'agri_officer_status_name','agri_officer_date', 'gm_name', 'gm_status_date','gm_status_name', 'dispatched_by_name', 'dispatch_date','dispatch_status_name']
    combo_requested_agent_df = pd.DataFrame(combo_requested_agent_list, columns=combo_requested_agent_column)

    user_cluster_list = list(UserClusterMap.objects.filter(season_id=request.data['season_id'], user_id__in=selected_agent_ids).order_by('unique_code').values_list('user_id', 'unique_code'))
    user_cluster_columns = ['agent_id', 'unique_code']
    user_cluster_df = pd.DataFrame(user_cluster_list, columns=user_cluster_columns)

    combo_requested_agent_df['senior_supervisor_date'] = pd.to_datetime(combo_requested_agent_df['senior_supervisor_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_requested_agent_df['assitant_manager_date'] = pd.to_datetime(combo_requested_agent_df['assitant_manager_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_requested_agent_df['agri_officer_date'] = pd.to_datetime(combo_requested_agent_df['agri_officer_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_requested_agent_df['gm_status_date'] = pd.to_datetime(combo_requested_agent_df['gm_status_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_requested_agent_df['dispatch_status_date'] = pd.to_datetime(combo_requested_agent_df['dispatch_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')

    combo_requested_agent_df = combo_requested_agent_df.merge(user_cluster_df, how="left", left_on="agent_id", right_on="agent_id")
    combo_requested_agent_df = combo_requested_agent_df.fillna(0)

    combo_requested_agent_df['senior_supervisor_status_text'] = combo_requested_agent_df['senior_supervisor_name'].astype(str) + ' ' + combo_requested_agent_df['senior_supervisor_status_name'].astype(str) + ' on ' + combo_requested_agent_df['senior_supervisor_date'].astype(str)
    combo_requested_agent_df['assitant_manager_status_text'] = combo_requested_agent_df['assitant_manager_name'].astype(str) + ' ' + combo_requested_agent_df['assitant_manager_status_name'].astype(str) + ' on ' + combo_requested_agent_df['assitant_manager_date'].astype(str)
    combo_requested_agent_df['agri_officer_status_text'] = combo_requested_agent_df['agri_officer_name'].astype(str) + ' ' + combo_requested_agent_df['agri_officer_status_name'].astype(str) + ' on ' + combo_requested_agent_df['agri_officer_date'].astype(str)
    combo_requested_agent_df['gm_status_text'] = combo_requested_agent_df['gm_name'].astype(str) +' '+ combo_requested_agent_df['gm_status_name'].astype(str) + ' on ' + combo_requested_agent_df['gm_status_date'].astype(str)
    combo_requested_agent_df['gm_status_text'] = combo_requested_agent_df['dispatched_by_name'].astype(str) +' '+ combo_requested_agent_df['dispatch_status_name'].astype(str) + ' on ' + combo_requested_agent_df['dispatch_status_date'].astype(str)
    
    combo_requested_agent_df = combo_requested_agent_df.sort_values(by=['unique_code'])
    data_dict['agent_list'] = combo_requested_agent_df.drop_duplicates(subset='agent_id', keep="last").to_dict('r')

    data_dict['agent_wise_combo_issue'] = combo_requested_agent_df.groupby('agent_id').apply(lambda x:x.to_dict('r')).to_dict()

    agent_ids = list(set(list(combo_requested_agent_obj.values_list('agent_id', flat=True))))
    agent_combo_receipt_obj = ComboIssueAgentInventoryReceipt.objects.filter(agent_id__in=agent_ids)
    agent_combo_receipt_list = list(agent_combo_receipt_obj.values_list('id', 'agent_id', 'combo_issue_request'))
    agent_combo_receipt_column = ['id', 'agent_id', 'combo_issue_request']
    agent_combo_receipt_df = pd.DataFrame(agent_combo_receipt_list, columns=agent_combo_receipt_column)
    data_dict['agent_combo_wise_receipt'] = agent_combo_receipt_df.groupby('agent_id')['combo_issue_request'].apply(list).to_dict()

    return Response(data=data_dict, status=status.HTTP_200_OK)


def generate_bill_numeber_for_code_bank():
    code_bank_obj = AgentReceiptBillNumberCodeBank.objects.filter()[0]
    last_digit_code = code_bank_obj.last_bill_number
    new_bill_code = last_digit_code + 1
    code_bank_obj.last_bill_number = new_bill_code
    code_bank_obj.save()
    return new_bill_code


@api_view(['POST'])
@transaction.atomic
def serve_document_for_agent_receipt(request):
    print(request.data)
    issue_request_ids = request.data['combo_issue_ids']
    agent_id = request.data['agent_id']
    final_dict = {}

    seed_list = []
    kit_list = []

    for combo in issue_request_ids:
        combo_id_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=combo)
        for combo in combo_id_obj:
            input_id = combo.combo_issue_request.input_combo.id
            if input_id in [8,9]:
                seed_list.append(input_id)
            else:
                kit_list.append(input_id)

    if len(seed_list) == 0 and len(kit_list) > 0:
        print('kit ok')
        # request_input_ids = issue_request_ids
        print(issue_request_ids, agent_id)
        data = serve_document_pesticide_fertilizer_pdf(issue_request_ids,agent_id)
        # print(data)
        return Response(data=data, status=status.HTTP_200_OK)
        
    elif len(kit_list) == 0 and len(seed_list) >0:
        request_input_ids = issue_request_ids
        print('seed ok')
    else:
        data={
        'status':False,
        'alert':'Select any one kit or seed'
        }
        return Response(data=data, status=status.HTTP_200_OK) 
    sid = transaction.savepoint()
    try:
        for issue_request in request_input_ids:
            if ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request_id=issue_request, agent_id=agent_id).exists():
                print('came')
                combo_issue_receipt_obj = ComboIssueAgentInventoryReceipt.objects.get(combo_issue_request_id=issue_request, agent_id=agent_id)
                print(combo_issue_receipt_obj.file)
                final_dict['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.file)
                final_dict['bill_number'] = combo_issue_receipt_obj.bill_number
                return Response(data=final_dict, status=status.HTTP_200_OK)
        print('out')
        new_bill_code = generate_bill_numeber_for_code_bank()

        #data constriction
        combo_issue_agent_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id__in=request_input_ids, agent_id=agent_id)  
        agent_details_list = list(combo_issue_agent_obj.values_list('agent__first_name', 'agent__last_name', 'agent__userprofile__code', 'agent__userprofile__village__name', 'agent__userclustermap__cluster__name', 'agent__subordinate_user__superior__username'))
        data_dict = pd.DataFrame(agent_details_list, columns=['agent_name', 'father_name', 'agent_code', 'village_ame', 'cluster_name', 'superior_name']).drop_duplicates().to_dict('r')[0]
        combo_request_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id__in=request_input_ids, agent_id=agent_id)
        combo_request_list = list(combo_request_obj.values_list('combo_issue_request', 'combo_issue_request__input_combo_id', 'combo_issue_request__input_combo__name', 'combo_issue_request__input_combo__price', 'combo_issue_request__input_combo__area__quantity_in_acre','quantity_in_numbers' ,'substoreissuelabelagentmap', 'substoreissuelabelagentmap__label', 'substoreissuelabelagentmap__input_sub_store_inventory__input_store_inventory__input_packet_inventory__packet_code', 'substoreissuelabelagentmap__input_sub_store_inventory__section', 'substoreissuelabelagentmap__input_sub_store_inventory', 'combo_issue_request__dispatch_date','combo_issue_request__supervisor__username', 'combo_issue_request__dispatched_by_id', 'combo_issue_request__issue_rised_date'))
        combo_request_column = ['combo_issue_request', 'input_combo_id', 'input_combo_name', 'input_combo_price', 'input_combo_acre','quantity_in_numbers', 'store_issue_label_id', 'label', 'store_name', 'section', 'store_id', 'dispatch_date', 'supervisor_name', 'dispatched_by_id','issue_rised_date']
        combo_request_df = pd.DataFrame(combo_request_list, columns=combo_request_column)
        combo_request_df['total_price'] = 0
        combo_request_df['total_acre'] = 0
        combo_request_df['total_price'] = combo_request_df['quantity_in_numbers'] * combo_request_df['input_combo_price']
        combo_request_df['total_acre'] = combo_request_df['quantity_in_numbers'] * combo_request_df['input_combo_acre']
        combo_request_df = combo_request_df.groupby(['combo_issue_request', 'store_id']).agg({'label': list,  'input_combo_name': 'first', 'store_name': 'first', 'section': 'first', 'quantity_in_numbers': 'first', 'total_acre': 'first', 'input_combo_acre': 'first', 'total_price': 'first', 'input_combo_id': 'first', 'input_combo_price': 'first', 'dispatch_date': 'first',  'supervisor_name': 'first', 'dispatched_by_id': 'first', 'issue_rised_date': 'first'}).reset_index()
        combo_request_df['label_from'] = combo_request_df.apply(lambda x: x['label'][0], axis=1)
        combo_request_df['label_to'] = combo_request_df.apply(lambda x: x['label'][-1], axis=1)
        data_dict['input_part_list'] = combo_request_df.groupby('combo_issue_request').apply(lambda x:x.to_dict('r')).to_dict()
        data_dict['input_combo_list'] = combo_request_df.drop_duplicates(subset='combo_issue_request', keep="last").to_dict('r')
        data_dict['bill_number'] = new_bill_code
        input_combo_ids = list(set(list(combo_request_obj.values_list('combo_issue_request__input_combo_id', flat=True))))
        input_combo_dict = {}
        for input_combo in InputCombo.objects.filter(id__in=input_combo_ids):
            if not input_combo.id in input_combo_dict:
                input_combo_dict[input_combo.id] = {
                    'value': 1,
                    'unit_name': 'Nos'
                }
            if InputPart.objects.filter(input_combo_id=input_combo).count() == 1:
                input_part_obj = InputPart.objects.get(input_combo_id=input_combo)
                input_combo_dict[input_combo.id]['value'] = input_part_obj.value
                input_combo_dict[input_combo.id]['unit_name'] = input_part_obj.unit.name
            
        data_dict['input_combo_dict'] = input_combo_dict  

        today_date = datetime.datetime.now().date()
        file_name = str(new_bill_code) + '.pdf'
        try:
            path = os.path.join('static/media/agent_receipt/', str(agent_id), str(today_date))
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/agent_receipt/' + str(agent_id) + '/' + str(today_date) + '/',file_name)

        # file generation
        mycanvas = canvas.Canvas(file_path, pagesize=A4)

        #border line
        mycanvas.line(25,820,570,820)
        mycanvas.line(25,20,570,20)
        mycanvas.line(25,820,25,20)
        mycanvas.line(570,820,570,20)
        img_file = os.path.join('static/media/',"ccgb_logo.jpeg")
        mycanvas.drawInlineImage(img_file, 40, 760,(.6*inch), (.8*inch))


        #heading part
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(325, 800,'CHENGUANG NATURAL EXTRACTS (INDIA) PVT.LTD.,')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(305, 780,'SY.No.251,Thriyambakapura Village,Terakanambi Hobali,Gundlupet Taluk,')
        mycanvas.setFont('Helvetica', 13)
        mycanvas.drawCentredString(305, 760,'Chamarajanagar District')
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(305, 735,'AGENT SEED ISSUE RECEIPT')


        #actual pdf part

        #left Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(40,700,str('R.No. ')+str(data_dict['bill_number']))
        mycanvas.drawString(40,670,str('Agent Name: ')+str(data_dict['agent_name']))
        mycanvas.drawString(40,640,str('Father Name: ')+str(data_dict['father_name']))
        mycanvas.drawString(40,610,str('Supervisor Name: ')+str(data_dict['superior_name']))
        mycanvas.drawString(40,580,str('Permission department: '))

        #Right Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(350,700,str('Date: ')+str(datetime.datetime.now().date()))
        mycanvas.drawString(350,670,str('Agent Code: ')+str(data_dict['agent_code']))
        mycanvas.drawString(350,640,str('Village Name: ')+str(data_dict['village_ame']))
        mycanvas.drawString(350,610,str('Cluster: ')+str(data_dict['cluster_name']))
        mycanvas.drawString(350,580,str('Out Time: '))


        #Table Content
        mycanvas.setFont('Helvetica-Bold', 15)
        mycanvas.drawCentredString(305, 545,'Seed Details')

        #headder part
        mycanvas.line(25,538,570,538)
        mycanvas.line(25,500,570,500)

        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.drawCentredString(50, 515,'Items')
        mycanvas.drawCentredString(105, 515,'Lot No')
        mycanvas.drawCentredString(165, 515,'Lable No')
        mycanvas.drawCentredString(240, 525,'Req. Date /')
        mycanvas.drawCentredString(240, 510,'Dspt. Date')
        mycanvas.drawCentredString(305, 515,'Value')

        mycanvas.drawCentredString(370, 520,'No Of')
        mycanvas.drawCentredString(370, 505,'Pkts')

        mycanvas.drawCentredString(420, 515,'Acre')
        mycanvas.drawCentredString(460, 515,'Price')
        mycanvas.drawCentredString(530, 515,'Amount')

        y = 480
        x = 110
        total_num_of_packet = 0
        total_num_of_acre = 0
        total_price = 0
        mycanvas.setLineWidth(0)
        mycanvas.setFont('Helvetica', 10)
        supervisor_name = ''
        for input_combo in data_dict['input_combo_list']:
            length = len(data_dict['input_part_list'][input_combo['combo_issue_request']])
            length = length/2
            length = math.ceil(length)
            store_id = data_dict['input_part_list'][input_combo['combo_issue_request']][length-1]['store_id']
            for input_part in data_dict['input_part_list'][input_combo['combo_issue_request']]:
                mycanvas.drawString(x-25, y ,str(input_part['store_name'])+" "+str(input_part['section']))
                mycanvas.setFont('Helvetica', 9)
                mycanvas.drawString(x+25, y+5 ,str(input_part['label_from'])+ ' -')
                mycanvas.drawString(x+29, y-5 ,str(input_part['label_to']))
                mycanvas.drawString(x+105, y+5 ,str(input_part['issue_rised_date'].date()))
                mycanvas.drawString(x+105, y-5 ,str(input_part['dispatch_date'].date()))
                mycanvas.setFont('Helvetica', 10)
                if input_part['store_id'] == store_id:
                    name = str(input_combo['input_combo_name']).split(' ')
                    if len(name) == 1:
                        mycanvas.drawString(30, y ,str(name[0][0:8]))
                    else:
                        mycanvas.drawString(30, y ,str(name[0][0:4]+" "+ str(name[1])[0:4]))
                    unit_value = data_dict['input_combo_dict'][input_combo['input_combo_id']]
                    mycanvas.drawString(285, y ,str(int(unit_value['value'])) + ' ' + str(unit_value['unit_name']))

                    mycanvas.drawRightString(380, y ,str(input_combo['quantity_in_numbers']))
                    total_num_of_packet += input_combo['quantity_in_numbers']

                    mycanvas.drawRightString(430, y ,str(int(input_combo['total_acre'])))
                    total_num_of_acre += input_combo['total_acre']

                    mycanvas.drawRightString(480, y ,str(input_combo['input_combo_price']))

                    mycanvas.drawRightString(565, y ,str(input_combo['total_price']))
                    total_price += input_combo['total_price']
                supervisor_name = input_combo['supervisor_name']
                y -= 14
            mycanvas.line(25,y,570,y)
            y -= 14

        mycanvas.line(x-30,538,x-30,y+15)
        mycanvas.line(x+20,538,x+20,y+15)
        mycanvas.line(200,538,200,y+15)
        mycanvas.line(280,538,280,y+15)
        mycanvas.line(340,538,340,y-10)
        mycanvas.line(440,538,440,y-10)
        mycanvas.line(400,538,400,y-10)
        mycanvas.line(490,538,490,y-10)

        #Total
        mycanvas.line(340,y-10,570,y-10)
        mycanvas.setFont('Helvetica-Bold', 11)
        mycanvas.drawString(300, y-3 , 'Total :')
        mycanvas.drawRightString(380, y-3 ,str(total_num_of_packet))
        mycanvas.drawRightString(430, y-3 ,str(int(total_num_of_acre)))
        mycanvas.drawRightString(560, y-3 ,str(total_price))

        mycanvas.setFont('Helvetica', 11)
        mycanvas.drawRightString(100,  y-140, str('Remarks :'))
        bottom_signs_y_axis = y-180 

        # bottom_signs
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawRightString(130,  100, str('Agent Signature'))
        mycanvas.drawRightString(280,  100, str('Supervisor Signature'))
        mycanvas.drawRightString(410,  100, str('Issued Signature'))
        mycanvas.drawRightString(530,  100, str('GM Signature'))

        #bottom sign images
        file_name = str(data_dict['superior_name']) + '.jpeg'
        sup_file = os.path.join('static/media/signs/',file_name)
        mycanvas.drawInlineImage(sup_file, 180, 120,(1.4*inch), (.7*inch))
        gm_img_file = os.path.join('static/media/signs/',"gm.png")
        mycanvas.drawInlineImage(gm_img_file, 460, 120,(1.4*inch), (.7*inch))

        mycanvas.save()
        for issue_request in issue_request_ids:
            combo_issue_receipt_obj = ComboIssueAgentInventoryReceipt(combo_issue_request_id=issue_request,
                                                                    agent_id=agent_id,
                                                                    bill_number=new_bill_code,
                                                                    file=file_path)
            combo_issue_receipt_obj.save()
            combo_issue_obj = ComboIssueRequest.objects.get(id=issue_request)
            combo_issue_obj.max_status_id = 9
            combo_issue_obj.save()
        final_dict['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.file)
        final_dict['bill_number'] = combo_issue_receipt_obj.bill_number
        final_dict['status'] = True
        transaction.savepoint_commit(sid)
        return Response(data=final_dict, status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)
    



@api_view(['POST'])
def serve_agents_for_given_request(request):
    print(request.data)
    ComboIssueRequest_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id'])
    master_list = []
    for data in ComboIssueRequest_obj:
        temp={
            'agent_first_name':data.agent.first_name,
            'agent_last_name':data.agent.last_name,
            'agent_code':UserProfile.objects.get(user_id=data.agent.id).code,
            'quantity_in_numbers':data.quantity_in_numbers,
            'request_code':data.combo_issue_request.request_code,
            'issue_rised_date':data.combo_issue_request.issue_rised_date,
            'agent_id':data.agent.id,
            'issue_expected_date':data.combo_issue_request.expected_date,
            'issue_id':data.id,
            'max_status_id': data.combo_issue_request.max_status.id
            
        }
        if data.shop != None:
            temp['shop_id']=data.shop.id
            temp['shop_name']=data.shop.name
            temp['shop_type']=data.shop.type.name
            temp['shop_type_id']=data.shop.type.id
            if data.shop.type.id == 2:
                temp['delivery_from']=data.delivery_from
                temp['delivery_to']=data.delivery_to
            else:
                temp['delivery_from']=''
                temp['delivery_to']=''
        else:
            temp['shop_id']= ''
            temp['shop_name']= ''
            temp['shop_type']= ''
            temp['shop_type_id']= 0
            temp['delivery_from']=''
            temp['delivery_to']=''

        master_list.append(temp)

    
    master_list
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_season(request):
    print("getting seasons")
    data = Season.objects.all().values()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_user_unique_codes(request):
    user_cluster_obj = UserClusterMap.objects.filter(season_id=request.data['season_id'], cluster_id=request.data['cluster_id'], user__userprofile__user_type_id__in=[6]).order_by('unique_code')
    user_cluster_values = list(user_cluster_obj.values_list('id', 'user__first_name', 'user__username', 'unique_code', 'user__userprofile__user_type__name', 'user__userprofile__user_type_id'))
    user_cluster_columns = ['id', 'first_name','username', 'unique_code','user_type_name' , 'user_type_id']
    user_cluster_df = pd.DataFrame(user_cluster_values, columns=user_cluster_columns)
    user_cluster_df = user_cluster_df.fillna('-').groupby("user_type_name").apply(lambda x: x.to_dict("r")).to_dict()
    return Response(user_cluster_df, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def update_unique_code(request):
    UserClusterMap.objects.filter(id=request.data['user_cluster_map_id']).update(unique_code=request.data['unique_code'])
    return Response(status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((AllowAny,))
def date_range_cultivation_phase_report(request):
    master_dict={
        'have_data': False
    }
    print(request.data)
    season_id = request.data['season_id']
    if Sowing.objects.filter(sowing_date__gte=request.data['start_date'], sowing_date__lte=request.data['end_date'], season_id=season_id).exists(): 
        master_dict['have_data'] = True  
        sowing_obj = Sowing.objects.filter(sowing_date__gte=request.data['start_date'], sowing_date__lte=request.data['end_date'], season_id=season_id).order_by('sowing_date')
        # print(sowing_obj)
        for data in sowing_obj:
            date_string = data.sowing_date.strftime('%Y-%m-%d')
            if not date_string in master_dict:
                master_dict[date_string]={}
            if not data.cultivation_phase.name in master_dict[date_string]:
                master_dict[date_string][data.cultivation_phase.name] = 0

            master_dict[date_string][data.cultivation_phase.name] += data.area
        return Response(data=master_dict, status=status.HTTP_200_OK)
    else:
        return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_cluster_based_on_loged_user_for_current_season(request):
    season_id = get_active_season_id()
    if UserProfile.objects.get(user_id=request.user.id).user_type_id==5:
        cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list('cluster_id', flat=True))
    elif UserProfile.objects.get(user_id=request.user.id).user_type_id==3:
        all_subordinates = UserHierarchyMap.objects.filter(superior_id=request.user.id, season_id=season_id)
        all_subordinate_user_ids = list(all_subordinates.values_list("subordinate", flat=True))
        cluster_ids = list(UserClusterMap.objects.filter(user_id__in=all_subordinate_user_ids, season_id=season_id).values_list('cluster_id', flat=True))
    else:
        cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    data = Cluster.objects.filter(id__in=cluster_ids).values()  
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_cluster_based_on_loged_user_for_given_season(request):
    season_id = request.data['season_id']
    print(request.user.id)
    if UserProfile.objects.get(user_id=request.user.id).user_type_id==5:
        cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list('cluster_id', flat=True))
    elif UserProfile.objects.get(user_id=request.user.id).user_type_id==3:
        all_subordinates = UserHierarchyMap.objects.filter(superior_id=request.user.id, season_id=season_id)
        all_subordinate_user_ids = list(all_subordinates.values_list("subordinate", flat=True))
        cluster_ids = list(UserClusterMap.objects.filter(user_id__in=all_subordinate_user_ids, season_id=season_id).values_list('cluster_id', flat=True))
    else:
        cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))
    data = Cluster.objects.filter(id__in=cluster_ids).values()  
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_cluster_based_agent_for_current_season(request):
    season_id = get_active_season_id()
    cluster_based_agent = {}
    agent_user_ids = list(UserProfile.objects.filter(user_type_id=6).values_list("user_id", flat=True))
    for cluster in UserClusterMap.objects.filter(user_id__in=agent_user_ids, season_id=season_id):
        if cluster.cluster.id not in cluster_based_agent:
            cluster_based_agent[cluster.cluster.id] = []

        cluster_based_agent[cluster.cluster.id].append({"name": cluster.user.first_name,"id": cluster.user.id,"first_name": cluster.user.first_name,"last_name": cluster.user.last_name,"user_id": cluster.user.id,})
    return Response(cluster_based_agent, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_role_for_current_season(request):
    season_id = get_active_season_id()
    positions_users = list(PositionPositionUserMap.objects.all().values_list("user_id", flat=True))
    user_ids = list(UserProfile.objects.filter(user_id__in=positions_users, user_type_id=5).values_list("user_id", flat=True))
    season_users = list(UserClusterMap.objects.filter(user_id__in=user_ids, season_id=season_id).values_list('user_id',flat=True))
    user_list = list(User.objects.filter(id__in=season_users).order_by("username").values_list("id", "first_name", "username"))
    user_column = ["id", "name", "username"]
    user_df = pd.DataFrame(user_list, columns=user_column)
    return Response(user_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def app_version_check(request):
    """
    app version check
    """
    version = '0.0.36'
    relogin = True
    data = {'version': version, 'relogin': relogin}
    return Response(data)


@api_view(['GET'])
def season_cluster_management(request):
    master_dict = {}
    season_id=get_active_season_id()
    current_season_cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id',flat=True))
    master_dict['all_clusters'] = list(Cluster.objects.filter().values())
    master_dict['clusters_not_included_for_this_season'] = list(Cluster.objects.filter().exclude(id__in=current_season_cluster_ids).values())
    master_dict['current_season_clusters'] = list(Cluster.objects.filter(id__in=current_season_cluster_ids).values())
    return Response(master_dict, status=status.HTTP_200_OK)

    
@api_view(['POST'])
def remove_cluster_from_season(request):
    season_id = get_active_season_id()
    ClusterSeasonMap.objects.filter(season_id=season_id, cluster_id= request.data['cluster_id']).delete()
    return Response(status=status.HTTP_200_OK)
    

@api_view(['POST'])
def add_cluster_to_season(request):
    season_id = get_active_season_id()
    cluster_season_obj = ClusterSeasonMap(season_id=season_id, cluster_id=request.data['cluster_id'])
    cluster_season_obj.save()
    return Response(status=status.HTTP_200_OK)
    

@api_view(['GET'])
def user_season_management(request):
    master_dict = {}
    season_id=get_active_season_id()

    current_season_users = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=5).values_list('user_id', flat=True))
    active_users = list(User.objects.filter(id__in=current_season_users).values_list('id', 'username'))
    active_users_columns = ['id','name']
    active_users_df = pd.DataFrame(active_users, columns=active_users_columns)
    positions = list(PositionManUserMap.objects.filter().values_list('user_id',flat=True))
    inactive_users = User.objects.filter(userprofile__user_type_id=5, is_active=True).exclude(id__in=current_season_users)
    inactive_users = list(inactive_users.exclude(id__in=positions).values_list('id', flat=True))
    
    in_active_users = list(User.objects.filter(id__in=inactive_users).values_list('id', 'username'))
    in_active_users_columns = ['id','name']
    in_active_users_df = pd.DataFrame(in_active_users, columns=in_active_users_columns)
    
    master_dict['current_season_users'] = active_users_df.to_dict('r')
    master_dict['inactive_users'] = in_active_users_df.to_dict('r')

    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_active_season_cluster(request):
    cluster_list = []
    # user_cluster = list(UserClusterMap.objects.filter(season_id=get_active_season_id()).values_list('cluster_id', flat=True))
    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=get_active_season_id()).values_list('cluster_id', flat=True))
    for cluster in Cluster.objects.filter(id__in=cluster_ids):
        cluster_dict = {"name": cluster.name, "id": cluster.id}
        cluster_list.append(cluster_dict)
    return Response(data=cluster_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_user_to_season(request):
    season_id = get_active_season_id()
    user_cluster_map = UserClusterMap(
        season_id=season_id, 
        cluster_id=request.data['cluster_id'],
        user_id = request.data['user_id'],
        unique_code = '',
        modified_by=request.user
        )
    user_cluster_map.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_user_from_season(request):
    season_id = get_active_season_id()
    UserClusterMap.objects.filter(season_id=season_id, user_id=request.data['user_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_agent_supervisor_map_season_wise(request):
    supervisor_id=request.data['user_id']
    master_dict = {}
    season_id = get_active_season_id()
    current_agent_list = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id', flat=True))
    un_active_users = list(UserProfile.objects.filter(user_type_id=6).exclude(user_id__in=current_agent_list).values_list('user_id', 'user__first_name', 'user__last_name'))
    un_active_users_columns = ['user_id', 'first_name', 'last_name']
    un_active_users_df = pd.DataFrame(un_active_users, columns=un_active_users_columns)
    master_dict['in_active'] = un_active_users_df.to_dict('r')

    active_users = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=supervisor_id, season_id=season_id).values_list('agent_id', 'agent__first_name', 'agent__last_name'))
    active_users_columns = ['user_id', 'first_name', 'last_name']
    active_users_df = pd.DataFrame(active_users, columns=active_users_columns)
    master_dict['active']=active_users_df.to_dict('r')
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_agent_to_supervisor(request):
    agent_sup_obj = AgentSupervisorSeasonMap(
        agent_id=request.data['agent_id'],
        supervisor_id=request.data['supervisor_id'],
        season_id=get_active_season_id()
    )
    agent_sup_obj.save()
    season_id = get_active_season_id()
    cluster_id = UserClusterMap.objects.get(season_id=season_id, user_id=request.data['supervisor_id']).cluster_id
    if UserClusterMap.objects.filter(season_id=season_id, user_id=request.data['agent_id']).exists():
        UserClusterMap.objects.filter(season_id=season_id, user_id=request.data['agent_id']).delete()
    user_cluster_obj = UserClusterMap(
        season_id=season_id,
        user_id=request.data['agent_id'],
        cluster_id=cluster_id,
        unique_code='',
        modified_by_id=request.user.id)
    user_cluster_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_agent_to_supervisor(request):
    season_id = get_active_season_id()
    AgentSupervisorSeasonMap.objects.filter(agent_id=request.data['agent_id'],supervisor_id=request.data['supervisor_id'],season_id=get_active_season_id()).delete()
    UserClusterMap.objects.filter(season_id=season_id, user_id=request.data['agent_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def get_afs_sfs_map(request):
    print(request.data)
    user_id = request.data['sfs_id']
    season_id = get_active_season_id()
    master_dict = {}
    afs_ids = list(UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type=5).values_list('user_id', flat=True))
    print(afs_ids)
    active_user_ids = list(UserHierarchyMap.objects.filter(season_id=season_id, superior_id=user_id).values_list('subordinate', flat=True))
    print(active_user_ids)

    curr_user_ids = list(UserHierarchyMap.objects.filter(season_id=season_id).values_list('subordinate', flat=True))
    inactive_ids = list(set(afs_ids) - set(curr_user_ids))
    print(inactive_ids)

    active_users = list(UserProfile.objects.filter(user_id__in=active_user_ids).values_list('user_id', 'user__username', 'user__last_name'))
    active_users_columns = ['user_id', 'first_name', 'last_name']
    active_users_df = pd.DataFrame(active_users, columns=active_users_columns)

    inactive_users = list(UserProfile.objects.filter(user_id__in=inactive_ids).values_list('user_id', 'user__username', 'user__last_name'))
    inactive_users_columns = ['user_id', 'first_name', 'last_name']
    inactive_users_df = pd.DataFrame(inactive_users, columns=inactive_users_columns)

    master_dict['active'] = active_users_df.to_dict('r')
    master_dict['inactive'] = inactive_users_df.to_dict('r')
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_sfs_users(request):
    position_users = list(UserHierarchyMap.objects.filter(season_id=get_active_season_id(), superior_user_type_id=3).values_list('superior_id',flat=True))
    user_ids = list(UserProfile.objects.filter(user_type_id__in=position_users).values_list('user_id', flat=True))
    active_users = list(UserProfile.objects.filter(user_id__in=position_users).values_list('user_id', 'user__username', 'user__last_name'))
    active_users_columns = ['id', 'first_name', 'last_name']
    active_users_df = pd.DataFrame(active_users, columns=active_users_columns)
    master_dict = active_users_df.to_dict('r')
    print(master_dict)
    return Response(master_dict, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def check_authentication(request):
    if request.user.is_authenticated:
        print('Yes')
    else:
        print('No')
    return Response(status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_cluster_based_on_season(request):
    cluster_season_values = list(ClusterSeasonMap.objects.filter().values_list('cluster_id', 'cluster__name', 'season_id'))
    cluster_season_columns = ['id', 'name', 'season_id']
    cluster_season_df = pd.DataFrame(cluster_season_values, columns=cluster_season_columns)
    data = cluster_season_df.groupby('season_id').apply(lambda x: x.to_dict("r")).to_dict()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_season_with_active_season(request):
    data = {}
    data['all_seasons'] = pd.DataFrame(Season.objects.filter().values()).to_dict('r')
    active_season = Season.objects.get(is_active=True)
    data['active_season'] = {'name':active_season.name, 'id':active_season.id}
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_sowing_data_in_date_wise(request):
    temp_list = []
    print(request.data)
    farmer_list=[]
    active_season = Season.objects.get(is_active=True)
    active_season_id = active_season.id
    cluster_season_map_obj = ClusterSeasonMap.objects.filter(season_id=active_season_id)

    for data in cluster_season_map_obj:
        temp_dict={'Cluster Name':data.cluster.name}
        
        farmer_cluster_seasonmap_obj = FarmerClusterSeasonMap.objects.filter(season_id=active_season_id, cluster_id=data.cluster.id).count()
        temp_dict['Farmer Count']=farmer_cluster_seasonmap_obj
        farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=active_season_id, cluster_id=data.cluster.id).values_list('farmer_id', flat=True))
            
            
        sowing_nursery_count = Sowing.objects.filter(season_id=active_season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1, sowing_date=request.data['sowing_date']).count()
        temp_dict['Nursery Count'] = sowing_nursery_count 


        sowing_transplant_count = Sowing.objects.filter(season_id=active_season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2, sowing_date=request.data['sowing_date']).count()
        temp_dict['Transplant Count']=sowing_transplant_count

        Nursery_area = Sowing.objects.filter(season_id=active_season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1, sowing_date=request.data['sowing_date']).aggregate(Sum('area'))["area__sum"]
        if not Nursery_area is None:
            temp_dict['Nursery Area']=Nursery_area
        else:
            Nursery_area=0
            temp_dict['Nursery Area']=Nursery_area

        Transplant_area = Sowing.objects.filter(season_id=active_season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2, sowing_date=request.data['sowing_date']).aggregate(Sum('area'))["area__sum"]
        if not Transplant_area is None:
            temp_dict['Transplant Area']=Transplant_area
        else:
            Transplant_area=0
            temp_dict['Transplant Area']=Transplant_area
        temp_list.append(temp_dict)
    data = {}
    data['data'] = temp_list
    df = pd.DataFrame(temp_list)

    df.index += 1
    total = df.sum(numeric_only=True)
    total.name = 'Total'
    df = df.append(total.transpose())

    df.to_excel(str("static/media/") + "day_wise.xlsx", engine="xlsxwriter", sheet_name="Sheet1", startrow=1)

    # data={}
    try:
        image_path = str("static/media/") + "day_wise.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print('Error',err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_sowing_data_report(request):
    temp_list = []
    season_id = request.data['season_id']
    cluster_season_map_obj = ClusterSeasonMap.objects.filter(season_id=season_id)
    for data in cluster_season_map_obj:
        temp_dict={'Cluster Name':data.cluster.name}
        farmer_cluster_seasonmap_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id=data.cluster.id).count()
        temp_dict['Farmer Count']=farmer_cluster_seasonmap_obj
        farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id=data.cluster.id).values_list('farmer_id', flat=True))
        sowing_Nursery_count = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1,).count()
        temp_dict['Nursery Count']=sowing_Nursery_count 
        sowing_transplant_count = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2).count()
        temp_dict['Transplant Count']=sowing_transplant_count
        Nursery_area = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=1).aggregate(Sum('area'))["area__sum"]
        if not Nursery_area is None:
            temp_dict['Nursery Area']=Nursery_area
        else:
            Nursery_area=0
            temp_dict['Nursery Area']=Nursery_area
        Transplant_area = Sowing.objects.filter(season_id=season_id, farmer_id__in=farmer_ids, cultivation_phase_id=2).aggregate(Sum('area'))["area__sum"]
        if not Transplant_area is None:
            temp_dict['Transplant Area']=Transplant_area
        else:
            Transplant_area=0
            temp_dict['Transplant Area']=Transplant_area
        temp_list.append(temp_dict)
    data = {}
    df = pd.DataFrame(temp_list)
    
    df_mean = pd.DataFrame(temp_list)
    # temp_list.append(dict(round(df_mean.mean(axis=0))))

    temp_list.append(dict(df_mean.sum(axis=0)))
    
    df = pd.DataFrame(temp_list)

    df = df.fillna(0)
    df.index += 1
    df.at[len(temp_list),'Cluster Name'] = 'Total'
    # df.at[len(temp_list),'Cluster Name'] = 'Average'
    df.to_excel(str("static/media/") + "overall_sowing.xlsx", engine="xlsxwriter", sheet_name="Sheet1", startrow=1)
    data['data'] = df.to_dict('r')


    # data={}
    try:
        image_path = str("static/media/") + "overall_sowing.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print('Error',err)

    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes((AllowAny,))
def combo_issue_request_data(request):
    ComboIssueRequest_obj = ComboIssueRequest.objects.filter(request.data['max_status_id'], request.data['dispatch_date__gte'], request.data['dispatch_date__lte'])
    if ComboIssueRequest.objects.filter(max_status_id=8, dispatch_date__gte='2020-03-01', dispatch_date__lte='2021-04-01').exists():

        ComboIssueRequest_obj = ComboIssueRequest.objects.filter(request.data['max_status_id'], request.data['dispatch_date__gte'], request.data['dispatch_date__lte'])
        ComboIssueRequest_list = list(ComboIssueRequest_obj.values_list('id', 
                                                                        'issue_rised_date',
                                                                       'input_combo__name',
                                                                       'quantity_in_numbers',
                                                                       'quantity_for_area',
                                                                        'supervisor__username',
                                                                        'senior_supervisor',
                                                                        'senior_supervisor_status_date',
                                                                        'assitant_manager__username',
                                                                       'assitant_manager_status_date',
                                                                        'agri_officer__username',
                                                                        'agri_officer_status_date',
                                                                        'gm__username',
                                                                        'gm_status_date',
                                                                        'dispatch_date',
                                                                        'dispatched_by'

                                                                       ))
#         pd.to_datetime(d).date()
        ComboIssueRequest_column_name = ['id', 
                                            'issue_rised_date',
                                           'input_combo__name',
                                           'quantity_in_numbers',
                                           'quantity_for_area',
                                            'supervisor__username',
                                            'senior_supervisor',
                                            'senior_supervisor_status_date',
                                            'assitant_manager__username',
                                            'assitant_manager_status_date',
                                            'agri_officer__username',
                                            'agri_officer_status_date',
                                            'gm__username',
                                            'gm_status_date',
                                            'dispatch_date',
                                            'dispatched_by']
        excel_temp_df = pd.DataFrame(ComboIssueRequest_list, columns=ComboIssueRequest_column_name)
        excel_temp_df = pd.DataFrame(ComboIssueRequest_list, columns=ComboIssueRequest_column_name)
        excel_temp_df['issue_rised_date'] = pd.to_datetime(excel_temp_df['issue_rised_date']).dt.date
        excel_temp_df['senior_supervisor_status_date'] = pd.to_datetime(excel_temp_df['senior_supervisor_status_date']).dt.date
        excel_temp_df['assitant_manager_status_date'] = pd.to_datetime(excel_temp_df['assitant_manager_status_date']).dt.date
        excel_temp_df['agri_officer_status_date'] = pd.to_datetime(excel_temp_df['agri_officer_status_date']).dt.date
        excel_temp_df['gm_status_date'] = pd.to_datetime(excel_temp_df['gm_status_date']).dt.date
        excel_temp_df['dispatch_date'] = pd.to_datetime(excel_temp_df['dispatch_date']).dt.date
        
        writer = pd.ExcelWriter(str("static/media/") + "ComboIssueRequestData.xlsx", engine="xlsxwriter")
        final_df = excel_temp_df    
        # creating excel sheet with name
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:V1", "Agent List with Bank details " + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
    return Response(data=final_df, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def sowing_cultivation_phase_report(request):
    season_id = request.data['season_id']
    sowing_obj = Sowing.objects.filter(season_id=season_id)
    sowing_values = list(sowing_obj.values_list('farmer_id','sowing_date', 'area', 'cultivation_phase__name'))
    column_names = ['Farmer Id','Sowing Date', 'Area','Cultivation Phase Name']
    sowing_df = pd.DataFrame(sowing_values, columns=column_names)
    # sowing_df

    agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
    agent_farmer_values = list(agent_farmer_obj.values_list('agent__first_name','farmer__farmer_id', 'farmer__seasonal_farmer_code', 'farmer__cluster__name'))
    coulumn_names = ['Agent Name','Farmer Id', 'Farmer Code', 'Cluster Name']

    agent_farmer_df = pd.DataFrame(agent_farmer_values, columns=coulumn_names)
    agent_farmer_df

    merge_sowing_df_agent_farmer_df = pd.merge(sowing_df, agent_farmer_df, how="left", on="Farmer Id")

    # merge_sowing_df_agent_farmer_df

    writer = pd.ExcelWriter(str("static/media/") +'agent_farmer_cluster_map.xlsx', engine = 'xlsxwriter')

    for cultivation_phase in CultivationPhase.objects.all():
        # print(cultivation_phase.name)
        final_df = merge_sowing_df_agent_farmer_df[merge_sowing_df_agent_farmer_df['Cultivation Phase Name']==cultivation_phase.name]
        final_df['Farmer Id'] = final_df['Farmer Id'].astype(str) 
        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())
        final_df.to_excel(writer, sheet_name=(cultivation_phase.name))

    writer.save()
    print('existed')
    data = {} 
    try:
        image_path = str("static/media/") + "agent_farmer_cluster_map.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def daily_activity_report(request):

    daterange = pd.date_range(request.data['start_date'], request.data['end_date'])
    master_dict={}
    
    created_by_user = request.data['user_id']
    
    for date_variable in daterange:
        single_date = date_variable.strftime("%Y-%m-%d")

        farmer_count = Farmer.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        sowing_count = Sowing.objects.filter(time_created__date=single_date, farmer__created_by_id=created_by_user).count()
        phase1_count = Sowing.objects.filter(time_created__date=single_date, farmer__created_by_id=created_by_user,cultivation_phase_id=1).count()
        phase2_count = Sowing.objects.filter(time_created__date=single_date, farmer__created_by_id=created_by_user,cultivation_phase_id=2).count()
        water_resource_count = WaterResource.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        userprofile_count = UserProfile.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        userbank_details_count = UserBankDetails.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        farmer_bank_details_count = FarmerBankDetails.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()   

        answer_logfor_radio_count     =  AnswerLogForRadio.objects.filter(time_added__date=single_date, added_by_id=created_by_user).count()
        answer_logfor_checkbox_count  =  AnswerLogForCheckbox.objects.filter(time_added__date=single_date, added_by_id=created_by_user).count()
        answer_logfor_dropdown_count  =  AnswerLogForDropDown.objects.filter(time_added__date=single_date, added_by_id=created_by_user).count()
        answer_logfor_textinput_count =  AnswerLogForTextInput.objects.filter(time_added__date=single_date, added_by_id=created_by_user).count()
        answer_logfor_password_count  =  AnswerLogForPassword.objects.filter(time_added__date=single_date, added_by_id=created_by_user).count()
        total_count_answerlog = answer_logfor_radio_count+answer_logfor_checkbox_count+answer_logfor_dropdown_count+answer_logfor_textinput_count+answer_logfor_password_count
        sowing_boundary_map_count = SowingBoundaryMap.objects.filter(time_created__date=single_date, added_by_id=created_by_user).count()


        procurement_group_count = ProcurementGroup.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        harvest_count = Harvest.objects.filter(time_created__date=single_date, created_by_id=created_by_user).count()
        sowing_boundary_map_count = SowingBoundaryMap.objects.filter(time_created__date=single_date, added_by_id=created_by_user).count()

        usertypeid = UserProfile.objects.get(user_id=created_by_user).user_type.id

        if not single_date in master_dict:
            master_dict[single_date] = {
                                        'farmer_count':farmer_count,
                                        'Total_sowing_register_count':sowing_count,
                                        'cultivation_phase1_count':phase1_count,
                                        'cultivation_phase2_count':phase2_count,
                                        'water_resource_count':water_resource_count,
                                        'user_profile_count':userbank_details_count,
                                        'user_bankdetails_count':userbank_details_count,
                                        'farmer_bank_details_count':farmer_bank_details_count,                                                            
                                        'dynamic_question_total_count':total_count_answerlog,
                                        'sowing_boundary_map_count':sowing_boundary_map_count,
                                        'procurement_group_count':procurement_group_count,
                                        'harvest_count':harvest_count,
                                        'sowing_boundary_map_count':sowing_boundary_map_count
                                            }
            if usertypeid == 5:
                supervisor_count =  ComboIssueRequest.objects.filter(time_created__date=single_date, supervisor_id= usertypeid).count()     
                master_dict[single_date]['supervisor_count']= supervisor_count
            if usertypeid == 4:
                agri_officer_count = ComboIssueRequest.objects.filter(time_created__date=single_date, agri_officer_id= usertypeid).count()
                master_dict[single_date]['agri_officer_count']= agri_officer_count  
            if usertypeid == 3:
                senior_supervisor_count = ComboIssueRequest.objects.filter(time_created__date=single_date, senior_supervisor_id= usertypeid).count()
                master_dict[single_date]['senior_supervisor_count']= senior_supervisor_count  
            if usertypeid == 2:
                Assistant_manager_count = ComboIssueRequest.objects.filter(time_created__date=single_date, Assistant_manager_count_id= usertypeid).count()
                master_dict[single_date]['Assistant_manager_count']= Assistant_manager_count  
            if usertypeid == 1:
                gm_count = ComboIssueRequest.objects.filter(time_created__date=single_date, gm_id= usertypeid).count()
                master_dict[single_date]['gm_count']= gm_count  

    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def sowing_farmer_report(request):
    farmar_list = []
    master_dict = {}

    active_season = get_active_season_id()
    days = request.data['day_count']
    farmer_id_list = list(set(FarmerClusterSeasonMap.objects.filter(season_id=active_season, cluster_id__in=request.data['cluster_ids']).values_list('farmer_id', flat=True)))
    # print(len(farmer_id_list))
    data = {} 
    if Sowing.objects.filter(cultivation_phase_id=1, season_id=active_season,farmer_id__in=farmer_id_list).exists():
        sowing_farmer_objects = Sowing.objects.filter(cultivation_phase_id=1, season_id=active_season,farmer_id__in=farmer_id_list)

        for farmer in sowing_farmer_objects:
            sowing_date = farmer.sowing_date
            new_date = sowing_date + datetime.timedelta(days=days)

            if not Sowing.objects.filter(cultivation_phase_id=2, farmer_id=farmer.farmer_id, season_id=active_season,sowing_date__gt=new_date).exists():
                farmer_season_map_obj = FarmerClusterSeasonMap.objects.get(farmer_id=farmer.farmer_id, season_id=active_season)
                temp = {
                    'Farmer First Name':farmer.farmer.first_name,
                    'Farmer Last Name' :farmer.farmer.last_name,
                    'Farmer Season Code':farmer_season_map_obj.seasonal_farmer_code,
                    'Agent Name':AgentFarmerMap.objects.get(farmer_id=farmer_season_map_obj.id).agent.first_name,
                    'Cluser Name':FarmerClusterSeasonMap.objects.get(farmer_id=farmer.farmer_id, season_id=active_season).cluster.name,
                    'Acre':farmer.area
                    }
                farmar_list.append(temp)
        temp_df = pd.DataFrame(farmar_list)
        writer = pd.ExcelWriter(str("static/media/") + "sowing_farmer_report.xlsx", engine="xlsxwriter")
        final_df = temp_df    

        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())
        # creating excel sheet with name
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:G1", "sowing farmer report " + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        data = {} 
        try:
            image_path = str("static/media/") + "sowing_farmer_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def remove_agent_from_issue(request):
    data= {}
    print(request.data)
    print(ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id']).values_list('agent_id',flat=True))
    print(ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id']).aggregate(Sum('quantity_in_numbers')))
    print(ComboIssueRequest.objects.get(id=request.data['request_combo_id']).quantity_in_numbers)

    if len(request.data['removed_agent_list']) !=0:
        for agent_id in request.data['removed_agent_list']:
            temp_obj = ComboIssueRequestAgentMap.objects.get(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id)
            combo_issue_delete_log_obj = ComboIssueDeleteAgentLog(
                combo_issue_request_id=temp_obj.combo_issue_request.id,
                agent_id=agent_id,
                issue_raised_date=temp_obj.issue_rised_date,
                quantity_in_numbers=temp_obj.quantity_in_numbers,
                removed_by_id=request.user.id,
            )
            combo_issue_delete_log_obj.save()
            combo_request_obj = ComboIssueRequest.objects.get(id=request.data['request_combo_id'])
            total_qty = combo_request_obj.quantity_in_numbers
            input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)
            updated_total_qty = total_qty - temp_obj.quantity_in_numbers
            updated_total_area = updated_total_qty * input_combo_obj.area.quantity_in_acre
            ComboIssueRequest.objects.filter(id=request.data['request_combo_id']).update(quantity_in_numbers=updated_total_qty, quantity_for_area=updated_total_area)
            temp_obj.delete()
        print(ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id']).values_list('agent_id',flat=True))
    print(request.data['shop_list'].keys())
    for agent_id in  request.data['shop_list'].keys():
        if ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id).exists():
            shop_type_id = Shop.objects.get(id=request.data['shop_list'][agent_id]['shop_id']).type.id
            if shop_type_id == 1:
                print('agri')
                ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id).update(
                    shop_id=request.data['shop_list'][agent_id]['shop_id']
                )
            elif shop_type_id == 2:
                print('direct')
                ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id).update(
                    shop_id=request.data['shop_list'][agent_id]['shop_id'],
                    delivery_from=request.data['shop_list'][agent_id]['from'],
                    delivery_to=request.data['shop_list'][agent_id]['to'],
                )
                combo_request_obj = ComboIssueRequest.objects.get(id=request.data['request_combo_id'])
                temp_obj = ComboIssueRequestAgentMap.objects.get(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id)
                input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)

                total_qty = combo_request_obj.quantity_in_numbers
                updated_total_qty = total_qty - temp_obj.quantity_in_numbers
                updated_total_area = updated_total_qty * input_combo_obj.area.quantity_in_acre
                ComboIssueRequest.objects.filter(id=request.data['request_combo_id']).update(quantity_in_numbers=updated_total_qty, quantity_for_area=updated_total_area)

            elif shop_type_id == 3:
                print('shops')
                ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id).update(
                    shop_id=request.data['shop_list'][agent_id]['shop_id'],
                )
                combo_request_obj = ComboIssueRequest.objects.get(id=request.data['request_combo_id'])
                temp_obj = ComboIssueRequestAgentMap.objects.get(combo_issue_request_id=request.data['request_combo_id'], agent_id=agent_id)
                input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)

                total_qty = combo_request_obj.quantity_in_numbers
                updated_total_qty = total_qty - temp_obj.quantity_in_numbers
                updated_total_area = updated_total_qty * input_combo_obj.area.quantity_in_acre
                ComboIssueRequest.objects.filter(id=request.data['request_combo_id']).update(quantity_in_numbers=updated_total_qty, quantity_for_area=updated_total_area)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_max_status(request):
    data = list(MaxStatus.objects.filter().exclude(id=1).values())
    return Response(data=data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def serve_completed_issue_request(request):
    season_id = get_active_season_id()
    if request.data['purpose']=='completed':
        combo_issue_request_obj = ComboIssueRequest.objects.filter(max_status_id__in=[8,9], season_id=season_id).order_by('issue_rised_date')
    else:
        combo_issue_request_obj = ComboIssueRequest.objects.filter(max_status_id__in=[7], season_id=season_id).order_by('issue_rised_date')
    combo_issue_request_list = list(combo_issue_request_obj.values_list('id', 'supervisor__username', 'issue_rised_date', 'input_combo_id','input_combo__name', 'quantity_for_area', 'expected_date', 'quantity_in_numbers', 'max_status',  'senior_supervisor__username', 'senior_supervisor_status', 'senior_supervisor_status__name', 'senior_supervisor_status_date', 'assitant_manager__username', 'assitant_manager_status', 'assitant_manager_status__name', 'assitant_manager_status_date', 'agri_officer__username', 'agri_officer_status', 'agri_officer_status__name', 'agri_officer_status_date', 'gm__username', 'gm_status_date', 'gm_status__name', 'dispatched_by__username', 'dispatch_status__name', 'dispatch_date'))
    combo_issue_request_column = ['id', 'supervisor_name', 'issue_raised_date', 'input_combo_id','input_combo_name', 'area_qty', 'date_of_expected', 'total_qty', 'max_status_id', 'senior_supervisor_name', 'senior_supervisor_status_id', 'senior_supervisor_status_name','senior_supervisor_date', 'assitant_manager_name', 'assitant_manager_status_id', 'assitant_manager_status_name','assitant_manager_date', 'agri_officer_name', 'agri_officer_status_id', 'agri_officer_status_name','agri_officer_date', 'gm_name', 'gm_status_date','gm_status_name', 'dispatched_by_username', 'dispatch_status_name', 'dispatch_date']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_list, columns=combo_issue_request_column)

    combo_issue_request_df['senior_supervisor_date'] = pd.to_datetime(combo_issue_request_df['senior_supervisor_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['assitant_manager_date'] = pd.to_datetime(combo_issue_request_df['assitant_manager_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['agri_officer_date'] = pd.to_datetime(combo_issue_request_df['agri_officer_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['gm_status_date'] = pd.to_datetime(combo_issue_request_df['gm_status_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')
    combo_issue_request_df['dispatch_date'] = pd.to_datetime(combo_issue_request_df['dispatch_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%b %d %Y')

    combo_issue_request_df = combo_issue_request_df.fillna(0)

    combo_issue_request_df['senior_supervisor_status_text'] = combo_issue_request_df['senior_supervisor_name'].astype(str) +' '+ combo_issue_request_df['senior_supervisor_status_name'].astype(str) + ' on ' + combo_issue_request_df['senior_supervisor_date'].astype(str)
    combo_issue_request_df['assitant_manager_status_text'] = combo_issue_request_df['assitant_manager_name'].astype(str) +' '+ combo_issue_request_df['assitant_manager_status_name'].astype(str) + ' on ' + combo_issue_request_df['assitant_manager_date'].astype(str)
    combo_issue_request_df['agri_officer_status_text'] = combo_issue_request_df['agri_officer_name'].astype(str) +' '+ combo_issue_request_df['agri_officer_status_name'].astype(str) + ' on ' + combo_issue_request_df['agri_officer_date'].astype(str)
    combo_issue_request_df['gm_status_text'] = combo_issue_request_df['gm_name'].astype(str) +' '+ combo_issue_request_df['gm_status_name'].astype(str) + ' on ' + combo_issue_request_df['gm_status_date'].astype(str)
    combo_issue_request_df['dispatch_status_text'] = combo_issue_request_df['dispatched_by_username'].astype(str) +' '+ combo_issue_request_df['dispatch_status_name'].astype(str) + ' on ' + combo_issue_request_df['dispatch_date'].astype(str)

    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(max_status_id=2, combo_issue_request__season_id=season_id)
    combo_issue_request_agent_list = list(combo_issue_request_agent_obj.values_list('id', 'combo_issue_request_id', 'agent', 'agent__userclustermap__cluster__name'))
    combo_issue_request_agent_column = ['agent_map_id', 'combo_issue_request_id', 'agent_user_id', 'cluster_name']
    combo_issue_request_agent_df = pd.DataFrame(combo_issue_request_agent_list, columns=combo_issue_request_agent_column)

    grouped_df = combo_issue_request_agent_df.groupby(['combo_issue_request_id']).agg({'agent_user_id': 'count', 'cluster_name': 'min'}).reset_index()

    final_df = combo_issue_request_df.merge(grouped_df, how='left', left_on='id', right_on='combo_issue_request_id')
    final_df = final_df.rename(columns={'agent_user_id': 'agent_count'})
    final_df = final_df.fillna(0)
    final_dict = final_df.groupby('input_combo_id').apply(lambda x: x.to_dict('r')).to_dict()   
    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_pending_agent_request_log(request):
    season_id = get_active_season_id()
    combo_obj = ComboIssueDeleteAgentLog.objects.filter(combo_issue_request__season_id=season_id)
    combo_delete_list = list(combo_obj.values_list('id', 'combo_issue_request_id', 'combo_issue_request__input_combo_id', 'combo_issue_request__input_combo__name', 'agent__id', 'agent__first_name', 'issue_raised_date', 'quantity_in_numbers', 'removed_by__username', 'time_created', 'combo_issue_request__supervisor__username'))
    combo_delete_columns = ['id', 'combo_issue_request_id', 'input_combo_id', 'input_combo_name', 'agent_id', 'agent_first_name', 'issue_raised_date', 'quantity_in_numbers', 'removed_by', 'removed_on', 'supervisor_name']
    combo_delete_df = pd.DataFrame(combo_delete_list, columns =combo_delete_columns)
    final_dict = combo_delete_df.groupby('input_combo_id').apply(lambda x:x.to_dict('r')).to_dict()
    return Response(data=final_dict, status=status.HTTP_200_OK)



@api_view(['POST'])
def save_fcm_device_token(request):
    print(request.user)
    fcm_device_token = request.data['token']
    name = 'grower'
    if 'name' in request.data:
        name = request.data['admin']
    if not FCMDevice.objects.filter(user=request.user).exists():
        obj = FCMDevice(
            name=name,
            active=True,
            device_id='test',
            registration_id=fcm_device_token,
            type='android',
            user=request.user
        )
        obj.save()

    else:
        obj = FCMDevice.objects.get(user=request.user)
        obj.registration_id = fcm_device_token
        obj.save()

    return Response(status=status.HTTP_200_OK)

def send_push_notification(title, body, user_ids, data):
    print('user_ids', user_ids)
    print('title', title)
    print('body', body)
    print('======= within in push notification ===========>')
    print(user_ids)
    print("title = {}, body = {}, data = {}".format(title, body, data))
    devices = FCMDevice.objects.filter(user_id__in=user_ids)
    for device in devices:
        device.send_message(title=title, body=body, sound="default", api_key="AIzaSyAw3UA4Y_K3_K87QoJ4UyO_UOEXAq11Tuo", data=data)
        print(device)
        print('-----notification sent success------')

@api_view(['GET'])
def serve_shop_list(request):
    shop_values = list(Shop.objects.filter().values_list('id', 'name', 'type__id', 'type__name'))
    shop_list = ['id', 'name', 'type_id', 'type_name']
    shop_df = pd.DataFrame(shop_values, columns=shop_list)
    data = {}
    data['all_shops'] = shop_df.to_dict('r')
    data['direct_delivery_shop_ids'] =  list(Shop.objects.filter(type_id=2).values_list('id',flat=True))
    defualt_shop_obj =Shop.objects.filter(type_id=1)[0]
    data['default_agri_shop_id'] = {
        'id':defualt_shop_obj.id,
        'name':defualt_shop_obj.name,
        'type_id': defualt_shop_obj.type.id,
        'type_name': defualt_shop_obj.type.name
    }

    return Response(data, status=status.HTTP_200_OK)


def generate_issue_notice_bill_no():
    bill_obj = AgentIssueNoticeNumberCodeBank.objects.get(id=1)
    updated_bill_no = bill_obj.last_bill_number + 1
    bill_obj.last_bill_number = updated_bill_no
    bill_obj.save()
    return updated_bill_no


@api_view(['POST'])
def generate_issue_notice_pdf(request):
    issue_id = request.data['issue_id']
    agent_id = request.data['agent_id']
    season_id = get_active_season_id()
    issue_agent_obj = ComboIssueRequestAgentMap.objects.get(id=issue_id, agent_id=agent_id)
    print(issue_agent_obj.issue_notice)
    if issue_agent_obj.issue_notice == '':
        data_dict = {}
        data_dict['bill_number'] = generate_issue_notice_bill_no()
        data_dict['agent_name'] = issue_agent_obj.agent.first_name
        data_dict['father_name'] = issue_agent_obj.agent.last_name
        data_dict['superior_name'] = issue_agent_obj.combo_issue_request.supervisor.username
        data_dict['agent_code'] = UserProfile.objects.get(user_id=issue_agent_obj.agent.id).code
        data_dict['village_name'] = UserProfile.objects.get(user_id=issue_agent_obj.agent.id).village.name
        data_dict['cluster_name'] = UserClusterMap.objects.get(season_id=season_id, user_id=issue_agent_obj.agent.id).cluster.name
        if issue_agent_obj.shop == None:
            data_dict['dispatch_from'] = '-'
            data_dict['dispatch_to'] = '-'
            data_dict['shop'] = '-'

        else:
            if issue_agent_obj.shop.type.id == 2:
                data_dict['dispatch_from'] = issue_agent_obj.delivery_from
                data_dict['dispatch_to'] = issue_agent_obj.delivery_to
            else:
                data_dict['dispatch_from'] = '-'
                data_dict['dispatch_to'] = '-'
            data_dict['shop'] = issue_agent_obj.shop.name
        data_dict['item_name'] = issue_agent_obj.combo_issue_request.input_combo.name
        data_dict['requested_date'] = issue_agent_obj.combo_issue_request.issue_rised_date.date()
        data_dict['quantity_in_pkts'] = issue_agent_obj.quantity_in_numbers
        data_dict['expected_date'] = str(issue_agent_obj.combo_issue_request.expected_date.date())

        data_dict['senior_supervisor'] = issue_agent_obj.combo_issue_request.senior_supervisor.username
        data_dict['senior_supervisor_date'] = datetime.datetime.strptime(str(issue_agent_obj.combo_issue_request.senior_supervisor_status_date).split('+')[0].split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y - %I:%M %p')

        data_dict['asst_manager'] = issue_agent_obj.combo_issue_request.assitant_manager.username
        data_dict['asst_manager_date'] = datetime.datetime.strptime(str(issue_agent_obj.combo_issue_request.assitant_manager_status_date).split('+')[0].split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y - %I:%M %p')


        data_dict['agri_officer'] = issue_agent_obj.combo_issue_request.agri_officer.username
        data_dict['agri_officer_date'] = datetime.datetime.strptime(str(issue_agent_obj.combo_issue_request.agri_officer_status_date).split('+')[0].split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y - %I:%M %p')

        data_dict['gm'] = issue_agent_obj.combo_issue_request.gm.username
        data_dict['gm_date'] = datetime.datetime.strptime(str(issue_agent_obj.combo_issue_request.gm_status_date).split('+')[0].split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y - %I:%M %p')

        # file generation
        today_date = datetime.datetime.now().date()
        file_name = 'issue_notice_'+ str(data_dict['bill_number']) + '.pdf'
        try:
            path = os.path.join('static/media/agent_issue_notice/', str(agent_id), str(today_date))
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/agent_issue_notice/' + str(agent_id) + '/' + str(today_date) + '/',file_name)

        # file generation
        mycanvas = canvas.Canvas(file_path, pagesize=A4)


        #border line
        mycanvas.line(25,820,570,820)
        mycanvas.line(25,20,570,20)
        mycanvas.line(25,820,25,20)
        mycanvas.line(570,820,570,20)
        img_file = os.path.join('static/media/',"ccgb_logo.jpeg")
        mycanvas.drawInlineImage(img_file, 40, 760,(.6*inch), (.8*inch))


        #heading part;;
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(325, 800,'CHENGUANG NATURAL EXTRACTS (INDIA) PVT.LTD.,')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(305, 780,'SY.No.251,Thriyambakapura Village,Terakanambi Hobali,Gundlupet Taluk,')
        mycanvas.setFont('Helvetica', 13)
        mycanvas.drawCentredString(305, 760,'Chamarajanagar District')
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(305, 735,'AGENT ISSUE RECEIPT')

        #left Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(40,700,str('R.No. ')+str(data_dict['bill_number']))
        mycanvas.drawString(40,670,str('Agent Name: ')+str(data_dict['agent_name']))
        mycanvas.drawString(40,640,str('Father Name: ')+str(data_dict['father_name']))
        mycanvas.drawString(40,610,str('Supervisor Name: ')+str(data_dict['superior_name']))
        mycanvas.drawString(40,580,str('Permission department: '))
        mycanvas.drawString(40,550,str('Shop: ')+str(data_dict['shop']))
        mycanvas.drawString(40,520,str('Dispatch from: ')+str(data_dict['dispatch_from']))
        # mycanvas.drawString(40,490,str('Shop: ')+str(data_dict['superior_name']))


        #Right Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(350,700,str('Date: ')+str(datetime.datetime.now().date()))
        mycanvas.drawString(350,670,str('Agent Code: ')+str(data_dict['agent_code']))
        mycanvas.drawString(350,640,str('Village Name: ')+str(data_dict['village_name']))
        mycanvas.drawString(350,610,str('Cluster: ')+str(data_dict['cluster_name']))
        mycanvas.drawString(350,580,str('Out Time: '))
        mycanvas.drawString(350,550,str('Vehicle No: '))
        mycanvas.drawString(350,520,str('Dispatch to: ')+str(data_dict['dispatch_from']))



        #item details
        mycanvas.setFont('Helvetica-Bold', 15)
        mycanvas.drawCentredString(305, 490,'Item Details')

        # left side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(40,470,str('Item Name: ')+str(data_dict['item_name']))
        mycanvas.drawString(40,440,str('Requested date: ')+str(data_dict['requested_date']))

        # right side
        mycanvas.drawString(350,470,str('Quantity: ')+str(data_dict['quantity_in_pkts']))
        mycanvas.drawString(350,440,str('Expected date: ')+str(data_dict['expected_date']))

        #approval details
        mycanvas.setFont('Helvetica-Bold', 15)
        mycanvas.drawCentredString(305, 415,'Approval Details')

        mycanvas.setFont('Helvetica', 12)
        # left side
        mycanvas.drawString(40,390,str('Sen. Supervisor: ')+str(data_dict['senior_supervisor']))
        mycanvas.drawString(40,365,str('Agri manager: ')+str(data_dict['asst_manager']))
        mycanvas.drawString(40,340,str('Agri office: ')+str(data_dict['agri_officer']))
        mycanvas.drawString(40,315,str('General Manager: ')+str(data_dict['gm']))


        # right side
        mycanvas.drawString(350,390,str(data_dict['senior_supervisor_date']))
        mycanvas.drawString(350,365,str(data_dict['asst_manager_date']))
        mycanvas.drawString(350,340,str(data_dict['agri_officer_date']))
        mycanvas.drawString(350,315,str(data_dict['gm_date']))


        file_name = str(data_dict['superior_name']) + '.jpeg'
        sup_file = os.path.join('static/media/signs/',file_name)
        mycanvas.drawInlineImage(sup_file, 180, 200,(1.4*inch), (.7*inch))
        gm_img_file = os.path.join('static/media/signs/',"gm.png")
        mycanvas.drawInlineImage(gm_img_file, 460, 200,(1.4*inch), (.7*inch))

        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawRightString(130,  190, str('Agent Signature'))
        mycanvas.drawRightString(280,  190, str('Supervisor Signature'))
        mycanvas.drawRightString(410,  190, str('Issued Signature'))
        mycanvas.drawRightString(530,  190, str('GM Signature'))

        mycanvas.save()
        ComboIssueRequestAgentMap.objects.filter(id=request.data['issue_id']).update(issue_notice=file_path)
        combo_issue_receipt_obj = ComboIssueRequestAgentMap.objects.get(id=request.data['issue_id'])
        data = {}
        data['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.issue_notice)
        return Response(data, status=status.HTTP_200_OK)
    else:
        print('taken from db')
        combo_issue_receipt_obj = ComboIssueRequestAgentMap.objects.get(id=request.data['issue_id'])
        data = {}
        data['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.issue_notice)
        return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def input_combo_wise_report(request):
    print(request.data)
    max_status_id = request.data['max_status_id']
    season_id = get_active_season_id()
    if ComboIssueRequestAgentMap.objects.filter(combo_issue_request__max_status_id=max_status_id, combo_issue_request__season_id=season_id).exists():
        combo_issue_request_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request__max_status_id=max_status_id, combo_issue_request__season_id=season_id)
        combo_issue_request_values = list(combo_issue_request_obj.values_list("agent__first_name","combo_issue_request__input_combo__name","combo_issue_request__quantity_in_numbers","combo_issue_request__request_code","combo_issue_request__issue_rised_date","combo_issue_request__supervisor__username","combo_issue_request__expected_date","combo_issue_request__dispatch_date","combo_issue_request__max_status__name","shop__name"))
        column_names = ["Agent Name","Requested Name","Requested Qty","Request Code","Issue Rised Date","Issued Supervisor","Expected Date","Dispatch Date","Status Name","Shop Name"]
        df = pd.DataFrame(combo_issue_request_values, columns=column_names)

        df['Issue Rised Date'] = pd.to_datetime(df['Issue Rised Date']).dt.date
        df['Expected Date'] = pd.to_datetime(df['Expected Date']).dt.date
        df['Dispatch Date'] = pd.to_datetime(df['Dispatch Date']).dt.date

        df1 = df.groupby('Requested Name')

        writer = pd.ExcelWriter(str("static/media/") + "Input_combo_wise_report.xlsx", engine='xlsxwriter')
        for row,group in df1:
            if ':' in row:
                mod_sheet_name = row.split(':')[0]
            else:
                mod_sheet_name = str(row[:30])
            group.to_excel(writer, sheet_name=mod_sheet_name,  index=False)
        writer.save()
        data={}
        try:
            image_path = str("static/media/") + "Input_combo_wise_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def input_combo_shop_wise_total(request):
    print('shop_id',request.data)
    shop_id = request.data['shop_id']
    season_id = get_active_season_id()
    if ComboIssueRequestAgentMap.objects.filter(shop_id=shop_id, combo_issue_request__season_id=season_id).exists():
        combo_issue_request_agentmap_obj = ComboIssueRequestAgentMap.objects.filter(shop_id=shop_id, combo_issue_request__season_id=season_id)
        combo_issue_request_agentmap_values = list(combo_issue_request_agentmap_obj.values_list("agent__first_name","combo_issue_request__request_code","combo_issue_request__input_combo__name","combo_issue_request__quantity_in_numbers","combo_issue_request__quantity_for_area","combo_issue_request__issue_rised_date","combo_issue_request__supervisor__username","combo_issue_request__expected_date","combo_issue_request__senior_supervisor__username","combo_issue_request__senior_supervisor_status_date","combo_issue_request__assitant_manager__username","combo_issue_request__assitant_manager_status_date",
                                                                            "combo_issue_request__agri_officer__username","combo_issue_request__agri_officer_status_date","combo_issue_request__gm__username","combo_issue_request__gm_status_date","combo_issue_request__dispatch_date",
                                                                            "delivery_from","delivery_to","shop__name"))
        column_names = ["Agent Name","Request Code","Input Combo Name","Requested Qty","Qty Area","Issue Rised Date","Issued Supervisor","Expected Date","Senior Supervisor","Senior Supervisor Status Date","Assitant Manager",
                        "Assitant Manager Status Date","Agri Officer","Agri Officer Status Date","Gm","Gm Status Date","Dispatch Date",
                        "Delivery From","Delivery To","Shop Name"]
        df = pd.DataFrame(combo_issue_request_agentmap_values, columns=column_names)
        df['Issue Rised Date'] = pd.to_datetime(df['Issue Rised Date']).dt.date
        df['Senior Supervisor Status Date'] = pd.to_datetime(df['Senior Supervisor Status Date']).dt.date
        df['Assitant Manager Status Date'] = pd.to_datetime(df['Assitant Manager Status Date']).dt.date
        df['Agri Officer Status Date'] = pd.to_datetime(df['Agri Officer Status Date']).dt.date
        df['Gm Status Date'] = pd.to_datetime(df['Gm Status Date']).dt.date
        df['Expected Date'] = pd.to_datetime(df['Expected Date']).dt.date
        df['Dispatch Date'] = pd.to_datetime(df['Dispatch Date']).dt.date
        df['Qty Area'] = df['Qty Area'].astype(int)


        if shop_id != 5:
            df= df.drop(columns=['Delivery From','Delivery To',])
            df= df.fillna(0)

        df1 = df.groupby('Input Combo Name')

        writer = pd.ExcelWriter(str("static/media/") + "input_combo_shop_wise_total.xlsx", engine='xlsxwriter')
        for row,group in df1:
            group.insert(loc=0, column='S No', value=0)
            group['S No'] = np.arange(1, len(group) + 1)
            group['S No'] = group['S No'].astype(str)
            group.loc['Total',:] = group.sum(axis=0, numeric_only=True)
            length_of_frame = len(group)
            group.iloc[-1, group.columns.get_loc('S No')] = 'Total'
            if ':' in row:
                mod_sheet_name = row.split(':')[0]
            else:
                mod_sheet_name = str(row[:30])

            group.to_excel(writer, sheet_name=mod_sheet_name, index=False)
        writer.save()
        
        data={}
        try:
            image_path = str("static/media/") + "input_combo_shop_wise_total.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def combo_issue_request_rised_data_agentwise(request):
    start_date = request.data['start_date']
    end_date = request.data['end_date']
    input_combo_id = request.data['combo_item_id']
    season_id = request.data['season_id']
    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter()
    if ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo_id=input_combo_id, issue_rised_date__gte=start_date, issue_rised_date__lte=end_date).exists():
        combo_issue_request_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo=input_combo_id, issue_rised_date__gte=start_date, issue_rised_date__lte=end_date)
        combo_issue_request_values = list(combo_issue_request_obj.values_list('id','agent_id','agent__first_name','combo_issue_request__issue_rised_date','combo_issue_request__input_combo__name','combo_issue_request__quantity_in_numbers','combo_issue_request__quantity_for_area','combo_issue_request__supervisor__username','combo_issue_request__senior_supervisor__username','combo_issue_request__senior_supervisor_status_date','combo_issue_request__assitant_manager__username','combo_issue_request__assitant_manager_status_date','combo_issue_request__agri_officer__username','combo_issue_request__agri_officer_status_date','combo_issue_request__gm__username','combo_issue_request__gm_status_date','combo_issue_request__dispatch_date','combo_issue_request__dispatched_by__username'))
        
        column_names = ['Id', 'Agent Id','Agent Name','Request Rised Date','Input Combo Name','Quantity In Numbers','Quantity For Area','Supervisor','Senior Superviosor',
                        'Senior Supervisor Status Date','Assitant Manager','Assitant Manager Status Date','Agri Officer','Agri Officer Status Date','Gm','Gm Status Date','Dispatch Date','Dispatched By']

        excel_temp_df = pd.DataFrame(combo_issue_request_values, columns=column_names)

        excel_temp_df['Request Rised Date'] = pd.to_datetime(excel_temp_df['Request Rised Date']).dt.date
        excel_temp_df['Senior Supervisor Status Date'] = pd.to_datetime(excel_temp_df['Senior Supervisor Status Date']).dt.date
        excel_temp_df['Assitant Manager Status Date'] = pd.to_datetime(excel_temp_df['Assitant Manager Status Date']).dt.date
        excel_temp_df['Agri Officer Status Date'] = pd.to_datetime(excel_temp_df['Agri Officer Status Date']).dt.date
        excel_temp_df['Gm Status Date'] = pd.to_datetime(excel_temp_df['Gm Status Date']).dt.date
        excel_temp_df['Dispatch Date'] = pd.to_datetime(excel_temp_df['Dispatch Date']).dt.date



        writer = pd.ExcelWriter(str("static/media/") + "Request_rised_data_agentwise.xlsx", engine="xlsxwriter")

        final_df = excel_temp_df
        for name in combo_issue_request_agent_obj:
    #         print(name.agent.first_name)
            temp_df = final_df[final_df['Agent Id'] == name.agent_id]

            # creating excel sheet with name
            temp_df = temp_df.drop(columns=['Id', 'Agent Id'])

            print(temp_df.columns)

            temp_df.to_excel(writer, sheet_name=str(name.agent.first_name), startrow=1, index=False)
            data = {}
            # assigning that sheet to obj
            workbook = writer.book
            worksheet = writer.sheets[str(name.agent.first_name)]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                    }
                )
            date = datetime.datetime.today()
            # Merge 3 cells.
            worksheet.merge_range("A1:V1", "Request rised data agentwise - " + str(name.agent.first_name),merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 25, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(temp_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "Request_rised_data_agentwise.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes((AllowAny,))
def sowing_age_wise_report_nursery(request):

    season_id=request.data['season_id']

    user_farmer_ids= list(UserFarmerMap.objects.filter(farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))

    filtered_farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id,).values_list("farmer__id", flat=True))   

    phase_two_farmers_ids = list(Sowing.objects.filter(season_id=season_id, cultivation_phase_id=2).values_list('farmer_id', flat=True))
    
    sowing_obj = Sowing.objects.filter(season_id=season_id, cultivation_phase_id=1).exclude(farmer_id__in=phase_two_farmers_ids)

    sowing_values = list(sowing_obj.values_list("id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase__name",))
    sowing_columns = [ "sowing_id", "farmer_id", "sowing_date", "area", "cultivation_phase_id", "cultivation_phase_name"]
    sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)
    today = datetime.datetime.now().date()

    sowing_df["crop_age"] = today - sowing_df["sowing_date"]
    sowing_df["crop_age"] = sowing_df["crop_age"].astype("timedelta64[D]")
    sowing_df["crop_age"] = sowing_df["crop_age"].astype(int)
    if 1== 1:
        range_list = [ "5-10","11-15","16-20", "21-25", "26-30", "31-35", "35-40", "40-135"]    
    else:
        range_list = [ "0-54", "55-61", "62-68", "69-75", "76-82", "83-89", "90-96", "97-103", "104-110", "111-117", "118-124"]
    master_dict = {}
    total = 0

    for row in range_list:
        above_sowing_df = sowing_df[(sowing_df["crop_age"] >= int(row.split("-")[0]))]
        below_sowing_df = above_sowing_df[(above_sowing_df["crop_age"] <= int(row.split("-")[1]))]
        master_dict[row] = below_sowing_df["area"].sum()
        total = total + below_sowing_df["area"].sum()
    above_sowing_df = sowing_df[(sowing_df["crop_age"] >= int(row.split("-")[0]))]
    master_dict["125 +"] = above_sowing_df["area"].sum()
    master_dict["total"] = total + above_sowing_df["area"].sum()
    df = pd.DataFrame(list(master_dict.items()), columns=["Age range in days", "Total Area"])

    writer = pd.ExcelWriter(str("static/media/") + "sowing_age_wise_report.xlsx", engine="xlsxwriter")

    df.to_excel(str("static/media/") + "sowing_age_wise_report.xlsx", engine="xlsxwriter", sheet_name="Sheet1", startrow=1)

    data={}
    try:
        image_path = str("static/media/") + "Input_combo_wise_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print('Error',err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_other_store_agents(request):
    season_id = get_active_season_id()
    combo_issue_requests = ComboIssueRequestAgentMap.objects.filter(shop__type_id__in=[2,3], combo_issue_request__input_combo_id=request.data['request_combo_id'], combo_issue_request__season_id=season_id)
    combo_issue_list = list(combo_issue_requests.values_list('id', 'combo_issue_request__id', 'agent__first_name', 'agent__userprofile__code', 'shop__name', 'shop__type_id', 'delivery_from', 'delivery_to', 'issue_rised_date', 'combo_issue_request__request_code', 'quantity_in_numbers', 'combo_issue_request__supervisor__username', 'agent_id', 'combo_issue_request__max_status_id', 'combo_issue_request__gm__username', 'combo_issue_request__gm_status__name', 'combo_issue_request__agri_officer__username', 'combo_issue_request__agri_officer_status__name'))
    combo_issue_columns = ['combo_issue_request_agent_map_id', 'combo_issue_request_id', 'agent_first_name', 'agent_code', 'shop_name', 'shop_type_id', 'delivery_from', 'delivery_to', 'issue_rised_date', 'request_code', 'quantity_in_numbers', 'supervisor_name', 'agent_id', 'max_status_id', 'gm_username', 'gm_status_name', 'agri_officer_username', 'agri_officer_status_name']
    combo_issue_request_agent_df = pd.DataFrame(combo_issue_list, columns=combo_issue_columns)
    data = combo_issue_request_agent_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_combo_item_list(request):
    input_combo_obj = InputCombo.objects.all().order_by('display_ordinal')
    data = list(input_combo_obj.values())
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_supervisor_based_on_cluster(request):
    user_cluster_map = UserClusterMap.objects.filter(user__userprofile__user_type_id=5)
    user_cluster_list = list(user_cluster_map.values_list('user_id', 'season_id', 'user__username'))
    user_cluster_columns = ['id', 'season_id', 'name']
    user_cluster_df = pd.DataFrame(user_cluster_list, columns=user_cluster_columns)
    data = user_cluster_df.groupby('season_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def combo_issue_request_rised_agent_overall_list(request):
    data = {}
    # date = date.today()
    start_date = request.data['start_date']
    input_combo_id = request.data['input_combo_id'] 
    season_id = request.data['season_id']
    print(request.data)
    if ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo_id=input_combo_id, issue_rised_date__date=start_date).exists():
        combo_issue_request_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo_id=input_combo_id, combo_issue_request__issue_rised_date__date=start_date)
        combo_issue_request_values = list(combo_issue_request_obj.values_list('id','agent__first_name','combo_issue_request__issue_rised_date','combo_issue_request__input_combo__name','combo_issue_request__quantity_in_numbers','combo_issue_request__quantity_for_area','combo_issue_request__supervisor__username','combo_issue_request__senior_supervisor__username','combo_issue_request__senior_supervisor_status_date','combo_issue_request__assitant_manager__username','combo_issue_request__assitant_manager_status_date','combo_issue_request__agri_officer__username','combo_issue_request__agri_officer_status_date','combo_issue_request__gm__username','combo_issue_request__gm_status_date','combo_issue_request__dispatch_date','combo_issue_request__dispatched_by__username'))
        column_names = ['Id', 'Agent Name','Issue Rised Date','Input Combo Name','Quantity In Numbers','Quantity For Area','Supervisor','Senior Supervisor','Senior Supervisor Status Date','Assitant Manager','Assitant Manager Status Date','Agri Officer','Agri Officer Status Date','Gm','Gm Status Date','Dispatch Date','Dispatched By']

        excel_temp_df = pd.DataFrame(combo_issue_request_values, columns=column_names)

        excel_temp_df['Issue Rised Date'] = pd.to_datetime(excel_temp_df['Issue Rised Date']).dt.date
        excel_temp_df['Senior Supervisor Status Date'] = pd.to_datetime(excel_temp_df['Senior Supervisor Status Date']).dt.date
        excel_temp_df['Assitant Manager Status Date'] = pd.to_datetime(excel_temp_df['Assitant Manager Status Date']).dt.date
        excel_temp_df['Agri Officer Status Date'] = pd.to_datetime(excel_temp_df['Agri Officer Status Date']).dt.date
        excel_temp_df['Gm Status Date'] = pd.to_datetime(excel_temp_df['Gm Status Date']).dt.date
        excel_temp_df['Dispatch Date'] = pd.to_datetime(excel_temp_df['Dispatch Date']).dt.date

        writer = pd.ExcelWriter(str("static/media/") + "Combo Item Request Rised Agent List.xlsx", engine="xlsxwriter")
        final_df = excel_temp_df

        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
                }
            )
        # Merge 3 cells.
        worksheet.merge_range("A1:V1", "Combo Item Request Rised Agent List", merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "Combo Item Request Rised Agent List.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        print('data not found')
        data = False
            
    return Response(data=data, status=status.HTTP_200_OK)


@transaction.atomic
def serve_document_pesticide_fertilizer_pdf(issue_request_ids, agent_id):
    # print(request.data)
    sid = transaction.savepoint()
    try:
        issue_request_ids = issue_request_ids
        agent_id = agent_id
        final_dict = {}
        for issue_request in issue_request_ids:
            if ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request_id=issue_request, agent_id=agent_id).exists():
                print('came')
                combo_issue_receipt_obj = ComboIssueAgentInventoryReceipt.objects.get(combo_issue_request_id=issue_request, agent_id=agent_id)
                print(combo_issue_receipt_obj.file)
                final_dict['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.file)
                final_dict['bill_number'] = combo_issue_receipt_obj.bill_number
                final_dict['status'] = True
                return (final_dict)

        print('out')
        new_bill_code = generate_bill_numeber_for_code_bank()

        # data constriction
        combo_issue_agent_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id__in=issue_request_ids, agent_id=agent_id)  
        agent_details_list = list(combo_issue_agent_obj.values_list('agent__first_name', 'agent__last_name', 'agent__userprofile__code', 'agent__userprofile__village__name', 'agent__userclustermap__cluster__name', 'agent__subordinate_user__superior__username','shop__name'))
        data_dict = pd.DataFrame(agent_details_list, columns=['agent_name', 'father_name', 'agent_code', 'village_name', 'cluster_name', 'superior_name','shop_name']).drop_duplicates().to_dict('r')[0]

        combo_request_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id__in=issue_request_ids, agent_id=agent_id)
        combo_request_list = list(combo_request_obj.values_list('combo_issue_request', 'combo_issue_request__input_combo_id', 'combo_issue_request__input_combo__name', 'combo_issue_request__input_combo__price', 'combo_issue_request__input_combo__area__quantity_in_acre','quantity_in_numbers' ,'substoreissuelabelagentmap', 'substoreissuelabelagentmap__input_sub_store_inventory__input_store_inventory__input_packet_inventory__packet_code', 'substoreissuelabelagentmap__input_sub_store_inventory__section', 'substoreissuelabelagentmap__input_sub_store_inventory', 'combo_issue_request__dispatch_date','combo_issue_request__supervisor__username', 'combo_issue_request__dispatched_by_id', 'combo_issue_request__issue_rised_date','shop__name'))
        combo_request_column = ['combo_issue_request', 'input_combo_id', 'input_combo_name', 'input_combo_price', 'input_combo_acre','quantity_in_numbers', 'store_issue_label_id', 'store_name', 'section', 'store_id', 'dispatch_date', 'supervisor_name', 'dispatched_by_id','issue_rised_date','shop_name']
        combo_request_df = pd.DataFrame(combo_request_list, columns=combo_request_column)

        combo_request_df = combo_request_df.fillna(0)
        combo_request_df['total_price'] = 0
        combo_request_df['total_price'] = combo_request_df['quantity_in_numbers'] * combo_request_df['input_combo_price']
        combo_request_df = combo_request_df.groupby(['combo_issue_request', 'store_id']).agg({'input_combo_name': 'first', 'store_name': 'first', 'section': 'first', 'quantity_in_numbers': 'first','input_combo_acre': 'first', 'total_price': 'first', 'input_combo_id': 'first', 'input_combo_price': 'first', 'dispatch_date': 'first',  'supervisor_name': 'first', 'dispatched_by_id': 'first', 'issue_rised_date': 'first','shop_name':'first'}).reset_index()
        data_dict['input_part_list'] = combo_request_df.groupby('combo_issue_request').apply(lambda x:x.to_dict('r')).to_dict()
        data_dict['input_combo_list'] = combo_request_df.drop_duplicates(subset='combo_issue_request', keep='last').to_dict('r')

        data_dict['bill_number'] = new_bill_code
        input_combo_ids = list(set(list(combo_request_obj.values_list('combo_issue_request__input_combo_id', flat=True))))
        input_combo_dict = {}
        data_dict
        for input_combo in InputCombo.objects.filter(id__in=input_combo_ids):
            if not input_combo.id in input_combo_dict:
                input_combo_dict[input_combo.id] = {
                    'value': 1,
                    'unit_name': 'Nos'
                }
            if InputPart.objects.filter(input_combo_id=input_combo).count() == 1:
                input_part_obj = InputPart.objects.get(input_combo_id=input_combo)
                input_combo_dict[input_combo.id]['value'] = input_part_obj.value
                input_combo_dict[input_combo.id]['unit_name'] = input_part_obj.unit.name

        data_dict['input_combo_dict'] = input_combo_dict  

        today_date = datetime.datetime.now().date()
        file_name = str(new_bill_code) + '.pdf'
        try:
            path = os.path.join('static/media/agent_receipt/', str(agent_id), str(today_date))
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/agent_receipt/' + str(agent_id) + '/' + str(today_date) + '/',file_name)

        mycanvas = canvas.Canvas(file_path, pagesize=A4)

        # border line
        mycanvas.line(25,820,570,820)
        mycanvas.line(25,20,570,20)
        mycanvas.line(25,820,25,20)
        mycanvas.line(570,820,570,20)
        img_file = os.path.join('static/media/',"ccgb_logo.jpeg")
        mycanvas.drawInlineImage(img_file, 40, 760,(.6*inch), (.8*inch))


        # #heading part
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(325, 800,'CHENGUANG NATURAL EXTRACTS (INDIA) PVT.LTD.,')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(305, 780,'SY.No.251,Thriyambakapura Village,Terakanambi Hobali,Gundlupet Taluk,')
        mycanvas.setFont('Helvetica', 13)
        mycanvas.drawCentredString(305, 760,'Chamarajanagar District')
        mycanvas.setFont('Helvetica-Bold', 17)
        mycanvas.drawCentredString(305, 735,'AGENT PESTICIDE /FERTILIZER  ISSUE RECEIPT')


        # #actual pdf part

        #left Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(40,700,str('R.No. ')+str(data_dict['bill_number']))
        mycanvas.drawString(40,670,str('Agent Name: ')+str(data_dict['agent_name']))
        mycanvas.drawString(40,640,str('Father Name: ')+str(data_dict['father_name']))
        mycanvas.drawString(40,610,str('Supervisor Name: ')+str(data_dict['superior_name']))
        mycanvas.drawString(40,580,str('Permission department: '))
        mycanvas.drawString(40,550,str('Shop: ')+str(data_dict['shop_name']))



        #Right Side
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(350,700,str('Date: ')+str(datetime.datetime.now().date()))
        mycanvas.drawString(350,670,str('Agent Code: ')+str(data_dict['agent_code']))
        mycanvas.drawString(350,640,str('Village Name: ')+str(data_dict['village_name']))
        mycanvas.drawString(350,610,str('Cluster: ')+str(data_dict['cluster_name']))
        mycanvas.drawString(350,580,str('Out Time: '))
        mycanvas.drawString(350,550,str('Vehicle No: '))



        #Table Content
        mycanvas.setFont('Helvetica-Bold', 15)
        mycanvas.drawCentredString(305, 520,'Pesticide/Fertilizer Details')

        # #headder part
        mycanvas.line(25,500,570,500)
        mycanvas.line(25,472,570,472)

        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.drawCentredString(60, 485,'Items')
        mycanvas.drawCentredString(220, 485,'Dspt. Date')
        mycanvas.drawCentredString(350, 485,'Req.Qty')
        mycanvas.drawCentredString(440, 485,'Price')
        mycanvas.drawCentredString(520, 485,'Amount')


        y = 470
        x = 100
        total_num_of_packet = 0
        total_num_of_acre = 0
        total_price = 0
        mycanvas.setLineWidth(0)
        mycanvas.setFont('Helvetica', 10)
        supervisor_name = ''
        for input_combo in data_dict['input_combo_list']:
            length = len(data_dict['input_part_list'][input_combo['combo_issue_request']])
            length = length/2
            length = math.ceil(length)
            store_id = data_dict['input_part_list'][input_combo['combo_issue_request']][length-1]['store_id']
            for input_part in data_dict['input_part_list'][input_combo['combo_issue_request']]:
                mycanvas.setFont('Helvetica', 9)
                
                str_date = str(input_part['dispatch_date'])
                new_dt = str_date.split('00')[0]
            
                mycanvas.drawString(x+105, y-20 ,new_dt)
                mycanvas.setFont('Helvetica', 10)
                if input_part['store_id'] == store_id:
                    name = str(input_combo['input_combo_name'])
                    mycanvas.drawString(30, y-20 ,str(name))
        #             if len(name) == 1:
        #                 mycanvas.drawString(30, y-20 ,str(name[0][0:8]))
        #             else:
        #                 mycanvas.drawString(30, y-20 ,str(name[0][0:4]+" "+ str(name[1])[0:4]))
                    unit_value = data_dict['input_combo_dict'][input_combo['input_combo_id']]

                    mycanvas.drawRightString(380, y-20 ,str(input_combo['quantity_in_numbers']))
                    total_num_of_packet += input_combo['quantity_in_numbers']
                    mycanvas.drawRightString(480, y-20 ,str(input_combo['input_combo_price']))
                    
                    mycanvas.drawRightString(565, y-20 ,str(input_combo['total_price']))
                    total_price += input_combo['total_price']
                supervisor_name = input_combo['supervisor_name']
                y -= 23
            mycanvas.line(25,y-5,570,y-5)
        y -= 23

        #in_between lines
        mycanvas.line(180,500,180,y+18)
        mycanvas.line(290,500,290,y-10)
        mycanvas.line(400,500,400,y-10)
        mycanvas.line(490,500,490,y-10)

        #Total
        mycanvas.line(290,y-10,570,y-10)
        mycanvas.setFont('Helvetica-Bold', 11)
        mycanvas.drawString(300, y-3 , 'Total   :')
        mycanvas.drawRightString(380, y-3 ,str(total_num_of_packet))
        mycanvas.drawRightString(560, y-3 ,str(total_price))

        mycanvas.setFont('Helvetica', 11)
        mycanvas.drawRightString(100,  y-140, str('Remarks :'))
        bottom_signs_y_axis = y-180 


        # bottom_signs
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawRightString(130,  100, str('Agent Signature'))
        mycanvas.drawRightString(280,  100, str('Supervisor Signature'))
        mycanvas.drawRightString(410,  100, str('Issued Signature'))
        mycanvas.drawRightString(530,  100, str('GM Signature'))

        #bottom sign images
        file_name = str(data_dict['superior_name']) + '.jpeg'
        sup_file = os.path.join('static/media/signs/',file_name)
        mycanvas.drawInlineImage(sup_file, 180, 120,(1.4*inch), (.7*inch))
        gm_img_file = os.path.join('static/media/signs/',"gm.png")
        mycanvas.drawInlineImage(gm_img_file, 460, 120,(1.4*inch), (.7*inch))
        
        mycanvas.save()

        for issue_request in issue_request_ids:
            combo_issue_receipt_obj = ComboIssueAgentInventoryReceipt(combo_issue_request_id=issue_request,
                                                                    agent_id=agent_id,
                                                                    bill_number=new_bill_code,
                                                                    file=file_path)
            combo_issue_receipt_obj.save()
            combo_issue_obj = ComboIssueRequest.objects.get(id=issue_request)
            combo_issue_obj.max_status_id = 9
            combo_issue_obj.save()
        final_dict['pdf'] = encode_image_with_out_static(combo_issue_receipt_obj.file)
        final_dict['bill_number'] = combo_issue_receipt_obj.bill_number
        final_dict['status'] = True
        transaction.savepoint_commit(sid)
        return (final_dict)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return False


@api_view(['POST'])
@permission_classes((AllowAny,))
def input_combo_items_based_on_agent_code(request):
    data={}
    agent_code = request.data['agent_code']
    if ComboIssueAgentInventoryReceipt.objects.filter(agent__userprofile__code=agent_code).exists():
        combo_items=[]
        reciept_obj = ComboIssueAgentInventoryReceipt.objects.filter(agent_code=bill_number)
        for item in reciept_obj:
            temp_dict={
                'item_name':item.combo_issue_request.input_combo.name,
                'item_price':item.combo_issue_request.input_combo.price * item.combo_issue_request.quantity_in_numbers,
                'request_code':item.combo_issue_request.request_code,
                'Qty':item.combo_issue_request.quantity_in_numbers,
                'label_from':AgentInventoryStoreLabelRangeMap.objects.get(agent_inventory__combo_issue_request_id=item.combo_issue_request.id).label_range_from,
                'label_to':AgentInventoryStoreLabelRangeMap.objects.get(agent_inventory__combo_issue_request_id=item.combo_issue_request.id).label_range_to
            }
            combo_items.append(temp_dict)
            bill_dict={

                'bill_number':item.bill_number,
                'bill_date':item.combo_issue_request.issue_rised_date,
                'agent_id':item.agent_id,
                'agent_code':item.agent.userprofile.code,
                'combo_items':combo_items
            }
    return Response(data=bill_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def input_combo_items_based_on_bill_number(request):
    data={}
    bill_number = request.data['bill_number']
    if ComboIssueAgentInventoryReceipt.objects.filter(bill_number=bill_number).exists():
        combo_items=[]
        reciept_obj = ComboIssueAgentInventoryReceipt.objects.filter(bill_number=bill_number)
        for item in reciept_obj:
            temp_dict={
                'item_name':item.combo_issue_request.input_combo.name,
                'item_price':item.combo_issue_request.input_combo.price * item.combo_issue_request.quantity_in_numbers,
                'request_code':item.combo_issue_request.request_code,
                'Qty':item.combo_issue_request.quantity_in_numbers,
                'label_from':AgentInventoryStoreLabelRangeMap.objects.get(agent_inventory__combo_issue_request_id=item.combo_issue_request.id).label_range_from,
                'label_to':AgentInventoryStoreLabelRangeMap.objects.get(agent_inventory__combo_issue_request_id=item.combo_issue_request.id).label_range_to
            }
            combo_items.append(temp_dict)
            bill_dict={
                'bill_number':item.bill_number,
                'bill_date':item.combo_issue_request.issue_rised_date,
                'agent_id':item.agent_id,
                'agent_code':item.agent.userprofile.code,
                'combo_items':combo_items
            }
    return Response(data=bill_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def find_no_of_packet(label_range_from, label_range_to):
    if label_range_from != '0':
        agent_inventry_substore_obj = AgentInventoryStoreLabelRangeMap.objects.get(label_range_from=label_range_from, label_range_to=label_range_to)
        sub_issue_label_map_cout = SubStoreIssueLabelAgentMap.objects.filter(input_sub_store_inventory_id=agent_inventry_substore_obj.input_sub_store_inventory_id, agent_inventory_id=agent_inventry_substore_obj.agent_inventory_id).count()
        # combo_request_obj = ComboIssueRequest.objects.get(id=input_combo_id)
        # input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)
        # total_area = sub_issue_label_map_cout * input_combo_obj.area.quantity_in_acre
        return sub_issue_label_map_cout
    else:
        return 0



@api_view(['GET']) 
def find_qty_acre(label_range_from, label_range_to,  quantity_for_area):
    if label_range_from != '0':
        agent_inventry_substore_obj = AgentInventoryStoreLabelRangeMap.objects.get(label_range_from=label_range_from, label_range_to=label_range_to)
        sub_issue_label_map_cout = SubStoreIssueLabelAgentMap.objects.filter(input_sub_store_inventory_id=agent_inventry_substore_obj.input_sub_store_inventory_id, agent_inventory_id=agent_inventry_substore_obj.agent_inventory_id).count()
        # combo_request_obj = ComboIssueRequest.objects.get(id=input_combo_id)
        # input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)
        total_area = sub_issue_label_map_cout * quantity_for_area
        return total_area
    else:
        return 0


@api_view(["POST"])
@permission_classes((AllowAny,))
def fertilizer_agrochemicals_report_agent_wise(request):
    season_id = get_active_season_id()
    max_status_id = 8
    print('clus_id',request.data['cluster_id'])
    input_combo_ids = []
    combo_ids = InputPart.objects.filter()
    for type_id in combo_ids:
        if type_id.name.input_type_id!=1:
            input_combo_ids.append(type_id.input_combo_id)

    # issue_rised_date = request.data['issue_raised_date']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    cluster_ids = request.data['cluster_id']

    if ComboIssueRequest.objects.filter(max_status_id__gte=max_status_id, season_id=season_id, input_combo_id__in=input_combo_ids, issue_rised_date__date__range=[from_date,to_date]).exists():
        data = {}
        print('yes')
        
        combo_issue_request_obj = ComboIssueRequest.objects.filter(max_status_id__gte=max_status_id, season_id=season_id, input_combo_id__in=input_combo_ids, issue_rised_date__date__range=[from_date,to_date])
        print(combo_issue_request_obj.count())
        combo_issue_request_values = list(combo_issue_request_obj.values_list('expected_date','issue_rised_date','agentinventory__agent','agentinventory__agent__first_name','request_code','input_combo_id','input_combo__name','agentinventory__agentinventorystorelabelrangemap__label_range_from','agentinventory__agentinventorystorelabelrangemap__label_range_to','quantity_in_numbers','quantity_for_area','input_combo__price','supervisor__username','senior_supervisor__username','senior_supervisor_status__name','senior_supervisor_status_date','assitant_manager__username','assitant_manager_status__name','assitant_manager_status_date','agri_officer__username','agri_officer_status__name','agri_officer_status_date','gm__username','gm_status__name','gm_status_date','dispatch_date','dispatched_by__username'))
        column_names = ['expected_date','issue_rised_date','agent_id','agent_name','request_code','input_combo_id','input_name','label_range_from','label_to','No_of_packets','quantity_for_area','price','supervisor','senior_supervisor','senior_supervisor_status','senior_supervisor_status_date','assitant_manager','assitant_manager_status','assitant_manager_status_date','agri_officer','agri_officer_status','agri_officer_status_date','gm','gm_status','gm_status_date','dispatch_date','dispatched_by']

        excel_temp_df = pd.DataFrame(combo_issue_request_values, columns=column_names)
        excel_temp_df = excel_temp_df.fillna('0')
        excel_temp_df['count']= excel_temp_df.apply(lambda x: find_no_of_packet(x['label_range_from'],x['label_to']), axis=1)
        excel_temp_df['acre_count']= excel_temp_df.apply(lambda x: find_qty_acre(x['label_range_from'],x['label_to'],x['quantity_for_area']), axis=1)
        excel_temp_df['agent_id'] = excel_temp_df['agent_id'].astype(int)
        amount_column = excel_temp_df["count"].astype(int)*excel_temp_df["price"].astype(int)
        excel_temp_df.insert (9, 'amount', amount_column)
        agent_ids = list(combo_issue_request_obj.values_list('agentinventory__agent__id', flat=True))
        user_cluster_season_obj = UserClusterMap.objects.filter(season_id=season_id, user_id__in=agent_ids)
        # if len(request.data['cluster_id']) > 0:
        #     user_cluster_season_obj = user_cluster_season_obj.filter(user_id__in=filtered_agent_ids)
        user_cluster_season_values = list(user_cluster_season_obj.values_list('user_id','cluster_id','cluster__name'))
        columns = ['user_id','cluster_id','cluster_name']
        df = pd.DataFrame(user_cluster_season_values, columns=columns)

        user_cluster_merged_df = pd.merge( excel_temp_df, df, left_on="agent_id", right_on="user_id", how="left")
        user_cluster_merged_df['issue_rised_date'] = pd.to_datetime(user_cluster_merged_df['issue_rised_date']).dt.date
        user_cluster_merged_df['senior_supervisor_status_date'] = pd.to_datetime(user_cluster_merged_df['senior_supervisor_status_date']).dt.date
        user_cluster_merged_df['assitant_manager_status_date'] = pd.to_datetime(user_cluster_merged_df['assitant_manager_status_date']).dt.date
        user_cluster_merged_df['agri_officer_status_date'] = pd.to_datetime(user_cluster_merged_df['agri_officer_status_date']).dt.date
        user_cluster_merged_df['gm_status_date'] = pd.to_datetime(user_cluster_merged_df['gm_status_date']).dt.date
        user_cluster_merged_df['dispatch_date'] = pd.to_datetime(user_cluster_merged_df['dispatch_date']).dt.date
        user_cluster_merged_df['expected_date'] = pd.to_datetime(user_cluster_merged_df['expected_date']).dt.date

        if len(cluster_ids) > 0:
            user_cluster_merged_df = user_cluster_merged_df[user_cluster_merged_df['cluster_id'].isin(cluster_ids)]
        print('cluster_pass')
        user_cluster_merged_df= user_cluster_merged_df.drop(columns=['agent_id','cluster_id','user_id' ])
        cluster_column = user_cluster_merged_df.pop('cluster_name')
        user_cluster_merged_df.insert(12, 'cluster_name',cluster_column)

        no_of_packet = user_cluster_merged_df.pop('count')
        user_cluster_merged_df.insert(7, 'No_of_Qty',no_of_packet)

        qty_acre = user_cluster_merged_df.pop('acre_count')
        user_cluster_merged_df.insert(8, 'Qty_for_acre',qty_acre)
        
        writer = pd.ExcelWriter(str("static/media/") + "fertilizer_agrochemicals_report.xlsx", engine="xlsxwriter")
        final_df = user_cluster_merged_df

        for name in combo_issue_request_obj:
            final_df1 = final_df[final_df['input_name'] == name.input_combo.name]
            if final_df1.empty:
                continue
            # creating excel sheet with name
            if ':' in name.input_combo.name:
                mod_sheet_name = name.input_combo.name.split(':')[0]
            else:
                mod_sheet_name = str(name.input_combo.name[:30])
            final_df1.to_excel(writer, sheet_name=str(mod_sheet_name), startrow=1, index=False)

            # assigning that sheet to obj
            workbook = writer.book
            worksheet = writer.sheets[str(mod_sheet_name)]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                    }
                )
            date = datetime.datetime.today()
            # Merge 3 cells.
            worksheet.merge_range("A1:AC1", "fertilizer_agrochemicals_report" + str(date), merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 26, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df1.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        data={}
        try:
            image_path = str("static/media/") + "fertilizer_agrochemicals_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def seed_report_agent_wise(request):
    season_id = get_active_season_id()
    max_status_id = 8

    input_combo_ids=[]
    combo_ids =  InputPart.objects.filter()
    for type_id in combo_ids:
        if type_id.name.input_type_id==1:
            input_combo_ids.append(type_id.input_combo_id)

    from_date = request.data['from_date']
    to_date = request.data['to_date']
    if ComboIssueRequest.objects.filter(max_status_id__gte=max_status_id, season_id=season_id, input_combo_id__in=input_combo_ids, issue_rised_date__date__range=[from_date,to_date]).exists():
        data = {}
        combo_issue_request_obj = ComboIssueRequest.objects.filter(max_status_id__gte=max_status_id, season_id=season_id, input_combo_id__in=input_combo_ids, issue_rised_date__date__range=[from_date,to_date])
        combo_issue_request_values = list(combo_issue_request_obj.values_list('expected_date','issue_rised_date','agentinventory__agent','agentinventory__agent__first_name','request_code','input_combo__name','agentinventory__agentinventorystorelabelrangemap__label_range_from','agentinventory__agentinventorystorelabelrangemap__label_range_to','quantity_in_numbers','quantity_for_area','input_combo__price','supervisor__username','senior_supervisor__username','senior_supervisor_status__name','senior_supervisor_status_date','assitant_manager__username','assitant_manager_status__name','assitant_manager_status_date','agri_officer__username','agri_officer_status__name','agri_officer_status_date','gm__username','gm_status__name','gm_status_date','dispatch_date','dispatched_by__username'))
        column_names = ['expected_date','issue_rised_date','agent_id','agent_name','request_code','input_name','label_range_from','label_to','No_of_packets','quantity_for_area','price','supervisor','senior_supervisor','senior_supervisor_status','senior_supervisor_status_date','assitant_manager','assitant_manager_status','assitant_manager_status_date','agri_officer','agri_officer_status','agri_officer_status_date','gm','gm_status','gm_status_date','dispatch_date','dispatched_by']

        excel_temp_df = pd.DataFrame(combo_issue_request_values, columns=column_names)

        excel_temp_df = excel_temp_df.fillna('0')

        excel_temp_df['count']= excel_temp_df.apply(lambda x: find_no_of_packet(x['label_range_from'],x['label_to']), axis=1)

        excel_temp_df['acre_count']= excel_temp_df.apply(lambda x: find_qty_acre(x['label_range_from'],x['label_to'],x['quantity_for_area']), axis=1)

        excel_temp_df['agent_id'] = excel_temp_df['agent_id'].astype(int)

        amount_column = excel_temp_df["count"].astype(int)*excel_temp_df["price"].astype(int)

        excel_temp_df.insert (9, 'amount', amount_column)

        agent_ids = list(combo_issue_request_obj.values_list('agentinventory__agent__id', flat=True))
        user_cluster_season_obj = UserClusterMap.objects.filter(season_id=season_id, user_id__in=agent_ids)
        user_cluster_season_values = list(user_cluster_season_obj.values_list('user_id','cluster_id','cluster__name'))
        columns = ['user_id','cluster_id','cluster_name']
        df = pd.DataFrame(user_cluster_season_values, columns=columns)

        user_cluster_merged_df = pd.merge(excel_temp_df, df, left_on="agent_id", right_on="user_id", how="left",)  

        user_cluster_merged_df['issue_rised_date'] = pd.to_datetime(user_cluster_merged_df['issue_rised_date']).dt.date
        user_cluster_merged_df['senior_supervisor_status_date'] = pd.to_datetime(user_cluster_merged_df['senior_supervisor_status_date']).dt.date
        user_cluster_merged_df['assitant_manager_status_date'] = pd.to_datetime(user_cluster_merged_df['assitant_manager_status_date']).dt.date
        user_cluster_merged_df['agri_officer_status_date'] = pd.to_datetime(user_cluster_merged_df['agri_officer_status_date']).dt.date
        user_cluster_merged_df['gm_status_date'] = pd.to_datetime(user_cluster_merged_df['gm_status_date']).dt.date
        user_cluster_merged_df['dispatch_date'] = pd.to_datetime(user_cluster_merged_df['dispatch_date']).dt.date
        user_cluster_merged_df['expected_date'] = pd.to_datetime(user_cluster_merged_df['expected_date']).dt.date

        if len(request.data['cluster_id']) > 0:
            user_cluster_merged_df = user_cluster_merged_df[user_cluster_merged_df['cluster_id'].isin(request.data['cluster_id'])]

        user_cluster_merged_df= user_cluster_merged_df.drop(columns=['agent_id','cluster_id','user_id','input_combo_id' ])

        cluster_column = user_cluster_merged_df.pop('cluster_name')
        user_cluster_merged_df.insert(12, 'cluster_name',cluster_column)

        no_of_packet = user_cluster_merged_df.pop('count')
        user_cluster_merged_df.insert(7, 'No_of_Qty',no_of_packet)

        qty_acre = user_cluster_merged_df.pop('acre_count')
        user_cluster_merged_df.insert(8, 'Qty_for_acre',qty_acre)

        writer = pd.ExcelWriter(str("static/media/") + "seed_report_agent_wise.xlsx", engine="xlsxwriter")
        final_df = user_cluster_merged_df

        for name in combo_issue_request_obj:
            final_df1=final_df[final_df['input_name'] == name.input_combo.name]

            # creating excel sheet with name
            final_df1.to_excel(writer, sheet_name=str(name.input_combo.name), startrow=1, index=False)

            # assigning that sheet to obj
            workbook = writer.book
            worksheet = writer.sheets[str(name.input_combo.name)]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                    }
                )

            date = datetime.datetime.today()
            # Merge 3 cells.
            worksheet.merge_range("A1:AC1", "seed_report_agent_wise" + str(date), merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 28, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df1.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "seed_report_agent_wise.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False

    return Response(data=data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((AllowAny,))
def input_combo_distribution_status_report(request):
    season_id = get_active_season_id()
    max_status_id = 8
    input_combo_id = request.data['input_combo_id']
    from_date = request.data['from_date']
    to_date = request.data['to_date']

    if (ComboIssueRequest.objects.filter(season_id=season_id, input_combo_id=input_combo_id, issue_rised_date__date__range=[from_date,to_date])).exists():
        data={}
        combo_issue_request_obj = ComboIssueRequest.objects.filter(season_id=season_id, input_combo_id=input_combo_id, issue_rised_date__date__range=[from_date,to_date])
        combo_issue_request_values = list(combo_issue_request_obj.values_list('input_combo_id','max_status_id','id','expected_date','issue_rised_date','agentinventory__agent','agentinventory__agent__userprofile__code','agentinventory__agent__first_name','request_code','input_combo__name','agentinventory__agentinventorystorelabelrangemap__label_range_from','agentinventory__agentinventorystorelabelrangemap__label_range_to','input_combo__price','supervisor__username','senior_supervisor__username','senior_supervisor_status__name','senior_supervisor_status_date','assitant_manager__username','assitant_manager_status__name','assitant_manager_status_date','agri_officer__username','agri_officer_status__name','agri_officer_status_date','gm__username','gm_status__name','gm_status_date','dispatch_date','dispatched_by__username'))
        column_names = ['input_combo_id','max_status_id','id','expected_date','issue_rised_date','agent_id','agent_code','agent_name','request_code','input_name','label_range_from','label_to','price','supervisor','senior_supervisor','senior_supervisor_status','senior_supervisor_status_date','assitant_manager','assitant_manager_status','assitant_manager_status_date','agri_officer','agri_officer_status','agri_officer_status_date','gm','gm_status','gm_status_date','dispatch_date','dispatched_by']

        excel_temp_df = pd.DataFrame(combo_issue_request_values, columns=column_names)

        excel_temp_df['issue_rised_date'] = pd.to_datetime(excel_temp_df['issue_rised_date']).dt.date
        excel_temp_df['senior_supervisor_status_date'] = pd.to_datetime(excel_temp_df['senior_supervisor_status_date']).dt.date
        excel_temp_df['assitant_manager_status_date'] = pd.to_datetime(excel_temp_df['assitant_manager_status_date']).dt.date
        excel_temp_df['assitant_manager_status_date'] = pd.to_datetime(excel_temp_df['assitant_manager_status_date'] ).dt.date
        excel_temp_df['agri_officer_status_date'] = pd.to_datetime(excel_temp_df['agri_officer_status_date']).dt.date
        excel_temp_df['gm_status_date'] = pd.to_datetime(excel_temp_df['gm_status_date']).dt.date
        excel_temp_df['dispatch_date'] = pd.to_datetime(excel_temp_df['dispatch_date']).dt.date
        excel_temp_df['expected_date'] = pd.to_datetime(excel_temp_df['expected_date']).dt.date

        excel_temp_df = excel_temp_df.fillna('0')
        excel_temp_df['agent_id'] = excel_temp_df['agent_id'].astype(int)

        excel_temp_df['count']= excel_temp_df.apply(lambda x: find_no_of_packet(x['label_range_from'],x['label_to'],x['id']), axis=1)
        excel_temp_df['acre_count']= excel_temp_df.apply(lambda x: find_qty_acre(x['label_range_from'],x['label_to'],x['id']), axis=1)

        amount_column = excel_temp_df["count"].astype(int)*excel_temp_df["price"].astype(int)
        excel_temp_df.insert (13, 'amount', amount_column)
            
        agent_ids = list(combo_issue_request_obj.values_list('agentinventory__agent__id', flat=True))
        user_cluster_season_obj = UserClusterMap.objects.filter(season_id=season_id, user_id__in=agent_ids)
        user_cluster_season_values = list(user_cluster_season_obj.values_list('user_id','cluster_id','cluster__name'))
        columns = ['user_id','cluster_id','cluster_name']
        df = pd.DataFrame(user_cluster_season_values, columns=columns)

        user_cluster_merged_df = pd.merge(excel_temp_df, df, left_on="agent_id", right_on="user_id", how="left",)  

        user_cluster_merged_df = user_cluster_merged_df.fillna('0')

        user_cluster_merged_df= user_cluster_merged_df.drop(columns=['id','agent_id','cluster_id','user_id','input_combo_id' ])

        cluster_column = user_cluster_merged_df.pop('cluster_name')
        user_cluster_merged_df.insert(11, 'cluster_name',cluster_column)

        no_of_packet = user_cluster_merged_df.pop('count')
        user_cluster_merged_df.insert(9, 'No_of_Qty',no_of_packet)

        qty_acre = user_cluster_merged_df.pop('acre_count')
        user_cluster_merged_df.insert(10, 'Qty_for_acre',qty_acre)

        writer = pd.ExcelWriter(str("static/media/") + "distribution_status_report.xlsx", engine="xlsxwriter")
        final_df = user_cluster_merged_df

        for row in combo_issue_request_obj:
            if row.max_status_id< 8:
                final_df1=final_df[final_df['max_status_id'] < 8]
                
                final_df1= final_df1.drop(columns=['max_status_id' ])
                # creating excel sheet with name
                final_df1.to_excel(writer, sheet_name=str('Hold_items'), startrow=1, index=False)
                
                # assigning that sheet to obj
                workbook = writer.book
                worksheet = writer.sheets[str('Hold_items')]
                merge_format = workbook.add_format(
                    {
                        "bold": 1,
                        "border": 1,
                        "align": "center",
                        "valign": "vcenter",
                        "fg_color": "yellow",
                        }
                    )
                date = datetime.datetime.today()
                # Merge 3 cells.
                worksheet.merge_range("A1:AC1", "distribution_status_report" + str(date), merge_format)

                format1 = workbook.add_format({"num_format": "#,##0.00"})

                # Set the column width and format.
                worksheet.set_column("B:B", 18, format1)
                worksheet.set_column(0, 28, 20)

                # Add a header format.
                header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            else:
                print('greater 8')
                final_df2=final_df[final_df['max_status_id'] >= 8]
                
                final_df2= final_df2.drop(columns=['max_status_id'])
                # creating excel sheet with name
                final_df2.to_excel(writer, sheet_name=str('dispatched_items'), startrow=1, index=False)
                
                # assigning that sheet to obj
                workbook = writer.book
                worksheet = writer.sheets[str('dispatched_items')]
                merge_format = workbook.add_format(
                    {
                        "bold": 1,
                        "border": 1,
                        "align": "center",
                        "valign": "vcenter",
                        "fg_color": "yellow",
                        }
                    )
                date = datetime.datetime.today()
                # Merge 3 cells.
                worksheet.merge_range("A1:AC1", "distribution_status_report" + str(date), merge_format)

                format1 = workbook.add_format({"num_format": "#,##0.00"})

                # Set the column width and format.
                worksheet.set_column("B:B", 18, format1)
                worksheet.set_column(0, 28, 20)

                # Add a header format.
                header_format = workbook.add_format({"fg_color": "#D7E4BC"})
        writer.save()
        try:
            image_path = str("static/media/") + "distribution_status_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
    else:
        data = False

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_issue_request_quantity(request):
    print(request.data)
    # updating agent map
    ComboIssueRequestAgentMap.objects.filter(id=request.data['combo_issue_agent_map_id']).update(quantity_in_numbers=request.data['value'])
    # updating issue request total value
    input_combo_obj_id = ComboIssueRequestAgentMap.objects.get(id=request.data['combo_issue_agent_map_id']).combo_issue_request.id
    input_combo_obj = ComboIssueRequest.objects.get(id=input_combo_obj_id)
    total_qty = ComboIssueRequestAgentMap.objects.filter(combo_issue_request_id=input_combo_obj_id).aggregate(Sum('quantity_in_numbers'))['quantity_in_numbers__sum']
    print(total_qty)

    total_acre = total_qty * input_combo_obj.input_combo.area.quantity_in_acre
    ComboIssueRequest.objects.filter(id=input_combo_obj_id).update(
        quantity_in_numbers=total_qty,
        quantity_for_area=total_acre
    )
    print('success')
    return Response(data='data', status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_bank_detail_with_ifsc_code(request):
    if Bank.objects.filter(ifsc_code__iexact=request.data['ifsc_code']).exists():
        bank_obj = Bank.objects.get(ifsc_code__iexact=request.data['ifsc_code'])
        data_dict = {
            'bank': bank_obj.name,
            'branch': bank_obj.branch,
            'ifsc_code': bank_obj.ifsc_code,
            'micr_code': bank_obj.micr_code,
        }
    else:
        data_dict = False
    return Response(data=data_dict, status=status.HTTP_200_OK)


def send_notification(title, message, user_ids):
    for user_id in user_ids:
        try:
            FCMDevice.objects.get(user_id=user_id).send_message(title=title, body=message)
            print('send')
        except Exception as err:
            print(err)


@api_view(['GET'])
def serve_return_products(request):
    season_id = get_active_season_id()
    combo_list = list(ReturnableComboItems.objects.filter(season_id=season_id).order_by('id').values_list('input_combo_id','input_combo__name','input_combo__area'))
    combo_columns = ['id','name','quantity_in_acre']
    combo_df = pd.DataFrame(combo_list,columns=combo_columns)
    data = combo_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_agents_under_senior_supervisor_for_active_season(request):
    user_id = request.user.id
    season_id = get_active_season_id()
    subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
    subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
    agent_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
    agent_list = list(UserClusterMap.objects.filter(user_id__in=agent_ids, season_id=season_id).values_list('user_id','user__first_name','user__last_name','user__userprofile__code', 'cluster_id', 'cluster__name'))
    agent_col = ['agent_id','first_name','last_name','agent_code', 'cluster_id', 'cluster_name']
    agent_df = pd.DataFrame(agent_list, columns=agent_col)
    data = agent_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


def generate_return_code(input_combo_id):
    code_bank_obj = ComboReturnRequestCodeBank.objects.filter(input_combo_id=input_combo_id)[0]
    last_digit_code = code_bank_obj.last_digit
    new_code = last_digit_code + 1
    value = str('RTN_') + str(code_bank_obj.input_combo.name) + str(new_code).zfill(3)
    code_bank_obj.last_digit = new_code
    code_bank_obj.save()
    return value


@api_view(['POST'])
@transaction.atomic
def save_return_request(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        season_id = get_active_season_id()
        ComboReturnRequest.objects.create(
            season_id=season_id,
            agent_id=request.data['agent_id'],
            request_code=generate_return_code(request.data['combo_id']),
            input_combo_id=request.data['combo_id'],
            request_raised_date=request.data['requested_date'],
            max_status_id=1,
            max_status_date=request.data['requested_date'],
            senior_supervisor_id=request.user.id,
            senior_supervisor_remarks=request.data['remarks'],
        )
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def serve_return_request_log(request):
    combo_return_obj = ComboReturnRequest.objects.filter(season_id=get_active_season_id())
    combo_list = list(combo_return_obj.values_list('id', 'season_id', 'agent_id', 'agent__first_name', 'agent__userprofile__code', 'request_code', 'input_combo__id', 'input_combo__name', 'request_raised_date', 
                                                'max_status_id', 'max_status__name', 'senior_supervisor_id', 'senior_supervisor__username', 'senior_supervisor_remarks', 'assitant_manager_id', 'assitant_manager__username',
                                                'assitant_manager_status_id','assitant_manager_status__name', 'assitant_manager_remarks', 'assitant_manager_status_date', 'agri_officer__id','agri_officer__username', 'agri_officer_remarks',
                                                'agri_officer_status_id', 'agri_officer_status_date'))
    combo_columns = ['combo_return_request_id', 'season_id', 'agent_id', 'agent_first_name', 'agent_code', 'request_code', 'input_combo_id', 'input_combo_name', 'request_raised_date', 
                                                'max_status_id', 'max_status_name', 'senior_supervisor_id', 'senior_supervisor_username', 'senior_supervisor_remarks', 'assitant_manager_id', 'assitant_manager_username',
                                                'assitant_manager_status_id','assitant_manager_status_name', 'assitant_manager_remarks', 'assitant_manager_status_date', 'agri_officer__id','agri_officer__username', 'agri_officer_remarks',
                                                'agri_officer_status_id', 'agri_officer_status_date']
    combo_request_df = pd.DataFrame(combo_list, columns=combo_columns)
    combo_request_df = combo_request_df.fillna(0)
    data =  combo_request_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_return_request_response(request):
    print(request.data)
    combo_obj = ComboReturnRequest.objects.get(id=request.data['combo_return_request_id'])
    print(combo_obj.max_status_id)
    if combo_obj.max_status_id == 1:
        if UserProfile.objects.get(user_id=request.user.id).user_type_id == 2:
            if request.data['option'] == 1:
                combo_obj.max_status_id = 2
                combo_obj.max_status_date = datetime.datetime.now()
                combo_obj.assitant_manager_status_id = 1
            else:
                combo_obj.max_status_id = 4
                combo_obj.max_status_date = datetime.datetime.now()
                combo_obj.assitant_manager_status_id = 2
            combo_obj.assitant_manager_id = request.user.id
            combo_obj.assitant_manager_status_date = datetime.datetime.now()
            combo_obj.assitant_manager_remarks = request.data['remarks']
            combo_obj.save()
    elif combo_obj.max_status_id == 2:
        if UserProfile.objects.get(user_id=request.user.id).user_type_id == 4:
            if request.data['option'] == 1:
                combo_obj.max_status_id = 3
                combo_obj.max_status_date = datetime.datetime.now()
                combo_obj.agri_officer_status_id = 1
            else:
                combo_obj.max_status_id = 4
                combo_obj.max_status_date = datetime.datetime.now()
                combo_obj.agri_officer_status_id = 2

            combo_obj.agri_officer_id = request.user.id
            combo_obj.agri_officer_status_date = datetime.datetime.now()
            combo_obj.agri_officer_remarks = request.data['remarks']
            combo_obj.save()

    return Response(status=status.HTTP_200_OK)



@api_view(['GET'])
def serve_return_approved_agent_list(request):
    combo_return_request_obj = ComboReturnRequest.objects.filter(max_status_id__in=[1,2], season_id=get_active_season_id()).order_by('request_code')
    print(combo_return_request_obj.count())
    combo_return_request_list = list(combo_return_request_obj.values_list('id', 'agent','agent__first_name', 'agent__last_name', 'agent__userprofile__code', 'max_status_id', 'max_status__name', 'senior_supervisor__username', 'request_raised_date', 'senior_supervisor_remarks', 'assitant_manager__username', 'assitant_manager_status_date', 'assitant_manager_remarks', 'assitant_manager_status_id', 'request_code', 'input_combo', 'input_combo__name'))
    combo_return_request_column = ['combo_return_id', 'agent_id', 'agent_first_name', 'agent_last_name', 'agent_code', 'max_status_id', 'max_status_name', 'raised_by', 'raised_on', 'remarks', 'assistant_manager_name', 'assistant_manager_raised_on', 'assistant_manager_remarks', 'assistant_manager_status_id', 'return_request_code', 'input_combo_id', 'input_combo_name']
    combo_return_request_df = pd.DataFrame(combo_return_request_list, columns=combo_return_request_column)
    combo_return_request_df = combo_return_request_df.fillna(0)
    combo_return_request = combo_return_request_df.to_dict('r')
    return Response(data=combo_return_request, status=status.HTTP_200_OK)


@api_view(['POST'])
def  serve_bill_based_label_and_sub_store(request):
    print(request.data)
    combo_return_obj = ComboReturnRequest.objects.get(id=request.data['combo_return_id'])
    combo_receipt_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__input_combo_id=combo_return_obj.input_combo_id, agent_id=combo_return_obj.agent.id).order_by('-id')
    combo_receipt_list = list(combo_receipt_obj.values_list('id', 'bill_number', 'time_created', 'combo_issue_request'))
    combo_receipt_column = ['bill_id', 'bill_number', 'bill_date', 'combo_issue_request_id']
    combo_receipt_df = pd.DataFrame(combo_receipt_list, columns=combo_receipt_column)
    print(combo_receipt_df.shape)
    combo_issue_ids = list(combo_receipt_obj.values_list('combo_issue_request', flat=True))

    sub_store_label_obj = SubStoreIssueLabelAgentMap.objects.filter(combo_issue_request_agent_map__combo_issue_request__in=combo_issue_ids, agent_id=combo_return_obj.agent.id, status_id=1).order_by('label')
    sub_store_label_list = list(sub_store_label_obj.values_list('id', 'label', 'combo_issue_request_agent_map__combo_issue_request'))
    sub_store_label_column = ['label_id', 'label', 'combo_issue_request_id']
    sub_store_label_df = pd.DataFrame(sub_store_label_list, columns=sub_store_label_column)
    print(sub_store_label_df.shape)
    if not sub_store_label_df.empty:
        bill_label_merge_df = pd.merge(combo_receipt_df, sub_store_label_df, how='left', left_on='combo_issue_request_id', right_on='combo_issue_request_id')
        bill_label_merge_df['is_dispatchable'] = True
        bill_label_merge_df['combo_remarks'] = ''
        bill_label_merge_grouped_dict = bill_label_merge_df.groupby('bill_number').apply(lambda x:x.to_dict('r')).to_dict()
    else:
        bill_label_merge_grouped_dict = {}

    active_season = get_active_season_id()
    if InputSubStoreInventory.objects.filter(input_store_inventory__input_packet_inventory__input_combo_id=combo_return_obj.input_combo_id, season_id=active_season).exists():
        sub_store_inventory_obj = InputSubStoreInventory.objects.filter(input_store_inventory__input_packet_inventory__input_combo_id=combo_return_obj.input_combo_id, quantity_now__gt=0, season_id=active_season)
        if sub_store_inventory_obj.count() == 0:
            sub_store_inventory_obj = InputSubStoreInventory.objects.filter(input_store_inventory__input_packet_inventory__input_combo_id=combo_return_obj.input_combo_id, season_id=active_season).order_by('-id')[:1]
        sub_store_inventory_list = list(sub_store_inventory_obj.values_list('id', 'quantity_now', 'label_range_start', 'label_range_end', 'section', 'sub_section', 'time_created'))
        sub_store_inventory_column = ['sub_store_id', 'quantity_now', 'label_from', 'label_to', 'section', 'sub_section', 'created_time']
        sub_store_inventory_df = pd.DataFrame(sub_store_inventory_list, columns=sub_store_inventory_column)
        sub_store_inventory_df = sub_store_inventory_df.fillna(0).to_dict('r')
    else:
        sub_store_inventory_df = []
    data_dict = {
        'bill_number_list': combo_receipt_df.to_dict('r'),
        'label_list_based_on_bill': bill_label_merge_grouped_dict,
        'sub_store_list': sub_store_inventory_df
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


# @transaction.atomic
@api_view(['POST'])
def retun_label_to_sub_store_inventory(request):
    # sid = transaction.savepoint()
    # try:
    combo_return_obj = ComboReturnRequest.objects.get(id=request.data['combo_return_id'])
    combo_return_obj.agri_officer_id = request.user.id
    combo_return_obj.agri_officer_status_id = 1 #acceped
    combo_return_obj.agri_officer_status_date = datetime.datetime.now()
    combo_return_obj.max_status_id = 3 #agri officer issued
    combo_return_obj.max_status_date = datetime.datetime.now()
    combo_return_obj.save()

    for label in request.data['label_list']:
        print('label:', label)
        substore_id = request.data['sub_store_id']
        print('substore_id:',substore_id)
        combo_return_request_label_obj = ComboReturnRequestLabelMap(combo_return_request_id=request.data['combo_return_id'],
                                                                    is_dispatchable=label['is_dispatchable'],
                                                                    combo_remarks=label['combo_remarks'],
                                                                    date_of_return=datetime.datetime.now(),
                                                                    return_label_id=label['label_id'],
                                                                    return_sub_store_inventory_id=substore_id
                                                                    )
        combo_return_request_label_obj.save()
        print('ComboReturnRequestLabelMap_Saved')

        sub_store_label_agent_map_obj = SubStoreIssueLabelAgentMap.objects.get(id=label['label_id'])
        sub_store_label_agent_map_obj.status_id = 2 #returned
        sub_store_label_agent_map_obj.save()
        print('sub_store_label_agent_map_obj_saved')

        input_sub_store_packet_label_obj = InputSubStoreInventoryPacketLabel(input_sub_store_inventory_id=request.data['sub_store_id'],
                                                                            label=sub_store_label_agent_map_obj.label,
                                                                            stock_status_id=3, #at_storage
                                                                            received_date=datetime.datetime.now(),
                                                                            received_by_id=request.user.id,
                                                                            )
        input_sub_store_packet_label_obj.save()
        print('input_sub_store_packet_label_obj_saved')

        input_sub_store_obj = InputSubStoreInventory.objects.get(id=request.data['sub_store_id'])
        input_sub_store_obj.quantity_now = input_sub_store_obj.quantity_now + 1
        input_sub_store_obj.quantity_now_time = datetime.datetime.now()
        input_sub_store_obj.save()
        print('input_sub_store_saved')
        print('id=', combo_return_obj.id)
    agent_return_transaction_log(combo_return_obj.id, combo_return_obj.agri_officer_id)     
    # transaction.savepoint_commit(sid)
    return Response(status=status.HTTP_200_OK)
    # except Exception as e:
        # print('error on {}'.format(e))
        # transaction.savepoint_rollback(sid)
        # return Response(status=status.HTTP_404_NOT_FOUND)


# @api_view(['GET'])
# def find_no_of_packet(label_range_from, label_range_to, input_combo_id):
#     if label_range_from != '0':
#         agent_inventry_substore_obj = AgentInventoryStoreLabelRangeMap.objects.get(label_range_from=label_range_from, label_range_to=label_range_to)
#         sub_issue_label_map_cout = SubStoreIssueLabelAgentMap.objects.filter(input_sub_store_inventory_id=agent_inventry_substore_obj.input_sub_store_inventory_id, agent_inventory_id=agent_inventry_substore_obj.agent_inventory_id).count()
#         combo_request_obj = ComboIssueRequest.objects.get(id=input_combo_id)
#         input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)
#         total_area = sub_issue_label_map_cout * input_combo_obj.area.quantity_in_acre
#         return sub_issue_label_map_cout
#     else:
#         return 0


# @api_view(['GET']) 
# def find_qty_acre(label_range_from, label_range_to, input_combo_id):
#     if label_range_from != '0':
#         agent_inventry_substore_obj = AgentInventoryStoreLabelRangeMap.objects.get(label_range_from=label_range_from, label_range_to=label_range_to)
#         sub_issue_label_map_cout = SubStoreIssueLabelAgentMap.objects.filter(input_sub_store_inventory_id=agent_inventry_substore_obj.input_sub_store_inventory_id, agent_inventory_id=agent_inventry_substore_obj.agent_inventory_id).count()
#         combo_request_obj = ComboIssueRequest.objects.get(id=input_combo_id)
#         input_combo_obj = InputCombo.objects.get(id=combo_request_obj.input_combo.id)
#         total_area = sub_issue_label_map_cout * input_combo_obj.area.quantity_in_acre
#         return total_area
#     else:
#         return 0


@api_view(['POST'])
@permission_classes((AllowAny,))
def combo_item_based_labels(request):
    print(request.data['farmer_id'])
    farmer_id = request.data['farmer_id']
    season_id = get_active_season_id()

    farmer_agent_obj_id = AgentFarmerMap.objects.get(farmer__farmer_id=farmer_id, farmer__season_id=season_id).agent.id
    agentinventry_obj_id = AgentInventory.objects.filter(season_id=season_id, agent_id=farmer_agent_obj_id)
    label_dict={}
    combo_item=[]
    master_dict={}
    data={}
    for item in agentinventry_obj_id:
        temp_dict={
            'id':item.combo_issue_request.input_combo.id,
            'name':item.combo_issue_request.input_combo.name
        }
        combo_item.append(temp_dict)
        master_dict['combo_list']=combo_item

        sub_store_issue_label_agent_map = SubStoreIssueLabelAgentMap.objects.filter(agent_inventory_id=item.id, status_id=1)
        if not item.id in label_dict:
            label_dict[item.combo_issue_request.input_combo.id] =[]
        for label_name in sub_store_issue_label_agent_map:
            label_range={
                'id':label_name.id,
                'label':label_name.label
            }
            label_dict[item.combo_issue_request.input_combo.id].append(label_range)
        master_dict['label_list']=label_dict
    master_dict['combo_list'] = [dict(t) for t in {tuple(d.items()) for d in master_dict['combo_list']}]
    master_dict['agent_id'] = farmer_agent_obj_id

    return Response(data= master_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_agent_farmer_distribution(request):
    data_dict = request.data
    season_id = get_active_season_id()
    if data_dict['type'] != 'seed':
        agent_farmer_distribution_sowing_obj = AgentFarmerDistributionSowing(
                                                    season_id = season_id,
                                                    sowing_id = data_dict['sowing_id'],
                                                    agent_id = data_dict['agent_id'],
                                                    input_combo_id = data_dict['input_combo_id'],
                                                    no_of_unit = data_dict['quantity'],
                                                    acre = InputCombo.objects.get(id=data_dict['input_combo_id']).area.quantity_in_acre * data_dict['quantity'],
                                                    dispatched_date = data_dict['date']
                                                )
        agent_farmer_distribution_sowing_obj.save()
    else:
        for label in data_dict['label_list']:
            if not AgentFarmerDistributionMap.objects.filter(label_id=label['id']).exists():
                if not AgentFarmerDistributionSowing.objects.filter(season_id = season_id, sowing_id = data_dict['sowing_id'], agent_id = data_dict['agent_id'],input_combo_id = data_dict['input_combo_id']).exists():
                    agent_farmer_distribution_sowing_obj = AgentFarmerDistributionSowing(
                                                                    season_id = season_id,
                                                                    sowing_id = data_dict['sowing_id'],
                                                                    agent_id = data_dict['agent_id'],
                                                                    input_combo_id = data_dict['input_combo_id'],
                                                                    no_of_unit = 1,
                                                                    acre = InputCombo.objects.get(id=data_dict['input_combo_id']).area.quantity_in_acre * 1,
                                                                    dispatched_date = data_dict['date']
                                                            )
                    agent_farmer_distribution_sowing_obj.save()
                
                    agent_farmer_distribution_obj = AgentFarmerDistributionMap(
                                                    agent_farmer_distribution_sowing_id = agent_farmer_distribution_sowing_obj.id,
                                                    label_id = label['id'],
                                                    created_by_id = request.user.id,
                                                    modified_by_id = request.user.id)
                    agent_farmer_distribution_obj.save()
                    
                    sub_store_label_agent_map_obj = SubStoreIssueLabelAgentMap.objects.get(agent_id=data_dict['agent_id'], id=label['id'], label=label['label'])
                    sub_store_label_agent_map_obj.status_id = 3
                    sub_store_label_agent_map_obj.save()
                    print('saved')
                else:
                    agent_farmer_distribution_sowing_obj = AgentFarmerDistributionSowing.objects.get(season_id = season_id, sowing_id = data_dict['sowing_id'], agent_id = data_dict['agent_id'],input_combo_id = data_dict['input_combo_id'])
                    agent_farmer_distribution_obj = AgentFarmerDistributionMap(
                                                    agent_farmer_distribution_sowing_id = AgentFarmerDistributionSowing.objects.get(season_id = season_id, sowing_id = data_dict['sowing_id'], agent_id = data_dict['agent_id'],input_combo_id = data_dict['input_combo_id']).id,
                                                    label_id = label['id'],
                                                    created_by_id = request.user.id,
                                                    modified_by_id = request.user.id)
                    agent_farmer_distribution_obj.save()
                    
                    sub_store_label_agent_map_obj = SubStoreIssueLabelAgentMap.objects.get(agent_id=data_dict['agent_id'], id=label['id'], label=label['label'])
                    sub_store_label_agent_map_obj.status_id = 3
                    sub_store_label_agent_map_obj.save()
                    no_of_unit_var = Decimal(agent_farmer_distribution_sowing_obj.no_of_unit)
                    
                    updated_no_of_unit = no_of_unit_var + 1
                    updated_acre = updated_no_of_unit * InputCombo.objects.get(id=data_dict['input_combo_id']).area.quantity_in_acre

                    agent_farmer_distribution_sowing_obj.no_of_unit = updated_no_of_unit
                    agent_farmer_distribution_sowing_obj.acre = updated_acre
                    agent_farmer_distribution_sowing_obj.save()
    return Response(status=status.HTTP_200_OK)


def get_input_combo_id(input_id):
    counts=InputPart.objects.filter(input_combo_id=input_id).count()
    print(counts)
    if counts == 1:
        type_id=InputPart.objects.get(input_combo_id=input_id).name.input_type.id

        if type_id == 1:
            types =  True
        else:
            types =  False
    else:
        types =  False
    return types


@api_view(['POST'])
def serve_farmer_distribution(request):
    data_dict = []
    if AgentFarmerDistributionSowing.objects.filter(season_id=get_active_season_id(), sowing_id=request.data['sowing_id']).exists():
        for entry in AgentFarmerDistributionSowing.objects.filter(season_id=get_active_season_id(), sowing_id=request.data['sowing_id']):
            data = {}
            data['agent_name'] = str(entry.agent.first_name) + ' ' +(entry.agent.last_name) 
            data['input_combo'] = str(entry.input_combo.name)
            data['number_of_units'] = entry.no_of_unit
            data['acre'] = entry.acre
            data['dispatched_date'] = entry.dispatched_date
            if get_input_combo_id(entry.input_combo.id):
                data['is_seed'] = True
                data['label_list'] = list(AgentFarmerDistributionMap.objects.filter(agent_farmer_distribution_sowing_id=entry.id).values_list('label__label'))
            else:
                data['is_seed'] = False       
            data_dict.append(data)
    else:
        data_dict = False
    return Response(data_dict, status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes((AllowAny,))
def input_combo_item_remining_report(request):
    season_id = get_active_season_id()
    issue_label_agent_map_obj = SubStoreIssueLabelAgentMap.objects.filter(agent_inventory__combo_issue_request__season_id=season_id)
    issue_label_agent_map_values = list(issue_label_agent_map_obj.values_list('agent_id','agent__first_name', 'combo_issue_request_agent_map__combo_issue_request__input_combo__id','combo_issue_request_agent_map__combo_issue_request__input_combo__name', 'combo_issue_request_agent_map__quantity_in_numbers','status_id', 'status__name'))
    column_names = ['agent_id','agent_name','input_combo_id', 'input_name', 'no_of_qty', 'status_id','status_name']
    df = pd.DataFrame(issue_label_agent_map_values, columns=column_names)

    df['remining_qty'] = df.apply(lambda x: to_find_remining_qty(x['agent_id'], x['input_combo_id']), axis=1)
    df['dispatched_to_farmer_count'] = df.apply(lambda x: dispatched_to_farmer_count(x['agent_id'], x['input_combo_id']), axis=1)
    df1 = df.drop_duplicates(subset=['agent_name', 'input_name', 'no_of_qty'])

    df2= df1.drop(columns=['agent_id','input_combo_id','status_id'])
    writer = pd.ExcelWriter(str("static/media/") + "input_item_remining_report.xlsx", engine="xlsxwriter")
    final_df = df2

    data={}
    # creating excel sheet with name
    for name in issue_label_agent_map_obj:
        final_df1 = final_df[final_df['input_name'] == name.agent_inventory.combo_issue_request.input_combo.name]
        if final_df1.empty:
            continue
        # creating excel sheet with name
        if ':' in name.agent_inventory.combo_issue_request.input_combo.name:
            mod_sheet_name = name.agent_inventory.combo_issue_request.input_combo.name.split(':')[0]
        else:
            mod_sheet_name = str(name.agent_inventory.combo_issue_request.input_combo.name[:30])
        final_df1.to_excel(writer, sheet_name=str(mod_sheet_name), startrow=1, index=False)
        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets[str(mod_sheet_name)]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
                }
            )
        date = datetime.datetime.today()
        # Merge 3 cells.
        worksheet.merge_range("A1:AC1", "input_item_remining_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 28, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df1.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "input_item_remining_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print('Error',err)
    return Response(data=data , status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def to_find_remining_qty(agent_id, input_combo_id):
    remining_qty = SubStoreIssueLabelAgentMap.objects.filter(agent_inventory__combo_issue_request__input_combo__id=input_combo_id, agent_id=agent_id, status_id=1).count()
    return remining_qty

@api_view(['GET'])
def dispatched_to_farmer_count(agent_id, input_combo_id):
    dispatched_farmer_count = SubStoreIssueLabelAgentMap.objects.filter(agent_inventory__combo_issue_request__input_combo__id=input_combo_id, agent_id=agent_id, status_id=3).count()
    return dispatched_farmer_count



# @api_view(['POST'])
# @permission_classes((AllowAny,))
# def agent_price_clusterwise(request):
#     cluster_ids=request.data['cluster_ids']
#     agent_distribution_price_obj = list(set(AgentDistributionPrice.objects.filter(agent__userclustermap__cluster_id__in=cluster_ids, season_id=get_active_season_id()).values_list('agent__userprofile__code','agent_id','agent__first_name', 'price')))
#     df = pd.DataFrame(agent_distribution_price_obj, columns=['agent_code','agent_id','agent_name', 'price'])
#     df['is_editable'] = False
#     df.to_dict('r')
#     data_dict = df.to_dict('r')
#     return Response(data_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def agent_price_clusterwise(request):
    cluster_ids = request.data['cluster_ids']
    agent_ids = list(UserClusterMap.objects.filter(season_id=get_active_season_id(), cluster_id__in=cluster_ids).values_list('user_id', flat=True))
    agent_distribution_price_obj = list(set(AgentDistributionPrice.objects.filter(agent_id__in=agent_ids, season_id=get_active_season_id()).values_list('agent__userprofile__code','agent_id','agent__first_name', 'price')))
    df = pd.DataFrame(agent_distribution_price_obj, columns=['agent_code','agent_id','agent_name', 'price'])
    df['is_editable'] = False
    df.to_dict('r')
    data_dict = df.to_dict('r')
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def agent_wallet_clusterwise(request):
    cluster_ids=request.data['cluster_ids']
    agent_wallet_obj = list(set(AgentWallet.objects.filter(agent__userclustermap__cluster_id__in=cluster_ids, agent__userclustermap__season_id=get_active_season_id()).values_list('agent__userprofile__code','agent_id','agent__first_name', 'current_balance')))
    df = pd.DataFrame(agent_wallet_obj, columns=['agent_code','agent_id','agent_name', 'cturrent_balance'])
    data_dict = df.to_dict('r')
    return Response(data_dict, status=status.HTTP_200_OK)


def generate_request_code_for_price_change():
    code_bank_obj = DistributionPriceChangeRequestCodeBank.objects.all()[0]
    last_digit_code = code_bank_obj.last_digit
    new_code = last_digit_code + 1
    value = str('DPCR') + '_' + str(new_code).zfill(3)
    code_bank_obj.last_digit = new_code
    code_bank_obj.save()
    return value


@api_view(['POST'])
@permission_classes((AllowAny,))
def request_agent_price_change(request):
    data_dict = request.data['agent_price_update_list']

    agent_distribution_price_change_request_obj = AgentDistributionPriceChangeRequest(request_code=generate_request_code_for_price_change(),
                                                                                 requested_by_id=request.user.id,
                                                                                 requested_on=datetime.datetime.today(),
                                                                                 status_id = 1)
    agent_distribution_price_change_request_obj.save()        

    for entry in data_dict:
        distribution_price_change_agent_map_obj = DistributionPriceChangeAgentMap(agent_price_change_request_id=agent_distribution_price_change_request_obj.id,
                                                                                agent_id=entry['agent_id'],
                                                                                price=entry['price'])
        distribution_price_change_agent_map_obj.save()

    return Response(data=True, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_request_list_for_agent_price_change(request):
    distribution_price_change_agent_map_obj = DistributionPriceChangeAgentMap.objects.filter(agent_price_change_request__status_id=1)
    distribution_price_change_agent_map_values = list(distribution_price_change_agent_map_obj.values_list('agent_price_change_request_id', 'agent_price_change_request__request_code', 'agent_price_change_request__requested_on', 'agent_price_change_request__requested_by__first_name', 'agent__userprofile__code','agent_id','agent__first_name', 'price', 'agent__agentdistributionprice__price'))
    column_names = ['request_id','request_code','requested_date', 'requested_by', 'agent_code', 'agent_id', 'agent_name', 'price', 'old_price']
    frame = pd.DataFrame(distribution_price_change_agent_map_values, columns=column_names)
    request_id_dict = frame.groupby('request_id').apply(lambda x:x.to_dict('r')).to_dict()
    return Response(data=request_id_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def register_agent_price_log(request):
    if request.data['status_id'] == 2:
        season_id=get_active_season_id()
        AgentDistributionPriceChangeRequest.objects.filter(id=request.data['request_id']).update(approved_by_id=request.user.id, status_date=datetime.datetime.today(), status_id=2)
        
        agent_lists = list(DistributionPriceChangeAgentMap.objects.filter(agent_price_change_request_id=request.data['request_id']).values_list('agent_id', flat=True))

        for agent in agent_lists:
            agent_price_change_log_obj = AgentDistributionPriceChangeLog(agent_id=agent,
                                                                        price=AgentDistributionPrice.objects.get(agent_id=agent).price,
                                                                        from_date = AgentDistributionPrice.objects.get(agent_id=agent).updated_on,
                                                                        to_date = datetime.datetime.today())
            agent_price_change_log_obj.save()
            AgentDistributionPrice.objects.filter(agent_id=agent).update(price=DistributionPriceChangeAgentMap.objects.get(agent_id=agent,agent_price_change_request_id=request.data['request_id']).price, updated_on=datetime.datetime.today(), season_id=season_id)
    else:
        AgentDistributionPriceChangeRequest.objects.filter(id=request.data['request_id']).update(approved_by_id=request.user.id, status_date=datetime.datetime.today(), status_id=3)
    return Response(data=True, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def distribution_price_log_agent_wise(request):
    season_id=get_active_season_id()
    price_change_list = list(AgentDistributionPriceChangeLog.objects.filter(agent__userclustermap__season_id=season_id).values_list('agent__first_name', 'agent__last_name', 'agent__userprofile__code', 'from_date', 'to_date', 'price', 'agent__agentdistributionprice__price', 'agent__userclustermap__cluster__name'))
    price_change_column = ['first_name', 'last_name', 'agent_code', 'from_date', 'to_date', 'price', 'current_price','cluster_name']
    price_change_df = pd.DataFrame(price_change_list, columns=price_change_column)
    price_change_log_dict = price_change_df.groupby('agent_code').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=price_change_log_dict, status=status.HTTP_200_OK)

#season_clusterwise agents
@api_view(['GET'])
@permission_classes((AllowAny,))
def season_clusterwise_agents(request):
    temp_dict={}
    usercluster_obj = UserClusterMap.objects.filter(user__userprofile__user_type_id=6)
    for item in usercluster_obj:
        if not item.season_id in temp_dict:
            temp_dict[item.season_id]={}
        if not item.cluster_id in temp_dict[item.season_id]:
            temp_dict[item.season_id][item.cluster_id]=[]
        agent_dict={'agent_id':item.user.id,
                    'first_name':item.user.first_name,
                    'last_name':item.user.last_name
                    }
        temp_dict[item.season_id][item.cluster_id].append(agent_dict)
    return Response(data=temp_dict, status=status.HTTP_200_OK)

#season_wise agents
@api_view(['GET'])
@permission_classes((AllowAny,))
def season_wise_agents(request):
    data_dict = {}
    usercluster_obj = list(UserClusterMap.objects.filter(user__userprofile__user_type_id=6).values_list('season_id', 'user_id', 'user__first_name', 'user__last_name'))
    column_names = ['season_id', 'agent_id', 'first_name', 'last_name']
    agent_df = pd.DataFrame(usercluster_obj, columns=column_names)
    agent_dict_seasonwise = agent_df.groupby('season_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict['season_list'] = list(Season.objects.all().values('id', 'name'))
    data_dict['current_season'] = get_active_season_id()
    data_dict['season_wise_agent'] = agent_dict_seasonwise
    return Response(data=data_dict, status=status.HTTP_200_OK)    


@api_view(['GET'])
@permission_classes((AllowAny,))
def season_wise_clusters(request):
    season_cluster_obj = ClusterSeasonMap.objects.filter().values_list('season_id', 'cluster_id', 'cluster__name')
    column_names = ['season_id', 'cluster_id', 'cluster_name']
    df = pd.DataFrame(season_cluster_obj, columns=column_names)
    season_cluster_dict = df.groupby('season_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=season_cluster_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def input_item_report_agent_wise(request):
    # agent_inventry_obj = list(AgentInventory.objects.filter(season_id=get_active_season_id()).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))      
    # agent_inventry_column = ['agent_id', 'agent_name', 'input_combo_id', 'quantity',  'input_combo_name']
    # agent_inventry_df = pd.DataFrame(agent_inventry_obj, columns=agent_inventry_column)
    # agent_inventry_df = agent_inventry_df.groupby(['agent_id', 'input_combo_id']).agg({'agent_name': 'first', 'quantity': sum, 'input_combo_name': 'first'}).reset_index()
    # agent_inventry_df = agent_inventry_df.drop(columns=['input_combo_id']) 

    # #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    # final_df = pd.pivot_table(agent_inventry_df, index=['agent_id','agent_name'] , columns='input_combo_name', aggfunc=min, fill_value=0)

    # #convert_pivot_table_to_normal_df
    # final_df.columns = final_df.columns.droplevel(0) #remove amount
    # final_df.columns.name = None  #remove categories

    # final_df = final_df.reset_index() #index to columns
    # final_df1 = final_df.drop(columns=['agent_id'])

    # columns_to_sum = final_df1.columns[ : final_df1.shape[1]]
    # final_df1['Total'] = final_df1[columns_to_sum].sum(axis=1)
    combo_issue_request_agentmap_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=get_active_season_id(), combo_issue_request__max_status_id__in=[8,9], shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))
    combo_issue_request_agentmap_column = ['agent_id', 'Agent Name', 'input_combo_id', 'quantity',  'input_combo_name']
    combo_issue_request_agentmap_df = pd.DataFrame(combo_issue_request_agentmap_obj, columns=combo_issue_request_agentmap_column)

    combo_issue_request_othershop_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=get_active_season_id(), combo_issue_request__max_status_id=6).exclude(shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))
    column_names = ['agent_id', 'Agent Name', 'input_combo_id', 'quantity',  'input_combo_name']
    combo_issue_request_othershop_obj_df = pd.DataFrame(combo_issue_request_othershop_obj, columns=column_names)

    merge_df = pd.concat([combo_issue_request_agentmap_df, combo_issue_request_othershop_obj_df])
    merge_df1 = merge_df.groupby(['agent_id', 'input_combo_id']).agg({'Agent Name': 'first', 'quantity': sum, 'input_combo_name': 'first'}).reset_index()
    merge_df1 = merge_df1.drop(columns=['input_combo_id']) 
    final_df = merge_df1

    #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    final_df = pd.pivot_table(merge_df1, index=['agent_id','Agent Name'] , columns='input_combo_name', aggfunc=min, fill_value=0)

    #convert_pivot_table_to_normal_df
    final_df.columns = final_df.columns.droplevel(0) #remove amount
    final_df.columns.name = None  #remove categories

    final_df = final_df.reset_index() #index to columns
    final_df1 = final_df.drop(columns=['agent_id'])

    columns_to_sum = final_df1.columns[ : final_df1.shape[1]]
    final_df1['Total'] = final_df1[columns_to_sum].sum(axis=1)

    total = final_df1.sum(numeric_only=True)
    total.name = 'Total'
    final_df1 = final_df1.append(total.transpose())
                                            
    final_df1.to_excel(str("static/media/") + "input_item_agent_wise_report.xlsx")

    data_dict = {}

    try:
        image_path = str("static/media/") + "input_item_agent_wise_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict["excel"] = encoded_image
    except Exception as err:
        print('Error',err)
    
    print(data_dict)
    return Response(data=data_dict , status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_weigh_bridge_excel(request):
    base64_file = request.data['base_64_excel'] 
    file_name = request.data['file_name'].split('\\')[-1]
    season_id = get_active_season_id()
    Procurement_file_upload_obj = ProcurementFileUpload(uploaded_by=request.user, 
                                                        uploaded_at=datetime.datetime.now(), 
                                                        uploaded_count=0, 
                                                        excel_file=decode_excel_image(base64_file, file_name), 
                                                        file_name=file_name,
                                                        season_id = season_id)
    Procurement_file_upload_obj.save()

    temp_df = pd.read_excel(Procurement_file_upload_obj.excel_file) 

    temp_df['Gross time'] = temp_df['Gross time'].astype(str)
    temp_df['Tare Time'] = temp_df['Tare Time'].astype(str)
    print(temp_df['Gross time'])
    print(temp_df['Tare Time'])

    uploaded_count_no = 0
    for index, df in temp_df.iterrows():
        if not Procurement.objects.filter(ticket_number=df['Ticket No']).exists():
            if df['Ticket No'] != 'Total:':
                if not TempProcurement.objects.filter(ticket_number=df['Ticket No']).exists():
                    temp_procurement_obj = TempProcurement(procurement_file_upload_id=Procurement_file_upload_obj.id,
                                                        ticket_number=df['Ticket No'],
                                                        id_company = df['ID/Company'],
                                                        customer_name = df['Customer'],
                                                        vehicle_number=df['Vehicle No'],
                                                        vehicle_driver_name=df['Driver'],
                                                        gross_weight=df['Gross Wt'], 
                                                        gross_time=df['Gross time'],
                                                        tare_weight=df['Tare Wt'],
                                                        tare_time=df['Tare Time'],
                                                        net_wt=df['Net Wt'],
                                                        bag_number=df['Bag No'],
                                                        bag_weight=df['Bag weight'],
                                                        net_weight=df['Net Weight'],
                                                        price=df['prices'],
                                                        amount=df['Amount'],
                                                        gross_operator=df['GrossOperator'],
                                                        deduct=df['Deduct'],
                                                        moisture=df['Moisture'],
                                                        tare_operator=df['TareOperator'],
                                                        date=df['Date']
                                                        )
                                                        
                    temp_procurement_obj.save()
                    print('time',temp_procurement_obj.gross_time)
                    uploaded_count_no = uploaded_count_no +1 
                else:
                    print('Is_existed:', df['Ticket No'])
            Procurement_file_upload_obj.uploaded_count = uploaded_count_no
            Procurement_file_upload_obj.save()
        else:
            print('Already_existed:', df['Ticket No'])
    return Response(data=True , status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_weigh_bridge_excel_upload_log(request):
    uploaded_log_list = list(ProcurementFileUpload.objects.filter(season_id=get_active_season_id()).values_list('uploaded_by__first_name', 'uploaded_at', 'file_name', 'uploaded_count'))
    uploaded_log_col = ['uploaded_by', 'uploaded_at', 'file_name', 'uploaded_count']
    upload_df = pd.DataFrame(uploaded_log_list, columns=uploaded_log_col)
    upload_dict = upload_df.to_dict('r')
    return Response(data=upload_dict , status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_weigh_bridge_excel_data(request):
    temp_procurement_obj = TempProcurement.objects.filter(is_uploaded=False).order_by('ticket_number')
    temp_procurement_values = temp_procurement_obj.values_list('ticket_number', 'id_company', 'customer_name', 'vehicle_number', 'vehicle_driver_name', 'gross_weight', 'tare_weight', 'net_wt', 'bag_number', 'bag_weight', 'net_weight', 'price', 'amount', 'gross_time', 'tare_time','gross_operator', 'deduct', 'moisture', 'tare_operator', 'date')
    column_names = ['Ticket No', 'ID/Company', 'Customer', 'Vehicle No', 'Driver','Gross Wt', 'Tare Wt', 'Net Wt', 'Bag No', 'Bag Deuct', 'Net Weight', 'prices', 'Amount', 'Gross time', 'Tare Time', 'GrossOperator', 'Deduct', 'Moisture', 'TareOperator', 'Date']
    df = pd.DataFrame(temp_procurement_values, columns=column_names)
    df['ID/Company'] = df['ID/Company'].astype(float)
    df['ID/Company'] = df['ID/Company'].astype(int)
    df['Gross Wt'] = df['Gross Wt'].astype(str)  
    df['Tare Wt'] = df['Tare Wt'].astype(str)  
    df = df.fillna(0)
    data_list = df.to_dict('r')
    return Response(data=data_list , status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def harvest_report_datewise(request):
    season_id = request.data['season_id']
    # date = request.data['date']

    ticket_list=[]
    procurement_ticket_obj = list(Procurement.objects.filter( procurement_group__season_id=season_id).values_list('ticket_number', flat=True))
    if len(procurement_ticket_obj)!= 0:
        harvest_obj = Harvest.objects.filter(ticket_number__in=procurement_ticket_obj)
        harvest_values = list(harvest_obj.values_list('sowing__farmer__id','sowing__farmer__first_name', 'value', 'ticket_number', 'date_of_harvest'))
        column_names = ['Farmer Id', 'Farmer First Name','Value', 'Ticket Number', 'Date Of Harvest']
        df = pd.DataFrame(harvest_values, columns=column_names)
        
        farmer_season_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id).values_list('farmer_id','seasonal_farmer_code', 'cluster__name')
        column_names = ["Farmer Id","Farmer Code", "Cluster Name"]
        farmer_season_df = pd.DataFrame(list(farmer_season_obj), columns=column_names)

        final_df = pd.merge(df, farmer_season_df, left_on='Farmer Id', right_on='Farmer Id', how='left')

        final_df = final_df.drop(columns=['Farmer Id'])

        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "harvest_report.xlsx", engine="xlsxwriter")
        sheet_name = "harvest_data"
        final_df.to_excel(writer, sheet_name=sheet_name, startrow=1)

        harvest_ticket_list = list(set(list(Harvest.objects.filter(sowing__season_id=season_id).values_list('ticket_number',flat=True))))
        non_harvest_ticket_list = list(Procurement.objects.filter(procurement_group__season_id=season_id).exclude(ticket_number__in=harvest_ticket_list).values_list('ticket_number',flat=True))

        # for ticket in procurement_ticket_obj:
        #     if ticket in final_df.values:
        #         print('in')
        #     else:
        #         ticket_list.append(ticket)
        ticket_df = pd.DataFrame(non_harvest_ticket_list, columns=['Ticket'])
        print(ticket_df.columns)
        sheet_name = "no_harvest"
        ticket_df.to_excel(writer, sheet_name=sheet_name, startrow=1, index=False)
        writer.save()
        data={
            'status':True,
            'alert':'excel data'
        } 
        try:
            image_path = str("static/media/") + "harvest_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print('Error',err)
        return Response(data=data , status=status.HTTP_200_OK)
    else:
        data={
            'status':False,
            'alert':'No data available'
        }
        print('Give valid date')
        return Response(data=data , status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_master_farmer_data_report(request):
    season_id = request.data['season_id']
    cluster_id_list = request.data['cluster_id_list']

    if len(cluster_id_list) == 0:
        cluster_id_list = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list('cluster_id', flat=True))

    if 'demo_farmer' in request.data:
        #demo farmer, agent, cluster, df
        farmer_agent_obj =  FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_id_list, farmer__is_demo_farmer=True)
    else:
        #  master farmer, agent, cluster, df
        farmer_agent_obj =  FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_id_list)
    farmer_agent_list = farmer_agent_obj.values_list('farmer_id', 'farmer__first_name', 'farmer__last_name', 'seasonal_farmer_code', 'farmer__aadhaar_number','cluster__name','agentfarmermap__agent__first_name', 'userfarmermap__officer__username', 'farmer__village__name', 'farmer__taluk__name', 'farmer__hobli__name', 'farmer__district__name', 'farmer__state__name', 'season__name',)
    farmer_agent_column = ['farmer_id', 'first_name', 'last_name', 'farmer_code', 'aadhaar_number','cluster_name','agent_name', 'superviosr_name', 'village', 'taluk', 'hobli', 'district', 'state', 'season_name']
    farmer_agent_df = pd.DataFrame(list(farmer_agent_list), columns=farmer_agent_column)
    farmer_agent_df = farmer_agent_df.drop_duplicates('farmer_id')

    # farmer sowing df
    farmer_sowing_list = list(Sowing.objects.filter(cultivation_phase_id=2, season_id=season_id, farmer_id__in=list(farmer_agent_df['farmer_id'])).values_list('farmer_id', 'farmer__mobile', 'area_calculated_via_geo_fencing'))            
    farmer_sowing_column = ['farmer_id', 'mobile',  'geo_calculated_area']
    farmer_sowing_df = pd.DataFrame(farmer_sowing_list, columns=farmer_sowing_column)
    farmer_sowing_df = farmer_sowing_df.fillna(0)
    farmer_sowing_df_geo = farmer_sowing_df.groupby('farmer_id').agg({'mobile':'first','geo_calculated_area':sum}).reset_index()

    combain_df = pd.merge(farmer_agent_df, farmer_sowing_df_geo, left_on='farmer_id', right_on='farmer_id', how='outer')
    combain_df = combain_df.drop_duplicates('farmer_id')

    # cultivation pase
    phase_list = list(Sowing.objects.filter(season_id=season_id, farmer_id__in=list(combain_df['farmer_id'])).values_list('farmer_id', 'sowing_date','cultivation_phase_id', 'area', 'water_source__name'))
    phase_column = ['farmer_id', 'sowing_date','pase_id', 'area', 'main_crop_water_resource_name']
    phase_df = pd.DataFrame(phase_list, columns=phase_column)

    phase1_df = phase_df[phase_df['pase_id']==1].drop(columns=['pase_id'])
    phase1_df = phase1_df.rename(columns={'area': 'total_nursury_crop_area'})
    phase1_df = phase1_df.groupby('farmer_id').agg({'total_nursury_crop_area': sum,'main_crop_water_resource_name': 'first', 'sowing_date': 'first'}).reset_index()

    phase2_df = phase_df[phase_df['pase_id']==2].drop(columns=['pase_id', 'main_crop_water_resource_name'])
    phase2_df = phase2_df.rename(columns={'area': 'total_transplant_crop_area', 'sowing_date': 'Tp_date'})
    phase2_df = phase2_df.groupby('farmer_id').agg({'total_transplant_crop_area': sum,  'Tp_date': 'first'}).reset_index()

    cultivation_phase_df = pd.merge(phase1_df, phase2_df, left_on='farmer_id', right_on='farmer_id', how='outer')
    cultivation_phase_df = cultivation_phase_df.fillna(0)

    combain_df = pd.merge(combain_df, cultivation_phase_df, left_on='farmer_id', right_on='farmer_id', how='left')

    # farmer bank df
    farmer_bank_list = FarmerBankDetails.objects.filter(farmer_id__in=list(combain_df['farmer_id']), is_primary=True).values_list("farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name", "account_number", 'remarks')                
    farmer_bank_column = ["farmer_id", "bank", "branch", "ifsc_code", "micr_code", "account_holder_name", "account_number", 'remarks']
    farmer_bank_df = pd.DataFrame(farmer_bank_list, columns=farmer_bank_column).fillna(0).drop_duplicates('farmer_id')
    combain_df = pd.merge(combain_df, farmer_bank_df, left_on='farmer_id', right_on='farmer_id', how='left')

    # farmer distribution sowing
    sowing_list = list(Sowing.objects.filter(season_id=season_id, farmer_id__in=list(combain_df['farmer_id'])).values_list('id', flat=True))
    if AgentFarmerDistributionSowing.objects.filter(sowing_id__in=sowing_list).exists():
        farmer_distribution_list = AgentFarmerDistributionSowing.objects.filter(sowing_id__in=sowing_list).values_list('sowing__farmer_id', 'input_combo__name', 'no_of_unit')
        farmer_distribution_column = ['farmer_id', 'input_combo', 'number_of_unit']
        farmer_distribution_df = pd.DataFrame(farmer_distribution_list, columns=farmer_distribution_column)
        farmer_distribution_df = farmer_distribution_df.groupby(['farmer_id', 'input_combo']).agg({'number_of_unit':sum}).reset_index()

        #->##convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        farmer_distribution_df = pd.pivot_table(farmer_distribution_df, index=['farmer_id'] , columns='input_combo', aggfunc=min, fill_value=0)

        #->##convert_pivot_table_to_normal_df
        farmer_distribution_df.columns = farmer_distribution_df.columns.droplevel(0) #remove amount
        farmer_distribution_df.columns.name = None  #remove categories
        farmer_distribution_df = farmer_distribution_df.reset_index() #index to columns
        combain_df = pd.merge(combain_df, farmer_distribution_df, left_on='farmer_id', right_on='farmer_id', how='left').fillna(0)

    # harvest 
    sowing_id_list = list(Sowing.objects.filter(season_id=season_id, farmer_id__in=list(combain_df['farmer_id']), cultivation_phase_id=2).values_list('id', flat=True))
    harvest_list = list(Harvest.objects.filter(sowing_id__in=sowing_id_list).values_list('sowing__farmer_id', 'value'))
    harvest_column = ['farmer_id', 'harvest_value']
    
    haevesr_df = pd.DataFrame(harvest_list, columns=harvest_column)
    haevesr_df = haevesr_df.groupby('farmer_id').agg({'harvest_value':sum}).reset_index()

    combain_df = pd.merge(combain_df, haevesr_df, left_on='farmer_id', right_on='farmer_id', how='left').fillna(0)

    combain_df['total_yeild_on_sowing _acre'] = combain_df['harvest_value'] / combain_df['total_transplant_crop_area']

    combain_df = combain_df.rename(columns={'farmer_id' : "Farmer Id" , 'first_name' : "First Name" , 'last_name' : "Last Name" , 'farmer_code' : "Farmer Code" , 'cluster_name' : "Cluster Name" ,
       'agent_name' : "Agent Name" , 'superviosr_name' : "Superviosr Name" , 'mobile' : "Mobile" , 'village' : "Village" , 'village2': "village2", 'season_name' : "Season Name" ,
       'geo_calculated_area' : "Geo Calculated Area" , 'total_nursury_crop_area' : "Total Nursury Crop Area" ,
       'main_crop_water_resource_name' : "Main Crop Water Resource Name" , 'sowing_date' : "Sowing Date" ,
       'total_transplant_crop_area' : " Total Transplant Crop Area" , 'Tp_date' : "Tp Date" , 'bank' : "Bank" , 'branch' : "Branch" , 'ifsc_code' : "IFSC Code" ,
       'micr_code' : "Micr Code" , 'account_holder_name' : "Account Holder Name" , 'account_number' : "Account Number" , 'remarks' : "Remarks" ,
       'harvest_value' : "Harvest Value" , 'total_yeild_on_sowing _acre' : "Total Yeild On Sowing Acre" ,})

    combain_df = combain_df.fillna(0)
    combain_df['Farmer Id'] = combain_df['Farmer Id'].astype(str)
    combain_df.index += 1
    total = combain_df.sum(numeric_only=True)
    total.name = 'Total'
    combain_df = combain_df.append(total.transpose())

    writer = pd.ExcelWriter(str("static/media/") + "master_farmers_report.xlsx", engine="xlsxwriter")
    # creating excel sheet with name
    combain_df.to_excel(writer, sheet_name="Sheet1", startrow=1)
    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:AK1", "Master Farmer Report - " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 17, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(combain_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    data = {}
    data['excel_name'] = "master_farmer_report.xlsx"
    try:
        image_path = str("static/media/") + "master_farmers_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_cluster_wise_farmer_village_count_data_report(request):
    agent_cluster_list = list(UserClusterMap.objects.filter(user__userprofile__user_type_id=6, season_id=request.data['season_id']).values_list('user_id', 'user__first_name', 'cluster__name'))
    agent_cluster_df = pd.DataFrame(agent_cluster_list, columns=['Agent Id', 'Agent Name', 'Cluster Name']).sort_values('Cluster Name')

    agent_farmer_village_list = list(AgentFarmerMap.objects.filter(agent_id__in = agent_cluster_df['Agent Id'], farmer__season_id=get_active_season_id()).values_list('agent_id', 'farmer__farmer__village__name'))
    agent_farmer_village_df = pd.DataFrame(agent_farmer_village_list, columns=['Agent Id', 'Village'])
    agent_farmer_village_df = agent_farmer_village_df.groupby('Agent Id').agg({'Village': 'count'}).reset_index()

    final_df = pd.merge(agent_cluster_df, agent_farmer_village_df, left_on='Agent Id', right_on='Agent Id', how='outer')
    final_df = final_df.fillna(0)
    final_df = final_df.drop(columns=['Agent Id'])
    final_dict = final_df.groupby('Cluster Name').apply(lambda x: x.to_dict('r')).to_dict()

    writer = pd.ExcelWriter(str("static/media/") + "cluster_wise_agent_village_count.xlsx", engine="xlsxwriter")

    for index, title in enumerate(final_dict):
        cluster_df = pd.DataFrame(final_dict[title])
        cluster_df.index += 1
        total = cluster_df.sum(numeric_only=True)
        total.name = 'Total'
        cluster_df = cluster_df.append(total.transpose())

        # creating excel sheet with name
        cluster_df.to_excel(writer, sheet_name=title, startrow=1)
        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets[title]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:D1", "Cluster Wise Agent Village Count" + " - " + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 17, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(cluster_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    data = {}
    data['excel_name'] = "cluster_wise_agent_village_count.xlsx"
    try:
        image_path = str("static/media/") + "cluster_wise_agent_village_count.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def procurement_daterange_agentwise_report(request):
    print(request.data)
    start_date = request.data["start_date"]
    end_date = request.data["end_date"]
    season_id = request.data["season_id"]

    if Procurement.objects.filter(procurement_group__procurement_date__range=[start_date, end_date], procurement_group__season_id=season_id).exists():
        procurement_objs = (Procurement.objects.filter(procurement_group__procurement_date__range=[start_date, end_date], procurement_group__season_id=season_id).order_by("procurement_group__procurement_date")
                .values_list(
                "procurement_group__procurement_date",
                "ticket_number",
                "procurement_transaport_incharge_kyc__aadhar_number",
                "procurement_group__agent__id",
                "procurement_group__agent__first_name",
                "vehicle_number",
                "loaded_vehicle_weight",
                "empty_vehicle_weight",
                "produce_gross_weight",
                "gunnybag_count",
                "gunnybag_weight",
                "moisture",
                "other_deduction",
                "str_weight",
                "procurement_group__produce_net_weight",
                "procurement_group__price_per_unit",
                "procurement_group__agent_price_deduction",
                "procurement_group__payment_to_wallet",))
        procurement_columns = [
            "Date",
            "Ticket No",
            "ID/Company",
            "agent_id",
            "Agent Name",
            "Vehicle No",
            "Gross Wt/kg",
            "Tare Wt/kg",
            "Net Wt/kg",
            "Bag No",
            "Bag Deduct",
            "moisture Deduct",
            "other_deduction",
            "str_weight",
            "Final Weight",
            "Total prices/Per kg",
            "Deduction Price/kg",
            "Deduction/kg",]
        procurement_df = pd.DataFrame(procurement_objs, columns=procurement_columns)

        agent_cluster = UserClusterMap.objects.filter(season_id=season_id, user__userprofile__user_type_id=6).values_list('user_id', 'cluster__name')
        agent_cluster_col = ['agent_id', 'cluster_name']
        agent_cluster_df = pd.DataFrame(agent_cluster, columns=agent_cluster_col)
        agent_cluster_df

        procurement_cluster_df = pd.merge(procurement_df, agent_cluster_df, left_on='agent_id', right_on='agent_id', how='left')
        
        procurement_df = procurement_cluster_df

        procurement_df["Bag weight Deduction/ Per kg"] = procurement_df.apply(lambda x: "0.2", axis=1)
        procurement_df["Quality Weight"] = procurement_df.apply(lambda x: "0", axis=1)
        procurement_df["avg bag weight"] = procurement_df.apply(lambda x: round(x["Net Wt/kg"] / x["Bag No"], 2), axis=1)

        procurement_df["Payment Price/kg"] = procurement_df.apply(lambda x: (x["Total prices/Per kg"] - x["Deduction Price/kg"]), axis=1)
        
        procurement_df['loss'] = ((procurement_df['str_weight'] - procurement_df['Final Weight']) / procurement_df['str_weight']) * 100
        procurement_df['loss'] = procurement_df['loss'].astype(float).round(2)


        bank_details = UserBankDetails.objects.filter(is_primary=True).values_list(
            "user_id",
            "bank",
            "branch",
            "ifsc_code",
            "account_holder_name",
            "account_number",
        )
        bank_columns = [
            "user_id",
            "Bank name",
            "Branch",
            "IFSC Code",
            "BankAccount",
            "BankNumber",
        ]
        bank_df = pd.DataFrame(bank_details, columns=bank_columns)

        df = pd.merge(
            procurement_df, bank_df, left_on="agent_id", right_on="user_id", how="left"
        )
        df = df.fillna("-")
        df["Gross Wt/kg"] = df.apply(lambda x: convert_decimal(x["Gross Wt/kg"]), axis=1)
        df["Tare Wt/kg"] = df.apply(lambda x: convert_decimal(x["Tare Wt/kg"]), axis=1)
        df["Net Wt/kg"] = df.apply(lambda x: convert_decimal(x["Net Wt/kg"]), axis=1)
        df['Bag Deduct']=df.apply(lambda x: convert_decimal(x['Bag Deduct']), axis=1)
        df["str_weight"] = df.apply(lambda x: convert_decimal(x["str_weight"]), axis=1)
        df["Final Weight"] = df.apply(lambda x: convert_decimal(x["Final Weight"]), axis=1)
        df["Total Amount/kg"] = df.apply(lambda x: (x["Final Weight"] * x["Total prices/Per kg"]), axis=1)
        df["Total Amount/kg"] = df.apply(lambda x: convert_decimal(x["Total Amount/kg"]), axis=1)
        df["Deduction/kg"] = df.apply(lambda x: convert_decimal(x["Deduction/kg"]), axis=1)
        df["Payment Amount/per kg"] = df.apply(lambda x: x["Total Amount/kg"] - x["Deduction/kg"], axis=1)
        
        df = df[
            [
                "agent_id",
                "Date",
                "Ticket No",
                "ID/Company",
                "Agent Name",
                "cluster_name",
                "Vehicle No",
                "Gross Wt/kg",
                "Tare Wt/kg",
                "Net Wt/kg",
                "Bag No",
                "Bag weight Deduction/ Per kg",
                "Bag Deduct",
                "Quality Weight",
                "moisture Deduct",
                "other_deduction",
                "str_weight",
                "Final Weight",
                "Total prices/Per kg",
                "Total Amount/kg",
                "Deduction Price/kg",
                "Deduction/kg",
                "Payment Price/kg",
                "Payment Amount/per kg",
                "BankAccount",
                "Bank name",
                "Branch",
                "BankNumber",
                "IFSC Code",
                "avg bag weight",
                "loss"
            ]
        ]

        writer = pd.ExcelWriter("static/media" + "/procurement_report_agentwise.xlsx", engine="xlsxwriter")

        for item in ProcurementGroup.objects.filter(season_id=season_id):
            final_df=df[df['agent_id']==item.agent.id]
            
            final_df = final_df.drop(["agent_id"], axis=1)

            final_df = final_df.rename(columns={'cluster_name' : 'cluster_name','moisture Deduct' : 'Moisture Deduct', 'other_deduction' : 'Other Deduction', 'str_weight' : 'Str Weight','avg bag weight' : 'Avg Bag Weight', 'loss' : 'Loss',})

            final_df[['Gross Wt/kg', 'Tare Wt/kg', 'Net Wt/kg','Bag weight Deduction/ Per kg', 'Bag Deduct', 'Quality Weight','Moisture Deduct', 'Other Deduction', 'Str Weight', 'Final Weight',
                    'Total prices/Per kg', 'Total Amount/kg', 'Deduction Price/kg',
                    'Deduction/kg', 'Payment Price/kg', 'Payment Amount/per kg',
                    'Avg Bag Weight', 'Loss']] = final_df[['Gross Wt/kg', 'Tare Wt/kg', 'Net Wt/kg','Bag weight Deduction/ Per kg', 'Bag Deduct', 'Quality Weight','Moisture Deduct', 'Other Deduction', 'Str Weight', 'Final Weight',
                    'Total prices/Per kg', 'Total Amount/kg', 'Deduction Price/kg',
                    'Deduction/kg', 'Payment Price/kg', 'Payment Amount/per kg',
                    'Avg Bag Weight', 'Loss']].astype(float)

            final_df['Bag No'] = final_df['Bag No'].astype(str)

            final_df.index += 1
            total = final_df.sum(numeric_only=True)
            total.name = 'Total'
            final_df = final_df.append(total.transpose())
            
            final_df.to_excel(writer, sheet_name=str(item.agent.first_name), startrow=1, index=False)
            workbook = writer.book
            worksheet = writer.sheets[str(item.agent.first_name)]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                }
            )

            date = datetime.datetime.now().date()
            # Merge 3 cells.
            worksheet.merge_range(
                "A1:AE1",
                "procurement_report_agentwise( " + start_date + " - " + end_date + " )",
                merge_format,
            )

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:AE", 18, format1)
            worksheet.set_column(0, 7, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        document = {}
        try:
            image_path = str("static/media/") + "procurement_report_agentwise.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                document["excel"] = encoded_image
        except Exception as err:
            print(err)
        document["data"] = df.to_dict("r")
    else:
        document = {}
        document["excel"] = "no-data"
    return Response(document, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def input_item_report_agent_cluster_wise(request):
    print(request.data)
    cluster_id = request.data['cluster_id']
    season_id = get_active_season_id()
    cluster_agents = list(UserClusterMap.objects.filter(season_id=get_active_season_id(), cluster_id=cluster_id ,user__userprofile__user_type_id=6).values_list('user_id', flat=True))
    combo_issue_request_agentmap_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id__gte=8, agent_id__in=cluster_agents).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))      
    column_names = ['Agent Id', 'Agent Name', 'Input Combo Id', 'Quantity',  'Input Combo Name']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_agentmap_obj, columns=column_names)
    combo_issue_request_df = combo_issue_request_df.groupby(['Agent Id', 'Input Combo Id']).agg({'Agent Name': 'first', 'Quantity': sum, 'Input Combo Name': 'first'}).reset_index()
    combo_issue_request_df = combo_issue_request_df.drop(columns=['Input Combo Id']) 

    #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    final_df = pd.pivot_table(combo_issue_request_df, index=['Agent Id','Agent Name'] , columns='Input Combo Name', aggfunc=min, fill_value=0)

    #convert_pivot_table_to_normal_df
    final_df.columns = final_df.columns.droplevel(0) #remove amount
    final_df.columns.name = None  #remove categories

    final_df = final_df.reset_index() #index to columns
    final_df1 = final_df.drop(columns=['Agent Id'])

    #get total for all columns
    tot_dict = dict(final_df1.sum(numeric_only=True, axis=0))
    final_df1 = final_df1.append(tot_dict, ignore_index=True) #append dict in final_df1

    total_cols = len(final_df1.axes[0])-1
    # print(total_cols)
    final_df1.loc[total_cols, 'Agent Name'] = 'Input_total'

    columns_to_sum = final_df1.columns[ : final_df1.shape[1]]
    final_df1['Agent Total'] = final_df1[columns_to_sum].sum(axis=1)

    final_df1.to_excel(str("static/media/") + "input_item_agent_cluster_wise_report.xlsx")

    data_dict = {}

    try:
        image_path = str("static/media/") + "input_item_agent_cluster_wise_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict["excel"] = encoded_image
    except Exception as err:    
        print('Error',err)
    
    print(data_dict)
    return Response(data=data_dict , status=status.HTTP_200_OK)


@api_view(['POST'])
def season_wise_user_cluster_list(request):
    season_id = request.data['season_id']
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))

    print("user_id" , user_id)
    user_cluster_obj = UserClusterMap.objects.filter(user_id__in=subordinate_user_ids)
    user_cluster_list = list(user_cluster_obj.values_list('season_id','cluster_id', 'cluster__name'))
    user_cluster_column = ['season_id', 'cluster_id', 'cluster_name']
    user_cluster_df = pd.DataFrame(user_cluster_list,columns=user_cluster_column)
    print(user_cluster_df)
    user_cluster_df = user_cluster_df.groupby(['season_id', 'cluster_id']).agg({'cluster_name': 'first'}).reset_index()
    user_cluster_value_list = user_cluster_df.groupby('season_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=user_cluster_value_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def season_wise_agents_for_mobile(request):
    season_id = get_active_season_id()
    user_id = request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter().values_list('agent_id',flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))

    usercluster_obj = list(UserClusterMap.objects.filter(user_id__in=subordinate_user_ids).values_list('season_id', 'user_id', 'user__first_name', 'user__last_name'))
    column_names = ['season_id', 'agent_id', 'first_name', 'last_name']
    agent_df = pd.DataFrame(usercluster_obj, columns=column_names)
    agent_df = agent_df.groupby(['season_id', 'agent_id']).agg({'first_name': 'first', 'last_name': 'first'}).reset_index()
    agent_dict_seasonwise = agent_df.groupby('season_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=agent_dict_seasonwise, status=status.HTTP_200_OK)    


def agent_distribution_trasaction_log(id, modified_by_id):
    
    agent_inventry_obj = AgentInventory.objects.filter(season_id=get_active_season_id(), id=id)

    for item in agent_inventry_obj:
        # print(item.agent_id)
        if not AgentWallet.objects.filter(agent_id=item.agent_id).exists():
            updated_amount = 0 - (item.quantity_at_receipt * item.combo_issue_request.input_combo.price)
            old_balance = 0
            print("type : ", updated_amount)
            AgentWallet.objects.create(
                agent_id=item.agent_id,
                current_balance=updated_amount,
                modified_by_id=modified_by_id,
            )
            new_balance = updated_amount
        else:
            old_balance = AgentWallet.objects.get(agent_id=item.agent_id).current_balance
            updated_amount = old_balance - item.quantity_at_receipt * item.combo_issue_request.input_combo.price
            AgentWallet.objects.filter(agent_id=item.agent_id).update(current_balance=Decimal(updated_amount), modified_by=modified_by_id)
            new_balance = updated_amount

        agent_transaction_log = AgentTransactionLog(
            date=datetime.datetime.today(),
            transaction_direction_id=1,  # ccgb to agent wallet when wallet adjustment - positive
            agent_id=item.agent_id,
            data_entered_by_id=modified_by_id,
            amount= item.quantity_at_receipt * item.combo_issue_request.input_combo.price,
            transaction_id="1234",
            transaction_mode_id=1,
            transaction_approval_status_id=1,
            wallet_balance_before_this_transaction=old_balance,
            wallet_balance_after_this_transaction=new_balance,
            description="it will be added as a positive amount in agent wallet as a commision for wallet adjustment",
            modified_by_id=modified_by_id,
        )
        agent_transaction_log.save()

        input_distribution_transaction_map_obj = InputDistributionTransactionMap(
                                                agent_inventory_id = item.id,
                                                transaction_log_id = agent_transaction_log.id)
        input_distribution_transaction_map_obj.save()
    return True



def agent_return_transaction_log(id, modified_by_id):
    combo_return_request_obj = ComboReturnRequest.objects.get(id=id)
    combo_return_request_label_map_obj_count = ComboReturnRequestLabelMap.objects.filter(return_label__status_id=2, combo_return_request_id=combo_return_request_obj.id).count()
    combo_return_request_label_map_obj = list(ComboReturnRequestLabelMap.objects.filter(return_label__status_id=2, combo_return_request_id=combo_return_request_obj.id))[0]

    if not AgentWallet.objects.filter(agent_id=combo_return_request_obj.agent.id).exists():
        print('new agent entry')
        updated_amount = round(combo_return_request_label_map_obj_count * combo_return_request_label_map_obj.return_label.agent_inventory.combo_issue_request.input_combo.price) #price need update
        old_balance = 0
        print("type : ", updated_amount)
        AgentWallet.objects.create(
            agent_id=combo_return_request_obj.agent.id,
            current_balance=updated_amount,
            modified_by_id=modified_by_id,
        )
        new_balance = updated_amount
    else:
        old_balance = AgentWallet.objects.get(agent_id=combo_return_request_obj.agent.id).current_balance
        updated_amount = old_balance + combo_return_request_label_map_obj_count * combo_return_request_label_map_obj.return_label.agent_inventory.combo_issue_request.input_combo.price
        AgentWallet.objects.filter(agent_id=combo_return_request_obj.agent_id).update(current_balance=Decimal(updated_amount), modified_by=modified_by_id)
        new_balance = updated_amount
        
        agent_transaction_log = AgentTransactionLog(
            date=datetime.datetime.today(),
            transaction_direction_id=4,  # agent seed return
            agent_id=combo_return_request_obj.agent.id,
            data_entered_by_id=modified_by_id,
            amount= combo_return_request_label_map_obj_count * combo_return_request_label_map_obj.return_label.agent_inventory.combo_issue_request.input_combo.price, 
            transaction_id="1234",
            transaction_mode_id=1,
            transaction_approval_status_id=1,
            wallet_balance_before_this_transaction=old_balance,
            wallet_balance_after_this_transaction=new_balance,
            description="money adjustment to wallet - adding money to wallet(positive)",
            modified_by_id=modified_by_id,
        )
        agent_transaction_log.save()
        
        input_return_transaction_log_obj = InputReturnTransactionLog(
                                            transaction_log_id = agent_transaction_log.id,
                                            combo_return_request_id = combo_return_request_obj.id
                                            )
        input_return_transaction_log_obj.save()
        print('return_ok')
    return True


def agent_procurement_transaction_log(id, modified_by_id):
    # id=id
    procurement_obj = Procurement.objects.filter(id=id)
    for item in procurement_obj:
        # print(item.procurement_group.payment_to_agent)
        if not AgentWallet.objects.filter(agent_id=item.procurement_group.agent_id).exists():
            updated_amount = item.procurement_group.payment_to_wallet
            old_balance = 0
            print("type : ", updated_amount)
            AgentWallet.objects.create(
                agent_id=item.procurement_group.agent_id,
                current_balance=updated_amount,
                modified_by_id=modified_by_id,
            )
            new_balance = updated_amount
        else:
            old_balance = AgentWallet.objects.get(agent_id=item.procurement_group.agent_id).current_balance
            updated_amount = old_balance + item.procurement_group.payment_to_wallet
            AgentWallet.objects.filter(agent_id=item.procurement_group.agent_id).update(current_balance=Decimal(updated_amount), modified_by_id=modified_by_id)
            new_balance = updated_amount
        agent_transaction_log = AgentTransactionLog(
            date=datetime.datetime.today(),
            transaction_direction_id=3,  
            agent_id=item.procurement_group.agent_id,
            data_entered_by_id=modified_by_id,
            amount= item.procurement_group.payment_to_wallet, 
            transaction_id="1234",
            transaction_mode_id=1,
            transaction_approval_status_id=1,
            wallet_balance_before_this_transaction=old_balance,
            wallet_balance_after_this_transaction=new_balance,
            description="it will be given to agent hand",
            modified_by_id=modified_by_id,
        )
        agent_transaction_log.save()
        
        input_procurement_transaction_log_obj = InputProcurementTransactionLog(
                                                transaction_log_id = agent_transaction_log.id,
                                                procurement_id = item.id)
        input_procurement_transaction_log_obj.save()
        
        agent_transaction_log = AgentTransactionLog(
            date=datetime.datetime.today(),
            transaction_direction_id=2,  
            agent_id=item.procurement_group.agent_id,
            data_entered_by_id=modified_by_id,
            amount= item.procurement_group.payment_to_agent, 
            transaction_id="1234",
            transaction_mode_id=1,
            transaction_approval_status_id=1,
            wallet_balance_before_this_transaction=old_balance,
            wallet_balance_after_this_transaction=new_balance,
            description="it will be given to agent wallet ",
            modified_by_id=modified_by_id,
        )
        agent_transaction_log.save()
        
        input_procurement_transaction_log_obj = InputProcurementTransactionLog(
                                                transaction_log_id = agent_transaction_log.id,
                                                procurement_id = item.id)
        input_procurement_transaction_log_obj.save()
    return True

@api_view(['POST'])
@permission_classes((AllowAny,))
def agent_transaction_log_data(request):

    start_date = request.data['from_date']
    end_date = request.data['to_date']
    agent_id = request.data['agent_id']

    distribution_transaction_map_obj = InputDistributionTransactionMap.objects.filter(transaction_log__date__range=[start_date, end_date], transaction_log__agent_id=agent_id).order_by('transaction_log__date')
    distribution_transaction_map_values = distribution_transaction_map_obj.values_list('transaction_log__id',
                                                                                        'transaction_log__agent_id',
                                                                                        'transaction_log__date',
                                                                                        'transaction_log__agent__first_name',
                                                                                        'transaction_log__wallet_balance_before_this_transaction',
                                                                                        'transaction_log__amount',
                                                                                        'transaction_log__wallet_balance_after_this_transaction')
    distribution_columns = ['agent_transaction_id','agent_id','date','agent_name', 'wallet_balance_before_this_transaction', 'amount', 'wallet_balance_after_this_transaction']
    distribution_df = pd.DataFrame(list(distribution_transaction_map_values), columns=distribution_columns)
    distribution_df['category'] = 'distribution'
    distribution_df

    procurement_transaction_log_obj = InputProcurementTransactionLog.objects.filter(transaction_log__date__range=[start_date, end_date],transaction_log__agent_id=agent_id).order_by('transaction_log__date')
    procurement_transaction_log_values = procurement_transaction_log_obj.values_list('transaction_log__id',
                                                                                        'transaction_log__agent_id',
                                                                                        'transaction_log__date',
                                                                                        'transaction_log__agent__first_name',
                                                                                        'transaction_log__wallet_balance_before_this_transaction',
                                                                                        'transaction_log__amount',
                                                                                        'transaction_log__wallet_balance_after_this_transaction')
    procurement_transaction_columns = ['agent_transaction_id','agent_id','date','agent_name', 'wallet_balance_before_this_transaction', 'amount', 'wallet_balance_after_this_transaction']
    procurement_transaction_df = pd.DataFrame(list(procurement_transaction_log_values), columns=procurement_transaction_columns)
    procurement_transaction_df['category'] = 'procurement'
    procurement_transaction_df

    return_transaction_map_obj = InputReturnTransactionLog.objects.filter(transaction_log__date__range=[start_date, end_date],transaction_log__agent_id=agent_id).order_by('transaction_log__date')
    return_transaction_map_values = return_transaction_map_obj.values_list('transaction_log__id',
                                                                                'transaction_log__agent_id',
                                                                                'transaction_log__date',
                                                                                'transaction_log__agent__first_name',
                                                                                'transaction_log__wallet_balance_before_this_transaction',
                                                                                'transaction_log__amount',
                                                                                'transaction_log__wallet_balance_after_this_transaction')
    return_transaction_map_column = ['agent_transaction_id','agent_id','date','agent_name', 'wallet_balance_before_this_transaction', 'amount', 'wallet_balance_after_this_transaction']
    return_transaction_map_df = pd.DataFrame(list(return_transaction_map_values), columns=return_transaction_map_column)
    return_transaction_map_df['category'] = 'return'
    return_transaction_map_df

    input_distribution_other_store_transaction_map_obj = InputDistributionOtherStoreTransactionMap.objects.filter(transaction_log__date__range=[start_date, end_date],transaction_log__agent_id=agent_id).order_by('transaction_log__date')
    other_store_transaction_map_obj = input_distribution_other_store_transaction_map_obj.values_list('transaction_log__id',
                                                                                'transaction_log__agent_id',
                                                                                'transaction_log__date',
                                                                                'transaction_log__agent__first_name',
                                                                                'transaction_log__wallet_balance_before_this_transaction',
                                                                                'transaction_log__amount',
                                                                                'transaction_log__wallet_balance_after_this_transaction')
    other_store_transaction_map_obj_column = ['agent_transaction_id','agent_id','date','agent_name', 'wallet_balance_before_this_transaction', 'amount', 'wallet_balance_after_this_transaction']
    other_store_transaction_map_obj_df = pd.DataFrame(list(other_store_transaction_map_obj), columns=other_store_transaction_map_obj_column)
    other_store_transaction_map_obj_df['category'] = 'Other store'
    other_store_transaction_map_obj_df


    # distribution_procurement_df = pd.merge(distribution_df, procurement_transaction_df, left_on='agent_transaction_id', right_on='agent_transaction_id', how='outer')
    distribution_return_procurement_df = pd.concat([distribution_df, procurement_transaction_df,return_transaction_map_df, other_store_transaction_map_obj_df])
    data_dict = distribution_return_procurement_df.to_dict('r')

    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def show_more_log_data(request):
    agent_transaction_id = request.data['agent_transaction_id']
    category = request.data['category']
    print(category)
    print(agent_transaction_id)
    if category == 'distribution':
        distribution_transaction_map_obj = InputDistributionTransactionMap.objects.filter(transaction_log_id=agent_transaction_id)
        distribution_transaction_map_values = distribution_transaction_map_obj.values_list('agent_inventory__agent__first_name', 'agent_inventory__combo_issue_request__input_combo__name','agent_inventory__quantity_at_receipt', 'agent_inventory__price_per_item', 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__amount', 'transaction_log__wallet_balance_after_this_transaction')
        distribution_transaction_columns = ['agent_name', 'product_name', 'product_qty', 'price_per_item', 'wallet_balance_before_transaction', 'amount','wallet_balance_after_transaction']
        distribution_transaction_df = pd.DataFrame(list(distribution_transaction_map_values), columns=distribution_transaction_columns)
        data_dict = distribution_transaction_df.to_dict('r')[0]
    elif category == 'procurement':
        procurement_transaction_map_obj = InputProcurementTransactionLog.objects.filter(transaction_log_id=agent_transaction_id)
        procurement_transaction_map_values = procurement_transaction_map_obj.values_list('procurement__procurement_group__agent__first_name', 'procurement__procurement_group__produce_net_weight','procurement__ticket_number', 'procurement__procurement_group__cost', 'procurement__procurement_group__agent_price_deduction', 'procurement__procurement_group__payment_to_wallet', 'procurement__procurement_group__payment_to_agent', 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__amount', 'transaction_log__wallet_balance_after_this_transaction')
        procurement_transaction_map_columns = ['agent_name', 'produce_weight','ticket_number', 'cost', 'agent_price_deduction','payment_to_wallet', 'payment_to_agent', 'wallet_balance_before_transaction', 'amount','wallet_balance_after_transaction']
        procurement_transaction_map_df = pd.DataFrame(list(procurement_transaction_map_values), columns=procurement_transaction_map_columns)
        data_dict = procurement_transaction_map_df.to_dict('r')[0]
    elif category == 'return':
        return_transaction_map_obj = InputReturnTransactionLog.objects.filter(transaction_log_id=agent_transaction_id)
        return_transaction_map_values = list(return_transaction_map_obj.values_list('combo_return_request__agent__first_name','combo_return_request_id', 'combo_return_request__input_combo__name', 'combo_return_request__comboreturnrequestlabelmap__return_label__label', 'combo_return_request__comboreturnrequestlabelmap__return_label__label', 'transaction_log__wallet_balance_before_this_transaction', 'transaction_log__wallet_balance_after_this_transaction', 'transaction_log__amount'))
        return_transaction_map_column = ['agent_name','return_request_id', 'input_combo', 'quantity', 'label', 'wallet_balance_before_transaction','amount' ,'wallet_balance_after_transaction']
        return_transaction_map_df = pd.DataFrame(return_transaction_map_values, columns=return_transaction_map_column)
        return_transaction_map_df = return_transaction_map_df.groupby('return_request_id').agg({'input_combo': 'first', 'wallet_balance_before_transaction':'first', 'amount': 'first','wallet_balance_after_transaction': 'first',  'label':list, 'quantity':'count'}).reset_index()
        return_transaction_map_df['label'] = return_transaction_map_df['label'].astype(str)
        data_dict = return_transaction_map_df.to_dict('r')[0]
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_transaction_history_data_for_farmer_date(request):
    date_list = list(set(list(AgentFarmerDistributionSowing.objects.filter(agent_id=request.data['agent_id']).values_list('dispatched_date', flat=True))))
    return Response(date_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_transaction_history_data_for_farmer(request):
    agent_distribution_sowing_list = list(AgentFarmerDistributionSowing.objects.filter(agent_id=request.data['agent_id'], dispatched_date=request.data['date']).values_list('dispatched_date', 'sowing__farmer__farmerclusterseasonmap__seasonal_farmer_code', 'input_combo__name', 'no_of_unit', 'acre'))                                   
    agent_distribution_sowing_column = ['date', 'farmer_code', 'input_combo', 'no_of_units', 'acre']
    agent_dist_df = pd.DataFrame(agent_distribution_sowing_list, columns=agent_distribution_sowing_column)
    data = agent_dist_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)

# obj = InputProcurementTransactionLog.objects.filter(transaction_log__id=agent_transaction_id, procurement__procurement_group__agent_id=agent_id, procurement__procurement_group__season_id=season_id)
# obj_val = obj.values_list('procurement__procurement_group__agent__first_name', 
#                           'procurement__ticket_number', 
#                           'procurement__procurement_group__cost', 
#                           'procurement__procurement_group__agent_price_deduction', 
#                           'procurement__procurement_group__payment_to_wallet', 
#                           'procurement__procurement_group__payment_to_agent')
# obj_columns = ['agent_name', 
#                'ticket_number', 
#                'cost', 
#                'agent_price_deduction',
#                'payment_to_wallet', 
#                'payment_to_agent']
# df = pd.DataFrame(list(obj_val), columns=obj_columns)
# df

@transaction.atomic
@api_view(['POST'])
@permission_classes((AllowAny,))
def procurement_delete_track(request):
    sid = transaction.savepoint()
    try:
        user_id = request.user.id
        ticket_number = request.data['ticket_number']
        item = Procurement.objects.get(ticket_number=ticket_number)
        transaction_log_id = InputProcurementTransactionLog.objects.get(procurement_id=item.id, transaction_log__transaction_direction_id=2).transaction_log.id
        agent_transaction_amount = AgentTransactionLog.objects.get(id=transaction_log_id).amount
        agent_id = AgentTransactionLog.objects.get(id=transaction_log_id).agent.id
        old_amount = AgentWallet.objects.get(agent_id=agent_id).current_balance
        wallet_adjusted_amount = old_amount - (agent_transaction_amount)
        AgentWallet.objects.filter(agent_id=item.procurement_group.agent.id).update(current_balance=Decimal(wallet_adjusted_amount))
        
        
        print('agent_wallet_adjusted')
        
        delete_procurement_log_obj = DeleteProcurementLog(ticket_number=ticket_number,
                                                        agent_id = item.procurement_group.agent.id,
                                                        produce_net_weight = item.procurement_group.produce_net_weight,
                                                        price_per_unit = Decimal(item.procurement_group.price_per_unit),
                                                        payment_to_wallet = Decimal(item.procurement_group.payment_to_wallet),
                                                        deleted_by_id=user_id)
        delete_procurement_log_obj.save()
            
        #     to_deletes_ticket_based_items
        if TempProcurement.objects.filter(ticket_number=ticket_number).exists():
            procurement_file_upload_id = TempProcurement.objects.get(ticket_number=ticket_number).procurement_file_upload.id
        
            curr_uploaded_count_obj = ProcurementFileUpload.objects.get(id=procurement_file_upload_id, season_id=get_active_season_id())
            curr_uploaded_count_obj.uploaded_count = curr_uploaded_count_obj.uploaded_count -1
            curr_uploaded_count_obj.save()
            TempProcurement.objects.filter(ticket_number=ticket_number).delete()
        if Harvest.objects.filter(ticket_number=ticket_number).exists():    
            Harvest.objects.filter(ticket_number=ticket_number).delete()
        AgentTransactionLog.objects.filter(id=transaction_log_id).delete()
        ProcurementGroup.objects.filter(id=item.procurement_group.id).delete()
        print('deleted')
        transaction.savepoint_commit(sid)
        return Response({}, status=status.HTTP_200_OK)
    except Exception as e:
        print('error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)


# @api_view(['GET'])
# def serve_season_start_and_end_date(request):
#     season_date_df = pd.DataFrame(Season.objects.all().values('id', 'start_date', 'end_date'))
#     season_date_dict = season_date_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
#     return Response(season_date_dict, status=status.HTTP_200_OK)


def generate_farmer_code_prefix(cluster_id, agent_id, officer_id, season_id):
    # season = Season.objects.get(id=season_id).year
    # season_name = str(season.strftime("%y"))
    # cluster_name = Cluster.objects.get(id=cluster_id).name.upper()
    # agent_name = UserClusterMap.objects.get(user_id=agent_id, season_id=season_id).unique_code.upper()
    # officer_name = User.objects.get(id=officer_id).username[0:1].upper()
    # prefix = season_name + cluster_name[0] + officer_name[0] + agent_name[0]
    season = Season.objects.get(id=season_id).year
    season_name = str(season.strftime("%y"))
    cluster_name = Cluster.objects.get(id=cluster_id).name.upper()
    region_name = Cluster.objects.get(id=cluster_id).notes.upper()
    agent_name = UserClusterMap.objects.get(user_id=agent_id, season_id=season_id).unique_code.upper()
    officer_name = User.objects.get(id=officer_id).username[0:1].upper()
    prefix = season_name + region_name[0] + cluster_name[0] + agent_name[0]
    return prefix

@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_farmer_code_prefix(request):
    season_id=get_active_season_id()
    procurment_id = request.data['procurment_id']
    print('procurment_id',procurment_id)
    if Procurement.objects.get(id=procurment_id).have_other_agent_farmer == False:
        print('have_other_agent_farmer: No')
        agent_id = Procurement.objects.get(id=procurment_id).procurement_group.agent.id
        agent_supervisor_id = AgentSupervisorSeasonMap.objects.get(season_id=season_id, agent_id=agent_id).supervisor_id
        agent_cluster_id = UserClusterMap.objects.get(season_id=season_id, user_id=agent_id).cluster_id
        prefix_code = generate_farmer_code_prefix(agent_cluster_id, agent_id, agent_supervisor_id, season_id)
        print(prefix_code)
    else:
        ''
    return Response(data=prefix_code, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def delete_temp_procurement_track(request):
    ticket_number = request.data['ticket_number']
    temp_procurement_obj = TempProcurement.objects.filter(ticket_number=ticket_number)
    for item in temp_procurement_obj:
        print(item.ticket_number)
        delete_temp_procurement_track_obj = DeleteTempProcurementTrack(ticket_number = item.ticket_number,
                                                    id_company = item.id_company,
                                                    customer_name = item.customer_name,
                                                    vehicle_number = item.vehicle_number,
                                                    vehicle_driver_name = item.vehicle_driver_name,
                                                    gross_weight = item.gross_weight,
                                                    gross_time = item.gross_time,
                                                    tare_weight = item.tare_weight,
                                                    tare_time = item.tare_time,
                                                    net_wt = item.net_wt,
                                                    bag_number = item.bag_number,
                                                    bag_weight = item.bag_weight,
                                                    net_weight = item.net_weight,
                                                    price = item.price,
                                                    amount = item.amount,
                                                    gross_operator = item.gross_operator,
                                                    moisture = item.moisture,
                                                    tare_operator = item.tare_operator,
                                                    date = item.date)
        delete_temp_procurement_track_obj.save()
        print('saved')
        temp_procurement_obj.delete()
        print('deleted')
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def get_farmer_sowing(request):
    season_id=get_active_season_id()
    print(season_id)
    print(request.data)
    farmer_sowing_list = list(Sowing.objects.filter(farmer_id=request.data['farmer_id'], season_id=season_id).values_list('id','crop__name', 'cultivation_phase__name', 'sowing_date', 
                                                                                                                            'area', 'water_source__name', 'water_type__name', 'soil_type__name', 
                                                                                                                            'irrigation_method__name', 'crop_id', 'cultivation_phase_id', 'water_source_id', 
                                                                                                                            'water_type_id', 'soil_type_id', 'irrigation_method_id'))
    farmer_sowing_column = ['sowing_id', 'crop', 'cultivation_phase', 'sowing_date', 'area', 'water_source', 'water_type', 'soil_type', 'irrigation_method', 'crop_id', 'cultivation_phase_id', 'water_source_id', 'water_type_id', 'soil_type_id', 'irrigation_method_id']
    farmer_sowing_df = pd.DataFrame(farmer_sowing_list, columns=farmer_sowing_column)
    farmer_sowing_df = farmer_sowing_df.fillna('')
    data_dict = farmer_sowing_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_farmer_sowing_input(request):
    data_dict = {
        'crop_list': list(Crop.objects.all().values('id', 'name')),
        'cultivation_phase_list': list(CultivationPhase.objects.all().values('id', 'name')),
        'irrigation_method_list': list(IrrigationMethod.objects.all().values('id', 'name')),
        'soil_type_list': list(SoilType.objects.all().values('id', 'name')),
        'water_source_list': list(WaterSource.objects.all().values('id', 'name')),
        'water_type_list': list(WaterType.objects.all().values('id', 'name')),
    }
    
    print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_farmer_sowing_detils(request):
    print(request.data)
    data = request.data
    sowing_obj = Sowing.objects.get(id=data['sowing_id'])
    sowing_obj.crop_id = data['crop_id']
    sowing_obj.cultivation_phase_id = data['cultivation_phase_id']
    sowing_obj.water_source_id = data['water_source_id']
    sowing_obj.water_type_id = data['water_type_id']
    sowing_obj.soil_type_id = data['soil_type_id']
    sowing_obj.irrigation_method_id = data['irrigation_method_id']
    sowing_obj.area = data['area']
    sowing_obj.sowing_date = data['sowing_date']
    sowing_obj.save()
    return Response(True, status=status.HTTP_200_OK)

    
@api_view(["GET"])
@permission_classes((AllowAny,))
def agent_input_items_report_status(request):
    data_dict = {
        "have_data" : False
    }
    agent_invetry_obj = AgentInventory.objects.filter(season_id=get_active_season_id()).order_by('agent_id')
    agent_invetry_values = list(agent_invetry_obj.values_list('agent_id','agent__userprofile__code', 'agent__first_name', 'agent__last_name', 'combo_issue_request__issue_rised_date','combo_issue_request__dispatch_status__name','combo_issue_request__dispatch_date','combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers','combo_issue_request__input_combo__price', 'combo_issue_request__comboissuerequestagentmap__shop__type__name'))
    agent_invetry_columns = ['Agent Id', 'Agent Code', 'Agent First Name', 'Agent Last Name', 'Request Rised Date','Dispatch Status','Dispatch Date','Input Combo Id','Product Name', 'Product Qty','Price Per Item', 'Shop Name']
    agent_invetry_df = pd.DataFrame(agent_invetry_values, columns=agent_invetry_columns)
    agent_invetry_df['Before Return Total Cost'] = (agent_invetry_df['Product Qty'] * agent_invetry_df['Price Per Item'])
    agent_invetry_df

    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=get_active_season_id(), combo_issue_request__max_status_id=6).exclude(shop__type_id=1).order_by('agent_id')
    combo_issue_request_agent_values = combo_issue_request_agent_obj.values_list('agent_id', 'agent__userprofile__code', 'agent__first_name', 'agent__last_name', 'issue_rised_date','combo_issue_request__dispatch_status__name','combo_issue_request__dispatch_date','combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__price', 'shop__type__name')
    column_names = ['Agent Id', 'Agent Code', 'Agent First Name', 'Agent Last Name', 'Request Rised Date','Dispatch Status','Dispatch Date', 'Input Combo Id','Product Name', 'Product Qty','Price Per Item', 'Shop Name']
    combo_issue_other_shop_df = pd.DataFrame(list(combo_issue_request_agent_values), columns=column_names)
    combo_issue_other_shop_df['Before Return Total Cost'] = (combo_issue_other_shop_df['Product Qty'] * combo_issue_other_shop_df['Price Per Item'])
    combo_issue_other_shop_df

    agent_invetry_other_shop_df = pd.concat([agent_invetry_df, combo_issue_other_shop_df])

    combo_return_request_obj = list(ComboReturnRequest.objects.filter(season_id=get_active_season_id()).values_list('id', flat=True))
    combo_return_request_label_obj = ComboReturnRequestLabelMap.objects.filter(combo_return_request_id__in=combo_return_request_obj)
    combo_return_request_label_val = combo_return_request_label_obj.values_list('combo_return_request__agent_id', 'combo_return_request__input_combo_id','combo_return_request__request_raised_date','combo_return_request__agri_officer_status__name','combo_return_request__agri_officer_status_date','combo_return_request__input_combo__name','return_label_id', 'combo_return_request__input_combo__price')
    column_names = ['Agent Id', 'Input Combo Id','Return Request Raised Date','Agri Officer Status','Agri Officer Status Date','Return Product Name','Return Qty','Price Per Item Return']
    return_df = pd.DataFrame(combo_return_request_label_val, columns=column_names)
    return_df = return_df.groupby(['Agent Id', 'Input Combo Id']).agg({'Return Request Raised Date':'first','Agri Officer Status':'first','Agri Officer Status Date':'first','Return Product Name':'first','Return Qty':'count','Price Per Item Return':'first'}).reset_index()
    return_df['Return Product Total Price'] = (return_df['Return Qty'] * return_df['Price Per Item Return'])
    return_df.groupby(['Agent Id','Input Combo Id']).agg({'Return Request Raised Date':'first','Agri Officer Status':'first','Agri Officer Status Date':'first','Return Product Name':'first',"Return Qty":"first",'Price Per Item Return':'first',"Return Product Total Price": sum}).reset_index()
    return_df

    merged_df = pd.merge(agent_invetry_other_shop_df, return_df, left_on=['Agent Id', 'Input Combo Id'], right_on=['Agent Id', 'Input Combo Id'], how='left')
    # merged_df.to_excel('agent_report.xlsx')
    merged_df['Final Total Cost'] = (merged_df['Before Return Total Cost'] - merged_df['Return Product Total Price']).astype(float)
    
    merged_df['Price Per Item Return'] = merged_df['Price Per Item Return'].astype(float)
    merged_df['Price Per Item'] = merged_df['Price Per Item'].astype(float)
    merged_df['Return Product Total Price'] = merged_df['Return Product Total Price'].astype(float)
    merged_df['Before Return Total Cost'] = merged_df['Before Return Total Cost'].astype(float)
    merged_df['Product Qty'] = merged_df['Product Qty'].astype(str)
    merged_df['Return Qty'] = merged_df['Return Qty'].astype(str)

    merged_df['Request Rised Date'] = pd.to_datetime(merged_df['Request Rised Date']).dt.date
    merged_df['Dispatch Date'] = pd.to_datetime(merged_df['Dispatch Date']).dt.date
    merged_df['Return Request Raised Date'] = pd.to_datetime(merged_df['Return Request Raised Date']).dt.date
    merged_df['Agri Officer Status Date'] = pd.to_datetime(merged_df['Agri Officer Status Date']).dt.date

    writer = pd.ExcelWriter(str("static/media/") + "agent_input_items_report_status.xlsx", engine="xlsxwriter",)
    final_df = merged_df

    if not final_df.empty:
        for agent in agent_invetry_obj:
            final_df1 = final_df[final_df['Agent Id'] == agent.agent.id]
            final_df1 = final_df1.drop(columns=['Agent Id','Input Combo Id'])
            final_df1.index += 1
            total = final_df1.sum(numeric_only=True)
            total.name = 'Total'
            final_df1 = final_df1.append(total.transpose())
            final_df1.to_excel(writer, sheet_name=str(agent.agent.first_name), startrow=1)
            workbook = writer.book
            worksheet = writer.sheets[str(agent.agent.first_name)]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                    }
                )
            date = datetime.datetime.today()
            # Merge 3 cells.
            worksheet.merge_range("A1:AC1", "Agent Input Items Report Status" + str(date), merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 28, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df1.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        data_dict['have_data'] = True
    try:
        image_path = str("static/media/") + "agent_input_items_report_status.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict["excel"] = encoded_image
    except Exception as err:    
        print('Error',err)
    print('excel Ok')
    return Response(data=data_dict , status=status.HTTP_200_OK) 


@api_view(["GET"])
@permission_classes((AllowAny,))
def agent_input_items_report_return_status(request):
    agent_invetry_obj = AgentInventory.objects.filter(season_id=get_active_season_id()).order_by('agent_id')
    agent_invetry_values = list(agent_invetry_obj.values_list('agent_id','agent__userprofile__code', 'agent__first_name', 'agent__last_name', 'combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers','combo_issue_request__input_combo__price', 'combo_issue_request__comboissuerequestagentmap__shop__type__name'))
    agent_invetry_columns = ['agent_id', 'agent_code', 'agent_first_name', 'agent_last_name', 'input_combo_id','product_name', 'product_qty','price_per_item', 'shop_name']
    agent_invetry_df = pd.DataFrame(agent_invetry_values, columns=agent_invetry_columns)
    agent_invetry_df['Before Return Total Cost'] = (agent_invetry_df['product_qty'] * agent_invetry_df['price_per_item'])
    agent_invetry_df

    combo_issue_request_agent_obj = ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=get_active_season_id(), combo_issue_request__max_status_id=6).exclude(shop__type_id=1).order_by('agent_id')
    combo_issue_request_agent_values = combo_issue_request_agent_obj.values_list('agent_id', 'agent__userprofile__code', 'agent__first_name', 'agent__last_name', 'combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__price', 'shop__type__name')
    column_names = ['agent_id', 'agent_code', 'agent_first_name', 'agent_last_name',  'input_combo_id','product_name', 'product_qty','price_per_item', 'shop_name']
    combo_issue_other_shop_df = pd.DataFrame(list(combo_issue_request_agent_values), columns=column_names)
    combo_issue_other_shop_df['Before Return Total Cost'] = (combo_issue_other_shop_df['product_qty'] * combo_issue_other_shop_df['price_per_item'])
    combo_issue_other_shop_df

    agent_invetry_other_shop_df = pd.concat([agent_invetry_df, combo_issue_other_shop_df])

    combo_return_request_obj = list(ComboReturnRequest.objects.filter(season_id=get_active_season_id()).values_list('id', flat=True))
    combo_return_request_label_obj = ComboReturnRequestLabelMap.objects.filter(combo_return_request_id__in=combo_return_request_obj)
    combo_return_request_label_val = combo_return_request_label_obj.values_list('combo_return_request__agent_id', 'combo_return_request__input_combo_id','combo_return_request__input_combo__name','return_label_id', 'combo_return_request__input_combo__price')
    column_names = ['agent_id', 'input_combo_id','return_product_name','return_qty','price_per_item_return']
    return_df = pd.DataFrame(combo_return_request_label_val, columns=column_names)
    return_df = return_df.groupby(['agent_id', 'input_combo_id']).agg({'return_product_name':'first','return_qty':'count','price_per_item_return':'first'}).reset_index()
    return_df['return_product_total_price'] = (return_df['return_qty'] * return_df['price_per_item_return'])
    return_df.groupby(['agent_id','input_combo_id']).agg({'return_product_name':'first',"return_qty":"first",'price_per_item_return':'first',"return_product_total_price": sum}).reset_index()
    return_df

    merged_df = pd.merge(agent_invetry_other_shop_df, return_df, left_on=['agent_id', 'input_combo_id'], right_on=['agent_id', 'input_combo_id'], how='left')
    # merged_df.to_excel('agent_report.xlsx')
    merged_df['final_total_cost'] = (merged_df['Before Return Total Cost'] - merged_df['return_product_total_price'])

    # merged_df['request_rised_date'] = pd.to_datetime(merged_df['request_rised_date']).dt.date
    # merged_df['dispatch_date'] = pd.to_datetime(merged_df['dispatch_date']).dt.date
    # merged_df['return_request_raised_date'] = pd.to_datetime(merged_df['return_request_raised_date']).dt.date
    # merged_df['agri_officer_status_date'] = pd.to_datetime(merged_df['agri_officer_status_date']).dt.date

    writer = pd.ExcelWriter(str("static/media/") + "agent_input_items_report_return_status.xlsx", engine="xlsxwriter",)
    final_df = merged_df

    for agent in agent_invetry_obj:
        final_df1 = final_df[final_df['agent_id'] == agent.agent.id]
        final_df1 = final_df1.drop(columns=['agent_id','input_combo_id'])
        final_df1.to_excel(writer, sheet_name=str(agent.agent.first_name), startrow=1, index=False)
        workbook = writer.book
        worksheet = writer.sheets[str(agent.agent.first_name)]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
                }
            )
        date = datetime.datetime.today()
        # Merge 3 cells.
        worksheet.merge_range("A1:AC1", "agent_input_items_report_return_status" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 28, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df1.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    data_dict = {}
    try:
        image_path = str("static/media/") + "agent_input_items_report_return_status.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict["excel"] = encoded_image
    except Exception as err:    
        print('Error',err)
    print('excel Ok')
    return Response(data=data_dict , status=status.HTTP_200_OK) 


@api_view(["GET"])
def agent_mergeload_status(request):
    agent_merge_obj = AgentMergeloadEnable.objects.filter(season_id=get_active_season_id()).order_by('agent__first_name')
    agent_merge_values = agent_merge_obj.values_list('agent_id', 'agent__userprofile__code','agent__first_name', 'is_active') 
    agent_merge_col = ['agent_id','agent_code', 'agent_name', 'is_active']
    df = pd.DataFrame(list(agent_merge_values), columns=agent_merge_col)
    data_dict = df.to_dict('r')
    print(len(data_dict))
    return Response(data=data_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
def agent_mergeload_enable(request):
    agent_id = request.data['agent_id']
    print('agent_id:', agent_id)
    agent_merge_obj = AgentMergeloadEnable.objects.get(season_id=get_active_season_id(), agent_id=agent_id)
    previous_enable_status = agent_merge_obj.is_active
    print(previous_enable_status)
    print(not previous_enable_status)
    agent_merge_obj.is_active = not previous_enable_status
    agent_merge_obj.save()
    print(agent_merge_obj.is_active)
    print('saved')
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def nursery_geo_fencing_area(request):
    season_id = get_active_season_id()
    data={}
    if Sowing.objects.filter(season_id=season_id, area_calculated_via_geo_fencing__isnull=False).exists():
        print('yes')
        if Sowing.objects.filter(season_id=season_id, cultivation_phase_id=1).exists():
            print('nursery_exists')
            sowing_nursery_obj = Sowing.objects.filter(season_id=season_id, cultivation_phase_id=1).exclude(area_calculated_via_geo_fencing__isnull=True)
            sowing_nursery_obj_count = Sowing.objects.filter(season_id=season_id, cultivation_phase_id=1).exclude(area_calculated_via_geo_fencing__isnull=True).count()
            print(sowing_nursery_obj_count)
            
            sowing_nursery_values = list(sowing_nursery_obj.values_list( "id", "sowing_date", "cultivation_phase__name","area", "area_calculated_via_geo_fencing", "farmer_id", "farmer__first_name"))
            sowing_columns = ["id", "sowing_date", "cultivation_phase_name", "area", "area_calculated_via_geo_fencing", "farmer_id", "farmer_first_name",]
            sowing_df = pd.DataFrame(sowing_nursery_values, columns=sowing_columns)
            
            farmer_ids = list(Sowing.objects.filter(season_id=season_id,cultivation_phase_id=1).exclude(area_calculated_via_geo_fencing__isnull=True).values_list("farmer_id", flat=True))
            
            farmer_cluster_values = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id__in=farmer_ids).values_list("id", "cluster__name", "cluster_id", "farmer_id", "seasonal_farmer_code"))
            farmer_cluster_columns = ["id", "cluster__name", "cluster_id", "farmer_id", "farmer_code"]
            farmer_cluster_df = pd.DataFrame(farmer_cluster_values, columns=farmer_cluster_columns)
            
            farmer_agent_values = list(AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list("id", "farmer_id__farmer_id", "agent__first_name"))
            farmer_agent_columns = ["id", "farmer_id", "agent_name"]
            farmer_agent_df = pd.DataFrame(farmer_agent_values, columns=farmer_agent_columns)

            merged_df = pd.merge(sowing_df, farmer_cluster_df, left_on="farmer_id", right_on="farmer_id", how="left",)
            agent_merged_df = pd.merge(merged_df, farmer_agent_df, left_on="farmer_id", right_on="farmer_id", how="left",)
            df = agent_merged_df.fillna(0)
            df = df.drop(["id_x", "id", "farmer_id", "id_y", "cluster_id"], axis=1)

            # excel convert
            writer = pd.ExcelWriter(str("static/media/") + "farmer_nursery_geo_fencing.xlsx", engine="xlsxwriter")
            df.to_excel(writer, sheet_name="Sheet1", startrow=1)

            # assigning that sheet to obj
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                }
            )

            date = datetime.datetime.now().date()
            # Merge 3 cells.
            worksheet.merge_range("A1:J1", "farmer_nursery_geo_fencing" + str(date), merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 20, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            # Write the column headers with the defined format.
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num + 1, value, header_format)
            writer.save()
            try:
                image_path = str("static/media/") + "farmer_nursery_geo_fencing.xlsx"
                with open(image_path, "rb") as image_file:
                    encoded_image = b64encode(image_file.read())
                    data["excel"] = encoded_image
            except Exception as err:
                print(err)
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def get_non_supplied_farmer_list_all_cluster(request):
    data = {}
    season_id = request.data['season_id']
    data_dict_from_interface = request.data
    print('data_dict_from_interface', data_dict_from_interface)
    cluster_ids = list(ClusterSeasonMap.objects.filter(season_id=season_id).values_list("cluster", flat=True))
    user_type_id = UserProfile.objects.get(user=request.user).user_type.id
    print(user_type_id)
    user_id = request.user.id
    print(user_id)
    if user_type_id == 5:
        subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id=request.user.id, season_id=season_id).values_list('agent_id', flat=True))
    else:
        if user_type_id == 3:
            if UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id).exists():
                subordinates = UserHierarchyMap.objects.filter(superior_id=user_id, season_id=season_id)
                subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
                print("one")
                print(subordinate_user_ids)
                subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(supervisor_id__in=subordinate_user_ids, season_id=season_id).values_list('agent_id',flat=True))
                print(len(subordinate_user_ids))
        else:
            subordinate_user_ids = list(AgentSupervisorSeasonMap.objects.filter(season_id=season_id).values_list('agent_id',flat=True))
    print(subordinate_user_ids)
    subordinate_user_ids = list(set(subordinate_user_ids))
    # subordinate_user_ids = list(UserProfile.objects.filter(user_id__in=subordinate_user_ids, user_type_id=user_type_id).values_list("user_id", flat=True))

    if AgentFarmerMap.objects.filter(agent_id__in=subordinate_user_ids, farmer__season_id=season_id).exists():
        print('exetessoko')
        filter_farmer_ids = list(AgentFarmerMap.objects.filter(agent_id__in=subordinate_user_ids, farmer__season_id=season_id).values_list("farmer__farmer_id", flat=True))
        farmer_ids = Harvest.objects.filter(sowing__season_id=season_id).values_list("sowing__farmer__id", flat=True)
        filtered_farmer_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id, farmer_id__in=filter_farmer_ids).exclude(farmer_id__in=farmer_ids).values_list("farmer__id", flat=True))
        
        cluster_farmer_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id, cluster_id__in=cluster_ids)
        cluster_farmer_values = list(cluster_farmer_obj.filter(farmer_id__in=filter_farmer_ids, season_id=season_id).exclude(farmer_id__in=farmer_ids).values_list("id","cluster__name", "cluster__id", "farmer_id", "farmer__first_name", "farmer__last_name", "farmer__village__name", "seasonal_farmer_code",))
        cluster_farmer_columns = ["id","cluster_name","cluster_id","farmer_id","farmer_first_name","farmer_last_name","farmer_village_name","farmer_code",]
        cluster_farmer_df = pd.DataFrame(cluster_farmer_values, columns=cluster_farmer_columns)
        # filtering sowing objs based on option selected
        sowing_obj = Sowing.objects.filter(season_id=season_id)

        sowing_values = list(sowing_obj.filter(farmer_id__in=filtered_farmer_ids, season_id=season_id, cultivation_phase_id=2).values_list("id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase__name",))
        sowing_columns = ["sowing_id","farmer_id","sowing_date","area","cultivation_phase_id","cultivation_phase_name"]
        sowing_df = pd.DataFrame(sowing_values, columns=sowing_columns)

        # converted_today = datetime.datetime.strptime(, '%Y-%m-%d')
        today = datetime.datetime.now().date()
        sowing_df["crop_age"] = today - sowing_df["sowing_date"]
        sowing_df["crop_age"] = sowing_df["crop_age"].astype("timedelta64[D]")
        sowing_df["crop_age"] = sowing_df["crop_age"].astype(int)
        farmer_sowing_merged_df = pd.merge(cluster_farmer_df,sowing_df,left_on="farmer_id",right_on="farmer_id",how="left")

        if "age_greater_than" in data_dict_from_interface:
            farmer_sowing_merged_df = farmer_sowing_merged_df[farmer_sowing_merged_df["crop_age"] >= int(data_dict_from_interface["age_greater_than"])]

        if "age_lesser_than" in data_dict_from_interface:
            farmer_sowing_merged_df = farmer_sowing_merged_df[farmer_sowing_merged_df["crop_age"]<= int(data_dict_from_interface["age_lesser_than"])]

        farmer_cluster_map_ids = list(FarmerClusterSeasonMap.objects.filter(season_id=season_id).exclude(farmer_id__in=farmer_ids).values_list("id", flat=True))
        agent_farmer_map_values = list(AgentFarmerMap.objects.filter(farmer_id__in=farmer_cluster_map_ids).values_list("id", "farmer__farmer_id", "agent__first_name", "agent__last_name"))
        agent_farmer_map_columns = [ "agent_map_id", "farmer_id", "agent_first_name", "agent_last_name",]
        agent_farmer_map_df = pd.DataFrame(agent_farmer_map_values, columns=agent_farmer_map_columns)

        df = pd.merge(farmer_sowing_merged_df,agent_farmer_map_df,left_on="farmer_id",right_on="farmer_id",how="left",)
        df = df.drop(["id","cluster_id","farmer_id","sowing_id","cultivation_phase_id","agent_map_id",], axis=1,)
        df = df.fillna(0)
        # print(df)
        writer = pd.ExcelWriter(str("static/media/") + "Non-supplied_farmers_all_cluster.xlsx", engine="xlsxwriter")
        final_df = df    

        print(final_df.columns)

        final_df = final_df.rename(columns= {'cluster_name' : 'Cluster Name', 'farmer_first_name' : 'Farmer First Name', 'farmer_last_name' : 'Farmer Last Name',
       'farmer_village_name' : 'Farmer Village Name', 'farmer_code' : 'Farmer Code', 'sowing_date' : 'Sowing Date', 'area' : 'Area',
       'cultivation_phase_name' : 'Cultivation Phase Name', 'crop_age' : 'Crop Age', 'agent_first_name' : 'Agent First Name',
       'agent_last_name' : 'Agent Last Name'})
        # creating excel sheet with name
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1, index=False)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:L1", "Non-supplied_farmers_all_cluster " + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "Non-supplied_farmers_all_cluster.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
        return Response(data=data, status=status.HTTP_200_OK)
    
def to_find_cost(allowance_type_id, user_type_id):
    print(allowance_type_id, user_type_id)
    allowance_df = pd.DataFrame(UsertypewiseAllowanceCost.objects.filter().values('user_type_id', 'allowance_type_id','cost'))
    df = allowance_df[(allowance_df['user_type_id']==user_type_id ) & (allowance_df['allowance_type_id']==allowance_type_id)]
    print(float(df['cost']))
     # user_allowance_df['cost'] = user_allowance_df.apply(lambda x: to_find_cost(x['allowance_type_id'], x['user_type_id']), axis=1)
     # user_allowance_df['description'] = Allowance.objects.get(date=request.data['date'], user_id=request.user.id).description
    return float(df['cost'])





@api_view(['POST'])
def allowance_type_new(request):
    print(request.data)
    date = request.data['date']
    user_id=request.user.id
    season_id=get_active_season_id()
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id

    food_list = []
    travel_list = []
    stay_list = []
    master_list = []
    master_dict = {}
    stay_approve= {}

    if Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id).exists():
        print('existed')
        allowance_ids = list(Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id).exclude(allowance_status_id=3).values_list('allowance_type_id', flat=True))
        print(allowance_ids)

        user_allowance_ids = list(UsertypewiseAllowanceCost.objects.filter(user_type_id=user_type_id).exclude(allowance_type_id__in=allowance_ids).values_list('allowance_type_id', flat=True))
        for id in user_allowance_ids:
            if id == 1:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #food
                    food_dict = {'user_allowance_id': item.id,
                                # 'allowance_type_id': item.allowance_type_id,
                                'allowance_type_name': item.allowance_type.name,
                                'expence_type_id': item.expence_type_id,
                                'expence_type_name': item.expence_type.name,
                                'food':  True
                                }
                    food_list.append(food_dict)
                master_dict['food'] = food_list
            elif id == 2:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #travl
                    travel_dict = {'user_allowance_id': item.id,
                                'allowance_type_id': item.allowance_type_id,
                                'allowance_type_name': item.allowance_type.name,
                                'expence_type_id': item.expence_type_id,
                                'expence_type_name': item.expence_type.name,
                                'cost': item.cost
                                }
                    travel_list.append(travel_dict)
                master_dict['travel'] = travel_list
            elif id == 3:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #stay
                    stay_dict = {'user_allowance_id': item.id,
                                'allowance_type_id': item.allowance_type_id,
                                'allowance_type_name': item.allowance_type.name,
                                'expence_type_id': item.expence_type_id,
                                'expence_type_name': item.expence_type.name,
                                'stay_request': False
                                }
                    stay_list.append(stay_dict)
        if Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id, allowance_type_id=3, max_status_id__in=[4,6], allowance_status_id=1).exists():
            print('yes')
            stay_approve['req_status'] = True
            stay_approve['id'] = Allowance.objects.get(season_id=season_id, date=date, user_id=user_id, allowance_type_id=3, max_status_id__in=[4,6], allowance_status_id=1).id
            stay_approve['cost'] = UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=3).cost
        master_list.append(master_dict)
        master_list.append(user_allowance_ids)
        master_list.append(stay_approve)
    else:
        print('fresh_user')
        allowance_obj = list(AllowanceType.objects.filter().values_list('id', flat=True))
        for id in allowance_obj:
            if id == 1:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #food
                    food_dict = {'user_allowance_id': item.id}
                    food_list.append(food_dict)
                master_dict['food'] = food_list
            elif id == 2:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #travl
                    travel_dict = {'user_allowance_id': item.id,
                                'allowance_type_id': item.allowance_type_id,
                                'allowance_type_name': item.allowance_type.name,
                                'expence_type_id': item.expence_type_id,
                                'expence_type_name': item.expence_type.name,
                                'cost': item.cost
                                }
                    travel_list.append(travel_dict)
                master_dict['travel'] = travel_list
            else:
                user_allowance_obj = UsertypewiseAllowanceCost.objects.filter(allowance_type_id=id, user_type_id=user_type_id)
                for item in user_allowance_obj:
                    #stay
                    stay_dict = {'user_allowance_id': item.id,}
                    stay_list.append(stay_dict)
                master_dict['stay'] = stay_list
        master_list.append(master_dict)
        master_list.append(allowance_obj)
    print(master_list)
    return Response(data=master_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def allowance_type(request):
    print(request.data)
    date = request.data['date']
    user_id=request.user.id
    season_id=get_active_season_id()
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id

    if Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id, allowance_status_id__in=[2,3]).exists():
        user_allowance_ids = list(Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id, allowance_status_id__in=[2,3]).values_list('allowance_type_id', flat=True))
        allowance_obj = AllowanceType.objects.filter().exclude(id__in=user_allowance_ids).values_list('id', 'name')
        print('allowance_obj', allowance_obj)
        column=["allowance_type_id","allowance_name"]
        user_allowance_df = pd.DataFrame(allowance_obj, columns=column)
        if not user_allowance_df.empty:
            user_allowance_df['cost']=UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=2).cost
            user_allowance_df['stay_allowance']=UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=3, expence_type_id=3).cost
            user_allowance_dict = user_allowance_df.to_dict('r')
    else:
        print('fresh')
        user_allowance_ids = list(Allowance.objects.filter(season_id=season_id, date=date, user_id=user_id).values_list('allowance_type_id', flat=True))
        print(user_allowance_ids)
        user_allowance_cost = UsertypewiseAllowanceCost.objects.filter(user_type_id=user_type_id).values_list('allowance_type_id','allowance_type__name', 'user_type_id')
        print('user_allowance_cost', user_allowance_ids)
        columns=["allowance_type_id","allowance_name", "user_type_id"]
        user_allowance_df = pd.DataFrame(list(user_allowance_cost), columns=columns)
        user_allowance_df = user_allowance_df.groupby(['allowance_type_id']).agg({'allowance_name': 'first', 'user_type_id': 'first'}).reset_index()
        user_allowance_df['user_id']=user_id
        user_allowance_df['cost']=UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=2).cost
        user_allowance_df['stay_allowance']=UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=3, expence_type_id=3).cost
        user_allowance_df['stay_req_status']=False
        user_allowance_dict = user_allowance_df.to_dict('r')
    return Response(data=user_allowance_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def allow_food_allowance(request):
    print(request.data)
    food_cost = request.data['food_allowance']
    user_id=request.user.id
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    if food_cost == True:
        user_allowance_cost = UsertypewiseAllowanceCost.objects.filter(user_type_id=user_type_id).values_list('allowance_type_id','allowance_type__name', 'cost','expence_type__name','user_type_id')
        columns=["allowance_type_id","allowance_name", "cost", "expence_type_name","user_type_id"]
        user_food_allowance_df = pd.DataFrame(list(user_allowance_cost), columns=columns)
        user_food_allowance_df['user_id']=user_id
        user_food_allowance_dict = user_food_allowance_df.groupby('expence_type_name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    return Response(data=user_food_allowance_dict, status=status.HTTP_200_OK)

@api_view(["POST"])
@transaction.atomic
def allowance_save(request):
    sid = transaction.savepoint()
    print(request.data)
    try:
        season_id = get_active_season_id()
        from_kilometre = request.data['from_kilometre']
        to_kilometre = request.data['to_kilometre']
        created_by_id = request.user.id
        user_id = request.user.id
        date = request.data['date']
        description = request.data['description']
        total_cost = request.data['total_cost']
        food_allowance = request.data['food_allowance']
        stay_allowance = request.data['stay_allowance']
        allowance_id = request.data['allowance_id']
        
        user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
        print(user_type_id)

        if total_cost != None:
            if total_cost > 0:
                print('Travel')
                allowance_type_id = 2
                fixed_travel_cost = UsertypewiseAllowanceCost.objects.get(user_type_id=user_type_id, allowance_type_id=allowance_type_id).cost
                print(fixed_travel_cost)
                travelled_kilometre = Decimal(to_kilometre) - Decimal(from_kilometre)
                print(Decimal(travelled_kilometre))
                fuel_cost = fixed_travel_cost*travelled_kilometre
                print(fuel_cost)
                
                allowance_obj = Allowance(
                                        season_id = season_id,
                                        user_id = user_id,
                                        allowance_type_id = allowance_type_id,
                                        cost = fuel_cost,
                                        date = date,
                                        travelled_kilometre = travelled_kilometre,
                                        created_by_id = created_by_id,
                                        allowance_status_id = 2,
                                        description = description
                                    )
                allowance_obj.save()
                
                travel_allowance_details_obj = TravelAllowanceDetilas(allowance_id=allowance_obj.id,
                                                                    from_kilometre = from_kilometre,
                                                                    date = date,
                                                                    to_kilometre = to_kilometre,
                                                                    from_captured_image = decode_image(request.data['from_img']),
                                                                    to_captured_image = decode_image(request.data['to_img']))
                travel_allowance_details_obj.save()
                print('travel_saved')
        if food_allowance == True:
            if request.data['food_amount'] != 0:
                allowance_type_id = 1
                food_cost = request.data['food_amount']
                print('food_cost', food_cost)
                allowance_obj = Allowance(
                                        season_id = season_id,
                                        user_id = user_id,
                                        allowance_type_id = allowance_type_id,
                                        cost = food_cost,
                                        date = date,
                                        allowance_status_id = 2,
                                        created_by_id = created_by_id,
                                        description = description
                                    )
                allowance_obj.save()
                print('food_saved')
            else:
                return Response(data=False, status=status.HTTP_200_OK)
        if stay_allowance == True:
            stay_cost = request.data['stay_allowance_cost']
            print('stay_cost', stay_cost)
            allowance_obj = Allowance.objects.get(id=allowance_id)
            allowance_obj.cost = stay_cost
            allowance_obj.description = description
            allowance_obj.allowance_status_id = 2
            allowance_obj.save()
            print('stay_saved')
            transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_404_NOT_FOUND)


def reset_stay_allownace(allowance_rised_obj):
    allowance_rised_obj.max_status_id = 2
    allowance_rised_obj.gm_status_id = None
    allowance_rised_obj.gm_id = None
    allowance_rised_obj.gm_status_date =  None

    allowance_rised_obj.assitant_manager_id = None
    allowance_rised_obj.assitant_manager_status_id = None
    allowance_rised_obj.assitant_manager_status_date = None

    allowance_rised_obj.senior_supervisor_id = None
    allowance_rised_obj.senior_supervisor_status_id = None
    allowance_rised_obj.senior_supervisor_status_date = None

    allowance_rised_obj.allowance_status_id = 1
    allowance_rised_obj.save() 
    

@api_view(["POST"])
def user_stay_request(request):
    print(request.data)
    date = request.data['date']
    season_id = get_active_season_id()
    stay_request = request.data['stay_request']
    user_id = request.user.id
    print(user_id)
    user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
    print('user_type_id.............',user_type_id)
    if user_type_id == 5:
        print('in')
        if stay_request == 1:
            if Allowance.objects.filter(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3).exists():
                allowance_rised_obj = Allowance.objects.get(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3)
                reset_stay_allownace(allowance_rised_obj)
            else:
                print('notexis')
                allowance_obj = Allowance(season_id = season_id,
                                        date = date,
                                        user_id = user_id,
                                        max_status_id = 2,
                                        allowance_status_id = 1,
                                        allowance_type_id = 3,
                                        max_status_date = date,
                                        created_by_id = user_id)
                allowance_obj.save()
                print('stay_allowance_reqested_AFS')
    elif user_type_id == 3:
        if stay_request == 1:
            if Allowance.objects.filter(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3).exists():
                allowance_rised_obj = Allowance.objects.get(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3)
                reset_stay_allownace(allowance_rised_obj)

            else:
                print('notexis')
                allowance_obj = Allowance(season_id = season_id,
                                        date = date,
                                        user_id = user_id,
                                        max_status_id = 2,
                                        allowance_status_id = 1,
                                        allowance_type_id = 3,
                                        max_status_date = date,
                                        created_by_id = user_id)
                allowance_obj.save()
                print('stay_allowance_reqested_SFS')
    elif user_type_id == 2:
        if stay_request == 1:
            if Allowance.objects.filter(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3).exists():
                allowance_rised_obj = Allowance.objects.get(user_id=user_id, date=date, allowance_type_id=3, allowance_status_id=3)
                reset_stay_allownace(allowance_rised_obj)
            else:
                print('notexis')
                allowance_obj = Allowance(season_id = season_id,
                                        date = date,
                                        user_id = user_id,
                                        max_status_id = 2,
                                        allowance_status_id = 1,
                                        allowance_type_id = 3,
                                        max_status_date = date,
                                        created_by_id = user_id)
                allowance_obj.save()
                print('stay_allowance_reqested_Manager')
    else:
        print('wait')
    return Response(data='request_rised', status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_stay_requested_user(request):
    from django.db.models import Q
    user_id = request.user.id
    season_id = get_active_season_id()
    user_ids = list((UserProfile.objects.filter(user_type_id=3).values_list('user_id', flat=True)))
    afs_ids = list((UserProfile.objects.filter(user_type_id=5).values_list('user_id', flat=True)))
    am_ids = list((UserProfile.objects.filter(user_type_id=2).values_list('user_id', flat=True)))

    if UserProfile.objects.get(user_id=request.user.id).user_type_id==3:
        subordinates = UserHierarchyMap.objects.filter(superior_id=request.user.id, season_id=season_id)
        subordinate_user_ids = list(subordinates.values_list("subordinate", flat=True))
        stay_req_obj = Allowance.objects.filter(created_by_id__in=subordinate_user_ids, season_id=season_id, max_status_id__in=[2]).order_by('date')
    else:
        # stay_req_obj = Allowance.objects.filter(season_id=season_id, max_status_id=2).filter(user_id__in=user_ids)
        if UserProfile.objects.get(user_id=request.user.id).user_type_id==2:
            stay_req_obj = Allowance.objects.filter(Q(max_status_id=2) & Q(user_id__in=user_ids) | Q(max_status_id=3) & Q(user_id__in=afs_ids) | Q(max_status_id=2) & Q(user_id__in=am_ids))
        elif UserProfile.objects.get(user_id=request.user.id).user_type_id==1:
            stay_req_obj = Allowance.objects.filter(Q(max_status_id=2) & Q(user_id__in=am_ids))
    stay_req_obj = stay_req_obj.values_list('id' ,'user_id', 'date','user__first_name', 'user__username','allowance_type__name', 'max_status_id', 'max_status__name')
    columns = ["id", "user_id", "Date",'Name', "username", 'allowance', "max_status_id", "max_status_name"]
    stay_req_df = pd.DataFrame(list(stay_req_obj), columns=columns)
    stay_req_dict = stay_req_df.to_dict('r')
    return Response(data=stay_req_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def approve_or_decline_stay_request(request):
    user_id = request.user.id
    season_id = get_active_season_id()
    allowance_request_obj = Allowance.objects.get(id=request.data['id'])
    user_type_id = UserProfile.objects.get(user_id=request.user.id).user_type_id
    username = ''
    if request.data['status'] == 1:
        status_name = 'Approved'
    else:
        status_name = 'Declined'

    if user_type_id == 3:
        if request.data['max_status_id'] == 2:
            if request.data['status'] == 1:
                allowance_request_obj.max_status_id = 3
                allowance_request_obj.max_status_date = datetime.datetime.now()
            else:
                allowance_request_obj.max_status_id = 7
                allowance_request_obj.max_status_date = datetime.datetime.now()
                allowance_request_obj.allowance_status_id = 3
            allowance_request_obj.senior_supervisor_id = request.user.id
            allowance_request_obj.senior_supervisor_status_id = request.data['status']
            allowance_request_obj.senior_supervisor_status_date = datetime.datetime.now()
            

            title = "New Request for approval : " + " is approved"
            body = request.user.username + ' have ' + status_name + ' the stay request - ' + "is approved"
            user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=2).values_list('user_id',flat=True))
            send_notification(title,body,user_ids)
            print(request.user.username + ' have ' + status_name + ' the stay request - ' + 'approved')
            allowance_request_obj.save()

    elif user_type_id == 2:
        if request.data['max_status_id'] == 3 or request.data['max_status_id'] == 2:
            if request.data['status'] == 1:
                allowance_request_obj.max_status_id = 4
                allowance_request_obj.max_status_date = datetime.datetime.now()
            else:
                allowance_request_obj.max_status_id = 7
                allowance_request_obj.max_status_date = datetime.datetime.now()
                allowance_request_obj.allowance_status_id = 3
                
            allowance_request_obj.assitant_manager_id = request.user.id
            allowance_request_obj.assitant_manager_status_id = request.data['status']
            allowance_request_obj.assitant_manager_status_date = datetime.datetime.now()
            title = "New Request for approval : " + " is approved"
            body = request.user.username + ' have ' + status_name + ' the stay request - ' + "is approved"
            user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=2).values_list('user_id',flat=True))
            send_notification(title,body,user_ids)
            print(request.user.username + ' have ' + status_name + ' the stay request - ' + 'approved')
            allowance_request_obj.save()
           
    elif user_type_id == 4:
        if request.data['max_status_id'] == 4:
            if request.data['status'] == 1:
                allowance_request_obj.max_status_id = 5
                allowance_request_obj.max_status_date = datetime.datetime.now()
            else:
                allowance_request_obj.max_status_id = 7
                allowance_request_obj.max_status_date = datetime.datetime.now()
                allowance_request_obj.allowance_status_id = 3

            allowance_request_obj.agri_officer_id = request.user.id
            allowance_request_obj.agri_officer_status_id = request.data['status']
            allowance_request_obj.agri_officer_status_date = datetime.datetime.now()
            allowance_request_obj.save()
            print(request.user.username + ' have ' + status_name + ' the request - ' + 'approved')
            title = "New Request for approval : " + " is approved"
            body = request.user.username + ' have ' + status_name + ' the stay request - ' + "is approved"
            user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=2).values_list('user_id',flat=True))
            send_notification(title,body,user_ids)

    elif user_type_id == 1:  
        if request.data['max_status_id'] == 2:
            if request.data['status'] == 1:
                allowance_request_obj.max_status_id = 6
                allowance_request_obj.max_status_date = datetime.datetime.now()
            else:
                allowance_request_obj.max_status_id = 7
                allowance_request_obj.max_status_date = datetime.datetime.now()               
                allowance_request_obj.allowance_status_id = 3

            allowance_request_obj.gm_id = request.user.id
            allowance_request_obj.gm_status_id = request.data['status']
            allowance_request_obj.gm_status_date = datetime.datetime.now()
            allowance_request_obj.save()
    
    print(request.user.username + ' have ' + status_name + ' the request - ' + 'approved')
    title = "New Request for approval : " + " is approved"
    body = request.user.username + ' have ' + status_name + ' the stay request - ' + "is approved"
    user_ids = list(PositionPositionUserMap.objects.filter(user__userprofile__user_type_id=2).values_list('user_id',flat=True))
    send_notification(title,body,user_ids)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def view_submitted_allowances(request):
    print(request.user.id)
    season_id = get_active_season_id()
    allowance_obj = Allowance.objects.filter(season_id=season_id, user_id=request.user.id).order_by('-date')
    print(allowance_obj)
    allowance_values = allowance_obj.values_list('user_id','user__first_name','allowance_type_id','allowance_type__name', 'cost', 'date', 'travelallowancedetilas__from_kilometre', 'travelallowancedetilas__to_kilometre', 'travelled_kilometre')
    columns = ["user_id","user_name","allowance_type_id", "allowance_name", "cost", "date" ,"from_km", "to_km", "travelled_kilometre"]
    allowance_df = pd.DataFrame(list(allowance_values), columns=columns)
    final_df = allowance_df.fillna('-')
    final_dict = final_df.to_dict('r')
    return Response(data=final_dict, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_senior_assitant_supervisor(request):
    type_ids = [3,5,2]
    season_id = get_active_season_id()
    senior_assitant_supervisor_obj = UserHierarchyMap.objects.filter(superior_user_type_id__in=type_ids).values_list('superior_id', 'superior_id__first_name', 'superior_id__username')
    columns = ["id", "first_name", "username"]
    senior_assitant_supervisor_df= pd.DataFrame(list(set(senior_assitant_supervisor_obj)), columns=columns)
    final_dict=senior_assitant_supervisor_df.to_dict('r')
    return  Response(data=final_dict, status=status.HTTP_200_OK)


def to_find_travel_price(date, user_id):
    print(date, user_id)
    if Allowance.objects.filter(date=date, user_id=user_id, allowance_type_id=2).exists():
        return Allowance.objects.get(date=date, user_id=user_id, allowance_type_id=2).cost
    else:
        return 0

def check_exist(date, user_id):
    if Allowance.objects.filter(date=date, user_id=user_id, allowance_type_id=1).exists():
        return Allowance.objects.get(date=date, user_id=user_id, allowance_type_id=1).cost
    else:
        return 0
    
def to_get_travel_description(date, user_id):
    if Allowance.objects.filter(date=date, user_id=user_id, allowance_type_id=2).exists():
        return Allowance.objects.get(date=date, user_id=user_id, allowance_type_id=2).description
    else:
        return 0

def to_get_food_description(date, user_id):
    if Allowance.objects.filter(date=date, user_id=user_id, allowance_type_id=1).exists():
        return Allowance.objects.get(date=date, user_id=user_id, allowance_type_id=1).description
    else:
        return 0

def to_get_stay(date, user_id):
    if Allowance.objects.filter(date=date, user_id=user_id, allowance_type_id=3, allowance_status_id=2).exists():
        return Allowance.objects.get(date=date, user_id=user_id, allowance_type_id=3, allowance_status_id=2).cost
    else:
        return 0


@api_view(["POST"])
def view_submitted_allowances_datewise(request):
    print(request.data)
    data={}
    from_date=request.data['from_date']
    to_date = request.data['to_date']
    user_id=request.data['user_id']

    allowance_obj = Allowance.objects.filter(season_id=4,  date__range=[from_date, to_date], user_id=user_id).order_by('date')
    allowance_values = allowance_obj.values_list('user_id', 'date', 'user__username')
    columns = ["user_id", "date", "Username"]
    details_df = pd.DataFrame(list(allowance_values), columns=columns)
    if not details_df.empty:
        details_df = details_df.fillna('0')
        details_df['Travel cost'] = details_df.apply(lambda x: to_find_travel_price(x['date'], x['user_id']), axis=1).astype(float)
        details_df['Food cost'] = details_df.apply(lambda x: check_exist(x['date'], x['user_id']), axis=1).astype(float)
        details_df['Stay cost'] = details_df.apply(lambda x: to_get_stay(x['date'], x['user_id']), axis=1).astype(float)
        details_df['Description'] = details_df.apply(lambda x: to_get_food_description(x['date'], x['user_id']), axis=1)
        # details_df['Travel description'] = details_df.apply(lambda x: to_get_travel_description(x['date'], x['user_id']), axis=1)
        details_df = details_df.drop_duplicates(['date', 'user_id'])
        details_df = details_df.drop(columns=['user_id'])
        
        details_df['Total Cost'] = details_df['Food cost'] + details_df['Travel cost'] + details_df['Stay cost']
        details_df["Total Cost"] = details_df["Total Cost"].astype(float_repr_style) 
        details_df.index += 1
        total = details_df.sum(numeric_only=True)
        total.name = 'Total'
        details_df = details_df.append(total.transpose())
        
    writer = pd.ExcelWriter(str("static/media/") + "Transaction_and_allowance_report.xlsx", engine="xlsxwriter")
    #creating excel sheet with name
    details_df.to_excel(writer, sheet_name="Sheet1", startrow=1)
    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:I1", "Transaction_and_allowance_report " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(details_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "Transaction_and_allowance_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def crop_failure_report(request):
    season_id = request.data['season_id']
    data={}

    sowing_obj = Sowing.objects.filter(season_id=season_id, is_active=False).values_list('farmer_id', 'farmer__first_name', 'farmer__last_name', 'village__name', 'area', 'sowing_date','cultivation_phase__name', 'water_source__name' ,'reason_for_inactive')
    column_names = ["farmer_id", "farmer_name", "father_name", "village", "acre", "sowing_date", "cultivation_phase_name","water_source", "reason_for_inactive"]
    sowing_df = pd.DataFrame(list(sowing_obj), columns=column_names)
    sowing_df

    farmer_cluster_obj = FarmerClusterSeasonMap.objects.filter(season_id=season_id).values_list('farmer_id', 'seasonal_farmer_code', 'cluster__name')
    farmer_cluster_columns = ["farmer_id", "farmer_code", "cluster_name"]
    farmer_cluster_df = pd.DataFrame(list(farmer_cluster_obj), columns=farmer_cluster_columns)
    farmer_cluster_df

    supervisor_farmer_obj = UserFarmerMap.objects.filter(farmer__season_id=season_id).values_list('farmer__farmer_id','officer__username')
    supervisor_farmer_columns = ["farmer_id","superviosr_name"]
    supervisor_farmer_df = pd.DataFrame(list(supervisor_farmer_obj), columns=supervisor_farmer_columns)
    supervisor_farmer_df

    agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__season_id=season_id).values_list('farmer__farmer_id','agent__first_name')
    agent_farmer_columns = ["farmer_id","agent_name"]
    agent_farmer_df = pd.DataFrame(list(agent_farmer_obj), columns=agent_farmer_columns)
    agent_farmer_df

    farmer_cluster_sowing_df = pd.merge(sowing_df, farmer_cluster_df, left_on='farmer_id', right_on='farmer_id', how='left')
    farmer_cluster_sowing_df

    farmer_cluster_sowing_supervisor_df = pd.merge(farmer_cluster_sowing_df, supervisor_farmer_df, left_on='farmer_id', right_on='farmer_id', how='left')
    farmer_cluster_sowing_supervisor_df

    final_df = pd.merge(farmer_cluster_sowing_supervisor_df, agent_farmer_df, left_on='farmer_id', right_on='farmer_id', how='left')
    final_df

    df = final_df[[ "superviosr_name", "agent_name", "farmer_code", "farmer_name", "father_name", "village", "cluster_name", "acre", "sowing_date", "cultivation_phase_name", "water_source", "reason_for_inactive"]]
    df = df.rename(columns={"superviosr_name" : 'Superviosr Name' , "agent_name" : 'Agent Name' , "farmer_code" : 'Farmer Code' , "farmer_name" : 'Farmer Name' , "father_name" : 'Father Name' , "village" : 'Village' , "cluster_name" : 'Cluster Name' , "acre" : 'Acre' , "sowing_date" : 'Sowing Date' , "cultivation_phase_name" : 'Cultivation Phase Name' , "water_source" : 'Water Source' , "reason_for_inactive" : "Reason For Inactive"})
    df.index += 1
    total = df.sum(numeric_only=True)
    total.name = 'Total'
    df = df.append(total.transpose())
    writer = pd.ExcelWriter(str("static/media/") + "crop_failure_report.xlsx", engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:M1", "crop_failure_report" + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "crop_failure_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def agent_wise_flower_report(request):
    season_id = request.data['agent_wise_flower_season_id']
    data = {}
    agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
    agent_farmer_values = list(agent_farmer_obj.values_list('agent_id', 'agent__first_name', 'farmer__farmer__id', 'farmer__seasonal_farmer_code','farmer__farmer__first_name' ))
    agent_farmer_columns = ["agent_id", 'agent_name', 'farmer_id', 'farmer_code', 'farmer_name']
    agent_farmer_df = pd.DataFrame(agent_farmer_values, columns=agent_farmer_columns)

    sowing_farmers_obj = Sowing.objects.filter(season_id=season_id)
    sowing_farmers_values = list(sowing_farmers_obj.values_list('id','farmer_id', 'cultivation_phase_id', 'cultivation_phase__name', 'area', 'area_calculated_via_geo_fencing'))
    sowing_farmers_columns = ["sowing_id","farmer_id", "cultivation_phase_id", "cultivation_phase_name", "area", "geo_fence"]
    sowing_farmers_df = pd.DataFrame(sowing_farmers_values, columns=sowing_farmers_columns)

    sowing_agent_farmer = pd.merge(agent_farmer_df, sowing_farmers_df, left_on='farmer_id', right_on='farmer_id', how='left')

    phase1_df = sowing_agent_farmer[sowing_agent_farmer['cultivation_phase_id']==1].drop(columns=['cultivation_phase_id'])
    phase1_df = phase1_df.rename(columns={'area':'total_nursury'})
    phase1_df = phase1_df.groupby(['agent_id','agent_name']).agg({'total_nursury':sum, }).reset_index()

    phase2_df = sowing_agent_farmer[sowing_agent_farmer['cultivation_phase_id']==2].drop(columns=['cultivation_phase_id'])
    phase2_df = phase2_df.rename(columns={'area':'total_transplant'})
    phase2_df = phase2_df.groupby(['agent_id']).agg({ 'sowing_id':'first','total_transplant':sum, 'geo_fence':sum}).reset_index()

    sowing_phase_df = pd.merge(phase1_df, phase2_df, left_on='agent_id', right_on='agent_id', how='left')
    sowing_phase_df['sowing_id'] = sowing_phase_df['sowing_id'].astype(int)
    sowing_id_list = sowing_phase_df['sowing_id'].tolist()

    harvest_obj = Harvest.objects.filter(sowing__season_id=season_id, sowing_id__in=sowing_id_list).values_list('sowing_id', 'value')
    harvest_columns = ["sowing_id", "flower_qty"]
    harvest_df = pd.DataFrame(list(harvest_obj), columns=harvest_columns)
    harvest_df = harvest_df.groupby('sowing_id').agg({'flower_qty':sum}).reset_index()

    sowing_harvest_df = pd.merge(sowing_phase_df, harvest_df, left_on='sowing_id', right_on='sowing_id', how='left')
    sowing_harvest_df = sowing_harvest_df.fillna(0)

    sowing_harvest_df['flower_Qty/Ton'] = sowing_harvest_df['flower_qty']/1000
    sowing_harvest_df['avg_yield_on_tp_acre'] = round(sowing_harvest_df['flower_qty']/sowing_harvest_df['total_transplant'], 2)
    sowing_harvest_df['avg_yield_on_gps_effective_acre'] = round(sowing_harvest_df['flower_qty']/sowing_harvest_df['geo_fence'], 2)
    final_df = sowing_harvest_df.drop(columns=['agent_id', 'sowing_id'])

    final_df = final_df.rename(columns={'agent_name' : "Agent Name", 'total_nursury' : "Total Nursury", 'total_transplant' : "Total Transplant", 'geo_fence' : "Geo Fence",
       'flower_qty' : "Flower Qty", 'flower_Qty/Ton' : "Flower Qty / Ton", 'avg_yield_on_tp_acre' : "Avg Yield On Tp Acre",
       'avg_yield_on_gps_effective_acre' : "Avg Yield On Gps Effective Acre",})

    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())
    
    writer = pd.ExcelWriter(str("static/media/") + "agent_wise_flower_report.xlsx", engine="xlsxwriter")
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)
    
    print(final_df.columns)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:I1", "agent_wise_flower_report" + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "agent_wise_flower_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

def to_find_price(qty, combo_name):
    if qty != 0:
        price = InputCombo.objects.get(name=combo_name).price
        return price
    else:
        return 0


@api_view(["POST"])
def agent_pesticide_distribution_list(request):
    season_id=request.data['season_id']
    data = {
        'have_data': False
    }
    combo_receipt_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo__inputpart__name__input_type_id=2)
    combo_receipt_val = list(set(combo_receipt_obj.values_list('bill_number','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers')))
    columns = ["Bill","Input Combo Name", "Quantity In Numbers"]
    combo_receipt_df = pd.DataFrame(combo_receipt_val, columns=columns)
    combo_receipt_df

    converted_df = pd.pivot_table(combo_receipt_df, index='Bill', columns='Input Combo Name', aggfunc=min, fill_value=0 )
    converted_df.columns = converted_df.columns.droplevel(0)
    converted_df.columns.name = None
    converted_df = converted_df.reset_index()
    if not converted_df.empty:
        converted_df = converted_df.reindex(columns=['Bill', '1st KIT', '2nd KIT', '3rd KIT','Pesticide pack -3 dipping kit', 'Pesticide pack 2 - 30 ml coragen', 'Pesticide pack - 60 ml coragen']).fillna(0)
        converted_df['1st Kit Price'] = converted_df.apply(lambda x: to_find_price(x['1st KIT'], '1st KIT'), axis=1).astype(float)
        converted_df['2nd Kit Price'] = converted_df.apply(lambda x: to_find_price(x['2nd KIT'], '2nd KIT'), axis=1).astype(float)
        converted_df['3rd Kit Price'] = converted_df.apply(lambda x: to_find_price(x['3rd KIT'], '3rd KIT'), axis=1).astype(float)
        converted_df['Dipping Kit Price'] = converted_df.apply(lambda x: to_find_price(x['Pesticide pack -3 dipping kit'], 'Pesticide pack -3 dipping kit'), axis=1).astype(float)
        converted_df['Coragen Price 30 ml'] = converted_df.apply(lambda x: to_find_price(x['Pesticide pack 2 - 30 ml coragen'], 'Pesticide pack 2 - 30 ml coragen'), axis=1).astype(float)
        converted_df['Coragen Price 60 ml'] = converted_df.apply(lambda x: to_find_price(x['Pesticide pack - 60 ml coragen'], 'Pesticide pack - 60 ml coragen'), axis=1).astype(float)

        users_df_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo__inputpart__name__input_type_id=2)
        user_val = users_df_obj.values_list('bill_number', 'time_created','agent_id','agent__first_name', 'combo_issue_request__supervisor__username', 'agent__userprofile__village__name', 'agent__userclustermap__cluster__name')
        user_columns = ["Bill", "Date","Agent Id","Agent Name", "Superviosr Name", "Village Name", "Cluster Name"]
        user_df = pd.DataFrame(list(set(user_val)), columns=user_columns)
        print(user_df)

        combine_df = pd.merge(converted_df, user_df, left_on='Bill', right_on='Bill', how='left')
        combine_df['Date'] = pd.to_datetime(combine_df['Date']).dt.date

        combine_df = combine_df.rename(columns={"1st KIT":"1st kit Qty", "2nd KIT":"2nd kit Qty","3rd KIT":"3rd kit Oty","Pesticide pack -3 dipping kit": "Dipping kit Qty", "Pesticide pack 2 - 30 ml coragen": "Coragen 30 ml Qty", "Pesticide pack - 60 ml coragen":"Coragen 60 ml Qty"})
        combine_df['1st Kit Amount'] = combine_df['1st kit Qty'] * combine_df['1st Kit Price'].astype(float)
        combine_df['2nd Kit Amount'] = combine_df['2nd kit Qty'] * combine_df['2nd Kit Price'].astype(float)
        combine_df['3rd Kit Amount'] = combine_df['3rd kit Oty'] * combine_df['3rd Kit Price'].astype(float)
        combine_df['Dipping kit Amount'] = combine_df['Dipping kit Qty'] * combine_df['Dipping Kit Price'].astype(float)
        combine_df['Coragen 30 ml Amount'] = combine_df['Coragen 30 ml Qty'] * combine_df['Coragen Price 30 ml'].astype(float)
        combine_df['Coragen 60 ml Amount'] = combine_df['Coragen 60 ml Qty'] * combine_df['Coragen Price 60 ml'].astype(float)
        combine_df['Total Pesticide Amount'] = (combine_df['1st Kit Amount'].apply(Decimal) + combine_df['2nd Kit Amount'].apply(Decimal) + combine_df['3rd Kit Amount'].apply(Decimal) + combine_df['Dipping kit Amount'].apply(Decimal) + combine_df['Coragen 30 ml Amount'].apply(Decimal) + combine_df['Coragen 60 ml Amount'].apply(Decimal)).astype(float)
        combine_df = combine_df[["Bill","Date","Agent Name","Superviosr Name", "Cluster Name","Village Name","1st kit Qty", "1st Kit Price" ,"1st Kit Amount", "2nd kit Qty", "2nd Kit Price", "2nd Kit Amount","3rd kit Oty", "3rd Kit Price", "3rd Kit Amount","Dipping kit Qty", "Dipping Kit Price", "Dipping kit Amount","Coragen 30 ml Qty", "Coragen Price 30 ml", "Coragen 30 ml Amount","Coragen 60 ml Qty", "Coragen Price 60 ml", "Coragen 60 ml Amount", "Total Pesticide Amount"]]
        
        final_df = combine_df 
        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "agent_pesticide_distribution_report.xlsx", engine="xlsxwriter")
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:AB1", "agent_pesticide_distribution_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        data['have_data'] = True
    try:
        image_path = str("static/media/") + "agent_pesticide_distribution_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def agent_fertilizer_distribution_list(request):
    print(request.data)
    season_id=request.data['season_id']
    data = {}
    #.exclude(combo_issue_request__input_combo__inputpart__name__input_type_id=2)
    combo_receipt_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo__inputpart__name__input_type_id=3).exclude(combo_issue_request__input_combo__inputpart__name__input_type_id=2)
    combo_receipt_val = list(set(combo_receipt_obj.values_list('bill_number','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers')))
    columns = ["Bill","Input Combo Name", "Quantity In Numbers"]
    combo_receipt_df = pd.DataFrame(combo_receipt_val, columns=columns)
    combo_receipt_df

    if not combo_receipt_df.empty:
        print('not empty df')
        converted_df = pd.pivot_table(combo_receipt_df, index='Bill', columns='Input Combo Name', aggfunc=min, fill_value=0 )
        converted_df.columns = converted_df.columns.droplevel(0)
        converted_df.columns.name = None
        converted_df = converted_df.reset_index()
        converted_df = converted_df.reindex(columns=['Bill', 'DAP', '17:17:17', '10:26:26','20:20:0:13', '15 : 15 :15', 'MAP']).fillna(0)
        converted_df['DAP Price'] = converted_df.apply(lambda x: to_find_price(x['DAP'], 'DAP'), axis=1).astype(float)
        converted_df['17 All Price'] = converted_df.apply(lambda x: to_find_price(x['17:17:17'], '17:17:17'), axis=1).astype(float)
        converted_df['10:26:26 Price'] = converted_df.apply(lambda x: to_find_price(x['10:26:26'], '10:26:26'), axis=1).astype(float)
        converted_df['20:20:0:13 Price'] = converted_df.apply(lambda x: to_find_price(x['20:20:0:13'], '20:20:0:13'), axis=1).astype(float)
        converted_df['15 All Price'] = converted_df.apply(lambda x: to_find_price(x['15 : 15 :15'], '15 : 15 :15'), axis=1).astype(float)
        # converted_df['19:19:19_Price'] = converted_df.apply(lambda x: to_find_price(x['19:19:19'], '19:19:19'), axis=1)
        converted_df['MAP_Price'] = converted_df.apply(lambda x: to_find_price(x['MAP'], 'MAP'), axis=1).astype(float)

        users_df_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo__inputpart__name__input_type_id=3)
        user_val = users_df_obj.values_list('bill_number', 'time_created','agent_id','agent__first_name', 'combo_issue_request__supervisor__username', 'agent__userprofile__village__name', 'agent__userclustermap__cluster__name')
        user_columns = ["Bill", "Date","Agent Id","Agent Name", "Superviosr Name", "Village Name", "Cluster Name"]
        user_df = pd.DataFrame(list(set(user_val)), columns=user_columns)

        combine_df = pd.merge(converted_df, user_df, left_on='Bill', right_on='Bill', how='left')
        combine_df['Date'] = pd.to_datetime(combine_df['Date']).dt.date

        combine_df = combine_df.rename(columns={"DAP":"DAP Qty", "17:17:17":"17 All Qty","10:26:26":"10:26:26 Oty","20:20:0:13": "20:20:0:13 Qty", "15 : 15 :15": "15 All Qty", "MAP":"MAP Qty"})
        combine_df['DAP Amount'] = combine_df['DAP Qty'] * combine_df['DAP Price'].astype(float)
        combine_df['17 All Amount'] = combine_df['17 All Qty'] * combine_df['17 All Price'].astype(float)
        combine_df['10:26:26 Amount'] = combine_df['10:26:26 Oty'] * combine_df['10:26:26 Price'].astype(float)
        combine_df['20:20:0:13 Amount'] = combine_df['20:20:0:13 Qty'] * combine_df['20:20:0:13 Price'].astype(float)
        combine_df['15 All Amount'] = combine_df['15 All Qty'] * combine_df['15 All Price'].astype(float)
        combine_df['MAP Amount'] = combine_df['MAP Qty'] * combine_df['MAP_Price'].astype(float)
        combine_df['Total Fertilizer Amount'] = (combine_df['DAP Amount'].apply(Decimal) + combine_df['17 All Amount'].apply(Decimal) + combine_df['10:26:26 Amount'].apply(Decimal) + combine_df['20:20:0:13 Amount'].apply(Decimal) + combine_df['15 All Amount'].apply(Decimal) + combine_df['MAP Amount'].apply(Decimal)).astype(float)
        combine_df = combine_df[["Bill","Date","Agent Name","Superviosr Name", "Cluster Name","Village Name","DAP Qty", "DAP Price" ,"DAP Amount", "17 All Qty", "17 All Price", "17 All Amount", "10:26:26 Oty", "10:26:26 Price","10:26:26 Amount","20:20:0:13 Qty","20:20:0:13 Price","20:20:0:13 Amount", "15 All Qty", "15 All Price", "15 All Amount", "MAP Qty", "MAP_Price", "MAP Amount", "Total Fertilizer Amount"]]

        combine_df = combine_df.drop_duplicates(['Bill'])
        final_df = combine_df 
        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "agent_pesticide_distribution_report.xlsx", engine="xlsxwriter")
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:AB1", "agent_pesticide_distribution_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "agent_pesticide_distribution_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        print('empty_df')
        data = {}
        df_status = False
        return Response(data=df_status, status=status.HTTP_200_OK)
    
def to_find_from_lot_number(combo_issue_request_id, agent_id):
    season_id = get_active_season_id()
    agent_inventory_id = AgentInventory.objects.get(combo_issue_request_id=combo_issue_request_id, agent_id=agent_id ).id
    from_lot_no = list(AgentInventoryStoreLabelRangeMap.objects.filter(agent_inventory__season_id=season_id, agent_inventory_id=agent_inventory_id).values_list('label_range_from', flat=True))
    return from_lot_no

def to_find_to_lot_number(combo_issue_request_id, agent_id):
    season_id = get_active_season_id()
    agent_inventory_id = AgentInventory.objects.get(combo_issue_request_id=combo_issue_request_id, agent_id=agent_id).id
    to_lot_no = list(AgentInventoryStoreLabelRangeMap.objects.filter(agent_inventory__season_id=season_id, agent_inventory_id=agent_inventory_id).values_list('label_range_to', flat=True))
    return to_lot_no

@api_view(["POST"])
def agent_seed_distribution_list(request):
    print(request.data)
    season_id=request.data['season_id']
    data = {
        "have_data": False
    }

    combo_receipt_obj = ComboIssueAgentInventoryReceipt.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__input_combo__inputpart__name__input_type_id=1)
    combo_receipt_val = list(set(combo_receipt_obj.values_list('bill_number','combo_issue_request_id', 'combo_issue_request__input_combo__name','time_created','agent_id','agent__first_name', 'combo_issue_request__supervisor__username', 'agent__userprofile__village__name', 'agent__userclustermap__cluster__name', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__quantity_for_area')))
    columns = ["Bill number", "Combo Issue Request Id","Combo Name","Date","Agent Id","Agent Name", "Superviosr Name", "Village Name", "Cluster Name", "Quantity In Numbers", "Acre"]
    combo_receipt_df = pd.DataFrame(combo_receipt_val, columns=columns)

    one_acre_seed_df =  combo_receipt_df[combo_receipt_df['Combo Name']=='One Acre Seed Pkt']
    half_acre_seed_df = combo_receipt_df[combo_receipt_df['Combo Name']=='Half Acre Seed Pkt']

    combine_df = pd.concat([one_acre_seed_df, half_acre_seed_df])

    if not combine_df.empty:
        combine_df['From Lot Number'] = combine_df.apply(lambda x: to_find_from_lot_number(x['Combo Issue Request Id'], x['Agent Id']), axis=1)
        combine_df['To Lot Number'] = combine_df.apply(lambda x: to_find_to_lot_number(x['Combo Issue Request Id'], x['Agent Id']), axis=1)
        combine_df['Amount'] = (combine_df['Acre'] * 2300).astype(float)
        combine_df = combine_df.rename(columns={"Quantity In Numbers":"Seed Qty", "Acre":"Total Acre", "Combo Name":"Name"})
        combine_df['Date'] = pd.to_datetime(combine_df['Date']).dt.date
        combine_df.drop(columns=['Combo Issue Request Id', 'Agent Id'])
        combine_df = combine_df[["Bill number","Date","Agent Name","Superviosr Name", "Cluster Name","Village Name","Name","Seed Qty", "From Lot Number", "To Lot Number", "Total Acre", "Amount"]]
        
        final_df = combine_df 
        final_df['Total Acre'] = final_df['Total Acre'].astype(float) 

        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "agent_seed_distribution_report.xlsx", engine="xlsxwriter", )
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )
        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:N1", "agent_seed_distribution_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        data['have_data'] = True
    try:
        image_path = str("static/media/") + "agent_seed_distribution_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


def to_find_total_acre(agent_id):
    season_id = get_active_season_id()
    agent_inventry_ids = list(AgentInventory.objects.filter(season_id=season_id, agent_id=agent_id).values_list('combo_issue_request_id', flat=True))
    if len(agent_inventry_ids) == 0:
        return 0
    combo_request_obj = ComboIssueRequest.objects.filter(id__in=agent_inventry_ids).aggregate(Sum('quantity_for_area'))["quantity_for_area__sum"]
    return combo_request_obj

def to_find_cluster(agent_id, season_id = None):
    if season_id == None:
        season_id = get_active_season_id()
    return UserClusterMap.objects.get(season_id=season_id, user_id=agent_id).cluster.name

@api_view(["POST"])
def agent_wise_pesticides_fertilizers_summary(request):
    print(request.data)
    season_id=request.data['season_id']
    data = {'is_value_avaliable': True}

    combo_issue_request_agentmap_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id__in=[8,9], shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers','combo_issue_request__quantity_for_area', 'combo_issue_request__input_combo__name'))
    combo_issue_request_agentmap_column = ['agent_id', 'agent_name', 'input_combo_id', 'quantity',  'area','input_combo_name']
    combo_issue_request_agentmap_df = pd.DataFrame(combo_issue_request_agentmap_obj, columns=combo_issue_request_agentmap_column)

    combo_issue_request_othershop_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id=6).exclude(shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))
    column_names = ['agent_id', 'agent_name', 'input_combo_id', 'quantity',  'input_combo_name']
    combo_issue_request_othershop_obj_df = pd.DataFrame(combo_issue_request_othershop_obj, columns=column_names)

    merge_df = pd.concat([combo_issue_request_agentmap_df, combo_issue_request_othershop_obj_df])
    merge_df1 = merge_df.groupby(['agent_id', 'input_combo_id']).agg({'agent_name': 'first', 'quantity': sum, 'input_combo_name': 'first'}).reset_index()
    # merge_df1 = merge_df1.drop(columns=['input_combo_id']) 

    input_combo_obj = InputCombo.objects.filter().values_list('id', 'name')
    input_combo_df = pd.DataFrame(list(input_combo_obj), columns=['input_combo_id', 'name'])

    inupt_merge_df = pd.merge(merge_df1, input_combo_df,  left_on='input_combo_id', right_on='input_combo_id', how='outer')
    # inupt_merge_df.fillna(0)
    merge_df1 = inupt_merge_df.drop(columns=['input_combo_id', 'input_combo_name']) 

    # convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    final_df = pd.pivot_table(merge_df1, index=['agent_id','agent_name'] , columns='name', aggfunc=min, fill_value=0)

    #convert_pivot_table_to_normal_df
    final_df.columns = final_df.columns.droplevel(0) #remove amount
    final_df.columns.name = None  #remove categories

    final_df = final_df.reset_index() #index to columns
    # final_df1 = final_df.drop(columns=['agent_id'])

    agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
    agent_farmer_values = list(agent_farmer_obj.values_list('agent_id', 'agent__first_name', 'farmer__farmer__id', 'farmer__seasonal_farmer_code','farmer__farmer__first_name' ))
    agent_farmer_columns = ["agent_id", 'agent_name', 'farmer_id', 'farmer_code', 'farmer_name']
    agent_farmer_df = pd.DataFrame(agent_farmer_values, columns=agent_farmer_columns)

    sowing_farmers_obj = Sowing.objects.filter(season_id=season_id)
    sowing_farmers_values = list(sowing_farmers_obj.values_list('id','farmer_id', 'cultivation_phase_id', 'cultivation_phase__name', 'area', 'area_calculated_via_geo_fencing'))
    sowing_farmers_columns = ["sowing_id","farmer_id", "cultivation_phase_id", "cultivation_phase_name", "area", "geo_fence"]
    sowing_farmers_df = pd.DataFrame(sowing_farmers_values, columns=sowing_farmers_columns)

    sowing_agent_farmer = pd.merge(agent_farmer_df, sowing_farmers_df, left_on='farmer_id', right_on='farmer_id', how='left')
    sowing_agent_farmer.fillna(0)

    phase1_df = sowing_agent_farmer[sowing_agent_farmer['cultivation_phase_id']==1].drop(columns=['cultivation_phase_id'])
    phase1_df = phase1_df.rename(columns={'area':'total_nursury'})
    phase1_df = phase1_df.groupby(['agent_id','agent_name']).agg({'total_nursury':sum, }).reset_index()

    phase2_df = sowing_agent_farmer[sowing_agent_farmer['cultivation_phase_id']==2].drop(columns=['cultivation_phase_id'])
    phase2_df = phase2_df.rename(columns={'area':'total_transplant'})
    phase2_df = phase2_df.groupby(['agent_id']).agg({ 'sowing_id':'first','total_transplant':sum, 'geo_fence':sum}).reset_index()

    sowing_phase_df = pd.merge(phase1_df, phase2_df, left_on='agent_id', right_on='agent_id', how='left')
    sowing_phase_df['sowing_id'] = sowing_phase_df['sowing_id'].astype(int)

    final_sowing_df = pd.merge(sowing_phase_df, final_df, left_on='agent_id', right_on='agent_id', how='left')
    final_sowing_df1 = final_sowing_df.drop(columns=['agent_name_y'])

    final_sowing_df1 = final_sowing_df1.fillna(0)
    print("-------------------------------------", final_sowing_df1.empty)
    if not final_sowing_df1.empty:
        final_sowing_df1['seed_distribution_acre'] = final_sowing_df1.apply(lambda x: to_find_total_acre(x['agent_id']), axis=1)
        final_sowing_df1['cluster_name'] = final_sowing_df1.apply(lambda x: to_find_cluster(x['agent_id'], season_id), axis=1)
        final_sowing_df1['1 Kit %'] = round(final_sowing_df1['1st KIT']/final_sowing_df1['total_transplant'], 3)
        # final_sowing_df1['2nd_Kit %'] = final_sowing_df1['2nd KIT']/final_sowing_df1['total_transplant']
        # final_sowing_df1['3rd_Kit %'] = final_sowing_df1['3rd KIT']/final_sowing_df1['total_transplant']
        final_sowing_df1['Total Fertilizer'] = (final_sowing_df1['10:26:26'].apply(Decimal) + final_sowing_df1['17:17:17'].apply(Decimal)+ final_sowing_df1['1st KIT'].apply(Decimal) + final_sowing_df1['20:20:0:13'].apply(Decimal) + final_sowing_df1['DAP'].apply(Decimal)).astype(float)
        final_sowing_df1['Avg Fertilzer %'] = round(final_sowing_df1['Total Fertilizer'].apply(float)/final_sowing_df1['total_transplant'].apply(float), 3)
        final_sowing_df1 = final_sowing_df1.drop(columns=['agent_id', 'sowing_id'])
        final_sowing_df1 = final_sowing_df1.rename(columns={"agent_name_x":"agent_name"})
        final_sowing_df1 = final_sowing_df1.fillna(0)
        combine_df = final_sowing_df1[["agent_name", "seed_distribution_acre", "total_nursury", "total_transplant", "geo_fence", "1st KIT", "10:26:26", "17:17:17", "20:20:0:13", "DAP", "1 Kit %", "Total Fertilizer", "Avg Fertilzer %"]]
        final_df = combine_df 

        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "agent_wise_pesticides_fertilizers_report.xlsx", engine="xlsxwriter", )
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )
        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:T1", "agent_wise_pesticides_fertilizers_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "agent_wise_pesticides_fertilizers_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
    else:
        data['is_value_avaliable'] = False
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def cluster_wise_summary(request):
    season_id=request.data['season_id']
    data = {'is_value_avaliable': True}

    combo_issue_request_agentmap_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id__in=[8,9], shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers','combo_issue_request__quantity_for_area', 'combo_issue_request__input_combo__name'))
    combo_issue_request_agentmap_column = ['Agent Id', 'Agent Name', 'Input Combo Id', 'Quantity',  'Area','Input Combo Name']
    combo_issue_request_agentmap_df = pd.DataFrame(combo_issue_request_agentmap_obj, columns=combo_issue_request_agentmap_column)

    combo_issue_request_othershop_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id=6).exclude(shop_id=1).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers', 'combo_issue_request__input_combo__name'))
    column_names = ['Agent Id', 'Agent Name', 'Input Combo Id', 'Quantity',  'Input Combo Name']
    combo_issue_request_othershop_obj_df = pd.DataFrame(combo_issue_request_othershop_obj, columns=column_names)

    merge_df = pd.concat([combo_issue_request_agentmap_df, combo_issue_request_othershop_obj_df])
    merge_df1 = merge_df.groupby(['Agent Id', 'Input Combo Id']).agg({'Agent Name': 'first', 'Quantity': sum, 'Input Combo Name': 'first'}).reset_index()
    # merge_df1 = merge_df1.drop(columns=['input_combo_id']) 

    input_combo_obj = InputCombo.objects.filter().values_list('id', 'name')
    input_combo_df = pd.DataFrame(list(input_combo_obj), columns=['Input Combo Id', 'Name'])

    inupt_merge_df = pd.merge(merge_df1, input_combo_df,  left_on='Input Combo Id', right_on='Input Combo Id', how='outer')
    # inupt_merge_df.fillna(0)
    merge_df1 = inupt_merge_df.drop(columns=['Input Combo Id', 'Input Combo Name']) 
    merge_df1 = merge_df1.dropna(subset=['Agent Id'])
    if not merge_df1.empty:
        print(merge_df1)
        # convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        final_df = pd.pivot_table(merge_df1, index=['Agent Id','Agent Name'] , columns='Name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        final_df.columns = final_df.columns.droplevel(0) #remove amount
        final_df.columns.name = None  #remove categories

        final_df = final_df.reset_index() #index to columns
        # final_df1 = final_df.drop(columns=['agent_id'])

        agent_farmer_obj = AgentFarmerMap.objects.filter(farmer__season_id=season_id)
        agent_farmer_values = list(agent_farmer_obj.values_list('agent_id', 'agent__first_name', 'farmer__farmer__id', 'farmer__seasonal_farmer_code','farmer__farmer__first_name' ))
        agent_farmer_columns = ["Agent Id", 'Agent Name', 'Farmer Id', 'Farmer Code', 'Farmer Name']
        agent_farmer_df = pd.DataFrame(agent_farmer_values, columns=agent_farmer_columns)

        sowing_farmers_obj = Sowing.objects.filter(season_id=season_id)
        sowing_farmers_values = list(sowing_farmers_obj.values_list('id','farmer_id', 'cultivation_phase_id', 'cultivation_phase__name', 'area', 'area_calculated_via_geo_fencing'))
        sowing_farmers_columns = ["Sowing Id","Farmer Id", "Cultivation Phase Id", "Cultivation Phase Name", "Area", "Geo Fence"]
        sowing_farmers_df = pd.DataFrame(sowing_farmers_values, columns=sowing_farmers_columns)

        sowing_agent_farmer = pd.merge(agent_farmer_df, sowing_farmers_df, left_on='Farmer Id', right_on='Farmer Id', how='left')
        sowing_agent_farmer.fillna(0)

        phase1_df = sowing_agent_farmer[sowing_agent_farmer['Cultivation Phase Id']==1].drop(columns=['Cultivation Phase Id'])
        phase1_df = phase1_df.rename(columns={'Area':'Total Nursury'})
        phase1_df = phase1_df.groupby(['Agent Id','Agent Name']).agg({'Total Nursury':sum, }).reset_index()

        phase2_df = sowing_agent_farmer[sowing_agent_farmer['Cultivation Phase Id']==2].drop(columns=['Cultivation Phase Id'])
        phase2_df = phase2_df.rename(columns={'Area':'Total Transplant'})
        phase2_df = phase2_df.groupby(['Agent Id']).agg({ 'Sowing Id':'first','Total Transplant':sum, 'Geo Fence':sum}).reset_index()

        sowing_phase_df = pd.merge(phase1_df, phase2_df, left_on='Agent Id', right_on='Agent Id', how='left')
        sowing_phase_df['Sowing Id'] = sowing_phase_df['Sowing Id'].astype(int)

        final_sowing_df = pd.merge(sowing_phase_df, final_df, left_on='Agent Id', right_on='Agent Id', how='left')
        final_sowing_df1 = final_sowing_df.drop(columns=['Agent Name_y'])
        final_sowing_df1 = final_sowing_df1.fillna(0)
        final_sowing_df1['Seed Distribution Acre'] = final_sowing_df1.apply(lambda x: to_find_total_acre(x['Agent Id']), axis=1)
        final_sowing_df1['Cluster Name'] = final_sowing_df1.apply(lambda x: to_find_cluster(x['Agent Id'], season_id), axis=1)
        final_sowing_df1['1 Kit %'] = round(final_sowing_df1['1st KIT']/final_sowing_df1['Total Transplant'], 3)
        # final_sowing_df1['2nd_Kit %'] = final_sowing_df1['2nd KIT']/final_sowing_df1['Total Transplant']
        # final_sowing_df1['3rd_Kit %'] = final_sowing_df1['3rd KIT']/final_sowing_df1['Total Transplant']
        final_sowing_df1['Total Fertilizer'] = (final_sowing_df1['10:26:26'].apply(Decimal) + final_sowing_df1['17:17:17'].apply(Decimal)+ final_sowing_df1['1st KIT'].apply(Decimal) + final_sowing_df1['20:20:0:13'].apply(Decimal) + final_sowing_df1['DAP'].apply(Decimal)).astype(float)
        final_sowing_df1['Avg Fertilzer %'] = round(final_sowing_df1['Total Fertilizer'].apply(float)/final_sowing_df1['Total Transplant'].apply(float), 3)
        final_sowing_df1 = final_sowing_df1.drop(columns=['Agent Id', 'Sowing Id'])
        final_sowing_df1 = final_sowing_df1.rename(columns={"Agent Name_x":"Agent Name"})
        final_sowing_df1 = final_sowing_df1.fillna(0)
        combine_df = final_sowing_df1[["Agent Name", "Seed Distribution Acre", "Total Nursury", "Total Transplant", "Geo Fence", "1st KIT", "10:26:26", "17:17:17", "20:20:0:13", "DAP", "1 Kit %", "Total Fertilizer", "Avg Fertilzer %"]]

        cluster_summary_df = final_sowing_df1.groupby('Cluster Name').agg({'Seed Distribution Acre':sum, 'Total Nursury':sum, 'Total Transplant':sum, 'Geo Fence':sum, '10:26:26':sum, '17:17:17':sum, '1st KIT':sum, '20:20:0:13':sum, 'DAP':sum, 'Half Acre Seed Pkt':sum, 'One Acre Seed Pkt':sum, 'Pesticide pack -3 dipping kit':sum}).reset_index()
        
        cluster_summary_df['1 Kit %'] = round(cluster_summary_df['1st KIT']/cluster_summary_df['Total Transplant'], 3)
        # cluster_summary_df['2nd_Kit %'] = cluster_summary_df['2nd KIT']/cluster_summary_df['Total Transplant']
        # cluster_summary_df['3rd_Kit %'] = cluster_summary_df['3rd KIT']/cluster_summary_df['Total Transplant']
        cluster_summary_df['Total Fertilizer'] = (cluster_summary_df['10:26:26'].apply(Decimal) + cluster_summary_df['17:17:17'].apply(Decimal)+ cluster_summary_df['1st KIT'].apply(Decimal) + cluster_summary_df['20:20:0:13'].apply(Decimal) + cluster_summary_df['DAP'].apply(Decimal)).astype(float)
        cluster_summary_df['Avg Fertilzer %'] = round(cluster_summary_df['Total Fertilizer'].apply(float)/cluster_summary_df['Total Transplant'].apply(float), 3)

        final_df = cluster_summary_df 
        final_df.index += 1
        total = final_df.sum(numeric_only=True)
        total.name = 'Total'
        final_df = final_df.append(total.transpose())

        writer = pd.ExcelWriter(str("static/media/") + "cluster_wise_summary_report.xlsx", engine="xlsxwriter", )
        final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )
        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:T1", "cluster_wise_summary_report" + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 20, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "cluster_wise_summary_report.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
    else:
        data['is_value_avaliable'] = False
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def get_agent_total_cost(request):
    season_id=request.data['season_id']
    data = {}
    agent_invetry_obj = AgentInventory.objects.filter(season_id=season_id).order_by('agent_id')
    input_combo_type_list = []
    for i in agent_invetry_obj:
        data_dict = {
            "Input Combo Id":'',
            "Input Type Name": '',
            "Input Type Id": ''
        }
        data_dict["Input Combo Id"] = i.combo_issue_request.input_combo.id
        combo_name_obj = InputPart.objects.filter(input_combo_id=i.combo_issue_request.input_combo.id)
        if combo_name_obj.count() > 1:
            data_dict["Input Type Name"] = 'Fertilizers Amount'
            data_dict["Input Type Id"] = 3
        else:
            data_dict["Input Type Name"] = combo_name_obj[0].name.input_type.name + " Amount"
            data_dict["Input Type Id"] = combo_name_obj[0].name.input_type_id
        input_combo_type_list.append(data_dict)
    input_combo_df = pd.DataFrame(input_combo_type_list)
    input_combo_df = input_combo_df.drop_duplicates()
    if input_combo_df.empty:
        input_combo_df = pd.DataFrame(columns=['Input Combo Id', 'Input Type Name', 'Input Type Id'])


    agent_inventry_list = agent_invetry_obj.values_list('agent_id','agent__userprofile__code', 'agent__first_name', 'agent__last_name', 'combo_issue_request__input_combo_id','combo_issue_request__input_combo__name', 'combo_issue_request__quantity_in_numbers','combo_issue_request__input_combo__price', 'combo_issue_request__comboissuerequestagentmap__shop__type__name')
    agent_invetry_columns = ['Agent Id', 'Agent Code', 'Agent First Name', 'Agent Last Name', 'Input Combo Id','Product Name', 'Product Qty','Price Per Item', 'Shop Name']
    agent_invetry_df = pd.DataFrame(agent_inventry_list, columns=agent_invetry_columns)
    agent_invetry_df['Sub Total'] = agent_invetry_df['Product Qty'] * agent_invetry_df['Price Per Item'] 

    agent_seed_pesticides_fertilizer_df = pd.merge(agent_invetry_df, input_combo_df, left_on='Input Combo Id', right_on='Input Combo Id', how='left')
    agent_seed_pesticides_fertilizer_df = agent_seed_pesticides_fertilizer_df.groupby('Input Type Id').agg({'Agent Id':'first','Agent Code':'first', 'Agent First Name':'first','Input Type Name': 'first', 'Sub Total': sum}).reset_index()
    agent_seed_pesticides_fertilizer_df = agent_seed_pesticides_fertilizer_df.drop(columns=['Input Type Id'])

    ##convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    agent_seed_pesticides_fertilizer_df = pd.pivot_table(agent_seed_pesticides_fertilizer_df, index=['Agent Id','Agent Code', 'Agent First Name'] , columns='Input Type Name', aggfunc=min, fill_value=0)

    #->##convert_pivot_table_to_normal_df
    agent_seed_pesticides_fertilizer_df.columns = agent_seed_pesticides_fertilizer_df.columns.droplevel(0) #remove amount
    agent_seed_pesticides_fertilizer_df.columns.name = None  #remove categories
    agent_seed_pesticides_fertilizer_df = agent_seed_pesticides_fertilizer_df.reset_index() #index to columns

    if not 'Seeds Amount' in agent_seed_pesticides_fertilizer_df.columns:
        agent_seed_pesticides_fertilizer_df['Seeds Amount'] = 0
    if not 'Fertilizers Amount' in agent_seed_pesticides_fertilizer_df.columns:
        agent_seed_pesticides_fertilizer_df['Fertilizers Amount'] = 0
    if not 'Agrochemicals Amount' in agent_seed_pesticides_fertilizer_df.columns:
        agent_seed_pesticides_fertilizer_df['Agrochemicals Amount'] = 0
    agent_seed_pesticides_fertilizer_df.rename(columns = {'Agrochemicals Amount':'Pesticides Amount'}, inplace = True)


    procurement_group_obj = ProcurementGroup.objects.filter(season_id=season_id)
    procurement_group_values = procurement_group_obj.values_list('agent_id', 'cost')
    procurement_group_columns = ["Agent Id", "Total Flower Amount"]
    procurement_group_df = pd.DataFrame(list(set(procurement_group_values)), columns=procurement_group_columns)
    procurement_group_df = procurement_group_df.groupby('Agent Id').agg({'Total Flower Amount':sum}).reset_index()

    agent_seed_pesticides_fertilizer_flower_df = pd.merge(agent_seed_pesticides_fertilizer_df, procurement_group_df, left_on='Agent Id', right_on='Agent Id', how='left')
    combine_df = agent_seed_pesticides_fertilizer_flower_df.fillna(0)
    combine_df['Fertilizers Amount'] = combine_df['Fertilizers Amount'].astype(float)
    combine_df['Seeds Amount'] = combine_df['Seeds Amount'].astype(float)
    combine_df['Pesticides Amount'] = combine_df['Pesticides Amount'].astype(float)
    combine_df['Total Flower Amount'] = combine_df['Total Flower Amount'].astype(float)
    combine_df['Total Amount'] = combine_df['Fertilizers Amount'].astype(float) + combine_df['Seeds Amount'].astype(float) + combine_df['Pesticides Amount'].astype(float) + combine_df['Total Flower Amount'].astype(float)
    final_df = combine_df.drop(columns=['Agent Id'])
    # final_df = combine_df 

    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())

    writer = pd.ExcelWriter(str("static/media/") + "agent_wise_cost_report.xlsx", engine="xlsxwriter", )
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )
    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:H1", "agent_wise_cost_report" + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "agent_wise_cost_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def serve_input_combo_summary(request):
    cluster_id = request.data['cluster_id']
    season_id = request.data['season_id']
    data={}
    cluster_agents = list(UserClusterMap.objects.filter(season_id=season_id, cluster_id=cluster_id ,user__userprofile__user_type_id=6).values_list('user_id', flat=True))
    combo_issue_request_agentmap_obj = list(ComboIssueRequestAgentMap.objects.filter(combo_issue_request__season_id=season_id, combo_issue_request__max_status_id__in=[8,9], agent_id__in=cluster_agents).values_list('agent_id', 'agent__first_name', 'combo_issue_request__input_combo_id', 'combo_issue_request__quantity_in_numbers','combo_issue_request__quantity_for_area','combo_issue_request__input_combo__price', 'combo_issue_request__input_combo__name'))      
    column_names = ['Agent Id', 'Agent Name', 'Input Combo Id', 'Quantity', 'Acre', 'Price Per Item','Input Combo Name']
    combo_issue_request_df = pd.DataFrame(combo_issue_request_agentmap_obj, columns=column_names)
    combo_issue_request_df = combo_issue_request_df.groupby(['Input Combo Name']).agg({ 'Quantity': sum, 'Acre':sum, 'Price Per Item':'first'}).reset_index()
    combo_issue_request_df['Amount'] = (combo_issue_request_df['Quantity'] * combo_issue_request_df['Price Per Item']).astype(float)
    combo_issue_request_df['Quantity'] = combo_issue_request_df['Quantity'] .astype(str)
    combo_issue_request_df['Price Per Item'] = combo_issue_request_df['Price Per Item'] .astype(float)
    combo_issue_request_df['Acre'] = combo_issue_request_df['Acre'] .astype(float)

    final_df = combo_issue_request_df 

    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())

    writer = pd.ExcelWriter(str("static/media/") + "product_summary_report.xlsx", engine="xlsxwriter", )
    final_df.to_excel(writer, sheet_name="Sheet1", startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )
    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:F1", "product_summary_report" + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 20, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "product_summary_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def complete_farmer_data_report(request):
    season_id = get_active_season_id()

    available_cluster_ids = list(UserClusterMap.objects.filter(user_id=request.user.id, season_id=season_id).values_list("cluster_id", flat=True))
    farmer_cluster_list = FarmerClusterSeasonMap.objects.filter(cluster_id__in=available_cluster_ids, season_id=season_id).order_by("id").values_list(
        'farmer_id', 'farmer__first_name', 'farmer__last_name', 'seasonal_farmer_code', 'farmer__village__name', 'farmer__mobile', 'agentfarmermap__agent__first_name')
    farmer_cluster_column = ['Farmer Id', 'First Name', 'Last Name', 'Farmer Code', 'Village', 'Phone', 'Agent Name']
    farmer_cluster_df = pd.DataFrame(farmer_cluster_list, columns=farmer_cluster_column)


    sowing_obj = Sowing.objects.filter(farmer_id__in=farmer_cluster_df['Farmer Id'], season_id=season_id)

    #farmers without cp1 df
    ##cultivation phase 1 having farmers ids
    farmers_with_cp1_id_list = list(sowing_obj.filter(cultivation_phase_id=1).values_list('farmer_id', flat=True))
    ##cultivation phase 1 not having farmers ids
    farmers_without_cp1_id_list = list(set(farmer_cluster_df['Farmer Id'])-set(farmers_with_cp1_id_list))
    ##farmers without cp1 df
    farmers_without_cp1_df = farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_cp1_id_list)] 

    #farmers without cp2 df
    ##cultivation phase 2 having farmers ids
    farmers_with_cp2_id_list = list(sowing_obj.filter(cultivation_phase_id=2).values_list('farmer_id', flat=True))
    ##cultivation phase 2 not having farmers ids
    farmers_without_cp2_id_list = list(set(farmer_cluster_df['Farmer Id'])-set(farmers_with_cp2_id_list))
    ##farmers without cp2 df
    farmers_without_cp2_df = farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_cp2_id_list)] 

    #farmers without cp1 geo fence df
    ##farmers without cp1 geo fence list
    farmers_without_cp1_fence_id_list = list(sowing_obj.filter(cultivation_phase_id=1, area_calculated_via_geo_fencing__isnull=True).values_list('farmer_id', flat=True))
    #farmers without cp1 geo fence df
    farmers_without_cp1_fence_df = farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_cp1_fence_id_list)] 

    #farmers without cp2 geo fence df
    ##farmers without cp2 geo fence list
    farmers_without_cp2_fence_id_list = list(sowing_obj.filter(cultivation_phase_id=2, area_calculated_via_geo_fencing__isnull=True).values_list('farmer_id', flat=True))
    #farmers without cp2 geo fence df
    farmers_without_cp2_fence_df = farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_cp2_fence_id_list)] 

    #farmers without cp2 harvest df
    ##farmers with cp2 harvest
    farmers_with_cp2_harvest_id_list = list(sowing_obj.filter(cultivation_phase_id=2).values_list('harvest__sowing__farmer_id', flat=True))
    ##farmer without cp2 harvest
    farmers_without_cp2_harvest_id_list = list(set(farmer_cluster_df['Farmer Id'])-set(farmers_with_cp2_harvest_id_list))
    ##farmer without cp2 harvest df
    farmers_without_cp2_harvest_df= farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_cp2_harvest_id_list)] 

    #farmers without bank details df
    ##farmer with bank details
    farmers_with_bank_details_list = list(FarmerBankDetails.objects.filter(farmer_id__in=farmer_cluster_df['Farmer Id']).values_list('farmer_id', flat=True))
    ##farmers without bank details
    farmers_without_bank_details_list = list(set(farmer_cluster_df['Farmer Id'])-set(farmers_with_bank_details_list))
    ##farmers without bank details df
    farmers_without_bank_details_df = farmer_cluster_df[farmer_cluster_df['Farmer Id'].isin(farmers_without_bank_details_list)] 


    ## Excel Report

    writer = pd.ExcelWriter(str("static/media/") + "master_farmers_report.xlsx", engine="xlsxwriter")

    df_dict = {
        "Farmers And Details": {
            'df' : farmer_cluster_df.drop(['Farmer Id'], axis=1),
            'title' : "Farmer Details"
            },
        "Farmers Without Nursery Sowing": {
            "df" :farmers_without_cp1_df.drop(['Farmer Id'], axis=1),
            "title" : "No Nursery"
            },
        "Farmers Without Transplanted Sowing": {
            "df" :farmers_without_cp2_df.drop(['Farmer Id'], axis=1),
            "title" : "No Tp"
            },
        "Farmers Having Nursery Sowing But Cultivation Area Not Calculated": {
            "df" :farmers_without_cp1_fence_df.drop(['Farmer Id'], axis=1),
            "title" : "No Nursery Geo Fence"
            },
        "Farmers Having Transplanted Sowing But Cultivation Area Not Calculated": {
            "df" :farmers_without_cp2_fence_df.drop(['Farmer Id'], axis=1),
            "title" : "No Tp Geo Fence"
            },
        "Farmers Having Transplanted Sowing But Not Having Harvest": {
            "df" :farmers_without_cp2_harvest_df.drop(['Farmer Id'], axis=1),
            "title" : "No Harvest"
            },
        "Farmers Without Bank Account Details": {
            "df" :farmers_without_bank_details_df.drop(['Farmer Id'], axis=1),
            "title" : "No Bank Details"
            }
    }

    for index, title in enumerate(df_dict):
        
        print(title)
        # creating excel sheet with name
        df_dict[title]['df'].to_excel(writer, sheet_name=df_dict[title]['title'], startrow=1, index=False)
        # assigning that sheet to obj
        workbook = writer.book
        worksheet = writer.sheets[df_dict[title]['title']]
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )

        date = datetime.datetime.now().date()
        # Merge 3 cells.
        worksheet.merge_range("A1:G1", title + " - " + str(date), merge_format)

        format1 = workbook.add_format({"num_format": "#,##0.00"})

        # Set the column width and format.
        worksheet.set_column("B:B", 18, format1)
        worksheet.set_column(0, 17, 20)

        # Add a header format.
        header_format = workbook.add_format({"fg_color": "#D7E4BC"})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(df_dict[title]['df'].columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    data = {
        'name': "master_farmers_report.xlsx",
    }
    try:
        image_path = str("static/media/") + "master_farmers_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_transaction_balance(request):
    print('got hit')
    agent_id = request.data['agent_id']
    season_id = get_active_season_id()

    transaction_log_ids = []
    transaction_log_ids = transaction_log_ids + list(InputDistributionTransactionMap.objects.filter(agent_inventory__season_id=season_id).values_list('transaction_log', flat=True))
    transaction_log_ids = transaction_log_ids + list(InputReturnTransactionLog.objects.filter(combo_return_request__season_id=season_id).values_list('transaction_log', flat=True))
    transaction_log_ids = transaction_log_ids + list(InputProcurementTransactionLog.objects.filter(procurement__procurement_group__season_id=season_id).values_list('transaction_log', flat=True))
    transaction_log_ids = list(set(transaction_log_ids))

    if AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=1, id__in=transaction_log_ids).exists():
        total_bought = AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=1).aggregate(Sum('amount'))['amount__sum']
    else:
        total_bought = 0 
        
    if AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=4, id__in=transaction_log_ids).exists():
        returned_value = AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=4, id__in=transaction_log_ids).aggregate(Sum('amount'))['amount__sum']
    else:
        returned_value = 0
        
    total_purchased = total_bought - returned_value

    if AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=2, id__in=transaction_log_ids).exists():
        recovered_amount = AgentTransactionLog.objects.filter(agent_id=agent_id, transaction_direction_id=2).aggregate(Sum('amount'))['amount__sum']
    else:
        recovered_amount = 0
        
    wallet_balance = total_purchased - recovered_amount
    wallet_balance
    data = {
        'total_bought': total_bought,
        'returned_value': returned_value,
        'total_purchased': total_purchased,
        'recovered_amount': recovered_amount
    }
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_inward_goods_ledger_report(request):
    data = {
        "have_data": False
    }
    input_type_list = list(InputType.objects.all().values_list('id', 'name'))
    input_type_column = ['Input Type Id', 'Input Type Name']
    input_type_df = pd.DataFrame(input_type_list, columns=input_type_column)

    input_goods_obj = InputGoods.objects.all().order_by('id')
    input_goods_list = list(
        input_goods_obj.values_list('id', 'code', 'input_name__input_type', 'input_name__name','quantity_now', 'quantity_at_receipt',
                                    'number_of_units', 'date_of_expiry', 'date_of_manufacturing', 'date_of_receipt',
                                    'supplier__name', 'cost', 'unit__name'))
    input_goods_column = ['Id', 'Code', 'Input Type Id', 'Name Of Good', 'Total Qty', 'Received Qty', 'Number Of Units',
                          'Date Of Expiry', 'Date Of Manufacture', 'Date Of Receipt', 'Supplier Name', 'Cost', 'Unit Name']
    input_goods_df = pd.DataFrame(input_goods_list, columns=input_goods_column)

    if not input_goods_df.empty:
        data['have_data'] = True
        input_goods_df['Is Goods Taken'] = "False"
        input_goods_df.loc[input_goods_df['Total Qty'] != input_goods_df['Received Qty'], 'Is Goods Taken'] = "True"

        final_df = pd.merge(input_goods_df, input_type_df, left_on='Input Type Id', right_on='Input Type Id', how='left') 
        final_df = final_df.fillna(0)

        writer = pd.ExcelWriter(str("static/media/") + "inward_goods_ledger.xlsx", engine="xlsxwriter")

        for input_type in list(set(list(final_df['Input Type Name']))):
            input_df = final_df[final_df['Input Type Name'] == input_type].reset_index(drop=True)
            input_df = input_df.drop(columns=['Input Type Name', 'Unit Name', 'Is Goods Taken', 'Id', 'Input Type Id'])
            input_df['Cost'] = input_df['Cost'].astype(float)
            input_df['Number Of Units'] = input_df['Number Of Units'].astype(str)

            input_df.index += 1
            total = input_df.sum(numeric_only=True)
            total.name = 'Total'
            input_df = input_df.append(total.transpose())

            # creating excel sheet with name
            input_df.to_excel(writer, sheet_name=input_type, startrow=1)
            # assigning that sheet to obj"
            workbook = writer.book
            worksheet = writer.sheets[input_type]
            merge_format = workbook.add_format(
                {
                    "bold": 1,
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "fg_color": "yellow",
                }
            )

            date = datetime.datetime.now().date()
            # Merge 3 cells.
            worksheet.merge_range("A1:K1", "Inward Goods Ledger" + " - " + str(date), merge_format)

            format1 = workbook.add_format({"num_format": "#,##0.00"})

            # Set the column width and format.
            worksheet.set_column("B:B", 18, format1)
            worksheet.set_column(0, 17, 20)

            # Add a header format.
            header_format = workbook.add_format({"fg_color": "#D7E4BC"})

            # Write the column headers with the defined format.
            for col_num, value in enumerate(input_df.columns.values):
                worksheet.write(0, col_num + 1, value, header_format)
        writer.save()
        try:
            image_path = str("static/media/") + "inward_goods_ledger.xlsx"
            with open(image_path, "rb") as image_file:
                encoded_image = b64encode(image_file.read())
                data["excel"] = encoded_image
        except Exception as err:
            print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_agent_wise_procurement_weight_report(request):
    data = {}
    season_id = request.data['season_id']
    net_weight = str(request.data['net_weight'])


    agent_procurement_list = ProcurementGroup.objects.filter(season_id=season_id).values_list('agent__first_name', 'procurement_date', 'procurement_produce__name',
                                                                                                    'season__name', 'produce_net_weight', 'price_per_unit', 'cost', 'agent_price_deduction', 
                                                                                                    'payment_to_wallet', 'payment_to_agent')
    agent_procurement_column = ['Agent Name', 'Procurement Date', 'Procurement Produce Name','Season', 'Produce Net Weight', 'Price Per Unit', 'Cost', 'Agent Price Deduction', 
                                                                                                    'Payment To Wallet', 'Payment To Agent']  
    agent_procurement_df = pd.DataFrame(agent_procurement_list, columns=agent_procurement_column)

    agent_procurement_df["Net Weight In Ton"] = agent_procurement_df["Produce Net Weight"]/1000

    agent_procurement_df = agent_procurement_df.fillna(0)

    if net_weight == "4":
        final_df = agent_procurement_df[(agent_procurement_df['Net Weight In Ton'] >= 4) & (agent_procurement_df['Net Weight In Ton']/1000 <=6)]
    if net_weight == "6":
        final_df = agent_procurement_df[(agent_procurement_df['Net Weight In Ton'] > 6) & (agent_procurement_df['Net Weight In Ton']/1000 <=8)]
    if net_weight == "8":
        final_df = agent_procurement_df[(agent_procurement_df['Net Weight In Ton'] > 8)]

    writer = pd.ExcelWriter(str("static/media/") + "agent_wise_procurement_weight_report.xlsx", engine="xlsxwriter")

    final_df = final_df.reset_index(drop=True)
    final_df[['Produce Net Weight', 'Price Per Unit', 'Cost', 'Agent Price Deduction','Payment To Wallet', 'Payment To Agent', 'Net Weight In Ton']] = final_df[['Produce Net Weight', 'Price Per Unit', 'Cost', 'Agent Price Deduction','Payment To Wallet', 'Payment To Agent', 'Net Weight In Ton']].astype(float)

    final_df.index += 1
    total = final_df.sum(numeric_only=True)
    total.name = 'Total'
    final_df = final_df.append(total.transpose())

    # creating excel sheet with name
    final_df.to_excel(writer, sheet_name="sheet1", startrow=1)
    # assigning that sheet to obj"
    workbook = writer.book
    worksheet = writer.sheets["sheet1"]
    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        }
    )

    date = datetime.datetime.now().date()
    # Merge 3 cells.
    worksheet.merge_range("A1:L1", "Agent Wise Procurement Weight Report" + " - " + str(date), merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)
    worksheet.set_column(0, 17, 20)

    # Add a header format.
    header_format = workbook.add_format({"fg_color": "#D7E4BC"})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    try:
        image_path = str("static/media/") + "agent_wise_procurement_weight_report.xlsx"
        with open(image_path, "rb") as image_file:
            encoded_image = b64encode(image_file.read())
            data["excel"] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_seasons(request):
    from datetime import date
    today = date.today()
    season_list = []
    dict_season = {}
    season_obj = Season.objects.filter().order_by('id')
    for season in season_obj:
        temp_dict={
            'season_id': season.id,
            'season_name': season.name,
            'year': season.year,
            'start_date': season.start_date,
            'end_date': season.end_date,
            'is_active': season.is_active,
        }
        season_list.append(temp_dict)
        dict_season['season_list'] = season_list
        dict_season['end_date'] = today.strftime("%Y-%m-%d")
    return Response(data=dict_season, status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def add_new_season(request):
    sid = transaction.savepoint()
    print(request.data)
    ordinal = list(Season.objects.filter().values_list('ordinal', flat=True).order_by('-id'))
    new_ordinal = ordinal[0]+1
    is_active = request.data['is_active']
    season_name = request.data['season_name'].strip()
    print(season_name)
    if not Season.objects.filter(name=season_name).exists():
        try:
            new_season_obj = Season(
                name = request.data['season_name'],
                year = request.data['year'],
                crop_id = 1,
                start_date = request.data['start_date'],
                end_date = request.data['end_date'],
                ordinal = new_ordinal,
                created_by_id = request.user.id,
                modified_by_id = request.user.id
            )
            if is_active == True:
                Season.objects.filter(is_active=True).update(is_active=False)
                is_active = request.data['is_active']
            new_season_obj.save()
            print('new_season_saved')
            for superior in UserHierarchyMap.objects.filter(superior_user_type_id__in=[1,2,4]):
                new_hy_user_obj = UserHierarchyMap(
                    superior_user_type=superior.superior_user_type,
                    season_id=new_season_obj.id,
                    superior=superior.superior,
                    subordinate_user_type=superior.subordinate_user_type
                )
                subordinate_user_ids = UserHierarchyMap.objects.filter(superior_user_type_id=superior.superior_user_type_id)
                #to get manytomany field ids 
                subordinates = list(subordinate_user_ids.values_list("subordinate", flat=True))
                new_hy_user_obj.save()
                #loop and save the manytomany fields as Objs      
                for sub_ord in subordinates:
                    # print(sub_ord)
                    new_hy_user_obj.subordinate.add(User.objects.get(id=sub_ord))
                    new_hy_user_obj.save()
            print("user_mapped GM, AM, AO")
            transaction.savepoint_commit(sid)
            return Response(data='new_season_added', status=status.HTTP_200_OK)
        except Exception as e:
            print('error on {}'.format(e))
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_404_NOT_FOUND)   
    return Response(data=False, status=status.HTTP_200_OK)

@api_view(['POST'])
def make_season_active_inactive(request):
    Season.objects.filter(is_active=True).update(is_active=False)
    season_status = Season.objects.get(id=request.data).is_active
    if season_status == True:
        Season.objects.filter(id=request.data).update(is_active=False)
    else:
        Season.objects.filter(id=request.data).update(is_active=True)
    print('done')
        
    return Response(data='updated', status=status.HTTP_200_OK)

@api_view(["POST"])
def map_asf_and_sfs(request):
    print(request.data)

    if not UserHierarchyMap.objects.filter(superior_user_type_id=3, season_id=get_active_season_id(), superior_id=request.data['sfs_id'], subordinate_user_type_id=5).exists():
        user_hierarchy_obj = UserHierarchyMap.objects.create(superior_user_type_id=3, season_id=get_active_season_id(), superior_id=request.data['sfs_id'], subordinate_user_type_id=5)
    else:
        user_hierarchy_obj = UserHierarchyMap.objects.get(superior_user_type_id=3, season_id=get_active_season_id(), superior_id=request.data['sfs_id'], subordinate_user_type_id=5)
    user_obj = User.objects.get(id=request.data['afs_id'])
    user_hierarchy_obj.subordinate.add(user_obj)

    data = {
        "status" : "success"
    }
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def unmap_asf_and_sfs(request):
    print(request.data)

    user_hierarchy_obj = UserHierarchyMap.objects.get(superior_user_type_id=3, season_id=get_active_season_id(), superior_id=request.data['sfs_id'], subordinate_user_type_id=5)
    user_obj = User.objects.get(id=request.data['user_id'])
    user_hierarchy_obj.subordinate.remove(user_obj)
    data = {
        "status" : "success"
    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["POST"])
def active_inactive_users(request):
    print(request.data)
    data = request.data
    user_obj = User.objects.get(id=data['user_id'])
    user_obj.is_active = data['is_active']
    user_obj.save()
    return Response(True, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_active_inactive_sfs(request):
    season_id = get_active_season_id()
    master_dict = {}

    active_sfs_ids = list(UserHierarchyMap.objects.filter(superior_user_type_id=3, season_id=season_id).values_list('superior_id', flat=True))

    active_users = list(UserProfile.objects.filter(user_id__in=active_sfs_ids).values_list('user_id', 'user__username', 'user__last_name'))
    active_users_columns = ['user_id', 'first_name', 'last_name']
    active_users_df = pd.DataFrame(active_users, columns=active_users_columns)
    master_dict['active'] = active_users_df.to_dict('r')

    in_active_sfs_ids = list(UserHierarchyMap.objects.filter(superior_user_type_id=3).values_list('superior_id', flat=True))
    in_active_users = list(UserProfile.objects.filter(user_id__in=in_active_sfs_ids).exclude(user_id__in=active_sfs_ids).values_list('user_id', 'user__username', 'user__last_name'))
    in_active_users_columns = ['user_id', 'first_name', 'last_name']
    in_active_users_df = pd.DataFrame(in_active_users, columns=in_active_users_columns)
    in_active_users_df = in_active_users_df.drop_duplicates(subset=['user_id'])
    master_dict['in_active'] = in_active_users_df.to_dict('r')
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def map_unmap_season_for_sfs(request):
    print(request.data)
    data = request.data
    season_id = get_active_season_id()
    if data['map_to_season']:
        UserHierarchyMap.objects.create(superior_id=data['user_id'],season_id=season_id,superior_user_type_id=3,subordinate_user_type_id=5)
    else:
        user_hierarchy_obj = UserHierarchyMap.objects.get(superior_id=data['user_id'],season_id=season_id)
        user_hierarchy_obj.delete()
    return Response(True, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_temp_season_based_gap(request):
    print(request.data)
    if request.data['gap_id'] == None:
        season_id = request.data['gap_selected_season_id']
        ordinal_count = TempSeasonBasedGap.objects.filter().count()
        ordinal = ordinal_count + 1
        temp_season_based_gap = TempSeasonBasedGap(
                season_id = season_id,
                action_name = request.data['action_name'],
                followup_date = request.data['followup_date'],
                description = request.data['description'],
                ordinal = ordinal,
                # quantity = Decimal(request.data['quantity']),
                created_by_id = request.user.id,
                modified_by_id = request.user.id
                )
        temp_season_based_gap.save()
        return Response(data={'status':'success'}, status=status.HTTP_200_OK)
    else:
        temp_season_based_gap = TempSeasonBasedGap.objects.filter(id=request.data['gap_id']).update(
                action_name = request.data['action_name'],
                followup_date = request.data['followup_date'],
                description = request.data['description'],
                # quantity = Decimal(request.data['quantity']),
                modified_by_id = request.user.id
                )
        return Response(data={'status':'success'}, status=status.HTTP_200_OK)
        


@api_view(['POST'])
def get_season_based_gap(request):
    data = {}
    data['status']=False
    season_id = request.data['season_id']
    if season_id == get_active_season_id():
        data['display_clone'] = False
        if SeasonBasedGap.objects.filter(season_id=season_id).exists():
            temp_season_based_gap_obj = SeasonBasedGap.objects.filter(season_id=season_id).values_list('id','season_id' ,'action_name', 'followup_date', 'quantity', 'description', 'ordinal')
            data['status']=True
        else:
            data['status']=False
            temp_season_based_gap_obj = TempSeasonBasedGap.objects.filter(season_id=season_id).values_list('id','season_id' ,'action_name', 'followup_date', 'quantity', 'description', 'ordinal')
    else:
        if SeasonBasedGap.objects.filter(season_id=get_active_season_id()).exists():
            data['display_clone'] = False
        else:
            data['display_clone'] = True
        data['status']=True
        temp_season_based_gap_obj = SeasonBasedGap.objects.filter(season_id=season_id).values_list('id','season_id' ,'action_name', 'followup_date', 'quantity', 'description', 'ordinal')
    
    columns = ['gap_id','season_id' ,'action_name', 'followup_date', 'quantity', 'description', 'ordinal']
    temp_season_based_gap_df = pd.DataFrame(list(temp_season_based_gap_obj), columns=columns)
    temp_season_based_gap_list = temp_season_based_gap_df.to_dict('r') 
    data['data'] = temp_season_based_gap_list
   

    return Response(data=data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def delete_season_based_gap(request):
    temp_season_based_gap_obj = TempSeasonBasedGap.objects.filter(id=request.data['id'])
    temp_season_based_gap_obj.delete()
    return Response(data={'status':'Deleted'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def swapping_season_based_gap_rows(request):
    gap_id = request.data['gap_id']
    season_id = request.data['season_id']
    current_ordinal = request.data['current_ordinal']
    to_change_ordinal = request.data['to_change_ordinal']

    current = TempSeasonBasedGap.objects.get(id=gap_id)
    to_change = TempSeasonBasedGap.objects.get(season_id=season_id, ordinal=to_change_ordinal)

    print(current.ordinal, to_change.ordinal)

    current.ordinal = to_change_ordinal
    current.save()

    to_change.ordinal = current_ordinal
    to_change.save()
    return Response(data={'status':'success'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def freeze_season_based_gap(request):
    data = {}
    season_id = request.data['season_id']
    # check season has no previous gap activated
    if SeasonBasedGap.objects.filter(season_id=season_id).exists():
        data['message'] = 'You have been already finalized the GAP'
        data['status'] = False
        return Response(data=data, status=status.HTTP_200_OK)
    if not TempSeasonBasedGap.objects.filter(season_id=season_id).exists():
        data['message'] = 'You must have atleast one GAP to finalize'
        data['status'] = False
        return Response(data=data, status=status.HTTP_200_OK)
    temp_season_based_gap_obj = list(TempSeasonBasedGap.objects.filter(season_id=season_id).values())
    for row_obj in temp_season_based_gap_obj:
        iterated_obj_id = row_obj['id']
        row_obj['id'] = None
        gap_obj = SeasonBasedGap.objects.create(**row_obj)
        if TempSeasonBasedGapQuestion.objects.filter(gap_id=iterated_obj_id).exists():
            gap_datas = list(TempSeasonBasedGapQuestion.objects.filter(gap_id=iterated_obj_id).values())
            for gap_data in gap_datas:
                gap_data['id'] = None
                gap_data['gap_id'] = gap_obj.id
                SeasonBasedGapQuestion.objects.create(**gap_data)
    TempSeasonBasedGap.objects.filter().delete()
    # TempSeasonBasedGapQuestion.objects.filter().delete()
    data['message'] = 'You have successfully created the GAP for this season'
    data['status'] = True
    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['POST'])
def clone_to_current_season_gap(request):
    data = {}
    season_id = request.data['season_id']
    if not request.data['confirm']:
        # check season has no previous gap activated
        if not SeasonBasedGap.objects.filter(season_id=season_id).exists():
            data['message'] = 'You have no GAP recorded before.'
            data['status'] = 3
            return Response(data=data, status=status.HTTP_200_OK)
        if TempSeasonBasedGap.objects.filter(season_id=get_active_season_id()).exists():
            data['message'] = 'Already there are some GAP for current season , Do you want to replace them'
            data['status'] = 2
            return Response(data=data, status=status.HTTP_200_OK)
        temp_season_based_gap_obj = list(SeasonBasedGap.objects.filter(season_id=season_id).values())
        active_season_id = get_active_season_id()
        for row_obj in temp_season_based_gap_obj:
            iterated_obj_id = row_obj['id']
            row_obj['id'] = None
            row_obj['season_id'] = active_season_id
            temp_gap = TempSeasonBasedGap.objects.create(**row_obj)

            if SeasonBasedGapQuestion.objects.filter(gap_id=iterated_obj_id).exists():
                gap_datas = list(SeasonBasedGapQuestion.objects.filter(gap_id=iterated_obj_id).values())
                for gap_data in gap_datas:
                    gap_data['id'] = None
                    gap_data['gap_id'] = temp_gap.id
                    TempSeasonBasedGapQuestion.objects.create(**gap_data)

        data['message'] = 'You have successfully created the GAP for this season, please finalize to activate it.'
        data['status'] = 1
        return Response(data=data, status=status.HTTP_200_OK)

    else:
        TempSeasonBasedGap.objects.filter(season_id=get_active_season_id()).delete()
        temp_season_based_gap_obj = list(SeasonBasedGap.objects.filter(season_id=season_id).values())
        active_season_id = get_active_season_id()
        for row_obj in temp_season_based_gap_obj:
            row_obj['id'] = None
            row_obj['season_id'] = active_season_id
            TempSeasonBasedGap.objects.create(**row_obj)

        data['message'] = 'You have successfully created the GAP for this season, please finalize to activate it.'
        data['status'] = 1
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_gap_logs(request):
    data = {}
    data['logs'] = []
    data['answerd'] = []
    data['next_gap'] = "Done"
    sowing_id= request.data['sowing_id']
    season_id = get_active_season_id()
    sowing_obj = Sowing.objects.get(id=sowing_id)
    if SeasonBasesFarmerGpaLog.objects.filter(season_id=season_id, sowing_id=sowing_id).exists():
        season_based_farmer_gap_log = SeasonBasesFarmerGpaLog.objects.filter(season_id=season_id, sowing_id=sowing_id).order_by("gap__ordinal")
        gap_values = list(season_based_farmer_gap_log.values_list('gap_id', 'gap__action_name', 'gap__followup_date', 'gap__description',
            'gap__quantity', 'expected_date', 'actual_date', 'variations', 'gap__ordinal', 'is_skip'))
        gap_colummns = ['gap_id', 'gap__action_name', 'gap__followup_date', 'gap__description',
            'gap__quantity', 'expected_date', 'actual_date', 'variations', 'ordinal', 'is_skip']

        gap_df = pd.DataFrame(gap_values, columns=gap_colummns)
        gap_df = gap_df.fillna('')
        data['logs'] = gap_df.to_dict('r')

        season_based_farmer_gap_log_ids = list(SeasonBasesFarmerGpaLog.objects.filter(season_id=season_id, sowing_id=sowing_id).values_list('id', flat=True))
        print('season_based_farmer_gap_log', season_based_farmer_gap_log_ids)
        gap_answer_log_obj = SeasonBasesFarmerGpaQuestionAnswerLog.objects.filter(farmer_gap_log_id__in=season_based_farmer_gap_log_ids).values_list('farmer_gap_log_id','question__questions', 'farmer_gap_log__gap_id', 'answer')
        gap_answer_columns = ["farmer_gap_log_id", "question_name", "gap_id","answer"]
        gap_answer_log_df = pd.DataFrame(list(gap_answer_log_obj), columns=gap_answer_columns)
        gap_answer_log_df = gap_answer_log_df.fillna('')
        data['answerd'] = gap_answer_log_df.to_dict('r')
        print(data['answerd'])

        total_gap = SeasonBasedGap.objects.filter(season_id=season_id).count()
        completed_gap = season_based_farmer_gap_log.count()
        print(completed_gap)
        print(total_gap)
        if total_gap != completed_gap:
            next_gap_ordinal = completed_gap + 1
            data['next_gap'] = pd.DataFrame(SeasonBasedGap.objects.filter(ordinal=next_gap_ordinal, season_id=season_id).values()).to_dict('r')[0]
            data['next_gap']['expected_date'] = sowing_obj.sowing_date + datetime.timedelta(days=int(data['next_gap']['followup_date']))

    else:
        data['next_gap'] = pd.DataFrame(SeasonBasedGap.objects.filter(ordinal=1, season_id=season_id).values()).to_dict('r')[0]
        print(data['next_gap'])
        data['next_gap']['expected_date'] = sowing_obj.sowing_date + datetime.timedelta(days=int(data['next_gap']['followup_date']))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_gap(request):
    # data = {}
    print("======================")
    print(request.data)
    answer_list = request.data['answer_list']
    answer_list_text = request.data['answer_list_text']
    if request.data['is_skip'] == 0:
        is_skip = 0
    else:
        is_skip = 1
    season_id = get_active_season_id()
    if SeasonBasesFarmerGpaLog.objects.filter(season_id=season_id, sowing_id=request.data['sowing_id'], gap_id=request.data['id']).exists():
        print('already exists')
    else:
        print("new")
        sowing_obj = Sowing.objects.get(id=request.data['sowing_id'])
        variations = 1
        expected_date = datetime.datetime.strptime(request.data['expected_date'], '%Y-%M-%d')
        actual_date = datetime.datetime.strptime(request.data['actual_date'],  '%Y-%M-%d')
        variations_date = expected_date-actual_date
        variations_date = abs(variations_date.days)
        print(variations_date)
        season_bases_farmer_gpa_log_obj = SeasonBasesFarmerGpaLog(
            season_id=season_id, 
            sowing_id=request.data['sowing_id'], 
            gap_id=request.data['id'],
            tp_date=sowing_obj.sowing_date,
            expected_date=request.data['expected_date'],
            actual_date=request.data['actual_date'],
            variations = variations_date,
            is_skip = is_skip,
            created_by=request.user,
            modified_by=request.user
            )
        season_bases_farmer_gpa_log_obj.save()
        if len(answer_list) > 0 and is_skip == 0:
            answer = 'yes'
            for question_id in answer_list:
                gap_answer_log_obj = SeasonBasesFarmerGpaQuestionAnswerLog(
                                            farmer_gap_log_id=season_bases_farmer_gpa_log_obj.id,
                                            question_id = question_id,
                                            answer = answer)
                gap_answer_log_obj.save()
        else:
            print('for_skip')
            gap_answer_log_obj = SeasonBasesFarmerGpaQuestionAnswerLog(
                                        farmer_gap_log_id=season_bases_farmer_gpa_log_obj.id,
                                        # question_id = question_id,
                                        is_skipped = is_skip)
            gap_answer_log_obj.save()
        for value in answer_list_text:
            if value['answer'] != "":
                print("value['answer']", value['answer'])
                gap_answer_log_obj = SeasonBasesFarmerGpaQuestionAnswerLog(
                                        farmer_gap_log_id=season_bases_farmer_gpa_log_obj.id,
                                        question_id = value['quest_id'],
                                        answer = value['answer'],
                                        is_skipped = is_skip)
            gap_answer_log_obj.save()
    return Response(data={'status': 'saved successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_gap(request):
    data = {}
    if TempSeasonBasedGap.objects.filter(id=request.data['gap_id']).exists():
        TempSeasonBasedGap.objects.filter(id=request.data['gap_id']).delete()
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_farmer_bank_aadhar_photocopy(request):
    farmer_id = request.data['farmer_id']

    passbook_img = request.data['passbook_img']
    aadhar_img = request.data['aadhar_img']
    if passbook_img != None:
        print('yes')
        farmer_bank_obj = FarmerBankDetails.objects.get(farmer_id=farmer_id)
        farmer_bank_obj.bank_passbook_document = create_complete_image(passbook_img)
        farmer_bank_obj.save()
        print('passbook_img_saved')
    else:
        print('no')
        farmer_aadhar_obj = Farmer.objects.get(id=farmer_id)
        farmer_aadhar_obj.aadhaar_document = create_complete_image(aadhar_img)
        farmer_aadhar_obj.save()
        print('aadhar_img_saved')
    return Response(data={'status': 'Image Uploaded Successfully' }, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_question_types(request):
    data = pd.DataFrame(GapQuestionType.objects.filter().values()).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_question_based_on_gap(request):
    if SeasonBasedGapQuestion.objects.filter(gap__season_id=request.data['season_id']).exists():
        question_obj = SeasonBasedGapQuestion.objects.filter(gap__season_id=request.data['season_id'], gap_id=request.data['gap_id'])
    elif TempSeasonBasedGapQuestion.objects.filter(gap__season_id=request.data['season_id']).exists():
        question_obj = TempSeasonBasedGapQuestion.objects.filter(gap__season_id=request.data['season_id'], gap_id=request.data['gap_id'])
    else:
        data = []
        return Response(data=data, status=status.HTTP_200_OK)

    data = pd.DataFrame(question_obj.values()).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_questions(request):
    print(request.data)
    if request.data['qtn_id'] is None:
        count = TempSeasonBasedGapQuestion.objects.filter(gap_id=request.data['gap_id']).count()
        ordinal = count + 1
        TempSeasonBasedGapQuestion.objects.create(
            gap_id=request.data['gap_id'],
            questions=request.data['questions'],
            question_type_id=request.data['question_type_id'],
            ordinal=ordinal,
            created_by=request.user,
            modified_by=request.user,
        )
    else:
        TempSeasonBasedGapQuestion.objects.filter().update(
            questions=request.data['questions'],
            question_type_id=request.data['question_type_id'],
            modified_by=request.user,
        )
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_questions(request):
    TempSeasonBasedGapQuestion.objects.filter(id=request.data['qtn_id']).delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_gap_questions(request):
    season_based_question_obj =  SeasonBasedGapQuestion.objects.filter(gap__season_id=get_active_season_id(), gap_id=request.data['gap_id']).values_list('id', 'questions', 'gap_id','gap__action_name', 'question_type_id', 'question_type__name', 'is_active', 'is_manditory')
    season_based_question_columns = ["quest_id", "questions", "gap_id", "gap_action_name", "question_type_id", "question_type_name", "is_active", "is_manditory"]
    season_based_question_df = pd.DataFrame(list(season_based_question_obj), columns=season_based_question_columns)
    season_based_question_df['answer'] = ''
    season_based_question_df['toggle'] = False
    data = season_based_question_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def save_gap_questions(request):
    print(request.data)
    answer = request.data['answer']
    farmer_gap_log = request.data['farmer_gap_log']
    is_skipped = request.data['is_skipped']
    question_id = request.data['question_id']
    if not SeasonBasesFarmerGpaQuestionAnswerLog.objects.filter(question_id=question_id):
        gap_answer_log_obj = SeasonBasesFarmerGpaQuestionAnswerLog(
                                    farmer_gap_log_id=farmer_gap_log,
                                    question_id = question_id,
                                    answer = answer,
                                    is_skipped = is_skipped)
        gap_answer_log_obj.save()
    else:
         return Response(data={'status': 'already existed'}, status=status.HTTP_200_OK)
    return Response(data={'status': 'saved successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def payment_hold_procurement(request):
    print(request.data)
    procurement_id =  request.data['procurement_id']
    reason =  request.data['reason']
    if Procurement.objects.filter(procurement_group__season_id=get_active_season_id(), id=procurement_id).exists():
        procurement_obj = Procurement.objects.get(id=procurement_id)
        procurement_obj.paymet_status_id = 2
        procurement_obj.reason_for_payment_hold = reason
        procurement_obj.save()
        print('payment_hold_updated')
    else:
        print('not')
        Response(data={'status': 'not_existed'}, status=status.HTTP_200_OK)
    return Response(data={'status': 'payment_hold_updated'}, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_procurement_log_payment_hold(request):
    season_id = get_active_season_id()
    data = list(set(list(Procurement.objects.filter(procurement_group__season_id=season_id).order_by("procurement_group__procurement_date").values_list("procurement_group__procurement_date", flat=True))))
    # print(data)
    data = sorted(data, reverse=True)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def unhold_procurement(request):
    print(request.data)
    procurement_id = request.data['procurement_id']
    Procurement.objects.filter(id=procurement_id).update(paymet_status_id=1)
    return Response(data={'status': 'done'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_utr_number(request):
    print(request.data)
    utr_number = request.data['utr_number']
    if utr_number is not None:
        Procurement.objects.filter(ticket_number=request.data['ticket_number']).update(utr_number=utr_number, paymet_status_id=4)
    else:
        print('None_value')
    return Response(data={'status': 'done'}, status=status.HTTP_200_OK)

