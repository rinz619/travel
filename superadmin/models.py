from django.db import models
from django.contrib.postgres.fields import ArrayField
# from rest_framework import serializers
# from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from autoslug import AutoSlugField

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

# Create your models here.

GENDER_CHOICES = (
        ('1', 'Male'),
        ('2', 'Female'),
    )

USER_TYPE_CHOICES = (
      (1, 'superadmin'),
      (2, 'Sub Admin'),
      (3, 'Teacher'),
      (4, 'Student'),
  )

STATUS_CHOICES = (
      ('unpaid', 'unpaid'),
      ('paid', 'paid'),
      ('cancelled', 'cancelled'),
  )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.admin = 2
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.admin = 3
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.admin = 1
        user.save(using=self._db)
        return user




class User(AbstractBaseUser):
    unique_id = models.TextField(null=True,unique=True)
    name = models.TextField(null=True)
    contactperson = models.TextField(null=True)
    phone = models.TextField(null=True)
    password_text = models.TextField(null=True)
    trn = models.TextField(null=True)
    address = models.TextField(null=True)
    image = models.ImageField(upload_to='user', blank=True, null=True)
    attachement = models.FileField(upload_to='user', blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True,unique=True)
    password =  models.CharField(max_length=255, blank=True,null=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.name


    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.admin

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin





    objects = UserManager()





class Bookings(models.Model):
    agent = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    unique_id = models.TextField(null=True, blank=True)
    servicetype = models.TextField(null=True, blank=True)
    fromairport = models.TextField(null=True, blank=True)
    toairport = models.TextField(null=True, blank=True)
    departuredate = models.DateField(null=True, blank=True)
    airline = models.TextField(null=True, blank=True)
    pnr = models.TextField(null=True, blank=True)
    ticketnumber = models.TextField(null=True, blank=True)
    passengername = models.TextField(null=True, blank=True)
    servicedescription = models.TextField(null=True, blank=True)
    netamount = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    grossamount = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    markup = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Airports(models.Model):
    city_airport = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=10, blank=True, null=True)
    alpha_2 = models.CharField(max_length=5)
    alpha_3 = models.CharField(max_length=5)
    un_code = models.IntegerField()



class Airlines(models.Model):
    iata = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=255)
    country_or_region = models.CharField(max_length=100)
    



class AccountLedgers(models.Model):
    agent = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    unique_id = models.TextField(null=True, blank=True)
    transactiontype = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    debit = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    credit = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    balance = models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Banner(models.Model):
    image = models.ImageField(upload_to='banner', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Partners(models.Model):
    image = models.ImageField(upload_to='partners', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Countries(models.Model):
    image = models.ImageField(upload_to='country', null=True, blank=True)
    flag = models.ImageField(upload_to='country', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    subtitle = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    why = models.TextField(null=True, blank=True)
    eligblity = ArrayField(models.TextField(), blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = AutoSlugField(populate_from='title', null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.title != self.slug:
            self.slug = AutoSlugField(populate_from='title', unique=True).slugify(self.title)

        super(Countries, self).save(*args, **kwargs)

class Faqs(models.Model):
    country = models.ForeignKey(Countries,on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    subtitle = models.TextField(null=True, blank=True)   
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Universities(models.Model):
    country = models.ForeignKey(Countries,on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='university', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    duration = models.IntegerField(default=0,null=True, blank=True)
    ranking = models.IntegerField(default=0,null=True, blank=True)
    indian = models.IntegerField(default=0,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = AutoSlugField(populate_from='title', null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.title != self.slug:
            self.slug = AutoSlugField(populate_from='title', unique=True).slugify(self.title)

        super(Universities, self).save(*args, **kwargs)


class Services(models.Model):
    image = models.ImageField(upload_to='service', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Testimonials(models.Model):
    image = models.ImageField(upload_to='testimonials', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Events(models.Model):
    image = models.ImageField(upload_to='events', null=True, blank=True)
    sequence = models.IntegerField(default=1)
    title = models.TextField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Enquiries(models.Model):
    university = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
