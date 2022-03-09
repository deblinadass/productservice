'''
Created on 27 jan. 2020

 :  500
'''

from rest_framework import serializers

from hstproductservice.model.hstproductmodel import Macauth, Productcatalogue, ProductAttribute, ProductInstallbase, \
    ProductAttributeValue, Location, ProductProperty, ProductAuditLog, ProductAuditLogDetail, Producttabs, \
    ProductConfigurationHistory, Productstatus, ProductcatalogueProperty, Userbandwidth
from django.utils import timezone

class ProducttabsSerializer(serializers.ModelSerializer):
    class Meta:
      model = Producttabs
      fields = ('id','label','icon','link','indexno')
      ordering = ['id']
        
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False)
        

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
      model = ProductAttribute
      fields = ('id','attributename','productcatalogue')
      ordering = ['id']
      
class ProductAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = '__all__'

class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productcatalogue
        fields = [
            'id'
        ]


class ProductInstallbaseDetailsSerializer(serializers.ModelSerializer):

    productattributevaluesi= serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    billingstartdate = serializers.DateField(format='%d-%m-%Y', allow_null=True)
    class Meta:
        model = ProductInstallbase
        fields = ['id','productid','productcreationdate','billingstartdate', 'productactivationdate', 'productdeactivationdate', 'productattributevaluesi', 'productremarks', 'ponumber', 'orderid']



        
        
class ProductOrderInstallbaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInstallbase
        fields = ['id','productid', 'productcreationdate', 'productactivationdate', 'billingstartdate',  'productcatalogue', 'location','status','productremarks', 'ponumber', 'orderid', 'parentproductid']
    
        
            
class ProductInstallbaseRelocateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    location_id = serializers.IntegerField()
    class Meta:
      model = ProductInstallbase

    def create(self, validated_data):
        """
        Create and return a new `location` instance, given the validated data.
        """
        return Location.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        #instance.id = validated_data.get('id', instance.id)
        instance.location_id = validated_data.get('location_id', instance.location_id)
        
        instance.save()
        return instance
        
class ProductInstallbaseChangeStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.IntegerField()
    class Meta:
      model = ProductInstallbase

    def update(self, instance, validated_data):
        if (instance.status == 1):
            instance.productdeactivationdate = timezone.now()
            instance.status = validated_data.get('status', instance.status)
            instance.save()
            return instance
        else:
            instance.productactivationdate = timezone.now()
            instance.status = validated_data.get('status', instance.status)
            instance.save()
            return instance

class ProductCatalogueChangeStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    productstatus = serializers.IntegerField()
    class Meta:
      model = Productcatalogue

    def update(self, instance, validated_data):
        if (instance.productstatus == 1):
            instance.productstatus = validated_data.get('productstatus', instance.productstatus)
            instance.save()
            return instance
        else:
            instance.productstatus = validated_data.get('productstatus', instance.productstatus)
            instance.save()
            return instance


class ProductCatalogueSerializer(serializers.ModelSerializer):
    productattribute = serializers.StringRelatedField(many=True)

    class Meta:
        model = Productcatalogue
        fields = ['productname', 'producttype', 'productdescription', 'productattribute']
        
class ProductCatalogueListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='productname')
    class Meta:
      model = ProductProperty
      fields = (
        'id',
        'name',
      )
class UserbandwidthSerializer(serializers.ModelSerializer):
    class Meta:
      model = Userbandwidth
      fields = (
        'id',
        'profile' ,
        'download',
        'upload',
        'description',
        'serviceinfo',
      )

class MacauthSerializer(serializers.ModelSerializer):
    class Meta:
      model = Macauth
      fields = (
        'id',
        'macaddress' ,
        'location_id',
        'chain_id',
        'startdate',
        'enddate',
        'ubprofile',
        'billing',
        'startname',
        'ubprofiledownload',
        'ubprofileupload',
        'remark'
      )

class ProductCatalogueAllSerializer(serializers.ModelSerializer):
   # name = serializers.CharField(source='productname')
    class Meta:
      model = Productcatalogue
      fields = (
        'id',
        'catrefid' ,
        'productgroup',
        'producttype',
        'productname',
        'startdate',
        'enddate',
        'productprice',
        'startstaffel',
        'endstaffel',
        'rtlmemoline',
        'wsmemoline',
        'productstatus',
        'productdescription',
        'pieceperproduct',
        'maximumquantity',
        'locationids',
        'userrole'
      )

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
      model = Location
      fields = (
        'name',
        'model',
        'type'

      )

class ProductPropertySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='productpropertyvalue')
    name = serializers.CharField(source='productpropertyname')
    class Meta:
      model = ProductProperty
      fields = (
        'id',
        'name',
        'productattribute_id'
      )
      
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['customername','status','customertypeid']



class ProductAttributeValueDetailSerializer(serializers.ModelSerializer):
        productattributevalue=serializers.JSONField()
        class Meta:
            model = ProductAttributeValue
            fields = ['id', 'productattributevalue', 'productattribute']
            
        def to_internal_value(self, data):
            ret = super(ProductAttributeValueDetailSerializer, self).to_internal_value(data)
            if ret['productattributevalue']:
                ret['productattributevalue'] = str(ret['productattributevalue'])
    
            return ret


class ProductInstallbaseDetailSerializer(serializers.ModelSerializer):
    #productcataloguegroup = serializers.ReadOnlyField(source='productcatalogue.productgroup', read_only=True)
    class Meta:
        model = ProductInstallbase
        fields = ['id','productid', 'productcreationdate','billingstartdate', 'productcatalogue', 'location','status', 'productremarks', 'ponumber', 'orderid', 'parentproductid','productdeactivationdate']
      
      
      

class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
      model = ProductAttributeValue
      fields = (
        'productattribute',
        'productattributevalue'
      )
      
    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        #instance.id = validated_data.get('id', instance.id)
        instance.productattributevalue = validated_data.get('status', instance.productattributevalue)
        
        instance.save()
        return instance


class ProductInstallbaseSerializer(serializers.ModelSerializer):
    productattributevaluesi = ProductAttributeValueSerializer(many=True,read_only=True)
    #productcreationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    #productactivationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    #productdeactivationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M') 
    billingstartdate = serializers.DateField(format='%d-%m-%Y', allow_null=True)
    class Meta:
      model = ProductInstallbase
      fields = (
        #'productinstallbasef',
        'id',
        'productid',
        'status',
        'productcreationdate',
        'billingstartdate',
		'productactivationdate',
        'productdeactivationdate',
        'productattributevaluesi',
        'productremarks',
        'ponumber',
        'orderid',
        'location'
      )
      
     

class ProductInstallbaseZtvSerializer(serializers.ModelSerializer):
    productattributevaluesi = ProductAttributeValueSerializer(many=True,read_only=True)
    #productcreationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    productactivationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    productdeactivationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M') 
    class Meta:
      model = ProductInstallbase
      fields = (
        #'productinstallbasef',
        'id',
        'productid',
        'status',
        'parentproductid',
        'productcatalogue_id',
        'productcreationdate',
        'billingstartdate',
		'productactivationdate',
        'productdeactivationdate',
        'productattributevaluesi',
        'productremarks',
        'ponumber',
        'orderid',
        'billingstartdate',
        'productid'
      )
      
class ProductInstallbaseAccessSerializer(serializers.ModelSerializer):
    productattributevaluesi = ProductAttributeValueSerializer(many=True,read_only=True)
    productcreationdate = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    class Meta:
        model = ProductInstallbase
        fields = (
            'id',
            'productid',
            'status',
            'parentproductid',
            'productcreationdate',
            'billingstartdate',
            'productactivationdate',
            'productdeactivationdate',
            'productattributevaluesi',
            'productremarks',
            'ponumber',
            'orderid',
            'billingstartdate',
            'productid'
          )


class ProductInstallbaseBillingSerializer(serializers.ModelSerializer):
    productattributevaluesi = ProductAttributeValueSerializer(many=True,read_only=True)
    class Meta:
      model = ProductInstallbase
      fields = (
        'id',
        'productid',
        'status',
        'location',
        'productactivationdate',
        'productdeactivationdate',
        'productattributevaluesi'
      )

class ProductConfigurationHistorySerializer(serializers.ModelSerializer):
    configurationdate = serializers.DateTimeField(format='%Y-%m-%d') 
    class Meta:
        model = ProductConfigurationHistory
        fields = (
            'productinstallbase_id', 
            'configurationdate',
            'configuration',
            'basic_cas_service',
            'fox_cas_service',
            'mvh_cas_service',
            'basiccasservice_price',
            'foxcasservice_price',
            'mvhcasservice_price',
            'basiccasservice_viewing_point',
            'foxcasservice_viewing_point',
            'mvhcasservice_viewing_point'

        )

class ProductConfigurationHistoryForBillingSerializer(serializers.ModelSerializer):
    configurationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ProductConfigurationHistory
        fields = (
            'id',
            #'productinstallbase', 
            'configurationdate',
            'configuration',
            'basic_cas_service',
            'fox_cas_service',
            'mvh_cas_service',
            'basiccasservice_price',
            'foxcasservice_price',
            'mvhcasservice_price',
            'basiccasservice_viewing_point',
            'foxcasservice_viewing_point',
            'mvhcasservice_viewing_point'

        )

class ProductConfigurationHistoryForBackupSerializer(serializers.ModelSerializer):
    configurationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ProductConfigurationHistory
        fields = (
            'id',
            'productinstallbase_id', 
            'configurationdate',
            'configuration',
            'basic_cas_service',
            'fox_cas_service',
            'mvh_cas_service',
            'basiccasservice_price',
            'foxcasservice_price',
            'mvhcasservice_price',
            'basiccasservice_viewing_point',
            'foxcasservice_viewing_point',
            'mvhcasservice_viewing_point'

        )


class ProductConfigurationHistoryBillingSerializer(serializers.ModelSerializer):
    configurationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ProductConfigurationHistory
        fields = (
            'id',
            'configurationdate',
            'configuration',
            'billingstartdate',
            'price',
            'viewingpoint',

        )

class ProductInstallbaseBillingCounterSerializer(serializers.ModelSerializer):
    
    productattributevaluesi = ProductAttributeValueSerializer(many=True,read_only=True)
    productactivationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    productdeactivationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    productcreationdate = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    productconfigurationhistory = ProductConfigurationHistoryForBillingSerializer(many=True,read_only=True)
    class Meta:
        model = ProductInstallbase
        fields = (
          'id',
          'productid',
          'status',
          'location',
          'ponumber',
          'productcreationdate',
          'billingstartdate',
          'productactivationdate',
          'productdeactivationdate',
          'productconfigurationhistory',
          'productattributevaluesi'
          )
      
      


class ProductPropertyImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductProperty
        fields = (
            'productattribute',
            'productpropertyname',
            'productpropertyvalue'

        )

class ProductAuditlogDetailSerializer(serializers.ModelSerializer):
    #productauditlog= serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
      model = ProductAuditLogDetail
      fields = (
        'field_name',
        'old_value',
        'new_value',
        'productauditlog'        )
        
class LogSerializer(serializers.ModelSerializer):

    productauditlog = ProductAuditlogDetailSerializer(many=True,read_only=True)

    class Meta:
        model = ProductAuditLog
        fields = (
            'id',
            'action',
            'update_date',
            'product_type',
            'product_name',
            'updated_by',
            'location_id',
            'comment',
            'catalogue_id',
            'import_counter',
            'productauditlog',
            'installbase_id'
        )
        
class LogSerializerAdd(serializers.ModelSerializer):

    #productauditlog = ProductAuditlogDetailSerializer(many=True,read_only=True)

    class Meta:
        model = ProductAuditLog
        fields = (
            'id',
            'action',
            'update_date',
            'product_type',
            'product_name',
            'updated_by',
            'location_id',
            'comment',
            'catalogue_id',
            'import_counter',
            'installbase_id'
        )


class ProductStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Productstatus
        fields = ['id','productcatalogueid', 'status','statustext']
      
class ProductCataloguePropertyAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductcatalogueProperty
        fields = ['id',
	'catalogueproperty',
	'cataloguepropertygroup',
	'cataloguepropertytype' ,
	'cataloguepropertyname',
	'cataloguepropertyvalue',
    'userrole' ]