from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from .models import Admin, User, Hall, Booking, Log


def hall_list(request):
    halls = Hall.objects.all()
    return render(request, 'seminar/hall_list.html', {'halls': halls, 'MEDIA_URL': settings.MEDIA_URL})

def booking_list(request):
    selected_date = request.GET.get('booking_date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            bookings = Booking.objects.filter(date=selected_date)
        except ValueError:
            bookings = []
    else:
        bookings = Booking.objects.all()
    return render(request, 'seminar/booking_list.html', {'bookings': bookings, 'selected_date': selected_date})

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Booking, User, Hall, Admin, Log  # Assuming LogBooking is the log table

def booking_create(request):
    if not request.session.get('user_id'):
        return redirect('seminar:login')

    if request.method == 'POST':
        hall_id = request.POST.get('hall_id')
        admin_id = request.POST.get('admin_id')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        user_name = request.session.get('user_name')

        try:
            user = User.objects.get(name=user_name)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")
            return redirect('seminar:booking_create')

        current_date = datetime.now().date()
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please enter a valid date.")
            return redirect('seminar:booking_create')

        if selected_date < current_date:
            messages.error(request, "You cannot book a hall for a past date. Please select a future date.")
            return redirect('seminar:booking_create')

        # Check if start_time is less than end_time
        if start_time >= end_time:
            messages.error(request, "Start time must be earlier than the end time.")
            return redirect('seminar:booking_create')

        # *Check for overlapping time slots*
        overlapping_booking = Booking.objects.filter(
            hall_id=hall_id,
            date=date
        ).filter(
            # Check if the requested start time or end time overlaps with existing bookings
            start_time__lt=end_time,  # The start time of the existing booking is before the new end time
            end_time__gt=start_time   # The end time of the existing booking is after the new start time
        ).exists()

        if overlapping_booking:
            messages.error(request, "This seminar hall is already booked for the selected date and time slot.")
            return redirect('seminar:booking_create')

        # Create a new booking
        booking = Booking(
            hall_id=hall_id,
            user=user,
            admin_id=admin_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )
        booking.save()
        messages.success(request, "Booking created successfully!")
        return redirect('seminar:userdashboard')

    halls = Hall.objects.all()
    admins = Admin.objects.all()
    return render(request, 'seminar/booking_create.html', {
        'halls': halls,
        'admins': admins,
        'user_name': request.session.get('user_name')
    })

from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import User, Admin  # Import your models

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(Q(name=username) | Q(email=username))
            if check_password(password, user.password):  # Verify hashed password
                request.session['user_id'] = user.user_id
                request.session['user_name'] = user.name
                return redirect('seminar:userdashboard')
        except User.DoesNotExist:
            pass

        try:
            admin = Admin.objects.get(Q(name=username) | Q(email=username))
            
            request.session['admin_id'] = admin.admin_id
            request.session['admin_name'] = admin.name
            return redirect('seminar:admindashboard')
        except Admin.DoesNotExist:
            pass

        messages.error(request, "Invalid username or password.")
        return redirect('seminar:login')

    return render(request, 'seminar/login.html')


def userdashboard(request):
    if not request.session.get('user_id'):
        return redirect('seminar:login')
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    halls = Hall.objects.all()
    bookings = Booking.objects.filter(user__user_id=user_id)
    return render(request, 'seminar/userdashboard.html', {
        'user_name': user_name,
        'halls': halls,
        'bookings': bookings,
    })

def admindashboard(request):
    if not request.session.get('admin_id'):
        return redirect('seminar:login')
    admin_id = request.session.get('admin_id')
    admin_name = request.session.get('admin_name')
    halls = Hall.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'seminar/admindashboard.html', {
        'admin_name': admin_name,
        'halls': halls,
        'bookings': bookings,
    })

def user_logout(request):
    request.session.flush()
    return redirect('home')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User  # Assuming the User model is imported from your models

from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User  # Import your User model

def register_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')  # Get the concatenated phone number
        
        if name and email and password and phone:
            hashed_password = make_password(password)  # Hash the password
            user = User(name=name, email=email, password=hashed_password, phone=phone)
            user.save()
            
            messages.success(request, "User registered successfully.")
            return redirect('seminar:admindashboard')
        else:
            messages.error(request, "All fields are required.")
    
    return render(request, 'seminar/register_user.html')


def update_hall_list(request):
    if not request.session.get('admin_id'):
        return redirect('login')
    
    admin_id = request.session.get('admin_id')
    
    if request.method == 'POST':
        hall_name = request.POST.get('hall_name')
        capacity = request.POST.get('capacity')
        location = request.POST.get('location')
        facilities = request.POST.get('facilities')
        
        # Get the front and rear images
        front_image = request.FILES.get('front_image')
        rear_image = request.FILES.get('rear_image')
        
        front_image_path = None
        rear_image_path = None
        
        # Save the images if provided
        if front_image:
            fs = FileSystemStorage()
            front_image_path = fs.save(f"hall_images/front/{front_image.name}", front_image)
        
        if rear_image:
            fs = FileSystemStorage()
            rear_image_path = fs.save(f"hall_images/rear/{rear_image.name}", rear_image)
        
        # Update or create a hall instance
        hall = Hall(
            admin_id=admin_id,
            name=hall_name,
            capacity=capacity,
            location=location,
            facilities=facilities,
            front_image_path=front_image_path,
            rear_image_path=rear_image_path
        )
        hall.save()
        
        return redirect('seminar:update_hall_list')
    
    halls = Hall.objects.all()
    return render(request, 'seminar/update_hall_list.html', {'halls': halls})

from twilio.rest import Client
from django.conf import settings

def update_booking_status(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            old_status = booking.status
            new_status = 'confirmed' if action == 'accept' else 'rejected'
            if action == 'accept':
                booking.status = 'accepted'
                status_message = 'Your booking has been accepted.'
            elif action == 'reject':
                booking.status = 'rejected'
                status_message = 'Your booking has been rejected.'

            if old_status != new_status:
                booking.status = new_status
                booking.save()
                log_entry = Log(
                    user_id=booking.user_id,
                    booking_id=booking.booking_id,
                    hall_id=booking.hall_id,
                    status=new_status
                )
                log_entry.save()

                # Send Email Notification
                email_subject = 'Seminar Hall Booking Update'
                email_html_content = render_to_string('seminar/email.html', {
                    'username': booking.user.name,
                    'status_message': status_message,
                    'hall_name': booking.hall.name,
                    'booking_date': booking.date,
                    'start_time': booking.start_time,
                    'end_time': booking.end_time,
                })
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=status_message,
                    from_email=None,
                    to=[booking.user.email],
                )
                email.attach_alternative(email_html_content, "text/html")
                email.send()

                # **Send SMS Notification using Twilio**
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    message = client.messages.create(
                        body=f"Hello {booking.user.name}, {status_message} for {booking.hall.name} on {booking.date}.",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=booking.user.phone  # Ensure this is in E.164 format (+1234567890)
                    )
                    messages.success(request, f'Booking status updated to {new_status.capitalize()} successfully. SMS sent.')
                except Exception as e:
                    messages.error(request, f'Booking updated but SMS sending failed: {e}')
            else:
                messages.info(request, 'No changes were made to the booking status.')

        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found.')

    filter_date = request.GET.get('date', None)
    filters = {}
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            filters['date'] = filter_date
        except ValueError:
            messages.error(request, 'Invalid date format.')

    bookings = Booking.objects.filter(**filters) if filters else Booking.objects.all()
    users = User.objects.all()
    halls = Hall.objects.all()
    return render(request, 'seminar/update_booking_status.html', {
        'bookings': bookings,
        'users': users,
        'halls': halls
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User  # Import your custom User model

from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User  # Import your User model

def change_password(request):
    if 'user_id' not in request.session:
        return redirect('seminar:user_login')  # Redirect if not logged in

    try:
        user = User.objects.get(user_id=request.session['user_id'])
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('seminar:user_login')

    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Verify the old password using check_password
        if not check_password(old_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect('seminar:change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('seminar:change_password')

        # Hash the new password before saving
        user.password = make_password(new_password)
        user.save()

        messages.success(request, "Password updated successfully!")
        return redirect('seminar:userdashboard')  # Redirect after successful update

    return render(request, 'seminar/change_password.html')


def check_status(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'seminar/check_status.html', {'error': 'User not logged in'})
    filter_date = request.GET.get('date', None)
    logs = Log.objects.filter(user_id=user_id)
    if filter_date:
        bookings = Booking.objects.filter(
            booking_id__in=logs.values_list('booking_id', flat=True),
            date=filter_date
        )
    else:
        bookings = Booking.objects.filter(
            booking_id__in=logs.values_list('booking_id', flat=True)
        )
    booking_statuses = []
    for booking in bookings:
        log_entry = logs.filter(booking_id=booking.booking_id).last()
        status = log_entry.status if log_entry else "Unknown"
        booking_statuses.append({
            'booking_id': booking.booking_id,
            'hall_name': booking.hall.name,
            'date': booking.date,
            'start_time': booking.start_time,
            'end_time': booking.end_time,
            'status': status
        })
    return render(request, 'seminar/check_status.html', {'booking_statuses': booking_statuses, 'filter_date': filter_date})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Hall
from django.core.files.storage import FileSystemStorage

def edit_hall(request, hall_id):
    hall = get_object_or_404(Hall, hall_id=hall_id)
    
    if request.method == 'POST':
        hall_name = request.POST.get('hall_name')
        capacity = request.POST.get('capacity')
        location = request.POST.get('location')
        facilities = request.POST.get('facilities')

        # Handle image uploads
        fs = FileSystemStorage()
        front_image = request.FILES.get('front_image')
        rear_image = request.FILES.get('rear_image')

        if front_image:
            front_image_path = fs.save(f"hall_images/front/{front_image.name}", front_image)
            hall.front_image_path = front_image_path

        if rear_image:
            rear_image_path = fs.save(f"hall_images/rear/{rear_image.name}", rear_image)
            hall.rear_image_path = rear_image_path

        hall.name = hall_name
        hall.capacity = capacity
        hall.location = location
        hall.facilities = facilities

        hall.save()

        return redirect('seminar:update_hall_list')

    return render(request, 'seminar/edit_hall.html', {'hall': hall})
