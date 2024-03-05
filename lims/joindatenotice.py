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

# 找出明天入职周年的员工名单
tomorrow = datetime.now() + timedelta(days=1)
anniversary_joins = df[((df['joindate'].dt.month == tomorrow.month) & (df['joindate'].dt.day == tomorrow.day))]

# 生成提醒消息
message = "明天入职周年的员工有：\n"
for index, row in anniversary_joins.iterrows():
    anniversary_years = tomorrow.year - row['joindate'].year
    message += f"{row['name']} (入职{anniversary_years}年),入职日期{row['joindate']}\n"
message +='请及时发送入职关怀短信'


# 使用企业微信 API 或其他方式发送提醒消息给 pengxuerou 微信账号
# 这里假设你已经有了一个发送消息的函数 send_message()
send_wechat_message('wwc75be524bd50ea62', '1000019', '9AuHHCNnwf8in7ZE2UcxDy3hSIzwfRH-q5o-W-tKpjU', 
                    'huangchao', message)

send_wechat_message('wwc75be524bd50ea62', '1000019', '9AuHHCNnwf8in7ZE2UcxDy3hSIzwfRH-q5o-W-tKpjU', 
                    'pengxuerou', message)
    

# 打印提醒消息
print(message)