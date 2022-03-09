import os

JWT_KEYWORD=os.environ['JWT_KEYWORD']
JWT_TOKEN_PREFIX=os.environ['JWT_TOKEN_PREFIX']

URL_LOCATION_SERVICE = 'http://127.0.0.1:8000/customerservice/'
URL_ORDER_SERVICE = 'http://127.0.0.1:8009/orderservice/'
URL_LOGIN_SERVICE = 'http://127.0.0.1:8282/loginservice/'

product_macauth_export = {'Macadres': ['Hoofdlocatie Ref nr','Hoofdlocatie naam','Sublocatie Ref nr','Sublocatie naam','Mac adres','Gebruikersprofiel','Startdatum','Enddatum','Opmerkingen' ]}
product_macauth_export_position = {'Macadres': ['Hoofdlocatie Ref nr','Hoofdlocatie naam','Sublocatie Ref nr','Sublocatie naam','Mac adres','userbandwidth','startdate','enddate','remark']}
product_macauth_column_width = {'Macadres': [18, 60, 16, 60,35,35,15,15,150]}
