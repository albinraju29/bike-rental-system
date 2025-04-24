from django.apps import AppConfig


class BikeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bikeapp'

    def ready(self):
        import bikeapp.signals  # Add this line