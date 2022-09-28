from requests.sessions import session
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from diagnosis.models import *
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
from yield_calculator.models import *
from datetime import datetime
from dateutil import relativedelta
from decimal import Decimal



from django.core.files.base import ContentFile

# Create your views here.

@api_view(['GET'])
@permission_classes((AllowAny, ))
def test_url(request):
    return Response(data='data', status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_clone_for_calculation(request):
    clone_obj = CloneYieldEstimationTypeMap.objects.filter()
    clone_list = list(clone_obj.values_list('id', 'clone_id', 'clone__name', 'clone__crop_cv__name', 'yield_estimation_type_id', 'sample_percentage', 'yield_formula_id'))
    clone_column = ['id', 'clone_id', 'clone_name', 'crop_name', 'yield_estimation_type_id', 'sample_percentage', 'yield_formula_id']
    clone_df = pd.DataFrame(clone_list, columns=clone_column)
    estimation_type_wise_clone_dict = clone_df.groupby('yield_estimation_type_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=estimation_type_wise_clone_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_formula_for_clone(request):
    clone_formula_obj = YieldFormula.objects.filter(clone_id=request.data['clone_id'])
    clone_formula_list = list(clone_formula_obj.values_list('clone', 'constant', 'constant_value', 'constant_ordinal'))
    clone_formula_column = ['clone_formula_id', 'constant', 'constant_value', 'constant_ordinal']
    clone_formula_df = pd.DataFrame(clone_formula_list, columns=clone_formula_column)
    group_clone_formula_df = clone_formula_df.groupby('constant_ordinal').apply(lambda x: x.to_dict('r')[0]).to_dict()
    return Response(data=group_clone_formula_df, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny, ))
@transaction.atomic
def calculate_and_record_yield_value(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        form_value = request.data['form_value']
        current_date = datetime.now().date()
        if not form_value['age_in_month'] is None:
            current_date = current_date - relativedelta.relativedelta(months=form_value['age_in_month'])
        if not form_value['age_in_year'] is None:
            current_date = current_date - relativedelta.relativedelta(years=form_value['age_in_year'])

        plantation_yeild_obj = PlantationYield(user_id=request.user.id,
                                            population=form_value['population'],
                                            clone_id=form_value['plantation_crop']['id'],
                                            number_of_trees_to_sample=len(request.data['sample_list']),
                                            area_in_acre=form_value['area_in_acre'],
                                            yield_unit_id=1, #kg
                                            estimated_on=datetime.now(),
                                            estimated_by_id=request.user.id,
                                            )
        if not current_date != datetime.now().date():
            plantation_yeild_obj.date_of_planting = current_date.replace(day=1)
        if not form_value['latitude'] is None:
            plantation_yeild_obj.latitude = form_value['latitude']
            plantation_yeild_obj.longitude = form_value['longitude']
        if form_value['pincode'] != None and form_value['pincode'] != '':
            plantation_yeild_obj.pincode = form_value['pincode']
        plantation_yeild_obj.save()

        total_yield_value = 0
        if form_value['plantation_crop']['yield_formula_id'] == 1: #Quadratic
            yield_formula_obj = YieldFormula.objects.filter(clone_id=form_value['plantation_crop']['id'], yield_formula_id=form_value['plantation_crop']['yield_formula_id'])
            a = yield_formula_obj.get(constant_ordinal=1).constant_value
            b = yield_formula_obj.get(constant_ordinal=2).constant_value
            c = yield_formula_obj.get(constant_ordinal=3).constant_value
            tree_count_to_multiply = 100 / form_value['plantation_crop']['sample_percentage']
            for sample in request.data['sample_list']:
                final_value = 0
                formula = 'ax2+bx+c'
                first_position = a * Decimal(sample['input_value'] ** 2)
                second_position = b * Decimal(sample['input_value'])
                third_position = c
                final_value = first_position + second_position + third_position
                final_value = final_value * Decimal(tree_count_to_multiply)
                
                plantation_sample_obj = PlantationSample(plantation_yield_id=plantation_yeild_obj.id,
                                                            nth_sample=sample['nth_sample'],
                                                            girth=sample['input_value'],
                                                            girth_unit_id=2, #Cm
                                                            calculated_yield=final_value,
                                                            formula_used=formula,
                                                            )
                if not sample['latitude'] is None:
                    plantation_sample_obj.latitude = sample['latitude']
                    plantation_sample_obj.longitude = sample['longitude']
                plantation_sample_obj.save()
                total_yield_value += final_value
        elif form_value['plantation_crop']['yield_formula_id'] == 2: # straight line
            yield_formula_obj = YieldFormula.objects.filter(clone_id=form_value['plantation_crop']['id'], yield_formula_id=form_value['plantation_crop']['yield_formula_id'])
            a = yield_formula_obj.get(constant_ordinal=1).constant_value
            b = yield_formula_obj.get(constant_ordinal=2).constant_value
            tree_count_to_multiply = 100 / form_value['plantation_crop']['sample_percentage']
            for sample in request.data['sample_list']:
                final_value = 0
                formula = 'ax^b'
                final_value = a * Decimal(sample['input_value'] ** b)
                final_value = final_value * Decimal(tree_count_to_multiply)
                
                plantation_sample_obj = PlantationSample(plantation_yield_id=plantation_yeild_obj.id,
                                                            nth_sample=sample['nth_sample'],
                                                            girth=sample['input_value'],
                                                            girth_unit_id=2, #Cm
                                                            calculated_yield=final_value,
                                                            formula_used=formula,
                                                            )
                if not sample['latitude'] is None:
                    plantation_sample_obj.latitude = sample['latitude']
                    plantation_sample_obj.longitude = sample['longitude']
                plantation_sample_obj.save()
                total_yield_value += final_value

        total_yield_value = round(total_yield_value, 2)
        plantation_yeild_obj.estimated_yield = total_yield_value
        plantation_yeild_obj.save()
        transaction.savepoint_commit(sid)
        return Response(data=total_yield_value, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback(sid)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def send_message_via_netfision(purpose, mobile, message):
    payload = {'ClientId': 'c9dc2b72-a38c-4e29-9834-17fe1ef6df3f', 'ApiKey' :'0fa9908c-1e67-4ccb-86fc-2363f7f75839', 'SenderID' : 'KULTIV', 'fl':'0', 'gwid':'2', 'sid':'KULTIV'} 

    headers = {}
    url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'
    payload['msg'] = message
    payload['msisdn'] = mobile
    res = requests.post(url, data=payload, headers=headers)
    print(res)


@api_view(['POST'])
def send_yield_result_message(request):
    mobile_number = request.data['mobile_number']
    message_string = request.data['message_string']
    send_message_via_netfision('Send Yield Result to user', mobile_number, message_string)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register_individual_yield_calculation_value(request):
    form_value = request.data['form_value']
    individual_yield_obj = IndividualYield(clone_id=form_value['plantation_crop']['id'],
                                           girth=form_value['girth'],
                                           girth_unit_id=2, #CM
                                           estimated_yield=form_value['yield_value'],
                                           yield_unit_id=1, #kg
                                           estimated_on=datetime.now())
    if request.data['yield_unit'] == 'tones':
        individual_yield_obj.yield_unit_id = 3 # ton
    individual_yield_obj.save()
    return Response(status=status.HTTP_200_OK)
                                    