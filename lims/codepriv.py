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
from django.contrib.auth.models import User

@login_required
@permission_required('lims.codeamdin')
def setresourcetype(request):    
    return render(request, 'lims/resourcetype.html')

@login_required
@permission_required('lims.codewrite')
def setresource(request):    
    user_id=int(request.session.get('_auth_user_id'))
    print('this is my id:',user_id)
    context_dict = {'module': 'lims'}
    # 得到所有用户
    all_users = User.objects.all()
    userpara = []
    for user in all_users:
        userpara.append({'value': user.id, 'text': user.username})    
    userpara_json = json.dumps(userpara) 
    context_dict['users'] = userpara_json
    
    context_dict['currentuser'] = user_id

    # 得到其他用户
    otheruser = []
    for user in all_users:
        if user.id != user_id:
            otheruser.append({'value': user.id, 'text': user.username})    
    otheruser_json = json.dumps(otheruser) 
    context_dict['otheruser'] = otheruser_json
    
    # 得到资源类型
    fields = ['id', 'type_name']
    typelist = resourcetype.objects.values(*fields)
    typepara = []
    for asource in typelist:
        typepara.append({'value': asource['id'], 'text': asource['type_name']})
    typepara_json = json.dumps(typepara) 
    context_dict['resourcetype'] = typepara_json

    # 得到所有资源和用户的权限对应关系
    resource_user_mapping=list(resource_user.objects.all().values())
    context_dict['resource_user_mapping'] = json.dumps(resource_user_mapping)
    print(context_dict['resource_user_mapping'] )
    return render(request, 'lims/setresource.html',context_dict)

@login_required
@permission_required('lims.resource')
def resourcelisting(request):    
    user_id=request.session.get('_auth_user_id')
    print('this is my id:',user_id)
    all_users = User.objects.all()
    print('here are all the user ids:')
    for user in all_users:
        print(user.id)  

    allrecords=list(resource.objects.filter(
        owner_id__in=user_id).values())   
    total = len(allrecords)
    
    dict1={"Data": allrecords, "total":total,"success": True}
    return JsonResponse(dict1)
   
@login_required
@permission_required('lims.coderead')
def readresource(request):    
    user_id=request.session.get('_auth_user_id')
    print('this is my id:',user_id)
    context_dict = {'module': 'lims'}
    # 得到所有用户
    all_users = User.objects.all()
    userpara = []
    for user in all_users:
        userpara.append({'value': user.id, 'text': user.username})    
    userpara_json = json.dumps(userpara) 
    context_dict['users'] = userpara_json

    context_dict['currentuser'] = user_id
    
    # 得到资源类型
    fields = ['id', 'type_name']
    typelist = resourcetype.objects.values(*fields)
    typepara = []
    for asource in typelist:
        typepara.append({'value': asource['id'], 'text': asource['type_name']})
    typepara_json = json.dumps(typepara) 
    context_dict['resourcetype'] = typepara_json


    # 得到用户是owner的资源
    owner_allrecords=list(resource.objects.filter(
        owner_id=user_id).values())   
    

    
    # 得到用户有权限的资源
    filtered_ids = resource_user.objects.filter(user_id=user_id).values_list('resource_id',flat=True)
    list_resource_id = list(filtered_ids)

    # 得到用户被授权的资源
    granted_records = list(resource.objects.filter(
        id__in=list_resource_id).values())   

    all_records = owner_allrecords+granted_records

    total=len(all_records)
    
    
    context_dict['ls_data']=all_records
    context_dict['total']=total

    print(context_dict)
    return render(request, 'lims/readresource.html',context_dict)

def coderead(request):
    # get all the inputs from client
    selectedValues = request.POST.getlist('selectedValues[]')
    selected_id = request.POST.get('selected_id')
    print(selectedValues)
    print(selected_id)   

    resource_user.objects.filter(resource_id=selected_id).delete()

    for user_id in selectedValues:
        resource_user.objects.create(user_id=user_id,resource_id=selected_id,priv=1)
    
    ls_data = {
            "isok": 1}
    return JsonResponse(ls_data)
