from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Car, Booking
from django.core.mail import send_mail


# HOME PAGE
def home(request):
    cars = Car.objects.filter(is_available=True)[:6]
    return render(request, 'cars/index.html', {'cars': cars})


# BOOK CAR
@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if not car.is_available:
        messages.error(request, "Car is not available!")
        return redirect('home')

    if request.method == "POST":
        phone = request.POST.get('phone')
        pickup_location = request.POST.get('pickup_location')
        drop_location = request.POST.get('drop_location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # ✅ NEW FIELDS
        distance_km = request.POST.get('distance_km')
        hours = request.POST.get('hours')

        if not all([phone, pickup_location, drop_location, start_date, end_date]):
            messages.error(request, "All fields are required!")
            return redirect('book_car', car_id=car.id)

        try:
            distance_km = float(distance_km) if distance_km else 0
            hours = float(hours) if hours else 0
        except ValueError:
            messages.error(request, "Invalid KM or Hours value")
            return redirect('book_car', car_id=car.id)

        if start_date > end_date:
            messages.error(request, "End date must be after start date!")
            return redirect('book_car', car_id=car.id)

        # ✅ CALCULATE TOTAL PRICE
        total_price = (distance_km * car.price_per_km) + (hours * car.price_per_hour)

        # ✅ CREATE BOOKING (FIXED)
        booking = Booking.objects.create(
            user=request.user,
            car=car,
            phone=phone,
            pickup_location=pickup_location,
            drop_location=drop_location,
            start_date=start_date,
            end_date=end_date,
            distance_km=distance_km,
            hours=hours,
            total_price=total_price
        )
        

        car.is_available = False
        car.save()


        messages.success(request, "Booking Confirmed Successfully!")
        return redirect('home')

    return render(request, 'booking.html', {'car': car})

# CAR LIST
def car_list(request):
    cars = Car.objects.all()

    query = request.GET.get('q')
    if query:
        cars = cars.filter(name__icontains=query)

    max_price = request.GET.get('price')
    if max_price:
        cars = cars.filter(price__lte=max_price)

    fuel = request.GET.get('fuel')
    if fuel:
        cars = cars.filter(fuel_type__iexact=fuel)

    sort = request.GET.get('sort')
    if sort == 'low':
        cars = cars.order_by('price')
    elif sort == 'high':
        cars = cars.order_by('-price')
    elif sort == 'latest':
        cars = cars.order_by('-id')

    return render(request, 'car_list.html', {'cars': cars})


# CAR DETAIL
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'cars/car_detail.html', {'car': car})


# REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "register.html")


# LOGIN
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'cars/my_bookings.html', {'bookings': bookings})

@login_required
@require_POST
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Make car available again
    booking.car.is_available = True
    booking.car.save()

    booking.delete()

    messages.success(request, "Booking cancelled successfully!")
    return redirect('my_bookings')


@login_required
def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    elements.append(Paragraph("Car Rental Invoice", styles['Title']))
    elements.append(Spacer(1, 20))

    # USER INFO
    elements.append(Paragraph(f"Customer: {booking.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Car: {booking.car.name}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {booking.phone}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # BOOKING DETAILS
    elements.append(Paragraph(f"Pickup: {booking.pickup_location}", styles['Normal']))
    elements.append(Paragraph(f"Drop: {booking.drop_location}", styles['Normal']))
    elements.append(Paragraph(f"Start Date: {booking.start_date}", styles['Normal']))
    elements.append(Paragraph(f"End Date: {booking.end_date}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # COST DETAILS
    elements.append(Paragraph(f"Distance: {booking.distance_km} KM", styles['Normal']))
    elements.append(Paragraph(f"Hours: {booking.hours}", styles['Normal']))
    elements.append(Paragraph(f"Total Price: ₹{booking.total_price}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # FOOTER
    elements.append(Paragraph("Thank you for choosing our service!", styles['Italic']))

    doc.build(elements)

    return response

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review")

        booking.rating = rating
        booking.review = review
        booking.save()

        messages.success(request, "Review submitted successfully!")
        return redirect('my_bookings')

    return render(request, "cars/add_review.html", {"booking": booking})