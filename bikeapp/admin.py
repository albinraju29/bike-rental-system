from django.contrib import admin
from .models import UserRegister, Station, Bike, Booking, Feedback

# Register models normally
admin.site.register(UserRegister)
admin.site.register(Station)
admin.site.register(Bike)
admin.site.register(Feedback)

# Custom admin for Booking model
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'bikenum', 'strtstation', 'endstation', 'duration_display', 'status')  
    list_filter = ('status',)  # Admin can filter bookings by status

    def duration_display(self, obj):
        if obj.start_datetime and obj.end_datetime:
            return round((obj.end_datetime - obj.start_datetime).total_seconds() / 3600, 2)  # Convert seconds to hours
        return "N/A"
    
    duration_display.short_description = "Duration (hrs)"  # Column name in Django Admin

admin.site.register(Booking, BookingAdmin)  # Register with custom admin
