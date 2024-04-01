import mysql.connector
import requests
import json
import pandas as pd
import re
import time
import configparser
from pypinyin import pinyin, Style
from datetime import datetime, date,timedelta
from django.forms.models import model_to_dict

# 连接到 MySQL 数据库
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Abc_12345',
    database='xjny'
)

# 创建一个游标对象
cursor = conn.cursor()

def get_pinyin(word):
    # 将汉字转换为拼音，默认使用带声调的拼音风格
    pinyin_result = pinyin(word, style=Style.NORMAL)

    # 将列表中的拼音连接成字符串
    pinyin_str = ''.join([item[0] for item in pinyin_result])

    return pinyin_str

def get_sp_list(corpID, corpSecret):
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpID}&corpsecret={corpSecret}"
    token_response = requests.get(token_url)
    access_token = token_response.json().get("access_token", "")

    # 得到当前时间
    now = datetime.now()
    timestamp = int(time.mktime(now.timetuple()))

    # 得到30天前的时间
    dt_object_minus_30_days = now - timedelta(days=30)
    timestamp_30 = int(time.mktime(dt_object_minus_30_days.timetuple()))

    print(timestamp,timestamp_30)

    # 获取流程list的API
    message_api_url = f"https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovalinfo?access_token={access_token}"
    message_content = {
        "starttime" : timestamp_30,
        "endtime" : timestamp,
        "new_cursor" : "" ,
        "size" : 200 ,
        "filters" : [
            {
                "key": "template_id",
                "value": "3WLtykNqdAcWRngEpnMwt66g3EJUtRA8Wqfse4f4"
            }    
        ]
    }

    # 获取30天内所有的申请单
    response = requests.post(message_api_url, data=json.dumps(message_content, ensure_ascii=False).encode('utf-8'))
    result = response.json()
    print(print(json.dumps(result, indent=4)))
    return(result['sp_no_list'])



def get_sp_detail(corpID, corpSecret,sp_no):
    # 获取 Access Token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpID}&corpsecret={corpSecret}"
    token_response = requests.get(token_url)
    access_token = token_response.json().get("access_token", "")


    # 获取流程明细的API
    message_api_url = f"https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovaldetail?access_token={access_token}"

    

    message_content = {
        "sp_no" : sp_no,
    }

    # 发送消息
    response = requests.post(message_api_url, data=json.dumps(message_content, ensure_ascii=False).encode('utf-8'))
    result = response.json()

    # print(result['info'])
    # print(print(json.dumps(result, indent=4)))
    # 筛选出郑振彬已经通过的申请，意味着电芯已交付
    found_record=0
    for sp_record in result['info']['sp_record']:
        if sp_record["sp_status"]==2 and sp_record['details'][0]['approver']['userid']=='ZhengZhenBin':
            found_record = 1

    if found_record == 0:
        return 
    
    userid = result['info']['applyer']['userid']
    partyid = result['info']['applyer']['partyid']

    # 获取username的API
    message_api_url = f"https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={userid}"
    response = requests.get(message_api_url)
    userinfo = response.json()
    username = userinfo['name']

    # 获取department的API
    message_api_url = f"https://qyapi.weixin.qq.com/cgi-bin/department/get?access_token={access_token}&id={partyid}"
    response = requests.get(message_api_url)
    deptinfo = response.json()
    deptname=deptinfo['department']['name']




    for apply_item in result['info']['apply_data']['contents']:
        # print(apply_item)
        for title in apply_item['title']:
            if title['text']=='电芯需求数量':                
                quantity = apply_item['value']['new_number']
            if title['text']=='申请事由':
                reason = apply_item['value']['text'].replace("\n", " ")
            if title['text']=='电芯规格':
                spec = apply_item['value']['text'].replace("\n", " ")
            if title['text']=='正极和负极需要的材料':
                pn_material = apply_item['value']['text'].replace("\n", " ")
            if title['text']=='电解液/固态电解质膜的材料':
                electro_material = apply_item['value']['text'].replace("\n", " ")
            if title['text']=='电解液/固态电解质膜的来源':
                electro_source = apply_item['value']['selector']['options'][0]['value'][0]['text'].replace("\n", " ")
            if title['text']=='是否3.4Ah或以下':
                is34ah_orlower = apply_item['value']['selector']['options'][0]['value'][0]['text']
            if title['text']=='配方编码':
                formula_code = apply_item['value']['text'].replace("\n", " ") 
    
    is34ah_orlower = True if is34ah_orlower=='是' else False

    # print(f'''quantity:{quantity},reason:{reason},spec:{spec},
    #       pn_material:{pn_material},electro_material:{electro_material},
    #       electro_source:{electro_source},is34ah:{is34ah_orlower},
    #       formulat_code:{formula_code}''')
    
    
    # print(sp_no,'*'*100)
    sql = f"delete from lims_cellapply where applyid={sp_no}"
    cursor.execute(sql)
    
    sql = f"""INSERT INTO lims_cellapply (applyid,applier, apply_dep, reason, 
            spec, pn_material, electro_material, electro_source, 
            formula_code, is34ah, quantity) 
         VALUES ({sp_no} ,'{username}', '{deptname}', '{reason}', 
             '{spec}', '{pn_material}','{electro_material}', '{electro_source}',
              '{formula_code}', {is34ah_orlower}, {quantity})"""    
    cursor.execute(sql)

    # 提交事务
    conn.commit()
                

        

def main():
    
    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read('settings.ini')

    # 获取配置信息
    corpID = config.get('corp', 'corpID')
    agentID = config.get('corp', 'agentID')
    corpSecret = config.get('corp', 'corpSecret')


    splist = get_sp_list(corpID, corpSecret)
    
    for sp in splist:
        get_sp_detail(corpID, corpSecret,sp)
    cursor.close()
    conn.close()
    
        

if __name__ == "__main__":
    main()  # 在程序执行时调用主函数
