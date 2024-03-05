from django.db import models

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
        )