from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from .views import register_view, login_view, logout_view

urlpatterns = [

    path('', views.home, name='home'),
    path('book/<int:car_id>/', views.book_car, name='book_car'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/my-bookings/', views.my_bookings, name='my_bookings'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('invoice/<int:booking_id>/', views.download_invoice, name='download_invoice'),
    path('review/<int:booking_id>/', views.add_review, name='add_review'),
]