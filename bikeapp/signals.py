# signals.py (create new file)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Booking
import joblib
import pandas as pd
import requests

@receiver(pre_save, sender=Booking)
def predict_demand(sender, instance, **kwargs):
    if not instance.estimated_demand:
        try:
            model = joblib.load("bike_demand_model.pkl")
            input_data = pd.DataFrame([{
                "hour": instance.start_datetime.hour,
                "station_id": instance.strtstation.id,
                "is_weekend": instance.start_datetime.weekday() >= 5,
                "is_peak_hour": instance.is_peak_hour,
                "temperature": get_current_temperature(),  # Fetch real-time temperature
                "precipitation": get_current_precipitation(),  # Fetch real-time precipitation
                "is_holiday": is_holiday(instance.start_datetime.date()),  # Check if it's a holiday
            }])
            instance.estimated_demand = model.predict(input_data)[0]
        except Exception as e:
            instance.estimated_demand = None
            print(f"Error predicting demand: {str(e)}")


def get_current_temperature():
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "London,uk",  # Replace with the desired location
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"]
    else:
        return None
    pass

def get_current_precipitation():
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "London,uk",  # Replace with the desired location
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "rain" in data:
            return data["rain"]["1h"]
        elif "snow" in data:
            return data["snow"]["1h"]
        else:
            return 0
    else:
        return None

def is_holiday(date):
    holidays = [
        "2022-01-01",  # New Year's Day
        "2022-04-15",  # Good Friday
        "2022-04-18",  # Easter Monday
        "2022-05-02",  # Early May Bank Holiday
        "2022-06-03",  # Spring Bank Holiday
        "2022-08-29",  # Summer Bank Holiday
        "2022-12-26",  # Boxing Day
        "2022-12-27",  # Christmas Day (substitute day)
    ]
    return date.strftime("%Y-%m-%d") in holidays