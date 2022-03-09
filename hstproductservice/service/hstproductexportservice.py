import xlsxwriter
import json
from io import BytesIO
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from xlsxwriter.utility import xl_rowcol_to_cell
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.compat import requests
from hstproductservice.hstproductserviceconfig import URL_LOCATION_SERVICE, product_macauth_export, product_macauth_column_width, product_macauth_export_position 
from hstproductservice.serializer.hstproductserializer import UserbandwidthSerializer
from hstproductservice.model.hstproductmodel import Macauth, Userbandwidth



datetimeformat = "%d-%m-%Y %H:%M"
dateformat = "%d-%m-%Y"

@csrf_exempt
@api_view(["get"])
@permission_classes((AllowAny,))
def productExport(request, product):
    timestampStr = timezone.localtime(timezone.now()).strftime(datetimeformat)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' +'Order Marketing -{}.xlsx'.format(timestampStr)
    xlsx_data = WriteToExcel(product,request)
    response.write(xlsx_data)
    return response

def WriteToExcel(exportparam,request):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    bold = workbook.add_format({'bold': True})
    currency_format = workbook.add_format({'num_format': '###0.00'})


    if str(exportparam) == '3':
        worksheet_dict = product_macauth_export
        worksheet_dict_position = product_macauth_export_position
        worksheet_dict_column_width = product_macauth_column_width
    
    column_list = None
    
    headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', None)} 
    satellite_locations = requests.get(URL_LOCATION_SERVICE + 'getsatellitelocationlist/', headers=headers)    
    satellite_locations_dict = json.loads(satellite_locations.json()) 

    userbandwidth_list = Userbandwidth.objects.getUBList()
    userbandwidth_list = UserbandwidthSerializer(userbandwidth_list, many=True)
    #print(userbandwidth_list)
    for sheetname in worksheet_dict.keys():
        worksheet = workbook.add_worksheet(sheetname)
        col=0
        row=0
        column_list=worksheet_dict_position[sheetname]
        for headername,headerwidth in zip(worksheet_dict[sheetname],worksheet_dict_column_width[sheetname]):
            worksheet.write(xl_rowcol_to_cell(row, col),headername, bold)
            worksheet.set_column(col, col, headerwidth)
            col+=1
        row+=1

        macauthlists = Macauth.objects.getMacList().values('pk','userbandwidth_id','macaddress','startdate','enddate','remark','location_id')
            
        for macauth in macauthlists:
            mainlocationId = [x["parentcustomerid"] for x in satellite_locations_dict if x["customerid"] == macauth['location_id']][0]
            main_locations = requests.get(URL_LOCATION_SERVICE + 'mainlocationData/' + str(mainlocationId), headers=headers).json()
            
            userbandwidthname = [x["description"] for x in userbandwidth_list.data if x["id"] == macauth['userbandwidth_id']][0] if macauth['userbandwidth_id']!=0 else ''
                
            if str(exportparam) == '3':
                satCustomerName = [x["customername"] for x in satellite_locations_dict if x["customerid"] == macauth['location_id']][0]
                worksheet.write(xl_rowcol_to_cell(row, 0),str(mainlocationId))
                worksheet.write(xl_rowcol_to_cell(row, 1),main_locations[0]['customername'])
                worksheet.write(xl_rowcol_to_cell(row, 2),xstr(macauth['location_id']))
                worksheet.write(xl_rowcol_to_cell(row, 3),satCustomerName)
                worksheet.write(xl_rowcol_to_cell(row, 4),xstr(macauth['macaddress']))
                worksheet.write(xl_rowcol_to_cell(row, 5),xstr(userbandwidthname))
                worksheet.write(xl_rowcol_to_cell(row, 6),formatStringDateTime(xstr(macauth['startdate'])))
                worksheet.write(xl_rowcol_to_cell(row, 7),formatStringDateTime(xstr(macauth['enddate'])))
                worksheet.write(xl_rowcol_to_cell(row, 8),xstr(macauth['remark']))
                
            row+=1

    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data

def xstr(s):
    if s is None or s == 'None':
        return ''
    return str(s)

def xstrNum(s):
    if s is None or s == 'None' or not s:
        return '0.00'
    return str(s).replace(',','.')

def formatDateTime(strdatetime):
    if strdatetime:
        return strdatetime.astimezone(timezone.get_current_timezone()).strftime(datetimeformat)
    else:
        ''
def formatStringDateTime(strdatetime):
    if xstr(strdatetime):
        return datetime.strptime(strdatetime, '%Y-%m-%d').strftime(dateformat)
    else:
        ''
