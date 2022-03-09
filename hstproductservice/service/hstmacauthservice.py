import copy
import json
import requests
import time
import dateutil.parser
from datetime import date, datetime, timedelta
from django.utils.timezone import make_aware
from django.http import JsonResponse
from hstproductservice.model.hstproductmodel import Macauth, Userbandwidth
from hstproductservice.serializer.hstproductserializer import UserbandwidthSerializer, MacauthSerializer
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



class bk_MacauthUserBandwidthData(APIView):
    macuserbandwidthcache = dict()
    def get(self, request):
        if  'macuserbandwidth' in MacauthUserBandwidthData.macuserbandwidthcache:
            serializer = MacauthUserBandwidthData.macuserbandwidthcache['macuserbandwidth']
        else:
            macuserbandwidth = Userbandwidth.objects.getUBListWithDistinct()
            serializer = UserbandwidthSerializer(macuserbandwidth, many=True)
            MacauthUserBandwidthData.macuserbandwidthcache['macuserbandwidth'] = serializer
        return JsonResponse(serializer.data, safe=False)





class MacauthUserBandwidthData(APIView):
    macuserbandwidthcache = dict()
    def get(self, request):
        if  'macuserbandwidth' in MacauthUserBandwidthData.macuserbandwidthcache:
            macub_list = MacauthUserBandwidthData.macuserbandwidthcache['macuserbandwidth']
        else:
            userbandwidthdownload = Userbandwidth.objects.getUBListWithDistinctDownload()
            UBDownloadSrlzr = UserbandwidthSerializer(userbandwidthdownload, many=True)
            userbandwidthupload = Userbandwidth.objects.getUBListWithDistinctUpload()
            UBUploadSrlzr = UserbandwidthSerializer(userbandwidthupload, many=True)
            
            macub_list = []
            if UBDownloadSrlzr.data:
                for macub in UBDownloadSrlzr.data:
                    macub_list.append({"id": macub['id'],"type": "download","profile": macub['profile'],"download": macub['download']})
            if UBUploadSrlzr.data:
                for macub in UBUploadSrlzr.data:
                    macub_list.append({ "id": macub['id'],"type": "upload","profile": macub['profile'],"upload": macub['upload'] })
            MacauthUserBandwidthData.macuserbandwidthcache['macuserbandwidth'] = macub_list
        return JsonResponse(macub_list, safe=False)

class MacauthCreateView(APIView):
    def get(self, request, pk):
        try:
            macauthdata = self.get_object(pk)
            serializer = MacauthSerializer(macauthdata)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Macauth.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return Macauth.objects.getMac(pk)
        except Macauth.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST

    def post(self, request):
        request.data['startname'] = getUsername(request)
        serializer = MacauthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logAddMacauth(request, serializer, 'Aangemaakt')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        macauth = self.get_object(pk)
        request.data['startname'] = getUsername(request)
        serializerbefore = MacauthSerializer(macauth).data
        serializer = MacauthSerializer(macauth, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            logUpdateMacauth(request, serializerbefore, serializer, 'Aangepast', pk)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        
        macauth = Macauth.objects.getMac(pk)
        serializer = MacauthSerializer(macauth)
        
        if serializer.data:
            logDeleteMacauth(request, serializer, 'Verwijderd')
            Macauth.objects.filter(pk=pk).delete()
        return Response({"message": "Record Deleted"}, status=status.HTTP_200_OK)


class MacauthListView(APIView):
    def get(self, request, locationid):
        try:
            macauthdata = Macauth.objects.getMacListByLocation(locationid)
            serializer = MacauthSerializer(macauthdata, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Macauth.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)