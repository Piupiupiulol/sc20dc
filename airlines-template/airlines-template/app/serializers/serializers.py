from rest_framework import serializers
from ..models.models import Flight
from ..models.models import Booking, Customer, PSP

class FlightSerializer(serializers.ModelSerializer):
    departure_airport = serializers.StringRelatedField()
    destination_airport = serializers.StringRelatedField()
    aircraft = serializers.StringRelatedField()

    class Meta:
        model = Flight
        fields = ['id', 'flight_number', 'departure_airport', 'destination_airport', 'departure_datetime', 'duration', 'price_per_seat', 'aircraft']
 

class FlightSearchSerializer(serializers.Serializer):
    departure_airport = serializers.CharField()
    destination_airport = serializers.CharField()
    departure_datetime = serializers.DateField()


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'passport_number',
            'phone_number',
            'email_address',
            'date_of_birth',
            'home_address',
            'allergies',
        ]

class BookingDetailsSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    flight_id = serializers.CharField()
    duration = serializers.StringRelatedField(source='flight.duration')
    booking_status = serializers.CharField()
    destination_airport = serializers.CharField(source='flight.destination_airport')
    departure_airport = serializers.CharField(source='flight.departure_airport')

    class Meta:
        model = Booking
        fields = [
            'id',
            'customer',
            'destination_airport',
            'departure_airport',
            'flight_id',
            'duration',
            'booking_status',
        ]

class PaymentProvidersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    class Meta:
        model = PSP
        fields = [
            'id',
            'name',
            'url'
        ]
    
