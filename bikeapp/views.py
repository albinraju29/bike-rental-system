import csv
from os import name
import re
from statistics import LinearRegression
from time import timezone
from urllib import request
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect ,JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User 
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import numpy as np
from .models import  Holiday, UserRegister,Feedback,Bike,Station,Booking,Predict,Payment_last, WeatherData, Payment_last
from django.db.models import Q
import random
from datetime import datetime 
import pandas as pd
import matplotlib.pyplot as plt
from csv import writer
from django.utils.timezone import now
import datetime
from django.utils.timezone import make_aware
from datetime import datetime  # ✅ Best practice
from datetime import timedelta
import logging
import traceback
from tempfile import NamedTemporaryFile
from sklearn.linear_model import LinearRegression
from django.db.models import Count,Max
from geopy.distance import geodesic

def user_login(request):
    """User login view with user role-based redirection."""
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session["id"] = user.id
            request.session["email"] = user.email
            request.session["name"] = user.username

            # Redirect admin users
            if user.is_superuser:
                return redirect('admin_home')

            # For regular users, check status in UserRegister
            try:
                user_register = UserRegister.objects.get(user=user)
                if user_register.status == 'approved':
                    return redirect('user_home')
                elif user_register.status == 'reject':
                    messages.error(request, "You are rejected from the request to login.")
                else:
                    messages.warning(request, "Your profile is not validated yet.")
            except UserRegister.DoesNotExist:
                messages.error(request, "Your profile does not exist.")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def admin_home(request):
    # Ensure only superusers access this view
    if request.user.is_superuser:
        return render(request, 'admin_home.html')
    return HttpResponse("Unauthorized", status=401)


@login_required
def user_home(request):
    # Ensure only regular users access this view
    if not request.user.is_superuser:
        return render(request, 'user/user_home.html')
    return HttpResponse("Unauthorized", status=401)


from django.core.files.storage import default_storage

def user_register(request):
    msg = ""
    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        age = request.POST.get("age")
        email = request.POST.get("email")
        password = request.POST.get("password")
        place = request.POST.get("place")
        district = request.POST.get("district")
        pincode = request.POST.get("pincode")

        profile_picture = request.FILES.get("profile_picture")  # Get the uploaded file

        # Check if the user is already registered
        if User.objects.filter(email=email).exists():
            msg = "Email already registered"
        else:
            # Create a new user
            user = User.objects.create_user(username=name, email=email, password=password)

            # Save profile picture properly
            if profile_picture:
                filename = default_storage.save(f'profile_pictures/{profile_picture.name}', profile_picture)
            else:
                filename = None  # If no image is uploaded

            # Save additional user information
            user_register = UserRegister.objects.create(
                user=user,
                name=name,
                phone=phone,
                address=address,
                profile_picture=filename,  # Store the path only
                age=age,
                place=place,
                district=district,
                pincode=pincode,
                status="applied"
            )

            msg = "Successfully registered"
            request.session['email'] = email
            return redirect("bikeapp:login")

    return render(request, "user_register.html", {"msg": msg})



def logout(request):
    auth_logout(request)  # Log out the user
    request.session.flush()  # Clear session data
    return redirect('bikeapp:login')  # Redirect to the login page

@login_required
def userupdprofile(request):
    msg = ""

    if not request.user.is_authenticated:
        messages.error(request, "Please log in first.")
        return redirect('bikeapp:login')

    try:
        user_data = UserRegister.objects.get(user=request.user)
    except UserRegister.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('bikeapp:login')

    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        age = request.POST.get("age")
        email = request.POST.get("email")
        password = request.POST.get("password")
        place = request.POST.get("place")
        district = request.POST.get("district")
        pincode = request.POST.get("pincode")

        if 'profile_picture' in request.FILES:
            user_data.profile_picture = request.FILES['profile_picture']

        user_data.name = name
        user_data.phone = phone
        user_data.address = address
        user_data.age = age
        user_data.email = email
        user_data.place = place
        user_data.district = district
        user_data.pincode = pincode

        if password:
            user_data.password = make_password(password)

        user_data.save()

        # Update the built-in User model
        user = request.user
        user.first_name = name
        user.email = email
        if password:
            user.set_password(password)
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('bikeapp:userupdprofile')

    context = {"msg": msg, "data": user_data}
    return render(request, "user/userupdprofile.html", context)

def user_view_reply(request):
    """
    View for users to see replies to their feedback.
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please log in to view replies.", status=403)

    # Fetch feedback entries for the logged-in user
    feedback_entries = Feedback.objects.filter(user=request.user)

    return render(request, 'user/user_view_reply.html', {'feedback_entries': feedback_entries})

def user_feedback(request):
    msg = ""
    
    if 'id' in request.session:
        user_register = UserRegister.objects.filter(id=request.session['id']).first()

        if user_register and request.method == 'POST':
            feedback = request.POST.get("feedback")
            date = datetime.now()


            # Debugging logs
            print("User found:", user_register)
            print("Feedback input:", feedback)

            # Insert feedback
            fb = Feedback.objects.create(user=user_register.user, feedback=feedback, date=date)
            print("User linked to UserRegister:", user_register.user)  # Should print <User: username>
            print("Feedback created and saved:", Feedback.objects.all()) 
            print("Feedback created:", fb)
            msg = "Feedback sent successfully."

    return render(request, "user/user_feedback.html", {"msg": msg})



logger = logging.getLogger(__name__)

def cancelbooking(request):
    """Handles booking cancellation and penalty calculations."""
    if request.GET:
        sstation = request.GET.get("sstation")  # Start station name
        bikenum = request.GET.get("bikenum")  # Bike number

        if not sstation or not bikenum:
            return render(request, "error.html", {"message": "Invalid request parameters."})

        try:
            bike = get_object_or_404(Bike, bikenum=bikenum)
            booking = Booking.objects.filter(strtstation__stationname=sstation, bikenum=bike).first()

            if not booking:
                return render(request, "error.html", {"message": "Booking not found for the provided details."})

            booking_time = booking.start_datetime
            time_elapsed = now() - booking_time

            penalty_percent = 0  # Default (Free cancellation)

            if time_elapsed > timedelta(hours=1):
                penalty_percent = 40  # Apply 40% penalty

            total_amount = booking.total_amount
            advance_amount = booking.advance_paid
            penalty_amount = (total_amount * penalty_percent) / 100
            refund_amount = max(0, advance_amount - penalty_amount)

            if penalty_percent > 0:
                # Show penalty payment page
                return render(request, "payment/penalty.html", {
                    "booking": booking,
                    "total_amount": total_amount,
                    "advance_amount": advance_amount,
                    "penalty_amount": penalty_amount,
                    "refund_amount": refund_amount
                })

            # Free cancellation process
            booking.status = "canceled"
            booking.save()
            bike.status = 1  # Mark bike as available
            bike.save()

            station = get_object_or_404(Station, stationname=sstation)
            station.no_of_bikes += 1
            station.save()

            return redirect('/user_view_booking')

        except Exception as e:
            logger.error(f"Error in cancelbooking: {str(e)}\n{traceback.format_exc()}")
            return render(request, "error.html", {"message": f"An error occurred: {str(e)}"})

    return render(request, "user/user_view_booking.html")

def process_penalty(request, booking_id):
    """Handles penalty payment and updates booking status."""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # 1. Update bike status
        bike = booking.bikenum
        bike.status = 1  # Available
        bike.save()
        
        # 2. Update station bike count
        station = booking.strtstation
        station.no_of_bikes += 1
        station.save()
        
        # 3. Update booking status and save penalty info
        booking.status = "canceled"
        booking.penalty_paid = True
        booking.penalty_amount = (booking.amount * 0.4)  # 40% penalty
        booking.refund_amount = max(0, booking.advance_paid - booking.penalty_amount)
        booking.save()
        
        # 4. Create payment record (optional)
        Payment_last.objects.create(
            user=request.user,
            booking=booking,
            amount=booking.penalty_amount,
            payment_type='penalty',
            status='completed'
        )
        
        messages.success(request, "Booking canceled with penalty paid successfully")
        return redirect('bikeapp:user_view_booking')

    except Exception as e:
        logger.error(f"Error in process_penalty: {str(e)}\n{traceback.format_exc()}")
        messages.error(request, f"Error processing penalty: {str(e)}")
        return redirect('bikeapp:user_view_booking')


def send_mail(request):
    email = request.session.get('email')  # Retrieve email from session
    if email:
        subject = "Booking Confirmation"
        message = "COMPLETED THE PAYMENT. BOOKING DONE SUCCESSFULLY"
        from_email = settings.DEFAULT_FROM_EMAIL  # Use your default from email from settings

        # Send the email using Django's send_mail function
        send_mail(subject, message, from_email, [email])

        # If you want to show a confirmation page after sending the email:
        msg = "A confirmation email has been sent to your registered email address."
        return render(request, "mail.html", {"email": email, "msg": msg})

    else:
        # If no email is found in session, redirect to home or show an error message
        return redirect('/home')  # Or you can return an error page


def send_cancel_mail(request):
    email = request.session.get('email')  # Retrieve email from session
    if email:
        subject = "Booking Cancellation Confirmation"
        message = "SUCCESSFULLY CANCELLED..... YOUR FUND WILL BE REFUNDED WITHIN 7 DAYS"
        from_email = settings.DEFAULT_FROM_EMAIL  # Use your default from email from settings

        # Send the email using Django's send_mail function
        send_mail(subject, message, from_email, [email])

        # After sending the email, show a confirmation message
        msg = "A cancellation confirmation email has been sent to your registered email address."
        return render(request, "mail.html", {"email": email, "msg": msg})

    else:
        # If no email is found in session, redirect to home or show an error message
        return redirect('/home')  # Or you can return an error page


def admin_view_users(request):
    """View all users categorized by status: applied, approved, and rejected."""
    if 'name' in request.session:
        context = {
            "applied_users": UserRegister.objects.filter(status='applied'),
            "approved_users": UserRegister.objects.filter(status='approved'),
            "rejected_users": UserRegister.objects.filter(status='reject'),
        }
        return render(request, 'admin/admin_view_users.html', context)
    return redirect('login')  # ✅ Use named URL


def admin_approve_user(request, id):
    """Approve a user and move them to the approved list."""
    try:
        user = get_object_or_404(UserRegister, id=id)
        if user.status in ['applied', 'reject']:   # <-- Allow both applied and rejected users
            user.status = 'approved'
            user.save()
            messages.success(request, "User approved successfully!")
        else:
            messages.warning(request, "User cannot be approved.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect("bikeapp:admin_view_users")


def admin_approved_user(request):
    approved_users = UserRegister.objects.filter(status='approved')  # ✅ Fetch from UserRegister, not User
    return render(request, 'admin/admin_approved_user.html', {'approved_users': approved_users})

def admin_reject_user(request, id):
    """Reject a user from either applied or approved status."""
    try:
        user = get_object_or_404(UserRegister, id=id)
        if user.status in ['applied', 'approved']:
            user.status = 'reject'
            user.save()
            messages.success(request, "User rejected successfully!")
        else:
            messages.warning(request, "Only applied or approved users can be rejected.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect("bikeapp:admin_view_users")

def admin_rejected_user(request):
    """View rejected users."""
    rejected_users = UserRegister.objects.filter(status='reject')  # ✅ Fetch from UserRegister, not User
    return render(request, 'admin/admin_rejected_users.html', {'rejected_users': rejected_users})


def admin_restore_user(request, id):
    """Restore a rejected user back to the applied list."""
    try:
        user = get_object_or_404(UserRegister, id=id)
        if user.status == 'reject':
            user.status = 'applied'
            user.save()
            messages.success(request, "User restored successfully!")
        else:
            messages.warning(request, "Only rejected users can be restored.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect("bikeapp:admin_view_users")


def admin_delete_user(request, id):
    """Permanently delete a rejected user."""
    try:
        user = get_object_or_404(UserRegister, id=id)
        if user.status == 'reject':
            user.delete()
            messages.warning(request, "User deleted permanently!")
        else:
            messages.warning(request, "Only rejected users can be deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect("bikeapp:admin_view_users")


# def admin_user_update(request, id):
#     if 'name' in request.session:
#         user = get_object_or_404(UserRegister, id=id)

#         if request.method == "POST":
#             # Get the fields from the POST request
#             name = request.POST.get("name")
#             phone = request.POST.get("phone")
#             address = request.POST.get("address")
#             age = request.POST.get("age")
#             email = request.POST.get("email")
#             place = request.POST.get("place")
#             district = request.POST.get("district")
#             pincode = request.POST.get("pincode")

#             # Ensure that 'name' is not empty and is provided
#             if not name:
#                 messages.error(request, "Name is required.")
#                 return render(request, "admin_user_update.html", {"user": user})
            
#             # Handle file upload if available
#             if 'profile_picture' in request.FILES:
#                 user.profile_picture = request.FILES['profile_picture']

#             # Update the user model
#             user.name = name
#             user.phone = phone
#             user.address = address
#             user.age = age
#             user.email = email
#             user.place = place
#             user.district = district
#             user.pincode = pincode

#             # Save the user object after updating the fields
#             user.save()

#             # Provide success message and redirect to the users list
#             messages.success(request, "User details updated successfully.")
#             return redirect("/admin_view_users")

#         # If the request is GET or form is invalid, just render the update page with the existing user data
#         return render(request, "admin_user_update.html", {"user": user})
    
#     else:
#         # If session 'name' is not set, redirect to login page
#         return redirect("/login")
def admin_view_feedback(request):
    feedback_list = Feedback.objects.all()

    feedback_data = []
    for feedback in feedback_list:
        user_register = UserRegister.objects.filter(user=feedback.user).first()
        profile_picture_url = user_register.profile_picture.url if user_register and user_register.profile_picture else None

        feedback_data.append({
            'user_name': feedback.user.username,
            'profile_picture': profile_picture_url,
            'feedback_text': feedback.feedback,
            'date': feedback.date,
        })

    return render(request, 'admin/admin_view_feedback.html', {'feedback_list': feedback_data})



def admin_add_bike(request):
    msg = ""
    stations = Station.objects.all()
    bikes = Bike.objects.all()

    if request.method == 'POST':
        bikenum = request.POST.get("bikenum", "").strip()
        bikemodel = request.POST.get("bikemodel", "").strip()
        station_id = request.POST.get("station")
        bimg = request.FILES.get('bimg')

        # Validate required fields
        if not all([bikenum, bikemodel, station_id]):
            msg = "All fields are required."
            return render(request, "admin/admin_add_bike.html", 
                        {"msg": msg, "bikes": bikes, "stations": stations})

        try:
            station = get_object_or_404(Station, id=station_id)
            
            # Check station capacity
            current_bike_count = Bike.objects.filter(
                station=station, 
                is_removed=False
            ).count()
            
            if current_bike_count >= station.no_of_bikes:
                msg = (f"Cannot add bike. {station.stationname} has reached "
                    f"its capacity ({current_bike_count}/{station.no_of_bikes} bikes).")
                return render(request, "admin/admin_add_bike.html", 
                            {"msg": msg, "bikes": bikes, "stations": stations})

            # Validate bike number format (alphanumeric with optional hyphens)
            if not re.match(r'^[A-Za-z0-9-]+$', bikenum):
                msg = "Bike number can only contain letters, numbers, and hyphens."
                return render(request, "admin/admin_add_bike.html", 
                            {"msg": msg, "bikes": bikes, "stations": stations})

            # Check for duplicate bike number
            if Bike.objects.filter(bikenum__iexact=bikenum).exists():
                msg = f"Bike number '{bikenum}' already exists."
                return render(request, "admin/admin_add_bike.html", 
                            {"msg": msg, "bikes": bikes, "stations": stations})

            # Validate image if provided
            if bimg:
                if not bimg.content_type.startswith('image/'):
                    msg = "Only image files are allowed."
                    return render(request, "admin/admin_add_bike.html", 
                                {"msg": msg, "bikes": bikes, "stations": stations})
                
                if bimg.size > 5 * 1024 * 1024:  # 5MB limit
                    msg = "Image size should not exceed 5MB."
                    return render(request, "admin/admin_add_bike.html", 
                                {"msg": msg, "bikes": bikes, "stations": stations})

            # Create the bike
            Bike.objects.create(
                bikenum=bikenum,
                bikemodel=bikemodel,
                station=station,
                bimg=bimg
            )
            
            msg = "Bike successfully added!"
            return redirect('admin_view_bikes')  # Redirect to bike list after success

        except Exception as e:
            msg = f"An error occurred: {str(e)}"

    return render(request, "admin/admin_add_bike.html", 
                {"msg": msg, "bikes": bikes, "stations": stations})


def admin_update_bike(request, id):  # Use 'id' to match urls.py
    bike = get_object_or_404(Bike, id=id)
    stations = Station.objects.all()

    if request.method == "POST":
        bike.bikenum = request.POST.get("bikenum")
        bike.bikemodel = request.POST.get("bikemodel")
        bike.status = request.POST.get("status")

        # Handle station ID safely
        station_id = request.POST.get("station")
        try:
            bike.station = get_object_or_404(Station, id=station_id)  # Safely get station
        except ValueError:
            return render(request, "admin/admin_update_bike.html", {
                "msg": "Invalid station ID.",
                "bike": bike,
                "stations": stations
            })

        # Handle file upload if provided
        if request.FILES.get("bimg"):
            img = request.FILES["bimg"]
            fs = FileSystemStorage()
            filename = fs.save(img.name, img)
            bike.bimg = fs.url(filename)

        bike.save()
        return redirect("bikeapp:admin_view_bike")

    return render(request, "admin/admin_update_bike.html", {"bike": bike, "stations": stations})



def admin_view_bike(request):
    bikes = Bike.objects.select_related('station').filter(is_removed=False)  # ✅ Only active bikes
    return render(request, "admin/admin_view_bike.html", {"bikes": bikes})



def admin_delete_bike(request, id):
    bike = get_object_or_404(Bike, id=id)  # Get the bike or return 404 error
    bike.delete()  # Delete the bike
    
    messages.success(request, "Bike deleted successfully.")  # Show a success message
    
    return redirect("bikeapp:admin_view_bike")  # Redirect to the bike list view

def admin_remove_bike(request, id):
    """ Mark bike as removed (soft delete) """
    bike = get_object_or_404(Bike, id=id)
    bike.is_removed = True
    bike.save()
    return redirect("bikeapp:admin_view_bike")


def admin_removed_bikes(request):
    """ Display all removed bikes """
    bikes = Bike.objects.filter(is_removed=True).select_related('station').order_by('id')
    return render(request, "admin/admin_removed_bikes.html", {"bikes": bikes})


def admin_restore_bike(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)
    bike.is_removed = False
    bike.save()
    return redirect("bikeapp:admin_removed_bikes")

from django.shortcuts import render, get_object_or_404
from .models import Feedback


def admin_add_station(request):
    msg = ""
    if request.method == "POST":
        try:
            # Get and clean input data
            stationname = request.POST.get("stationname", "").strip()
            place = request.POST.get("place", "").strip()
            no_of_bikes = request.POST.get("no_of_bikes", "0").strip()
            
            # Basic validation
            if not stationname or not place:
                raise ValidationError("Station name and place are required")
            
            if not no_of_bikes:
                raise ValidationError("Number of bikes is required")
            
            # Case-insensitive duplicate check
            if Station.objects.filter(stationname__iexact=stationname).exists():
                raise ValidationError("Station with this name already exists")
            
            # Create station - let model handle number conversion and validation
            station = Station(
                stationname=stationname,
                place=place,
                no_of_bikes=no_of_bikes  # String value - model will convert
            )
            station.full_clean()  # Run model validation
            station.save()
            
            # Success message without redirect
            msg = "Station successfully added!"
            
        except ValidationError as e:
            msg = ", ".join(e.messages)
        except ValueError:
            msg = "Number of bikes must be a valid positive number"
        except Exception as e:
            msg = f"Error creating station: {str(e)}"
            # Log the full error for debugging
            logging.error(f"Station creation error: {str(e)}", exc_info=True)

    # GET request or failed POST
    station_data = Station.objects.filter(is_removed=False).order_by('stationname')
    return render(request, "admin/admin_add_station.html", {
        "msg": msg,
        "station_data": station_data,
        "form_data": {  # Return entered values to repopulate form on error
            "stationname": request.POST.get("stationname", ""),
            "place": request.POST.get("place", ""),
            "no_of_bikes": request.POST.get("no_of_bikes", "")
        } if request.method == "POST" else None
    })


def admin_delete_station(request, id):
    try:
        station = Station.objects.get(id=id)
        station.delete()
        return redirect("/admin_view_station")  # Use name-based redirect
    except Station.DoesNotExist:
        return HttpResponse("Station not found")

def admin_view_station(request):
    stations = Station.objects.filter(is_removed=False).order_by('id') # Retrieve all stations ordered by ID
    return render(request, "admin/admin_view_station.html", {"stations": stations})

def admin_update_station(request, id):
    try:
        station = Station.objects.get(id=id)
    except Station.DoesNotExist:
        return redirect('/admin_view_station/', 
                      {'message': 'Station not found'})

    if request.method == "POST":
        try:
            # Get form data
            station.stationname = request.POST.get("stationname", "").strip()
            station.place = request.POST.get("place", "").strip()
            
            # Convert and validate bike count
            new_capacity = request.POST.get("no_of_bikes")
            if not new_capacity or not new_capacity.isdigit():
                raise ValueError("Number of bikes must be a positive integer")
            
            station.no_of_bikes = int(new_capacity)
            station.save()
            
            return redirect('/admin_view_station/', 
                          {'message': 'Updated successfully'})
            
        except ValueError as e:
            return render(request, "admin/admin_update_station.html", {
                'station': station,
                'error_message': str(e)
            })
        except Exception as e:
            return render(request, "admin/admin_update_station.html", {
                'station': station,
                'error_message': f"An error occurred: {str(e)}"
            })

    return render(request, "admin/admin_update_station.html", 
                {'station': station})


def admin_remove_station(request, id):
    """ Mark station as removed (soft delete) """
    station = get_object_or_404(Station, id=id)
    station.is_removed = True
    station.save()
    return redirect("/admin_view_station")


def admin_removed_stations(request):
    """ Display all removed stations """
    stations = Station.objects.filter(is_removed=True).order_by('id')
    return render(request, "admin/admin_removed_stations.html", {"stations": stations})


def admin_restore_station(request, id):
    """ Restore a removed station """
    station = get_object_or_404(Station, id=id)
    station.is_removed = False
    station.save()
    return redirect("/admin_removed_stations")

def admin_view_booking(request):
    # Fetching all bookings using Django ORM
    bookings = Booking.objects.all()
    return render(request, "admin/admin_view_booking.html", {"bookings": bookings})

def admin_view_reply(request):
    # Fetching all feedback and replies using Django ORM
    data = Feedback.objects.all().values('feedback', 'date', 'reply')
    return render(request, "admin/admin_view_reply.html", {"data": data})

def admin_home(request):
    return render(request, "admin/admin_home.html")

def user_home(request):
    return render(request, "user/user_home.html")

def userheader(request):
    return render(request, "user/userheader.html")

from django.template.loader import get_template
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')




# Set up logging
logger = logging.getLogger(__name__)

def user_book_bike(request):
    msg = ""
    stations = Station.objects.filter(is_removed=False)
    available_bikes = Bike.objects.filter(status='available', is_removed=False)

    if request.method == "POST":
        try:
            # Validate required fields
            required_fields = ['sstation', 'estation', 'bikenum', 'start_datetime', 'end_datetime']
            for field in required_fields:
                if not request.POST.get(field):
                    return HttpResponse(f"Error: {field.replace('_', ' ').title()} is required.", status=400)

            sstation_id = request.POST.get("sstation").strip()
            estation_id = request.POST.get("estation").strip()
            bikenum = request.POST.get("bikenum").strip()
            start_datetime_str = request.POST.get("start_datetime").strip()
            end_datetime_str = request.POST.get("end_datetime").strip()
            submitted_distance = request.POST.get("calculated_distance", "0").strip()

            if not request.user.is_authenticated:
                return HttpResponse("Session expired. Please log in.", status=403)

            # Get station and bike objects
            start_station = get_object_or_404(Station, id=sstation_id, is_removed=False)
            end_station = get_object_or_404(Station, id=estation_id, is_removed=False)
            bike = get_object_or_404(Bike, bikenum__iexact=bikenum, is_removed=False, status='available')

            # Parse datetime
            start_datetime = make_aware(datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M"))
            end_datetime = make_aware(datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M"))

            if end_datetime <= start_datetime:
                return HttpResponse("Error: Return date/time must be after start date/time.", status=400)

            # Calculate distance (use submitted or recalculate)
            try:
                distance = float(submitted_distance)
                if distance <= 0:
                    raise ValueError("Invalid submitted distance")
            except (ValueError, TypeError):
                logger.warning(f"Invalid distance submitted: {submitted_distance}. Recalculating...")
                distance = geodesic(
                    (start_station.latitude, start_station.longitude),
                    (end_station.latitude, end_station.longitude)
                ).km

            # Calculate pricing
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            hourly_rate = 50
            total_amount = round(duration_hours * hourly_rate, 2)
            advance_paid = 500 if duration_hours < 24 else 1000
            final_amount_due = max(0, total_amount - advance_paid)

            # Clear previous session data
            request.session.pop('amount', None)
            request.session.pop('advance_paid', None)
            request.session.pop('final_amount_due', None)
            request.session.pop('booking_id', None)

            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                strtstation=start_station,
                endstation=end_station,
                bikenum=bike,
                amount=total_amount,
                advance_paid=advance_paid,
                final_amount_due=final_amount_due,
                distance=distance
            )

            # Update session
            request.session['amount'] = str(total_amount)
            request.session['advance_paid'] = str(advance_paid)
            request.session['final_amount_due'] = str(final_amount_due)
            request.session['booking_id'] = booking.id

            # Mark bike as booked
            bike.status = 'booked'
            bike.save()

            return redirect(f"/payment1/{booking.id}/")

        except Bike.DoesNotExist:
            return HttpResponse("Error: Selected bike does not exist or is not available.", status=400)
        except Station.DoesNotExist:
            return HttpResponse("Error: Selected station does not exist.", status=400)
        except ValueError as e:
            return HttpResponse(f"Invalid data format: {str(e)}", status=400)
        except Exception as e:
            logger.error(f"Booking error: {str(e)}", exc_info=True)
            return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)

    # Handle AJAX request for bike list
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        available_bikes = Bike.objects.filter(
            status='available', 
            is_removed=False
        ).values('bikenum', 'bikemodel', 'bimg')
        return JsonResponse(list(available_bikes), safe=False)

    return render(request, "user/user_book_bike.html", {
        "stations": stations,
        "available_bikes": available_bikes,
        "msg": msg
    })

def return_bike(request):
    """Handles bike return after checking pending payment."""

    if request.GET:
        bikenum = request.GET.get("bikenum")
        sstation = request.GET.get("sstation")

        # Fetch bike and station
        bike = get_object_or_404(Bike, bikenum=bikenum)
        station = get_object_or_404(Station, stationname=sstation)

        # Get the latest active booking
        booking = Booking.objects.filter(bikenum=bike, rtrn=False).order_by('-start_datetime').first()

        if not booking:
            messages.error(request, "No active booking found for this bike.")
            return redirect(reverse("bikeapp:user_view_booking"))

        # 🔄 Refresh booking data from DB
        booking.refresh_from_db()

        # Calculate remaining balance (Convert Decimal to float)
        final_amount_due = float(max(0, booking.amount - booking.advance_paid))

        # Redirect to payment if balance is pending
        if final_amount_due > 0:
            request.session["final_amount_due"] = final_amount_due  # ✅ Store remaining amount
            request.session["booking_id"] = booking.id
            messages.warning(request, "You must pay the remaining balance before returning the bike.")
            return redirect(reverse("bikeapp:payment_balance", args=[booking.id]))

        # ✅ Payment complete, proceed with return

        # Mark bike as available and update station
        bike.status = 1  # Set bike as available
        bike.station = station  # Update bike's new station
        bike.save(update_fields=["status", "station"])

        # Increase available bikes at the return station
        station.no_of_bikes += 1
        station.save(update_fields=["no_of_bikes"])

        # Update booking details
        booking.rtrn = True
        booking.status = "Completed"
        booking.end_time = now()  # Store full date & time
        booking.save(update_fields=["rtrn", "status", "end_datetime"])

        messages.success(request, "Bike returned successfully!")
        return redirect(reverse("bikeapp:user_view_booking"))

    messages.error(request, "Invalid request. Please select a bike to return.")
    return redirect(reverse("bikeapp:user_view_booking"))
# Payment Process
def payment1(request, booking_id):
    """Initial payment step where user enters card details."""
    booking = get_object_or_404(Booking, id=booking_id)

    advance_paid = request.session.get("advance_paid", 0)  # Retrieve stored advance

    if request.method == "POST":
        request.session["card_no"] = request.POST.get("cardno")
        request.session["pinno"] = request.POST.get("pinno")
        return redirect('bikeapp:payment2', booking_id=booking_id)

    return render(request, 'payment/payment1.html', {
        'booking_id': booking_id,
        'advance_paid': advance_paid  # Pass to template
    })



@login_required
def payment2(request, booking_id):
    """Processes the payment for a booking."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    advance_paid = request.session.get("advance_paid", 0)  # Retrieve stored advance

    if request.method == "POST":
        if all(request.POST.get(field) for field in ["cno", "full_name", "billing_address", "email", "phone_number"]):
            transaction_id = random.randint(100000, 999999)
            booking.payment_status = "Paid"
            booking.transaction_id = transaction_id
            booking.save()

            messages.success(request, f"Payment Successful! Transaction ID: {transaction_id}")
            return redirect("bikeapp:payment3")

    return render(request, 'payment/payment2.html', {
        "booking_id": booking.id,
        "bike_name": booking.bikenum.bikenum,
        "rental_period": f"{booking.start_datetime.strftime('%Y-%m-%d %H:%M')} to {booking.end_datetime.strftime('%Y-%m-%d %H:%M')}",
        "advance_payment": advance_paid,  # Ensure advance amount is passed
        "total_cost": booking.total_amount,
        "user": request.user,
    })

def payment3(request, booking_id):
    # Process the payment and then render payment3.html
    # You'll need to add your payment processing logic here
    return render(request, 'payment/payment3.html', {'booking_id': booking_id})

def payment4(request):
    return render(request, "payment/payment4.html")

def payment_last(request):
    # Get session data
    cno = request.session.get("card_no")  
    name = request.session.get("name", "Guest")
    try:
        advance_paid = float(request.session.get("advance_paid", 0))
        total_amount = float(request.session.get("amount", 0))
    except (ValueError, TypeError):
        messages.error(request, "Invalid payment amounts")
        return redirect('/payment_error/')
    final_amount = total_amount - advance_paid
    booking_id = request.session.get("booking_id")
    today = datetime.now()

    # Validate required data
    if not cno or not final_amount:
        return redirect('/payment_error/')

    if request.method == "POST":
        try:
            booking_instance = Booking.objects.get(id=booking_id)
            
            # Create payment record
            payment = Payment_last.objects.create(
                card_no=request.POST.get("card_no"),
                pin_no=request.POST.get("pin_no"),
                amount=final_amount,
                status=True,
                booking=booking_instance
            )
            
            # Send receipt email
            try:
                send_receipt(request.user.email, name, final_amount, payment.id)
                messages.success(request, "Payment successful! Receipt sent to your email.")
            except Exception as e:
                messages.warning(request, f"Payment successful but couldn't send email: {str(e)}")
            
            return redirect('payment5')
            
        except Booking.DoesNotExist:
            messages.error(request, "Booking not found!")
            return redirect('/payment_error/')
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect('/payment_error/')

    context = {
        "cno": cno,
        "today": today.strftime("%Y-%m-%d"),
        "name": name,
        "advance_paid": advance_paid,
        "final_amount": final_amount,
        "total_amount": total_amount,
        "booking_id": booking_id,
        "user": request.user
    }
    return render(request, "payment/payment5.html", context)


from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_receipt(request):
    if request.method == 'POST':
        context = {
            'name': request.POST.get('name'),
            'amount': request.POST.get('amount'),
            'transaction_id': request.POST.get('transaction_id'),
            'payment_date': timezone.now(),
            'payment_method': request.POST.get('payment_method', 'Credit Card'),
            'last_four': request.POST.get('card_no')[-4:],
            'bike_name': request.POST.get('bike_name'),
            'bike_number': request.POST.get('bike_number'),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'duration': request.POST.get('duration'),
            'pickup_station': request.POST.get('pickup_station'),
            'total_amount': request.POST.get('total_amount'),
            'advance_paid': request.POST.get('advance_paid'),
            'site_url': request.build_absolute_uri('/')
        }
        
        # Render email template
        message = render_to_string('email/receipt_email.txt', {
            'name': name,
            'amount': request.POST.get('amount'),
            'transaction_id': request.POST.get('transaction_id', 'N/A'),
        })
        
        # Send email
        send_mail(
            'Your Payment Receipt',
            message,
            'noreply@electrostation.com',
            [request.user.email],
            fail_silently=False,
        )
        
        return redirect('payment5')  # Redirect back to success page
        
    return redirect('user_home')

def user_view_booking(request):
    if request.session.get('id'):  
        user_id = request.session['id']  

        # Ensure you're fetching related models correctly
        user_bookings = Booking.objects.filter(user__id=user_id, rtrn=False).select_related(
            'strtstation', 'endstation', 'bikenum'
        )

        return render(request, "user/user_view_booking.html", {"bookings": user_bookings})
    else:
        return render(request, "error.html", {"message": "User not logged in"})

@login_required
def user_booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-start_datetime")  # Fetch user's past bookings
    return render(request, "user/user_booking_history.html", {"bookings": bookings})




def pay_remaining_balance(request, booking_id):
    """Handles final balance payment before returning the bike."""
    booking = get_object_or_404(Booking, id=booking_id)

    # Calculate remaining balance dynamically
    final_amount_due = max(0, booking.amount - booking.advance_paid)

    if final_amount_due == 0:
        return redirect(reverse("bikeapp:user_view_booking"))

    if request.method == "POST":
        print("✅ POST request received")  # Debugging line

        card_no = request.POST.get("cardno", "").replace(" ", "")  # Changed from card_no to cardno
        pin_no = request.POST.get("pinno", "")  # Changed from pin_no to pinno

        if not card_no or not pin_no:
            messages.error(request, "Card number and PIN are required!")
            print("❌ Missing card_no or pin_no")  # Debugging line
            return render(request, "payment/payment_balance.html", {
                "booking_id": booking_id,
                "bike_num": booking.bikenum.bikenum,  # Changed from bike_name to bike_num
                "final_amount_due": final_amount_due
            })

        # Validate card number (16 digits)
        if not re.match(r'^\d{16}$', card_no):
            messages.error(request, "Invalid card number (must be 16 digits)")
            return render(request, "payment/payment_balance.html", {
                "booking_id": booking_id,
                "bike_num": booking.bikenum.bikenum,
                "final_amount_due": final_amount_due
            })

        # Validate PIN (4 digits)
        if not re.match(r'^\d{4}$', pin_no):
            messages.error(request, "Invalid PIN (must be 4 digits)")
            return render(request, "payment/payment_balance.html", {
                "booking_id": booking_id,
                "bike_num": booking.bikenum.bikenum,
                "final_amount_due": final_amount_due
            })

        # Process payment & update advance_paid
        booking.advance_paid += final_amount_due
        booking.save(update_fields=["advance_paid"])

        # Log payment in Payment_last model (only storing last 4 digits of card for security)
        Payment_last.objects.create(
            card_no=card_no[-4:],  # Store only last 4 digits
            pin_no=pin_no,
            amount=final_amount_due,
            status='success',  # Changed from True to 'success' to match model
            booking=booking,
            payment_type='final'  # Added to distinguish final payments
        )

        # Refresh from DB to ensure update
        booking.refresh_from_db()
        print(f"✅ Updated advance_paid: {booking.advance_paid}")

        # Clear session data AFTER updating booking
        request.session.pop("final_amount_due", None)
        request.session.pop("booking_id", None)

        print("✅ Payment successful, redirecting")  # Debugging line
        messages.success(request, f"Final payment of ₹{final_amount_due} successful! You can now return the bike.")
        return redirect(reverse("bikeapp:return_bike") + f"?bikenum={booking.bikenum.bikenum}&sstation={booking.endstation.stationname}")

    print("❌ POST request not received")  # Debugging line
    return render(request, "payment/payment_balance.html", {
        "booking_id": booking_id,
        "bike_num": booking.bikenum.bikenum,  # Changed from bike_name to bike_num
        "final_amount_due": final_amount_due
    })




def predict(request):
    stations = Station.objects.all()
    prediction_result = ""

    if request.method == "POST":
        station_id = request.POST.get("station")

        # Fetch booking count per day for the selected station using start_datetime
        bookings = (
            Booking.objects.filter(strtstation_id=station_id)
            .annotate(date=models.functions.TruncDate("start_datetime"))  
            .values("date")
            .annotate(count=Count("bikenum"))
        )

        if not bookings.exists():
            return render(request, "predict.html", {"stations": stations, "prediction_result": "No data available"})

        station_instance = Station.objects.get(id=station_id)

        # Delete old predictions for this station
        Predict.objects.filter(sid=station_instance).delete()

        # Store new predictions
        for booking in bookings:
            Predict.objects.create(count=booking["count"], sid=station_instance)

        # Find station with the highest booking count
        highest_station = (
            Predict.objects.values("sid_id")
            .annotate(max_count=Max("count"))
            .order_by("-max_count")
            .first()
        )

        if highest_station:
            highest_station_obj = Station.objects.get(id=highest_station["sid_id"])
            prediction_result = highest_station_obj.stationname

        # Prepare CSV for Regression
        with NamedTemporaryFile(delete=False, mode="w", newline="") as temp_file:
            writer = csv.writer(temp_file)
            for booking in bookings:
                writer.writerow([booking["count"], booking["date"]])
            temp_file_path = temp_file.name

        # Load CSV
        df = pd.read_csv(temp_file_path, header=None, names=["NUM", "DATE"])
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["DATE_ORDINAL"] = df["DATE"].map(pd.Timestamp.toordinal)

        # Train Linear Regression Model
        X = df[["DATE_ORDINAL"]]
        y = df["NUM"]
        model = LinearRegression()
        model.fit(X, y)

        # Predict the next 7 days
        future_dates = [df["DATE"].max() + pd.Timedelta(days=i) for i in range(1, 8)]
        future_ordinal = [d.toordinal() for d in future_dates]
        predictions = model.predict(np.array(future_ordinal).reshape(-1, 1))

        # Plot past data
        plt.figure(figsize=(8, 5))
        plt.plot(df["DATE"], df["NUM"], marker="o", linestyle="-", color="b", label="Past Data")

        # Plot future predictions
        plt.plot(future_dates, predictions, marker="o", linestyle="--", color="r", label="Predicted")

        plt.xlabel("Date")
        plt.ylabel("Number of Bookings")
        plt.title("Booking Trend & Prediction")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.show()

    return render(request, "predict.html", {"stations": stations, "prediction_result": prediction_result})

from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Custom replace filter"""
    old, new = arg.split(',')
    return value.replace(old.strip(), new.strip())


from django.db.models import Count, Sum, Q
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Bike, Station, Booking, UserRegister, Feedback

from django.db.models.functions import TruncDay, TruncHour
from django.db.models import Avg

from django.db.models import Count, Sum, Avg, Max, F
from django.db.models.functions import TruncDay, TruncHour
from datetime import datetime, timedelta
from .models import Bike, Station, Booking, UserRegister, Feedback, Payment_last

def admin_analytics_dashboard(request):
    # Date range handling (last 30 days by default)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 1. Core Metrics
    total_bikes = Bike.objects.count()
    available_bikes = Bike.objects.filter(status='available').count()
    booked_bikes = Bike.objects.filter(status='booked').count()
    active_rentals = Booking.objects.filter(status='active').count()
    total_stations = Station.objects.count()
    total_users = UserRegister.objects.count()
    active_users = UserRegister.objects.filter(status='approved').count()
    pending_feedback = Feedback.objects.filter(reply__isnull=True).count()

    # 2. Top Station
    top_station = Station.objects.annotate(
        rental_count=Count('start_station')
    ).order_by('-rental_count').first()

    # 3. Revenue Calculations
    monthly_revenue = Payment_last.objects.filter(
        timestamp__month=datetime.now().month,
        status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    last_month_revenue = Payment_last.objects.filter(
        timestamp__month=datetime.now().month-1,
        status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    revenue_change = monthly_revenue > last_month_revenue
    revenue_percentage = abs((
        (monthly_revenue - last_month_revenue) / last_month_revenue * 100
    ) if last_month_revenue else 0)

    # 4. Rental Analytics
    rentals_data = (
        Booking.objects.filter(start_datetime__range=(start_date, end_date))
        .annotate(day=TruncDay('start_datetime'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # 5. Financial Metrics
    revenue_data = (
        Payment_last.objects.filter(
            status='success',
            timestamp__range=(start_date, end_date)
        )
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    # 6. Station Utilization
    station_utilization = (
        Station.objects.annotate(
            pickup_count=Count('start_station'),
            dropoff_count=Count('end_station'),
            avg_rental_duration=Avg(
                Booking.objects.filter(strtstation=models.OuterRef('pk'))
                .annotate(duration=models.F('end_datetime') - models.F('start_datetime'))
                .values('duration')
            )
        ).order_by('-pickup_count')[:5]
    )

    # 7. Peak Hours Analysis
    peak_hours = (
        Booking.objects.filter(start_datetime__range=(start_date, end_date))
        .annotate(hour=TruncHour('start_datetime'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # 8. Bike Utilization
    bike_utilization = (
        Bike.objects.annotate(
            rental_count=Count('booking'),
            last_rental=Max('booking__start_datetime')
        )
        .order_by('-rental_count')[:10]
    )

    # 9. Bike Models Distribution
    bike_models = (
        Bike.objects.values('bikemodel')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # 10. Recent Bookings
    recent_bookings = (
        Booking.objects.select_related('bikenum', 'user')
        .order_by('-start_datetime')[:5]
    )

    context = {
        # Core Metrics
        'total_bikes': total_bikes,
        'available_bikes': available_bikes,
        'booked_bikes': booked_bikes,
        'active_rentals': active_rentals,
        'total_stations': total_stations,
        'top_station': top_station,
        'total_users': total_users,
        'active_users': active_users,
        'pending_feedback': pending_feedback,
        'monthly_revenue': monthly_revenue,
        'revenue_change': revenue_change,
        'revenue_percentage': round(revenue_percentage, 1),
        
        # Chart Data
        'rentals_data': list(rentals_data),
        'revenue_data': list(revenue_data),
        'station_utilization': station_utilization,
        'peak_hours': list(peak_hours),
        'bike_utilization': bike_utilization,
        'bike_models': list(bike_models),
        'recent_bookings': recent_bookings,
        
        # Date Info
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        
        # Pre-formatted data for JavaScript
        'rental_days': [r['day'].strftime('%d %b') for r in rentals_data],
        'rental_counts': [r['count'] for r in rentals_data],
        'revenue_days': [r['day'].strftime('%d %b') for r in revenue_data],
        'revenue_amounts': [r['total'] for r in revenue_data],
        'station_names': [s.stationname for s in station_utilization],
        'pickup_counts': [s.pickup_count for s in station_utilization],
        'dropoff_counts': [s.dropoff_count for s in station_utilization],
        'peak_hour_labels': [h['hour'].strftime('%H:%M') for h in peak_hours],
        'peak_hour_counts': [h['count'] for h in peak_hours],
        'bike_model_names': [bm['bikemodel'] for bm in bike_models],
        'bike_model_counts': [bm['count'] for bm in bike_models],
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)

from django.utils import timezone
from datetime import timedelta

def fetch_weather_data():
    """Fetch weather data from OpenWeatherMap API."""
    API_KEY = "your_api_key_here"
    CITY = "your_city"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = request.get(url).json()
        WeatherData.objects.create(
            date=timezone.now().date(),
            temperature=response['main']['temp'],
            precipitation=response.get('rain', {}).get('1h', 0),
            weather_condition=response['weather'][0]['main']
        )
    except Exception as e:
        print(f"Weather API Error: {e}")

def generate_training_data():
    """Convert Booking data into a CSV for ML training."""
    bookings = Booking.objects.all().select_related('bikenum', 'strtstation')
    
    data = []
    for booking in bookings:
        data.append({
            "date": booking.start_datetime.date(),
            "hour": booking.start_datetime.hour,
            "station_id": booking.strtstation.id,
            "bike_model": booking.bikenum.bikemodel,
            "is_weekend": booking.start_datetime.weekday() >= 5,
            "is_peak_hour": booking.is_peak_hour,
            "duration": (booking.end_datetime - booking.start_datetime).seconds / 60,
            "temperature": WeatherData.objects.filter(date=booking.start_datetime.date()).first().temperature if WeatherData.objects.filter(date=booking.start_datetime.date()).exists() else None,
            "precipitation": WeatherData.objects.filter(date=booking.start_datetime.date()).first().precipitation if WeatherData.objects.filter(date=booking.start_datetime.date()).exists() else 0,
            "is_holiday": Holiday.objects.filter(date=booking.start_datetime.date()).exists(),
        })
    
    # Convert to DataFrame and save as CSV
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv("bike_rental_training_data.csv", index=False)
    return df

from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib
import os

def train_prediction_model(request):
    """Train an ML model to predict demand."""
    if not os.path.exists("bike_rental_training_data.csv"):
        generate_training_data()
    
    df = pd.read_csv("bike_rental_training_data.csv")
    df = df.dropna()  # Remove missing values
    
    # Feature engineering
    X = df[["hour", "station_id", "is_weekend", "is_peak_hour", "temperature", "precipitation", "is_holiday"]]
    y = df["duration"]  # Or use bookings count for demand prediction
    
    # Train a simple Random Forest model
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    # Save the model for future use
    joblib.dump(model, "bike_demand_model.pkl")
    return HttpResponse("Model trained successfully!")

def predict_demand(request):
    """Predict bike demand for a given station and time."""
    if not os.path.exists("bike_demand_model.pkl"):
        return HttpResponse("Model not trained yet. Run /train_model first.")
    
    model = joblib.load("bike_demand_model.pkl")
    
    # Example prediction for Station 1 at 8 AM on a weekday
    input_data = pd.DataFrame([{
        "hour": 8,
        "station_id": 1,
        "is_weekend": False,
        "is_peak_hour": True,
        "temperature": 25.0,
        "precipitation": 0.0,
        "is_holiday": False,
    }])
    
    predicted_demand = model.predict(input_data)[0]
    return JsonResponse({"predicted_demand": predicted_demand})

