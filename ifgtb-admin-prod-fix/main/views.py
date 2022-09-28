from django.db.models.expressions import Exists
from diagnosis.models import CircularCategory, UserQuery
from requests.models import Request
from diagnosis.models import CircularCategory
from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from main.models import *
from main.models import WaterResource
from diagnosis.models import QueryExpertAssignMap
import json
from jamun_admin.local_settings import *
from base64 import b64encode, b64decode
from cms.models import *
from django.conf import settings


from collections import defaultdict
import random
import requests
from django.contrib.auth.hashers import make_password
import pandas as pd
from django.db import transaction
import datetime
from main.serializer import *
import logging
import json
from django.core.files.base import ContentFile
from fcm_django.models import FCMDevice
from pyfcm import FCMNotification

# AIzaSyBgiY6Ia2lTFZfdWOUSQc3BkxfWim_3rFs
youtube_api_key = 'AIzaSyAJH8SrUjMOaHgFu4HlAkUGbS5hCOBN5pc'
push_service = FCMNotification(api_key="AAAAE2t8QAs:APA91bH9zLySlxXGTTFT7D4rOU1oSbXPbewxkveXrtSY7QrSpQJdwntKCjIaWt0pStqPd392eDIIrYjC62JcO6XXdmQ7Dq_yMNYhbtmL1bBtos5k7EChAzexloHkZbBVksciF3nU8v4G")
# youtube_api_key = 'AIzaSyAJH8SrUjMOaHgFu4HlAkpc'

#google auth
from google_access import Create_Service
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'google-client-data.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing',
          'https://www.googleapis.com/auth/photoslibrary.readonly']

# todate = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
# logging_path = f'/var/log/jamun/{todate}.log'
# logging.basicConfig(
#     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#     datefmt='%Y-%m-%d:%H:%M:%S', filename=logging_path, level=logging.INFO
# )
# logging.info('started')


# Create your views here.
@api_view(['POST'])
@permission_classes((AllowAny,))
def website_login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            user_dict['first_name'] = user.first_name
            user_dict['user_id'] = user.id
            user_dict['user_type'] = UserProfile.objects.get(user=user).user_type_id
            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((AllowAny,))
def portal_login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            user_dict['first_name'] = user.first_name
            user_dict['user_type'] = UserProfile.objects.get(user_id = user.id).user_type.name
            user_dict['indusry_contact_person'] = False
            user_dict['nursery_contact_person'] = False
            user_dict['institute_contact_person'] = False
            user_dict['forest_contact_person'] = False
            user_profile = UserProfile.objects.get(user_id = user.id)
            if IndustryOfficial.objects.filter(user_profile_id=user_profile.id).exists():    
                user_dict['indusry_contact_person'] = IndustryOfficial.objects.get(user_profile_id=user_profile.id).is_contact_person
            if NurseryIncharge.objects.filter(user_profile_id=user_profile.id).exists():
                user_dict['nursery_contact_person'] = NurseryIncharge.objects.get(user_profile_id=user_profile.id).is_contact_person
            if Scientist.objects.filter(user_profile_id=user_profile.id).exists():
                user_dict['institute_contact_person'] = Scientist.objects.get(user_profile_id=user_profile.id).is_contact_person
            if ForestOfficial.objects.filter(user_profile_id=user_profile.id).exists():
                user_dict['forest_contact_person'] = ForestOfficial.objects.get(user_profile_id=user_profile.id).is_contact_person

            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


def generate_otp():
    return str(random.randint(1000, 9999))


# check wheather a valid user for password reset
@api_view(["POST"])
@permission_classes((AllowAny,))
def username_validation(request):
    print(request.data)
    if User.objects.filter(username=request.data["user_name"]).exists():
        print(request.data['user_name'])
        user = User.objects.get(username=request.data["user_name"])
        user_obj = UserProfile.objects.get(user=user)
        if user_obj.mobile is None:
            data = {"message": "Phone number does not Exists!"}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
        otp = generate_otp()
        purpose = "forgot_password"
        msg = "OTP for password reset your IFGTP account is " + otp
        if OTP.objects.filter(mobile=request.data["user_name"], purpose=purpose).exists():
            OTP.objects.filter(mobile=request.data["user_name"], purpose=purpose).update(
                otp=otp
            )
        else:
            OTP_obj = OTP(
                purpose=purpose,
                mobile=request.data["user_name"],
                otp=otp
            )
            OTP_obj.save()

        user_details = {
            'username': user_obj.user.username,
            'first_name': user_obj.user.first_name,
            'user_id': user_obj.user_id,
            'is_available': True
        }
        print(msg)
        send_message_via_netfision('verify', request.data['user_name'], str(msg))

        return Response(data=user_details, status=status.HTTP_200_OK)
    else:
        data = {"message": "User does not Exists!", 'is_available': False}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
@permission_classes((AllowAny,))
def otp_validation(request):
    print(request.data)
    if OTP.objects.filter(mobile=request.data["user_name"], purpose=request.data['purpose'],
                          otp=request.data["otp"]).exists():
        data = {"message": "OTP Matched"}
        print('verified')
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        print('not verified')
        data = {"message": "OTP does Not Match"}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
@permission_classes((AllowAny,))
def reset_password(request):
    print(request.data)
    if User.objects.filter(username=request.data["user_name"]).exists():
        user_obj = User.objects.get(username=request.data["user_name"])
        user_obj.password = make_password(request.data["password"])
        user_obj.save()
        print("password is updated")
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


# For convert wav(audio) to base 64:
def convert_wav_to_base64(file_path):
    print("---------------------------voice path-----------", file_path)
    try:
        file_path = os.path.join(settings.MEDIA_ROOT + '/') + file_path
        with open(file_path, 'rb') as audio_file:
            encoded_audio = b64encode(audio_file.read())
        return encoded_audio
    except Exception as e:
        print("Except part run")
        return ''


@api_view(["GET"])
def serve_industry(request):
    # industry_objs = IndustryOfficial.objects.filter()
    industry_list = list(IndustryOffice.objects.filter(is_head_office=True).values_list('id', 'industry__id', 'state', 'district', 
                        'block',  'industry__name', 'industry__short_name', 'revenue_village',
                         'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude'))
    industry_columns = ['id', 'industry_industry_id', 'industry_state_name', 'industry_district_name','industry_block_name', 'industry_name', 'industry_short_name', 
     'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude']
    industry_df = pd.DataFrame(industry_list, columns=industry_columns)
    industry_df['industry_branch_count']=industry_df.apply(lambda x: find_branch_count(x["industry_industry_id"]), axis=1)
    # industry_df = industry_df.fillna('')
    data_dict = industry_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


# sub function for finding the count of branches for an industry
def find_branch_count(industry_id):
    if IndustryOffice.objects.filter(industry_id=industry_id).exists():
        return IndustryOffice.objects.filter(industry_id=industry_id).count()
    else:
        return 0


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            user_profile_obj = UserProfile.objects.get(user=user)
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            user_dict['user_type_id'] = user_profile_obj.user_type.id
            user_dict['user_id'] = user.id
            user_dict['user_type_name'] = user_profile_obj.user_type.name
            user_dict['first_name'] = user.first_name
            user_dict['username'] = user.username
            user_dict['language'] = user_profile_obj.language_preference.name
            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


def send_message_via_netfision(purpose, mobile, message):
    payload = {'ClientId': 'c9dc2b72-a38c-4e29-9834-17fe1ef6df3f', 'ApiKey' :'0fa9908c-1e67-4ccb-86fc-2363f7f75839', 'SenderID' : 'KULTIV', 'fl':'0', 'gwid':'2', 'sid':'KULTIV'} 

    headers = {}
    url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'
    payload['msg'] = message
    payload['msisdn'] = mobile
    res = requests.post(url, data=payload, headers=headers)
    print(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_otp_for_registration(request):
    data_dict = {}
    if User.objects.filter(username=request.data['phone']).exists():
        data_dict['status'] = True
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        otp = generate_otp()
        mobile_number = request.data['phone']
        purpose = 'Register'
        message = 'Your OTP is ' + str(otp)
        print(otp)
        send_message_via_netfision('register', request.data['phone'], message)
        OTP.objects.update_or_create(mobile=mobile_number, purpose=purpose, defaults={'otp': otp, 'expiry_time': datetime.datetime.now()})
        data_dict['status'] = False
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def otp_validation_for_farmer_registration(request):
    print(request.data)
    data_dict = {}
    if OTP.objects.filter(mobile=request.data['phone']).exists():
        print('Temp Reg. Avl!')
        otp_obj = OTP.objects.get(mobile=request.data['phone'], purpose='Register')
        if otp_obj.otp == str(request.data['otp']):
            print('Otp Matched')
            return Response(data='Correct otp', status=status.HTTP_200_OK)
        else:
            return Response(data='OTP does Not Match', status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        print('Temp Not available')
        return Response(data='Not Avl', status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_user_types(request):
    values = UserType.objects.filter().values('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    return Response(data=df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_language(request):
    data_dict = pd.DataFrame(list(Language.objects.filter().values())).to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_castes(request):
    data_dict = pd.DataFrame(list(CasteCv.objects.filter().values())).to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_state_district_block_rev_village(request):
    states = State.objects.all().order_by('id')
    districts = District.objects.all().order_by('name')
    blocks = Block.objects.all().order_by('name')
    revenue_village = RevenueVillage.objects.all().order_by('name')

    state_values = states.values_list('id', 'name')
    state_columns = ['id', 'name']
    state_df = pd.DataFrame(list(state_values), columns=state_columns)

    district_values = districts.values_list('id', 'name', 'state')
    district_columns = ['id', 'name', 'state_id']
    district_df = pd.DataFrame(list(district_values), columns=district_columns)

    temp_dict = {'states': [], 'districts': {}, 'block': {}, 'villages': {}, 'revenue_village': {}}

    temp_dict['states'] = state_df.to_dict('r')

    temp_dict['districts'] = district_df.groupby('state_id').apply(lambda x: x.set_index('state_id').to_dict('r')).to_dict()

    block_values = blocks.values_list('id', 'name', 'district', 'district__name')
    block_columns = ['id', 'name', 'district_id', 'district_name']
    block_df = pd.DataFrame(list(block_values), columns=block_columns)

    temp_dict['block'] = block_df.groupby('district_id').apply(lambda x: x.to_dict('r')).to_dict()
    revenue_village_values = revenue_village.values_list('id', 'name', 'block')
    revenue_village_columns = ['id', 'name', 'block_id']
    revenue_village_df = pd.DataFrame(list(revenue_village_values), columns=revenue_village_columns)

    temp_dict['revenue_village'] = revenue_village_df.groupby('block_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict = temp_dict
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_industry(request):
    print(request.data)
    data = {}
    if request.data['id'] == None:
        if Industry.objects.filter(name=request.data['name'], short_name=request.data['short_name']).exists():
            print('Error: Industry name already exists')
            data['message'] = 'Industry Name Already Exists'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            sid = transaction.savepoint()
            try:
                industry_obj = Industry(name=request.data['name'], short_name=request.data['short_name'])
                industry_obj.save()
                print('industry saved')
                
                industry_office_obj = IndustryOffice(
                    name='Head Office',
                    industry=industry_obj,
                    is_head_office = True,
                    state=request.data['state'],
                    district=request.data['district'],
                    block=request.data['block'],
                    revenue_village=request.data['revenue_village'],
                    village=request.data['village'],
                    street=request.data['street'],
                    taluk=request.data['taluk'],
                    pincode=request.data['pincode'],
                    latitude=request.data['latitude'],
                    longitude=request.data['longitude'],
                )
                industry_office_obj.save()          
                print('IndustryOffice saved')  
                data = {'message' : 'saved'}
                transaction.savepoint_commit(sid)
            except Exception as e:
                print('Error - {}'.format(e))
                transaction.savepoint_rollback(sid)
                data = {'message' : 'something went wrong!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        try:
            IndustryOffice.objects.filter(id=request.data['id']).update(
                name='Head Office',
                state=request.data['state'],
                district=request.data['district'],
                block=request.data['block'],
                revenue_village=request.data['revenue_village'],
                village=request.data['village'],
                street=request.data['street'],
                taluk=request.data['taluk'],
                pincode=request.data['pincode'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude'],
                # name='Head Office'0
            )

            industry_id = IndustryOffice.objects.get(id=request.data['id']).industry.id
            Industry.objects.filter(id=industry_id).update(
                name=request.data['name'], short_name=request.data['short_name']
            )

            print('data updated')
            data = {'message' : 'updated'}
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error - {}'.format(e))
            data = {'message' : 'something went wrong!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def serve_industry_branches(request):
    # industry_official_ids = list(IndustryOffice.objects.filter(industry_id=request.data['industry_id'], is_head_office=False).values_list('id',flat=True))
    industry_list = list(IndustryOffice.objects.filter(industry_id=request.data['industry_id']).values_list('id', 'name', 'short_name',
                            'state', 'district','block', 'industry__name', 'industry__short_name'
                            , 'industry__id',                        
                         'revenue_village','village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office'
                            ))
    industry_columns = ['id', 'name', 'short_name', 'industry_state_name', 'industry_district_name','industry_block_name', 'industry_name', 'industry_short_name','industry_id',
      'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office']
    industry_df = pd.DataFrame(industry_list, columns=industry_columns)
    data_dict = industry_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_industry_branch(request):
    if request.data['id'] == None:
        industry_office_obj = IndustryOffice(
        industry_id=request.data['industry_id'],
        name=request.data['name'],
        short_name=request.data['short_name'],
        is_head_office = False,
        state=request.data['state'],
        district=request.data['district'],
        block=request.data['block'],
        revenue_village=request.data['revenue_village'],
        village=request.data['village'],
        street=request.data['street'],
        taluk=request.data['taluk'],
        pincode=request.data['pincode'],
        latitude=request.data['latitude'],
        longitude=request.data['longitude'],
        )
        industry_office_obj.save()   
        data= {'message':'branch added'}
    else:
        IndustryOffice.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            short_name=request.data['short_name'],
            state=request.data['state'],
            district=request.data['district'],
            block=request.data['block'],
            revenue_village=request.data['revenue_village'],
            village=request.data['village'],
            street=request.data['street'],
            taluk=request.data['taluk'],
            pincode=request.data['pincode'],
            latitude=request.data['latitude'],
            longitude=request.data['longitude'],
        )
        data= {'message':'branch updated'}
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_industry_office_list(request):
    industry_office_list = list(IndustryOffice.objects.all().values_list('id', 'is_head_office', 'state', 'district', 'industry__name'))
    industry_office_columns = ['id', 'is_head_office', 'state_name', 'district_name','name']
    industry_df = pd.DataFrame(industry_office_list, columns=industry_office_columns)
    data = industry_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_industry_users(request):
    data = {}
    print(request.data)
    if request.data['user_id'] == None:
        if User.objects.filter(username=request.data['mobile']).exists():
            print('already exists')
            data['message'] = 'User already exists'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_obj = User(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                username=request.data['mobile'],
                password=make_password('1234')
            )
            user_obj.save()
            if request.data['email'] != None:
                print('inside')
                user_obj.email = request.data['email']
                user_obj.save()
            try:
                user_profile_obj = UserProfile(
                    user=user_obj,
                    user_type_id=4,
                    added_by=request.user,
                    mobile=request.data['mobile'],
                    alternate_mobile=request.data['alternate_mobile'],
                )

                if request.data['language_preference_id'] != None:
                    user_profile_obj.language_preference_id = request.data['language_preference_id']
                user_profile_obj.save()

                if request.data['is_contact_person'] == True:
                    if IndustryOfficial.objects.filter(industry_office_id=request.data['industry_office_id'], is_contact_person=True).exists():
                        official_obj = IndustryOfficial.objects.get(industry_office_id=request.data['industry_office_id'], is_contact_person=True)
                        official_obj.is_contact_person = False
                        official_obj.save()

                industry_obj = IndustryOfficial(
                    user_profile=user_profile_obj,
                    industry_office_id=request.data['industry_office_id'],
                    is_contact_person=request.data['is_contact_person']
                )
                industry_obj.save()
                data = {}
                data['message'] = 'industry user saved'
            except Exception as e:
                print(e)
                user_obj.delete()
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        User.objects.filter(id=request.data['user_id']).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            )
        
        UserProfile.objects.filter(user_id=request.data['user_id']).update(
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
        )
        
        if request.data['language_preference_id'] != '0':
            UserProfile.objects.filter(user_id=request.data['user_id']).update(
            language_preference_id=request.data['language_preference_id'])

        if request.data['is_contact_person'] == True:
            if IndustryOfficial.objects.filter(industry_office_id=request.data['industry_office_id'], is_contact_person=True).exists():
                official_obj = IndustryOfficial.objects.get(industry_office_id=request.data['industry_office_id'], is_contact_person=True)
                official_obj.is_contact_person = False
                official_obj.save()

        IndustryOfficial.objects.filter(id=request.data['industry_official_id']).update(
            industry_office_id=request.data['industry_office_id'],
            is_contact_person=request.data['is_contact_person']
        )
        data = {}
        data['message'] = 'updated'
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_industry_user_list(request):
    ind_official_obj = IndustryOfficial.objects.filter()
    industry_official_list = list(ind_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'industry_office_id', 'industry_office__industry__name',
            'industry_office__state', 'industry_office__is_head_office', 'industry_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    industry_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'industry_office_id', 'industry_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    industry_official_df = pd.DataFrame(industry_official_list, columns=industry_official_columns)
    industry_official_df = industry_official_df.fillna('0')
    data = industry_official_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)

    
def generate_farmer_code(district_id):
    """
        # TN_TNJ_0001
    """
    id_bank_obj = IdBank.objects.get(purpose='farmer_register', district_id=district_id)
    last_count = id_bank_obj.last_count + 1
    farmer_code = ''
    if id_bank_obj.prefix_code is not None:
        farmer_code += id_bank_obj.prefix_code
    if id_bank_obj.last_count is not None:
        farmer_code += '_' + str(last_count).zfill(4)
    if id_bank_obj.suffix_code is not None:
        farmer_code += '_' + id_bank_obj.suffix_code
    return farmer_code, last_count


@api_view(["POST"])
@permission_classes((AllowAny,))
@transaction.atomic
def register_farmer(request):
    if 'user_id' in request.data:
        added_by_id = request.data['user_id']
    else:
        added_by_id = 1
    print(request.user)
    print(request.data)
    logging.info(request.data)
    sid = transaction.savepoint()
    try:
        user = User.objects.create(
            first_name=request.data['first_name'],
            username=request.data['mobile'],
            password=make_password(request.data['password'])
        )
        if request.data['last_name'] is not None:
            user.last_name = request.data['last_name']
        print('user saved')
        user_profile = UserProfile.objects.create(
            user=user,
            user_type_id=1,
            mobile=request.data['mobile'],
            language_preference_id=1,
            added_by_id = added_by_id
        )
        status_code, data = post_data_to_micro_service(1, '/v1/main/save/farmer/', request.data)
        user_profile.ms_farmer_code = data['farmer_code']
        print("this is access code", data)
        user_profile.save()

        data['token'] = make_token(request.data['mobile'], request.data['password'])
        data['user_type_id'] = user_profile.user_type_id
        data['user_profile_id'] = user_profile.id
        data['message'] = "Farmer saved successfully"
        transaction.savepoint_commit(sid)
        return Response(data=data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        transaction.rollback(sid)
        logging.critical(f'Farmer save error = {e}')
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def make_token(username, password):
    print('making token')
    print(username, password)
    user = authenticate(username=username, password=password)
    print('user  = {}'.format(user))
    if user is not None:
        print('with in none')
        if Token.objects.filter(user_id=user.id).exists():
            print('user already logged')
            Token.objects.filter(user_id=user.id).delete()
        token = Token.objects.create(user=user)
        return str(token)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_land(request):
    data_dict = pd.DataFrame(list(CasteCv.objects.filter().values())).to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@transaction.atomic
def register_land(request):
    ms_farmer_code = request.user.userprofile.ms_farmer_code
    request.data['ms_farmer_code'] = ms_farmer_code
    try:
        status_code, data = post_data_to_micro_service(1, '/v1/main/register/land/', request.data)
        logging.info('status code = {}'.format(status_code))
        logging.info('data = {}'.format(data))
        return Response(data=data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def serve_lands(request):
    print(request.data)
    ms_farmer_code = request.user.userprofile.ms_farmer_code
    # ms_farmer_code = UserProfile.objects.get(id=request.data['user_profile_id']).ms_farmer_code
    req_data = {'ms_farmer_code': ms_farmer_code}
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/lands/', req_data)

    # farmer_id = request.data['farmer_id']
    # if farmer_id is None:
    #     farmer_id = request.user.userprofile.farmer.id
    #
    # values = Land.objects.filter(farmer_id=farmer_id).values_list('id', 'area_in_hectare', 'revenue_village__name', 'village')
    # columns = ['id', 'area_in_hectare', 'revenue_village', 'village']
    # df = pd.DataFrame(list(values), columns=columns)
    # data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def register_crop(request):
    print(request.data)
    # sowing_year = datetime.datetime.now().year - request.data['age_in_year']
    # sowing_year = datetime.datetime.strptime(f'{sowing_year}-01-01', '%Y-%m-%d').date()
    status_code, data = post_data_to_micro_service(1, '/v1/main/register/crop/', request.data)
    # print(sowing_year)
    # land = Crop.objects.create(
    #     land_id=request.data['land_id'],
    #     crop_cv_id=request.data['crop_cv_id'],
    #     area_in_hectare=request.data['area_in_hectare'],
    #     sowing_year=sowing_year,
    #     notes=request.data['notes']
    # )
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_child_pages(request):

    print(request.data)
    data_dict = {}
    input_lang = request.data['app_language']
    print(input_lang)
    # data_dict[input_lang] = {}
    node_id = Title.objects.get(title=input_lang).page.node.id
    print(node_id)
    question_id = list(TreeNode.objects.filter(parent_id=node_id).values_list('id', flat=True))
    print(question_id)
    qts_ans_df = pd.DataFrame(list(TreeNode.objects.filter(parent_id__in=question_id).values('parent_id', 'id')))
    print(qts_ans_df)
    value_df = qts_ans_df.groupby('parent_id').agg({'id':list}).reset_index()

    for index,value in value_df.iterrows():
        page_id = Page.objects.get(node_id=value.parent_id)
        question_type = Title.objects.get(page_id=page_id).title

        # if not question_type in data_dict[input_lang]:
        #     data_dict[input_lang][question_type] = []

        if question_type not in data_dict:
            data_dict[question_type] = []

        for question_id in value.id:
            page_id2 = Page.objects.get(node_id=question_id)
            question_obj = Title.objects.get(page_id=page_id2)
            question_dict = {
                'question': question_obj.title,
                'answer': question_obj.meta_description
            }
            data_dict[question_type].append(question_dict)
    print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_helpline_json_for_app(request):
    print(request.data)
    if request.data['app_language'] == 'English':
        try:
            with open('static/instance/static-json/Helpline_english.json', "r") as json_file:
                data = json.load(json_file)
                return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print('----Error--------')
            print(err)

    elif request.data['app_language'] == 'தமிழ்':
        try:
            with open('static/instance/static-json/Helpline_tamil.json', "r") as json_file:
                data = json.load(json_file)
                return Response(data=data, status=status.HTTP_200_OK)

        except Exception as err:
            print('----Error--------')
            print(err)

    return Response(data={}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def serve_crop_cvs(request):
    print('called')
    data = get_data_from_micro_service(1, '/v1/main/serve/crop/cvs/')
    print(data)
    # data_dict = pd.DataFrame(list(CropCv.objects.filter().values())).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


def serve_crop_cvs_for_notification():
    print('called')
    data = get_data_from_micro_service(1, '/v1/main/serve/crop/cvs/')
    print(data)
    # data_dict = pd.DataFrame(list(CropCv.objects.filter().values())).to_dict('r')
    return data


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_geo_tag_fence_for_selected_filter(request):
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/geo/tag/fence/for/selected/filter/', request.data)
    # data_dict = pd.DataFrame(list(CropCv.objects.filter().values())).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_question_types(request):
    values = QuestionType.objects.filter().values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_farmer_dynamic_questions_answers(request):
    """
    serve dynamic question id and its answer based on farmer
    :param request:
    :return:
    """
    try:
        print('GATHER ANSWERS FUNCTION')
        data = {'text': {}, 'dropdown': {},
                'radio': {}, 'number': {}, 'checkbox': {}}
        id = request.data['id']
        print(request.data)
        print(id)
        print(request.data['for'])

        if request.data['for'] == 'farmer':
            print('ANSWER GATHER FOR FARMER')
            text_answers = AnswerLogForTextInput.objects.filter(
                farmer_id=id, is_current=True)
            number_answers = AnswerLogForNumberInput.objects.filter(
                farmer_id=id, is_current=True)
            radio_answers = AnswerLogForRadio.objects.filter(
                farmer_id=id, is_current=True)
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                farmer_id=id, is_current=True)
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                farmer_id=id, is_current=True)

        if request.data['for'] == 'sowing':
            print('ANSWER GATHER FOR SOWING')
            text_answers = AnswerLogForTextInput.objects.filter(
                crop_id=id, is_current=True)
            number_answers = AnswerLogForNumberInput.objects.filter(
                crop_id=id, is_current=True)
            radio_answers = AnswerLogForRadio.objects.filter(
                crop_id=id, is_current=True)
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                crop_id=id, is_current=True)
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                crop_id=id, is_current=True)

        if request.data['for'] == 'farmer_field':
            print('ANSWER GATHER FOR FARMER FIELD')
            text_answers = AnswerLogForTextInput.objects.filter(
                farmer_field_id=id, is_current=True)
            number_answers = AnswerLogForNumberInput.objects.filter(
                farmer_field_id=id, is_current=True)
            radio_answers = AnswerLogForRadio.objects.filter(
                farmer_field_id=id, is_current=True)
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                farmer_field_id=id, is_current=True)
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                farmer_field_id=id, is_current=True)

        if request.data['for'] == 'water_resource':
            print('ANSWER GATHER FOR WATER RESOURCE')
            text_answers = AnswerLogForTextInput.objects.filter(
                water_resource_id=id, is_current=True)
            number_answers = AnswerLogForNumberInput.objects.filter(
                water_resource_id=id, is_current=True)
            radio_answers = AnswerLogForRadio.objects.filter(
                water_resource_id=id, is_current=True)
            dropdown_answers = AnswerLogForDropDown.objects.filter(
                water_resource_id=id, is_current=True)
            checkbox_answers = AnswerLogForCheckbox.objects.filter(
                water_resource_id=id, is_current=True)

        if request.data['for'] == 'scheme':
            print('ANSWER GATHER FOR WATER RESOURCE')
            text_answers = AnswerLogForTextInput.objects.filter(farmer_scheme_map_id=id, is_current=True)
            number_answers = AnswerLogForNumberInput.objects.filter(farmer_scheme_map_id=id, is_current=True)
            radio_answers = AnswerLogForRadio.objects.filter(farmer_scheme_map_id=id, is_current=True)
            dropdown_answers = AnswerLogForDropDown.objects.filter(farmer_scheme_map_id=id, is_current=True)
            checkbox_answers = AnswerLogForCheckbox.objects.filter(farmer_scheme_map_id=id, is_current=True)

        # text answers
        print(text_answers)
        text_answer_values = text_answers.values_list('question', 'answer')
        text_answer_columns = ['id', 'answer']
        text_df = pd.DataFrame(list(text_answer_values),
                               columns=text_answer_columns)
        data['text'] = pd.Series(
            text_df.answer.values, index=text_df.id).to_dict()

        # DROPDOWN
        dropdown_answer_values = dropdown_answers.values_list(
            'question', 'answer')
        dropdown_answer_columns = ['id', 'answer']
        dropdown_df = pd.DataFrame(
            list(dropdown_answer_values), columns=dropdown_answer_columns)
        data['dropdown'] = pd.Series(
            dropdown_df.answer.values, index=dropdown_df.id).to_dict()

        # RADIO
        radio_answer_values = radio_answers.values_list('question', 'answer')
        radio_answer_columns = ['id', 'answer']
        radio_df = pd.DataFrame(list(radio_answer_values),
                                columns=radio_answer_columns)
        data['radio'] = pd.Series(
            radio_df.answer.values, index=radio_df.id).to_dict()

        # NUMBER
        number_answer_values = number_answers.values_list('question', 'answer')
        number_answer_columns = ['id', 'answer']
        number_df = pd.DataFrame(
            list(number_answer_values), columns=number_answer_columns)
        data['number'] = pd.Series(
            number_df.answer.values, index=number_df.id).to_dict()

        # CHECKBOX
        checkbox_answer_values = checkbox_answers.values_list(
            'question', 'answer')
        checkbox_answer_columns = ['id', 'answer']
        checkbox_df = pd.DataFrame(
            list(checkbox_answer_values), columns=checkbox_answer_columns)
        checkbox_df = checkbox_df.groupby('id')['answer'].apply(list)
        print(checkbox_df)
        # data['checkbox'] = checkbox_df.groupby('id').apply(lambda x: x.set_index('id').to_dict('r')).to_list()
        data['checkbox'] = checkbox_df.to_dict()
        return Response(data=data, status=status.HTTP_200_OK)

    except Exception as e:
        print('ERROR - {}'.format(e))
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


def save_dynamic_question_text_answer(question_answers, answer_save_for, added_by_id, farmer_id, farmer_field_id,
                                      crop_id, water_resource_id, farmer_scheme_map_id):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == 'farmer':

        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                        is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                        is_current=True)

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
                        added_by_id=added_by_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'land':
        print('farmer filed')
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                        farmer_field_id=farmer_field_id, is_current=True).exists():
                print('question not exists')
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                    farmer_field_id=farmer_field_id
                )
                answer_log_obj.save()
                print('answer logged')
                continue
            else:
                print('not yet answered this question')
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(farmer_id=farmer_id,
                                                                        farmer_field_id=farmer_field_id,
                                                                        question_id=question_id, is_current=True)

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
                        farmer_field_id=farmer_field_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'crop':

        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                        crop_id=crop_id, is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                    crop_id=crop_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(farmer_id=farmer_id, crop_id=crop_id,
                                                                        question_id=question_id, is_current=True)

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
                        crop_id=crop_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'water_resource':

        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))

            if not AnswerLogForTextInput.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                        water_resource_id=water_resource_id, is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForTextInput(
                    question_id=question_id,
                    answer=answer,
                    farmer_id=farmer_id,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForTextInput.objects.get(farmer_id=farmer_id,
                                                                        water_resource_id=water_resource_id,
                                                                        question_id=question_id, is_current=True)

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
                        water_resource_id=water_resource_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    return True


def save_dynamic_question_number_answer(question_answers, answer_save_for, added_by_id, farmer_id, farmer_field_id,
                                        crop_id, water_resource_id, farmer_scheme_map_id):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == 'farmer':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                          is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                          is_current=True)

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
                        added_by_id=added_by_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'land':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(question_id=question_id, farmer_field_id=farmer_field_id,
                                                          farmer_id=farmer_id,
                                                          is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                    farmer_field_id=farmer_field_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(farmer_id=farmer_id,
                                                                          farmer_field_id=farmer_field_id,
                                                                          question_id=question_id,
                                                                          is_current=True)

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
                        farmer_field_id=farmer_field_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'crop':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(question_id=question_id, crop_id=crop_id,
                                                          farmer_id=farmer_id,
                                                          is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                    crop_id=crop_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(farmer_id=farmer_id, crop_id=crop_id,
                                                                          question_id=question_id,
                                                                          is_current=True)

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
                        crop_id=crop_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    if answer_save_for == 'water':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForNumberInput.objects.filter(question_id=question_id, water_resource_id=water_resource_id,
                                                          farmer_id=farmer_id,
                                                          is_current=True).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForNumberInput(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer=answer,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForNumberInput.objects.get(farmer_id=farmer_id,
                                                                          water_resource_id=water_resource_id,
                                                                          question_id=question_id,
                                                                          is_current=True)

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
                        water_resource_id=water_resource_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer = answer
                    previous_answer_obj.save()

    return True


def save_dynamic_question_radio_answer(question_answers, answer_save_for, added_by_id, farmer_id, farmer_field_id,
                                       crop_id, water_resource_id, farmer_scheme_map_id):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == 'land':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(question_id=question_id, farmer_field_id=farmer_field_id,
                                                    farmer_id=farmer_id).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                    farmer_field_id=farmer_field_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(farmer_id=farmer_id,
                                                                    farmer_field_id=farmer_field_id,
                                                                    question_id=question_id)

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
                        farmer_field_id=farmer_field_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    if answer_save_for == 'crop':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(question_id=question_id, crop_id=crop_id,
                                                    farmer_id=farmer_id).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                    crop_id=crop_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(farmer_id=farmer_id, crop_id=crop_id,
                                                                    question_id=question_id, is_current=True)

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
                        crop_id=crop_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    if answer_save_for == 'water':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(question_id=question_id, water_resource_id=water_resource_id,
                                                    farmer_id=farmer_id).exists():
                # if this question not answered for this farmer log answer
                answer_log_obj = AnswerLogForRadio(
                    farmer_id=farmer_id,
                    question_id=question_id,
                    answer_id=answer,
                    added_by_id=added_by_id,
                    water_resource_id=water_resource_id
                )
                answer_log_obj.save()
                continue
            else:
                # if already answer logged for this farmer and question
                question = Question.objects.get(id=question_id)
                previous_answer_obj = AnswerLogForRadio.objects.get(farmer_id=farmer_id,
                                                                    water_resource_id=water_resource_id,
                                                                    question_id=question_id, is_current=True)

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
                        water_resource_id=water_resource_id
                    )
                    answer_log_obj.save()
                else:
                    # this question config not to make new entry; update the answer
                    previous_answer_obj.answer_id = answer
                    previous_answer_obj.save()

    if answer_save_for == 'farmer':
        for question_id, answer in question_answers.items():
            print('{} - {}'.format(question_id, answer))
            if not AnswerLogForRadio.objects.filter(question_id=question_id, farmer_id=farmer_id).exists():
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
                previous_answer_obj = AnswerLogForRadio.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                    is_current=True)

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


def save_dynamic_question_checkbox_answer(question_answers, answer_save_for, added_by_id, farmer_id, farmer_field_id,
                                          crop_id, water_resource_id, farmer_scheme_map_id):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    if answer_save_for == 'land':
        for question_id, answer_ids in question_answers.items():
            print('{} - {}'.format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(farmer_id=farmer_id, farmer_field_id=farmer_field_id,
                                                           question_id=question_id, answer_id=answer_id).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                        farmer_field_id=farmer_field_id
                    )
                    answer_log_obj.save()

    if answer_save_for == 'crop':
        for question_id, answer_ids in question_answers.items():
            print('{} - {}'.format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(farmer_id=farmer_id, crop_id=crop_id,
                                                           question_id=question_id, answer_id=answer_id).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                        crop_id=crop_id
                    )
                    answer_log_obj.save()

    if answer_save_for == 'water':
        for question_id, answer_ids in question_answers.items():
            print('{} - {}'.format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(farmer_id=farmer_id, water_resource_id=water_resource_id,
                                                           question_id=question_id, answer_id=answer_id).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id
                    )
                    answer_log_obj.save()

    if answer_save_for == 'farmer':
        for question_id, answer_ids in question_answers.items():
            print('{} - {}'.format(question_id, answer_ids))
            for answer_id in answer_ids:
                if not AnswerLogForCheckbox.objects.filter(farmer_id=farmer_id, question_id=question_id,
                                                           answer_id=answer_id).exists():
                    answer_log_obj = AnswerLogForCheckbox(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer_id,
                        added_by_id=added_by_id,
                    )
                    answer_log_obj.save()
    return True


def save_dynamic_question_dropdown_answer(question_answers, answer_save_for, added_by_id, farmer_id, farmer_field_id,
                                          crop_id, water_resource_id, farmer_scheme_map_id):
    """
    save text question type answer in 'AnswerLogForTextInput' model
    :param question_answers:
    :return:
    """
    for question_id, answer in question_answers.items():
        print('{} - {}'.format(question_id, answer))
        try:
            if answer_save_for == 'land':
                if not AnswerLogForDropDown.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                           farmer_field_id=farmer_field_id).exists():
                    print('new entry')
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        farmer_field_id=farmer_field_id
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print('already answer logged')
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                           farmer_field_id=farmer_field_id)

                    if question.questionconfig.create_new_answer_row_on_update:
                        print('create new entry')
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
                            farmer_field_id=farmer_field_id
                        )
                        answer_log_obj.save()
                    else:
                        print('replace answer')
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

            if answer_save_for == 'crop':
                if not AnswerLogForDropDown.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                           crop_id=crop_id).exists():
                    print('new entry')
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        crop_id=crop_id
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print('already answer logged')
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                           crop_id=crop_id)

                    if question.questionconfig.create_new_answer_row_on_update:
                        print('create new entry')
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
                            crop_id=crop_id
                        )
                        answer_log_obj.save()
                    else:
                        print('replace answer')
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

            if answer_save_for == 'water':
                if not AnswerLogForDropDown.objects.filter(question_id=question_id, farmer_id=farmer_id,
                                                           water_resource_id=water_resource_id).exists():
                    print('new entry')
                    # if this question not answered for this farmer log answer
                    answer_log_obj = AnswerLogForDropDown(
                        farmer_id=farmer_id,
                        question_id=question_id,
                        answer_id=answer,
                        added_by_id=added_by_id,
                        water_resource_id=water_resource_id
                    )
                    answer_log_obj.save()
                    continue
                else:
                    # if already answer logged for this farmer and question
                    print('already answer logged')
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(farmer_id=farmer_id, question_id=question_id,
                                                                           water_resource_id=water_resource_id)

                    if question.questionconfig.create_new_answer_row_on_update:
                        print('create new entry')
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
                            water_resource_id=water_resource_id
                        )
                        answer_log_obj.save()
                    else:
                        print('replace answer')
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

            if answer_save_for == 'farmer':
                if not AnswerLogForDropDown.objects.filter(question_id=question_id, farmer_id=farmer_id).exists():
                    print('new entry')
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
                    print('already answer logged')
                    question = Question.objects.get(id=question_id)
                    previous_answer_obj = AnswerLogForDropDown.objects.get(
                        farmer_id=farmer_id, question_id=question_id)

                    if question.questionconfig.create_new_answer_row_on_update:
                        print('create new entry')
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
                        print('replace answer')
                        # this question config not to make new entry; update the answer
                        previous_answer_obj.answer_id = answer
                        previous_answer_obj.save()

        except Exception as error:
            print('dropdown ANSWER SAVE ERROR {}'.format(error))
    return True


@api_view(['POST'])
def save_dynamic_questions_answers(request):
    logging.info(request.data)
    # farmer_id = request.data['id']
    serve_url = '/v1/main/save/dynamic/questions/answers/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def serve_questions(request):
    serve_url = '/v1/main/serve/dynaminc/questions/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    return Response(response_data, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def serve_farmer_dynamic_questions_answers(request):
    """
    serve dynamic question id and its answer based on farmer
    :param request:
    :return:
    """
    serve_url = '/v1/main/serve/dynamic/questions/answers/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    return Response(response_data, status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'POST'])
def serve_farmer_lands(request):
    print('serve farmer lands')
    # serve land depend upon usertypes
    print(request.user)
    user_type_name = request.user.userprofile.user_type.name
    print(user_type_name)
    farmer_id = None
    if user_type_name == 'Farmer':
        farmer_id = request.user.userprofile.farmer.id
    else:
        farmer_id = request.data['farmer_id']
    lands = Land.objects.filter(farmer_id=farmer_id)
    values = lands.values_list('id', 'area_in_acre', 'revenue_village__name', 'village', 'latitude', 'longitude')
    columns = ['id', 'area_in_acre', 'revenue_village', 'village', 'latitude', 'longitude']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def serve_farmer_crops(request):
    print('serve farmer crops')
    print(request.data)
    land_id = request.data['land_id']
    crops = Crop.objects.filter(land_id=land_id)
    values = crops.values_list('id', 'area_in_acre', 'sowing_year', 'is_active', 'land__revenue_village__name', 'land__village', 'land__latitude', 'land__longitude')
    columns = ['id', 'area_in_acre', 'sowing_year', 'is_active', 'revenue_village', 'village', 'latitude', 'longitude']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny, ))
# def username_validation(request):
#     is_available = User.objects.filter(username=request.data['username'], is_active=True).exists()
#     # create otp
#     otp = generate_otp()
#     print(otp)
#     expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
#     OTP.objects.create(purpose='forgot_password', mobile=request.data['username'], otp=otp, expiry_time=expiry_time)
#     return Response(data={'is_available': is_available, 'username': request.data['username']}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# def otp_validation(request):
#     if OTP.objects.filter(purpose='forgot_password', mobile=request.data['user_id'],
#                                            expiry_time__gte=datetime.datetime.now()).exists():
#         password_reset_obj = OTP.objects.get(purpose='forgot_password', mobile=request.data['user_id'],
#                                                                  expiry_time__gte=datetime.datetime.now())
#         print(password_reset_obj.otp)
#         if request.data['otp'] == password_reset_obj.otp:
#             return Response(data='Correct otp', status=status.HTTP_200_OK)
#         else:
#             data = {'message': 'OTP does Not Match'}
#             return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
#     else:
#         data = {'message': 'Please Try After Some Time'}
#         return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_language_translation(request):
    languages = list(Language.objects.filter().values_list("name", flat=True))
    values = LanguageTransformTerm.objects.all().values_list(
        "language__name", "language_term__name", "name"
    )
    columns = ["language", "english", "name"]
    l_df = pd.DataFrame(list(values), columns=columns)
    print(l_df)
    language_dict = {}
    for language in languages:
        # for language in l_df['language'].unique():
        if language not in language_dict:
            language_dict[language] = {}
        filtered = l_df[l_df["language"] == language]
        language_dict[language] = dict(zip(filtered["english"], filtered["name"]))
    print("**************************")
    print(language_dict)
    print("**************************")
    return Response(data=language_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_expensive_for_crop(request):
    # crop_cv_id = request.data['crop_id']
    # crop_id = Crop.objects.get(crop_cv_id = crop_cv_id).id
    crop_id = request.data['crop_id']
    expasive_list = list(ExpenseCV.objects.filter(crop_id=crop_id).values('id', 'name'))
    return Response(data=expasive_list, status=status.HTTP_200_OK)


@api_view(["POST"])
def register_harvest(request):
    print(request.data)
    Harvest.objects.create(
        crop_id=request.data['crop_id'],
        date=request.data['date'],
        value=request.data['value'],
        unit_id=request.data['unit_id']
    )
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def register_expansive(request):
    print(request.data)
    data = request.data
    print(data)
    expense_obj = ExpenseLog(expense_cv_id=data['expense_id'], crop_id=data['crop_id'], date=data['date'], cost=data['cost'])
    expense_obj.save()
    return Response(data={'hi': 'test'}, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_harvest_log(request):
    """
    serve harvest history by crop order by date
    """
    values = Harvest.objects.filter(crop_id=request.data['crop_id']).order_by('-date').values_list('date', 'value', 'unit__display_term')
    columns = ['date', 'value', 'unit']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def serve_crop_expence_details(request):
    # crop_id = request.data['crop_id']
    expense_log_list = list(ExpenseLog.objects.filter(crop_id=2).order_by('date').values_list('id', 'expense_cv', 'expense_cv__name', 'cost', 'date', 'crop', 'crop__crop_cv__name', 'crop__area_in_hectare', 'crop__sowing_year__year'))
    expense_log_column = ['expense_id', 'expense_cv_id', 'expense_cv_name', 'cost', 'date', 'crop_id', 'crop_name', 'area', 'showing_year']
    expense_df = pd.DataFrame(expense_log_list, columns=expense_log_column)
    year = datetime.datetime.now().year
    expense_df['curent_year'] = year
    expense_df['age'] = expense_df['curent_year'] - expense_df['showing_year']
    data_dict = expense_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_harvest_units(request):
    """
    serve harvest history by crop order by date
    """
    print(request.data)
    crop_cv = Crop.objects.get(id=request.data['crop_id']).crop_cv
    print(crop_cv)
    values = HarvestUnit.objects.filter(instance_crop=crop_cv).values_list('id', 'term')
    print(values)
    columns = ['id', 'term']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes((AllowAny, ))
# def serve_water_sources(request):
#     data = WaterResource.objects.all().values("id", "name")
#     return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes((AllowAny, ))
# def serve_water_types(request):
#     data = WaterType.objects.all().values("id", "name")
#     return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_ownership(request):
    data = get_data_from_micro_service(1, '/v1/main/serve/ownership/type/')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_farmer_area_and_ownership(request):
    print(request.data)
    user_profile = UserProfile.objects.get(id=request.data['user_profile_id'])
    ms_farmer_code = user_profile.ms_farmer_code
    request.data['ms_farmer_code'] = ms_farmer_code
    status_code, data = post_data_to_micro_service(1, '/v1/main/save/farmer/area/and/ownership/', request.data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register_minimal_land_crop_register(request):
    """
    register land and crop with minimal information
    """
    status_code, data = post_data_to_micro_service(1, '/v1/main/register/minimal/land/crop/register/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_water_sources(request):
    data = get_data_from_micro_service(1, '/v1/main/serve/water/sources/')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_water_types(request):
    data = get_data_from_micro_service(1, '/v1/main/serve/water/types/')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
@transaction.atomic
def register_water_resource(request):
    status_code, data = post_data_to_micro_service(1, '/v1/main/register/water/resource/', request.data)
    return Response(data=data, status=status.HTTP_200_OK)


def get_data_from_micro_service(micro_service_id: int, serve_url: str):
    micro_service_auth_obj = MicroServiceAuthentication.objects.get(micro_service_id=micro_service_id)
    base_url = micro_service_auth_obj.base_url
    access_token = micro_service_auth_obj.access_token
    url = f'{base_url}{serve_url}'
    headers = {"Authorization": f"Bearer {access_token}"}
    responce_data = requests.get(url, headers=headers)
    print(responce_data, 'hellow')
    if responce_data.status_code == 401:
        get_refresh_and_access_token(micro_service_id)
        responce_data = get_data_from_micro_service(micro_service_id, serve_url)
        json_output = responce_data
        return json_output
    else:
        json_output = responce_data.json()
        return json_output


def post_data_to_micro_service(micro_service_id: int, serve_url: str, post_data: json):
    print("inside post")
    print(post_data)
    micro_service_auth_obj = MicroServiceAuthentication.objects.get(micro_service_id=micro_service_id)
    base_url = micro_service_auth_obj.base_url
    access_token = micro_service_auth_obj.access_token
    print("acccess token : ", access_token)
    url = f'{base_url}{serve_url}'
    print(url)
    logging.info(f'url = {url}')
    headers = {"Authorization": f"Bearer {access_token}"}
    request = requests.post(url, headers=headers, json=post_data)
    print(request)
    if request.status_code == 401:
        get_refresh_and_access_token(micro_service_id)
        responce_data = post_data_to_micro_service(micro_service_id, serve_url, post_data)
        json_output = responce_data[1]
        status_code = responce_data[0]
        return status_code, json_output
    else:
        return request.status_code, request.json()


def get_refresh_and_access_token(micro_service_id: int):
    base_url = MicroServiceAuthentication.objects.get(micro_service_id=micro_service_id).base_url
    if micro_service_id == 3:
        username = 'pincode'
        password = 'pincode'
        url = '/main/api/token/'
    else :
        username = 'jamun'
        password = 'jamun'
        url = '/v1/main/api/token/'
    r = requests.post(f'{base_url}{url}', data={'username': username, 'password': password})
    print(r)
    MicroServiceAuthentication.objects.filter(micro_service_id=micro_service_id).update(refresh_token=r.json()['refresh'], access_token=r.json()['access'])


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_gender(request):
    serve_url = '/v1/main/serve/gender/'
    response_data = get_data_from_micro_service(1, serve_url)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_faq_child_pages(request):
    serve_url = '/v1/main/serve/faq/child/pages/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(2, serve_url, post_data)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_raq_child_pages(request):
    serve_url = '/v1/main/serve/raq/details/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(2, serve_url, post_data)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_featured_video_link(request):
    serve_url = '/v1/main/serve/featured/video/link/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(2, serve_url, post_data)
    video_id = response_data['video_id']
    video_details = requests.get('https://www.googleapis.com/youtube/v3/videos?id=' + video_id + '&key=' + youtube_api_key +'&part=snippet').json()
    video_item_details_in_json = video_details['items'][0]['snippet']
    final_dict = {
        'title': video_item_details_in_json['title'],
        'iframe_link': 'https://www.youtube.com/embed/' + video_id,

    }
    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_advisory_child_page(request):
    serve_url = '/v1/main/serve/advisory/child/pages/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(2, serve_url, post_data)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_languages(request):
    print(request.user.username)
    print(request.data)
    values = Language.objects.filter().values('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    return Response(data=df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_url_for_pdf_and_video(request):
    serve_url = '/v1/main/serve/url/for/pdf/and/video/'
    post_data = request.data
    status_code, response_data = post_data_to_micro_service(2, serve_url, post_data)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register_or_update_language_preference(request):
    print(request.data)
    print('Register languate preference')
    print(request.data['user_profile_id'])
    user_profile_id = None
    if 'user_profile_id' in request.data:
        if request.data['user_profile_id'] is None:
            user_profile_id = request.user.userprofile
        else:
            user_profile_id = request.data['user_profile_id']
    else:
        user_profile_id = request.user.userprofile

    print('User Profile id = {}'.format(user_profile_id))
    user_profile = UserProfile.objects.get(id=user_profile_id)
    user_profile.language_preference_id = request.data['language_id']
    user_profile.save()
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_single_water_resource(request):
    print(request.data)
    request.data['ms_farmer_code'] = request.user.userprofile.ms_farmer_code
    status_code, data = post_data_to_micro_service(1, '/v1/main/register/single/water/resource/', request.data)
    print(status_code)
    print(data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_industry_details_for_stakeholder_directory(request):
    
    if IndustryOffice.objects.filter().exists():
        industry_office_obj = IndustryOffice.objects.filter(is_head_office=True)
        industry_incharge_obj = IndustryOfficial.objects.all()

        industry_value_list = list(industry_office_obj.values_list('id','industry__name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image'))                                                                                                                     
        industry_value_column = ['industry_office_id', 'industry_name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image']
        industry_df = pd.DataFrame(industry_value_list, columns=industry_value_column)
        industry_df = industry_df.fillna('')

        incharge_value_list = list(industry_incharge_obj.values_list('id','user_profile_id', 'industry_office_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__mobile', 'is_contact_person', 'user_profile__user__email'))
        incharge_value_column = ['industry_incharge_id','user_profile_id', 'industry_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'email']
        incharge_df = pd.DataFrame(incharge_value_list, columns=incharge_value_column)
        incharge_df = incharge_df[incharge_df['contact_person']==True]
        incharge_df

        final_df = pd.merge(incharge_df, industry_df, left_on='industry_office_id', right_on='industry_office_id', how='left')
        final_df = final_df.fillna('')
        final_df

        for index, row in final_df.iterrows():
            image_path = settings.MEDIA_ROOT + '/' + str(row.image)
            final_df.at[index, 'full_address'] = str(row.street) + ', ' + str(row.village) + ', ' + str(row.taluk) + ', ' + str(row.block) + ', ' + str(row.district) + ', ' + str(row.state) 
            try:
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    final_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
            except Exception as e:
                print('ERROR - {}'.format(e))
                final_df.at[index, 'image'] = 0
        data_dict = final_df.fillna('').to_dict('r')
    else:
        data_dict = []
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_qpm_nursery_details_for_stakeholder_directory(request):
    
    nursery_office_obj = NurseryOffice.objects.filter()
    nursery_incharge_obj = NurseryIncharge.objects.all()

    nursery_value_list = list(nursery_office_obj.values_list('id','nursery__name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'nurseryofficecropmap__clone__name', 'nurseryofficecropmap__clone__crop_cv__name', 'image'))                                                                                                                     
    nursery_value_column = ['nursery_office_id', 'nursery_name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'clone_name', 'crop_name', 'image']
    nursery_df = pd.DataFrame(nursery_value_list, columns=nursery_value_column)
    nursery_df = nursery_df.fillna('')

    nursery_df['crop_clone'] =  nursery_df['crop_name'] + ' - ' + nursery_df['clone_name']
    nursery_crop_df = nursery_df.groupby('nursery_office_id').agg({'crop_clone': 'unique'})
    nursery_df = nursery_df.drop(columns=['crop_name', 'clone_name'])

    nursery_df = nursery_df.groupby(['nursery_office_id', 'nursery_name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office','image']).agg({'crop_clone': 'unique'}).reset_index()
    data_dict = nursery_df.to_dict('r')

    incharge_value_list = list(nursery_incharge_obj.values_list('id','user_profile_id', 'nursery_office_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__mobile', 'is_contact_person', 'user_profile__user__email'))
    incharge_value_column = ['nursery_incharge_id','user_profile_id', 'nursery_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'email']
    incharge_df = pd.DataFrame(incharge_value_list, columns=incharge_value_column)
    incharge_df = incharge_df[incharge_df['contact_person']==True]

    final_df = pd.merge(nursery_df, incharge_df, left_on='nursery_office_id', right_on='nursery_office_id', how='left')
    final_df = final_df.fillna('')

    for index, row in final_df.iterrows():
        image_path = settings.MEDIA_ROOT + '/' + str(row.image)
        final_df.at[index, 'full_address'] = str(row.street) + ', ' + str(row.village) + ', ' + str(row.taluk) + ', ' + str(row.block) + ', ' + str(row.district) + ', ' + str(row.state) 
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                final_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        except Exception as e:
            print('ERROR - {}'.format(e))
            final_df.at[index, 'image'] = 0
    print(final_df.shape)
    data_dict = final_df.fillna('').to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_ifgtb_scientist_details_for_stakeholder_directory(request):
    # institute_office_obj = InstituteOffice.objects.all()
    # scientist_obj = Scientist.objects.all()

    # institute_office_list = list(institute_office_obj.values_list('id','institute__name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image'))                                                                                                              
    # institute_office_column = ['institute_office_id', 'institute_name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image']
    # institute_office_df = pd.DataFrame(institute_office_list, columns=institute_office_column)
    

    # scientist_value_list = list(scientist_obj.values_list('institute_office_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__mobile', 'is_contact_person', 'expertise__name', 'user_profile__user__email', 'designation'))
    # scientist_value_column = ['institute_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'expertise', 'email', 'designation']
    # scientist_df = pd.DataFrame(scientist_value_list, columns=scientist_value_column)
    # scientist_df = scientist_df.groupby(['institute_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'email']).agg({'expertise': 'unique', 'designation':'first'}).reset_index()
    # scientist_df = scientist_df[scientist_df['contact_person']==True]

    # final_df = pd.merge(institute_office_df, scientist_df, left_on='institute_office_id', right_on='institute_office_id', how='left').fillna('')
    # for index, row in final_df.iterrows():
    #     image_path = settings.MEDIA_ROOT + '/' + str(row.image)
    #     final_df.at[index, 'full_address'] = str(row.street) + ', ' + str(row.village) + ', ' + str(row.taluk) + ', ' + str(row.block) + ', ' + str(row.district)
    #     try:
    #         with open(image_path, 'rb') as image_file:
    #             encoded_image = b64encode(image_file.read())
    #             final_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    #     except Exception as e:
    #         print('ERROR - {}'.format(e))
    #         final_df.at[index, 'image'] = 0
    scientist_obj = Scientist.objects.all()
    scientist_value_list = list(scientist_obj.values_list('id', 'user_profile__user_id', 'institute_office_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__mobile', 'is_contact_person', 'expertise__name', 'user_profile__user__email', 'designation', 'institute_office__name', 'institute_office__short_name', 
                                                     'institute_office__institute__name', 'institute_office__state', 'institute_office__district', 'institute_office__block', 'institute_office__revenue_village', 'institute_office__image'))
    scientist_value_column = ['scientist_id', 'user_id', 'institute_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'expertise', 'email', 'designation',  'institute_office_name', 'institute_office_short_name', 
                                                        'institute_name', 'institute_office_state', 'institute_office_district', 'institute_office_block', 'institute_office_revenue_village', 'image']
    scientist_df = pd.DataFrame(scientist_value_list, columns=scientist_value_column)
    scientist_df
    for index, row in scientist_df.iterrows():
        image_path = settings.MEDIA_ROOT + '/' + str(row.image)
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                scientist_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        except Exception as e:
            print('ERROR - {}'.format(e))
            scientist_df.at[index, 'image'] = 0
    # scientist_df
    data_dict = scientist_df.fillna('').to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_farmer_details_for_stakeholder_directory_from_farmer_ms(request):
    serve_url = '/v1/main/serve/farmer/details/for/stakeholder/directory/'
    response_data = get_data_from_micro_service(1, serve_url)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_farmers_basic_info_data(request):
    serve_url = '/v1/main/serve/farmers/basic/info/data/'
    response_data = get_data_from_micro_service(1, serve_url)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_farmer_basic_info(request):
    # print(request.data)
    print("-----------------------------------", UserProfile.objects.get(user_id=request.user.id).ms_farmer_code)
    serve_url = '/v1/main/serve/farmer/basic/info/'
    post_data = {}
    # post_data = request.data
    if request.data['checksum_farmer_code'] != 0:
        print("check sum not 0")
        post_data['checksum_farmer_code'] = request.data['checksum_farmer_code']
    else:
        print("checksum 0")
        post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
    print(request.data)
    # post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    print('status code = {}'.format(status_code))
    print('response = {}'.format(response_data))
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_land_detail_by_id(request):
    print(request.data)
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/land/detail/by/id/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def serve_crop_detail_by_id(request):
    print(request.data)
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/crop/detail/by/id/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def serve_water_resource_detail_by_id(request):
    print(request.data)
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/water/resource/detail/by/id/', request.data)
    print(data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def serve_farmer_detail_by_id(request):
    ms_farmer_code = request.user.userprofile.ms_farmer_code
    req_data = {'ms_farmer_code': ms_farmer_code}
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/farmer/detail/by/id/', req_data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def update_farmer(request):
    print(request.data)
    ms_farmer_code = request.user.userprofile.ms_farmer_code
    request.data['ms_farmer_code'] = ms_farmer_code
    status_code, data = post_data_to_micro_service(1, '/v1/main/update/farmer/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def update_farmer_via_portal(request):
    print(request.data)
    status_code, data = post_data_to_micro_service(1, '/v1/main/update/farmer/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_geo_location(request):
    print(request.data)
    status_code, data = post_data_to_micro_service(1, '/v1/main/update/geo/location/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def serve_geo_fence_data(request):
    status_code, data = post_data_to_micro_service(1, '/v1/main/serve/geo/fence/data/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_geo_fence_gps_data(request):
    status_code, data = post_data_to_micro_service(1, '/v1/main/upload/geo/fence/gps/data/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_or_create_farmer_profile(request):
    status_code, data = post_data_to_micro_service(1, '/v1/main/update/or/create/farmer/profile/', request.data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_user_type_tile_list(request):
    print('---')
    print(request.user.id)
    print(request.data)
    if request.data['user_type_id'] == 'guest':
        user_type_id = 1
        print('guest')
    else:
        print('actual user')
        user_type_id = UserProfile.objects.get(user_id=request.user.id).user_type_id
    if request.data['language'] == 'English':
        language_id= 2
    else:
        language_id= 1
    user_type_tile_map_obj = UserTypeTilesMap.objects.filter(user_type_id=user_type_id, is_active=True, tile__is_active=True, language_preference=language_id).order_by('display_ordinal')
    user_type_tile_map_list = list(user_type_tile_map_obj.values_list('id', 'tile__display_name', 'tile__route_url', 'tile__icon_path', 'css_class_name', 'is_icon_available', 'column_size', 'title_class_name', 'icon_class_name', 'tile__tab_name', 'display_image'))
    user_type_tile_map_column = ['id', 'display_name', 'route_url', 'icon_path', 'class_name', 'is_icon_available', 'column_size', 'title_class_name', 'icon_class_name', 'tab_name', 'display_image']
    user_type_tile_map_df = pd.DataFrame(user_type_tile_map_list, columns=user_type_tile_map_column)
    for index, row in user_type_tile_map_df.iterrows():
        image_path = str(settings.MEDIA_ROOT) + '/' + str(row['display_image'])
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                user_type_tile_map_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        except Exception as e:
            print('ERROR - {}'.format(e))
            user_type_tile_map_df.at[index, 'image'] = 0

    return Response(data=user_type_tile_map_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_youtube_video_by_play_list_id(request):
    list_ld = 'PLiK29z7UemitrSulyo52pWsGzh22SXtdu'
    video_under_play_list_response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?key=' + youtube_api_key + '&playlistId=' + list_ld +'&part=snippet,id&maxResults=20')
    video_under_play_list_response = video_under_play_list_response.json()['items']
    master_list = []
    for video in video_under_play_list_response:
        video_dict = {
            'video_id': video['snippet']['resourceId']['videoId'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'iframe_link': 'https://www.youtube.com/embed/' + video['snippet']['resourceId']['videoId'],
            'thumbnail_list': video['snippet']['thumbnails']['medium']['url'],
            'video_link': 'https://www.youtube.com/watch?v=' + video['snippet']['resourceId']['videoId']
        }
        master_list.append(video_dict)
    return Response(data=master_list, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_google_album(request):
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    data_dict = service.albums().list(pageSize=50).execute()
    print(data_dict)
    data_list = []
    # these codes are for removing all the unwanted albums
    for data in data_dict['albums']:
        if data['title'].startswith('Book'):
            print(data['title'])
        else:
            data_list.append(data)
    return Response(data=data_list, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_photos_inside_album(request):
    print('------------')
    print(request.data)
    print('------------')
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    photos_inside_album = service.mediaItems().search(body=request.data).execute()
    return Response(data=photos_inside_album, status=status.HTTP_200_OK)


@api_view(['POST'])
def post_data_to_farmer_server(request):
    url = '/v1/' + request.data['url']
    post_data = request.data
    status_code, data = post_data_to_micro_service(1, url, post_data)
    if status_code == 200:
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def serve_farmer_basic_details(request):
    print('---------------')
    print(request.data)
    print(request.user)
    serve_url = '/v1/main/serve/farmer/basic/details/'
    post_data = request.data
    post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
    # print(request.data)
    # post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    print('status code = {}'.format(status_code))
    # print('response = {}'.format(response_data))
    user_profile_id = UserProfile.objects.get(user_id=request.user.id).id
    response_data['farmer_data']['about_me'] = UserProfile.objects.get(id=user_profile_id).about_me
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_farmer_basic_details(request):
    if request.data['field'] == 'about':
        user_profile_id = UserProfile.objects.get(user_id=request.user.id).id
        UserProfile.objects.filter(id=user_profile_id).update(
            about_me=request.data['about']
        )
        return Response(data={}, status=status.HTTP_200_OK)
    else:
        serve_url = '/v1/main/update/farmer/basic/details/'
        post_data = request.data
        post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code

        print(request.data)
        # post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
        status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
        print('status code = {}'.format(status_code))
        print('response = {}'.format(response_data))
        return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_qpm_basic_details(request):
    data_dict = {}
    nursery_incharge_obj = NurseryIncharge.objects.get(user_profile__user_id=request.user.id)
    nursery_obj = nursery_incharge_obj.nursery_office.nursery
    nursery_office_obj = nursery_incharge_obj.nursery_office
    data_dict['nursery_id'] = nursery_incharge_obj.id
    data_dict['nursery_name'] = nursery_obj.name
    data_dict['taluk_name'] = nursery_office_obj.taluk
    # data_dict['district_id'] = nursery_office_obj.district
    data_dict['district_name'] = nursery_office_obj.district
    if NurseryIncharge.objects.filter(nursery_office=nursery_office_obj, is_contact_person=True).exists():
        contact_person = NurseryIncharge.objects.get(nursery_office=nursery_office_obj, is_contact_person=True).user_profile
        data_dict['mobile'] = contact_person.mobile
        data_dict['email'] = contact_person.user.email
        data_dict['first_name'] = contact_person.user.first_name
        data_dict['last_name'] = contact_person.user.last_name
        data_dict['about_me'] = contact_person.about_me
    else:
        data_dict['mobile'] = '' 
        data_dict['email'] = ''
        data_dict['first_name'] = ''
        data_dict['last_name'] = ''
        data_dict['about_me'] = ''
    # data_dict['state_id'] = nursery_office_obj.state.id
    data_dict['state_name'] = nursery_office_obj.state
    # data_dict['block_id'] = nursery_office_obj.block.id
    data_dict['address'] = nursery_office_obj.street + ', ' + nursery_office_obj.village + ', ' + nursery_office_obj.taluk  + ', ' + nursery_office_obj.district + ', ' + nursery_office_obj.state
    data_dict['block_name'] = nursery_office_obj.block
    # data_dict['revenue_village'] = nursery_office_obj.revenue_village.id
    data_dict['revenue_village'] = nursery_office_obj.revenue_village
    data_dict['village'] = nursery_office_obj.village
    data_dict['street'] = nursery_office_obj.street
    data_dict['pincode'] = nursery_office_obj.pincode
    data_dict['latitude'] = nursery_office_obj.latitude
    data_dict['longitude'] = nursery_office_obj.longitude
    

    nursery_office_clone_map_obj = NurseryOfficeCropMap.objects.filter(nursery_office_id=nursery_office_obj.id)

    nursery_office_clone_map_list = list(nursery_office_clone_map_obj.values_list('id', 'clone_id', 'clone__name', 'current_stock'))
    nursery_office_clone_map_column = ['id', 'clone_id', 'clone_name', 'current_stock']
    nursery_office_clone_map_df = pd.DataFrame(nursery_office_clone_map_list, columns=nursery_office_clone_map_column)
    data_dict['clone_data'] = nursery_office_clone_map_df.to_dict('r')
    # getting cost details
    print(nursery_office_obj.id)
    if NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map__nursery_office__id=nursery_office_obj.id, is_active=True).exists():
        nursery_office_clone_cost_map_obj = NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map__nursery_office__id=nursery_office_obj.id, is_active=True)
        nursery_office_clone_cost_map_list = list(nursery_office_clone_cost_map_obj.values_list('id', 'nursery_office_crop_map_id', 'cost', 'from_date'))
        nursery_office_clone_cost_map_column = ['id', 'nursery_office_crop_map_id', 'cost', 'from_date']
        nursery_office_clone_cost_map_df = pd.DataFrame(nursery_office_clone_cost_map_list, columns=nursery_office_clone_cost_map_column)
        data_dict['clone_cost_data'] =  nursery_office_clone_cost_map_df.groupby('nursery_office_crop_map_id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    else:
        data_dict['clone_cost_data'] = None
    try:
        photo_obj = UserProfile.objects.get(user_id=request.user.id)
        image_path = settings.MEDIA_ROOT + '/' + str(photo_obj.photo)
        # image_path = str(photo_obj.photo)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def update_qpm_basic_details(request):
    print(request.data)
    nursery_incharge_obj = NurseryIncharge.objects.get(user_profile__user_id=request.user.id)
    nursery_obj = nursery_incharge_obj.nursery_office.nursery
    nursery_office_obj = nursery_incharge_obj.nursery_office
    contact_person = NurseryIncharge.objects.get(nursery_office=nursery_office_obj, is_contact_person=True).user_profile
    if request.data['field'] == 'name':
        nursery_obj.name = request.data['nursery_name']
        nursery_obj.save()
    if request.data['field'] == 'contact_person':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.first_name = request.data['first_name']
        user_obj.last_name = request.data['last_name']
        user_obj.save()
    if request.data['field'] == 'address':
        nursery_office_obj.pincode = request.data['pincode']
        nursery_office_obj.taluk = request.data['taluk']
        nursery_office_obj.village = request.data['village']
        nursery_office_obj.street = request.data['street']
        nursery_office_obj.latitude = request.data['latitude']
        nursery_office_obj.longitude = request.data['longitude']
        nursery_office_obj.save()
    if request.data['field'] == 'email':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.email = request.data['email']
        user_obj.save()

        contact_person.about_me = request.data['about_me']
        contact_person.save()
    return Response(status=status.HTTP_200_OK)
    

@api_view(['POST'])
def update_forest_basic_details(request):
    print(request.data)
    forest_incharge_obj = ForestOfficial.objects.get(user_profile__user_id=request.user.id)
    forest_obj = forest_incharge_obj.forest_office.forest
    forest_office_obj = forest_incharge_obj.forest_office
    contact_person = ForestOfficial.objects.get(nursery_office=forest_office_obj, is_contact_person=True).user_profile
    if request.data['field'] == 'name':
        forest_obj.name = request.data['nursery_name']
        forest_obj.save()
    if request.data['field'] == 'contact_person':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.first_name = request.data['first_name']
        user_obj.last_name = request.data['last_name']
        user_obj.save()
    if request.data['field'] == 'address':
        forest_office_obj.pincode = request.data['pincode']
        forest_office_obj.taluk = request.data['taluk']
        forest_office_obj.village = request.data['village']
        forest_office_obj.street = request.data['street']
        forest_office_obj.save()
    if request.data['field'] == 'email':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.email = request.data['email']
        user_obj.save()
    if request.data['field'] == 'about_me':
        contact_person.about_me = request.data['about_me']
        contact_person.save()
    return Response(status=status.HTTP_200_OK)



@api_view(['GET'])
def serve_industry_basic_details(request):
    data_dict = {}
    print(request.user.id)
    industry_incharge_obj = IndustryOfficial.objects.get(user_profile__user_id=request.user.id)
    industry_obj = industry_incharge_obj.industry_office.industry
    industry_office_obj = industry_incharge_obj.industry_office
    data_dict['industry_name'] = industry_obj.name
    data_dict['industry_id'] = industry_incharge_obj.id
    data_dict['taluk_name'] = industry_office_obj.taluk
    data_dict['district_name'] = industry_office_obj.district
    contact_person = IndustryOfficial.objects.get(industry_office=industry_office_obj, is_contact_person=True).user_profile
    data_dict['mobile'] = contact_person.mobile
    data_dict['email'] = contact_person.user.email
    data_dict['first_name'] = contact_person.user.first_name
    data_dict['last_name'] = contact_person.user.last_name
    data_dict['state_name'] = industry_office_obj.state
    data_dict['address'] = industry_office_obj.street + ', ' + industry_office_obj.village + ', ' + industry_office_obj.taluk  + ', ' + industry_office_obj.district + ', ' + industry_office_obj.state
    data_dict['block_name'] = industry_office_obj.block
    data_dict['revenue_village'] = industry_office_obj.revenue_village
    data_dict['village'] = industry_office_obj.village
    data_dict['street'] = industry_office_obj.street
    data_dict['pincode'] = industry_office_obj.pincode
    data_dict['latitude'] = industry_office_obj.latitude
    data_dict['longitude'] = industry_office_obj.longitude
    data_dict['about_me'] = contact_person.about_me

    try:
        img_obj = UserProfile.objects.get(user_id=request.user.id)
        image_path = settings.MEDIA_ROOT + '/' + str(img_obj.photo)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0

    return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['POST'])
def update_industry_basic_details(request):
    print(request.data)
    industry_incharge_obj = IndustryOfficial.objects.get(user_profile__user_id=request.user.id)
    industry_obj = industry_incharge_obj.industry_office.industry
    industry_office_obj = industry_incharge_obj.industry_office
    contact_person = IndustryOfficial.objects.get(industry_office=industry_office_obj, is_contact_person=True).user_profile

    if request.data['field'] == 'name':
        industry_obj.name = request.data['industry_name']
        industry_obj.save()
    if request.data['field'] == 'contact_person':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.first_name = request.data['first_name']
        user_obj.last_name = request.data['last_name']
        user_obj.save()
    if request.data['field'] == 'address':
        industry_office_obj.pincode = request.data['pincode']
        industry_office_obj.taluk = request.data['taluk']
        industry_office_obj.village = request.data['village']
        industry_office_obj.street = request.data['street']
        industry_office_obj.latitude = request.data['latitude']
        industry_office_obj.longitude = request.data['longitude']
        industry_office_obj.save()
    if request.data['field'] == 'email':
        user_id = contact_person.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.email = request.data['email']
        user_obj.save()
    if request.data['field'] == 'about':
        UserProfile.objects.filter(id=contact_person.id).update(
           about_me = request.data['about'] 
        )
    return Response(status=status.HTTP_200_OK)




@api_view(['GET'])
def serve_scientist_basic_details(request):
    print(request.user.id)
    data_dict = {}
    scientist_obj = Scientist.objects.get(user_profile__user=request.user)
    institute_obj = scientist_obj.institute_office.institute
    institute_office_obj = scientist_obj.institute_office
    data_dict['scientist_id'] = scientist_obj.id
    data_dict['scientist_first_name'] = scientist_obj.user_profile.user.first_name
    data_dict['scientist_last_name'] = scientist_obj.user_profile.user.last_name
    data_dict['institute_name'] = institute_obj.name
    data_dict['mobile'] = scientist_obj.user_profile.mobile
    data_dict['email'] =  scientist_obj.user_profile.user.email
    data_dict['about_me'] =  scientist_obj.user_profile.about_me
    data_dict['position'] =  scientist_obj.designation

    try:
        img_obj = UserProfile.objects.get(user_id=request.user.id)
        image_path = settings.MEDIA_ROOT + '/' + str(img_obj.photo)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_scientist_basic_details(request):
    scientist_obj = Scientist.objects.get(user_profile__user_id=request.user.id)
    institute_obj = scientist_obj.institute_office.institute
    institute_office_obj = scientist_obj.institute_office
    if request.data['field'] == 'name':
        usr_profile_obj = scientist_obj.user_profile.user
        usr_profile_obj.first_name = request.data['first_name']
        usr_profile_obj.last_name = request.data['last_name']
        usr_profile_obj.save()
    elif request.data['field'] == 'email':
        usr_profile_obj = scientist_obj.user_profile.user
        usr_profile_obj.email = request.data['email']
        usr_profile_obj.save()
    elif request.data['field'] == 'about':
        usr_profile_obj = scientist_obj.user_profile
        usr_profile_obj.about_me = request.data['about']
        usr_profile_obj.save()
    elif request.data['field'] == 'position':
        scientist_obj.designation = request.data['position']
        scientist_obj.save()
    return Response(status=status.HTTP_200_OK)
    

@api_view(['GET'])
def serve_crop_clone(request):
    # nursery_office = NurseryIncharge.objects.get(user_profile__user_id=request.user.id).nursery_office
    # nursery_office_clone_map_obj = NurseryOfficeCropMap.objects.filter(nursery_office_id=nursery_office.id)
    # clone_ids = list(nursery_office_clone_map_obj.values_list('clone_id', flat=True))
    # crop_clone_obj = Clone.objects.filter().exclude(id__in=clone_ids)
    crop_clone_obj = Clone.objects.filter()
    crop_clone_list = list(crop_clone_obj.values_list('id', 'name', 'crop_cv', 'crop_cv__name'))
    crop_clone_column = ['id', 'name', 'crop_cv_id', 'crop_name']
    crop_clone_df = pd.DataFrame(crop_clone_list, columns=crop_clone_column)
    data = crop_clone_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_crop_clone(request):
    print(request.data)
    nursery_office = NurseryIncharge.objects.get(user_profile__user_id=request.user.id).nursery_office
    if NurseryOfficeCropMap.objects.filter(nursery_office_id=nursery_office.id, clone_id=request.data['clone_form']['clone_id']).exists():
        nursery_office_clone_map = NurseryOfficeCropMap.objects.get(nursery_office_id=nursery_office.id, clone_id=request.data['clone_form']['clone_id'])
        nursery_office_clone_map.current_stock=request.data['clone_form']['stock']
        nursery_office_clone_map.save()
    else:
        nursery_office_clone_map = NurseryOfficeCropMap(nursery_office_id=nursery_office.id,
                                                        clone_id=request.data['clone_form']['clone_id'],
                                                        current_stock=request.data['clone_form']['stock'],
                                                        )
        nursery_office_clone_map.save()
    # create_nursery_office_crop_price_log(nursery_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    if not NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map=nursery_office_clone_map, is_active=True).exists():
        create_nursery_office_crop_price_log(nursery_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    else:
        old_cost_map_obj = NurseryOfficeCropPriceLog.objects.get(nursery_office_crop_map=nursery_office_clone_map, is_active=True)
        old_cost_map_obj.is_active = False
        old_cost_map_obj.effective_date = datetime.datetime.now()
        old_cost_map_obj.modified_by = request.user
        old_cost_map_obj.save()
        create_nursery_office_crop_price_log(nursery_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_crop_clone(request):
    NurseryOfficeCropMap.objects.filter(id=request.data['clone_map_id']).delete()
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_crop_clone(request):
    nursery_office_clone_map = NurseryOfficeCropMap.objects.get(id=request.data['clone_map_id'])
    nursery_office_clone_map.current_stock = request.data['clone_form']['stock']
    nursery_office_clone_map.save()

    # update the cost of the clone
    if not NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map=nursery_office_clone_map, is_active=True).exists():
        create_nursery_office_crop_price_log(nursery_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    else:
        old_cost_map_obj = NurseryOfficeCropPriceLog.objects.get(nursery_office_crop_map=nursery_office_clone_map, is_active=True)
        old_cost_map_obj.is_active = False
        old_cost_map_obj.effective_date = datetime.datetime.now()
        old_cost_map_obj.modified_by = request.user
        old_cost_map_obj.save()
        create_nursery_office_crop_price_log(nursery_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    return Response(data={}, status=status.HTTP_200_OK)


def create_nursery_office_crop_price_log(nursery_office_clone_map_id, cost, user):
    nursery_obj = NurseryOfficeCropPriceLog.objects.create(
        nursery_office_crop_map_id=nursery_office_clone_map_id,
        cost=cost,
        is_active=True,
        from_date=datetime.datetime.now(),
        created_by=user,
        modified_by=user
    )
    print('new nursery cost log created')
    return nursery_obj



def create_complete_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')

    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)

    return ContentFile(decoded_image, str(file_name) + '.jpeg')



@api_view(['POST'])
def update_profile_photo(request):
    if request.data['type'] == "scientist":
        obj = Scientist.objects.get(id=request.data['id']).user_profile
        complete_image = create_complete_image(request.data['picture'])
        obj.photo = complete_image
        obj.save()
    elif request.data['type'] == "qpm":
        obj = UserProfile.objects.get(user_id=request.user.id)
        print(request.user.id)
        print(obj.user_type.name)
        complete_image = create_complete_image(request.data['picture'])
        obj.photo = complete_image
        obj.save()
    elif request.data['type'] == "industry":
        obj = IndustryOfficial.objects.get(id=request.data['id']).user_profile
        complete_image = create_complete_image(request.data['picture'])
        obj.photo = complete_image
        obj.save()
    elif request.data['type'] == "forest":
        obj = ForestOfficial.objects.get(id=request.data['id']).user_profile
        complete_image = create_complete_image(request.data['picture'])
        obj.photo = complete_image
        obj.save()
    return Response(status=status.HTTP_200_OK)
    



@api_view(['POST'])
def serve_farmer_details_for_selected_id(request):
    print(request.data)
    serve_url = '/v1/main/serve/farmer/basic/details/for/selected/farmer/'
    post_data = request.data
    post_data['checksum_farmer_code'] = request.user.userprofile.ms_farmer_code
    print(request.data)
    # post_data['checksum_farmer_code'] = UserProfile.objects.get(user_id=request.user.id).ms_farmer_code
    status_code, response_data = post_data_to_micro_service(1, serve_url, post_data)
    print('status code = {}'.format(status_code))
    print('response = {}'.format(response_data))
    response_data['farmer_data']['about_me'] = UserProfile.objects.get(ms_farmer_code=response_data['farmer_data']['checksum_farmer_code']).about_me
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_qpm_details_for_selected_id(request):
    print(request.data)
    data_dict = {}
    nursery_incharge_obj = NurseryIncharge.objects.get(id=request.data['qpm_id'])
    nursery_obj = nursery_incharge_obj.nursery_office.nursery
    nursery_office_obj = nursery_incharge_obj.nursery_office
    data_dict['nursery_id'] = nursery_incharge_obj.id
    data_dict['nursery_name'] = nursery_obj.name
    data_dict['taluk_name'] = nursery_office_obj.taluk
    data_dict['district_name'] = nursery_office_obj.district
    contact_person = NurseryIncharge.objects.get(nursery_office=nursery_office_obj, is_contact_person=True).user_profile
    data_dict['mobile'] = contact_person.mobile
    data_dict['email'] = contact_person.user.email
    data_dict['first_name'] = contact_person.user.first_name
    data_dict['last_name'] = contact_person.user.last_name
    data_dict['state_name'] = nursery_office_obj.state
    data_dict['address'] = nursery_office_obj.street + ', ' + nursery_office_obj.village + ', ' + nursery_office_obj.taluk  + ', ' + nursery_office_obj.district + ', ' + nursery_office_obj.state
    data_dict['block_name'] = nursery_office_obj.block
    data_dict['revenue_village'] = nursery_office_obj.revenue_village
    data_dict['village'] = nursery_office_obj.village
    data_dict['street'] = nursery_office_obj.street
    data_dict['pincode'] = nursery_office_obj.pincode
    data_dict['latitude'] = nursery_office_obj.latitude
    data_dict['longitude'] = nursery_office_obj.longitude
    data_dict['about_me'] = contact_person.about_me

    nursery_office_clone_map_obj = NurseryOfficeCropMap.objects.filter(nursery_office_id=nursery_office_obj.id)
    nursery_office_clone_map_list = list(nursery_office_clone_map_obj.values_list('id', 'clone_id', 'clone__name', 'current_stock'))
    nursery_office_clone_map_column = ['id', 'clone_id', 'clone_name', 'current_stock']
    nursery_office_clone_map_df = pd.DataFrame(nursery_office_clone_map_list, columns=nursery_office_clone_map_column)
    data_dict['clone_data'] = nursery_office_clone_map_df.to_dict('r')
    
    if NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map__nursery_office__id=nursery_office_obj.id, is_active=True).exists():
        nursery_office_clone_cost_map_obj = NurseryOfficeCropPriceLog.objects.filter(nursery_office_crop_map__nursery_office__id=nursery_office_obj.id, is_active=True)
        nursery_office_clone_cost_map_list = list(nursery_office_clone_cost_map_obj.values_list('id', 'nursery_office_crop_map_id', 'cost', 'from_date'))
        nursery_office_clone_cost_map_column = ['id', 'nursery_office_crop_map_id', 'cost', 'from_date']
        nursery_office_clone_cost_map_df = pd.DataFrame(nursery_office_clone_cost_map_list, columns=nursery_office_clone_cost_map_column)
        data_dict['clone_cost_data'] =  nursery_office_clone_cost_map_df.groupby('nursery_office_crop_map_id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    else:
        data_dict['clone_cost_data'] = None

    try:
        image_path = settings.MEDIA_ROOT + '/' + str(nursery_office_obj.image)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0

    else:
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_industry_basic_details_for_given_id(request):
    data_dict = {}
    print(request.data)
    print(request.data['industry_id'])
    industry_incharge_obj = IndustryOfficial.objects.get(industry_office_id=request.data['industry_id'], is_contact_person=True)
    industry_obj = industry_incharge_obj.industry_office.industry
    industry_office_obj = industry_incharge_obj.industry_office
    data_dict['industry_name'] = industry_obj.name
    data_dict['taluk_name'] = industry_office_obj.taluk
    data_dict['district_name'] = industry_office_obj.district
    if IndustryOfficial.objects.filter(industry_office=industry_office_obj, is_contact_person=True).exists():
        contact_person = IndustryOfficial.objects.get(industry_office=industry_office_obj, is_contact_person=True).user_profile
        data_dict['mobile'] = contact_person.mobile
        data_dict['email'] = contact_person.user.email
        data_dict['first_name'] = contact_person.user.first_name
        data_dict['last_name'] = contact_person.user.last_name
    else:
        data_dict['mobile'] = ''
        data_dict['email'] = ''
        data_dict['first_name'] =''
        data_dict['last_name'] = ''
    data_dict['state_name'] = industry_office_obj.state
    data_dict['block'] = industry_office_obj.block
    data_dict['address'] = str(industry_office_obj.street) + ', ' + str(industry_office_obj.village) + ', ' + str(industry_office_obj.taluk)  + ', ' + str(industry_office_obj.district) + ', ' + str(industry_office_obj.state)
    data_dict['block_name'] = industry_office_obj.block
    data_dict['revenue_village'] = industry_office_obj.revenue_village
    data_dict['village'] = industry_office_obj.village
    data_dict['street'] = industry_office_obj.street
    data_dict['pincode'] = industry_office_obj.pincode
    data_dict['latitude'] = industry_office_obj.latitude
    data_dict['longitude'] = industry_office_obj.longitude

    if IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map__industry_office_id=industry_office_obj.id, is_active=True).exists():
        Industry_office_clone_cost_map_obj = IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map__industry_office_id=industry_office_obj.id, is_active=True)
        industry_office_clone_cost_map_list = list(Industry_office_clone_cost_map_obj.values_list('id', 'industry_office_crop_map__crop_cv__name', 'cost', 'from_date'))
        industry_office_clone_cost_map_column = ['id', 'nursery_office_crop_map_name', 'cost', 'from_date']
        industry_office_clone_cost_map_df = pd.DataFrame(industry_office_clone_cost_map_list, columns=industry_office_clone_cost_map_column)
        industry_office_clone_cost_map_df = industry_office_clone_cost_map_df.fillna(0)
        data_dict['clone_cost_data'] =  industry_office_clone_cost_map_df.to_dict('r')  
    else:
        data_dict['clone_cost_data'] = []   

    try:
        image_path = settings.MEDIA_ROOT + '/' + str(industry_office_obj.image)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0

    else:
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_ifgtb_basic_details_for_given_id(request):
    print(request.data)
    data_dict = {}
    scientist_obj = Scientist.objects.get(id=request.data['scientist_id'])
    institute_obj = scientist_obj.institute_office.institute
    institute_office_obj = scientist_obj.institute_office
    data_dict['scientist_id'] = scientist_obj.id
    data_dict['scientist_first_name'] = scientist_obj.user_profile.user.first_name
    data_dict['scientist_last_name'] = scientist_obj.user_profile.user.last_name
    data_dict['institute_name'] = institute_obj.name
    data_dict['mobile'] = scientist_obj.user_profile.mobile
    data_dict['email'] =  scientist_obj.user_profile.user.email
    data_dict['about_me'] =  scientist_obj.user_profile.about_me
    data_dict['position'] =  scientist_obj.designation
    data_dict['expertise_list'] = list(Scientist.objects.filter(id=request.data['scientist_id']).values_list('expertise__name', flat=True))

    try:
        image_path = settings.MEDIA_ROOT + '/' + str(institute_office_obj.image)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0

    else:
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_farmer_dashboard_data(request):
    serve_url = '/v1/main/serve/farmers/for/dashboard/'
    print(serve_url)
    data_dict = get_data_from_micro_service(1, serve_url)

    ins_df = pd.DataFrame(list(InstituteOffice.objects.all().values('id', 'district')))
    ins_df = ins_df.groupby('district').agg({'id': 'count'}).reset_index().rename(columns={'id':'count'})

    ind_df = pd.DataFrame(list(IndustryOffice.objects.all().values('id', 'district')))
    ind_df = ind_df.groupby('district').agg({'id': 'count'}).reset_index().rename(columns={'id':'count'})

    nus_df = pd.DataFrame(list(NurseryOffice.objects.all().values('id', 'district')))
    nus_df = nus_df.groupby('district').agg({'id': 'count'}).reset_index().rename(columns={'id':'count'})

    forest_df = pd.DataFrame(list(ForestOffice.objects.all().values('id', 'district')))
    forest_df = forest_df.groupby('district').agg({'id': 'count'}).reset_index().rename(columns={'id':'count'})


    data_dict['Research Institutes'] = {
                'total_count': ins_df['count'].sum(),
                'district_wise': ins_df.to_dict('r')    
    }

    data_dict['Wood Based Industries'] = {
                'total_count': ind_df['count'].sum(),
                'district_wise': ind_df.to_dict('r')    
    }

    data_dict['Nurseries'] = {
                'total_count': nus_df['count'].sum(),
                'district_wise': nus_df.to_dict('r')    
    }

    data_dict['TNFD Circles'] = {
                'total_count': forest_df['count'].sum(),
                'district_wise': forest_df.to_dict('r')    
    }
    
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_institute(request):
    print(request.data)
    data = {}
    if request.data['id'] == None:
        if Institute.objects.filter(name=request.data['name'], short_name=request.data['short_name']).exists():
            print('Error: Institute name already exists')
            data['message'] = 'Institute Name Already Exists'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            sid = transaction.savepoint()
            try:
                institute_obj = Institute(name=request.data['name'], short_name=request.data['short_name'])
                institute_obj.save()
                print('Institute saved')
                
                institute_office_obj = InstituteOffice(
                    institute=institute_obj,
                    is_head_office = True,
                    name='Head Office',
                    state=request.data['state'],
                    district=request.data['district'],
                    block=request.data['block'],
                    revenue_village=request.data['revenue_village'],
                    village=request.data['village'],
                    street=request.data['street'],
                    taluk=request.data['taluk'],
                    pincode=request.data['pincode'],
                    latitude=request.data['latitude'],
                    longitude=request.data['longitude'],
                )
                institute_office_obj.save()          
                print('instituteOffice saved')  
                data = {'message' : 'saved'}
                transaction.savepoint_commit(sid)
            except Exception as e:
                print('Error - {}'.format(e))
                transaction.savepoint_rollback(sid)
                data = {'message' : 'something went wrong!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        try:
            InstituteOffice.objects.filter(id=request.data['id']).update(
                name='Head Office',
                state=request.data['state'],
                district=request.data['district'],
                block=request.data['block'],
                revenue_village=request.data['revenue_village'],
                village=request.data['village'],
                street=request.data['street'],
                taluk=request.data['taluk'],
                pincode=request.data['pincode'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude'],
            )

            institute_id = InstituteOffice.objects.get(id=request.data['id']).institute.id
            Institute.objects.filter(id=institute_id).update(
                name=request.data['name'], short_name=request.data['short_name']
            )

            print('data updated')
            data = {'message' : 'updated'}
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error - {}'.format(e))
            data = {'message' : 'something went wrong!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def serve_institute(request):
    # institute_objs = instituteOfficial.objects.filter()
    institute_list = list(InstituteOffice.objects.filter(is_head_office=True).values_list('id', 'institute__id', 'state', 'district', 
                        'block',  'institute__name', 'institute__short_name', 
                        'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude'))
    institute_columns = ['id', 'institute_institute_id', 'institute_state_name', 'institute_district_name','institute_block_name', 'institute_name', 'institute_short_name', 
    'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude']
    institute_df = pd.DataFrame(institute_list, columns=institute_columns)
    institute_df['institute_branch_count']=institute_df.apply(lambda x: find_branch_institute_count(x["institute_institute_id"]), axis=1)
    # institute_df = institute_df.fillna('')
    data_dict = institute_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_institute_branch(request):
    if request.data['id'] == None:
        institute_office_obj = InstituteOffice(
        institute_id=request.data['institute_id'],
        name=request.data['name'],
        short_name=request.data['short_name'],
        is_head_office = False,
        state=request.data['state'],
        district=request.data['district'],
        block=request.data['block'],
        revenue_village=request.data['revenue_village'],
        village=request.data['village'],
        street=request.data['street'],
        taluk=request.data['taluk'],
        pincode=request.data['pincode'],
        latitude=request.data['latitude'],
        longitude=request.data['longitude'],
        )
        institute_office_obj.save()   
        data= {'message':'branch added'}
    else:
        InstituteOffice.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            short_name=request.data['short_name'],
            state=request.data['state'],
            district=request.data['district'],
            block=request.data['block'],
            revenue_village=request.data['revenue_village'],
            village=request.data['village'],
            street=request.data['street'],
            taluk=request.data['taluk'],
            pincode=request.data['pincode'],
            latitude=request.data['latitude'],
            longitude=request.data['longitude'],
        )
        data= {'message':'branch updated'}
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_institute_branches(request):
    # institute_official_ids = list(instituteOffice.objects.filter(institute_id=request.data['institute_id'], is_head_office=False).values_list('id',flat=True))
    institute_list = list(InstituteOffice.objects.filter(institute_id=request.data['institute_id']).values_list('id', 'name', 'short_name',
                            'state', 'district','block', 'institute__name', 'institute__short_name'
                            , 'institute__id','revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office'))
    institute_columns = ['id', 'name', 'short_name', 'institute_state_name', 'institute_district_name','institute_block_name', 'institute_name', 'institute_short_name','institute_id',
      'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office']
    institute_df = pd.DataFrame(institute_list, columns=institute_columns)
    data_dict = institute_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_institute_users(request):
    print(request.data) 
    if request.data['user_id'] == None:
        if User.objects.filter(username=request.data['mobile']).exists():
            print('already exists')

            data = {}
            data['message'] = 'User already exists'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_obj = User(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                username=request.data['mobile'],
                password=make_password('1234')
            )
            user_obj.save()
            if request.data['email'] != None:
                user_obj.email = request.data['email']
                user_obj.save()
            print('------------------------user-saves--------------')
            try:
                user_profile_obj = UserProfile(
                    user=user_obj,
                    added_by=request.user,
                    user_type_id=5,
                    mobile=request.data['mobile'],
                    alternate_mobile=request.data['alternate_mobile'],
                )

                if request.data['language_preference_id'] != None:
                    user_profile_obj.language_preference_id = request.data['language_preference_id']
                user_profile_obj.save()

                if request.data['is_contact_person'] == True:
                    if Scientist.objects.filter(institute_office_id=request.data['institute_office_id'], is_contact_person=True).exists():
                        official_obj = Scientist.objects.get(institute_office_id=request.data['institute_office_id'], is_contact_person=True)
                        official_obj.is_contact_person = False
                        official_obj.save()

                institute_obj = Scientist(
                    user_profile=user_profile_obj,
                    institute_office_id=request.data['institute_office_id'],
                    designation=request.data['designation'],
                    is_contact_person = request.data['is_contact_person']
                )
                print('-------------------saves------------------')
                institute_obj.save()
                expertise_obj = list(Expertise.objects.filter(id__in=request.data['expertise_list']))
                institute_obj.expertise.add(*expertise_obj)
                print('saves')
                data = {}
                data['message'] = 'institute user saved'
            except Exception as e:
                print(e)
                user_obj.delete()
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        User.objects.filter(id=request.data['user_id']).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            )
        
        UserProfile.objects.filter(user_id=request.data['user_id']).update(
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
        )
        
        if request.data['language_preference_id'] != '0':
            UserProfile.objects.filter(user_id=request.data['user_id']).update(
            language_preference_id=request.data['language_preference_id'])

        if request.data['is_contact_person'] == True:
            if Scientist.objects.filter(institute_office_id=request.data['institute_office_id'], is_contact_person=True).exists():
                official_obj = Scientist.objects.get(institute_office_id=request.data['institute_office_id'], is_contact_person=True)
                official_obj.is_contact_person = False
                official_obj.save()

        Scientist.objects.filter(id=request.data['institute_official_id']).update(
            institute_office_id=request.data['institute_office_id'],
            is_contact_person = request.data['is_contact_person']
        )
        data = {}
        data['message'] = 'updated'
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_institute_office_list(request):
    institute_office_list = list(InstituteOffice.objects.all().values_list('id', 'is_head_office', 'state', 'district', 'institute__name'))
    institute_office_columns = ['id', 'is_head_office', 'state_name', 'district_name','name']
    institute_df = pd.DataFrame(institute_office_list, columns=institute_office_columns)
    data = institute_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_institute_user_list(request):
    ins_official_obj = Scientist.objects.filter()
    institute_official_list = list(ins_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'institute_office_id', 'institute_office__institute__name',
            'institute_office__state', 'institute_office__is_head_office', 'institute_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'designation', 'user_profile__user__email', 'expertise'))
    institute_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'institute_office_id', 'institute_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'designation', 'email', 'expertise_list']
    institute_official_df = pd.DataFrame(institute_official_list, columns=institute_official_columns)
    institute_official_df = institute_official_df.fillna('0')

    institute_official_df = institute_official_df.groupby(['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'institute_office_id', 'institute_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'designation', 'email']).agg({'expertise_list' : 'unique'}).reset_index()

    data = institute_official_df.to_dict('r')
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


def find_branch_institute_count(institute_id):
    if InstituteOffice.objects.filter(institute_id=institute_id).exists():
        return InstituteOffice.objects.filter(institute_id=institute_id).count()
    else:
        return 0


#Nursery

@api_view(["GET"])
def serve_nursery(request):
    nursery_list = list(NurseryOffice.objects.filter(is_head_office=True).values_list('id', 'nursery__id', 'state', 'district', 
                        'block',  'nursery__name', 'nursery__short_name', 
                        'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude'))
    nursery_columns = ['id', 'nursery_nursery_id', 'nursery_state_name', 'nursery_district_name','nursery_block_name', 'nursery_name', 'nursery_short_name', 
    'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude']
    nursery_df = pd.DataFrame(nursery_list, columns=nursery_columns)
    nursery_df['nursery_branch_count']=nursery_df.apply(lambda x: find_branch_nursery_count(x["nursery_nursery_id"]), axis=1)
    # nursery_df = nursery_df.fillna('')
    data_dict = nursery_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


def find_branch_nursery_count(nursery_id):
    if NurseryOffice.objects.filter(nursery_id=nursery_id).exists():
        return NurseryOffice.objects.filter(nursery_id=nursery_id).count()
    else:
        return 0


@api_view(["POST"])
def save_nursery(request):
    print(request.data)
    data = {}
    if request.data['id'] == None:
        if Nursery.objects.filter(name=request.data['name'], short_name=request.data['short_name']).exists():
            print('Error: Institute name already exists')
            data['message'] = 'Institute Name Already Exists'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            sid = transaction.savepoint()
            try:
                nursery_obj = Nursery(name=request.data['name'], short_name=request.data['short_name'], nursery_type_id=1)
                nursery_obj.save()
                print('nursery saved')
                
                nursery_office_obj = NurseryOffice(
                    name="Head Office",
                    nursery=nursery_obj,
                    is_head_office = True,
                    state=request.data['state'],
                    district=request.data['district'],
                    block=request.data['block'],
                    revenue_village=request.data['revenue_village'],
                    village=request.data['village'],
                    street=request.data['street'],
                    taluk=request.data['taluk'],
                    pincode=request.data['pincode'],
                    latitude=request.data['latitude'],
                    longitude=request.data['longitude'],
                )
                nursery_office_obj.save()          
                print('nurseryOffice saved')  
                data = {'message' : 'saved'}
                transaction.savepoint_commit(sid)
            except Exception as e:
                print('Error - {}'.format(e))
                transaction.savepoint_rollback(sid)
                data = {'message' : 'something went wrong!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        try:
            NurseryOffice.objects.filter(id=request.data['id']).update(
                name="Head Office",
                state=request.data['state'],
                district=request.data['district'],
                block=request.data['block'],
                revenue_village=request.data['revenue_village'],
                village=request.data['village'],
                street=request.data['street'],
                taluk=request.data['taluk'],
                pincode=request.data['pincode'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude'],
            )

            nursery_id = NurseryOffice.objects.get(id=request.data['id']).nursery.id
            Nursery.objects.filter(id=nursery_id).update(
                name=request.data['name'], short_name=request.data['short_name']
            )

            print('data updated')
            data = {'message' : 'updated'}
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error - {}'.format(e))
            data = {'message' : 'something went wrong!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def save_nursery_branch(request):
    if request.data['id'] == None:
        nursery_office_obj = NurseryOffice(
        nursery_id=request.data['nursery_id'],
        name=request.data['name'],
        short_name=request.data['short_name'],
        is_head_office = False,
        state=request.data['state'],
        district=request.data['district'],
        block=request.data['block'],
        revenue_village=request.data['revenue_village'],
        village=request.data['village'],
        street=request.data['street'],
        taluk=request.data['taluk'],
        pincode=request.data['pincode'],
        latitude=request.data['latitude'],
        longitude=request.data['longitude'],
        )
        nursery_office_obj.save()   
        data= {'message':'branch added'}
    else:
        NurseryOffice.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            short_name=request.data['short_name'],
            state=request.data['state'],
            district=request.data['district'],
            block=request.data['block'],
            revenue_village=request.data['revenue_village'],
            village=request.data['village'],
            street=request.data['street'],
            taluk=request.data['taluk'],
            pincode=request.data['pincode'],
            latitude=request.data['latitude'],
            longitude=request.data['longitude'],
        )
        data= {'message':'branch updated'}
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_nursery_branches(request):
    nursery_list = list(NurseryOffice.objects.filter(nursery_id=request.data['nursery_id']).values_list('id', 'name', 'short_name',
                            'state', 'district','block', 'nursery__name', 'nursery__short_name'
                            , 'nursery__id','revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office'))
    nursery_columns = ['id', 'name', 'short_name', 'nursery_state_name', 'nursery_district_name','nursery_block_name', 'nursery_name', 'nursery_short_name','nursery_id',
      'revenue_village_name', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office']
    nursery_df = pd.DataFrame(nursery_list, columns=nursery_columns)
    data_dict = nursery_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_nursery_user_list(request):
    ins_official_obj = NurseryIncharge.objects.filter()
    nursery_official_list = list(ins_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'nursery_office_id', 'nursery_office__nursery__name',
            'nursery_office__state', 'nursery_office__is_head_office', 'nursery_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    nursery_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'nursery_office_id', 'nursery_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    nursery_official_df = pd.DataFrame(nursery_official_list, columns=nursery_official_columns)
    nursery_official_df = nursery_official_df.fillna('0')
    data = nursery_official_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_nursery_office_list(request):
    nursery_office_list = list(NurseryOffice.objects.all().values_list('id', 'is_head_office', 'state', 'district', 'nursery__name'))
    nursery_office_columns = ['id', 'is_head_office', 'state_name', 'district_name','name']
    nursery_df = pd.DataFrame(nursery_office_list, columns=nursery_office_columns)
    data = nursery_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_nursery_users(request):
    data = {}
    if request.data['user_id'] == None:
        if User.objects.filter(username=request.data['mobile']).exists():
            print('already exists')
            data['message'] = 'User already exists'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_obj = User(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                username=request.data['mobile'],
                password=make_password('1234')
            )
            user_obj.save()
            if request.data['email'] != None:
                user_obj.email = request.data['email']
                user_obj.save()
            print('------------------------user-saves--------------')
            try:
                user_profile_obj = UserProfile(
                    user=user_obj,
                    user_type_id=3,
                    added_by=request.user,
                    mobile=request.data['mobile'],
                    alternate_mobile=request.data['alternate_mobile'],
                )

                if request.data['language_preference_id'] != None:
                    user_profile_obj.language_preference_id = request.data['language_preference_id']
                user_profile_obj.save()
                print("-----------------------saves user profile------------------")
                
                if request.data['is_contact_person'] == True:
                    if NurseryIncharge.objects.filter(nursery_office_id=request.data['nursery_office_id'], is_contact_person=True).exists():
                        official_obj = NurseryIncharge.objects.get(nursery_office_id=request.data['nursery_office_id'], is_contact_person=True)
                        official_obj.is_contact_person = False
                        official_obj.save()

                nursery_obj = NurseryIncharge(
                    user_profile=user_profile_obj,
                    nursery_office_id=request.data['nursery_office_id'],
                    is_contact_person=request.data['is_contact_person']
                )
                nursery_obj.save()
                data = {}
                data['message'] = 'nursery user saved'
            except Exception as e:
                print(e)
                user_obj.delete()
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        User.objects.filter(id=request.data['user_id']).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            )
        
        UserProfile.objects.filter(user_id=request.data['user_id']).update(
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
        )
        
        if request.data['language_preference_id'] != '0':
            UserProfile.objects.filter(user_id=request.data['user_id']).update(
            language_preference_id=request.data['language_preference_id'])

        if request.data['is_contact_person'] == True:
            if NurseryIncharge.objects.filter(nursery_office_id=request.data['nursery_office_id'], is_contact_person=True).exists():
                official_obj = NurseryIncharge.objects.get(nursery_office_id=request.data['nursery_office_id'], is_contact_person=True)
                official_obj.is_contact_person = False
                official_obj.save()

        NurseryIncharge.objects.filter(id=request.data['nursery_official_id']).update(
            nursery_office_id=request.data['nursery_office_id'],
            is_contact_person=request.data['is_contact_person']
        )
        data = {}
        data['message'] = 'updated'
        return Response(data=data, status=status.HTTP_200_OK)

# forest
def find_forest_branch_count(forest_id):
    if ForestOffice.objects.filter(forest_id=forest_id).exists():
        return ForestOffice.objects.filter(forest_id=forest_id).count()
    else:
        return 0


@api_view(["GET"])
def serve_forest(request):
    forest_list = list(ForestOffice.objects.filter(is_head_office=True).values_list('id', 'forest__id', 'state', 'district', 
                        'block',  'forest__name', 'forest__short_name', 
                         'village', 'street', 'taluk', 'revenue_village','pincode', 'latitude', 'longitude'))
    forest_columns = ['id', 'forest_forest_id', 'forest_state_name', 'forest_district_name','forest_block_name', 'forest_name', 'forest_short_name', 
     'village', 'street', 'taluk', 'revenue_village', 'pincode', 'latitude', 'longitude']
    forest_df = pd.DataFrame(forest_list, columns=forest_columns)
    forest_df['forest_branch_count']=forest_df.apply(lambda x: find_forest_branch_count(x["forest_forest_id"]), axis=1)
    # forest_df = forest_df.fillna('')
    data_dict = forest_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_forest_office_list(request):
    forest_office_list = list(ForestOffice.objects.all().values_list('id', 'is_head_office', 'state', 'district', 'forest__name'))
    forest_office_columns = ['id', 'is_head_office', 'state_name', 'district_name','name']
    forest_df = pd.DataFrame(forest_office_list, columns=forest_office_columns)
    data = forest_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_forest_branches(request):
    forest_list = list(ForestOffice.objects.filter(forest_id=request.data['forest_id']).values_list('id', 'name', 'short_name',
                            'state', 'district','block', 'forest__name', 'forest__short_name'
                            , 'forest__id',                        
                         'revenue_village', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office'
                            ))
    forest_columns = ['id', 'name', 'short_name', 'forest_state_name', 'forest_district_name','forest_block_name', 'forest_name', 'forest_short_name','forest_id',
      'revenue_village_name', 'village', 'street', 'taluk', 'pincode', 'latitude', 'longitude', 'is_head_office']
    forest_df = pd.DataFrame(forest_list, columns=forest_columns)
    data_dict = forest_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_forest_user_list(request):
    ind_official_obj = ForestOfficial.objects.filter()
    forest_official_list = list(ind_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'forest_office_id', 'forest_office__forest__name',
            'forest_office__state', 'forest_office__is_head_office', 'forest_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    forest_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'forest_office_id', 'forest_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    forest_official_df = pd.DataFrame(forest_official_list, columns=forest_official_columns)
    forest_official_df = forest_official_df.fillna('0')
    data = forest_official_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
def save_forest(request):
    print(request.data)
    data = {}
    if request.data['id'] == None:
        if Forest.objects.filter(name=request.data['name'], short_name=request.data['short_name']).exists():
            print('Error: Forest name already exists')
            data['message'] = 'Forest Name Already Exists'
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            sid = transaction.savepoint()
            try:
                forest_obj = Forest(name=request.data['name'], short_name=request.data['short_name'])
                forest_obj.save()
                print('forest saved')
                forest_office_obj = ForestOffice(
                    name="Head Office",
                    forest=forest_obj,
                    is_head_office = True,
                    state=request.data['state'],
                    district=request.data['district'],
                    block=request.data['block'],
                    revenue_village=request.data['revenue_village'],
                    village=request.data['village'],
                    street=request.data['street'],
                    taluk=request.data['taluk'],
                    pincode=request.data['pincode'],
                    latitude=request.data['latitude'],
                    longitude=request.data['longitude'],
                )
                forest_office_obj.save()          
                print('forestOffice saved')  
                data = {'message' : 'saved'}
                transaction.savepoint_commit(sid)
            except Exception as e:
                print('Error - {}'.format(e))
                transaction.savepoint_rollback(sid)
                data = {'message' : 'something went wrong!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        try:
            ForestOffice.objects.filter(id=request.data['id']).update(
                state=request.data['state'],
                district=request.data['district'],
                block=request.data['block'],
                revenue_village=request.data['revenue_village'],
                village=request.data['village'],
                street=request.data['street'],
                taluk=request.data['taluk'],
                pincode=request.data['pincode'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude'],
            )

            forest_id = ForestOffice.objects.get(id=request.data['id']).forest.id
            Forest.objects.filter(id=forest_id).update(
                name=request.data['name'], short_name=request.data['short_name']
            )

            print('data updated')
            data = {'message' : 'updated'}
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error - {}'.format(e))
            data = {'message' : 'something went wrong!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def save_forest_branch(request):
    if request.data['id'] == None:
        forest_office_obj = ForestOffice(
        forest_id=request.data['forest_id'],
        is_head_office = False,
        state=request.data['state'],
        name=request.data['name'],
        short_name=request.data['short_name'],
        district=request.data['district'],
        block=request.data['block'],
        revenue_village=request.data['revenue_village'],
        village=request.data['village'],
        street=request.data['street'],
        taluk=request.data['taluk'],
        pincode=request.data['pincode'],
        latitude=request.data['latitude'],
        longitude=request.data['longitude'],
        )
        forest_office_obj.save()   
        data= {'message':'branch added'}
    else:
        ForestOffice.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            short_name=request.data['short_name'],
            state=request.data['state'],
            district=request.data['district'],
            block=request.data['block'],
            revenue_village=request.data['revenue_village'],
            village=request.data['village'],
            street=request.data['street'],
            taluk=request.data['taluk'],
            pincode=request.data['pincode'],
            latitude=request.data['latitude'],
            longitude=request.data['longitude'],
        )
        data= {'message':'branch updated'}
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_forest_users(request):
    print(request.data)
    data = {}
    if request.data['user_id'] == None:
        if User.objects.filter(username=request.data['mobile']).exists():
            print('already exists')
            data['message'] = 'User already exists'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_obj = User(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                username=request.data['mobile'],
                password=make_password('1234')
            )
            user_obj.save()
            if request.data['email'] != None:
                user_obj.email = request.data['email']
                user_obj.save()
            try:
                user_profile_obj = UserProfile(
                    user=user_obj,
                    user_type_id=6,
                    mobile=request.data['mobile'],
                    added_by=request.user,  
                    alternate_mobile=request.data['alternate_mobile'],
                )

                if request.data['language_preference_id'] != None:
                    user_profile_obj.language_preference_id = request.data['language_preference_id']
                user_profile_obj.save()
                
                if request.data['is_contact_person'] == True:
                    if ForestOfficial.objects.filter(forest_office_id=request.data['forest_office_id'], is_contact_person=True).exists():
                        official_obj = ForestOfficial.objects.get(forest_office_id=request.data['forest_office_id'], is_contact_person=True)
                        official_obj.is_contact_person = False
                        official_obj.save()

                forest_obj = ForestOfficial(
                    user_profile=user_profile_obj,
                    forest_office_id=request.data['forest_office_id'],
                    is_contact_person=request.data['is_contact_person']
                )
                forest_obj.save()
                data['message'] = 'forest user saved'
            except Exception as e:
                print(e)
                user_obj.delete()
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        User.objects.filter(id=request.data['user_id']).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            )
        
        UserProfile.objects.filter(user_id=request.data['user_id']).update(
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
        )
        
        if request.data['language_preference_id'] != '0':
            UserProfile.objects.filter(user_id=request.data['user_id']).update(
            language_preference_id=request.data['language_preference_id'])

        if request.data['is_contact_person'] == True:
            if ForestOfficial.objects.filter(forest_office_id=request.data['forest_office_id'], is_contact_person=True).exists():
                official_obj = ForestOfficial.objects.get(forest_office_id=request.data['forest_office_id'], is_contact_person=True)
                official_obj.is_contact_person = False
                official_obj.save()

        ForestOfficial.objects.filter(id=request.data['forest_official_id']).update(
            forest_office_id=request.data['forest_office_id'],
            is_contact_person=request.data['is_contact_person']
        )
        data = {}
        data['message'] = 'updated'
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_usertype_role_menu(request):
    data_dict = {'header': [], 'page': {}}
    print('get menu function')
    print(request.user)
    # request.user.user_profile
    user_id = request.user.id
    print(user_id)
    user_type = UserProfile.objects.get(user_id=user_id).user_type
    # user_type = request.user.userprofile.user_type
    print(user_type)
    if user_type.id == 7:
        menu_header_ids = MenuHeader.objects.filter().values_list('id', flat=True)
        menu_header_page_ids = MenuHeaderPage.objects.filter().values_list('id', flat=True)
    else:
        menu_header_ids = MenuHeaderPermission.objects.filter(user_type=user_type).values_list('menu_header',
                                                                                                       flat=True)
        menu_header_page_ids = MenuHeaderPagePermission.objects.filter(user_type=user_type).values_list(
            'menu_header_page', flat=True)
    print('one')
    header_values = MenuHeader.objects.filter(id__in=menu_header_ids).values_list('id', 'display_name', 'icon',
                                                                                  'link').order_by('ordinal')
    header_columns = ['id', 'display_name', 'icon', 'link']
    header_df = pd.DataFrame(list(header_values), columns=header_columns)
    data_dict['header'] = header_df.to_dict('r')

    page_values = MenuHeaderPage.objects.filter(id__in=menu_header_page_ids).values_list('id', 'display_name', 'icon',
                                                                                         'link', 'menu_header').order_by('ordinal')
    page_columns = ['id', 'display_name', 'icon', 'link', 'header_id']
    page_df = pd.DataFrame(list(page_values), columns=page_columns)
    data_dict['page'] = page_df.groupby('header_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_forest_stack_holders(request):
    
    if ForestOffice.objects.filter().exists():
        forest_office_obj = ForestOffice.objects.filter(is_head_office=True)
        forest_incharge_obj = ForestOfficial.objects.all()

        forest_value_list = list(forest_office_obj.values_list('id','forest__name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image'))                                                                                                                     
        forest_value_column = ['forest_office_id', 'forest_name', 'street', 'village', 'taluk', 'pincode', 'block', 'district', 'state', 'is_head_office', 'image']
        forest_df = pd.DataFrame(forest_value_list, columns=forest_value_column)
        forest_df = forest_df.fillna('')

        forest_value_list = list(forest_incharge_obj.values_list('id','user_profile_id', 'forest_office_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__mobile', 'is_contact_person', 'user_profile__user__email'))
        forest_officer_value_column = ['forest_official_id','user_profile_id', 'forest_office_id', 'first_name', 'last_name', 'mobile', 'contact_person', 'email']
        incharge_df = pd.DataFrame(forest_value_list, columns=forest_officer_value_column)
        incharge_df = incharge_df[incharge_df['contact_person']==True]

        final_df = pd.merge(forest_df, incharge_df, left_on='forest_office_id', right_on='forest_office_id', how='left')
        final_df = final_df.fillna('')

        for index, row in final_df.iterrows():
            image_path = settings.MEDIA_ROOT + '/' + str(row.image)
            final_df.at[index, 'full_address'] = str(row.street) + ', ' + str(row.village) + ', ' + str(row.taluk) + ', ' + str(row.block) + ', ' + str(row.district) + ', ' + str(row.state) 
            try:
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    final_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
            except Exception as e:
                print('ERROR - {}'.format(e))
                final_df.at[index, 'image'] = 0

        data_dict = final_df.fillna('').to_dict('r')
    else:
        data_dict = []
    return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['POST'])
def get_forest_details_for_given_id(request):
    data_dict = {}
    print(request.data)
    industry_incharge_obj = ForestOfficial.objects.get(forest_office_id=request.data['industry_id'], is_contact_person=True)
    industry_obj = industry_incharge_obj.forest_office.forest
    industry_office_obj = industry_incharge_obj.forest_office
    data_dict['industry_name'] = industry_obj.name
    data_dict['taluk_name'] = industry_office_obj.taluk
    # data_dict['district_id'] = industry_office_obj.district.id
    data_dict['district_name'] = industry_office_obj.district
    contact_person = ForestOfficial.objects.get(forest_office=industry_office_obj, is_contact_person=True).user_profile
    data_dict['mobile'] = contact_person.mobile
    data_dict['email'] = contact_person.user.email
    data_dict['first_name'] = contact_person.user.first_name
    data_dict['last_name'] = contact_person.user.last_name
    # data_dict['state_id'] = industry_office_obj.state.id
    data_dict['state_name'] = industry_office_obj.state
    # data_dict['block_id'] = industry_office_obj.block.id
    data_dict['address'] = str(industry_office_obj.street) + ', ' + str(industry_office_obj.village) + ', ' + str(industry_office_obj.taluk)  + ', ' + str(industry_office_obj.district) + ', ' + str(industry_office_obj.state)
    data_dict['block_name'] = industry_office_obj.block
    # data_dict['revenue_village'] = industry_office_obj.revenue_village.id
    data_dict['revenue_village'] = industry_office_obj.revenue_village
    data_dict['village'] = industry_office_obj.village
    data_dict['street'] = industry_office_obj.street
    data_dict['pincode'] = industry_office_obj.pincode
    data_dict['latitude'] = industry_office_obj.latitude
    data_dict['longitude'] = industry_office_obj.longitude

    try:
        image_path = settings.MEDIA_ROOT + '/' + str(industry_office_obj.image)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0

    else:
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)
def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name))


@api_view(["POST"])
@permission_classes((AllowAny,))
@transaction.atomic
def farmer_bulk_register(request):
    print(request.data)
    logging.info(request.data)
    sid = transaction.savepoint()
    try:
        print(request.user.id)

        base64_file = request.data['base_64_excel']
        file_name = request.data['file_name'].split('\\')[-1]
        print(file_name)
        farmer_bulk_upload_obj = FarmerBulkUploadLog(uploaded_by=request.user, uploaded_at=datetime.datetime.now(), uploaded_count=0, already_exists=0, excel_file=decode_image(base64_file, file_name), file_name=file_name)
        farmer_bulk_upload_obj.save()

        print(farmer_bulk_upload_obj.excel_file)
        #------------------data_upload_for_log--------------------------#
        df_from_excel = pd.read_excel(farmer_bulk_upload_obj.excel_file)

        # df_from_excel = df_from_excel.dropna(how='all', axis='columns')
        excel_columns = df_from_excel.columns

        # rename_columns
        for column_name in excel_columns:
            new_column_name = column_name.lower()
            if " " in new_column_name:
                new_column_name = new_column_name.replace(' ', '_')
                if new_column_name[-1] == "_":
                    new_column_name = new_column_name[:-1]

            df_from_excel = df_from_excel.rename(columns={column_name: new_column_name})
        print(df_from_excel)
        df_from_excel = df_from_excel.fillna(0)

        #------------------data_upload_for_farmer_profile--------------------------#
        already_exists = 0
        uploaded_count = 0
        for index, value in df_from_excel.iterrows():
            if User.objects.filter(username=value['mobile']).exists():
                already_exists += 1
            else:
                uploaded_count += 1
                user = User.objects.create(
                    first_name=value['first_name'],
                    last_name=value['last_name'],
                    username=value['mobile'],
                    password=make_password('1234')
                )
                print('user saved')
                user_profile = UserProfile.objects.create(
                    user=user,
                    user_type_id=1,
                    mobile=value['mobile'],
                    language_preference_id=1
                )
                value_dict = value.to_dict()
                if value.gender == 'Male':
                    value_dict['gender_id'] = 1
                elif value.gender == 'Female':
                    value_dict['gender_id'] = 2
                else:
                    value_dict['gender_id'] = 3

                status_code, data = post_data_to_micro_service(1, '/v1/main/save/farmer/', value_dict )
                user_profile.ms_farmer_code = data['farmer_code']
                print("this is access code", data)
                user_profile.save()

                data['token'] = make_token(value['mobile'], '1234')
                data['user_type_id'] = user_profile.user_type_id
                data['user_profile_id'] = user_profile.id

        #------------------data_upload_for_log--------------------------#
        farmer_bulk_upload_obj.uploaded_count = uploaded_count
        farmer_bulk_upload_obj.already_exists = already_exists
        farmer_bulk_upload_obj.save()
        transaction.savepoint_commit(sid)
        return Response(data={'status': 'Upload Complete !!!'}, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        logging.critical(f'Farmer save error = {e}')
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def serve_farmer_bulk_uploaded_detalils(request):
    uploaded_data_list = list(FarmerBulkUploadLog.objects.all().order_by('-id').values('file_name', 'uploaded_at', 'uploaded_by__first_name', 'uploaded_count', 'already_exists'))
    return Response(data=uploaded_data_list, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_forest_basic_details(request):
    data_dict = {}
    forest_incharge_obj = ForestOfficial.objects.get(user_profile__user_id=request.user.id)
    forest_obj = forest_incharge_obj.forest_office.forest
    forest_office_obj = forest_incharge_obj.forest_office
    data_dict['forest_id'] = forest_incharge_obj.id
    data_dict['forest_name'] = forest_obj.name
    data_dict['taluk_name'] = forest_office_obj.taluk
    # data_dict['district_id'] = forest_office_obj.district
    data_dict['district_name'] = forest_office_obj.district
    contact_person = ForestOfficial.objects.get(forest_office=forest_office_obj, is_contact_person=True).user_profile
    data_dict['mobile'] = contact_person.mobile
    data_dict['email'] = contact_person.user.email
    data_dict['first_name'] = contact_person.user.first_name
    data_dict['last_name'] = contact_person.user.last_name
    # data_dict['state_id'] = forest_office_obj.state.id
    data_dict['state_name'] = forest_office_obj.state
    # data_dict['block_id'] = forest_office_obj.block.id
    data_dict['address'] = forest_office_obj.street + ', ' + forest_office_obj.village + ', ' + forest_office_obj.taluk  + ', ' + forest_office_obj.district + ', ' + forest_office_obj.state
    data_dict['block_name'] = forest_office_obj.block
    # data_dict['revenue_village'] = forest_office_obj.revenue_village.id
    data_dict['revenue_village'] = forest_office_obj.revenue_village
    data_dict['village'] = forest_office_obj.village
    data_dict['street'] = forest_office_obj.street
    data_dict['pincode'] = forest_office_obj.pincode
    data_dict['latitude'] = forest_office_obj.latitude
    data_dict['longitude'] = forest_office_obj.longitude
    data_dict['about_me'] = contact_person.about_me

    forest_office_clone_map_obj = ForestOfficeCropMap.objects.filter(forest_office_id=forest_office_obj.id)
    forest_office_clone_map_list = list(forest_office_clone_map_obj.values_list('id', 'clone_id', 'clone__name', 'current_stock'))
    forest_office_clone_map_column = ['id', 'clone_id', 'clone_name', 'current_stock']
    forest_office_clone_map_df = pd.DataFrame(forest_office_clone_map_list, columns=forest_office_clone_map_column)
    data_dict['clone_data'] = forest_office_clone_map_df.to_dict('r')

    if ForestOfficeCropPriceLog.objects.filter(forest_office_crop_map__forest_office__id=forest_office_obj.id, is_active=True).exists():
        forest_office_clone_cost_map_obj = ForestOfficeCropPriceLog.objects.filter(forest_office_crop_map__forest_office__id=forest_office_obj.id, is_active=True)
        forest_office_clone_cost_map_list = list(forest_office_clone_cost_map_obj.values_list('id', 'forest_office_crop_map_id', 'cost', 'from_date'))
        forest_office_clone_cost_map_column = ['id', 'forest_office_crop_map_id', 'cost', 'from_date']
        forest_office_clone_cost_map_df = pd.DataFrame(forest_office_clone_cost_map_list, columns=forest_office_clone_cost_map_column)
        data_dict['clone_cost_data'] =  forest_office_clone_cost_map_df.groupby('nursery_office_crop_map_id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    else:
        data_dict['clone_cost_data'] = None




    try:
        photo_obj = UserProfile.objects.get(user_id=request.user.id)
        image_path = settings.MEDIA_ROOT + '/' + str(photo_obj.photo)
        # image_path = str(photo_obj.photo)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            
            data_dict['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        data_dict['image'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_crop_clone_forest(request):
    print(request.data)
    forest_office = ForestOfficial.objects.get(user_profile__user_id=request.user.id).forest_office
    forest_office_clone_map = ForestOfficeCropMap(forest_office_id=forest_office.id,
                                                    clone_id=request.data['clone_form']['clone_id'],
                                                    current_stock=request.data['clone_form']['stock'],
                                                    )
    forest_office_clone_map.save()
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_crop_clone_forest(request):
    forest_office = ForestOfficial.objects.get(user_profile__user_id=request.user.id).forest_office
    forest_office_clone_map_obj = ForestOfficeCropMap.objects.filter(forest_office_id=forest_office.id)
    clone_ids = list(forest_office_clone_map_obj.values_list('clone_id', flat=True))
    crop_clone_obj = Clone.objects.filter().exclude(id__in=clone_ids)
    crop_clone_list = list(crop_clone_obj.values_list('id', 'name', 'crop_cv', 'crop_cv__name'))
    crop_clone_column = ['id', 'name', 'crop_cv_id', 'crop_name']
    crop_clone_df = pd.DataFrame(crop_clone_list, columns=crop_clone_column)
    data = crop_clone_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['POST'])
def delete_crop_clone_forest(request):
    ForestOfficeCropMap.objects.filter(id=request.data['clone_map_id']).delete()
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_crop_clone_forest(request):
    forest_office_clone_map = ForestOfficeCropMap.objects.get(id=request.data['clone_map_id'])
    forest_office_clone_map.current_stock = request.data['clone_form']['stock']
    forest_office_clone_map.save()

     # update the cost of the clone
    if not ForestOfficeCropPriceLog.objects.filter(forest_office_crop_map=forest_office_clone_map, is_active=True).exists():
        create_forest_office_crop_price_log(forest_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    else:
        old_cost_map_obj = ForestOfficeCropPriceLog.objects.get(forest_office_crop_map=forest_office_clone_map, is_active=True)
        old_cost_map_obj.is_active = False
        old_cost_map_obj.effective_date = datetime.datetime.now()
        old_cost_map_obj.modified_by = request.user
        old_cost_map_obj.save()
        create_forest_office_crop_price_log(forest_office_clone_map.id, request.data['clone_form']['cost'], request.user)
    return Response(data={}, status=status.HTTP_200_OK)


def create_forest_office_crop_price_log(forest_office_clone_map_id, cost, user):
    nursery_obj = ForestOfficeCropPriceLog.objects.create(
        forest_office_crop_map_id=forest_office_clone_map_id,
        cost=cost,
        is_active=True,
        from_date=datetime.datetime.now(),
        created_by=user,
        modified_by=user
    )
    print('new forest cost log created')
    return nursery_obj


@api_view(['GET'])
def serve_branches_for_industry(request):
    print('function called')
    data_dict = {}
    industry_official_obj = IndustryOfficial.objects.get(user_profile__user_id=request.user.id)
    industry_office_obj = industry_official_obj.industry_office
    industry_id = industry_office_obj.industry_id
    if industry_office_obj.is_head_office:
        data_dict['head_office'] = IndustryOffice.objects.filter(id=industry_office_obj.id).values()[0]
        head_office_id = IndustryOffice.objects.filter(id=industry_office_obj.id).values()[0]['id']
    else:
        data_dict['head_office'] = IndustryOffice.objects.filter(industry_id=industry_id, is_head_office=True).values()[0]
        head_office_id = IndustryOffice.objects.filter(industry_id=industry_id, is_head_office=True).values()[0]['id']

    #     branches
    data_dict['branches'] = list(IndustryOffice.objects.filter(industry_id=industry_id).exclude(id=head_office_id).values())
    
    if IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map__industry_office__id=data_dict['head_office']['id'], is_active=True).exists():
        procurement_price_objs =IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map__industry_office__id=data_dict['head_office']['id'], is_active=True)
        price_list = list(procurement_price_objs.values_list('id', 'industry_office_crop_map__crop_cv__name', 'cost'))
        price_values = ['id', 'crop_name', 'cost']
        price_df = pd.DataFrame(price_list, columns=price_values)
        price_df = price_df.fillna(0)
        data_dict['procurement_price'] = price_df.to_dict('r')
    else:
        data_dict['procurement_price'] = []
    print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@transaction.atomic
def farmer_geo_fence_data_register(request):
    sid = transaction.savepoint()
    try:
        print(request.user.id)

        sheet_id = "1hdYgyHUqCesUfr22PpYx_VgA88A2QavcKSRP011sCRY"
        sheet_name = "farmer_geo_fence"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df_from_excel = pd.read_csv(url)

        #------------------data_upload_for_log--------------------------#

        # df_from_excel = df_from_excel.dropna(how='all', axis='columns')
        excel_columns = df_from_excel.columns

        # rename_columns
        for column_name in excel_columns:
            new_column_name = column_name.lower()
            if " " in new_column_name:
                new_column_name = new_column_name.replace(' ', '_')
                if new_column_name[-1] == "_":
                    new_column_name = new_column_name[:-1]

            df_from_excel = df_from_excel.rename(columns={column_name: new_column_name})
        print(df_from_excel)
        df_from_excel = df_from_excel.fillna(0)

        #------------------data_upload_for_farmer_profile--------------------------#
        already_exists = 0
        uploaded_count = 0
        for index, value in df_from_excel.iterrows():
            if User.objects.filter(username=value['mobile']).exists():
                already_exists += 1
            else:
                uploaded_count += 1
                user = User.objects.create(
                    first_name=value['first_name'],
                    last_name=value['last_name'],
                    username=value['mobile'],
                    password=make_password('1234')
                )
                print('user saved')
                user_profile = UserProfile.objects.create(
                    user=user,
                    user_type_id=1,
                    mobile=value['mobile'],
                    language_preference_id=1
                )
                value_dict = value.to_dict()
                if value.gender == 'Male':
                    value_dict['gender_id'] = 1
                elif value.gender == 'Female':
                    value_dict['gender_id'] = 2
                else:
                    value_dict['gender_id'] = 3

                status_code, data = post_data_to_micro_service(1, '/v1/main/save/farmer/for/geo/fence/', value_dict )
                user_profile.ms_farmer_code = data['farmer_code']
                print("this is access code", data)
                user_profile.save()

                data['token'] = make_token(value['mobile'], '1234')
                data['user_type_id'] = user_profile.user_type_id
                data['user_profile_id'] = user_profile.id

        transaction.savepoint_commit(sid)
        return Response(data={'status': 'Upload Complete !!!'}, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        logging.critical(f'Farmer save error = {e}')
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def serve_farmers_location_with_crop(request):
    serve_url = '/v1/main/serve/farmers/location/with/crop/'
    data_dict = get_data_from_micro_service(1, serve_url)
    return Response(data=data_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_all_scientist(request):
    assigned_id_list = list(QueryExpertAssignMap.objects.filter().values_list('assigned_to_id', flat=True))
    scientist_obj = UserProfile.objects.filter(user_type=5).values_list('user_id', 'user__first_name')
    columns = ["user_id", "scientist_name"]
    scientist_df = pd.DataFrame(list(scientist_obj), columns=columns)
    scientist_list = scientist_df.to_dict('r')
    return Response(data=scientist_list, status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_assigned_scientist_list(request):
    assigned_id_list = list(QueryExpertAssignMap.objects.filter(user_query=request.data['query_id']).values_list('assigned_to_id', flat=True))
    return Response(data=assigned_id_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_for_authentication(request):
    print('authentication check')
    return Response(status=status.HTTP_200_OK)


# farmer register via field officer
@api_view(['POST'])
@permission_classes((AllowAny,))
def check_for_farmer(request):
    data_dict = {}
    if User.objects.filter(username=request.data['mobile']).exists():
        data_dict['status'] = True
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        return Response(data=data_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_experties_list(request):
    expertise_list = list(Expertise.objects.all().values())
    return Response(data=expertise_list, status=status.HTTP_200_OK)

@api_view(['GET'])
def farmer_list_for_field_officer(request):
    print(request.user.id)
    
    farmer_code_list = list(UserProfile.objects.filter(added_by__id=request.user.id).values_list('ms_farmer_code', flat=True))
    data_dict = {
        'farmer_checksums': farmer_code_list,
    }
    status_code, data = post_data_to_micro_service(1, '/v1/main/get/farmer/list/for/field/officer/', data_dict)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_user_type_for_surveyor(request):
    type_ids = [3,4,5]
    master_dict = {}
    user_list = []
    final_dict = {}

    user_type_obj = UserType.objects.filter(id__in=type_ids)
    type_list = []
    for item in user_type_obj:
        user_type = {
            'id': item.id,
            'type': item.name
            }
        type_list.append(user_type)
        
        if not item.id in master_dict:
            master_dict[item.id] = []
            
            if item.id == 3:  #QPM
                nursery_obj = NurseryOffice.objects.filter().values_list('id', 'nursery__name')
                nursery_columns = ['office_id', 'office_name']
                nursery_df = pd.DataFrame(list(nursery_obj), columns=nursery_columns)
                nursery_list = nursery_df.to_dict('r')
                master_dict[item.id] = nursery_list
            elif item.id == 4:  #IndustryOffice
                industry_obj = IndustryOffice.objects.filter().values_list('id', 'industry__name')
                industry_columns = ['office_id', 'office_name']
                industry_df = pd.DataFrame(list(industry_obj), columns=industry_columns)
                industry_list = industry_df.to_dict('r')
                master_dict[item.id] = industry_list
            elif item.id == 5:  #InstituteOffice
                institute_obj = InstituteOffice.objects.filter().values_list('id', 'institute__name')
                institute_columns = ['office_id', 'office_name']
                institute_df = pd.DataFrame(list(institute_obj), columns=institute_columns)
                institute_list = institute_df.to_dict('r')
                master_dict[item.id] = institute_list
        final_dict['user_types'] = type_list
        final_dict['user_types_details'] = master_dict
    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def surveyor_official_map_save(request):
    sid = transaction.savepoint()
    first_name = request.data['first_name']
    last_name =  request.data['last_name']
    mobile = request.data['mobile']
    office_id = request.data['office_id']
    superior_user_type = request.data['superior_user_type']
    user_type_id = 7  #surveyor
    added_by_id = request.user.id
    try:
        if not User.objects.filter(username=mobile).exists():
            user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    username=mobile,
                    password=make_password('1234')
                )
            user.save()
            print('user saved')

            user_profile = UserProfile.objects.create(
                user_id=user.id,
                user_type_id=user_type_id,
                mobile=mobile,
                added_by_id = added_by_id
            )
            user_profile.save()
            print('user_profile saved')
            if superior_user_type == 3:
                print('qpm')
                surveyor_official_map = SurveyorOfficialMap.objects.create(
                                        surveyor_id = user.id,
                                        superior_user_type_id = superior_user_type,
                                        nursery_office_id = office_id)
                surveyor_official_map.save()
                print('surveyor_official_saved')
                data = {'status':'Surveyor Registred Sucessfully'}
            elif superior_user_type == 4:
                print('industry_office')
                surveyor_official_map = SurveyorOfficialMap.objects.create(
                                        surveyor_id = user.id,
                                        superior_user_type_id = superior_user_type,
                                        industry_office_id = office_id)
                surveyor_official_map.save()
                print('surveyor_official_saved')
                data = {'status':'Surveyor Registred Sucessfully'}
            elif superior_user_type == 5:
                print('inistitute_office')
                surveyor_official_map = SurveyorOfficialMap.objects.create(
                                        surveyor_id = user.id,
                                        superior_user_type_id = superior_user_type,
                                        institute_office_id = office_id)
                surveyor_official_map.save()
                print('surveyor_official_saved')
                data = {'status':'Surveyor Registred Sucessfully'}
            else:
                print('no_value_found_in_tabe')
                data = {'status':'error'}
        else:
            data = {'status':'User alredy exists'}    
        transaction.savepoint_commit(sid)
        return Response(data=data, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        logging.critical(f'surveyor save error = {e}')
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_surveyor_list(request):
    # office_name = []
    # surveyou_first_name = []
    # surveyou_last_name = []
    # mobile = []
    # temp_dict = {}
    surveyor_official_map_obj = SurveyorOfficialMap.objects.filter().values_list('surveyor', 'surveyor__first_name', 'surveyor__last_name', 'surveyor__username','superior_user_type_id','superior_user_type__name', 'industry_office','industry_office__industry__name', 'institute_office_id','institute_office__institute__name', "nursery_office",'nursery_office__nursery__name')
    columns = ["surveyor_id", "surveyor_first_name", 'surveyor_last_name', "mobile", "superior_user_type","superior_user_type_name", "industry_office_id", "industry_office_name", "institute_id","institute_office_name", "nursery_id","nursery_office_name"]
    surveyor_df = pd.DataFrame(list(surveyor_official_map_obj), columns=columns)
    surveyor_df = surveyor_df.fillna(0)
    surveyor_df['office_id'] = None
    surveyor_df['office_name'] = None
    for index, row in surveyor_df.iterrows():
        if row['superior_user_type'] == 3:
            surveyor_df.at[index, 'office_id'] = row['nursery_id']
            surveyor_df.at[index, 'office_name'] = row['nursery_office_name']
        elif row['superior_user_type'] == 4:
            surveyor_df.at[index, 'office_id'] = row['industry_office_id']
            surveyor_df.at[index, 'office_name'] = row['industry_office_name']
        elif row['superior_user_type'] == 5:
            surveyor_df.at[index, 'office_id'] = row['institute_id']
            surveyor_df.at[index, 'office_name'] = row['institute_office_name']
    surveyor_list = surveyor_df.to_dict('r')
    return Response(data=surveyor_list, status=status.HTTP_200_OK)

@api_view(['POST'])
def to_update_surveyor(request):
    sid = transaction.savepoint()
    first_name = request.data['first_name']
    last_name =  request.data['last_name']
    mobile = request.data['mobile']
    office_id = request.data['office_id']
    superior_user_type = request.data['superior_user_type']
    user_type_id = 7  #surveyor
    added_by_id = request.user.id
    surveyor_id = request.data['surveyor_id']
    try:
        if User.objects.filter(id=surveyor_id).exists():
            print('yes')
            User.objects.filter(id=surveyor_id).update(
                            first_name=first_name,
                            last_name=last_name)
            print('names_updated')
            print('user saved')
            SurveyorOfficialMap.objects.filter(surveyor_id=surveyor_id).update(nursery_office_id = None,
                                                                        industry_office_id = None,
                                                                        institute_office_id = None)
            if superior_user_type == 3:
                print('qpm')
                SurveyorOfficialMap.objects.filter(surveyor_id=surveyor_id).update(nursery_office_id = office_id, 
                                                                                superior_user_type_id=superior_user_type)
                data = {'status':'Surveyor Updated Sucessfully'}
            elif superior_user_type == 4:
                SurveyorOfficialMap.objects.filter(surveyor_id=surveyor_id).update(industry_office_id = office_id, 
                                                                                superior_user_type_id=superior_user_type)
                data = {'status':'Surveyor Updated Sucessfully'}
            elif superior_user_type == 5:
                print('inistitute_office')
                SurveyorOfficialMap.objects.filter(surveyor_id=surveyor_id).update(institute_office_id = office_id, 
                                                                            superior_user_type_id=superior_user_type)
                data = {'status':'Surveyor Updated Sucessfully'}
            else:
                print('no_value_found_in_tabe')
                data = {'status':'error'}
        else:
            data = {'status':'User alredy exists'}    
        transaction.savepoint_commit(sid)
        return Response(data=data, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        logging.critical(f'surveyor save error = {e}')
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def to_delete_surveyor(request):
    print(request.data)
    mobile = request.data['mobile']
    User.objects.filter(username=mobile).update(is_active=False)
    return Response(data={'status':'Surveyor Deleted'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_surveyor_basic_details(request):
    print(request.data)
    surveyor_official_map_obj = SurveyorOfficialMap.objects.filter(surveyor_id=request.user.id).values_list('surveyor', 'surveyor__first_name', 'surveyor__last_name', 'surveyor__username','superior_user_type_id','superior_user_type__name', 'industry_office','industry_office__industry__name', 'institute_office_id','institute_office__institute__name', "nursery_office",'nursery_office__nursery__name')
    columns = ["surveyor_id", "surveyor_first_name", 'surveyor_last_name', "mobile", "superior_user_type","superior_user_type_name", "industry_office_id", "industry_office_name", "institute_id","institute_office_name", "nursery_id","nursery_office_name"]
    surveyor_df = pd.DataFrame(list(surveyor_official_map_obj), columns=columns)
    surveyor_df = surveyor_df.fillna(0)
    surveyor_df['office_id'] = None
    surveyor_df['office_name'] = None
    user_type_name = UserProfile.objects.get(user_id=request.user.id).user_type.name
    surveyor_df['user_type_name'] = user_type_name

    for index, row in surveyor_df.iterrows():
        if row['superior_user_type'] == 3:
            surveyor_df.at[index, 'office_id'] = row['nursery_id']
            surveyor_df.at[index, 'office_name'] = row['nursery_office_name']
        elif row['superior_user_type'] == 4:
            surveyor_df.at[index, 'office_id'] = row['industry_office_id']
            surveyor_df.at[index, 'office_name'] = row['industry_office_name']
        elif row['superior_user_type'] == 5:
            surveyor_df.at[index, 'office_id'] = row['institute_id']
            surveyor_df.at[index, 'office_name'] = row['institute_office_name']
    surveyor_df = surveyor_df.fillna(0)
    surveyor_list = surveyor_df.to_dict('r')[0]

    try:
        img_obj = UserProfile.objects.get(user_id=request.user.id)
        image_path = settings.MEDIA_ROOT + '/' + str(img_obj.photo)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            surveyor_list['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as e:
        print('ERROR - {}'.format(e))
        surveyor_list['image'] = 0
    return Response(data=surveyor_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_surveyor_basic_details(request):
    print('datea::',request.user.id)
    surveyor_obj = User.objects.get(id=request.user.id)
    if request.data['field'] == 'name':
        surveyor_obj.first_name = request.data['first_name']
        surveyor_obj.last_name = request.data['last_name']
        surveyor_obj.save()
    elif request.data['field'] == 'email':
        surveyor_obj.email = request.data['email']
        surveyor_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_notification_for_admin(request):
   # ask expert notification 
    user_query_list = UserQuery.objects.filter(is_assigned=False).order_by('-id').values_list('id', 'requested_date', 'notes', 'query_type__id', 'query_type__name',
                            'status', 'status__name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone__name', 'clone__crop_cv__name', 'voice')
    user_query_column = ['id', 'requested_date', 'notes', 'query_type', 'query_type__name',
                        'status_id', 'status_name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone_name', 'crop_name', 'voice_path']
    user_query_df = pd.DataFrame(user_query_list, columns=user_query_column)
    data_list = user_query_df.to_dict('r')
    return Response(data=data_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_notification_for_scientist(request):
    user_id = request.user.id
    notification_list = NotificatiionLog.objects.filter(user_id=user_id, is_active=True).order_by('-id').values_list('id', 'user_query_id', 'user_query__requested_date', 'user_query__notes', 'user_query__query_type__id', 'user_query__query_type__name',
                            'user_query__status', 'user_query__status__name', 'user_query__time_created', 'user_query__area_in_acre', 'user_query__age_in_year', 'user_query__age_in_month', 'user_query__title', 'user_query__clone__name', 'user_query__clone__crop_cv__name', 'user_query__voice', 
                            'notification_type__name', 'notification_type_id', 'notification_type__color', 'notification_type__background', 'is_sceen', 'notification_text', 'time_created')
    notification_column = ['id', 'user_query_id', 'requested_date', 'notes', 'query_type', 'query_type__name',
                        'status_id', 'status_name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone_name', 'crop_name', 'voice_path', 'notification_type', 'notification_type_id', 'color', 'background', 'is_seen', 'notification_text', 'time_created']
    notification_df = pd.DataFrame(notification_list, columns=notification_column)
    print(notification_df)
    if not notification_df.empty:
        notification_df['audio'] = notification_df.apply(lambda x: convert_wav_to_base64(x['voice_path']), axis=1)
        notification_df['play_audio'] = False
        notification_df = notification_df.fillna('')
    data_list = notification_df.sort_values(["id"], ascending=False)
    data_list = notification_df.to_dict('r')
    return Response(data=data_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_notification_for_farmer(request):
    user_id = request.user.id
    notification_list = NotificatiionLog.objects.filter(user_id=user_id, is_active=True).order_by('-id').values_list('id', 'recommendation__user_query_id', 'recommendation__user_query__requested_date', 'recommendation__user_query__notes', 'recommendation__user_query__query_type__id', 'recommendation__user_query__query_type__name',
                            'recommendation__user_query__status', 'recommendation__user_query__status__name', 'recommendation__user_query__time_created', 'recommendation__user_query__area_in_acre', 'recommendation__user_query__age_in_year', 'recommendation__user_query__age_in_month', 'recommendation__user_query__title', 'recommendation__user_query__clone__name', 'recommendation__user_query__clone__crop_cv__name', 'recommendation__user_query__voice', 
                            'notification_type__name', 'notification_type_id', 'notification_type__color', 'notification_type__background', 'is_sceen', 'notification_text', 'time_created')
    notification_column = ['id', 'user_query_id', 'requested_date', 'notes', 'query_type', 'query_type__name',
                        'status_id', 'status_name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone_name', 'crop_name', 'voice_path', 'notification_type', 'notification_type_id', 'color', 'background', 'is_seen', 'notification_text', 'time_created']
    notification_df = pd.DataFrame(notification_list, columns=notification_column)
    print(notification_df)
    if not notification_df.empty:
        notification_df['audio'] = notification_df.apply(lambda x: convert_wav_to_base64(x['voice_path']), axis=1)
        notification_df['play_audio'] = False
        notification_df = notification_df.fillna('')
    data_list = notification_df.sort_values(["id"], ascending=False)
    data_list = notification_df.to_dict('r')
    return Response(data=data_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def disable_notifications(request):
    notification_obj = NotificatiionLog.objects.get(id=request.data['notification_id'])
    notification_obj.is_sceen = True
    notification_obj.save()
    print("status changed to true")
    return Response(True, status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_scientists(request):
    print(request.data)
    user_query = request.data['user_query']
    removed_scientists = QueryExpertAssignMap.objects.filter(user_query=user_query)
    removed_scientists.delete()
    return Response(data='success', status=status.HTTP_200_OK)


@api_view(["POST"])
def serve_journals(request):
    print("=============================================",request.data)
    start_id = request.data['current_id']
    end_id = start_id + 12
    journal_obj = Journal.objects.filter().order_by('-id')[start_id:end_id]
    journal_values = list(journal_obj.values_list('id', 'title', 'author', 'published_on', 'journal_file', 'category__name', 'category_id'))
    journal_columns = ['id', 'title', 'author', 'published_on', 'journal_file', 'category_name', 'category_id']
    journal_df = pd.DataFrame(journal_values, columns=journal_columns)

    for index, row in journal_df.iterrows():
        image_path = settings.MEDIA_ROOT + '/' + str(row.journal_file)
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                journal_df.at[index, 'image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        except Exception as e:
            print('ERROR - {}'.format(e))
            journal_df.at[index, 'image'] = 0
    final_df = journal_df.fillna('0')
    data = final_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_category(request):
    category_list = JournalsCategory.objects.filter().values_list('id', 'name')
    category_columns = ["id", "category_name"]
    category_df = pd.DataFrame(list(category_list), columns=category_columns)
    category_list = category_df.to_dict('r')
    return Response(data=category_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def store_journal(request):
    # new news create
    print(request.data)
    if request.data['news_id'] == '0':
        print('new journal')
        print(request.data)
        journal_obj = Journal(title=request.data['title'],
                            author=request.data['author'],
                            published_on=request.data['published_on'],
                            category_id=request.data['category_id'],
                            )
        if 'journal_file' in request.data:
            if request.data['journal_file'] != 'undefined':
                complete_image = create_complete_image(request.data['image'])
                journal_obj.journal_file = complete_image
        journal_obj.save()
        print('saved_journal')
        return Response(status=status.HTTP_200_OK)

    if request.data['news_id'] != '0':
        print('update news')
        journal_obj = Journal.objects.get(id=request.data['news_id'])

        journal_obj.title=request.data['title']
        journal_obj.author=request.data['author']
        journal_obj.published_on=request.data['published_on']
        journal_obj.category_id=request.data['category_id']

        # journal_obj = Journal(title=request.data['title'],
        #                         author=request.data['author'],
        #                         published_on=request.data['published_on'],
        #                         category_id=request.data['category_id'],
        #                         )
        if 'journal_file' in request.data:
            if request.data['journal_file'] != 'undefined':
                complete_image = create_complete_image(request.data['image'])
                journal_obj.journal_file = complete_image
        journal_obj.save()
        print("updated")
        return Response(status=status.HTTP_200_OK)
    
    
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


def send_push_notification(title, body, notification_log_obj, data):
    print('user_ids', notification_log_obj.user_id)
    prefix_text = 'IFGTB - '
    if title == 'Recommendation':
        user_name = User.objects.get(id=notification_log_obj.recommendation.recommended_by_id).first_name
        prefix_text = 'Recommended by, ' + user_name + ' - '
    elif title == 'User Query':
        user_name = User.objects.get(id=notification_log_obj.user_query.user.id).first_name
        prefix_text = 'Asked by, ' + user_name + ' - '
    
    print('title', title)
    print('body', body)
    print('======= within in push notification ===========>')
    print("title = {}, body = {}, data = {}".format(title, prefix_text + body, data))
    
    
    user_objects = FCMDevice.objects.filter(user_id=notification_log_obj.user_id)
    try:
        fcm_token = []
        for obj in user_objects:
            fcm_token.append(obj.registration_id)
        return push_service.notify_multiple_devices(
            registration_ids=fcm_token,message_title=title,
            message_body=prefix_text + body, data_message=data)
    except:
        pass

    # devices = FCMDevice.objects.filter(user__in=list(user_id))
    # print('-----notification sent success------')
    # for device in devices:
    #     result = device.send_message(title=title, body=body, sound="default", data=data)
    #     print(device)
    #     print('-----notification sent success------')
    # retur


@api_view(['GET'])
def serve_district_wise_data(request):
    data_dict = {}
    data_dict['address_dict'] = serve_country_state_district()
    data_dict['stake_holders'] = list(UserType.objects.all().exclude(id__in=[2,7]).values('id', 'name'))
    data_dict['crop_list'] = serve_crop_cvs_for_notification()
    print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)

# def serve_crop_cvs():
#     data = get_data_from_micro_service(1, '/v1/main/serve/crop/cvs/')
#     # data_dict = pd.DataFrame(list(CropCv.objects.filter().values())).to_dict('r')
#     return data

def serve_country_state_district():
    serve_url = '/main/serve/country/state/district/taluk/city/'
    response_data = get_data_from_micro_service(3, serve_url)
    return response_data

def serve_farmers_basic_info_data_district_wise(data):
    serve_url = '/v1/main/serve/farmers/basic/info/data/district/wise/'
    status_code, response_data = post_data_to_micro_service(1, serve_url, data)
    return response_data

def get_nursery_user_list_district_wise():
    ins_official_obj = NurseryIncharge.objects.filter()
    nursery_official_list = list(ins_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'nursery_office_id', 'nursery_office__nursery__name',
            'nursery_office__state', 'nursery_office__is_head_office', 'nursery_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    nursery_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'nursery_office_id', 'nursery_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    nursery_official_df = pd.DataFrame(nursery_official_list, columns=nursery_official_columns)
    nursery_official_df = nursery_official_df.fillna('0')
    data_dict = nursery_official_df.groupby('district_name').apply(lambda x: x.to_dict('r')).to_dict()
    return data_dict

def get_forest_user_list_district_wise():
    ind_official_obj = ForestOfficial.objects.filter()
    forest_official_list = list(ind_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'forest_office_id', 'forest_office__forest__name',
            'forest_office__state', 'forest_office__is_head_office', 'forest_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    forest_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'forest_office_id', 'forest_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    forest_official_df = pd.DataFrame(forest_official_list, columns=forest_official_columns)
    forest_official_df = forest_official_df.fillna('0')
    data_dict = forest_official_df.groupby('district_name').apply(lambda x: x.to_dict('r')).to_dict()
    return data_dict

def get_industry_user_list_district_wise():
    ind_official_obj = IndustryOfficial.objects.filter()
    industry_official_list = list(ind_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'industry_office_id', 'industry_office__industry__name',
            'industry_office__state', 'industry_office__is_head_office', 'industry_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'user_profile__user__email'))
    industry_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'industry_office_id', 'industry_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'email']
    industry_official_df = pd.DataFrame(industry_official_list, columns=industry_official_columns)
    industry_official_df = industry_official_df.fillna('0')
    data_dict = industry_official_df.groupby('district_name').apply(lambda x: x.to_dict('r')).to_dict()
    return data_dict

def get_institute_user_list_district_wise():
    ins_official_obj = Scientist.objects.filter()
    institute_official_list = list(ins_official_obj.values_list('id', 'user_profile__user_id','user_profile_id', 'user_profile__user__first_name', 
            'user_profile__user__last_name', 'user_profile__mobile', 'institute_office_id', 'institute_office__institute__name',
            'institute_office__state', 'institute_office__is_head_office', 'institute_office__district', 'user_profile__alternate_mobile', 
            'user_profile__language_preference_id', 'is_contact_person', 'designation', 'user_profile__user__email', 'expertise'))
    institute_official_columns = ['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'institute_office_id', 'institute_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'designation', 'email', 'expertise_list']
    institute_official_df = pd.DataFrame(institute_official_list, columns=institute_official_columns)
    institute_official_df = institute_official_df.fillna('0')

    institute_official_df = institute_official_df.groupby(['id', 'user_id', 'user_profile_id', 'first_name', 'last_name', 'mobile', 'institute_office_id', 'institute_name',
            'state_name', 'is_head_office', 'district_name', 'alternate_mobile', 'language_preference_id', 'is_contact_person', 'designation', 'email']).agg({'expertise_list' : 'unique'}).reset_index()

    data_dict = institute_official_df.groupby('district_name').apply(lambda x: x.to_dict('r')).to_dict()
    return data_dict


@api_view(['POST'])
def send_notification_to_users(request):
    notification_dict = request.data
    state = notification_dict['state']
    district = notification_dict['district']

    if notification_dict['stakeholder_id'] == 1:
        farmer_data_df = pd.DataFrame(serve_farmers_basic_info_data_district_wise(notification_dict))
        user_ids = list(UserProfile.objects.filter(ms_farmer_code__in=list(farmer_data_df['ms_farmer_code'])).values_list('user_id', flat=True))
        print(user_ids)

    elif notification_dict['stakeholder_id'] == 3:
        user_obj = NurseryIncharge.objects.filter()
        if district != "All":
            user_obj = user_obj.filter(nursery_office__district=district)
        if state != "All":
            user_obj = user_obj.filter(nursery_office__state=state)
        
        user_ids = list(user_obj.values_list('user_profile__user_id', flat=True))

    elif notification_dict['stakeholder_id'] == 4:
        user_obj = IndustryOfficial.objects.filter()
        if district != "All":
            user_obj = user_obj.filter(industry_office__district=district)
        if state != "All":
            user_obj = user_obj.filter(industry_office__state=state)
        user_ids = list(user_obj.values_list('user_profile__user_id', flat=True))

    elif notification_dict['stakeholder_id'] == 5:
        user_obj = Scientist.objects.filter()
        if district != "All":
            user_obj = user_obj.filter(institute_office__district=district)
        if state != "All":
            user_obj = user_obj.filter(institute_office__state=state)
        user_ids = list(user_obj.values_list('user_profile__user_id', flat=True))

    elif notification_dict['stakeholder_id'] == 6:
        user_obj = ForestOfficial.objects.filter()
        if district != "All":
            user_obj = user_obj.filter(forest_office__district=district)
        if state != "All":
            user_obj = user_obj.filter(forest_office__state=state)
        user_ids = list(user_obj.values_list('user_profile__user_id', flat=True))

    for user_id in user_ids:
        notification_log_obj = NotificatiionLog.objects.create(user_id=user_id, notification_type_id=3, notification_text=notification_dict['notification_text'])

        send_push_notification(notification_log_obj.notification_type.name, notification_log_obj.notification_text, notification_log_obj, data={'by': 'IFGTB'})
        
    return Response(data={'is_send':True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_iframe(request):
    data = 'http://portal.ifgtbtreegenie.in/mobile_map'
    return Response(data=data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_procurement_price_industry(request):
    data = {}
    print(request.data)
    if IndustryOfficeCropMap.objects.filter(industry_office_id=request.data['head_office_id'], crop_cv=request.data['crop_id']).exists():
        industry_office_crop_map_id = IndustryOfficeCropMap.objects.get(industry_office_id=request.data['head_office_id'], crop_cv_id=request.data['crop_id'])
    else:
        industry_office_crop_map_id = IndustryOfficeCropMap.objects.create(
            industry_office_id=request.data['head_office_id'],
            crop_cv_id=request.data['crop_id'],
        )
    if IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map_id=industry_office_crop_map_id, is_active=True).exists():
        IndustryOfficeCropProcurementPriceLog.objects.filter(industry_office_crop_map_id=industry_office_crop_map_id, is_active=True).update(
            effective_date=datetime.datetime.now(),
            is_active=False,
            modified_by=request.user
        )
    
    IndustryOfficeCropProcurementPriceLog.objects.create(
        industry_office_crop_map=industry_office_crop_map_id,
        cost=request.data['price'],
        is_active=True,
        from_date=datetime.datetime.now(),
        created_by=request.user,
        modified_by=request.user
    )
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_crop(request):
    data = list(CropCv.objects.all().values())
    return Response(data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_products(request):
    serve_url = '/v1/main/serve/products/list/'
    post_data = request.data
    response_data = get_data_from_micro_service(2, serve_url)
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def serve_publication(request):
    serve_url = '/v1/main/serve/publication/'
    status_code, data = post_data_to_micro_service(2, serve_url, request.data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_user_manual(request):
    data_dict = {'manual': [], 'videos': []}
    user_manual_obj = UsertypeWiseUserManual.objects.filter().order_by('display_ordinal')
    user_manual_list = list(user_manual_obj.values_list('id', 'tamil_manual_url', 'english_manual_url', 'display_name'))
    user_manual_column = ['id', 'tamil_manual_url', 'english_manual_url', 'display_name']
    user_manual_df = pd.DataFrame(user_manual_list, columns=user_manual_column)
    data_dict['manual'] = user_manual_df.to_dict('r')

    # manual videos from youtube
    list_ld = 'PLiK29z7UemiuaDoSQRuUDlzxMr4qGxXj9'
    video_under_play_list_response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?key=' + youtube_api_key + '&playlistId=' + list_ld +'&part=snippet,id&maxResults=20')
    video_under_play_list_response = video_under_play_list_response.json()['items']
    master_list = []
    for video in video_under_play_list_response:
        video_dict = {
            'video_id': video['snippet']['resourceId']['videoId'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'iframe_link': 'https://www.youtube.com/embed/' + video['snippet']['resourceId']['videoId'],
            'thumbnail_list': video['snippet']['thumbnails']['medium']['url'],
            'video_link': 'https://www.youtube.com/watch?v=' + video['snippet']['resourceId']['videoId']
        }
        master_list.append(video_dict)
    data_dict['videos'] = master_list
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def disable_notifications_from_ask_expert(request):
    if NotificatiionLog.objects.filter(user=request.user, recommendation__user_query_id=request.data['id']).exists():
        notification_obj = NotificatiionLog.objects.filter(user=request.user, recommendation__user_query_id=request.data['id'])
        for farmer_notificatin in notification_obj:
            farmer_notificatin.is_sceen = True
            farmer_notificatin.save()
    return Response(data=True, status=status.HTTP_200_OK)


@api_view(['POST'])
def disable_notifications_from_recommendation(request):
    print(request.data)
    if NotificatiionLog.objects.filter(user=request.user, user_query_id=request.data['user_query_id']).exists():
        notification_obj = NotificatiionLog.objects.filter(user=request.user, user_query_id=request.data['user_query_id'])
        for scientist_notificatin in notification_obj:
            scientist_notificatin.is_sceen = True
            scientist_notificatin.save()
    return Response(data=True, status=status.HTTP_200_OK)


@api_view(['POST'])
def clear_notifications(request):
    print(request.data)
    user_id = request.user.id
    purpose = request.data['purpose']
    if NotificatiionLog.objects.filter(user_id=user_id,is_active=True).exists():
        print("inside clear notification !!!")
        if(purpose == 'viewed') :
            notifiction_obj = NotificatiionLog.objects.filter(user_id=user_id, is_sceen=True, is_active=True)
        else:
            notifiction_obj = NotificatiionLog.objects.filter(user_id=user_id, is_active=True)
        for obj in notifiction_obj:
            obj.is_active = False
            print(obj.id)
            obj.save()
    else:
        print("there is no active notifications !!!")
    return Response(data=True, status=status.HTTP_200_OK)