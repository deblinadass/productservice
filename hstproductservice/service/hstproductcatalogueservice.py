import copy
import json
import requests
import time
import dateutil.parser
from datetime import date, datetime, timedelta
from django.utils.timezone import make_aware
from django.http import JsonResponse
from hstproductservice.model.hstproductmodel import getproductcatalogueid, Productcatalogue, ProductcatalogueProperty
from hstproductservice.serializer.hstproductserializer import ProductCataloguePropertyAllSerializer, \
    ProductCatalogueAllSerializer, ProductCatalogueChangeStatusSerializer
from hstproductservice.service.hstlogservice import logAddProductCatalogue, logUpdateProductCatalogue, logDeleteProductCatalogue, logStatusProductCatalogue
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

productcataloguecache = dict()

def getUserRole(request):
        
        token = request.META.get('HTTP_AUTHORIZATION')
        tokenarr = token.split()
        token = tokenarr[1]
        try:
            decodedtoken = jwt.decode(token, JWT_KEYWORD, algorithm='HS256')
            userrole = decodedtoken.get('role')
            return userrole
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('Token Expired')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Invalid Signature')

class CataloguePropertyNameByAttr(APIView):
    cataloguepropertycache = dict()
    def get(self, request, catalogueprop, cataloguevalue, cataloguepropertygr, cataloguepropertytyp):
        catPropertyList = ProductcatalogueProperty.objects.getProductName(catalogueprop, cataloguevalue, cataloguepropertygr, cataloguepropertytyp)
        serializer = ProductCataloguePropertyAllSerializer(catPropertyList)
        return JsonResponse(serializer.data, safe=False)

class CataloguePropertyByGroup(APIView):
    def get(self, request, cataloguepropertygroup):
        catPropertyList = ProductcatalogueProperty.objects.getProductCatalogueByGroup(cataloguepropertygroup)
        serializer = ProductCataloguePropertyAllSerializer(catPropertyList, many=True)
        #CataloguePropertyData.cataloguepropertycache[catalogueproperty] = serializer
        return JsonResponse(serializer.data, safe=False)

class CataloguePropertyData(APIView):
    cataloguepropertycache = dict()
    def get(self, request, catalogueproperty):
        if  catalogueproperty in CataloguePropertyData.cataloguepropertycache:
            serializer = CataloguePropertyData.cataloguepropertycache[catalogueproperty]
        else:
            catPropertyList = ProductcatalogueProperty.objects.getPropertyList(catalogueproperty)
            serializer = ProductCataloguePropertyAllSerializer(catPropertyList, many=True)
            CataloguePropertyData.cataloguepropertycache[catalogueproperty] = serializer
        return JsonResponse(serializer.data, safe=False)

class CataloguePropertyName(APIView):
    cataloguepropertycache = dict()
    def get(self, request, productgroup,producttype):
        catPropertyList = ProductcatalogueProperty.objects.getProductCatalogueNameList(productgroup,producttype)
        serializer = ProductCataloguePropertyAllSerializer(catPropertyList, many=True)
        return JsonResponse(serializer.data, safe=False)

class ProductCatalogueCreateView(APIView):

    def get(self):
        productcatalogue = Productcatalogue.objects.getProductCatalogueList()
        serializer = ProductCatalogueAllSerializer(productcatalogue, many=True)
        return JsonResponse(serializer.data, safe=False)

    def get_object(self, pk):
        try:
            return Productcatalogue.objects.getCatalogue(pk)
        except Productcatalogue.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST

    def put(self, request, pk):
        productcatalogue = self.get_object(pk)
        serializerbefore = ProductCatalogueAllSerializer(productcatalogue).data

        if request.data['locationids']!= '' and str(request.data['locationids']) != "['']":
            request.data['locationids'] = str(request.data['locationids']).split(',')
        else:
            request.data['locationids'] = list(" ")
        if 'userrole' in request.data and  request.data['userrole']!= '' and str(request.data['userrole']) != "['']":
            request.data['userrole'] = str(request.data['userrole']).split(',')
        else:
            request.data['userrole'] = list(" ")
        serializer = ProductCatalogueAllSerializer(productcatalogue, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            logUpdateProductCatalogue(request, serializerbefore, serializer, 'Aangepast', pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        request.data['catrefid'] = getproductcatalogueid()
        request.data['productstatus'] = 0
        
        if request.data['locationids'] != '':
            request.data['locationids'] = str(request.data['locationids']).split(',')
        else:
            request.data['locationids'] = list(" ")
        if 'userrole' in request.data and  request.data['userrole']!= '':
            request.data['userrole'] = str(request.data['userrole']).split(',')
        else:
            request.data['userrole'] = list(" ")
        print(request.data)
        serializer = ProductCatalogueAllSerializer(data=request.data)
        data=''
        if serializer.is_valid():
            serializer.save()
        
            logAddProductCatalogue(request, serializer, 'Aangemaakt')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # return Response(pk)
        try:
            productcatalogue = Productcatalogue.objects.getCatalogue(pk)
            serializer = ProductCatalogueAllSerializer(productcatalogue)
            Productcatalogue.objects.filter(id=pk).delete()
            # return Response(serializer.data)
            productdata=json.dumps(serializer.data)

            if serializer.data:
                logDeleteProductCatalogue(request, serializer, 'Verwijderd', pk)
                return Response({"message": "Record Deleted"}, status=status.HTTP_200_OK)
        except Productcatalogue.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST

class ProductCatalogueChangeStatus(APIView):
    
    def get_object(self, pk):
        try:
            return Productcatalogue.objects.getCatalogueByID(pk)
        except Productcatalogue.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', None)}
        productcatalogue = self.get_object(pk)
        print(request.data)
        #save deactivate data to DB
        serializer = ProductCatalogueChangeStatusSerializer(productcatalogue, data=request.data)
        if serializer.is_valid():
            productcataloguedetail = Productcatalogue.objects.getCatalogue(pk)
            serializerCatalogueDetail = ProductCatalogueAllSerializer(productcataloguedetail)
            serializer.save()
            logStatusProductCatalogue(request, serializer, serializerCatalogueDetail,'status changed')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductCatalogueFilterByDateList(APIView):
    def get(self, request, productcatalogue, creationdate, ordertype, locationid):
        userrole=getUserRole(request)
        print(userrole)
        creationdate = make_aware(datetime.strptime(creationdate, '%Y-%m-%d'))
        productcatalogueMain = Productcatalogue.objects.getProductCatalogueByDateMain(productcatalogue,creationdate,ordertype, locationid, userrole)
        productcatalogueserializerMain = ProductCatalogueAllSerializer(productcatalogueMain, many=True)
        productcatalogueAddOn = Productcatalogue.objects.getProductCatalogueByDateAddOn(productcatalogue,creationdate,ordertype, locationid)
        productcatalogueserializerAddOn = ProductCatalogueAllSerializer(productcatalogueAddOn, many=True)
        catalogueproperty = ProductcatalogueProperty.objects.getPropertyList('productname')
        cataloguepropertyserlzr = ProductCataloguePropertyAllSerializer(catalogueproperty, many=True)
        #print(productcatalogueserializerMain.data)
        productcatalogue_list = []
        if productcatalogueserializerMain.data:
            for productcatalogue in productcatalogueserializerMain.data:
                productnamevalue = [x for x in list(cataloguepropertyserlzr.data) if x["cataloguepropertygroup"] == productcatalogue['productgroup'] and x["cataloguepropertytype"] == productcatalogue['producttype'] and x["cataloguepropertyvalue"] == productcatalogue['productname']][0]['cataloguepropertyname']
                productcatalogue_list.append({
                        "id": productcatalogue['id'],
                        "catrefid": productcatalogue['catrefid'],
                        "productgroup": productcatalogue['productgroup'],
                        "producttype": productcatalogue['producttype'],
                        "productname" : productcatalogue['productname'],
                        "productnamesort" : int(productcatalogue['productname']),
                        "productnamevalue" : productnamevalue,
                        "startdate": productcatalogue['startdate'],
                        "enddate": productcatalogue['enddate'],
                        "productprice": productcatalogue['productprice'],
                        "pieceperproduct" : productcatalogue['pieceperproduct'],
                        "maximumquantity" : productcatalogue['maximumquantity'],
                        "rtlmemoline" : productcatalogue['rtlmemoline'],
                        #"locationid": productcatalogue['locationids'],
                        #"productuserrole" : None if not productuserrole else list(productuserrole)
                    })
        if productcatalogueserializerAddOn.data:
            for productcatalogue in productcatalogueserializerAddOn.data:
                productnamevalue = [x for x in list(cataloguepropertyserlzr.data) if x["cataloguepropertygroup"] == productcatalogue['productgroup'] and x["cataloguepropertytype"] == productcatalogue['producttype'] and x["cataloguepropertyvalue"] == productcatalogue['productname']][0]['cataloguepropertyname']
                productcatalogue_list.append({
                        "id": productcatalogue['id'],
                        "catrefid": productcatalogue['catrefid'],
                        "productgroup": productcatalogue['productgroup'],
                        "producttype": productcatalogue['producttype'],
                        "productname" : productcatalogue['productname'],
                        "productnamesort" : int(productcatalogue['productname']),
                        "productnamevalue" : productnamevalue,
                        "startdate": productcatalogue['startdate'],
                        "enddate": productcatalogue['enddate'],
                        "productprice": productcatalogue['productprice'],
                        "pieceperproduct" : productcatalogue['pieceperproduct'],
                        "maximumquantity" : productcatalogue['maximumquantity'],
                        "rtlmemoline" : productcatalogue['rtlmemoline'],
                        #"locationid": productcatalogue['locationids'],
                    })
            
        if productcatalogue_list:
            productcatalogue_list.sort(key=lambda e: e['productnamesort'])
            
        return JsonResponse(productcatalogue_list, safe=False)


class ProductCatalogue(APIView):
    def get(self, request):
        productcatalogue = Productcatalogue.objects.getProductCatalogue()
        serializer = ProductCatalogueAllSerializer(productcatalogue, many=True)
        return JsonResponse(serializer.data, safe=False)

class ProductCatalogueProperty(APIView):
    productcataloguepropertycache = dict()
    def get(self, request):
        if  'productcatalogueproprty' in ProductCatalogueProperty.productcataloguepropertycache:
            serializer = ProductCatalogueProperty.productcataloguepropertycache['productcatalogueproprty']
        else:
            productcatalogueproperty = ProductcatalogueProperty.objects
            serializer = ProductCataloguePropertyAllSerializer(productcatalogueproperty, many=True)
            ProductCatalogueProperty.productcataloguepropertycache['productcatalogueproprty'] = serializer
        return JsonResponse(serializer.data, safe=False)

def resetproductcataloguecache():
    productcataloguecache.clear()


    


            