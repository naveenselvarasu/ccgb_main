from pickletools import float8
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from inputdistri.models import *
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import pandas as pd
from base64 import b64encode, b64decode
# Create your views here.


def get_active_season_id():
    season_obj = Season.objects.get(is_active=True)
    return season_obj.id

@api_view(['GET'])
def serve_harvest_level(request):
    print(request.method)
    values = HarvestLevel.objects.filter().order_by('ordinal').values_list('id', 'harvest_name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_harvest(request):
    print(request.data)
    sowing_id = Sowing.objects.filter(farmer_id=request.data['farmer_id']).order_by('id')[0].id
    harvest = Harvest.objects.create(
        sowing_id=sowing_id,
        date_of_harvest=request.data['date_of_harvest'],
        value=request.data['value'],
        unit_id=request.data['unit_id'],
        nth_harvest_id=request.data['nth_harvest_id']
    )
    return Response(data={}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_weight_loss_percentage(request):
    procurement_values = Procurement.objects.filter(procurement_group__season_id=get_active_season_id()).values_list('id', 'procurement_group__produce_net_weight',
                                                                  'procurement_group__agent__first_name',
                                                                  'procurement_group__agent__last_name',
                                                                  'procurement_group__procurement_date',
                                                                  'ticket_number', 'vehicle_number','str_weight', 'str_weight_unit',
                                                                  'gunnybag_weight', 'moisture', 'other_deduction', 'reason_for_weight_loss')
    procurment_column = ['procurment_id', 'produce_net_weight', 'agent_first_name', 'agent_last_name',
                         'procurement_date', 'ticket_number', 'vehicle_number','str_weight', 'str_weight_unit', 'gunnybag_weight',
                         'moisture', 'other_deduction', 'reason_for_weight_loss']

    procurement_df = pd.DataFrame(list(procurement_values), columns=procurment_column)

    procurement_df['loss'] = ((procurement_df['str_weight'] - procurement_df['produce_net_weight']) / procurement_df['str_weight']) * 100
    procurement_df['loss'] = procurement_df['loss'].astype(float).round(2)
    procurement_df= procurement_df.drop(['procurment_id'], axis=1)
    procurement_df = procurement_df[['agent_first_name','agent_last_name', 'procurement_date', 'ticket_number', 'vehicle_number','produce_net_weight', 'str_weight', 'str_weight_unit',
    'gunnybag_weight', 'moisture', 'other_deduction', 'loss', 'reason_for_weight_loss']]

    procurement_df[['produce_net_weight', 'str_weight', 'str_weight_unit','gunnybag_weight', 'moisture', 'other_deduction', 'loss']] = procurement_df[['produce_net_weight', 'str_weight', 'str_weight_unit','gunnybag_weight', 'moisture', 'other_deduction', 'loss']].astype(float)
    procurement_df = procurement_df.rename(columns={'agent_first_name' : 'Agent First Name','agent_last_name' : 'Agent Last Name', 'procurement_date' : 'Procurement Date', 'ticket_number' : 'Ticket Number', 'vehicle_number': 'Vehicle Number','produce_net_weight' : 'Produce Net Weight', 'str_weight' : 'Str Weight', 'str_weight_unit' : 'Str Weight Unit',
    'gunnybag_weight' : 'Gunnybag Weight', 'moisture' : 'Moisture', 'other_deduction' : 'Other Deduction', 'loss' : 'Loss', 'reason_for_weight_loss': 'Reason for Weight Loss',})

    data = {}
    data['data'] = procurement_df.to_dict('r')

    procurement_df.index += 1
    total = procurement_df.sum(numeric_only=True)
    total.name = 'Total'
    procurement_df = procurement_df.append(total.transpose())

    # initializing excel
    writer = pd.ExcelWriter(str('static/media/') + 'weight_loss_report.xlsx', engine='xlsxwriter')
    # creating excel sheet with name
    procurement_df.to_excel(writer, sheet_name='Sheet1',startrow=1)

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

    # Merge 3 cells.
    worksheet.merge_range('A1:Z1', 'Procurement Weight Loss report', merge_format)

    format1 = workbook.add_format({'num_format': '#,##0.00'})

    # Set the column width and format.
    worksheet.set_column('B:B', 18, format1)
    worksheet.set_column(0, 15, 20)

    # Add a header format.
    header_format = workbook.add_format({
        'fg_color': '#D7E4BC'})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(procurement_df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    writer.save()
    document = {}
    try:
        image_path = str('static/media/') + "weight_loss_report.xlsx"
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data['excel'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=data, status=status.HTTP_200_OK)

