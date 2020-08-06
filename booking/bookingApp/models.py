from django.db import models

# Create your models here.


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    class Meta:
        db_table = 'admin'



class RoomType(models.Model):
    
    room_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=64)
    price = models.IntegerField()

    class Meta:
        db_table = 'room_type'
    def __str__(self):
        return self.type_name

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_type_id = models.ForeignKey('RoomType', on_delete=models.DO_NOTHING)
    room_status = models.CharField(max_length=128)
    room_num = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'room'

class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128) 
    client_email = models.CharField(max_length=128)
    client_phone = models.CharField(max_length=128)
    room_id = models.ForeignKey('Room', on_delete=models.CASCADE)
    date_in = models.DateField()
    date_out = models.DateField()

    class Meta:
        db_table = 'reservation'



# class PaymentDetails(models.Model):
#     payment_details_id = models.AutoField(primary_key=True)
#     reservation_id = models.ForeignKey('Reservation', on_delete=models.DO_NOTHING)
#     value = models.IntegerField()
#     days = models.IntegerField()
#     total = models.IntegerField()

#     class Meta:
#         db_table = 'payment_details'








