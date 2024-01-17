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
        # 处理每个上传的文件
        for filename in request.FILES.getlist('files'):
            print(filename)
            # 使用 pandas 读取 Excel 文件
            df = pd.read_excel(filename)
            
            # 获取列头信息
            columns = list(df.columns)
            # 去掉括号，否则会导致kendogrid生成不了
            columns =[re.sub(r'\(|\)|\%','',item) for item in columns]
            print(columns)
            # 将 DataFrame 转换为 JSON 格式
            json_data = df.to_dict(orient='records')
            
            json_data = [{key.replace('(', '').replace(')', '').replace('%', ''): value for key,value in d.items()} for d in json_data]
            print(json_data)
            json_data = json.dumps(json_data)

            # 将数据和文件名添加到响应数据中
            response_data.append({
                'filename': filename.name,
                'data': json_data,
                'columns': columns
            })
        return JsonResponse({'data': response_data}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)

    
