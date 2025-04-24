from django.conf import settings  # Add this import
from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError
from geopy.distance import geodesic  
from geopy.geocoders import Nominatim  

from django import forms

class UserRegister(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    age = models.IntegerField()
    email = models.EmailField()
    place = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    status = models.CharField(
        max_length=20,
        choices=[('applied', 'Applied'), ('approved', 'Approved'), ('reject', 'Reject')],
        default='applied'  # Default status
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feedback = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Feedback from {self.user.username}"

class Station(models.Model):
    stationname = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    no_of_bikes = models.IntegerField(default=0)
    is_removed = models.BooleanField(default=False)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    address = models.TextField(default='Unknown Location')

    def clean(self):
        """Validation that prevents reducing capacity below current bikes"""
        if self.pk:  # Only check for existing stations (better than hasattr)
            current_bikes = Bike.objects.filter(station=self, is_removed=False).count()
            if self.no_of_bikes < current_bikes:
                raise ValidationError(
                    f"Cannot set capacity to {self.no_of_bikes}. "
                    f"Station already has {current_bikes} bikes."
                )

    def save(self, *args, **kwargs):
        """Simplified save method with robust number handling"""
        # Ensure no_of_bikes is always an integer
        try:
            self.no_of_bikes = int(float(self.no_of_bikes)) if self.no_of_bikes else 0
        except (ValueError, TypeError):
            raise ValidationError("Bike capacity must be a valid number")
        
        # Only geocode if we have an address but no coordinates
        if self.address and self.address != 'Unknown Location' and (not self.latitude or not self.longitude):
            try:
                geolocator = Nominatim(user_agent="bike_rental_app")
                location = geolocator.geocode(self.address)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
            except Exception:
                pass  # Don't fail if geocoding fails
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.stationname

class Bike(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance')
    ]

    id = models.BigAutoField(primary_key=True)
    bikenum = models.CharField(max_length=20, unique=True)
    bikemodel = models.CharField(max_length=50)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    status = models.CharField(
            max_length=100,
            choices=STATUS_CHOICES,
            default='available'
            )# Default status is 'available'

    is_available = models.BooleanField(default=True)  # New field for easy filtering
    bimg = models.ImageField(upload_to='bikes/')
    is_removed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Automatically update is_available based on status"""
        self.is_available = self.status == 'available'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bikemodel} ({self.bikenum}) - {self.get_status_display()}"


from django.db import models
from django.conf import settings
from datetime import timedelta

class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bikenum = models.ForeignKey('Bike', on_delete=models.CASCADE)
    strtstation = models.ForeignKey('Station', on_delete=models.CASCADE, related_name='start_station')
    endstation = models.ForeignKey('Station', on_delete=models.CASCADE, related_name='end_station')
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    
    rtrn = models.BooleanField(default=False)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    penalty_paid = models.BooleanField(default=False)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    distance = models.FloatField(null=True, blank=True)
    is_peak_hour = models.BooleanField(default=False)
    estimated_demand = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-set peak hour
        hour = self.start_datetime.hour
        self.is_peak_hour = (7 <= hour <= 9) or (16 <= hour <= 18)
        
        # Calculate distance if stations exist
        if self.strtstation and self.endstation:
            try:
                coords1 = (self.strtstation.latitude, self.strtstation.longitude)
                coords2 = (self.endstation.latitude, self.endstation.longitude)
                self.distance = geodesic(coords1, coords2).km
            except (AttributeError, ValueError) as e:
                # Handle cases where coordinates are missing/invalid
                self.distance = None
        
        # Update bike status
        if self.status == 'active' and self.bikenum.status == 'available':
            self.bikenum.status = 'booked'
        elif self.status in ['completed', 'canceled']:
            self.bikenum.status = 'available'
        
        # Save bike status changes
        if self.bikenum.pk:
            self.bikenum.save()
        
        super().save(*args, **kwargs)

    def calculate_duration(self):
        """Calculate rental duration in hours"""
        duration = self.end_datetime - self.start_datetime
        return duration.total_seconds() / 3600

    def set_advance_payment(self):
        """Set advance payment based on booking duration"""
        duration_hours = self.calculate_duration()
        self.advance_paid = 500 if duration_hours < 24 else 1000
        self.save()

    def calculate_final_amount(self, hourly_rate=50):
        """Calculate final rent based on exact duration"""
        duration_hours = self.calculate_duration()
        self.amount = duration_hours * hourly_rate
        self.final_amount_due = max(0, self.amount - self.advance_paid)
        self.total_amount = self.amount
        self.save()

    def __str__(self):
        return f"Booking #{self.id} - {self.bikenum} by {self.user.username}"


class Predict(models.Model):
    sid = models.ForeignKey(Station, on_delete=models.CASCADE)
    count = models.IntegerField()

    def __str__(self):
        return f"{self.sid.stationname} - {self.count} bookings"


class Payment_last(models.Model):  # Renaming Payment_last to Payment for clarity
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('advance', 'Advance Payment'),
        ('final', 'Final Payment'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)  
    card_no = models.CharField(max_length=16)
    pin_no = models.CharField(max_length=4)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)  # New field
    timestamp = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status}) for {self.payment_type}"


class WeatherData(models.Model):
    date = models.DateField()
    temperature = models.FloatField()  # in Celsius
    precipitation = models.FloatField()  # in mm
    weather_condition = models.CharField(max_length=50)  # e.g., "Rain", "Sunny"
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.weather_condition}"

class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    is_public_holiday = models.BooleanField(default=True)

    def __str__(self):
        return self.name