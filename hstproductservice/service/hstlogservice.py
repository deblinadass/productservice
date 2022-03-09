# Create your views here.
from django.http import JsonResponse
from hstproductservice.model.hstproductmodel import  \
    ProductProperty, Productcatalogue, ProductAuditLog, ProductcatalogueProperty, Userbandwidth
from hstproductservice.serializer.hstproductserializer import  \
    LogSerializer, LogSerializerAdd, ProductAuditlogDetailSerializer
from rest_framework.permissions import AllowAny
from hstproductservice.hstproductserviceconfig import JWT_KEYWORD, URL_ORDER_SERVICE, URL_LOCATION_SERVICE
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework import exceptions
import jwt
from django.db.models import Max
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.compat import requests
from datetime import datetime
from rest_framework.status import (
    HTTP_200_OK
)
import re
dateformat = "%d-%m-%Y"
datetimeformat= "%d-%m-%Y %H:%M"

YES = 'Ja'
NO = 'Nee'
Sublocatie = 'Sublocatie'
Gedeactiveerd = 'Gedeactiveerd'
Geactiveerd = 'Geactiveerd'
STATIC_ENDDATE = '2099-12-31'

def change_date_format(dt):
        return re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', dt)
    
def getUsername(request):
        
        token = request.META.get('HTTP_AUTHORIZATION')
        tokenarr = token.split()
        token = tokenarr[1]

        try:
            decodedtoken = jwt.decode(token, JWT_KEYWORD, algorithm='HS256')
            username = decodedtoken.get('user')
            #user = User.objects.get(username=username)
            return username
        except jwt.ExpiredSignature:
            #return Response({"message": "token_expired"}, status=403)
            raise exceptions.AuthenticationFailed('Token Expired')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Invalid Signature')
            


def logAddMacauth(request, serializer, action):
        array_dict_add_log = {}
        array_dict_add_log_detail = {}
        
        
        productname = serializer.data['macaddress']

        
        comment = 'MAC-adres ' + productname +' aangemaakt'
        producttype = 'MAC adres'
        
        pk = serializer.data['id']
        
        productlocid=serializer.data['location_id']
        catalogue_excluded_fields = ['id', 'startdate', 'location_id', 'chain_id', 'startname']

        user = getUsername(request)
        ins_id = 0
        array_dict_add_log.update(
            {'action': action, 'update_date': str(timezone.now()), 'product_type': producttype, 'product_name' : productname,
                'updated_by': user, 'location_id': productlocid, 'comment': comment, 'catalogue_id':0, 'installbase_id' : pk})
        serializerLog = LogSerializerAdd(data=array_dict_add_log)

        if serializerLog.is_valid():
            serializerLog.save()
            ins_id = serializerLog.data['id']

        for (k, v) in serializer.data.items():
            
            if k == 'ubprofile':
                newvalue = ProductProperty.objects.getPropertyListByAttrID(20,1,serializer.data['ubprofile']) if serializer.data['ubprofile'] and serializer.data['ubprofile']!=0 else ''
            elif k == 'ubprofiledownload':
                newvalue = Userbandwidth.objects.getUBDownloadName(serializer.data['ubprofiledownload']) if serializer.data['ubprofiledownload']  and serializer.data['ubprofiledownload']!=0 else ''
            elif k == 'ubprofileupload':
                newvalue = Userbandwidth.objects.getUBUploadName(serializer.data['ubprofileupload']) if serializer.data['ubprofileupload'] and serializer.data['ubprofileupload']!=0 else ''
            else :
                newvalue = v

            if k in ['startdate', 'enddate']:
                newvalue = formatStringDate(newvalue)
                
            if v != '' and v!= None and str(v)!='0' and k not in catalogue_excluded_fields:
                array_dict_add_log_detail.update(
                    {'field_name': k, 'old_value': '', 'new_value': newvalue,
                        'productauditlog': ins_id})

                serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_add_log_detail)
                if serializerLogdetail.is_valid():
                    serializerLogdetail.save()

def logUpdateMacauth(request, serializerbefore, serializerafter, action, pk):
    if serializerbefore != serializerafter.data:
        array_dict = {}
        array_dict_update_log_detail = {}
        locationid = serializerbefore['location_id']
        productname = serializerafter.data['macaddress']
        producttype = 'MAC adres'
        comment = 'MAC-adres ' +productname +' aangepast'
        user = getUsername(request)
        array_dict.update({'action': action, 'update_date': str(timezone.now()), 'product_name' : productname, 'product_type': producttype, 'updated_by': user, 'location_id':locationid, 'comment': comment, 'installbase_id': pk})
        serializerLog = LogSerializerAdd(data=array_dict)
        if serializerLog.is_valid():
            serializerLog.save()
            ins_id = serializerLog.data['id']
        
        for (k, v) in serializerbefore.items():
            if v != serializerafter.data[k]:
                
                if k == 'ubprofile' : # Dynamic, DBB, L3
                    print('ubprofile')
                    newVal = ProductProperty.objects.getPropertyListByAttrID(20,1,serializerafter.data['ubprofile']) if serializerafter.data['ubprofile'] and serializerafter.data['ubprofile']!=0 else ''
                    oldVal = ProductProperty.objects.getPropertyListByAttrID(20,1,serializerbefore['ubprofile']) if serializerbefore['ubprofile'] and serializerbefore['ubprofile']!=0 else ''
                elif k == 'ubprofiledownload' and v!=None and str(v)!='0' and v!='':
                    newVal = Userbandwidth.objects.getUBDownloadName(serializerafter.data['ubprofiledownload']) if serializerafter.data['ubprofiledownload'] and serializerafter.data['ubprofiledownload']!=0 else ''
                    oldVal = Userbandwidth.objects.getUBDownloadName(serializerbefore['ubprofiledownload']) if serializerbefore['ubprofiledownload'] and serializerbefore['ubprofiledownload']!=0 else ''
                elif k == 'ubprofileupload' and v!=None and str(v)!='0' and v!='':
                    newVal = Userbandwidth.objects.getUBUploadName(serializerafter.data['ubprofileupload']) if serializerafter.data['ubprofileupload'] and serializerafter.data['ubprofileupload']!=0 else ''
                    oldVal = Userbandwidth.objects.getUBUploadName(serializerbefore['ubprofileupload']) if serializerbefore['ubprofileupload'] and serializerbefore['ubprofileupload']!=0 else ''
                elif k in ['startdate', 'enddate']:
                    oldVal = formatStringDate(v)
                    newVal = formatStringDate(serializerafter.data[k])
                else :
                    newVal=serializerafter.data[k]
                    oldVal = v

                
                
                    
                array_dict_update_log_detail.update(
                                {'field_name': k, 'old_value': oldVal, 'new_value': newVal, 'productauditlog': ins_id})
                serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_update_log_detail)
                if serializerLogdetail.is_valid():
                    serializerLogdetail.save()

def logDeleteMacauth(request, serializer, action):
        array_dict_add_log = {}
        array_dict_add_log_detail = {}
        
        productname = serializer.data['macaddress']
        comment = 'MAC-adres ' +productname +' verwijderd'
        producttype = 'MAC adres'
        
        pk = serializer.data['id']
        
        productlocid=serializer.data['location_id']
        catalogue_excluded_fields = ['id', 'startdate', 'location_id', 'chain_id', 'startname']

        user = getUsername(request)
        ins_id = 0
        array_dict_add_log.update(
            {'action': action, 'update_date': str(timezone.now()), 'product_type': producttype, 'product_name' : productname,
                'updated_by': user, 'location_id': productlocid, 'comment': comment, 'catalogue_id':0, 'installbase_id' : pk})
        serializerLog = LogSerializerAdd(data=array_dict_add_log)

        if serializerLog.is_valid():
            serializerLog.save()
            ins_id = serializerLog.data['id']

        for (k, v) in serializer.data.items():
            if k == 'ubprofile':
                newvalue = ProductProperty.objects.getPropertyListByAttrID(20,1,serializer.data['ubprofile']) if serializer.data['ubprofile'] and serializer.data['ubprofile']!=0 else ''
            elif k == 'ubprofiledownload':
                newvalue = Userbandwidth.objects.getUBDownloadName(serializer.data['ubprofiledownload']) if serializer.data['ubprofiledownload'] and serializer.data['ubprofiledownload']!=0 else ''
            elif k == 'ubprofileupload':
                newvalue = Userbandwidth.objects.getUBUploadName(serializer.data['ubprofileupload']) if serializer.data['ubprofileupload'] and serializer.data['ubprofileupload']!=0 else ''
                
            elif k in ['startdate', 'enddate']:
                newvalue = formatStringDate(v)
            else :
                newvalue = v

            
                
            if v != '' and k not in catalogue_excluded_fields:
                array_dict_add_log_detail.update(
                    {'field_name': k, 'old_value': newvalue, 'new_value': 'verwijderd',
                        'productauditlog': ins_id})

                serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_add_log_detail)
                if serializerLogdetail.is_valid():
                    serializerLogdetail.save()

def logAddProductCatalogue(request, serializer, action):
            array_dict_add_log = {}
            array_dict_add_log_detail = {}
            
            productgroupval = serializer.data['productgroup']
            producttypeval = serializer.data['producttype']
            productnameval = serializer.data['productname']
            rtlmemoline = serializer.data['rtlmemoline']
            catid = serializer.data['catrefid']
            
            productgroup = ProductcatalogueProperty.objects.getCataloguePropertyName('productgroup', str(productgroupval))
            producttype = ProductcatalogueProperty.objects.getCataloguePropertyName('producttype', str(producttypeval))
            productname = ProductcatalogueProperty.objects.getProductName('productname', str(productnameval), str(productgroupval), str(producttypeval))
            rtlmemolinename = ProductcatalogueProperty.objects.getProductName('productmemoline', str(rtlmemoline), str(productgroupval), str(producttypeval)).cataloguepropertyname if str(productgroupval) == '1' else str(rtlmemoline)
            
            #comment= productgroup + ' Product catalogue ' + ' '+ productname +' aangemaakt'
            comment = productname.cataloguepropertyname+' product met catalogus ID '+ catid + ' aangemaakt'

            
            pk = serializer.data['id']
            
            productlocid=0
            catalogue_excluded_fields = ['id', 'startstaffel', 'endstaffel', 'productdescription', 'productstatus', 'maximumquantity']

            user = getUsername(request)
            ins_id = 0
            array_dict_add_log.update(
                {'action': action, 'update_date': str(timezone.now()), 'product_type': productgroup, 'product_name' : productname.cataloguepropertyname,
                 'updated_by': user, 'location_id': productlocid, 'comment': comment, 'catalogue_id':productgroupval, 'installbase_id' : pk})
            
            serializerLog = LogSerializerAdd(data=array_dict_add_log)

            if serializerLog.is_valid():
                serializerLog.save()
                ins_id = serializerLog.data['id']
                
            for (k, v) in serializer.data.items():
                if k == 'productgroup':
                    product_cat_field_newvalue = productgroup
                elif k == 'producttype':
                    product_cat_field_newvalue = producttype
                elif k == 'productname':
                    product_cat_field_newvalue = productname
                elif k == 'rtlmemoline':
                    product_cat_field_newvalue = rtlmemolinename
                else :
                    product_cat_field_newvalue = v

                if k in ['startdate', 'enddate']:
                    if product_cat_field_newvalue != STATIC_ENDDATE:
                        product_cat_field_newvalue = formatStringDate(product_cat_field_newvalue)
                    else:
                        v = ''
                if v != '' and k not in catalogue_excluded_fields:

                    array_dict_add_log_detail.update(
                        {'field_name': k, 'old_value': '', 'new_value': product_cat_field_newvalue,
                         'productauditlog': ins_id})
                    
                    serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_add_log_detail)
                    if serializerLogdetail.is_valid():
                        serializerLogdetail.save()

def logUpdateProductCatalogue(request, serializerbefore, serializerafter, action, pk):
    if serializerbefore != serializerafter.data:
        array_dict = {}
        array_dict_update_log_detail = {}
        productgroupval_old = serializerbefore['productgroup']
        producttypeval_old = serializerbefore['producttype']
        productnameval_old = serializerbefore['productname']
        catid = serializerbefore['catrefid']
        rtlmemoline_old = serializerbefore['rtlmemoline']
        productgroup_old = ProductcatalogueProperty.objects.getCataloguePropertyName('productgroup', str(productgroupval_old))
        producttype_old = ProductcatalogueProperty.objects.getCataloguePropertyName('producttype', str(producttypeval_old))
        productname_old = ProductcatalogueProperty.objects.getProductName('productname', str(productnameval_old), str(productgroupval_old), str(producttypeval_old))
        rtlmemolinename_old = ProductcatalogueProperty.objects.getProductName('productmemoline', str(rtlmemoline_old), str(productgroupval_old), str(producttypeval_old)).cataloguepropertyname if str(productgroupval_old) == '1' else str(rtlmemoline_old)

        productgroupval_new = serializerafter.data['productgroup']
        producttypeval_new = serializerafter.data['producttype']
        productnameval_new = serializerafter.data['productname']
        rtlmemoline_new = serializerafter.data['rtlmemoline']
        productgroup_new = ProductcatalogueProperty.objects.getCataloguePropertyName('productgroup', str(productgroupval_new))
        producttype_new = ProductcatalogueProperty.objects.getCataloguePropertyName('producttype', str(producttypeval_new))
        productname_new = ProductcatalogueProperty.objects.getProductName('productname', str(productnameval_new), str(productgroupval_new), str(producttypeval_new))
        rtlmemolinename_new = ProductcatalogueProperty.objects.getProductName('productmemoline', str(rtlmemoline_new), str(productgroupval_new), str(producttypeval_new)).cataloguepropertyname if str(productgroupval_new) == '1' else str(rtlmemoline_new)

        #comment = productgroup_old + ' Product catalogue ' + ' '+ productname_old + ' aangepast'
        comment = productname_new.cataloguepropertyname +' product met catalogus ID '+ catid + ' aangepast'
        user = getUsername(request)
        array_dict.update({'action': action, 'update_date': str(timezone.now()), 'product_name' : productname_new.cataloguepropertyname, 'product_type': productgroup_new, 'updated_by': user, 'comment': comment, 'installbase_id': pk})
        
        serializerLog = LogSerializerAdd(data=array_dict)
        if serializerLog.is_valid():
            serializerLog.save()
            ins_id = serializerLog.data['id']

        array_dict_add_old_loc_log ={}
        array_dict_add_old_log_detail_product = []


        for (k, v) in serializerbefore.items():
            if v != serializerafter.data[k]:
                if k == 'productgroup':
                    newVal = productgroup_new
                    oldVal = productgroup_old
                elif k == 'producttype':
                    newVal = producttype_new
                    oldVal = producttype_old
                elif k == 'productname':
                    newVal = productname_new
                    oldVal = productname_old
                elif k == 'rtlmemoline':
                    newVal = rtlmemolinename_new
                    oldVal = rtlmemolinename_old
                else :
                    newVal=serializerafter.data[k]
                    oldVal = v

                if k in ['startdate', 'enddate']:
                    if oldVal != STATIC_ENDDATE:
                        oldVal = formatStringDate(oldVal)
                    else:
                        oldVal = ''
                    if newVal != STATIC_ENDDATE:
                        newVal = formatStringDate(newVal)
                    else:
                        newVal = ''
                    
                array_dict_update_log_detail.update(
                                {'field_name': k, 'old_value': oldVal, 'new_value': newVal, 'productauditlog': ins_id})
                serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_update_log_detail)
                if serializerLogdetail.is_valid():
                    serializerLogdetail.save()

def logDeleteProductCatalogue(request, serializer, action, pk):
            array_dict_add_del_log_detail = {}
            array_dict_add_dele_log = {}
            productgroupval = serializer.data['productgroup']
            producttypeval = serializer.data['producttype']
            productnameval = serializer.data['productname']
            catid = serializer.data['catrefid']
            rtlmemoline = serializer.data['rtlmemoline']
            productgroup = ProductcatalogueProperty.objects.getCataloguePropertyName('productgroup', str(productgroupval))
            producttype = ProductcatalogueProperty.objects.getCataloguePropertyName('producttype', str(producttypeval))
            productname = ProductcatalogueProperty.objects.getProductName('productname', str(productnameval), str(productgroupval), str(producttypeval))
            rtlmemolinename = ProductcatalogueProperty.objects.getProductName('productmemoline', str(rtlmemoline), str(productgroupval), str(producttypeval)) if str(productgroupval) == '1' else str(rtlmemoline)
            
            #comment= productgroup + ' Product catalogue ' + ' '+ productname+ ' verwijderd'
            comment = productname.cataloguepropertyname +' product met catalogus ID '+ catid + ' verwijderd'
            
            user = getUsername(request)
            catalogue_excluded_fields = ['id', 'startstaffel', 'endstaffel', 'productdescription', 'productstatus']
            ins_id = 0
            array_dict_add_dele_log.update({'action': action, 'update_date': str(timezone.now()), 'product_name' : productname, 'product_type': productgroup, 'updated_by': user, 'comment': comment, 'installbase_id': pk})
            serializerLog = LogSerializerAdd(data=array_dict_add_dele_log)
            if serializerLog.is_valid():
                serializerLog.save()
                ins_id = serializerLog.data['id']

                for (k, v) in serializer.data.items():
                    if k == 'productgroup':
                        product_cat_field_newvalue = productgroup
                    elif k == 'producttype':
                        product_cat_field_newvalue = producttype
                    elif k == 'productname':
                        product_cat_field_newvalue = productname
                    elif k == 'rtlmemoline':
                        product_cat_field_newvalue = rtlmemolinename
                    else :
                        product_cat_field_newvalue = v

                    if k in ['startdate', 'enddate']:
                        product_cat_field_newvalue = formatStringDate(product_cat_field_newvalue)
                        
                    if v != '' and k not in catalogue_excluded_fields:

                        array_dict_add_del_log_detail.update(
                            {'field_name': k, 'old_value': product_cat_field_newvalue, 'new_value': 'verwijderd',
                            'productauditlog': ins_id})

                        serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_add_del_log_detail)
                        if serializerLogdetail.is_valid():
                            serializerLogdetail.save()

def logStatusProductCatalogue(request, serializer, productcataloguedata, action):
            array_dict_status_log = {}
            array_dict_status_log_detail = {}
            productoldstatus = productcataloguedata.data['productstatus']
            newstatus = serializer.data['productstatus']
            
            pk = serializer.data['id']
            status = serializer.data['productstatus']
            if productoldstatus == 0:
                productoldstatus=Gedeactiveerd
            elif productoldstatus == 1:
                productoldstatus=Geactiveerd
            elif productoldstatus == '' or productoldstatus is None:
                productoldstatus = ''
            if newstatus == 0:
                status=Gedeactiveerd
                action = Gedeactiveerd
            else:
                status=Geactiveerd
                action = Geactiveerd
           
            productgroupval = productcataloguedata.data['productgroup']
            producttypeval = productcataloguedata.data['producttype']
            productnameval = productcataloguedata.data['productname']
            catid = productcataloguedata.data['catrefid']
            productgroup = ProductcatalogueProperty.objects.getCataloguePropertyName('productgroup', str(productgroupval))
            producttype = ProductcatalogueProperty.objects.getCataloguePropertyName('producttype', str(producttypeval))
            productname = ProductcatalogueProperty.objects.getProductName('productname', str(productnameval), str(productgroupval), str(producttypeval))
            
            #comment= productgroup + ' Product catalogue ' + ' '+ productname+ ' ' + status 
            comment = productname.cataloguepropertyname +' product met catalogus ID '+ catid + ' ' + status
            
            user = getUsername(request)

            ins_id = 0
            array_dict_status_log.update(
                {'action': action, 'update_date': str(timezone.now()), 'product_name' : productname, 'product_type': productgroup,
                 'updated_by': user, 'comment': comment, 'installbase_id': pk})
            serializerLog = LogSerializerAdd(data=array_dict_status_log)
            if serializerLog.is_valid():
                serializerLog.save()
                ins_id = serializerLog.data['id']
                
            array_dict_status_log_detail.update(
                    {'field_name': 'productstatus', 'old_value': productoldstatus, 'new_value': status,
                     'productauditlog': ins_id})
                     
            serializerLogdetail = ProductAuditlogDetailSerializer(data=array_dict_status_log_detail)
            if serializerLogdetail.is_valid():
                serializerLogdetail.save()

class ProductAuditLogService(APIView):
    def get(self, request, id, catalogueid):
        
        headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', None)}
        logListDict = []
        log = ProductAuditLog.objects.getProductAuditLogList(id)
        serializer = LogSerializer(log, many=True)
        if serializer.data:
            for prodlog in serializer.data:
                logListDict.append({
                    'id': prodlog['id'],
                    'type': 'Producten',
                    'product_name' : prodlog['product_name'],
                    'action': prodlog['action'],
                    'update_date': prodlog['update_date'],
                    'product_type': prodlog['product_type'],
                    'updated_by': prodlog['updated_by'],
                    'location_id': prodlog['location_id'],
                    'comment': prodlog['comment'],
                    'catalogue_id': prodlog['catalogue_id'],
                    'productauditlog': prodlog['productauditlog'],
                    'mailid': 0,
                    'ticketid':0
                })
        result = requests.get(URL_LOCATION_SERVICE+'location_log/'+str(id)+'/' , headers=headers)
        if result.status_code is HTTP_200_OK:
            locationlogList= result.json()
            #print(orderlogList)
            for locationlog in locationlogList:
                type=''
                if locationlog['ticketid'] is not None and locationlog['ticketid'] != 0 and str(locationlog['documentid'])=='0' :
                    type='Ticket'
                elif str(locationlog['documentid'])=='0':
                    type='Locatie'
                logListDict.append({
                    'id': locationlog['id'],
                    'type': type,
                    'action': locationlog['action'],
                    'update_date': locationlog['update_date'],
                    'product_type': locationlog['location_type'],
                    'updated_by': locationlog['updated_by'],
                    'comment': locationlog['comment'],
                    'location_id': locationlog['customer_id'],
                    'catalogue_id': '',
                    'productauditlog': locationlog['locationauditlog'],
                    'mailid': locationlog['mailid'],
                    'ticketid': locationlog['ticketid'],
                    'documentid': locationlog['documentid'],
                })
        
        result = requests.get(URL_ORDER_SERVICE+'order_log/'+str(id)+'/'+str(catalogueid) , headers=headers)
        if result.status_code is HTTP_200_OK:
            orderlogList= result.json()
            #print(orderlogList)
            for orderlog in orderlogList:
                
                orderlogdetailsDict = []
                for orderlogdetails in  orderlog['orderauditlog']:
                    
                    orderlogdetailsDict.append({
                        'field_name': orderlogdetails['fieldname'],
                        'old_value': orderlogdetails['oldvalue'],
                        'new_value': orderlogdetails['newvalue'],
                        'productauditlog': orderlogdetails['orderauditlog']
                    })
                logListDict.append({
                        'id': orderlog['id'],
                        'type': 'Order',
                        #'product_name' : orderlog['product_name'],
                        'action': orderlog['action'],
                        'update_date': orderlog['updatedate'],
                        'product_type': orderlog['producttype'],
                        'updated_by': orderlog['updatedby'],
                        'location_id': orderlog['locationid'],
                        'comment': orderlog['comment'],
                        'catalogue_id': orderlog['catalogueid'],
                        'productauditlog': orderlogdetailsDict,
                        'mailid': 0,
                        'ticketid':0
                    })
        
        sorted_date = sorted(logListDict, key=lambda x: x['update_date'],reverse=True)
        return Response(sorted_date)


def xstr(s):
    if s is None or s == 'None':
        return ''
    return str(s)

def formatStringDate(strdatetime):
    if xstr(strdatetime):
        return datetime.strptime(strdatetime, '%Y-%m-%d').strftime(dateformat)
    else:
        ''
def formatStringDateTime(strdatetime):
    if strdatetime:
        strdatetime = datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
        return strdatetime.astimezone(timezone.get_current_timezone()).strftime(datetimeformat)
    else:
        ''