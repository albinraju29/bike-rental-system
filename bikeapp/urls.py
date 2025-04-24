from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'bikeapp'

urlpatterns = [
    # Admin-related routes
    path('admin_add_bike/', views.admin_add_bike, name='admin_add_bike'),
    path('admin_view_bike/', views.admin_view_bike, name='admin_view_bike'),
    path("admin_remove_bike/<int:id>/", views.admin_remove_bike, name="admin_remove_bike"),
    path("admin_removed_bikes/", views.admin_removed_bikes, name="admin_removed_bikes"),
    path("admin_restore_bike/<int:bike_id>/", views.admin_restore_bike, name="admin_restore_bike"),

    path('admin_delete_bike/<int:id>/', views.admin_delete_bike, name='admin_delete_bike'),
    path('admin_update_bike/<id>', views.admin_update_bike, name='admin_update_bike'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_add_station/', views.admin_add_station, name='admin_add_station'),
    path('admin_view_station/', views.admin_view_station, name='admin_view_station'),

    path('admin_delete_station/<id>', views.admin_delete_station, name='admin_delete_station'),
    path('admin_update_station/<int:id>/', views.admin_update_station, name='admin_update_station'),
    path('admin_remove_station/<int:id>/', views.admin_remove_station, name='admin_remove_station'),
    path('admin_removed_stations/', views.admin_removed_stations, name='admin_removed_stations'),  # No arguments here
    path('admin_restore_station/<int:id>/', views.admin_restore_station, name='admin_restore_station'),

    path('admin_view_booking/', views.admin_view_booking, name='admin_view_booking'),
    
    path('admin_view_feedback/', views.admin_view_feedback, name='admin_view_feedback'),
    # path('admin_add_reply/<int:feedback_id>/', views.admin_add_reply, name='admin_add_reply'),
    path('admin_view_users/', views.admin_view_users, name='admin_view_users'),
    path('admin_approved_user/', views.admin_approved_user, name='admin_approved_user'),  # View approved users
    path('admin_approved_user/<int:id>/', views.admin_approve_user, name='admin_approve_user'),  # Approve user
    path('admin_rejected_user/', views.admin_rejected_user, name='admin_rejected_users'),  # View rejected users
    path('admin_rejected_user/<int:id>/', views.admin_reject_user, name='admin_reject_user'),  # Reject user
    path('admin_restore_user/<int:id>/', views.admin_restore_user, name='admin_restore_user'),  # Restore user
    path('admin_delete_user/<int:id>/', views.admin_delete_user, name='admin_delete_user'),  # Delete user

    # path('admin_user_update/<id>', views.admin_user_update, name='admin_user_update'),

    path('admin_analytics/', views.admin_analytics_dashboard, name='admin_analytics'),

    # User-related routes
    path('user_home/', views.user_home, name='user_home'),
    path('user_book_bike/', views.user_book_bike, name='user_book_bike'),
    path('user_feedback/', views.user_feedback, name='user_feedback'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_view_booking/', views.user_view_booking, name='user_view_booking'),
    path("user_booking_history/", views.user_booking_history, name="user_booking_history"),
    path('userupdprofile/', views.userupdprofile, name='userupdprofile'),
    path('user_view_reply/', views.user_view_reply, name='user_view_reply'),

    # Authentication routes
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    

    # Other routes
    path('', views.index, name='index'),
    path('predict/', views.predict, name='predict'),
    path('return_bike/', views.return_bike, name='return_bike'),
    path('send_mail/', views.send_mail, name='send_mail'),
    path('payment1/<int:booking_id>/', views.payment1, name='payment1'),
    path('payment2/<int:booking_id>/', views.payment2, name='payment2'),
    path('payment_balance/<int:booking_id>/', views.pay_remaining_balance, name='payment_balance'),
    path('payment3/<int:booking_id>/', views.payment3, name='payment3'),
    path('payment4/', views.payment4, name='payment4'),  # Final Payment Confirmation
    path('payment5/', views.payment_last, name='payment_last'),
    path('cancelbooking/', views.cancelbooking, name='cancelbooking'),
    path('process_penalty/<int:booking_id>/', views.process_penalty, name='process_penalty'),

    #password manages

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password/password_reset.html'), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password/password_reset_done.html'), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password/password_reset_confirm.html'), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password/password_reset_complete.html'), name='password_reset_complete'),

    # path('payment-success/', views.payment_success, name='payment_success'),
    path('send-receipt/', views.send_receipt, name='send_receipt'),

    path('train_model/', views.train_prediction_model, name='train_model'),
    path('predict_demand/', views.predict_demand, name='predict_demand'),
    path('fetch_weather/', views.fetch_weather_data, name='fetch_weather'),

]

