from django.db import models
from datetime import date
# Create your models here.

class teams(models.Model):
    id = models.AutoField(primary_key=True)
    teamname = models.CharField(
        max_length=64, verbose_name='组名称', null=False, blank=True)
    teampriv = models.CharField(
        max_length=64, verbose_name='权限id', null=False, blank=True)

class teamcomputer(models.Model):
    id = models.AutoField(primary_key=True)
    teamid = models.IntegerField(
        verbose_name='team id', null=False)
    computer_name =  models.CharField(
        max_length=64, verbose_name='计算机名称', null=False, blank=True)

class hrjoindate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=64, verbose_name='姓名', null=False, blank=True)
    joindate =  models.CharField(
        max_length=64, verbose_name='日期', null=False, blank=True)

class pagepermission(models.Model):
    class Meta:
        permissions = (("uatdata", "Can view uat data"), ("yanfa1", "Can view yanfa1 data"),
                       ("yanfa2", "Can view yanfa2 data"),("yanfa3", "Can view yanfa3 data"),
                       ("cycleexcel", "Can handle cycleexcel"),("labfunction", "Can view lab function"),
                       ("crateexcel", "Can handle crateexcel"),("cyclebybarcode", "Can search by barcode"),
                       ("cyclesummary", "Can search summary"),("hrfunction", "Can view hr function"),
                       ("joindate", "Can maintain joindate"),('signature','Can generate signature'),
                       ('wms','manage wms'),('celltype','manage cell type'),('cellsource','manage cell source'),
                       ('stockin','can stock in cells'),('stockout','can stock out cells'),
                       ('stockquery','can query stock'),('codeamdin','can manage codepriv'),
                       ('coderead','can read codepriv'),('codewrite','can modify codepriv'),
                       ('resource','manage resource'),('resourcetype','manage resource type'),
                       ('sendsalary','can send salary'),('uatwms','manage uatwms'),('uatcelltype','manage uat cell type'),
                       ('uatstockin','can stock in uat cells'),('uatstockout','can stock out uat cells'),
                       ('uatstockquery','can query uat stock'),('getuatstockoutreturn','can query returned uat cells'),
        )

class appfunction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=64, verbose_name='功能名称', null=False, blank=True)
    priv = models.CharField(
        max_length=64, verbose_name='功能权限', null=True, blank=True)
    link = models.CharField(
        max_length=256, verbose_name='功能链接', null=True, blank=True)
    desc = models.CharField(
        max_length=256, verbose_name='功能描述', null=True, blank=True)
    parentid = models.IntegerField(
        verbose_name='父功能节点', null=False, default=1)
    
class cellapply(models.Model):
    id = models.AutoField(primary_key=True)
    applyid = models.CharField(
        max_length=64, verbose_name='流程号', null=False, blank=True)
    applier =  models.CharField(
        max_length=64, verbose_name='申请人', null=True, blank=True)
    apply_dep =  models.CharField(
        max_length=256, verbose_name='申请部门', null=True, blank=True)
    reason = models.CharField(
        max_length=256, verbose_name='申请事由', null=False, blank=True)
    spec = models.CharField(
        max_length=64, verbose_name='电芯规格', null=True, blank=True)
    pn_material = models.CharField(
        max_length=256, verbose_name='正极和负极', null=True, blank=True)
    electro_material = models.CharField(
        max_length=256, verbose_name='电解液/固态电解质膜的材料', null=True, blank=True)    
    electro_source = models.CharField(
        max_length=256, verbose_name='电解液/固态电解质膜的来源', null=True, blank=True)
    formula_code = models.CharField(
        max_length=256, verbose_name='配方编码', null=True, blank=True)
    is34ah = models.BooleanField(
        max_length=64, verbose_name='是否3.4Ah或以下', null=True, blank=True)
    quantity = models.IntegerField(
        verbose_name='电芯需求数量', null=False, default=1)

class celltype(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=64, verbose_name='电芯类型名称', null=True, blank=True)
    capacity = models.FloatField(
        verbose_name='容量', null=True, blank=True)
    positive = models.CharField(
        max_length=64, verbose_name='正极材料', null=True, blank=True)
    negative = models.CharField(
        max_length=64, verbose_name='负极材料', null=True, blank=True)
    positive_layer = models.CharField(
        max_length=32,verbose_name='正极层数', null=True)
    negative_layer =models.CharField(
        max_length=32,verbose_name='负极层数', null=True)
    electrolyte = models.CharField(
        max_length=64, verbose_name='电解质材料', null=True, blank=True)
    formula_code = models.CharField(
        max_length=64, verbose_name='配方编码', null=True, blank=True)


class cellsource(models.Model):
    id = models.AutoField(primary_key=True)
    source_name = models.CharField(
        max_length=64, verbose_name='电芯来源', null=True, blank=True)

class stockin(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    source_id = models.IntegerField(
       verbose_name='电芯来源', null=True, blank=True)
    quantity = models.IntegerField(
       verbose_name='入库数量', null=True, blank=True)
    price = models.FloatField(
        verbose_name='入库单价', null=True, blank=True, default=0)
    indate = models.DateField(verbose_name='入库日期', default=date.today)
    staff = models.CharField(
        max_length=32,verbose_name='交付人',null=True,blank=True)
    memo = models.CharField(
        max_length=64, verbose_name='备注', null=True, blank=True)
    status = models.IntegerField(
       verbose_name='是否生效', null=True, blank=True)
    operator = models.CharField(
        max_length=32,verbose_name='操作人',null=True,blank=True)
    operate_date = models.DateField(verbose_name='操作日期', default=date.today)

class stockout(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    recipient_id =  models.IntegerField(
       verbose_name='领用部门', null=True, blank=True)
    quantity = models.IntegerField(
       verbose_name='出库数量', null=True, blank=True)
    price = models.FloatField(
        verbose_name='出库单价', null=True, blank=True, default=0)
    outdate = models.DateField(verbose_name='出库日期', default=date.today)
    staff = models.CharField(
        max_length=32,verbose_name='领用人',null=True,blank=True)
    memo = models.CharField(
        max_length=64, verbose_name='备注', null=True, blank=True)
    status = models.IntegerField(
       verbose_name='是否生效', null=True, blank=True)
    operator = models.CharField(
        max_length=32,verbose_name='操作人',null=True,blank=True)
    operate_date = models.DateField(verbose_name='操作日期', default=date.today)

class stock(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    quantity = models.IntegerField(
       verbose_name='库存数量', null=True, blank=True)
    last_operate_date = models.DateField(verbose_name='最后操作日期', default=date.today)

class resourcetype(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=64, verbose_name='资源类型名称', null=True, blank=True)
    

class resource(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='资源类型', null=True, blank=True)
    owner_id = models.IntegerField(
       verbose_name='所有者id', null=True, blank=True)
    code = models.CharField(
        max_length=32,verbose_name='编码',null=True,blank=True)
    desc =  models.CharField(
        max_length=512,verbose_name='资源描述',null=True,blank=True)

class resource_user (models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(
       verbose_name='用户id', null=True, blank=True)
    resource_id = models.IntegerField(
       verbose_name='资源id', null=True, blank=True)
    PRIV_CHOICES = (
        (0,'无权限'),
        (1,'读权限'),
        (2,'写权限')
    )
    priv = models.IntegerField(
       choices=PRIV_CHOICES,verbose_name='权限类型', null=True, blank=True)
   
    

class uatcelltype(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=64, verbose_name='电芯类型名称', null=True, blank=True)
    capacity = models.FloatField(
        verbose_name='容量', null=True, blank=True)
    positive = models.CharField(
        max_length=64, verbose_name='正极材料', null=True, blank=True)
    negative = models.CharField(
        max_length=64, verbose_name='负极材料', null=True, blank=True)
    positive_layer = models.CharField(
        max_length=32,verbose_name='正极层数', null=True)
    negative_layer =models.CharField(
        max_length=32,verbose_name='负极层数', null=True)
    electrolyte = models.CharField(
        max_length=64, verbose_name='电解质材料', null=True, blank=True)
    formula_code = models.CharField(
        max_length=64, verbose_name='配方编码', null=True, blank=True)


class uatstockin(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    source = models.CharField(
       max_length=64,verbose_name='电芯来源', null=True, blank=True)
    batch_no = models.CharField(
        max_length=64,verbose_name='电芯批号',null=True,blank=True)
    project_name = models.CharField(
        max_length=64,verbose_name='所属项目',null=True,blank=True)
    quantity = models.IntegerField(
       verbose_name='入库数量', null=True, blank=True)
    indate = models.DateField(verbose_name='入库日期', default=date.today)
    staff = models.CharField(
        max_length=32,verbose_name='交付人',null=True,blank=True)
    memo = models.CharField(
        max_length=64, verbose_name='备注', null=True, blank=True)
    status = models.IntegerField(
       verbose_name='是否生效', null=True, blank=True)
    operator = models.CharField(
        max_length=32,verbose_name='操作人',null=True,blank=True)
    operate_date = models.DateField(verbose_name='操作日期', default=date.today)

class uatstockout(models.Model):
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    batch_no = models.CharField(
        max_length=64,verbose_name='电芯批号',null=True,blank=True)
    project_name = models.CharField(
        max_length=64,verbose_name='所属项目',null=True,blank=True)
    quantity = models.IntegerField(
       verbose_name='出库数量', null=True, blank=True)
    outdate = models.DateField(verbose_name='出库日期', default=date.today)
    staff = models.CharField(
        max_length=32,verbose_name='领用人',null=True,blank=True)
    expect_return_date = models.DateField(verbose_name='预计归还日期', default=date.today)
    purpose = models.CharField(
        max_length=64,verbose_name='用途',null=True,blank=True)
    actual_return_date = models.DateField(verbose_name='实际归还日期', default=date.today)
    memo = models.CharField(
        max_length=1024, verbose_name='备注', null=True, blank=True)
    STATUS_CHOICES = (
        (0,'撤销出库'),
        (1,'已出库'),
        (2,'已还回')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,verbose_name='是否生效', null=True, blank=True)
    operator = models.CharField(
        max_length=32,verbose_name='操作人',null=True,blank=True)
    operate_date = models.DateField(verbose_name='操作日期', default=date.today)

class uatstock(models.Model): 
    id = models.AutoField(primary_key=True)
    type_id = models.IntegerField(
       verbose_name='电芯类型', null=True, blank=True)
    quantity = models.IntegerField(
       verbose_name='库存数量', null=True, blank=True)
    last_operate_date = models.DateField(verbose_name='最后操作日期', default=date.today)

