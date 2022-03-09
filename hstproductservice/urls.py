'''hstproductservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
'''
from django.urls import path
from hstproductservice.service.hstproductcatalogueservice import  CataloguePropertyNameByAttr, CataloguePropertyData, \
    CataloguePropertyName, ProductCatalogueCreateView, ProductCatalogueChangeStatus, \
    ProductCatalogueFilterByDateList, CataloguePropertyByGroup, ProductCatalogue, ProductCatalogueProperty
from hstproductservice.service.hstlogservice import ProductAuditLogService
from hstproductservice.service.hstmacauthservice import MacauthUserBandwidthData, MacauthCreateView, MacauthListView
from hstproductservice.service.hstproductexportservice import productExport
from hstproductservice.service.hstproductservice import Productattribute, ProductAttributePropertyList
from django.conf.urls import url

urlpatterns = [
    #Product Catalogue 
    path('productservice/catalogueproperty/<str:catalogueproperty>/', CataloguePropertyData.as_view()),
    path('productservice/cataloguename/<str:productgroup>/<str:producttype>/', CataloguePropertyName.as_view()),
    path('productservice/createcatalogue/', ProductCatalogueCreateView.as_view()),
    path('productservice/updatecatalogue/<int:pk>/', ProductCatalogueCreateView.as_view()),
    path('productservice/deletecatalogue/<int:pk>/', ProductCatalogueCreateView.as_view()),
    path('productservice/getfiltercataloguelist/<str:productcatalogue>/<str:creationdate>/<str:ordertype>/<str:locationid>/', ProductCatalogueFilterByDateList.as_view()),
    path('productservice/cataloguepropertybygroup/<str:cataloguepropertygroup>/', CataloguePropertyByGroup.as_view()),
    path('productservice/productcatalogueproperty/', ProductCatalogueProperty.as_view()),
    path('productservice/getpropertynamebyattr/<str:catalogueprop>/<str:cataloguevalue>/<str:cataloguepropertygr>/<str:cataloguepropertytyp>/',CataloguePropertyNameByAttr.as_view() ),
    path('productservice/changecataloguestatus/<int:pk>/', ProductCatalogueChangeStatus.as_view()),
    path('productservice/viewproductcataloguelist/', ProductCatalogue.as_view()),
    path('productservice/product_log/<int:id>/<int:catalogueid>/', ProductAuditLogService.as_view()),
    path('productservice/getuserbandwidth/', MacauthUserBandwidthData.as_view()),
    path('productservice/createmacauth/', MacauthCreateView.as_view()),
    path('productservice/updatemacauth/<int:pk>/', MacauthCreateView.as_view()),
    path('productservice/viewmacauthlist/<int:locationid>/', MacauthListView.as_view()),
    path('productservice/deletemacauth/<int:pk>/', MacauthCreateView.as_view()),
    path('productservice/productexport/<str:product>', productExport),
    path('productservice/productattribute/<int:catalogueid>', Productattribute.as_view()),
    path('productservice/productpropertybycatalogue/<int:catalogueid>', ProductAttributePropertyList.as_view()),
]