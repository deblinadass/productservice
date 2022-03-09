import copy
import json
import requests
import time
import dateutil.parser
from datetime import date, datetime, timedelta
from django.utils.timezone import make_aware
from django.http import JsonResponse
from hstproductservice.model.hstproductmodel import Macauth, ProductAttribute, ProductProperty, Userbandwidth
from hstproductservice.serializer.hstproductserializer import ProductAttributeSerializer, ProductPropertySerializer, UserbandwidthSerializer, MacauthSerializer
from hstproductservice.service.hstlogservice import getUsername, logUpdateMacauth, logAddMacauth, logDeleteMacauth
from hstproductservice.hstproductserviceconfig import JWT_KEYWORD
from rest_framework import exceptions
from rest_framework.views import APIView
from django.http import Http404
import jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import json
from rest_framework.status import (
    HTTP_200_OK
)
from django.utils import timezone


class Productattribute(APIView):
    productattribuecache = dict()
    def get(self, request, catalogueid):
        #logger_info(request, 'Productattribute get()', 'Parameters:' + str(catalogueid))
        if  catalogueid in Productattribute.productattribuecache:
            serializer = Productattribute.productattribuecache[catalogueid]
        else:
            productinstallbase = ProductAttribute.objects.getProductaAttributesList(catalogueid).order_by('id')
            serializer = ProductAttributeSerializer(productinstallbase, many=True)
            Productattribute.productattribuecache[catalogueid] = serializer
        return JsonResponse(serializer.data, safe=False)


class ProductAttributePropertyList(APIView):
    productattributepropertylistcache = dict()
    def get(self, request, catalogueid):
        #logger_info(request, 'ProductAttributePropertyList get()', 'Parameters:' + str(catalogueid)+ ''+ str(attribute))
        if  (str(catalogueid)) in ProductAttributePropertyList.productattributepropertylistcache:
            serializer = ProductAttributePropertyList.productattributepropertylistcache[str(catalogueid)]
            #print(serializer)
        else:
            productinstallbase = ProductProperty.objects.getPropertyListByCatId(catalogueid)
            
            serializer = ProductPropertySerializer(productinstallbase, many=True)
            ProductAttributePropertyList.productattributepropertylistcache[str(catalogueid)] = serializer
            #print(ProductAttributePropertyList)
        return JsonResponse(serializer.data, safe=False)