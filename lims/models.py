from django.db import models

# Create your models here.

class teams(models.Model):
    id = models.AutoField(primary_key=True)
    teamname = models.CharField(
        max_length=64, verbose_name='组名称', null=False, blank=True)

class teamcomputer(models.Model):
    id = models.AutoField(primary_key=True)
    teamid = models.IntegerField(
        verbose_name='team id', null=False)
    computer_name =  models.CharField(
        max_length=64, verbose_name='计算机名称', null=False, blank=True)