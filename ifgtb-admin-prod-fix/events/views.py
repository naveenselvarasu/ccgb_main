from django.shortcuts import render
from events.models import *
from knowledgebase.models import *
from main.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
import datetime
from datetime import timedelta
import knowledgebase.models as kbm

from collections import defaultdict
import pandas as pd

# image storing
from base64 import b64decode, b64encode
from django.core.files.base import ContentFile
# from instance.views import send_push_notification
from fcm_django.models import FCMDevice
import os
from django.conf import settings

# Create your views here.

@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_latest_news_details_for_portal(request):
    """
    get the latest news details
    """
    print(request.data)

    if 'no_of_news' in request.data:
        no_of_news = request.data['no_of_news']
        print('Requested News for display in numbers ', no_of_news)
        news = News.objects.filter(
            expires_on__gte=datetime.datetime.now()).order_by('-id')[0:no_of_news]

    if 'all_news' in request.data:
        news = News.objects.filter(
            expires_on__gte=datetime.datetime.now()).order_by('-id')

    news_list = list(
        news.values_list('id', 'title', 'description', 'journal', 'news_link', 'publish_from', 'expires_on',
                         'app_alert', 'available_for_guest', 'time_created', 'language', 'is_active'))
    news_column = ['id', 'title', 'description', 'journal', 'news_link', 'publish_from', 'expires_on', 'app_alert',
                   'available_for_guest', 'time_created', 'language', 'is_active']

    news_df = pd.DataFrame(news_list, columns=news_column)
    news_dict = news_df.to_dict('r')

    return Response(news_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_latest_news_details(request):
    """
    get the latest news details
    """
    print(request.data)
    if request.data['app_language'] == 'English':
        language = 'English'
    if request.data['app_language'] == 'தமிழ்':
        language = 'தமிழ்'

    if 'no_of_news' in request.data:
        no_of_news = request.data['no_of_news']
        print('Requested News for display in numbers ', no_of_news)
        news = News.objects.filter(
            expires_on__gte=datetime.datetime.now(), is_active=True).order_by('-id')[0:no_of_news]

    if 'all_news' in request.data:
        news = News.objects.filter(
            expires_on__gte=datetime.datetime.now(), is_active=True).order_by('-id')

    news_list = list(
        news.values_list('id', 'title', 'description', 'journal', 'news_link', 'publish_from', 'expires_on',
                         'app_alert', 'available_for_guest', 'time_created', 'language', 'is_active'))
    news_column = ['id', 'title', 'description', 'journal', 'news_link', 'publish_from', 'expires_on', 'app_alert',
                   'available_for_guest', 'time_created', 'language', 'is_active']

    news_df = pd.DataFrame(news_list, columns=news_column)
    news_dict = news_df.to_dict('r')

    return Response(news_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def show_news(request):
    news_obj = News.objects.get(id=request.data['id'])
    news_obj.is_active = request.data['is_active']
    news_obj.save()
    success_dict = {
        'status': 'Success'
    }
    return Response(success_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def show_event(request):
    news_obj = Event.objects.get(id=request.data['id'])
    news_obj.is_active = request.data['is_active']
    news_obj.save()
    success_dict = {
        'status': 'Success'
    }
    return Response(success_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_active_events(request):
    """
    serve the registered events
    """
    print(request.data)
    today = datetime.datetime.now().date()
    if request.data['app_language'] == 'English':
        language = 'English'
    if request.data['app_language'] == 'தமிழ்':
        language = 'தமிழ்'

    if Event.objects.filter(expires_on__gte=today,is_active=True).exists():
        events = Event.objects.filter(expires_on__gte=today,is_active=True).order_by('date_from')
        event_list = list(
            events.values_list('id', 'title','city','country','inter_city', 'description', 'event_image', 'link', 'date_from', 'date_to', 'time_from',
                               'time_to', 'contact_person', 'contact_number', 'all_day', 'contact_email',
                               'publish_from', 'expires_on', 'state', 'locality', 'district', 'language',
                                'pincode', 'latitude', 'longitude', 'country', 'login_required',
                               'event_type', 'event_type__name', 'is_free', 'app_alert', 'time_created', 'is_active'))

        event_column = ['id', 'title','city','country','inter_city', 'description', 'event_image', 'link', 'date_from', 'date_to', 'time_from',
                        'time_to', 'contact_person', 'contact_number', 'all_day', 'contact_email', 'publish_from',
                        'expires_on', 'state', 'locality', 'district', 'language',
                        'pincode',
                        'latitude', 'longitude', 'country', 'login_required', 'event_type', 'event_type_name',
                        'is_free', 'app_alert', 'time_created', 'is_active']

        event_df = pd.DataFrame(event_list, columns=event_column)
        event_df['event_image'] = event_df.apply(lambda x: encode_image(x), axis=1)
        event_df = event_df.fillna('')

        # for index, row in event_df.iterrows():
        #     if row['event_image'] != None and row['event_image'] != '':
        #         event_image = 'static/media/' + row['event_image']
        #         try:
        #             with open(event_image, "rb") as image_file:
        #                 encode_string = b64encode(image_file.read())
        #                 event_df.at[index, 'event_image'] = encode_string
        #
        #         except Exception as err:
        #             print('----Error--------')
        #             print(err)
        # event_df = event_df.fillna('')
        return Response(data=event_df.to_dict('r'), status=status.HTTP_200_OK)
    else:
        return Response(data=[], status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_active_events_for_portal(request):
    """
    serve the registered events
    """
    print(request.data)
    today = datetime.datetime.now().date()

    if Event.objects.filter(expires_on__gte=today).exists():
        events = Event.objects.filter(expires_on__gte=today).order_by('date_from')
        event_list = list(
            events.values_list('id', 'title','city','country','inter_city', 'description', 'event_image', 'link', 'date_from', 'date_to', 'time_from',
                               'time_to', 'contact_person', 'contact_number', 'all_day', 'contact_email',
                               'publish_from', 'expires_on', 'state', 'locality', 'district', 'language',
                                'pincode', 'latitude', 'longitude', 'country', 'login_required',
                               'event_type', 'event_type__name', 'is_free', 'app_alert', 'time_created', 'is_active', 'base64_type', 'file_name', 'mime_type'))

        event_column = ['id', 'title','city','country','inter_city', 'description', 'event_image', 'link', 'date_from', 'date_to', 'time_from',
                        'time_to', 'contact_person', 'contact_number', 'all_day', 'contact_email', 'publish_from',
                        'expires_on', 'state',  'locality', 'district', 'language', 
                        'pincode',
                        'latitude', 'longitude', 'country', 'login_required', 'event_type', 'event_type_name',
                        'is_free', 'app_alert', 'time_created', 'is_active', 'base64_type', 'file_name', 'mime_type']

        event_df = pd.DataFrame(event_list, columns=event_column)
        event_df = event_df.fillna('')
        event_df['date_from'] = pd.to_datetime(event_df['date_from'], errors='coerce')
        event_df['event_image'] = event_df.apply(lambda x: encode_image(x), axis=1)
        data = event_df.to_dict('r')
        print(data) 
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=[], status=status.HTTP_200_OK)


def encode_image(url):
    print('--------------------------------------------------------------------', url['event_image'])
    if not url['event_image'] == '' or url['event_image'] == None:
        image_path = os.path.join(settings.MEDIA_ROOT + '/' + str(url['event_image']))
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            #         print('data:image/jpeg;base64,' + encoded_image.decode("utf-8"))
            return encoded_image.decode("utf-8")
    else:
        return None


def create_complete_image(encoded_image, file_name=None, mime_type=None):
    print('Convert string to image file(Decode)')
    if file_name == None or file_name == '':
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    if mime_type != None:
        return ContentFile(decoded_image, str(file_name) + '.'+mime_type)
    else:
        return ContentFile(decoded_image, str(file_name) + '.jpeg')


@api_view(['POST'])
@permission_classes((AllowAny,))
def store_new_event(request):
    print(request.data)
    data = request.data['news_details']
    try:
        event_obj = Event(
            # form 1
            title=data['title'],
            description=data['event_description'],
            # form 2
            all_day=data['all_day'],
            date_from=data['date_from'],
            date_to=data['date_to'],
            time_from=data['time_from'],
            time_to=data['time_to'],
            # form 3 
            language=data['language'],
            # form 4
            event_type_id=data['event_type'],
            publish_from=data['event_published_on'],
            is_free=data['is_free'],
            expires_on=data['event_untill'],
            app_alert=True,

            user_created=request.user,
            user_modified=request.user,
        )

        if data['state'] is not None:
            event_obj.state_id = data['state']

        if data['pincode'] is not None:
            event_obj.pincode = data['pincode']
            
        if data['city'] is not None:
            event_obj.city = data['city']
            
        if data['inter_city'] is not None:
            event_obj.inter_city = data['inter_city']
            
        if data['country'] is not None:
            event_obj.country = data['country']
        
        if data['event_website'] is not None:
            event_obj.link = data['event_website']

        if data['contact_person'] is not None:
            event_obj.contact_person = data['contact_person']

        if data['number'] is not None:
            event_obj.contact_number = data['number']

        if data['email'] is not None:
            event_obj.contact_email = data['email']

        if 'pictures' in request.data:
            if request.data['pictures'] != 'undefined':
                complete_image = create_complete_image(request.data['pictures'])
                event_obj.event_image = complete_image

        event_obj.save()

        print('event_saved')
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        print('======================')
        print(e)

@api_view(['POST'])
@permission_classes((AllowAny,))
def store_edit_new_event_portal(request):
    print(request.data)

    data = request.data
    
    try:

        if data['event_id'] == 0 :
            print("inside")
            event_obj = Event(
                    title=data['title'],
                    description=data['event_description'],
                    all_day=data['all_day'],
                    date_from=data['date_from'],
                    date_to=data['date_to'],
                    time_from=data['time_from'],
                    time_to=data['time_to'],
                    language=data['language'],
                    event_type_id=data['event_type'],
                    publish_from=data['event_published_on'],
                    expires_on=data['event_untill'],
                    app_alert=True,
                    user_created=request.user,
                    user_modified=request.user,
                )

            if data['base64_type'] != None or data['base64_type'] != '':
                event_obj.base64_type = data['base64_type']

            if data['mime_type'] != None or data['mime_type'] != '':
                event_obj.mime_type = data['mime_type']

            if data['file_name'] != None or data['file_name'] != '':
                event_obj.file_name = data['file_name']

            if data['state'] is not None:
                event_obj.state = data['state']
            
            if data['district'] is not None:
                event_obj.district = data['district']

            if data['pincode'] is not None:
                event_obj.pincode = data['pincode']
            
            if data['locality'] is not None:
                event_obj.locality = data['locality']
                    
            if data['city'] is not None:
                event_obj.city = data['city']
                
            if data['inter_city'] is not None:
                event_obj.inter_city = data['inter_city']
                    
            if data['country'] is not None:
                event_obj.country = data['country']
            
            if data['link'] is not None:
                event_obj.link = data['link']

            if data['contact_person'] is not None:
                event_obj.contact_person = data['contact_person']

            if data['number'] is not None:
                event_obj.contact_number = data['number']

            if data['email'] is not None:
                event_obj.contact_email = data['email']

            if 'image' in request.data:
                if request.data['image'] != '' and request.data['image'] != None:
                    complete_image = create_complete_image(request.data['image'], request.data['file_name'], request.data['mime_type'])
                    event_obj.event_image = complete_image

            event_obj.save()
        
        else :
            event_obj = Event.objects.get(id=data['event_id'])

            event_obj.title=data['title']
            event_obj.description=data['event_description']
            event_obj.all_day=data['all_day']
            event_obj.date_from=data['date_from']
            event_obj.date_to=data['date_to']
            event_obj.time_from=data['time_from']
            event_obj.time_to=data['time_to']
            event_obj.language=data['language']
            event_obj.event_type_id=data['event_type']
            event_obj.publish_from=data['event_published_on']
            event_obj.is_free=False
            event_obj.expires_on=data['event_untill']
            event_obj.app_alert=True
            event_obj.user_created=request.user
            event_obj.user_modified=request.user
                
            if data['base64_type'] != None or data['base64_type'] != '':
                event_obj.base64_type = data['base64_type']
            
            if data['mime_type'] != None or data['mime_type'] != '':
                event_obj.mime_type = data['mime_type']

            if data['file_name'] != None or data['file_name'] != '':
                event_obj.file_name = data['file_name']

            if data['state'] is not None:
                event_obj.state = data['state']
            
            if data['locality'] is not None:
                event_obj.locality = data['locality']
            
            if data['district'] is not None:
                event_obj.district = data['district']

            if data['pincode'] is not None:
                event_obj.pincode = data['pincode']
                
            if data['city'] is not None:
                event_obj.city = data['city']
                
            if data['inter_city'] is not None:
                event_obj.inter_city = data['inter_city']
                    
            if data['country'] is not None:
                event_obj.country = data['country']
            
            if data['link'] is not None:
                event_obj.link = data['link']

            if data['contact_person'] is not None:
                event_obj.contact_person = data['contact_person']

            if data['number'] is not None:
                event_obj.contact_number = data['number']

            if data['email'] is not None:
                event_obj.contact_email = data['email']

            if 'image' in request.data:
                if request.data['image'] != None and request.data['image'] != '':
                    print('image', request.data['image'])
                    if len(request.data['image'].split('base64,')) == 2:
                        complete_image = create_complete_image(request.data['image'], request.data['file_name'], request.data['mime_type'])
                        event_obj.event_image = complete_image
            event_obj.save()
        print('event_saved')
        data_dict = {
            'status': 'Success'
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        data_dict = {
            'status': 'Not Success'
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_district_data(request):
    states = State.objects.all()
    final_dict = {}
    for state in states:
        final_dict[state.name] = []
        districts = District.objects.filter(state=state)
        for district in districts:
            district_dict = {
                "name": district.name,
                "id": district.id,
                "state_id": state.id
            }
            final_dict[state.name].append(district_dict)
    print(final_dict)
    return Response(final_dict)

@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_language(request):
    language_list = list(kbm.Language.objects.all().values('id', 'name'))
    data_dict = {
        'language_list': language_list
    }
    return Response(data_dict)

@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_district_data_portal(request):
    state_list = list(kbm.State.objects.all().values('id', 'name'))
    district_list = list(kbm.District.objects.all().values('id', 'name'))
    final_dict = {
        'state_list': state_list,
        'district_list': district_list
    }
    print(final_dict)
    return Response(final_dict)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_event_type(request):
    event_types = EventType.objects.all()
    master_list = []
    for event in event_types:
        master_dict = {}
        master_dict['name'] = event.name
        master_dict['id'] = event.id
        master_list.append(master_dict)
    # print(final_dict)
    return Response(master_list)


@api_view(['POST'])
@permission_classes((AllowAny,))
def store_news(request):
    # new news create
    print(request.data)

    if request.data['news_id'] == '0':
        print('new news')
        print(request.data)
        title_obj = News(title=request.data['title'],
                         description=request.data['news_description'],
                         journal=request.data['journal'],
                         news_link=request.data['website_link'],
                         publish_from=request.data['displayed_from'],
                         expires_on=request.data['display_untill'],
                         available_for_guest=request.data['available_for_guests'],
                         language=request.data['language'],
                         is_active=True
                         )
        title_obj.save()
        title = request.data['title']
        body = request.data['news_description']
        owner_ids = FCMDevice.objects.all().values_list('user_id', flat=True)
        # send_push_notification(title, body, owner_ids, {})
        return Response(status=status.HTTP_200_OK)

    if request.data['news_id'] != '0':
        print('update news')
        news_obj = News.objects.filter(id=request.data['news_id']).update(
            title=request.data['title'],
            description=request.data['news_description'],
            journal=request.data['journal'],
            news_link=request.data['website_link'],
            publish_from=request.data['displayed_from'],
            expires_on=request.data['display_untill'],
            available_for_guest=request.data['available_for_guests'],
            language=request.data['language'],
            is_active=True
        )
        print("updated")
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_advertisement(request):
    advertisement_obj = Advertisement.objects.filter(expires_on__gte=datetime.datetime.now())

    advertisement_list = list(advertisement_obj.values_list(
        'id', 'advertisement_image', 'link', 'publish_from', 'expires_on', 'is_active', 'time_created'))

    advertisement_column = ['id', 'advertisement_image', 'link', 'publish_from', 'expires_on', 'is_active',
                            'time_created']

    advertisement_df = pd.DataFrame(advertisement_list, columns=advertisement_column)

    for index, row in advertisement_df.iterrows():
        try:
            image_path = 'static/media/' + row['advertisement_image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                advertisement_df.at[index, 'advertisement_image'] = encoded_image
        except Exception as err:
            print(err)

    return Response(advertisement_df.to_dict('r'))


@api_view(['POST'])
def deactivate_news(request):
    if News.objects.filter(id=request.data['news_id']).exists():
        news = News.objects.get(id=request.data['news_id'])
        news.expires_on = datetime.datetime.now()
        news.save()
        return Response(status=status.HTTP_200_OK)
    else:
        error = {'error': 'News not Available'}
        return Response(data=error, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def deactivate_event(request):
    if Event.objects.filter(id=request.data['event_id']).exists():
        event_obj = Event.objects.get(id=request.data['event_id'])
        event_obj.expires_on = datetime.datetime.now() - timedelta(days=1)
        event_obj.save()
        return Response(status=status.HTTP_200_OK)
    else:
        error = {'error': 'Event not Available'}
        return Response(data=error, status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
def serve_state_district_taluks(request):
    """
    serve state, district and taluks structured by dependent id used for farmer register purpose
    :param request:
    :return:
    """
    states = kbm.State.objects.all().order_by('name')
    districts = kbm.District.objects.all().order_by('id')
    taluks = kbm.Taluk.objects.all().order_by('id')
    blocks = kbm.Block.objects.all().order_by('id')
    revenue_village = kbm.RevenueVillage.objects.all().order_by('id')
    languages = InstanceLanguage.objects.all().order_by('id')

    state_values = states.values_list('id', 'name')

    state_columns = ['id', 'name']
    state_df = pd.DataFrame(list(state_values), columns=state_columns)

    district_values = districts.values_list('id', 'name', 'state')
    district_columns = ['id', 'name', 'state_id']
    district_df = pd.DataFrame(list(district_values), columns=district_columns)

    taluk_values = taluks.values_list('id', 'name', 'district')
    taluk_columns = ['id', 'name', 'district_id']
    taluk_df = pd.DataFrame(list(taluk_values), columns=taluk_columns)

    temp_dict = {'states': [], 'districts': {}, 'taluks': {},
                 'block': {}, 'villages': {}, 'revenue_village': {}}

    temp_dict['states'] = state_df.to_dict('r')

    temp_dict['districts'] = district_df.groupby('state_id').apply(
        lambda x: x.set_index('state_id').to_dict('r')).to_dict()

    temp_dict['taluks'] = taluk_df.groupby('district_id').apply(
        lambda x: x.set_index('district_id').to_dict('r')).to_dict()

    block_values = blocks.values_list('id', 'name', 'district')
    block_columns = ['id', 'name', 'district_id']
    block_df = pd.DataFrame(list(block_values), columns=block_columns)
    temp_dict['block'] = block_df.groupby('district_id').apply(
        lambda x: x.to_dict('r')).to_dict()

    revenue_village_values = revenue_village.values_list('id', 'name', 'block')
    revenue_village_columns = ['id', 'name', 'block_id']
    revenue_village_df = pd.DataFrame(
        list(revenue_village_values), columns=revenue_village_columns)
    temp_dict['revenue_village'] = revenue_village_df.groupby(
        'block_id').apply(lambda x: x.to_dict('r')).to_dict()

    language_list = list(languages.values_list('id', 'name'))
    language_column = ['id', 'name']
    language_df = pd.DataFrame(language_list, columns=language_column)
    temp_dict['languages'] = language_df.to_dict('r')

    return Response(data=temp_dict, status=status.HTTP_200_OK)

