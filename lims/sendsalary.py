import requests
import json
import pandas as pd
import re
import time
import configparser
from pypinyin import pinyin, Style
from datetime import datetime, date
from django.shortcuts import render
import random,string
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import shutil
import os
import random
import string
from datetime import datetime
import openpyxl
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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.shortcuts import redirect
import redis,uuid

def get_pinyin(word):
    # 将汉字转换为拼音，默认使用带声调的拼音风格
    pinyin_result = pinyin(word, style=Style.NORMAL)

    # 将列表中的拼音连接成字符串
    pinyin_str = ''.join([item[0] for item in pinyin_result])

    return pinyin_str

def send_wechat_message(corpID, agentID, corpSecret, toUser, markdown_table):
    # 获取 Access Token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpID}&corpsecret={corpSecret}"
    token_response = requests.get(token_url)
    access_token = token_response.json().get("access_token", "")
    print('access_token is:',access_token)

    # 发送文本消息的 API
    message_api_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

    

    message_content = {
        "touser": toUser,
        "msgtype": "markdown",
        "agentid": agentID,
        "markdown": {
            "content": markdown_table,
        }
    }

    # 发送消息
    response = requests.post(message_api_url, data=json.dumps(message_content, ensure_ascii=False).encode('utf-8'))
    result = response.json()

    # 输出发送结果
    print(result)

def processfile(excel_file,yearmonth):    
    df = pd.read_excel(excel_file,skiprows=1, header=None)
    # 获取前两行作为表头
    header_rows = df.iloc[:2]
    header_rows = header_rows.fillna(method='ffill', axis=0)
    header_rows = header_rows.fillna(method='ffill', axis=1)
    print(header_rows)
    df.iloc[:2]=header_rows
    df=df.fillna(0)
   


    markdown_messages = []
    all_names = []
    # 遍历每一行数据
    for rowindex, row in df.iterrows():
        # 遍历每一列数据
        markdown_table = f"#### 您{yearmonth}工资明细如下："
        preivous_level1 = 'empty'
        if rowindex < 2 or row[1]==0 :
            continue
        is_level2=0
        for colindex,value in enumerate(row):
            df.iloc[0,colindex] = df.iloc[0,colindex].replace("\n", "")
            df.iloc[1,colindex] = df.iloc[1,colindex].replace("\n", "")
            col_message=''
            if df.iloc[0,colindex]=='序号':
                continue
            if preivous_level1!=df.iloc[0,colindex]:
                preivous_level1 = df.iloc[0,colindex]
                if is_level2==1:
                    col_message = '\n'+col_message
                    is_level2=0
                col_message = col_message + f'\n> #### {df.iloc[0,colindex]}:'                
            if df.iloc[0,colindex]==df.iloc[1,colindex]:
                if type(value) is date:
                    # 格式化日期，去掉时间部分
                    value = value.strftime('%Y-%m-%d')
                if pd.notnull(value) and type(value) is float:
                    value = round(value,2)
                col_message = col_message + f"{value}"
                # col_message = col_message + f"<font color='warning'>{value}</font>"                
            else:
                if type(value) is date:
                    # 格式化日期，去掉时间部分
                    value = value.strftime('%Y-%m-%d')
                if pd.notnull(value) and type(value) is float:
                    value = round(value,2)
                col_message = col_message + f"\n>> {df.iloc[1,colindex]}:{value}"
                # col_message = col_message + f"\n>> {df.iloc[1,colindex]}:<font color='warning'>{value}</font>"
                is_level2=1
            if df.iloc[1,colindex]=='姓名':
                all_names.append(value)
            markdown_table += col_message

        # print(markdown_table)
        # print(rowindex,'*'*100)
        markdown_messages.append(markdown_table)
    return markdown_messages,all_names
        
def hangdlesalary(request):
   
    toUser = request.POST.get('touser')

    if request.method == 'POST' and request.FILES.getlist('files'):
        afile = request.FILES.getlist('files')[0]

    file_content = afile.read()
    with open('/tmp/'+afile.name,'wb') as destination_file:
        destination_file.write(file_content)

    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read('/data/django/xjny/lims/settings.ini')

    # 获取配置信息
    corpID = config.get('corp', 'corpID')
    agentID = config.get('corp', 'agentID')
    corpSecret = config.get('corp', 'corpSecret')

    # 读取JSON文件
    with open('/data/django/xjny/lims/nameid.json', 'r',encoding='utf-8') as file:
        namelist = json.load(file)
    
    print(namelist.keys())
    
    filename = afile.name 
    pattern = r"\d{4}年\d+月"
    yearmonth=re.findall(pattern, filename)[0]


    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    all_messages,all_names = processfile(afile,yearmonth)
    for message in all_messages:
        send_wechat_message(corpID, agentID, corpSecret, toUser, message)
        time.sleep(1.3)

    return_message = f'所有信息均已发送到{toUser}的企业微信，请检查一下内容是否正确，如果正确，则请点击send发送到每位员工。'

     # 将result_detail存入redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    # 生成随机的 key
    message_key = str(uuid.uuid4())
    name_key = str(uuid.uuid4())
    print('all_names are:',all_names)
    json_all_messages = json.dumps(all_messages)
    json_all_names = json.dumps(all_names)

    r.set(message_key,json_all_messages)
    r.set(name_key,json_all_names)

    # 注意这里reesultdatalist是数组
    ls_data = {'return_message': return_message, 
               'message_key':message_key,
               "name_key":name_key,
               "yearmonth":yearmonth,
                "isok": 1}

    # print(ls_data)
    return JsonResponse(ls_data)

def sendtoeachuser(request):
    # get all the inputs from client    
    message_key = request.POST.get('message_key')
    name_key = request.POST.get('name_key')
    yearmonth = request.POST.get('yearmonth')

    # print(message_key,name_key,yearmonth)

    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read('/data/django/xjny/lims/settings.ini')

    # 获取配置信息
    corpID = config.get('corp', 'corpID')
    agentID = config.get('corp', 'agentID')
    corpSecret = config.get('corp', 'corpSecret')


    # 读取JSON文件
    with open('/data/django/xjny/lims/nameid.json', 'r',encoding='utf-8') as file:
        namelist = json.load(file)


    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    json_all_messages = r.get(message_key)
    json_all_names = r.get(name_key)

    all_messages = json.loads(json_all_messages)
    all_names = json.loads(json_all_names)
    print(all_messages)
    print(all_names)

    for message_i,message in enumerate(all_messages):
        if all_names[message_i] in namelist.keys():
            eachUser = namelist[all_names[message_i] ]
        else:
            eachUser = get_pinyin(all_names[message_i])            
        print(message_i,eachUser)
        send_wechat_message(corpID, agentID, corpSecret, eachUser, message)
        time.sleep(1.3)
    
    return_message = f'{yearmonth}工资条发送完毕，一共{len(all_messages)}条，谢谢！'
    
    ls_data = {'return_message': return_message, 
                "isok": 1}

    # print(ls_data)
    return JsonResponse(ls_data)