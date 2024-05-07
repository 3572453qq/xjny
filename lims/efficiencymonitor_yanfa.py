from sqlalchemy import create_engine
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import pymysql
import multiprocessing
import time
import requests,json


db_host, db_user, db_pass,db_name = '172.28.20.100','root','Abc_12345','yanfa'
ef_thredhold = 0.8
kl_threadhold = 0.965

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


    # muti processes to query data
    pool = multiprocessing.Pool()
    df = pd.DataFrame()

    for query in queries:
        # print(query)
        process = pool.apply_async(query_database, (db_host,db_user,db_pass,db_name,query))
        onedf = process.get()
        idx_to_keep = onedf.groupby(['computer_name','dev_unit_chl', 'test_id', 'Test_StartTime', 'EndTime'])[deduplication_column].idxmin()
   
        # 使用这些索引过滤 DataFrame，确保保留所有列的值       
        onedf = onedf.loc[idx_to_keep]
        if len(onedf)>0:
            df = pd.concat([df,onedf], ignore_index=True)
    return df

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

def findnewtest(computer_name,dev_unit_chl,barcode,abs_time,formatted_date):
    sqlstr = f'''select * from record{formatted_date} 
                where computer_name='{computer_name}' 
                and dev_unit_chl = '{dev_unit_chl}'
                and barcode<>'{barcode}' '''
    con = pymysql.connect(host=db_host, user=db_user,
                                password=db_pass, database=db_name)
    cursor = con.cursor(cursor=pymysql.cursors.Cursor)
    cursor.execute(sqlstr)
    records = [record[0] for record in cursor.fetchall()]
    print(records)
    return len(records) 


def main():
    # 获取当前日期
    current_date = datetime.now()

    # 格式化日期
    formatted_date = current_date.strftime('%Y%m%d')

    # 获取当天cycle表的记录
    query_sql = f'select * from cycle{formatted_date}'
    df = query_database(db_host,db_user,db_pass,db_name,query_sql)
        
    unique_values_combined = df[['computer_name', 'dev_unit_chl','test_id']].drop_duplicates()
    print(unique_values_combined)

    # 获取30天以前到现在所有符合条件cycle表的记录
    expand_start_date=get_adjacent_date(formatted_date,-30)
    expand_end_date=formatted_date
    start_table='cycle'+expand_start_date
    end_table='cycle'+expand_end_date

    df_cycle = runsqlovertables(start_table,end_table,unique_values_combined,db_name,'cycle_id')
    grouped_cycle = df_cycle.groupby(['computer_name','test_id', 'dev_unit_chl'],as_index=False)
    msg_count = 0
    for name, group in grouped_cycle:
        if len(group)<=2:
            continue
        
        group.sort_values(by='EndTime', inplace=True)
        group.reset_index(drop=True, inplace=True)

        group['保持率'] = (group['discharge_capacity'] / group['discharge_capacity'].iloc[2] ).round(4)
        group['库伦效率'] = (group['discharge_capacity'] / group['charge_capacity'] ).round(4)

        # 找到'保持率'这一列最小值的索引
        # idx_min = group['保持率'].idxmin()

        # 找到最后一行
        lastrow=len(group)-1

        # 使用这个索引来获取整行数据
        row = group.loc[lastrow]
        computer_name = row['computer_name']
        dev_unit_chl  = row['dev_unit_chl']
        barcode = row['barcode']
        abs_time = row['EndTime']
        
        if row['保持率']<ef_thredhold: 
            msg_count +=1 
            print('abs_time',abs_time,type(abs_time))   
            now = datetime.now()
            time_difference = now - abs_time
            if findnewtest(computer_name,dev_unit_chl,barcode,abs_time,formatted_date) == 0 and time_difference<timedelta(hours=4) :           
                message = f'条码为{barcode}的电芯在上位机{computer_name}的通道{dev_unit_chl}中保持率已经低于{ef_thredhold}，当前保持率为：{row["保持率"]}，库伦效率为：{row["库伦效率"]}，请及时检查'

                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'huangchao', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'LiYingBo', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'LuYongGuang', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'ZhaoHuiZi', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'GuoJiaXing', message)
        if row['库伦效率']<kl_threadhold:
            msg_count +=1 
            print('abs_time',abs_time,type(abs_time))   
            now = datetime.now()
            time_difference = now - abs_time
            if findnewtest(computer_name,dev_unit_chl,barcode,abs_time,formatted_date) == 0 and time_difference<timedelta(hours=4) :   
                message = f'条码为{barcode}的电芯在上位机{computer_name}的通道{dev_unit_chl}中库伦效率已经低于{kl_threadhold}，当前保持率为：{row["保持率"]}，库伦效率为：{row["库伦效率"]}，请及时检查'
                print('discharge_capacity:',row['discharge_capacity'])
                print('charge_capacity:',row['charge_capacity'])
                print('dev_unit_chl',row['dev_unit_chl'])
                print('test_id',row['test_id'])
                print('endtime',row['EndTime'])
                print('barcode',row['barcode'])
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'huangchao', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'LiYingBo', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'LuYongGuang', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'ZhaoHuiZi', message)
                send_wechat_message('wwc75be524bd50ea62', '1000016', 'pILyhKytz4T1WvcpLpBgXEhWqLy7gAdr6TglVGoGJTI', 
                        'GuoJiaXing', message)
    print('msg_count',msg_count)

if __name__ == "__main__":
    # 程序开始时记录时间
    start_time = time.time()
    main()
    # 程序结束时记录时间
    end_time = time.time()

    # 计算运行时间
    elapsed_time = end_time - start_time

    # 输出程序运行时间
    print(f"程序运行了 {elapsed_time} 秒")
