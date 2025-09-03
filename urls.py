from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'seminar'

urlpatterns = [
    
    path('login/', views.login, name='login'),
    path('userdashboard/', views.userdashboard, name='userdashboard'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('halls/', views.hall_list, name='hall_list'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('register_user/', views.register_user, name='register_user'),  # URL for Register User
    path('update_booking_status/', views.update_booking_status, name='update_booking_status'),  # URL for Update Booking Status
    path('update_hall_list/', views.update_hall_list, name='update_hall_list'),  # URL for Update Hall List
    path('check_status/', views.check_status, name='check_status'),
    path('change_password/', views.change_password, name='change_password'),
    path('edit_hall/<int:hall_id>/', views.edit_hall, name='edit_hall'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
