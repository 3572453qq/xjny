from django.shortcuts import render
import random,string
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

# Create your views here.
def base(request):
    return render(request,'base.html')

def vkeepexcel(request):
    return render(request,'vkeepexcel.html')

def handlevkeep(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        response_data = []
        summary_data = []
        print('hello')
        print( request.FILES.getlist('files'))
        
        max_length = 0
        for afile in request.FILES.getlist('files'): 
            df_result = pd.read_excel(afile,sheet_name='cycle')  
            current_length = df_result.shape[0]
            if max_length < current_length:
                max_length=current_length
        chart_df = pd.DataFrame(index=range(max_length))
        # 处理每个上传的文件
        for filename in request.FILES.getlist('files'):
            # print(filename)
            # 使用 pandas 读取 Excel 文件
            df = pd.read_excel(filename,sheet_name='cycle')
            df_result = df[['循环号','充电容量(Ah)','放电容量(Ah)']]
            df_result['保持率'] = (df_result['放电容量(Ah)'] / df_result['放电容量(Ah)'].iloc[0] ).round(4)
            df_result['库伦效率'] = (df_result['放电容量(Ah)'] / df_result['充电容量(Ah)'] ).round(4)



            # print(df_result)
            # 获取列头信息
            columns = list(df_result.columns)
            # 去掉字符串里面的括号，否则会导致kendogrid生成不了
            columns =[re.sub(r'\(|\)|\%','',item) for item in columns]
            # print(columns)
            # 将 DataFrame 转换为 JSON 格式
            json_data = df_result.to_dict(orient='records')
            
            json_data = [{key.replace('(', '').replace(')', '').replace('%', ''): value for key,value in d.items()} for d in json_data]
            # print(json_data)
            json_data = json.dumps(json_data)

            barcode = re.sub(r'\.[^.]*$','', filename.name)
            chart_df[barcode] = df_result['保持率']
            # 将数据和文件名添加到响应数据中
            response_data.append({
                'filename': filename.name,
                'barcode': barcode,
                'data': json_data,
                'columns': columns
            })

            summary_data.append({
                '电芯编码': barcode,
                '通道': '待填写',
                '分容容量Ah':'待填写',
                '放电电流':'待填写',
                '测试后电压':'待填写',
                '测试后内阻':'待填写',
                '测试后厚度':'待填写',

            })

        
        summary_data = json.dumps(summary_data)
        
        # 单独抽出来的保持率搞一个列表
        chart_df = chart_df.fillna(0)
        print(chart_df)
        # 转换为二维列表
        two_dimensional_list = chart_df.values.tolist()
        # 获取列头
        column_headers = list(chart_df.columns)
        # 在二维列表中插入列头作为第一行
        two_dimensional_list.insert(0, column_headers)
        
        # print('*'*1000)
        return JsonResponse({'data': response_data,'summary':summary_data,'chart':two_dimensional_list}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)

    
