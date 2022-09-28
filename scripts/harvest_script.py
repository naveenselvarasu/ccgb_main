from instance.models import *
from inputdistri.models import *
import datetime
import pandas as pd
import numpy as np
from inputdistri.models import *
from decimal import *
from django.db.models import Sum
from collections import defaultdict, OrderedDict, Counter
import pandas as pd
import datetime
from pytz import timezone


def test(args):
    f = open("../guru99.txt", "w+")
    for i in range(10):
        f.write("This is line %d\r\n" % (i + 1))
    f.close()

season_id=Season.objects.get(is_active=True).id

def harvest_range_report():
    t1 = datetime.datetime.now()
    print('-----script started at : {} -----'.format(t1))
    harvest_values = Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).order_by('sowing_id','date_of_harvest').values_list(
        'sowing_id', 'sowing__farmer_id', 'date_of_harvest', 'value', 'unit__name', 'sowing__sowing_date','sowing__farmer__aadhaar_number', 'sowing__farmer__village__name','sowing__area_calculated_via_geo_fencing','sowing__water_source__name')
    harvest_columns = ['sowing_id', 'farmer_id', 'date_of_harvest', 'value', 'unit', 'sowing_date', 'farmer_aadhaar_number','farmer_village','area_calculated_via_geo_fencing','water_source']
    harvest_df = pd.DataFrame(list(harvest_values), columns=harvest_columns)

    harvest_df['harvest_days'] = (harvest_df['date_of_harvest'] - harvest_df['sowing_date']).dt.days
    print('harvest df created')
    harvest_days_group = {
        1: {'min': 0, 'max': 61},
        2: {'min': 62, 'max': 68},
        3: {'min': 69, 'max': 75},
        4: {'min': 76, 'max': 82},
        5: {'min': 83, 'max': 89},
        6: {'min': 90, 'max': 96},
        7: {'min': 97, 'max': 103},
        8: {'min': 104, 'max': 110},
        9: {'min': 111, 'max': 117},
        10: {'min': 118, 'max': 200},
    }

    harvest_count_dict = {
        1: ('First Harvest Date', '1st Kg'),
        2: ('2nd Harvest Date', '2nd Kg'),
        3: ('3rd Harvest Date', '3rd Kg'),
        4: ('4th Harvest Date', '4th Kg'),
        5: ('5th Harvest Date', '5th Kg'),
        6: ('6th Harvest Date', '6th Kg'),
        7: ('7th Harvest Date', '7th Kg'),
        8: ('8th Harvest Date', '8th Kg'),
        9: ('9th Harvest Date', '9th Kg'),
        10: ('10th Harvest Date', '10th Kg'),
    }

    harvest_df = harvest_df.assign(**{'harvest_count': None})
    for i in harvest_days_group:
        harvest_df.loc[(harvest_df['harvest_days'] >= harvest_days_group[i]['min']) & (harvest_df['harvest_days'] <= harvest_days_group[i]['max']), 'harvest_count'] = i
    for i in harvest_count_dict:
        harvest_df[harvest_count_dict[i][1]] = 0
        harvest_df[harvest_count_dict[i][0]] = 0
    print('created new fields')
    for sowing_id in harvest_df['sowing_id'].unique():
        sowing_based_harvest_df = harvest_df[harvest_df['sowing_id']==sowing_id]
        har_count_based_sowing = sowing_based_harvest_df.groupby("harvest_count")["value"].sum().to_dict()
        for harvest_count in har_count_based_sowing:
            harvest_df.loc[harvest_df['sowing_id'] == sowing_id, harvest_count_dict[harvest_count][1]] = har_count_based_sowing[harvest_count]
            min_date = harvest_df[(harvest_df['sowing_id'] == sowing_id) & (harvest_df['harvest_count'] == harvest_count)].date_of_harvest.min()
            harvest_df.loc[harvest_df['sowing_id'] == sowing_id, harvest_count_dict[harvest_count][0]] = min_date

    print('all the sowing values calculated and filled in fields')
    harvest_df = harvest_df.drop_duplicates('sowing_id')
    farmer_values = Farmer.objects.filter(id__in=harvest_df['farmer_id']).values_list('id', 'first_name', 'last_name','code')
    farmer_columns = ['id', 'farmer_first_name', 'farmer_last_name', 'farmer_code']
    farmer_df = pd.DataFrame(list(farmer_values), columns=farmer_columns)
    agent_values = AgentFarmerMap.objects.filter(farmer__farmer_id__in=harvest_df['farmer_id'], farmer__season_id=season_id).values_list('farmer__farmer_id', 'agent_id', 'agent__first_name', 'agent__last_name')
    agent_columns = ['farmer_id', 'agent_id', 'agent_first_name', 'agent_last_name']

    print('created farmer df for farmer details')

    agent_df = pd.DataFrame(list(agent_values), columns=agent_columns)
    harvest_df = harvest_df.merge(farmer_df, how='left', left_on='farmer_id', right_on='id').merge(agent_df, how='left',left_on='farmer_id',right_on='farmer_id')
    harvest_df = harvest_df.fillna(0)

    print('merged farmer df with harvest df')

    harvest_table_list = list(Harvest.objects.filter(sowing__cultivation_phase_id=2, sowing__season_id=season_id).values_list( "sowing__farmer__code", "sowing__farmer__id", "sowing__farmer__first_name", "sowing__farmer__last_name", "sowing__season__name", "value", "date_of_harvest", "sowing__area", "sowing__farmer__cluster__name",))
    column_list = [ "farmer_code", "farmer_id", "farmer_first_name", "farmer_last_name", "season", "yeald", "date_of_harvest", "tp_area", "cluster_name",]
    harvest_data_frame = pd.DataFrame(harvest_table_list, columns=column_list)

    # agent_data
    agent_farmer_list = list(AgentFarmerMap.objects.filter(farmer__farmer__code__in=harvest_data_frame["farmer_code"], farmer__season_id=season_id).values_list("farmer__seasonal_farmer_code", "agent__first_name"))
    agent_farmer_columns = ["farmer_code", "agent_name"]
    agent_farmer_df = pd.DataFrame(agent_farmer_list, columns=agent_farmer_columns)

    # supervisor_data
    supervisor_farmer_list = list(UserFarmerMap.objects.filter(farmer__farmer__code__in=harvest_data_frame["farmer_code"], farmer__season_id=season_id).values_list("farmer__farmer__code", "officer__username"))
    supervisor_farmer_colums = ["farmer_code", "supervisor_name"]
    supervisor_farmer_df = pd.DataFrame(supervisor_farmer_list, columns=supervisor_farmer_colums)

    # merged_data
    farmer_agent_map_df = pd.merge(harvest_data_frame,agent_farmer_df,left_on="farmer_code",right_on="farmer_code")
    supervisor_fatmer_agent_map_df = pd.merge(farmer_agent_map_df, supervisor_farmer_df, left_on="farmer_code", right_on="farmer_code")

    # sum yeald and find last harvest date finally merge with supervisor_fatmer_agent_map_df
    grouped_df = (supervisor_fatmer_agent_map_df.groupby(["farmer_code"]).agg({"yeald": "sum", "date_of_harvest": "max"}).rename(columns={"yeald": "total_yeild", "date_of_harvest": "last_harvest_date"}))
    final_supervisor_fatmer_agent_map_df = pd.merge(supervisor_fatmer_agent_map_df,grouped_df,left_on="farmer_code",right_index=True,)
    final_supervisor_fatmer_agent_map_df = final_supervisor_fatmer_agent_map_df.drop(columns=["yeald", "date_of_harvest"])
    final_supervisor_fatmer_agent_map_df = (final_supervisor_fatmer_agent_map_df.drop_duplicates())

    print('final consolidated df created')
    # final_df
    cons_df = final_supervisor_fatmer_agent_map_df.reindex(columns=["farmer_id","cluster_name","last_harvest_date","tp_area","total_yeild","supervisor_name"])

    harvest_df = harvest_df.fillna(0)
    harvest_df['total'] = harvest_df['1st Kg'] + harvest_df['2nd Kg'] + harvest_df['3rd Kg']+ harvest_df['4th Kg']+ harvest_df['5th Kg']+ harvest_df['6th Kg']+ harvest_df['7th Kg']+ harvest_df['8th Kg']+ harvest_df['9th Kg']+ harvest_df['10th Kg']
    df = pd.merge(harvest_df, cons_df, left_on="farmer_id", right_on="farmer_id", how="left")
    df.drop_duplicates(subset="farmer_id", keep="first", inplace=True)
    df = df.drop(['sowing_id', 'farmer_id', 'unit', 'value', 'date_of_harvest'], axis=1)
    df = df.fillna(0)
    df["avg_yield_per_acre"] = round(df['total_yeild']/df['tp_area'],2)
    writer = pd.ExcelWriter(str('/opt/bin/ccgb/ccgb_admin/static/media/') + 'harvest_wise_reports.xlsx', engine='xlsxwriter')
    # writer = pd.ExcelWriter(str("static/media/") + 'harvest_wise_reports.xlsx', engine='xlsxwriter')

    # creating excel sheet with name
    df1 = df[df['total'] == df['total_yeild']]
    df1['S.No'] = range(1, 1 + len(df1))
    df1 = df1[['S.No', 'supervisor_name','agent_first_name', 'agent_last_name','farmer_first_name', 'farmer_last_name', 'farmer_code', 'farmer_aadhaar_number', 'farmer_village',
            'First Harvest Date', '1st Kg','2nd Harvest Date', '2nd Kg', '3rd Harvest Date', '3rd Kg', '4th Harvest Date', '4th Kg',
            '5th Harvest Date', '5th Kg','6th Harvest Date', '6th Kg', '7th Harvest Date', '7th Kg', '8th Harvest Date', '8th Kg',
            '9th Harvest Date', '9th Kg', '10th Harvest Date', '10th Kg', 'total', 'tp_area','total_yeild', 'avg_yield_per_acre']]
    df1.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1)
    print('correct harvest filter created')

    df2 = df[df['total'] != df['total_yeild']]
    df2['S.No'] = range(1, 1 + len(df2))
    df2 = df2[['S.No', 'supervisor_name','agent_first_name', 'agent_last_name','farmer_first_name', 'farmer_last_name', 'farmer_code', 'farmer_aadhaar_number', 'farmer_village',
            'First Harvest Date', '1st Kg', '2nd Harvest Date', '2nd Kg', '3rd Harvest Date', '3rd Kg', '4th Harvest Date', '4th Kg', '5th Harvest Date', '5th Kg','6th Harvest Date',
            '6th Kg', '7th Harvest Date', '7th Kg', '8th Harvest Date', '8th Kg','9th Harvest Date', '9th Kg','10th Harvest Date', '10th Kg', 'total', 'tp_area', 'total_yeild','avg_yield_per_acre']]
    df2.to_excel(writer, sheet_name='Sheet2', index=False, startrow=1)
    # df.insert(1, 'S.no', range(1, 1 + len(df)))
    print('incorrect harvest filter created')
    # assigning that sheet to obj
    workbook = writer.book
    worksheet1 = writer.sheets['Sheet1']
    worksheet2 = writer.sheets['Sheet2']
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

    # Merge 3 cells.
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    current_time = now_asia.strftime("%b %d %Y %H:%M:%S")

    name = 'Harvest Range wise report' + ' (Updated on: ' + str(current_time) +')'
    worksheet1.merge_range('A1:AG1', name, merge_format)
    worksheet2.merge_range('A1:AG1', 'Late harvest data (some entries will not be included for these entries)', merge_format)
    format1 = workbook.add_format({'num_format': '#,##0.00'})

    # Set the column width and format.
    worksheet1.set_column('B:B', 18, format1)
    worksheet1.set_column(0, 32, 20)

    # Set the column width and format.
    worksheet2.set_column('B:B', 18, format1)
    worksheet2.set_column(0, 32, 20)

    # Add a header format.
    header_format = workbook.add_format({'fg_color': '#D7E4BC'})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df1.columns.values):
        worksheet1.write(0, col_num + 1, value, header_format)

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df2.columns.values):
        worksheet2.write(0, col_num + 1, value, header_format)

    writer.save()
    print('excel generated and stored')
    t2 = datetime.datetime.now()
    print('script completed with duration of : {}'.format(t2-t1))


def run(*args):
    harvest_range_report()
