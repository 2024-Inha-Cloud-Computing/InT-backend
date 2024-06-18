# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class AuthEmailTable(models.Model):
    objects = models.Manager()
    email = models.CharField(primary_key=True, max_length=255)
    arn = models.CharField(max_length=255, null=True)
    #authcode = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'auth_email_table'


class AuthPhoneTable(models.Model):
    objects = models.Manager()
    phone = models.CharField(primary_key=True, max_length=20)
    authNo = models.CharField(max_length=4, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # managed = False
        db_table = 'auth_phone_table'

class Users(models.Model):
    objects = models.Manager()
    user_id = models.AutoField(primary_key=True)
    id = models.CharField(unique=True, max_length=255)
    pw = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    birth = models.DateField()
    phone = models.CharField(unique=True, max_length=20)
    email = models.CharField(unique=True, max_length=255)
    register_day = models.DateField()
    
    am_pm = models.IntegerField(blank=True, null=True)
    first_class = models.IntegerField(blank=True, null=True)
    space_time = models.IntegerField(blank=True, null=True)
    
    first_login = models.IntegerField()
    
    # objects = UserManager()
    
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = []
    class Meta:
        # managed = False
        db_table = 'users'
        
    def check_password(self, raw_password):
        return self.pw == raw_password