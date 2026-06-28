from django.contrib import admin
from .models import Car, Booking



@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'city', 'price', 'fuel', 'transmission', 'is_available')
    search_fields = ('name','model' 'city')
    list_filter = ('fuel', 'transmission', 'is_available')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'phone', 'pickup_location', 'drop_location', 'start_date', 'end_date')
    search_fields = ('user__username', 'car__name', 'phone')
    list_filter = ('start_date', 'end_date')

    
