import asyncio
from django.http import JsonResponse
from django.views.generic import TemplateView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import json
import pandas as pd
import re
import time
import configparser
from pypinyin import pinyin, Style
from datetime import datetime, date



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



async def process_file(file):
    # 模拟处理文件的过程，每一行处理可能需要几秒钟
    for line in file:
        await asyncio.sleep(2)  # 模拟处理每一行需要 2 秒
        yield line.upper()  # 在实际应用中，这里可以进行实际的处理

async def send_result_to_frontend(channel_name, result):
    channel_layer = get_channel_layer()
    await channel_layer.send(channel_name, {
        'type': 'send_message',
        'message': result,
    })

async def handle_file_upload(file, channel_name):
    async for line in process_file(file):
        await send_result_to_frontend(channel_name, line)


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
    if request.method == 'POST' and request.FILES.get('file'):
        filename = request.FILES['file']
        print(filename)
        pattern = r"\d{4}年\d+月"
        yearmonth=re.findall(pattern, filename)[0]

        all_messages,all_names = processfile(filename,yearmonth)
        for message in all_messages:
            send_wechat_message(corpID, agentID, corpSecret, toUser, message)
            time.sleep(2.3)
            send_result_to_frontend(channel_name, message)
        
        channel_name = request.POST.get('channel_name')


        
        return JsonResponse({'status': 'processing'})
    return JsonResponse({'status': 'error', 'message': 'No file uploaded or invalid request'})
