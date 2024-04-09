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
import math
import base64
import pymysql
from lims.models import *
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import io
from django.http import HttpResponse
import mysql.connector

@login_required
def setcelltype(request):    
    return render(request, 'lims/celltype.html')

@login_required
def setcellsource(request):    
    return render(request, 'lims/cellsource.html')

@login_required
def setstockin(request):
    context_dict={}
    # 得到电芯类型
    fields = ['id', 'type_name']
    typelist = celltype.objects.values(*fields)
    companypara = []
    for atype in typelist:
        companypara.append({'value': atype['id'], 'text': atype['type_name']})
    companypara_json = json.dumps(companypara) 
    context_dict['all_types'] = companypara_json

    # 得到电芯来源
    fields = ['id', 'source_name']
    typelist = cellsource.objects.values(*fields)
    companypara = []
    for asource in typelist:
        companypara.append({'value': asource['id'], 'text': asource['source_name']})
    companypara_json = json.dumps(companypara) 
    context_dict['all_sources'] = companypara_json

    # 得到所有status=1的电芯入库记录
    stockins = stockin.objects.filter(status=1).values()

    for stockin_data in stockins:
       stockin_data['indate'] = stockin_data['indate'].isoformat()
       stockin_data['operate_date'] = stockin_data['operate_date'].isoformat()
    
    context_dict['stockins']=list(stockins)

    print(context_dict)
   
    return render(request, 'lims/stockin.html',context_dict)


def stockin_form(request):
    cell_types = celltype.objects.all()
    cell_sources = cellsource.objects.all()
    return render(request, 'lims/stockin_form.html', {'cell_types': cell_types, 'cell_sources': cell_sources})

def stockin_create(request):    
    if request.method == 'POST':
        print('in_create')
        print('typeid',request.POST.get('type_id'))
        type_id = request.POST.get('type_id')
        source_id = request.POST.get('source_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price', 0)
        indate = request.POST.get('indate', date.today())
        staff = request.POST.get('staff')
        memo = request.POST.get('memo')
        status = request.POST.get('status', 1)
        operator = request.POST.get('operator',request.user)
        operate_date = request.POST.get('operate_date', date.today())

        stockin_obj = stockin.objects.create(
            type_id=type_id,
            source_id=source_id,
            quantity=quantity,
            price=price,
            indate=indate,
            staff=staff,
            memo=memo,
            status=status,
            operator=operator,
            operate_date=operate_date
        )
        # 连接到 MySQL 数据库
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Abc_12345',
            database='xjny'
        )

        # 从 MySQL 表中读取数据
        query = f"SELECT id FROM lims_stock where type_id={type_id}"
        df = pd.read_sql(query, conn)
        if len(df) > 0:
            sql_statement = f'''update lims_stock set quantity=quantity+{quantity},
              last_operate_date = sysdate() 
              where type_id={type_id}'''
        else:
            sql_statement = f'''insert into lims_stock(type_id,quantity,last_operate_date) 
            values ({type_id},{quantity},sysdate())'''
        
        print(sql_statement)
        # 创建一个游标对象，执行语句
        cursor = conn.cursor()
        cursor.execute(sql_statement)
        conn.commit()
        cursor.close()
        conn.close()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


def stockin_cancel(request):    
    if request.method == 'POST':
        print('in_stockin_cancel')
        stockin_id = request.POST.get('id')
        print('id',request.POST.get('id'))
        print(str(request.user))

        astockin = stockin.objects.get(pk=stockin_id)


        # 判断减去库存数量
        type_id = astockin.type_id
        quantity = astockin.quantity

        astock = stock.objects.get(pk=type_id)
        sum_quantity = astock.quantity

        if sum_quantity - quantity < 0:
            errmsg = '库存数量少于需要撤销入库的数量'
            print(errmsg)
            return JsonResponse({'status': 'error','errmsg':errmsg})
        

        # 撤销入库记录
        astockin.status = 0
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d:%H%M%S') 
        astockin.memo = astockin.memo +' status changed to 0 by '+str(request.user)+' on '+ formatted_time


        # 减去库存数量
        astock.quantity = sum_quantity - quantity
        astock.last_operate_date = datetime.now()

        astockin.save()   
        astock.save()         

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})
    

@login_required
def setstockout(request):
    context_dict={}
    # 得到电芯类型
    fields = ['id', 'type_name']
    typelist = celltype.objects.values(*fields)
    companypara = []
    for atype in typelist:
        companypara.append({'value': atype['id'], 'text': atype['type_name']})
    companypara_json = json.dumps(companypara) 
    context_dict['all_types'] = companypara_json

    # 得到领用部门
    fields = ['id', 'teamname']
    teamlist = teams.objects.values(*fields)
    companypara = []
    for ateam in teamlist:
        companypara.append({'value': ateam['id'], 'text': ateam['teamname']})
    companypara_json = json.dumps(companypara) 
    context_dict['all_teams'] = companypara_json

    # 得到所有status=1的电芯出库记录
    stockouts = stockout.objects.filter(status=1).values()

    for stockout_data in stockouts:
       stockout_data['outdate'] = stockout_data['outdate'].isoformat()
       stockout_data['operate_date'] = stockout_data['operate_date'].isoformat()
    
    context_dict['stockouts']=list(stockouts)

    print(context_dict)
   
    return render(request, 'lims/stockout.html',context_dict)



def stockout_create(request):    
    if request.method == 'POST':
        print('in_create_stockout')
        print('typeid',request.POST.get('type_id'))
        type_id = request.POST.get('type_id')
        recipient_id = request.POST.get('recipient_id')
        quantity = int(request.POST.get('quantity'))
        price = request.POST.get('price', 0)
        outdate = request.POST.get('outdate', date.today())
        staff = request.POST.get('staff')
        memo = request.POST.get('memo')
        status = request.POST.get('status', 1)
        operator = request.POST.get('operator',request.user)
        operate_date = request.POST.get('operate_date', date.today())

        # 判断减去库存数量
        try:
            astock = stock.objects.get(pk=type_id) 
            sum_quantity = astock.quantity
        except:
            sum_quantity = 0
        

        if sum_quantity - quantity < 0:
            errmsg = '库存数量少于需要出库的数量'
            print(errmsg)
            return JsonResponse({'status': 'error','errmsg':errmsg})

        stockout_obj = stockout.objects.create(
            type_id=type_id,
            recipient_id=recipient_id,
            quantity=quantity,
            price=price,
            outdate=outdate,
            staff=staff,
            memo=memo,
            status=status,
            operator=operator,
            operate_date=operate_date
        )

        # 减去库存数量
        astock.quantity = sum_quantity - quantity
        astock.last_operate_date = datetime.now()
        astock.save()        

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})
    

def stockout_cancel(request):    
    if request.method == 'POST':
        print('in_stockouit_cancel')
        stockout_id = request.POST.get('id')
        print('id',request.POST.get('id'))
        print(str(request.user))

        astockout = stockout.objects.get(pk=stockout_id)


        # 库存数量
        type_id = astockout.type_id
        quantity = astockout.quantity

        astock = stock.objects.get(pk=type_id)
        sum_quantity = astock.quantity

       

        # 撤销入库记录
        astockout.status = 0
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d:%H%M%S') 
        astockout.memo = astockout.memo +' status changed to 0 by '+str(request.user)+' on '+ formatted_time


        # 增加库存数量
        astock.quantity = sum_quantity + quantity
        astock.last_operate_date = datetime.now()

        astockout.save()   
        astock.save()         

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})
    

@login_required
def stockquery(request):
    context_dict={}

    # 得到电芯类型
    fields = ['id', 'type_name']
    typelist = celltype.objects.values(*fields)
    companypara = []
    for atype in typelist:
        companypara.append({'value': atype['id'], 'text': atype['type_name']})
    companypara_json = json.dumps(companypara) 
    context_dict['all_types'] = companypara_json

   

    # 得到电芯库存记录
    stocks = stock.objects.all().values() 

    for stock_data in stocks:
       stock_data['last_operate_date'] = stock_data['last_operate_date'].isoformat()
    
    context_dict['stocks']=list(stocks)

    print(context_dict)
   
    return render(request, 'lims/stockquery.html',context_dict)