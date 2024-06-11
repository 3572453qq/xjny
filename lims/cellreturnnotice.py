import pandas as pd
import mysql.connector
from datetime import datetime, timedelta,date
import requests
import json
import pandas as pd
import re
import time
import configparser
from datetime import datetime, date
from pypinyin import pinyin, Style


from cchardet import UniversalDetector

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

# 连接到 MySQL 数据库
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Abc_12345',
    database='xjny'
)

# 从 MySQL 表中读取数据
query = '''select a.id, b.type_name,a.batch_no,a.project_name,a.outdate,a.staff,a.expect_return_date,a.purpose,a.memo,a.quantity
from lims_uatstockout a, lims_uatcelltype b
where status=1 and a.type_id = b.id'''

df = pd.read_sql(query, conn)

# 关闭数据库连接
conn.close()


# 得出今天
today = date.today()



 # 读取JSON文件
with open('nameid.json', 'r',encoding='utf-8') as file:
    namelist = json.load(file)



# 生成提醒消息
for index, row in df.iterrows():

    delta = row['expect_return_date'] - today
    print(row['expect_return_date'],today,delta)
    if delta.days < 0:
        remindmessage = f'已逾期{-delta.days}天'
    else:
        remindmessage = f'将在{delta.days}天后需要归还'
    
    if row['staff'] in namelist.keys():
        eachUser = namelist[row['staff'] ]
    else:
        eachUser = get_pinyin(row['staff'])  

    if delta.days <= 3:
        message = f'''您好，有一批电芯需要关注，批号为：{row['batch_no']}，类型为：{row['type_name']},
            所属项目为:{row['project_name']}，领用人为：{row['staff']}， 数量为：{row['quantity']}，
            出库日期为：{row['outdate']}，预计归还日期为：{row['expect_return_date']}，
            用途为：{row['purpose']}，备注为：{row['memo']}，'''+remindmessage


   
    send_wechat_message('wwc75be524bd50ea62', '1000026', '6-4nK0ei2e-ywGoOGYhLL_GdwzK52Pe8otR6HZWm2F0', 
                    'huangchao', message)

    send_wechat_message('wwc75be524bd50ea62', '1000026', '6-4nK0ei2e-ywGoOGYhLL_GdwzK52Pe8otR6HZWm2F0', 
                    'yinzhouhong', message)
    
    send_wechat_message('wwc75be524bd50ea62', '1000026', '6-4nK0ei2e-ywGoOGYhLL_GdwzK52Pe8otR6HZWm2F0', 
                    eachUser, message)
    
    # # 打印提醒消息
    # print(message)

