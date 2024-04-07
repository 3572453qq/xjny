#coding=utf-8
from django.http import JsonResponse
from django.http import HttpResponse
import json
from querystring_parser import parser
from .models import *
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,permission_required
from django.core.exceptions import PermissionDenied
# from djangops.settings import CMDB_MODELS
from django.contrib.auth.models import Permission 



@csrf_exempt
def listing(request,model_name):
    arguments = parser.parse(request.POST.urlencode())
    l_id=request.POST.get('id')
    var_b=eval(model_name)
    try:
        aline=var_b.objects.filter(pk=l_id).update(**arguments )
    except:
        print("id not exist" )
        print(l_id)
    allrecords=list(var_b.objects.all().values())
    first300=allrecords[0:30000]
    total=var_b.objects.count()
    # print(first300)
    dict1={"Data": first300, "total":total,"success": True}
    return JsonResponse(dict1)

@login_required
@csrf_exempt
def updatelist(request,model_name):
        #if request.method == 'POST':
    #    req=json.loads(request.body)
    arguments = parser.parse(request.POST.urlencode())
    print("in update")
    print(model_name)
    print(request.POST)
    print(arguments)
    print(request.POST.get('username'))
        #print request.POST.get('id')
        #print request.POST.getall()
    l_id=request.POST.get('id')
        #print l_id
    var_b=eval(model_name)
    try:
        aline=var_b.objects.filter(pk=l_id).update(**arguments )
    except Exception as e:

        print("id not exist",e )
        print(l_id)
    
    
    dict1={"Data": [], "success": "true"}
    # print(dict1)
    return HttpResponse(json.dumps(dict1))

@login_required
@csrf_exempt
def createnew(request,model_name):
    arguments = parser.parse(request.POST.urlencode())
    print("in create")
    print(model_name)
    print(arguments)

    p1=eval(model_name)
    
    l_id=arguments['id']
    print("this id"+l_id)
    try:
        aline=p1.objects.filter(pk=l_id).delete()
    except:
        print("id not exist" )
        print(l_id)
    
    del arguments['id']
    print(arguments)
    aline=p1.objects.create(**arguments)
    print(aline.id)
    dictaline=model_to_dict(aline)
    #print "this is aline:"+aline
    dict1={"Data": [dictaline], "success": "true"}
    # print(dict1)

    return JsonResponse(dict1)
    #return HttpResponse(json.dumps(dict1))


@csrf_exempt
def deleteone(request,model_name):
    arguments = parser.parse(request.POST.urlencode())
    print("in delete")
    print(model_name)
    print(arguments)
    p1=eval(model_name)
    l_id=arguments['id']
    
    aline=p1.objects.filter(pk=l_id).delete()
    
    dict1={"Data": [], "success": "true"}
    # print(dict1)
    return HttpResponse(json.dumps(dict1))  