
# encoding: UTF-8
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_bleach.models import BleachField
from django.contrib.postgres.fields import ArrayField
from django.db import connection

def getproductcatalogueid():
    cursor = connection.cursor()
    cursor.execute("select nextval('productcatalogueseq_id_seq')")
    result = cursor.fetchone()
    return 'HST-cat-' + str(result[0]).zfill(4)

def getproductid(catalogueid):
    cursor = connection.cursor()
    cursor.execute("select nextval('productid_seq')")
    result = cursor.fetchone()
    if str(catalogueid) == '2':
        return 'HST-acs-' + str(result[0]).zfill(7)
    elif str(catalogueid) == '3':
        return 'HST-ztv-' + str(result[0]).zfill(7)
    


class MacauthManager(models.Manager):
    def getMacDetails(self,product):
        return self.get(id=product)
    def getMac(self, pk):
        return self.get(id = pk)
    def getMacListByLocation(self, locationid):
        return self.get_queryset().filter(location_id=locationid).order_by('-id')
    def getMacList(self):
        return self.get_queryset().filter().order_by('-id')

class Macauth(models.Model):
    id = models.AutoField(primary_key=True)
    macaddress = BleachField(blank=True, default='')
    location_id = models.IntegerField()
    chain_id  = models.IntegerField(default=0)
    startdate = models.DateField(null=True,blank=True, default=None)
    enddate = models.DateField(null=True,blank=True, default=None)
    #userbandwidth_id  = models.IntegerField(default=0)
    billing = models.BooleanField(default=False)
    startname = BleachField(max_length=100,blank=True, default='')
    remark = BleachField(blank=True, default='')
    endname = BleachField(max_length=100,blank=True, default='')
    ubprofile = BleachField(max_length=10, blank=True, default='')
    ubprofileupload = models.IntegerField(default=0)
    ubprofiledownload = models.IntegerField(default=0)

    class Meta:
        db_table = 'macauth'
    objects = MacauthManager()





class UserbandwidthManager(models.Manager):
    def getUBDetails(self,product):
        return self.get(id=product)
    def getUBName(self,product):
        return self.get(id=product).description
    def getUBDownloadName(self,product):
        return self.get(id=product).download
    def getUBUploadName(self,product):
        return self.get(id=product).upload
    def getUBList(self):
        return self.get_queryset().filter().order_by('-id')
    def getUBListWithDistinctDownload(self):
        return self.get_queryset().filter(profile__in = ['DBB','L3']).distinct('profile','download').order_by('download','profile') 
    def getUBListWithDistinctUpload(self):
        return self.get_queryset().filter(profile__in = ['DBB','L3']).distinct('profile','upload').order_by('profile','upload') 

class Userbandwidth(models.Model):
    id = models.AutoField(primary_key=True)
    profile = BleachField(max_length=100,blank=True, default='')
    description = BleachField(max_length=100,blank=True, default='')
    download = BleachField(max_length=100,blank=True, default='')
    upload = BleachField(max_length=100,blank=True, default='')
    serviceinfo = BleachField(max_length=100,blank=True, default='')

    class Meta:
        db_table = 'userbandwidth'

    objects = UserbandwidthManager()

	
        
    


class ProductCatalogueManager(models.Manager):
    def getProductName(self,product):
        return self.get(id=product).productname
    def getProduct(self,product):
        return self.get_queryset().filter(id=product)
    def getProductCatalogueList(self):
        return self.all()
    def getCatalogue(self, catid):
        return self.get(id=catid)
    def getProductCatalogue(self):
        return self.get_queryset().filter().order_by('-id')
    def getCatalogueByID(self, catalogueId):
        return self.get(id = catalogueId)
    def getAllMainCatalogue(self):
        return self.get_queryset().filter(Q(productdescription__isnull=False)).exclude(productdescription__exact='').order_by('id')
    def getProductCatalogueByDate(self,productcatalogue,creationdate):
        return self.get_queryset().filter(startdate__lte=creationdate, enddate__gte=creationdate, productgroup=productcatalogue,productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname','-id')
    def getProductCatalogueID(self,productgroup, productattribute, producttype, creationdate):
        return self.get(startdate__lte=creationdate, enddate__gte=creationdate, productstatus__iexact='1', productgroup=productgroup, producttype=producttype, productname=productattribute).id
    def getProductCatalogueByDateMain(self,productcatalogue,creationdate,ordertype,locationid, userrole):
        if(ordertype == 'add'):
            
            if str(productcatalogue) == "1":
                
                resultset = self.get_queryset().filter(locationids__contains=[locationid], userrole__contains=[userrole], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                if not resultset:
                    
                    resultset = self.get_queryset().filter(locationids__contains=[locationid], userrole__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                if not resultset:
                    
                    resultset = self.get_queryset().filter(locationids__contains=[""], userrole__contains=[userrole], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                if not resultset:
                    
                    resultset = self.get_queryset().filter(locationids__contains=[""], userrole__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                return resultset
            else:
                resultset = self.get_queryset().filter( startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                #if not resultset:
                #    resultset = self.get_queryset().filter(locationids__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
                return resultset
        else:
            resultset = self.get_queryset().filter( startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            #if not resultset:
            #    resultset = self.get_queryset().filter(locationids__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            return resultset

    def getProductCatalogueByDateAddOn(self,productcatalogue,creationdate,ordertype,locationid):
        if(ordertype == 'add'):
            resultset = self.get_queryset().filter(startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='2',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            #if not resultset:
            #    resultset = self.get_queryset().filter(locationids__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='2',productstatus__iexact='1').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            return resultset
        else:
            resultset = self.get_queryset().filter(startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='2').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            #if not resultset:
            #    resultset = self.get_queryset().filter(locationids__contains=[""], startdate__lte=creationdate,enddate__gte=creationdate,productgroup=productcatalogue, producttype='2').distinct('producttype','productname').order_by('-producttype','-productname', '-id') 
            return resultset
    
class Productcatalogue(models.Model):
    id = models.AutoField(primary_key=True)
    catrefid = BleachField(max_length=100,blank=True, default='')
    productgroup = BleachField(max_length=2,blank=True, default='')
    producttype = BleachField(max_length=2,blank=True, default='')
    productname = BleachField(max_length=100,blank=True, default='')
    startdate = models.DateField(null=True,blank=True, default='')
    enddate = models.DateField(null=True,blank=True, default='')
    productprice = BleachField(max_length=10,blank=True, default='')
    startstaffel = models.IntegerField()
    endstaffel = models.IntegerField()
    rtlmemoline = BleachField(max_length=50,blank=True, default='')
    wsmemoline = BleachField(max_length=50,blank=True, default='')
    productstatus = models.IntegerField()
    relatedvve = BleachField(max_length=50,blank=True, default='')
    productdescription = BleachField(max_length=100,blank=True, default='')
    pieceperproduct = BleachField(max_length=100,blank=True, default='')
    maximumquantity = models.IntegerField(default=0)
    userrole = ArrayField(BleachField(max_length=255,blank=True, null=True))
    locationids = ArrayField(BleachField(max_length=255, blank=True, null=True))

    class Meta:
        db_table = 'productcatalogue'
    objects = ProductCatalogueManager()

    def __str__(self):
        return '%s, %s' % (self.productname, self.producttype)

class ProductAttributeManager(models.Manager):
    def getProductaAttributesList(self, product):
        return self.filter(productcatalogue = product).order_by('id')
    def getProductaAttributes(self, attributeid):
        return self.filter(id = attributeid)
        
class ProductAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    productcatalogue = models.ForeignKey(Productcatalogue, related_name='productattribute', on_delete=models.CASCADE)
    attributename = BleachField(max_length=100)

    class Meta:
        db_table = 'productattribute'
    objects = ProductAttributeManager()

    def __str__(self):
        return '%s' % (self.attributename)

class Location(models.Model):
    customerid = models.AutoField(primary_key=True)
    customername = BleachField(max_length=100, blank=True, default='')
    housenumber = BleachField(max_length=100, blank=True, default='')
    housenumberaddition = BleachField(max_length=100, blank=True, default='')
    streetname = BleachField(max_length=100)
    postcode = BleachField(max_length=100, blank=True, default='')
    city = BleachField(max_length=100)
    country = BleachField(max_length=100)
    kvknumber = BleachField(max_length=100, blank=True, default='')
    kvkname = BleachField(max_length=100)
    btwnumber = BleachField(max_length=100, blank=True, default='')
    salescloudreferencenumber = BleachField(max_length=100, blank=True, default='')
    netcode = BleachField(max_length=100, blank=True, default='')
    onboardingcompleted = BleachField(max_length=100, blank=True, default='')
    newsitenumber = BleachField(max_length=100, blank=True, default='')
    clientaccountnumber = BleachField(max_length=100, blank=True, default='')
    parentcustomerid = models.IntegerField()
    status = models.IntegerField()
    customertypeid = models.IntegerField(null=True, blank=True)
    contactpersonname = BleachField(max_length=100, blank=True, default='')
    contactpersontelephone = BleachField(max_length=100, blank=True, default='')
    contactpersonfunction = BleachField(max_length=100, blank=True, default='')
    contactpersonemail = BleachField(max_length=100, blank=True, default='')
    billingmodel = BleachField(max_length=100, blank=True, default='')
    ponumber = BleachField(max_length=100, blank=True, default='')
    regelreferentie = BleachField(max_length=150, blank=True, default='')
    billingid = BleachField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'customer'
        
class ProductInstallbaseManager(models.Manager):
        def getAllInstallbase(self):
            return self.all()
        def getInstallbaseByID(self, installbaseId):
            return self.get(id = installbaseId)
        def getInstall(self, product):
            return self.get_queryset().filter(productcatalogue = product).order_by('id')
        def getBillingProducts(self, product, startdate):
            return self.get_queryset().filter(Q(productdeactivationdate__gte = startdate) | Q(productdeactivationdate__isnull = True), productcatalogue__productname__iexact = product)
        def getInstallbaseList(self, location_id, catalogueid):
            return self.get_queryset().filter(location_id=location_id, productcatalogue_id = catalogueid).order_by('-productcreationdate')
        def getInstallbaseZtvList(self, location_id, catalogueid):
            #return self.get_queryset().filter(location_id=location_id, productcatalogue_id = catalogueid).order_by('-id','-parentproductid')
            return self.get_queryset().filter(location_id=location_id, productcatalogue_id__in=Productcatalogue.objects.filter(productgroup = 3).values_list('id', flat=True))
        def getInstallbaseAccessList(self, location_id, catalogueid):
            return self.get_queryset().filter(location_id=location_id, productcatalogue_id = catalogueid).order_by('-id','-parentproductid')
        def getAddonInstallbase(self, installbaseId):
            return self.get_queryset().filter(parentproductid = installbaseId)
            #.values('id')
        def getInstallbaseSingle(self, installbaseid):
            return self.get_queryset().filter(id=installbaseid).order_by('-productcreationdate')
        def getInstallbase(self, installbaseId):
            return self.get_queryset().filter(id = installbaseId)
        def getInstallbaseAll(self, installbaseId):
            return self.get_queryset().filter(Q(id = installbaseId) | Q(parentproductid = installbaseId))
        def getInstallbaseListForBillingCounter(self, catalogueid):
            return self.get_queryset().filter(productcatalogue_id = catalogueid).order_by('-productcreationdate')
        def updateproductstatusviaorder(self, installbaseId, status):
            if status == 1:
                return self.filter(id = installbaseId).update(status = status,productactivationdate = timezone.now())
            else:
                return self.filter(id = installbaseId).update(status = status,productdeactivationdate = timezone.now())
        def getSatelliteLocationListProduct(self, searchparameter):
            return self.get_queryset().filter(productid__iexact=searchparameter).values('location') 
        def getInstallbaseIDByParentID(self, parentinstallbaseId):
            return self.get_queryset().filter(parentproductid = parentinstallbaseId)
        def getInstallbaseCountPerCustomer(self, customerid):
            return self.get_queryset().filter(location=customerid).count()

        
class ProductInstallbase(models.Model):
    location = models.ForeignKey(Location, related_name='productinstallbase', on_delete=models.CASCADE)
    productcatalogue = models.ForeignKey(Productcatalogue, related_name='productinstallbase', on_delete=models.CASCADE)
    productcreationdate = models.DateTimeField(default = timezone.now)
    productactivationdate = models.DateTimeField(null=True)
    productdeactivationdate = models.DateTimeField(null=True)
    status = models.IntegerField(default=0)
    productremarks = BleachField(max_length=100, blank=True, default='')
    ponumber = BleachField(max_length=30, blank=True, default='')
    orderid = BleachField(max_length=20, blank=True, default='')
    parentproductid =  models.IntegerField(default=0)
    billingstartdate = models.DateField(null=True)
    productid  = BleachField(max_length=50, blank=True,null=True, default='')

    
    class Meta:
        db_table = 'productinstallbase'
        ordering = ['id']
    objects = ProductInstallbaseManager()

class ProductConfigurationHistoryManager(models.Manager):
    def getConfigurationHistory(self, product, startdate, enddate):
        return self.get_queryset().filter(productinstallbase__productcatalogue = product, configurationdate = (startdate, enddate)).order_by(-'configurationdate')
    def getConfigurationHistoryByProductID(self, installbase_id):
        return self.get_queryset().filter(productinstallbase_id = installbase_id).values().order_by('configurationdate', 'productinstallbase_id')
    def getConfigByID(self, installbaseId):
        #return self.get_queryset().filter(productinstallbase_id = installbaseId, configuration = 0).order_by('-id')
        return self.get_queryset().filter(productinstallbase_id = installbaseId, configuration = 0).last()
    def getActiveConfigByID(self, installbaseId):
        #return self.get_queryset().filter(productinstallbase_id = installbaseId, configuration = 0).order_by('-id')
        return self.get_queryset().filter(productinstallbase_id = installbaseId, configuration = 1).first()
    def getConfigHistoryForBillCalculation(self):
        return self.get_queryset().all()
    def getAllConfigHistory(self):
        return self.all()
    
class ProductConfigurationHistory(models.Model):
    #productinstallbase = models.ForeignKey(ProductInstallbase, related_name='productconfigurationhistory', on_delete=models.CASCADE)
    productinstallbase_id = models.IntegerField()
    configurationdate = models.DateTimeField(null=True)
    configuration = models.IntegerField(default=0)
    basic_cas_service = models.SmallIntegerField(default=0)
    fox_cas_service = models.SmallIntegerField(default=0)
    mvh_cas_service = models.SmallIntegerField(default=0)
    basiccasservice_price = models.FloatField(default=0)
    foxcasservice_price = models.FloatField(default=0)
    mvhcasservice_price = models.FloatField(default=0)
    basiccasservice_viewing_point = models.IntegerField(default=0)
    foxcasservice_viewing_point = models.IntegerField(default=0)
    mvhcasservice_viewing_point = models.IntegerField(default=0)
    class Meta:
        db_table = 'productconfigurationhistory'
        ordering = ['configurationdate']
    objects = ProductConfigurationHistoryManager()

class ProductAttributeValueManager(models.Manager):
        def getAllProductAttributeValue(self):
            return self.all()
        def getAttributeByInstallbaseID(self, installbaseId):
            return self.get_queryset().filter(productinstallbasef_id=installbaseId).order_by('id')
        def getAttribute(self, product):
            return self.select_related('productinstallbasef').filter(productinstallbasef__productcatalogue = product)
        def getSatelliteLocationList(self, searchparameter):
            return self.get_queryset().filter(productattributevalue=searchparameter,productattribute__attributename='CASnumber').values('productinstallbasef__location')
        def getAttributeByInstallbaseIDOrderById(self, installbaseId):
            return self.get_queryset().filter(productinstallbasef_id=installbaseId).order_by('productattribute')
        def getListofProductsTobeActivated(self):
            return self.get_queryset().filter(Q(productattribute__attributename='ZTVRfsDate') | Q(productattribute__attributename='AccessRfsDate'), productinstallbasef__productcatalogue__gt = 1, productinstallbasef__status__in=[200,201,300,301], productinstallbasef__productdeactivationdate = None).values('productinstallbasef__pk','productinstallbasef__location','productattributevalue','productinstallbasef__productcatalogue','productinstallbasef__status')
        def getListofProductsTobeDeactivated(self):
            return self.get_queryset().filter(Q(productattribute__attributename='ZTVEndDate') | Q(productattribute__attributename='AccessEndDate'), productinstallbasef__productcatalogue__gt = 1, productinstallbasef__status__in=[210,211,310,311]).values('productinstallbasef__pk','productinstallbasef__location','productattributevalue','productinstallbasef__productcatalogue','productinstallbasef__status')
        def getAttributeValuesByInstallbaseID(self, installbaseId):
            return self.get_queryset().filter(productinstallbasef_id__in=installbaseId).values('id', 'productattribute__attributename', 'productattributevalue', 'productinstallbasef_id')
        def getAttributeValueByID(self, attributevalueId):
            return self.get(pk=attributevalueId)
        def getZTVEndDateAttributeValueRow(self, installbaseid):
            return self.get(productinstallbasef=installbaseid, productattribute__attributename='ZTVEndDate')
        def getAccessEndDateAttributeValueRow(self, installbaseid):
            return self.get(productinstallbasef=installbaseid, productattribute__attributename='AccessEndDate')
class ProductAttributeValue(models.Model):
    id = models.AutoField(primary_key=True)
    productinstallbasef = models.ForeignKey(ProductInstallbase, related_name='productattributevaluesi', on_delete=models.CASCADE)
    productattribute = models.ForeignKey(ProductAttribute, related_name='productattributevalues', on_delete=models.CASCADE)
    productattributevalue = BleachField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'productattributevalue'
        ordering = ['productattribute']
        
    objects = ProductAttributeValueManager()
    
class ProductPropertyManager(models.Manager):
        def getPropertyListByAttr(self, catalogueid, attribute):
            return self.get_queryset().filter(productcatalogue = catalogueid, productattribute__attributename__iexact=attribute)
        def getPropertyListByAttrID(self, catalogueid, attribute, propertyvalue):
            return self.get(productattribute_id=attribute, productcatalogue_id=catalogueid, productpropertyvalue=propertyvalue).productpropertyname
        def getPropertyListByCatId(self, catalogueid):
            return self.get_queryset().filter(productcatalogue = catalogueid)
        def getPropertyList(self, product):
            return self.get_queryset().filter(productcatalogue=product)
        def getProductPropertyAttribute(self, value):
            return self.get_queryset().filter(productpropertyname__iexact=value)
        def getProductPropertyAttributeList(self, attributeid, productcatid, v):
            return self.get_queryset().filter(productattribute_id=attributeid, productcatalogue_id=productcatid, productpropertyvalue=v)
        def getProductPropertyAttributeName(self, propertyvalue, catalogue_id):
            return self.get_queryset().filter(productpropertyvalue=propertyvalue, productattribute_id=2, productcatalogue_id=catalogue_id)
        def getProductPropertyName(self, propertyvalue, catalogue_id, attributename):
            return self.get(productpropertyvalue=propertyvalue, productattribute__attributename=attributename, productcatalogue_id=catalogue_id).productpropertyname
        
class ProductProperty(models.Model):
    productcatalogue = models.ForeignKey(Productcatalogue, related_name='productcatalogue', on_delete=models.CASCADE)
    productattribute = models.ForeignKey(ProductAttribute, related_name='productattribute', on_delete=models.CASCADE)
    productpropertyname = BleachField(max_length=100, blank=True, default='')
    productpropertyvalue = BleachField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'productproperty'
    
    def __str__(self):
        return '%s' % (self.productpropertyname)
    objects = ProductPropertyManager()

    #class Meta:
        #unique_together = ['productcatalogue', 'order']
        #ordering = ['order']

class ProductAuditLogManager(models.Manager):
        def getProductAuditLogAll(self):
            return self.all()
        def getProductAuditLogList(self, locationid):
            return self.get_queryset().filter(location_id = locationid)

class ProductAuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=True, blank=True, default=0)
    update_date = models.DateTimeField(blank=True, null=True)
    action = BleachField(max_length=100, blank=True, default='')
    product_type = BleachField(max_length=100, blank=True, default='')
    product_name = BleachField(max_length=100, blank=True, default='')
    updated_by = BleachField(max_length=100)
    comment = BleachField(max_length=255, null=True, blank=True,)
    catalogue_id = models.IntegerField(null=True, blank=True, default=0)
    import_counter = models.IntegerField(null=True, blank=True, default=0)
    installbase_id = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = 'product_audit_log'
        ordering = ['-update_date']
    objects = ProductAuditLogManager()

class ProductAuditLogDetailManager(models.Manager):
        def getProductAuditLogDetailAll(self):
            return self.all()

class ProductAuditLogDetail(models.Model):
    id = models.AutoField(primary_key=True)
    productauditlog = models.ForeignKey(ProductAuditLog, related_name='productauditlog', on_delete=models.CASCADE)
    field_name = BleachField(max_length=100, blank=True, default='')
    old_value = BleachField(max_length=255, blank=True, null=True)
    new_value = BleachField(max_length=255, blank=True, null=True)


    class Meta:
        db_table = 'product_audit_log_detail'
        ordering = ['id']
    objects = ProductAuditLogDetailManager()
        
class ProducttabsManager(models.Manager):
    def getProductatabsList(self):
        return self.get_queryset().all()
        
class Producttabs(models.Model):
    id = models.AutoField(primary_key=True)
    label = BleachField(max_length=100)
    icon = BleachField(max_length=100)
    link = BleachField(max_length=100)
    indexno = models.IntegerField()

    class Meta:
        db_table = 'producttabs'
    objects = ProducttabsManager()
    
class ProductzTVConfigurationHistoryManager(models.Manager):
    def getLatestRecordConfigurationHistory(self, productinstallbaseid):
        return self.get_queryset().filter(productinstallbaseid = productinstallbaseid).order_by('-id')[0]
    def getConfigurationHistoryByProductID(self, installbase_id):
        return self.get_queryset().filter(productinstallbaseid = installbase_id).values().order_by('configurationdate', 'productinstallbaseid')
    def getConfigByID(self, installbaseId):
        return self.get_queryset().filter(productinstallbaseid = installbaseId, configuration = 300).last()
    def getActiveConfigByID(self, installbaseId):
        return self.get_queryset().filter(productinstallbaseid = installbaseId, configuration = 310).first()

class ProductzTVConfigurationHistory(models.Model):
    productinstallbaseid = models.IntegerField()
    productparentinstallbaseid = models.IntegerField()
    configurationdate = models.DateTimeField(null=True)
    configuration = models.IntegerField(default=0)
    viewingpoint = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    billingstartdate = models.DateField(null=True)
    class Meta:
        db_table = 'productztvconfigurationhistory'
        ordering = ['configurationdate']
    objects = ProductzTVConfigurationHistoryManager()
    
class ProductAccessConfigurationHistoryManager(models.Manager):
    def getLatestRecordConfigurationHistory(self, productinstallbaseid):
        return self.get_queryset().filter(productinstallbaseid = productinstallbaseid).order_by('-id')[0]
    def getConfigurationHistoryByProductID(self, installbase_id):
        return self.get_queryset().filter(productinstallbaseid = installbase_id).values().order_by('configurationdate', 'productinstallbaseid')
    def getConfigByID(self, installbaseId):
        return self.get_queryset().filter(productinstallbaseid = installbaseId, configuration = 200).last()
    def getActiveConfigByID(self, installbaseId):
        return self.get_queryset().filter(productinstallbaseid = installbaseId, configuration = 210).first()
    
class ProductAccessConfigurationHistory(models.Model):
    productinstallbaseid = models.IntegerField()
    productparentinstallbaseid = models.IntegerField()
    configurationdate = models.DateTimeField(null=True)
    configuration = models.IntegerField(default=0)
    viewingpoint = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    billingstartdate = models.DateField(null=True)
    class Meta:
        db_table = 'productaccessconfigurationhistory'
        ordering = ['configurationdate']
    objects = ProductAccessConfigurationHistoryManager()

class ProductstatusManager(models.Manager):
    def getProductStatusAll(self):
            return self.all()
    def getProductStatusList(self, productcatalogueid):
        return self.get_queryset().filter(productcatalogueid = productcatalogueid)
        
class Productstatus(models.Model):
    id = models.AutoField(primary_key=True)
    productcatalogueid = models.IntegerField()
    status = models.IntegerField()
    statustext = BleachField(max_length=30)
    
    class Meta:
        db_table = 'productstatus'
    objects = ProductstatusManager()

class ProductcataloguePropertyManager(models.Manager):
    def getProductcataloguePropertyList(self):
        return self.all()
    def getPropertyList(self, catalogueproperty):
        return self.get_queryset().filter(catalogueproperty = catalogueproperty).order_by('cataloguepropertyvalue')
    
    def getProductCatalogueByGroup(self, productgroup):
        return self.get_queryset().filter(cataloguepropertygroup = productgroup)
    
    def getProductCatalogueNameList(self, productgroup, producttype):
        return self.get_queryset().filter(cataloguepropertygroup = productgroup, cataloguepropertytype=producttype ).order_by('cataloguepropertyvalue')
    def getCataloguePropertyName(self, catalogueprop, cataloguevalue):
        return self.get(catalogueproperty=catalogueprop, cataloguepropertyvalue=cataloguevalue).cataloguepropertyname
    def getProductName(self, catalogueprop, cataloguevalue, cataloguepropertygr, cataloguepropertytyp):
        return self.get(catalogueproperty=catalogueprop, cataloguepropertyvalue=cataloguevalue, cataloguepropertygroup=cataloguepropertygr, cataloguepropertytype=cataloguepropertytyp)
    def getCatalogueProperty(self, cataloguegroup):
        return self.get_queryset().filter(cataloguepropertygroup=cataloguegroup)
        
class ProductcatalogueProperty(models.Model):
    id = models.AutoField(primary_key=True)
    catalogueproperty = BleachField(max_length=100, blank=True, default='')
    cataloguepropertygroup = BleachField(max_length=100, blank=True, default='')
    cataloguepropertytype = BleachField(max_length=100, blank=True, default='')
    cataloguepropertyname = BleachField(max_length=100, blank=True, default='')
    cataloguepropertyvalue = BleachField(max_length=100, blank=True, default='')
    userrole = ArrayField(BleachField(max_length=255, blank=True, null=True))

    class Meta:
        db_table = 'productcatalogueproperty'
        ordering = ['cataloguepropertyvalue']
    objects = ProductcataloguePropertyManager()