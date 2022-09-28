from asyncio.proactor_events import constants
from requests.sessions import session
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from diagnosis.models import *
from main.models import Clone, CropCv, Scientist, UserProfile
from base64 import b64encode, b64decode
import base64
from django.core.files.base import ContentFile
from main.models import *
from collections import defaultdict
import random
import requests
from django.contrib.auth.hashers import make_password
import pandas as pd
from django.db import transaction
import json
from django.conf import settings
import os
from main.views import *



from django.core.files.base import ContentFile




@api_view(['GET'])
def serve_crop_list(request):
    crop_obj = Clone.objects.all()
    crop_list = list(crop_obj.values_list('id', 'name', 'crop_cv__name'))
    crop_column = ['id', 'name', 'crop_name']
    crop_df = pd.DataFrame(crop_list, columns=crop_column)
    return Response(data=crop_df.to_dict('r'), status=status.HTTP_200_OK)


# media conversrion
def create_complete_voice(encoded_voice, file_name=None):
    print('Convert string to audio file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splitted_audio = encoded_voice.split('base64,')
    decoded_audio = b64decode(splitted_audio)
    return ContentFile(decoded_audio, str(file_name) + '.wav')


def create_complete_image(encoded_image, file_name=None):
    print(encoded_image)
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.jpeg')


@api_view(['POST'])
@transaction.atomic
def register_user_query(request):
    """
        upload the user query and their Images
    """
    sid = transaction.savepoint()
    try:
        print(request.data)
        query_form = request.data['query_from']
        user_query_obj = UserQuery(
            user_id=request.user.id,
            query_type_id=request.data['query_type'],
            requested_date=datetime.datetime.now().date(),
            status_id=1,
            notes=query_form['notes'],
            clone_id=query_form['crop_id'],
            age_in_month=query_form['age_in_month'],
            age_in_year=query_form['age_in_year'],
            area_in_acre=query_form['crop_area'],
            title=query_form['title'],
        )

        if 'query_audio' in request.data:
            voice = request.data['query_audio']
            complete_voice = create_complete_voice(voice)
            user_query_obj.voice = complete_voice
            print("voice")
        user_query_obj.save()


        print('User Query is saved !!!')
        if 'query_image' in request.data:
            if len(request.data['query_image']) != 0:
                print('with in if')
                for image in request.data['query_image']:
                    print('with in for')
                    complete_image = create_complete_image(image)
                    image_obj = UserQueryImage(
                        user_query=user_query_obj,
                        image=complete_image
                    )
                    image_obj.save()
                    print('----Image saved!----')
        if request.data['scientist_id'] != 0:

            scientist_user_id = Scientist.objects.get(id=request.data['scientist_id']).user_profile.user.id
            
            QueryExpertAssignMap.objects.create(
                user_query=user_query_obj, 
                assigned_to_id=scientist_user_id,
                assigned_by_id=1)
            user_query_obj.is_assigned = True
            user_query_obj.save()

            notification_log_obj = NotificatiionLog.objects.create(user_id=scientist_user_id, notification_type_id=1, user_query=user_query_obj, notification_text=user_query_obj.notes)
            send_push_notification(notification_log_obj.notification_type.name, notification_log_obj.notification_text, notification_log_obj, '')
            print("Query Asigned to Scientist!!!")
        # title = 'sample'
        # owner_id = QueryCategoryExpertUserMap.objects.filter(
        #     expert_type_id=request.data['query_type'])
        # owner_ids = []
        # for ids in owner_id:
        #     print('ids', ids.user_id)
        #     owner_ids.append(ids.user_id)
        transaction.savepoint_commit(sid)
    except Exception as e:
        print('=======*******===============')
        print(e)
        transaction.savepoint_rollback(sid)
    return Response(status=status.HTTP_201_CREATED)

def convert_wav_to_base64(file_path):
    print("---------------------------voice path-----------", file_path)
    try:
        file_path = os.path.join(settings.MEDIA_ROOT + '/') + file_path
        with open(file_path, 'rb') as audio_file:
            encoded_audio = b64encode(audio_file.read())
        return encoded_audio
    except Exception as e:
        return ''
    

@api_view(['POST', 'GET'])
def serve_user_query_history(request):
    print(request.user.id)
    user_query = UserQuery.objects.filter(user_id=request.user.id).order_by('-requested_date')
    user_query_ids = user_query.values_list('id', flat=True)
    user_query_list = list(
        user_query.values_list('id', 'requested_date', 'notes', 'query_type__id', 'query_type__name',
                            'status', 'status__name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone__name', 'clone__crop_cv__name', 'voice'))
    user_query_column = ['id', 'requested_date', 'notes', 'query_type', 'query_type__name',
                        'status_id', 'status_name', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'title', 'clone_name', 'crop_name', 'voice_path']
    user_query_df = pd.DataFrame(user_query_list, columns=user_query_column)
    user_query_df = user_query_df.fillna('')
    print(user_query_df)
    if not user_query_df.empty:
        user_query_df['audio'] = user_query_df.apply(lambda x: convert_wav_to_base64(x['voice_path']), axis=1)
        user_query_df['play_audio'] = False
    user_query_images = UserQueryImage.objects.filter(
        user_query_id__in=user_query_ids)
    user_query_image_list = list(
        user_query_images.values_list('user_query', 'user_query__user__first_name', 'image'))
    user_query_image_columns = ['user_query_id', 'user_name', 'image']
    user_query_image_df = pd.DataFrame(
        user_query_image_list, columns=user_query_image_columns)
    for image_index, image_row in user_query_image_df.iterrows():
        try:
            image_path = settings.MEDIA_ROOT + '/' + image_row['image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                user_query_image_df.at[image_index, 'image'] = encoded_image
        except Exception as e:
            user_query_image_df.at[image_index, 'image'] = 0
            pass
    
    user_query_image_df = user_query_image_df.groupby('user_query_id')[
        'image'].apply(list).to_frame().reset_index()
    user_query_df = user_query_df.merge(user_query_image_df, how='left', left_on='id',
                                        right_on='user_query_id')
    user_query_df = user_query_df.fillna(0)
    user_query_df = user_query_df.sort_values('requested_date', ascending=True)

    recomendation_obj = RecommendationLog.objects.filter(user_query_id__in=list(user_query_df['id']))
    recomendation_list = list(recomendation_obj.values_list('id', 'user_query_id', 'notes', 'link', 'status', 'time_created', 'recommended_by__first_name','voice'))
    recomendation_column = ['id', 'user_query_id', 'notes', 'link', 'status_id', 'recommeded_date', 'recommended_by_first_name', 'voice_path']
    recomendation_df = pd.DataFrame(recomendation_list, columns=recomendation_column)
    recomendation_df = recomendation_df.fillna('')
    print(recomendation_df)
    if not recomendation_df.empty:
        recomendation_df['audio'] = recomendation_df.apply(lambda x: convert_wav_to_base64(x['voice_path']), axis=1)
        recomendation_df['play_audio'] = False

    recommendation_image_obj = RecommendationImage.objects.filter(recommendation_id__in=list(recomendation_df['id']))
    recommendation_image_list = list(recommendation_image_obj.values_list('recommendation_id', 'image'))
    recommendation_image_column = ['recommendation_id', 'image']
    recommendation_image_df = pd.DataFrame(recommendation_image_list, columns=recommendation_image_column)


    for image_index, image_row in recommendation_image_df.iterrows():
        try:
            image_path = settings.MEDIA_ROOT + '/'  + image_row['image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                recommendation_image_df.at[image_index, 'image'] = encoded_image
        except Exception as e:
            print(e)
            recommendation_image_df.at[image_index, 'image'] = 0
            pass
    
    recommendation_image_df = recommendation_image_df.groupby('recommendation_id')['image'].apply(list).to_frame().reset_index()

    recomendation_df = recomendation_df.merge(recommendation_image_df, how='left', left_on='id', right_on='recommendation_id')
    recomendation_df = recomendation_df.fillna(0)
    
    recomendation_dict = recomendation_df.groupby('user_query_id').apply(lambda x:x.to_dict('r')).to_dict()
    user_query_df = user_query_df.sort_values(by=['requested_date'], ascending=False)
    data_dict = {
        'user_query': user_query_df.to_dict('r'),
        'recommedation': recomendation_dict
    }

    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_user_query_history_for_scientist(request):
    user_type_id = UserProfile.objects.get(user=request.user).user_type_id
    if user_type_id == 5 and QueryMediatorToggle.objects.filter()[0].is_system_assigned == True:
        user_assigned_query_id_list = QueryExpertAssignMap.objects.filter(assigned_to=request.user)
        query_ids = list(user_assigned_query_id_list.values_list('user_query_id', flat=True))
        user_query = UserQuery.objects.filter(id__in=query_ids).order_by('-requested_date')
    else:
        user_query = UserQuery.objects.all().order_by('-requested_date')


    user_query_ids = user_query.values_list('id', flat=True)
    user_query_list = list(user_query.values_list('id', 'user__id', 'query_type__id', 'query_type__name',
                                                  'is_assigned', 'requested_date', 'notes', 'status', 'status__name', 'voice', 'time_created','area_in_acre', 'age_in_year', 'age_in_month', 'clone__name', 'user__first_name', 'title')) #user__userprofile__ms_farmer_code
    user_query_column = ['user_query_id', 'user_id', 'query_type_id', 'query_type', 'is_assigned',
                         'requested_date', 'notes', 'status_id', 'status_name', 'voice', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month', 'crop_name', 'first_name', 'title']
    user_query_df = pd.DataFrame(user_query_list, columns=user_query_column)
    user_query_df['audio'] = user_query_df.apply(lambda x: convert_wav_to_base64(x['voice']), axis=1)

    user_query_df = user_query_df.fillna(0)

    user_query_images = UserQueryImage.objects.filter(user_query_id__in=user_query_ids)
    user_query_image_list = list(user_query_images.values_list('user_query', 'user_query__user__first_name', 'image'))
    user_query_image_columns = ['user_query_id', 'user_name', 'image']
    user_query_image_df = pd.DataFrame(user_query_image_list, columns=user_query_image_columns)

    

    for image_index, image_row in user_query_image_df.iterrows():
        try:
            print(image_row['image'])
            image_path = settings.MEDIA_ROOT + '/'  + image_row['image']
            print(image_path)
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                user_query_image_df.at[image_index, 'image'] = encoded_image
        except Exception as e:
            print(e)
            user_query_image_df.at[image_index, 'image'] = 0
            pass

    user_query_image_df = user_query_image_df.groupby('user_query_id')['image'].apply(list)
    user_query_df = user_query_df.merge(user_query_image_df, how='left', left_on='user_query_id', right_on='user_query_id')

    
    
    # recommendation_df = recommendation_df.fillna(0)
    # user_query_df = user_query_df.merge(recommendation_df, how='left', left_on='user_query_id', right_on='user_query_id')

    user_query_df = user_query_df.fillna(0)
    
    user_query_df = user_query_df.sort_values(by=['requested_date'], ascending=False)
    
    user_query_df['requested_date'] = user_query_df['requested_date'].astype(str)
    final_dict = {
        'recommedation_list': user_query_df.to_dict('r'),
        'taluk_name': {},
        'pending_list':user_query_df[user_query_df['status_id']==1].to_dict('r'),
    }
    print('wrkig')
    if RecommendationLog.objects.filter(user_query_id__in=user_query_ids).exists():
        # recommendation audio
        recommendation = RecommendationLog.objects.filter(user_query_id__in=user_query_ids)
        recommendation_list = list(recommendation.values_list('id', 'user_query_id', 'voice', 'notes', 'link', 'recommended_by__first_name'))
        recommendation_columns = ['recommendation_id', 'user_query_id', 'voice', 'notes', 'link', 'recommended_by__first_name']
        recommendation_df = pd.DataFrame(recommendation_list, columns=recommendation_columns)
        recommendation_df = recommendation_df.fillna(0)
        recommendation_df['audio'] = recommendation_df.apply(lambda x: convert_wav_to_base64(x['voice']), axis=1)

        #recommendation image
        recommendation_image = RecommendationImage.objects.filter()
        recommendation_image_list = list(recommendation_image.values_list('recommendation_id', 'image'))
        recommendation_image_columns = ['recommendation_id', 'image']
        recommendation_image_df = pd.DataFrame(recommendation_image_list, columns=recommendation_image_columns)
        recommendation_image_df = recommendation_image_df.fillna(0)
        print('wrkig')
        for image_index, image_row in recommendation_image_df.iterrows():
            try:
                print(image_row['image'])
                image_path = settings.MEDIA_ROOT + '/'  + image_row['image']
                print(image_path)
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    recommendation_image_df.at[image_index, 'image'] = encoded_image
            except Exception as e:
                print(e)
                recommendation_image_df.at[image_index, 'image'] = 0
                pass
        
        recommendation_image_df = recommendation_image_df.groupby('recommendation_id')['image'].apply(list)
        recommendation_df = recommendation_df.merge(recommendation_image_df, how='left', left_on='recommendation_id', right_on='recommendation_id')
        recommendation_df =recommendation_df.fillna(0)
        recommendation_df = recommendation_df.groupby('user_query_id').apply(lambda x: x.to_dict('r')).to_frame().reset_index()
        answered_df = user_query_df[user_query_df['status_id']==2]
        print('wrkig')
        answered_df = answered_df.merge(recommendation_df, how='left', left_on='user_query_id', right_on='user_query_id')
        answered_df = answered_df.rename(columns={0: "recommendations"})
        answered_df = answered_df.fillna(0)
        final_dict['answered_list'] = answered_df.to_dict('r')
        print('wrkig')
    else:
        final_dict['answered_list'] = []
    return Response(data=final_dict, status=status.HTTP_200_OK)


def get_refresh_and_access_token(micro_service_id: int):
    base_url = MicroServiceAuthentication.objects.get(micro_service_id=micro_service_id).base_url
    username = 'jamun'
    password = 'jamun'
    r = requests.post(f'{base_url}/v1/main/api/token/', data={'username': username, 'password': password})
    MicroServiceAuthentication.objects.filter(micro_service_id=micro_service_id).update(refresh_token=r.json()['refresh'], access_token=r.json()['access'])



def post_data_to_micro_service(micro_service_id: int, serve_url: str, post_data: json):
    print("inside post")
    micro_service_auth_obj = MicroServiceAuthentication.objects.get(micro_service_id=micro_service_id)
    base_url = micro_service_auth_obj.base_url
    access_token = micro_service_auth_obj.access_token
    url = f'{base_url}{serve_url}'
    headers = {"Authorization": f"Bearer {access_token}"}
    request = requests.post(url, headers=headers, json=post_data)
    if request.status_code == 401:
        get_refresh_and_access_token(micro_service_id)
        responce_data = post_data_to_micro_service(micro_service_id, serve_url, post_data)
        json_output = responce_data[1]
        status_code = responce_data[0]
        return status_code, json_output
    else:
        return request.status_code, request.json()

@api_view(['POST'])
@transaction.atomic
def register_recommendation_from_scientist(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        recommedation_log_obj = RecommendationLog(user_query_id=request.data['user_query_id'],
                                                notes=request.data['note'],
                                                link=request.data['link'],
                                                recommended_by_id=request.user.id,
                                                status_id=1)
        recommedation_log_obj.save()

        user_query_obj = UserQuery.objects.get(id=request.data['user_query_id'])
        user_query_obj.status_id = 2
        user_query_obj.save()

        # Notification log entry for scientist
        existing_notification_obj = NotificatiionLog.objects.filter(user=request.user, user_query_id=user_query_obj.id)
        for obj in existing_notification_obj:
            obj.is_sceen = True
            obj.save()
        notification_log_obj = NotificatiionLog.objects.create(user_id=user_query_obj.user_id, notification_type_id=2, recommendation=recommedation_log_obj, notification_text=recommedation_log_obj.notes)
        send_push_notification(notification_log_obj.notification_type.name, notification_log_obj.notification_text, notification_log_obj, '')
        if 'voice' in request.data:
            voice = request.data['voice']
            complete_voice = create_complete_voice(voice)
            recommedation_log_obj.voice = complete_voice
            recommedation_log_obj.save()
            print('recommendation voice saved 321')

        if len(request.data['images']) != 0:
            if RecommendationImage.objects.filter(recommendation_id=recommedation_log_obj.id).exists():
                RecommendationImage.objects.filter(
                    recommendation_id=recommedation_log_obj.id).delete()
            for image in request.data['images']:
                complete_image = create_complete_image(image)
                image_obj = RecommendationImage(
                    recommendation_id=recommedation_log_obj.id,
                    image=complete_image
                )
                image_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        return Response(data={'status': 'Failure'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def serve_query_history_for_admin(request):
    print(request.data)
    print("serve query is called")
    user_obj = User.objects.all()
    user_type_id = UserProfile.objects.get(user=request.user).user_type_id
    print(user_type_id)
    if user_type_id != 2 and QueryMediatorToggle.objects.filter()[0].is_system_assigned == True:
        user_assigned_query_id_list = QueryExpertAssignMap.objects.filter(
            assigned_to=request.user)
        query_ids = list(user_assigned_query_id_list.values_list(
            'user_query_id', flat=True))
        user_query = UserQuery.objects.filter(
            id__in=query_ids).order_by('-requested_date')
    else:
        user_query = UserQuery.objects.all().order_by('-requested_date')
    user_query_ids = user_query.values_list('id', flat=True)
    user_query_list = list(user_query.values_list('id', 'user__id', 'query_type__id', 'query_type__name',
                                                  'is_assigned', 'user__first_name','requested_date', 'notes', 'status', 'status__name', 'voice', 'time_created','area_in_acre', 'age_in_year', 'age_in_month'))
    user_query_column = ['user_query_id', 'user_id', 'query_type_id', 'query_type', 'is_assigned', 'asked_by',
                         'requested_date', 'notes', 'status_id', 'status_name', 'voice_path', 'time_created', 'area_in_acre', 'age_in_year', 'age_in_month']
    user_query_df = pd.DataFrame(user_query_list, columns=user_query_column)
    user_query_df['voice'] = user_query_df.apply(lambda x: convert_wav_to_base64(x['voice_path']), axis=1)
    user_query_df = user_query_df.fillna(0)

    user_query_images = UserQueryImage.objects.filter(
        user_query_id__in=user_query_ids)
    user_query_image_list = list(user_query_images.values_list(
        'user_query', 'user_query__user__first_name', 'image'))
    user_query_image_columns = ['user_query_id', 'user_name', 'image']
    user_query_image_df = pd.DataFrame(
        user_query_image_list, columns=user_query_image_columns)
    for image_index, image_row in user_query_image_df.iterrows():
        try:
            image_path = settings.MEDIA_ROOT + '/'  + image_row['image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                user_query_image_df.at[image_index, 'image'] = encoded_image
        except Exception as e:
            user_query_image_df.at[image_index, 'image'] = 0
            pass

    user_query_image_df = user_query_image_df.groupby('user_query_id')[
        'image'].apply(list)
    user_query_df = user_query_df.merge(
        user_query_image_df, how='left', left_on='user_query_id', right_on='user_query_id')
    user_query_df = user_query_df.fillna(0)

    user_query_df['requested_date'] = user_query_df['requested_date'].astype(
        str)
    master_dict = {}
    master_dict['all'] = {}
    master_dict['pending'] = {}
    master_dict['answered'] = {}

    for index, row in user_query_df.iterrows():
        query_dict = {}
        recommendation_dict = {}

        # user_pincode = UserProfile.objects.get(user_id=row['user_id']).pincode
        row['requested_date'] = str(row['requested_date'])
        if row['requested_date'] not in master_dict['all']:
            master_dict['all'][row['requested_date']] = {}
        if row['user_query_id'] not in master_dict['all'][row['requested_date']]:
            master_dict['all'][row['requested_date']][row['user_query_id']] = {}
        if 'user_name' not in master_dict['all'][row['requested_date']][row['user_query_id']]:
            print(row['user_query_id'])
            if RecommendationLog.objects.filter(user_query_id=row['user_query_id']).exists():
                answer_given_by = RecommendationLog.objects.filter(user_query_id=row['user_query_id'])[0].recommended_by.first_name
                master_dict['all'][row['requested_date']][row['user_query_id']]['user_name'] = answer_given_by
            else:
                master_dict['all'][row['requested_date']][row['user_query_id']]['user_name'] = ''
        # master_dict['all'][row['requested_date']
        #                    ][row['user_query_id']]['user_pincode'] = user_pincode
        master_dict['all'][row['requested_date']][row['user_query_id']]['requested_date'] = row['requested_date']
        master_dict['all'][row['requested_date']][row['user_query_id']]['asked_by'] = row['asked_by']
        master_dict['all'][row['requested_date']
                           ][row['user_query_id']]['notes'] = row['notes']
        master_dict['all'][row['requested_date']][row['user_query_id']
                                                  ]['time_created'] = row['time_created']
        master_dict['all'][row['requested_date']
                           ][row['user_query_id']]['is_assigned'] = row['is_assigned']
        master_dict['all'][row['requested_date']][row['user_query_id']
                                           ]['area_in_acre'] = row['area_in_acre']
        master_dict['all'][row['requested_date']][row['user_query_id']
                                           ]['age_in_year'] = row['age_in_year']

        master_dict['all'][row['requested_date']][row['user_query_id']
                                           ]['age_in_month'] = row['age_in_month']
        master_dict['all'][row['requested_date']][row['user_query_id']
                                           ]['is_assigned_to_scientist'] = QueryExpertAssignMap.objects.filter(user_query_id=row['user_query_id']).exists()
        

        if row['is_assigned']:
            query_assignment_obj = QueryExpertAssignMap.objects.filter(
                user_query_id=row['user_query_id'])
            query_assignment_list = list(query_assignment_obj.values_list(
                'assigned_to__first_name', flat=True))
            master_dict['all'][row['requested_date']][row['user_query_id']
                                                      ]['assigned_to'] = query_assignment_list

        if 'image' in row:
            master_dict['all'][row['requested_date']
                               ][row['user_query_id']]['image'] = row['image']

        if 'user_query_id' in row:
            master_dict['all'][row['requested_date']
                                ][row['user_query_id']]['user_query_id'] = row['user_query_id']

        if 'voice' in row:
            master_dict['all'][row['requested_date']
                               ][row['user_query_id']]['voice'] = row['voice']
        master_dict['all'][row['requested_date']
                           ][row['user_query_id']]['status_id'] = row['status_id']

        #answered given
        if row['status_id'] == 2 or row['status_id'] == 3:

            if row['requested_date'] not in master_dict['answered']:
                master_dict['answered'][row['requested_date']] = {}
            if row['user_query_id'] not in master_dict['answered'][row['requested_date']]:
                master_dict['answered'][row['requested_date']
                                       ][row['user_query_id']] = {}
            if 'user_name' not in master_dict['answered'][row['requested_date']][row['user_query_id']]:
                print(row['user_query_id'])
                if RecommendationLog.objects.filter(user_query_id=row['user_query_id']).exists():
                    answer_given_by = RecommendationLog.objects.filter(user_query_id=row['user_query_id'])[0].recommended_by.first_name
                    master_dict['answered'][row['requested_date']][row['user_query_id']]['user_name'] = answer_given_by
                else:
                    master_dict['answered'][row['requested_date']][row['user_query_id']]['user_name'] = ''
            # master_dict['answered'][row['requested_date']
            #                        ][row['user_query_id']]['user_pincode'] = user_pincode
            master_dict['answered'][row['requested_date']][row['user_query_id']]['asked_by'] = row['asked_by']
            master_dict['answered'][row['requested_date']][row['user_query_id']]['requested_date'] = row[
                'requested_date']
            master_dict['answered'][row['requested_date']
                                   ][row['user_query_id']]['notes'] = row['notes']
            master_dict['answered'][row['requested_date']
                                   ][row['user_query_id']]['is_assigned'] = row['is_assigned']
            
            if row['is_assigned']:
                query_assignment_obj = QueryExpertAssignMap.objects.filter(
                    user_query_id=row['user_query_id'])
                query_assignment_list = list(query_assignment_obj.values_list(
                    'assigned_to__first_name', flat=True))
                master_dict['answered'][row['requested_date']][row['user_query_id']
                                                              ]['assigned_to'] = query_assignment_list
            if 'image' in row:
                master_dict['answered'][row['requested_date']
                                       ][row['user_query_id']]['image'] = row['image']

            if 'voice' in row:
                master_dict['answered'][row['requested_date']
                                       ][row['user_query_id']]['voice'] = row['voice']
            master_dict['answered'][row['requested_date']
                                   ][row['user_query_id']]['status_id'] = row['status_id']
            

            #recomendation part

            master_dict['all'][row['requested_date']
                               ][row['user_query_id']]['recommendation'] = []
            master_dict['answered'][row['requested_date']
                               ][row['user_query_id']]['recommendation'] = []
            #         recommendation log dataframe
            recommendation_obj = RecommendationLog.objects.filter(
                user_query__id=row['user_query_id'])
            recommendation_values = list(recommendation_obj.values_list('id', 'user_query__id', 'voice', 'notes',
                                                                        'recommended_by__id', 'time_created', 'user_query__requested_date', 'status', 'status__name'))
            recommendation_columns = ['id', 'user_query_id', 'voice', 'notes',
                                      'recommended_by_id', 'time_created', 'requested_date', 'status_id', 'status_name']
            recommendation_df = pd.DataFrame(
                recommendation_values, columns=recommendation_columns)
            #         voice converison
            recommendation_df = recommendation_df.fillna(0)
            recommendation_df['voice'] = settings.MEDIA_ROOT + '/'  + \
                recommendation_df['voice']
            # voice
            for index, recommendation_voice_row in recommendation_df.iterrows():
                try:
                    voice_path = recommendation_voice_row['voice']
                    with open(voice_path, 'rb') as audio_file:
                        recommendation_encoded_voice = b64encode(
                            audio_file.read())
                        recommendation_df.at[index,
                                             'voice'] = recommendation_encoded_voice
                except Exception as e:
                    #         print('e')
                    pass
            for index, recommendation_row in recommendation_df.iterrows():
                recommendation_dict = {}
                recommendation_dict['voice'] = recommendation_row['voice']
                recommendation_dict['image'] = []
                recommendation_dict['id'] = recommendation_row['id']
                recommendation_dict['status_id'] = recommendation_row['status_id']
                recommendation_dict['status_name'] = recommendation_row['status_name']
                recommendation_dict['user_query_id'] = recommendation_row['user_query_id']
                recommendation_dict['recommended_by_id'] = recommendation_row['recommended_by_id']
                recommendation_dict['recommended_by'] = user_obj.get(
                    id=recommendation_row['recommended_by_id']).first_name
                recommendation_dict['notes'] = recommendation_row['notes']
                recommendation_dict['time_created'] = recommendation_row['time_created']
                if recommendation_row['recommended_by_id'] == request.user.id:
                    recommendation_dict['recommendation_is_gieven_by_logged_user'] = True
                if recommendation_row['recommended_by_id'] != request.user.id:
                    if not RecommendationLog.objects.filter(user_query_id=recommendation_row['user_query_id'], recommended_by_id=request.user.id).exists():
                        recommendation_dict['this_user_recommendation_not_available'] = True

                #         recommendation video url
                # if RecommendationVideoUrl.objects.filter(recommendation_id=recommendation_row['id']).exists():
                #     recommendation_video_obj = RecommendationVideoUrl.objects.filter(
                #         recommendation_id=recommendation_row['id'])
                #     recommendation_dict['video_url'] = list(
                #         recommendation_video_obj.values_list('video_url', flat=True))
                # #           recommendation text url
                # if RecommendationTextUrl.objects.filter(recommendation_id=recommendation_row['id']).exists():
                #     recommendation_text_obj = RecommendationTextUrl.objects.filter(
                #         recommendation_id=recommendation_row['id'])
                #     recommendation_dict['text_url'] = list(
                #         recommendation_text_obj.values_list('text_url', flat=True))

                # image
                if RecommendationImage.objects.filter(recommendation_id=recommendation_row['id']).exists():
                    recommendation_dict['image'] = []
                    rec_img_obj = RecommendationImage.objects.filter(
                        recommendation_id=recommendation_row['id'])
                    rec_img_values = list(rec_img_obj.values_list(
                        'id', 'recommendation__id', 'image'))
                    rec_img_columns = ['id', 'recommendation_id', 'image']
                    rec_img_df = pd.DataFrame(
                        rec_img_values, columns=rec_img_columns)

                    for index, rec_row in rec_img_df.iterrows():
                        try:
                            image_path =settings.MEDIA_ROOT + '/'  + rec_row['image']
                            with open(image_path, 'rb') as image_file:
                                encoded_image = b64encode(image_file.read())
                                recommendation_dict['image'].append(
                                    encoded_image)
                        except Exception as e:
                            pass

                master_dict['all'][row['requested_date']][row['user_query_id']]['recommendation'].append(
                    recommendation_dict)
                
                master_dict['answered'][row['requested_date']][row['user_query_id']]['recommendation'].append(
                    recommendation_dict)
                
        if row['status_id'] == 1:
            if row['requested_date'] not in master_dict['pending']:
                master_dict['pending'][row['requested_date']] = {}
            if row['user_query_id'] not in master_dict['pending'][row['requested_date']]:
                master_dict['pending'][row['requested_date']
                                       ][row['user_query_id']] = {}
            master_dict['pending'][row['requested_date']][row['user_query_id']]['user_name'] = ''
            # master_dict['pending'][row['requested_date']
            #                        ][row['user_query_id']]['user_pincode'] = user_pincode
            master_dict['pending'][row['requested_date']][row['user_query_id']]['asked_by'] = row['asked_by']
            master_dict['pending'][row['requested_date']][row['user_query_id']]['requested_date'] = row[
                'requested_date']
            master_dict['pending'][row['requested_date']
                                   ][row['user_query_id']]['notes'] = row['notes']
            master_dict['pending'][row['requested_date']
                                   ][row['user_query_id']]['is_assigned'] = row['is_assigned']
            if row['is_assigned']:
                query_assignment_obj = QueryExpertAssignMap.objects.filter(
                    user_query_id=row['user_query_id'])
                query_assignment_list = list(query_assignment_obj.values_list(
                    'assigned_to__first_name', flat=True))
                master_dict['pending'][row['requested_date']][row['user_query_id']
                                                              ]['assigned_to'] = query_assignment_list
            if 'image' in row:
                master_dict['pending'][row['requested_date']
                                       ][row['user_query_id']]['image'] = row['image']
            if 'user_query_id' in row:
                master_dict['pending'][row['requested_date']
                                    ][row['user_query_id']]['user_query_id'] = row['user_query_id']

            if 'voice' in row:
                master_dict['pending'][row['requested_date']
                                       ][row['user_query_id']]['voice'] = row['voice']
            master_dict['pending'][row['requested_date']
                                   ][row['user_query_id']]['status_id'] = row['status_id']
            master_dict['pending'][row['requested_date']][row['user_query_id']
                                           ]['is_assigned_to_scientist'] = QueryExpertAssignMap.objects.filter(user_query_id=row['user_query_id']).exists()
            
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_recommendation_data_for_update(request):
    print(request.data)
    recommendation_obj = RecommendationLog.objects.filter(
        user_query__id=request.data['query_id'], recommended_by=request.user)
    recommendation_values = list(recommendation_obj.values_list('id', 'user_query__id', 'notes',
                                                                'recommended_by__id', 'time_created', 'user_query__requested_date', 'status', 'status__name'))
    recommendation_columns = ['id', 'user_query_id', 'notes', 'recommended_by_id',
                              'time_created', 'requested_date', 'status_id', 'status_name']
    recommendation_df = pd.DataFrame(
        recommendation_values, columns=recommendation_columns)
    #         voice converison
    recommendation_df = recommendation_df.fillna(0)
    recommendation_dict = {}
    for index, recommendation_row in recommendation_df.iterrows():
        recommendation_dict['id'] = recommendation_row['id']
        recommendation_dict['user_query_id'] = recommendation_row['user_query_id']
        recommendation_dict['recommended_by_id'] = recommendation_row['recommended_by_id']
        recommendation_dict['notes'] = recommendation_row['notes']
        recommendation_dict['time_created'] = recommendation_row['time_created']
        if recommendation_row['recommended_by_id'] == request.user.id:
            recommendation_dict['recommendation_is_gieven_by_logged_user'] = True
        if recommendation_row['recommended_by_id'] != request.user.id:
            if not RecommendationLog.objects.filter(user_query_id=recommendation_row['user_query_id'], recommended_by_id=request.user.id).exists():
                recommendation_dict['this_user_recommendation_not_available'] = True

        # if RecommendationVideoUrl.objects.filter(recommendation_id=recommendation_row['id']).exists():
        #     recommendation_video_obj = RecommendationVideoUrl.objects.filter(
        #         recommendation_id=recommendation_row['id'])
        #     recommendation_dict['video_url'] = list(
        #         recommendation_video_obj.values_list('video_url', flat=True))
        # #           recommendation text url
        # if RecommendationTextUrl.objects.filter(recommendation_id=recommendation_row['id']).exists():
        #     recommendation_text_obj = RecommendationTextUrl.objects.filter(
        #         recommendation_id=recommendation_row['id'])
        #     recommendation_dict['text_url'] = list(
        #         recommendation_text_obj.values_list('text_url', flat=True))
    print(recommendation_dict)
    return Response(recommendation_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def store_recommendations(request):
    print(request.data)
    # updating existing recmmendtionI

    user_type = UserProfile.objects.get(user=request.user).user_type.id
    print('user type id')
    print(user_type)
    if 'recommendation_id' in request.data:
        RecommendationLog.objects.filter(id=request.data['recommendation_id']).update(
            user_query_id=request.data['user_query_id'],
            notes=request.data['recommendation'],
            recommended_by=request.user,
            status_id=1
        )

        # voice
        if 'voice' in request.data:
            voice = request.data['voice']
            complete_voice = create_complete_voice(voice)
            RecommendationLog.objects.filter(
                id=request.data['recommendation_id']).update(voice=complete_voice)

        # if 'video_url' in request.data:
        #     if RecommendationVideoUrl.objects.filter(recommendation_id=request.data['recommendation_id']).exists():
        #         RecommendationVideoUrl.objects.filter(
        #             recommendation_id=request.data['recommendation_id']).delete()
        #     for video in request.data['video_url']:
        #         video_url_obj = RecommendationVideoUrl(
        #             recommendation_id=request.data['recommendation_id'],
        #             video_url=video
        #         )
        #         video_url_obj.save()
        #
        # # text url
        # if 'text_url' in request.data:
        #     if RecommendationTextUrl.objects.filter(recommendation_id=request.data['recommendation_id']).exists():
        #         RecommendationTextUrl.objects.filter(
        #             recommendation_id=request.data['recommendation_id']).delete()
        #     for text in request.data['text_url']:
        #         text_url_obj = RecommendationTextUrl(
        #             recommendation_id=request.data['recommendation_id'],
        #             text_url=text
        #         )
        #         text_url_obj.save()

         # images
        if 'images' in request.data:
            if len(request.data['images']) != 0:
                if RecommendationImage.objects.filter(recommendation_id=request.data['recommendation_id']).exists():
                    RecommendationImage.objects.filter(
                        recommendation_id=request.data['recommendation_id']).delete()
                # for image in request.data['images']:
                complete_image = create_complete_image(request.data['images'])
                image_obj = RecommendationImage(
                    recommendation_id=request.data['recommendation_id'],
                    image=complete_image
                )
                image_obj.save()

    else:
        recommendation_log_obj = RecommendationLog(
            user_query_id=request.data['user_query_id'],
            notes=request.data['recommendation'],
            recommended_by=request.user,
        )

        if user_type == 5:
            recommendation_log_obj.status_id = 2
            UserQuery.objects.filter(
                id=request.data['user_query_id']).update(status_id=3)
            print(UserQuery.objects.filter(id=request.data['user_query_id']))
        else:
            recommendation_log_obj.status_id = 1
            if UserQuery.objects.get(id=request.data['user_query_id']).status_id != 3:
                status_id = UserQuery.objects.filter(
                    id=request.data['user_query_id']).update(status_id=2)
        recommendation_log_obj.save()

        user_query_obj = UserQuery.objects.get(id=request.data['user_query_id'])
        notification_obj = NotificatiionLog.objects.create(user_id=user_query_obj.user_id, notification_type_id=2, recommendation=recommendation_log_obj, notification_text=recommendation_log_obj.notes)

        # voice
        if 'voice' in request.data:
            voice = request.data['voice']
            complete_voice = create_complete_voice(voice)
            recommendation_log_obj.voice = complete_voice
            recommendation_log_obj.save()
            print('recommendation voice saved 733')
        # # video url
        # if 'video_url' in request.data:
        #     for video in request.data['video_url']:
        #         video_url_obj = RecommendationVideoUrl(
        #             recommendation=recommendation_log_obj,
        #             video_url=video
        #         )
        #         video_url_obj.save()
        #
        # # text url
        # if 'text_url' in request.data:
        #     for text in request.data['text_url']:
        #         text_url_obj = RecommendationTextUrl(
        #             recommendation=recommendation_log_obj,
        #             text_url=text
        #         )
        #         text_url_obj.save()

        # images
        print('above image')
        if 'images' in request.data:
            if len(request.data['images']) != 0:
                # for image in request.data['images']:
                complete_image = create_complete_image(request.data['images'])
                image_obj = RecommendationImage(
                    recommendation=recommendation_log_obj,
                    image=complete_image
                )
                image_obj.save()

    print('success')
    return Response(status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
def check_for_pending_queries(request):
    user_type_id = UserProfile.objects.get(user=request.user).user_type_id
    pending_count = 0
    if user_type_id == 4:
        if UserQuery.objects.filter(is_assigned=False).exists():
            pending_count = UserQuery.objects.filter(is_assigned=False).count()
        if QueryExpertAssignMap.objects.filter(assigned_to=request.user).exists():
            query_id_list = list(QueryExpertAssignMap.objects.filter(
                assigned_to=request.user).values_list('id', flat=True))
            pending_count = pending_count + \
                UserQuery.objects.filter(
                    id__in=query_id_list, status_id=1).count()
    if user_type_id == 3:
        if QueryExpertAssignMap.objects.filter(assigned_to=request.user).exists():
            query_id_list = list(QueryExpertAssignMap.objects.filter(
                assigned_to=request.user).values_list('id', flat=True))
            pending_count = pending_count + \
                UserQuery.objects.filter(
                    id__in=query_id_list, status_id=1).count()
    return Response(pending_count, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def approve_recommendation(request):
    print(request.data['recommendation_id'])
    RecommendationLog.objects.filter(
        id=request.data['recommendation_id']).update(status_id=2)
    UserQuery.objects.filter(id=request.data['query_id']).update(status_id=3)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def disapprove_recommendation(request):
    print(request.data['recommendation_id'])
    RecommendationLog.objects.filter(
        id=request.data['recommendation_id']).update(status_id=3)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_expert_list(request):
    expert_list = []
    users = UserProfile.objects.filter(user_type_id__in=[2,5])
    for user in users:
        user_dict = {
            'name': user.user.first_name,
            'id': user.user.id
        }
        expert_list.append(user_dict)
    return Response(expert_list, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def assign_query_to_users(request):
    print(request.data)
    query_id = request.data['query_id']
    user_list = request.data['selected_users']
    for user in user_list:
        if QueryExpertAssignMap.objects.filter(user_query_id=query_id).exists():
            QueryExpertAssignMap.objects.filter(
                user_query_id=query_id).delete()
        query_expert_assign_map = QueryExpertAssignMap(
            user_query_id=query_id,
            assigned_to_id=user,
            assigned_by=request.user
        )
        query_expert_assign_map.save()
        UserQuery.objects.filter(id=query_id).update(is_assigned=True)
    user_name_list = list(User.objects.filter(
        id__in=user_list).values_list('first_name', flat=True))
    return Response(data=user_name_list,  status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def ask_expert_is_system_assigned(request):
    system_assigned = QueryMediatorToggle.objects.filter()[0].is_system_assigned
    return Response(data=system_assigned, status=status.HTTP_200_OK)


def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name))


@api_view(['POST'])
def store_circulars(request):
    base64_file = request.data['file']
    file_name = request.data['file_name'].split('\\')[-1]
    if request.data['circular_id'] == '0':
        print('new circular')
        print(request.data)
        circular_obj = CircularLog(posted_by_id=request.user.id, 
                         title=request.data['title'],
                         description=request.data['description'],
                         file=decode_image(base64_file, file_name),
                         circular_date=request.data['circular_date'],
                         circular_category_id=request.data['circular_type_id'],
                         expiry_date=request.data['expiry_date'],
                         is_active=True
                         )
        circular_obj.save()
        print('created')
        return Response(status=status.HTTP_200_OK)

    if request.data['circular_id'] != '0':
        print('update Circular')
        circular_obj = CircularLog.objects.get(id=request.data['circular_id'])
        circular_category_id=request.data['circular_type_id']
        circular_obj.title=request.data['title']
        circular_obj.description=request.data['description']
        circular_obj.file=decode_image(base64_file, file_name)
        circular_obj.circular_date=request.data['circular_date']
        circular_obj.expiry_date=request.data['expiry_date']
        circular_obj.save()
        print("updated")
        return Response(status=status.HTTP_200_OK)


def encode_imafe(file_path):
    image_path = str(settings.MEDIA_ROOT) + '/' + file_path
    try:
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            return encoded_image
    except Exception as e:
        print(e)
        return ''

def get_file_name(file_path):
    file_name = file_path.split('/')[-1]
    return file_name

@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_circulars(request):
    """
    get the latest circular details
    """
    if CircularLog.objects.filter(expiry_date__gte=datetime.datetime.now()).exists():
        print('have ciruclar')
        circular = CircularLog.objects.filter(expiry_date__gte=datetime.datetime.now()).order_by('-id')

        circular_list = list(circular.values_list('id', 'title', 'description', 'file', 'circular_date', 'expiry_date', 'is_active','posted_by__first_name', 'circular_category_id', 'circular_category__name'))
        circular_column = ['circular_id', 'title', 'description', 'file_path', 'circular_date', 'expiry_date', 'is_active','posted_by', 'circular_category_id', 'category_name']

        circular_df = pd.DataFrame(circular_list, columns=circular_column)
        circular_df['file_name'] = circular_df.apply(lambda x: get_file_name(x['file_path']), axis=1)
        circular_df['file'] = circular_df.apply(lambda x: encode_imafe(x['file_path']), axis=1)
        # data_dict['page'] = page_df.groupby('header_id').apply(lambda x: x.to_dict('r')).to_dict()
        print(circular_df)
        circular_dict = circular_df.groupby('category_name').apply(lambda x: x.to_dict('r')).to_dict()
        print(circular_dict)
    else:
        print('dont have ciruclar')
        circular_dict = []
    return Response(circular_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_circulars_mobile(request):
    """
    get the latest circular details
    """
    if CircularLog.objects.filter(expiry_date__gte=datetime.datetime.now(), is_active=True).exists():
        print('have ciruclar')
        circular = CircularLog.objects.filter(expiry_date__gte=datetime.datetime.now(),is_active=True).order_by('-id')

        circular_list = list(circular.values_list('id', 'title', 'description', 'file', 'circular_date', 'expiry_date', 'is_active','posted_by__first_name', 'circular_category_id', 'circular_category__name'))
        circular_column = ['circular_id', 'title', 'description', 'file_path', 'circular_date', 'expiry_date', 'is_active','posted_by', 'circular_category_id', 'category_name']

        circular_df = pd.DataFrame(circular_list, columns=circular_column)
        circular_df['file_name'] = circular_df.apply(lambda x: get_file_name(x['file_path']), axis=1)
        circular_df['file'] = circular_df.apply(lambda x: encode_imafe(x['file_path']), axis=1)
        # data_dict['page'] = page_df.groupby('header_id').apply(lambda x: x.to_dict('r')).to_dict()
        print(circular_df)
        circular_dict = circular_df.groupby('category_name').apply(lambda x: x.to_dict('r')).to_dict()
        print(circular_dict)
    else:
        print('dont have ciruclar')
        circular_dict = []
    return Response(circular_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def show_circular(request):
    Circular_obj = CircularLog.objects.get(id=request.data['circular_id'])
    Circular_obj.is_active = request.data['is_active']
    Circular_obj.save()
    success_dict = {
        'status': 'Success'
    }
    return Response(success_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_circular_types(request):
    citcular_list = list(CircularCategory.objects.all().values('id', 'name'))
    return Response(data=citcular_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_query_assign_to_scientist(request):
    print(request.data)
    assigned_to = request.data['assigned_to']
    user_query = request.data['user_query']
    assigned_by = request.user.id

    #user query is assignend columns is true
    user_query_obj = UserQuery.objects.get(id=user_query)
    user_query_obj.is_assigned = True
    user_query_obj.save()

    #asign user query to scientist
    QueryExpertAssignMap.objects.filter(user_query_id=user_query).delete()
    print('deleted')
    for item in assigned_to:
        print(item)
        #new entry in notification log.
        if not QueryExpertAssignMap.objects.filter(user_query_id = user_query,assigned_to_id = item).exists():
            if not NotificatiionLog.objects.filter(user_id=item, user_query=user_query_obj).exists():
                notification_log_obj = NotificatiionLog.objects.create(user_id=item, notification_type_id=1, user_query=user_query_obj, notification_text=user_query_obj.notes)
                send_push_notification(notification_log_obj.notification_type.name, notification_log_obj.notification_text, notification_log_obj, '')

        query_expert_assign_map = QueryExpertAssignMap(
                                    user_query_id = user_query,
                                    assigned_to_id = item,
                                    assigned_by_id = assigned_by)
        query_expert_assign_map.save()
    print('Assigned')
    
    return Response(data='success', status=status.HTTP_200_OK)