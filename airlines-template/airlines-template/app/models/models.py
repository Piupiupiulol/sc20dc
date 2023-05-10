from django.db import models
from django.core.validators import RegexValidator




class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="flight")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="customer")
    payment_provider = models.ForeignKey("PSP", on_delete=models.CASCADE, related_name="payment_provider")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    booking_datetime = models.DateTimeField()
    BOOKING_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )
    booking_status = models.CharField(max_length=250, choices=BOOKING_STATUS_CHOICES)
    transaction_id = models.CharField(max_length=250)
    success_key = models.CharField(max_length=250)


class Flight(models.Model):
    id = models.AutoField(primary_key=True)
    destination_airport = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name='destination_airport')
    departure_airport = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name='departure_airport')
    flight_number = models.CharField(max_length=250)
    departure_datetime = models.DateTimeField()
    duration = models.DurationField()
    price_per_seat = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_seat = models.DecimalField(max_digits=8, decimal_places=2)
    aircraft = models.ForeignKey("Aircraft", on_delete=models.CASCADE, related_name="aircraft")

class Airport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    time_zone = models.SmallIntegerField(null=True, default=0)

    def __str__(self):
        return self.name

class Aircraft(models.Model):
    id = models.AutoField(primary_key=True)
    tail_number = models.CharField(max_length=250)
    model = models.CharField(max_length=250)
    number_of_seats = models.PositiveBigIntegerField(null=True, default=0)
    
    def __str__(self):
        return self.tail_number

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    passport_number = models.CharField(max_length=20)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email_address = models.EmailField(max_length=255, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)

class PSP(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    url = models.URLField(max_length=250)
    account_id = models.PositiveSmallIntegerField()
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)


