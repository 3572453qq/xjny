import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
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

def arabic_to_chinese_number(number):
    chinese_numbers = {
        '0': '零',
        '1': '一',
        '2': '两',
        '3': '三',
        '4': '四',
        '5': '五',
        '6': '六',
        '7': '七',
        '8': '八',
        '9': '九'
    }

    chinese_number = ''
    for digit in str(number):
        chinese_number += chinese_numbers.get(digit, digit)

    return chinese_number

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
query = "SELECT id, name, joindate FROM lims_hrjoindate"
df = pd.read_sql(query, conn)

# 关闭数据库连接
conn.close()


# 将 joindate 列转换为日期时间类型
df['joindate'] = pd.to_datetime(df['joindate'])

# 找出今天入职周年的员工名单
# tomorrow = datetime.now() + timedelta(days=1)
tomorrow = datetime.now()
anniversary_joins = df[((df['joindate'].dt.month == tomorrow.month) & (df['joindate'].dt.day == tomorrow.day))]

 # 读取JSON文件
with open('nameid.json', 'r',encoding='utf-8') as file:
    namelist = json.load(file)

# 生成提醒消息
for index, row in anniversary_joins.iterrows():

    if row['name'] in namelist.keys():
        eachUser = namelist[row['name'] ]
    else:
        eachUser = get_pinyin(row['name'])    
    anniversary_years = tomorrow.year - row['joindate'].year
    anniversary_years = arabic_to_chinese_number(anniversary_years)

    print(eachUser)
    message = f'''亲爱的{row['name']},
时光飞逝，一岁一更迭。
{anniversary_years}年前的今天，你加入了欣界大家庭，{anniversary_years}周年快乐 :)
这{anniversary_years}年，成长与收获，沉淀与突破。
在未来的年份中，期待继续出发。
欣界愿和你一起走繁花盛开，曲折而向上的路。
目光所及皆是温暖，心之所向皆是朝阳，欣界大家庭一路相行
    '''
    send_wechat_message('wwc75be524bd50ea62', '1000022', '0Lg-SE1-B4mDihn_rKKB1xNy8ba1PCNwRK8kOrZeoEE', 
                    'huangchao', message)

    send_wechat_message('wwc75be524bd50ea62', '1000022', '0Lg-SE1-B4mDihn_rKKB1xNy8ba1PCNwRK8kOrZeoEE', 
                    'pengxuerou', message)
    
    send_wechat_message('wwc75be524bd50ea62', '1000022', '0Lg-SE1-B4mDihn_rKKB1xNy8ba1PCNwRK8kOrZeoEE', 
                    eachUser, message)
    
    # 打印提醒消息
    print(message)




# 使用企业微信 API 或其他方式发送提醒消息给 pengxuerou 微信账号
# 这里假设你已经有了一个发送消息的函数 send_message()

    

