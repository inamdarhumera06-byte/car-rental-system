from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Car(models.Model):

    FUEL_CHOICES = (
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    )

    TRANSMISSION_CHOICES = (
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    )

    DISTANCE_MAP = {
    ("Pune", "Mumbai"): 150,
    ("Mumbai", "Bangalore"): 980,
    ("Pune", "Bangalore"): 840,
    ("vasmat road parbhani", "Dargha road parbhani"):25,
    ("qaudrabad plot parbhani","vakil colony" ):8,
    }

   
  

    name = models.CharField(max_length=200)
    # NEW FIELD ✅
    model_name = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    year = models.IntegerField()

    # Base price (optional display)
    price = models.IntegerField()

    # Pricing logic
    price_per_km = models.FloatField(default=12.0)
    price_per_hour = models.FloatField(default=300.0)

    features = models.TextField()

    passengers = models.IntegerField()
    fuel = models.CharField(max_length=50, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=50, choices=TRANSMISSION_CHOICES)

    image = models.ImageField(upload_to='cars/')

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)

    pickup_location = models.CharField(max_length=200)
    drop_location = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    # ✅ NEW FIELDS (IMPORTANT)
    distance_km = models.FloatField(null=True, blank=True)
    hours = models.FloatField(null=True, blank=True)

    total_price = models.FloatField(blank=True, null=True)
    rating = models.IntegerField(default=0)   # ⭐ IMPORTANT

     # ✅ STATUS FIELD (ADD HERE)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")

    def save(self, *args, **kwargs):
        # ✅ AUTO CALCULATE TOTAL PRICE
        self.total_price = (
            (self.distance_km * self.car.price_per_km) +
            (self.hours * self.car.price_per_hour)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.car.name}"

            # ⭐ NEW RATING SYSTEM
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.car.name}"
    