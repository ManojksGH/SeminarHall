from django.db import models
from django.shortcuts import redirect

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)  # Add phone field

    def __str__(self):
        return self.name


class Hall(models.Model):
    hall_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    location = models.CharField(max_length=100)
    facilities = models.TextField()
    
    # Front and Rear images
    front_image_path = models.ImageField(upload_to='hall_images/front/', blank=True, null=True)
    rear_image_path = models.ImageField(upload_to='hall_images/rear/', blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Default status is pending

    def __str__(self):
        return f"Booking {self.booking_id} - {self.status}"

class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)  # Allow null temporarily
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, default='Pending')  # Add default value
    
    def __str__(self):
        return f"Log {self.log_id}: Booking {self.booking_id} - {self.status}"
