from django.shortcuts import render
import random,string
from django.contrib.auth.decorators import login_required, permission_required
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import shutil
import os
import string
from datetime import datetime, timedelta
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.styles import Border, Side
import math
from openpyxl.utils import get_column_letter
import base64
import pymysql
import multiprocessing
from lims.models import *
import numpy as np
from sqlalchemy import create_engine
import redis,uuid
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import io
from django.http import HttpResponse
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# 指定字体文件的路径
font_path = '/usr/share/fonts/Microsoft-Yahei.ttf'
# 设置中文字体
font = FontProperties(fname=font_path, size=10)

db_host, db_user, db_pass = '172.28.20.100','root','Abc_12345'
MINUSDAYS = -2
ADDDAYS = 2
FORWARDDAYS = -100

def get_adjacent_date(date_str,days):
    # 将日期字符串解析成 datetime 对象
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    delta = timedelta(days=days)
    # 计算日期
    new_date = date_obj + delta
    return new_date.strftime("%Y%m%d")

def query_database(host,user,password,db,query):
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:3306/{db}')
    # 执行 SQL 查询并将结果加载到 DataFrame 中
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df

def row_to_string(row):
    string_parts = [f"{col}='{val}'" for col, val in row.items()]
    return ' and '.join(string_parts)

def runsqlovertables(start_table,end_table,where_df,db_name,deduplication_column):
    # 首先得到范围之内的表
    select_table_name = f'''SELECT table_name 
        FROM INFORMATION_SCHEMA.TABLES
        where table_name between '{start_table}' and '{end_table}'
        and table_schema='{db_name}' '''
    con = pymysql.connect(host=db_host, user=db_user,
                                password=db_pass, database=db_name)
    cursor = con.cursor(cursor=pymysql.cursors.Cursor)
    cursor.execute(select_table_name)
    tables = [table[0] for table in cursor.fetchall()]
    
    
    # 然后构建查询结果的sql语句
    where_df['row_string'] = where_df.apply(row_to_string, axis=1)
    queries = []

    for table in tables:
        for index,row in where_df.iterrows():
            and_part = row['row_string']
            queries.append(f"select * from {table} where {and_part}")
            # print(f"select * from {table} where {and_part}")

    # print(len(queries))

    # muti processes to query data
    pool = multiprocessing.Pool()
    df = pd.DataFrame()

    for query in queries:
        process = pool.apply_async(query_database, (db_host,db_user,db_pass,db_name,query))
        onedf = process.get()
        idx_to_keep = onedf.groupby(['computer_name','dev_unit_chl', 'test_id', 'Test_StartTime', 'EndTime'])[deduplication_column].idxmin()
   
        # 使用这些索引过滤 DataFrame，确保保留所有列的值       
        onedf = onedf.loc[idx_to_keep]
        if len(onedf)>0:
            df = pd.concat([df,onedf], ignore_index=True)
    return df

    


def handlecyclesummary(request):
    # get all the inputs from client
    start_date = request.POST.get('startdate')
    end_date = request.POST.get('enddate')
    db_name = request.POST.get('dbname')
    team_id = request.POST.get('teamid')
    cycle_count = int(request.POST.get('cyclecount'))
    chg_efficiency = float(request.POST.get('chgefficiency'))/100

    MINUSDAYS = int(request.POST.get('fs'))
    ADDDAYS = int(request.POST.get('bs'))
    MINUSDAYS = -MINUSDAYS

    print(start_date, end_date,db_name,team_id,cycle_count,chg_efficiency)
    is_ok=1


    # generate sql statement
    all_computers = list(teamcomputer.objects.filter(
        teamid=team_id).values('computer_name'))
    
    computer_names = [k['computer_name'] for k in all_computers]

    start_table = 'cycle'+start_date
    end_table = 'cycle'+end_date

    select_table_name = f'''SELECT table_name 
        FROM INFORMATION_SCHEMA.TABLES
        where table_name between '{start_table}' and '{end_table}'
        and table_schema='{db_name}' '''
    
    con = pymysql.connect(host=db_host, user=db_user,
                                password=db_pass, database=db_name)
    cursor = con.cursor(cursor=pymysql.cursors.Cursor)
    cursor.execute(select_table_name)

    tables = [table[0] for table in cursor.fetchall()]

    
    where_clause = f''' where upper(computer_name) in ('{"','".join(computer_names)}') '''
    # print(where_clause)
    

    queries = ['SELECT * FROM '+table+where_clause for table in tables]

    # muti processes to query data
    pool = multiprocessing.Pool()
    df = pd.DataFrame()

    for query in queries:
        process = pool.apply_async(query_database, (db_host,db_user,db_pass,db_name,query))
        df = pd.concat([df,process.get()], ignore_index=True)

    if(len(df.to_dict(orient='records')))<1:
        ls_data = {"isok": 0, "errmsg": '无满足条件的记录'}
        return JsonResponse(ls_data)
    # get distinct computer dev_unit_chl test_id
    unique_values_combined = df[['computer_name', 'dev_unit_chl','test_id']].drop_duplicates()
    print(unique_values_combined)

    expand_start_date=get_adjacent_date(start_date,MINUSDAYS)
    expand_end_date = get_adjacent_date(end_date,ADDDAYS)
    print(expand_start_date,expand_end_date)
    start_table='cycle'+expand_start_date
    end_table='cycle'+expand_end_date

    df = runsqlovertables(start_table,end_table,unique_values_combined,db_name,'cycle_id')
    if(len(df.to_dict(orient='records')))<1:
        ls_data = {"isok": 0, "errmsg": '无满足条件的记录'}
        return JsonResponse(ls_data)
    
    print('查询符合条件的前60后5天之后df的长度：',len(df))

    idx_to_keep = df.groupby(['computer_name','dev_unit_chl', 'test_id', 'Test_StartTime', 'EndTime'])['cycle_id'].idxmin()

    
    # 使用这些索引过滤 DataFrame，确保保留所有列的值
    df = df.loc[idx_to_keep]
    print('去重后df的长度：',len(df))

    # 按computer_name,test_id和dev_unit_chl进行分组
    grouped = df.groupby(['computer_name','test_id', 'dev_unit_chl'],as_index=False)

    # 初始化一个空的DataFrame，用于存储符合条件的组
    filtered_df = pd.DataFrame()

    summary_data = {
        '序号':[],
        '计算机名': [],
        '设备单元通道': [],
        'test_id': [],
        '条码':[],
        '最后循环次数':[],
        '最后保持率':[],
        '最后库伦效率':[]
    }
    summary_df = pd.DataFrame(summary_data)
    detail_df = []
    summary_count = 0
    for name, group in grouped:   
        if len(group) >= cycle_count:
            # 检查每个组是否超过一定行，并且前面行的保持率都大于指定值            
            group['保持率'] = (group['discharge_capacity'] / group['discharge_capacity'].iloc[1] ).round(4)
            group['库伦效率'] = (group['discharge_capacity'] / group['charge_capacity'] ).round(4)
            group.fillna(0, inplace=True)
            group.replace([np.inf, -np.inf], 0, inplace=True)
            first_k_rows = group.iloc[2:cycle_count-1]
            all_greater_than_08 = (first_k_rows['保持率'] > chg_efficiency).all()

            # and group.iloc[cycle_count-1]['保持率'] > chg_efficiency:
            # 如果符合条件，则将这个组添加到新的DataFrame中
            if all_greater_than_08:
                print(name,'满足条件')
                filtered_df = pd.concat([filtered_df, group])
                summary_df.loc[len(summary_df)] = [ summary_count,
                                                    group.iloc[0]['computer_name'],
                                                    group.iloc[0]['dev_unit_chl'],
                                                    group.iloc[0]['test_id'],
                                                    group.iloc[0]['barcode'],
                                                    group.iloc[len(group)-1]['cycle_id'],
                                                    group.iloc[len(group)-1]['保持率'],
                                                    group.iloc[len(group)-1]['库伦效率']]
                # group.to_excel('/tmp/'+group.iloc[0]['dev_unit_chl']+'.xlsx')
                detail_df.append(group)
                summary_count += 1

    
    if(len(filtered_df.to_dict(orient='records')))<1:
        ls_data = {"isok": 0, "errmsg": '无满足条件的记录'}
        return JsonResponse(ls_data)
    
    # 根据某个字段排序
    df_sorted = filtered_df.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])
    df_sorted.fillna(0, inplace=True)
    df_sorted.replace([np.inf, -np.inf], 0, inplace=True)

    # 得到所有字段名称
    ls_columns = df_sorted.columns.tolist()

     # 将排序后的 DataFrame 转换回字典列表
    result = df_sorted.to_dict(orient='records')


    # 得到所有字段名称
    ls_columns = summary_df.columns.tolist()

     # 将排序后的 DataFrame 转换回字典列表
    result = summary_df.to_dict(orient='records')

    # 处理detail数据
    result_details=[]
    print('before 画图')
    # print(detail_df)
    for adetail in detail_df:
        adetail = adetail.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])
        # 画图
        plt.clf()  # 清空当前图形绘制区域
        plt.plot(adetail['cycle_id'], adetail['保持率'])
        plt.xlabel('循环圈数', fontproperties=font)
        plt.ylabel('保持率', fontproperties=font)
        plt.title(adetail.iloc[0]['dev_unit_chl'])
        # 将图形保存为图像文件
        buffer = io.BytesIO()
        plt.savefig(buffer, format='jpg')
        buffer.seek(0)
        img=base64.b64encode(buffer.getvalue()).decode()
        # 清空缓冲区
        buffer.truncate(0)


        result_detail=adetail.to_dict(orient='records')
        ls_detail_columns = adetail.columns.tolist()
        detail_response = {'data':result_detail,
                      'total':len(result_detail),
                      'columns':ls_detail_columns,
                      'img':img}
        result_details.append(detail_response)
    
    summary_response = {'data':result,'total': len(
        result),'columns': ls_columns}
    
    print('after 画图')

    # 将result_detail存入redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    # 生成随机的 key
    key = str(uuid.uuid4())
    # 存储数据
    for idx, adf in enumerate(detail_df):
        akey = f'{key}_{idx}'  # 使用递增的键名
        df_json = adf.to_json(orient='records')  # 将 DataFrame 转换为 JSON 字符串
        r.set(akey, df_json)  # 存储 JSON 字符串
        print(akey)
    print(key)
    # 注意这里reesultdatalist是数组
    ls_data = {'summarydata': summary_response, 
               'resultdatalist': result_details,
               'rediskey':key,
                "isok": is_ok}

    # print(ls_data)
    return JsonResponse(ls_data)
    # return HttpResponse(ls_data)

    
@login_required(login_url='/admin/login/') 
def cyclesummary(request):
    context_dict = {'module': 'lims'}
    user_all_permissions = request.user.get_all_permissions()
    all_teams = list(teams.objects.filter(
        teampriv__in=user_all_permissions).values())

    context_dict['teams']=all_teams
    return render(request,'lims/cyclesummary.html',context_dict) 

def cycledetail(request):
    rediskey = request.GET.get('key')
    detailno = request.GET.get('xuhao')

    crate =-100  if request.GET.get('cr') is None else float(request.GET.get('cr', -100))
    keeplow =-100 if request.GET.get('pl') is None else float(request.GET.get('pl', -100))
    print('hello',request.GET.get('pl'))
    keephigh =-100 if request.GET.get('ph') is None else float(request.GET.get('ph')) 
    kulunlow =-100 if request.GET.get('kl') is None else float(request.GET.get('kl')) 
    kulunhigh =-100 if request.GET.get('kh') is None else float(request.GET.get('kh', -100)) 
    basecycle = 1 if request.GET.get('bc') is None else int(request.GET.get('bc', 1)) 
    cyclecount = -100 if request.GET.get('cc') is None else int(request.GET.get('cc', -100)) 
    startdate = '20240101' if request.GET.get('startdate') is None else request.GET.get('startdate') 
    db_name = 'uat' if request.GET.get('db') is None else request.GET.get('db') 
    detail_type = request.GET.get('tp')
    print(rediskey,detailno,crate,keeplow,keephigh,kulunlow,kulunhigh,basecycle,cyclecount)

    context_dict = {'module': 'lims'}

    
    r = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True)
    key = f'{rediskey}_{detailno}'
    print(key)
    

    # 从 Redis 中获取 JSON 字符串
    df_json = r.get(key)

    if df_json:
        
        # 将 JSON 字符串转换为 DataFrame
        df = pd.read_json(df_json, orient='records')
        df = df.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])

        
        if detail_type != ('redraw'):
            # 不是redraw则取下更多结果并存入redis
            startdate = get_adjacent_date(startdate,FORWARDDAYS)
            enddate = '20991231'
            unique_values_combined = df[['computer_name', 'dev_unit_chl','test_id']].drop_duplicates()
            start_table='cycle'+startdate
            end_table='cycle'+enddate
            print('starttable',start_table,'endtable',end_table)
            df = runsqlovertables(start_table,end_table,unique_values_combined,db_name,'cycle_id')
            # 将result_detail存入redis
            r = redis.Redis(host='127.0.0.1', port=6379, db=0)
            # 生成随机的 key
            solokey = str(uuid.uuid4())
            # 存储数据
            akey = f'{solokey}_1'  # 将本次结果单独存入redis
            df_json = df.to_json(orient='records')  # 将 DataFrame 转换为 JSON 字符串
            r.set(akey, df_json)  # 存储 JSON 字符串
            print(akey)
        else:
            solokey=rediskey

        df = df.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])
        if len(df)>basecycle:
            df['保持率'] = (df['discharge_capacity'] / df['discharge_capacity'].iloc[basecycle-1] ).round(4)
            df['库伦效率'] = (df['discharge_capacity'] / df['charge_capacity'] ).round(4)
            df.fillna(0, inplace=True)
            df.replace([np.inf, -np.inf], 0, inplace=True)

        if detail_type == 'barcode':
            df = df.iloc[basecycle-1:cyclecount-1, :]
            df.reset_index(drop=True, inplace=True)
            df['cycle_id'] = df.index + 1
        # 画图
        plt.clf()  # 清空当前图形绘制区域
        print(df['cycle_id'])      

        # 使用Seaborn绘制双 y 轴图
        plt.figure(figsize=(10, 6))
        ax1 = sns.lineplot(x='cycle_id', y='保持率', data=df, marker='o', color='blue', label='保持率')
        ax2 = ax1.twinx()
        sns.lineplot(x='cycle_id', y='库伦效率', data=df, marker='s', color='red', ax=ax2, label='库伦效率')

        # 添加图例
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right', prop=font)

        # 设置标题和标签
        print('hello barcode',df.iloc[0]['barcode'])
        print(df.iloc[0]['dev_unit_chl'])
        print(crate)
        if crate == -100:
            crate == 1
        title = 'barcode:'+df.iloc[0]['barcode']+' 通道:'+df.iloc[0]['dev_unit_chl']+' 倍率:'+str(crate)
        plt.title(title,fontproperties=font)
        ax1.set_ylabel('保持率', fontproperties=font)
        ax2.set_ylabel('库伦效率', fontproperties=font)
        ax1.set_xlabel('循环圈数', fontproperties=font)
        ax2.set_xlabel('循环圈数', fontproperties=font)
       
        if detail_type == 'barcode' or detail_type=='redraw':
            ax1.set_ylim(keeplow,keephigh)
            ax2.set_ylim(kulunlow, kulunhigh)  
             # 设定 x 轴下限为 0
            plt.xlim(left=1)
            # 设置 x 轴刻度为整数
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

        plt.xlabel('循环圈数', fontproperties=font)        

        # 将图形保存为图像文件
        buffer = io.BytesIO()
        plt.savefig(buffer, format='jpg')
        buffer.seek(0)
        img=base64.b64encode(buffer.getvalue()).decode()
        # 清空缓冲区
        buffer.truncate(0)

        # if detail_type != 'redraw':
        if pd.api.types.is_datetime64_any_dtype(df['Test_StartTime']):
            df['Test_StartTime'] = df['Test_StartTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df['EndTime'] = df['EndTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        if pd.api.types.is_datetime64_any_dtype(df['Total_charge_time']):
            df['Total_charge_time'] = df['Total_charge_time'].dt.strftime('%H:%M:%S')
            df['Total_discharge_time'] = df['Total_discharge_time'].dt.strftime('%H:%M:%S')

    result_detail=df.to_dict(orient='records')
    ls_detail_columns = df.columns.tolist()
    response = {'data':result_detail,
                    'total':len(result_detail),
                    'columns':ls_detail_columns,
                    'img':img}
    context_dict['img']=img
    context_dict['response']=response

    context_dict['crate']=crate
    context_dict['keeplow']=keeplow
    context_dict['keephigh']=keephigh
    context_dict['kulunlow']=kulunlow
    context_dict['kulunhigh']=kulunhigh
    context_dict['key']=solokey

      
    return render(request,'lims/cycledetail.html',context_dict) 


@login_required(login_url='/admin/login/')
def cyclebybarcode(request):
    context_dict = {'module': 'lims'}
    
    user_all_permissions = request.user.get_all_permissions()

    all_teams = list(teams.objects.filter(
        teampriv__in=user_all_permissions).values())
    context_dict['teams']=all_teams
    return render(request,'lims/cyclebybarcode.html',context_dict) 
	
	


def handlecyclebarcode(request):
    # get all the inputs from client
    start_date = request.POST.get('startdate')
    end_date = request.POST.get('enddate')
    barcode = request.POST.get('barcode').replace('，', ',').split(',')
    db_name = request.POST.get('dbname')
    team_id = request.POST.get('teamid')
    cyclecount = int(request.POST.get('cyclecount'))
    crate = float(request.POST.get('crate'))

    keeplow = float(request.POST.get('keeplow'))
    keephigh = float(request.POST.get('keephigh'))
    kulunlow = float(request.POST.get('kulunlow'))
    kulunhigh = float(request.POST.get('kulunhigh'))

    basecycle = int(request.POST.get('basecycle'))

    print('here is the lenth of barcode1',len(barcode[0]))
    if len(barcode[0]) < 2:
        ls_data = {"isok": 0, "errmsg": '1无满足条件的记录'}
        return JsonResponse(ls_data)

    print(start_date, barcode,db_name,team_id,cyclecount,
          crate,keeplow,keephigh,kulunlow,kulunhigh,basecycle)
    is_ok=1


    # generate sql statement
    

    start_table = 'cycle'+start_date
    end_table = 'cycle'+end_date
    

    select_table_name = f'''SELECT table_name 
        FROM INFORMATION_SCHEMA.TABLES
        where table_name between '{start_table}' and '{end_table}'
        and table_schema='{db_name}' '''
    
    con = pymysql.connect(host=db_host, user=db_user,
                                password=db_pass, database=db_name)
    cursor = con.cursor(cursor=pymysql.cursors.Cursor)
    cursor.execute(select_table_name)

    tables = [table[0] for table in cursor.fetchall()]

    
    where_clause = f''' where barcode in ('{"','".join(barcode)}') '''
    # print(where_clause)
    

    queries = ['SELECT * FROM '+table+where_clause for table in tables]
    print(queries)
    # muti processes to query data
    pool = multiprocessing.Pool()
    df = pd.DataFrame()

    for query in queries:
        process = pool.apply_async(query_database, (db_host,db_user,db_pass,db_name,query))
        df = pd.concat([df,process.get()], ignore_index=True)

    if(len(df.to_dict(orient='records')))<1:
        ls_data = {"isok": 0, "errmsg": '1无满足条件的记录'}
        return JsonResponse(ls_data)
    
    
    print('查询符合条件df的长度：',len(df))

    idx_to_keep = df.groupby(['computer_name','dev_unit_chl', 'test_id', 'Test_StartTime', 'EndTime'])['cycle_id'].idxmin()

    
    # 使用这些索引过滤 DataFrame，确保保留所有列的值
    df = df.loc[idx_to_keep]
    print('去重后df的长度：',len(df))

    # 按computer_name,test_id和dev_unit_chl进行分组
    grouped = df.groupby(['dev_unit_chl','barcode'],as_index=False)

    # 初始化一个空的DataFrame，用于存储符合条件的组
    filtered_df = pd.DataFrame()

    summary_data = {
        '序号':[],
        '计算机名': [],
        '设备单元通道': [],
        'test_id': [],
        '条码':[],
        '最后循环次数':[],
        '最后保持率':[],
        '最后库伦效率':[]
    }
    summary_df = pd.DataFrame(summary_data)
    detail_df = []
    summary_count = 0
    for name, group in grouped:   
        if len(group)>basecycle:
            group['保持率'] = (group['discharge_capacity'] / group['discharge_capacity'].iloc[basecycle-1] ).round(4)
            group['库伦效率'] = (group['discharge_capacity'] / group['charge_capacity'] ).round(4)
            group.fillna(0, inplace=True)
            group.replace([np.inf, -np.inf], 0, inplace=True)
            
            filtered_df = pd.concat([filtered_df, group])
            summary_df.loc[len(summary_df)] = [ summary_count,
                                                group.iloc[0]['computer_name'],
                                                group.iloc[0]['dev_unit_chl'],
                                                group.iloc[0]['test_id'],
                                                group.iloc[0]['barcode'],
                                                group.iloc[len(group)-1]['cycle_id'],
                                                group.iloc[len(group)-1]['保持率'],
                                                group.iloc[len(group)-1]['库伦效率']]
            # group.to_excel('/tmp/'+group.iloc[0]['dev_unit_chl']+'.xlsx')
            detail_df.append(group)
            summary_count += 1

    
    if(len(filtered_df.to_dict(orient='records')))<1:
        ls_data = {"isok": 0, "errmsg": '2无满足条件的记录'}
        return JsonResponse(ls_data)
    
    # 根据某个字段排序
    df_sorted = filtered_df.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])
    df_sorted.fillna(0, inplace=True)
    df_sorted.replace([np.inf, -np.inf], 0, inplace=True)

    # 得到所有字段名称
    ls_columns = df_sorted.columns.tolist()

     # 将排序后的 DataFrame 转换回字典列表
    result = df_sorted.to_dict(orient='records')


    # 得到所有字段名称
    ls_columns = summary_df.columns.tolist()

     # 将排序后的 DataFrame 转换回字典列表
    result = summary_df.to_dict(orient='records')

    # 处理detail数据
    result_details=[]
    print('before 画图')
    # print(detail_df)
    for adetail in detail_df:
        adetail = adetail.sort_values(by=['computer_name','dev_unit_chl','test_id','cycle_id'])
        # 画图
        plt.clf()  # 清空当前图形绘制区域
        plt.plot(adetail['cycle_id'], adetail['保持率'])
        plt.xlabel('循环圈数', fontproperties=font)
        plt.ylabel('保持率', fontproperties=font)
        plt.title(adetail.iloc[0]['dev_unit_chl'])
        # 将图形保存为图像文件
        buffer = io.BytesIO()
        plt.savefig(buffer, format='jpg')
        buffer.seek(0)
        img=base64.b64encode(buffer.getvalue()).decode()
        # 清空缓冲区
        buffer.truncate(0)


        result_detail=adetail.to_dict(orient='records')
        ls_detail_columns = adetail.columns.tolist()
        detail_response = {'data':result_detail,
                      'total':len(result_detail),
                      'columns':ls_detail_columns,
                      'img':img}
        result_details.append(detail_response)
    
    summary_response = {'data':result,'total': len(
        result),'columns': ls_columns}
    
    print('after 画图')

    # 将result_detail存入redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    # 生成随机的 key
    key = str(uuid.uuid4())
    # 存储数据
    for idx, adf in enumerate(detail_df):
        akey = f'{key}_{idx}'  # 使用递增的键名
        df_json = adf.to_json(orient='records')  # 将 DataFrame 转换为 JSON 字符串
        r.set(akey, df_json)  # 存储 JSON 字符串
        print(akey)
    print(key)
    
    r.set(f'{key}_basecycle',basecycle)
    r.set(f'{key}_crate',crate)
    r.set(f'{key}_keeplow',keeplow)
    r.set(f'{key}_keephigh',keephigh)
    r.set(f'{key}_kulunlow',kulunlow)
    r.set(f'{key}_kulunhigh',kulunhigh)
    r.set(f'{key}_cyclecount',cyclecount)

    # 注意这里reesultdatalist是数组
    ls_data = {'summarydata': summary_response, 
               'resultdatalist': result_details,
               'rediskey':key,
                "isok": is_ok}

    # print(ls_data)
    return JsonResponse(ls_data)
