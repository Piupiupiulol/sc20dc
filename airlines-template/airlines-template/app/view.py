from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import NotFound
from .models.models import Flight, Booking, PSP, Customer, Ticket
from .serializers.serializers import FlightSerializer, FlightSearchSerializer, BookingDetailsSerializer, PaymentProvidersSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from datetime import datetime
import traceback




class CancelBookingView(APIView):
    def put(self, request):
        try:
            booking_id = request.data['booking_id']

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response("Booking not found", status=status.HTTP_404_NOT_FOUND)

            booking.booking_status = 'CANCELLED'
            booking.save()


            return Response({"booking_id": booking.id, "booking_status": booking.booking_status}, status=status.HTTP_200_OK)
        except KeyError:
            return Response("Booking ID not provided", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("An internal error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateBookingView(APIView):
    def put(self, request, booking_id):
        try:
            customer_details = request.data.get('customer', None)
            departure_datetime_str = request.data.get('departure_datetime', None)
            departure_datetime = None
            if departure_datetime_str:
                departure_datetime = datetime.strptime(departure_datetime_str, '%Y-%m-%dT%H:%M:%S')

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response("Booking not found", status=status.HTTP_404_NOT_FOUND)

            if customer_details:
                for key, value in customer_details.items():
                    if hasattr(booking.customer, key):
                        setattr(booking.customer, key, value)
                booking.customer.save()

            if departure_datetime:
                flight = booking.flight
                flight.departure_datetime = departure_datetime
                flight.save()

            booking.save()

            return Response({"booking_id": booking.id}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("An internal error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ConfirmBookingView(APIView):
    def put(self, request):
        try:
            booking_id = request.data['booking_id']
            success_key = request.data['success_key']

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response("Booking not found", status=status.HTTP_404_NOT_FOUND)

            booking.booking_status = "CONFIRMED"
            booking.success_key = success_key
            booking.save()

        
            tickets = []
            for seat_number in range(1):
                ticket = Ticket.objects.create(
                    booking=booking,
                    customer=booking.customer,
                    seat_number=seat_number
                )
                tickets.append({
                    "ticket_id": ticket.id,
                    "customer_id": ticket.customer.id,
                    "seat_number": ticket.seat_number
                })

            response_data = {
                "booking_id": booking.id,
                "booking_status": booking.booking_status,
                "tickets": tickets
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response("Required data is missing", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Server is down", status=status.HTTP_503_SERVICE_UNAVAILABLE)





class BookFlightView(APIView):
    def post(self, request):
        try:
            flight_id = request.data['flight_id']
            payment_provider_id = request.data['payment_provider_id']
            customers = request.data['customers']

            try:
                flight = Flight.objects.get(id=flight_id)
            except Flight.DoesNotExist:
                return Response("Flight not found", status=status.HTTP_404_NOT_FOUND)

            try:
                payment_provider = PSP.objects.get(id=payment_provider_id)
            except PSP.DoesNotExist:
                return Response("Payment provider not found", status=status.HTTP_404_NOT_FOUND)

            booking_ids = []

            for customer in customers:
                first_name = customer['first_name']
                last_name = customer['last_name']
                passport_number = customer['passport_number']
                email = customer['email']
                phone = customer['phone']
                date_of_birth = datetime.strptime(customer['date_of_birth'], '%Y-%m-%d').date()
                home_address = customer.get('home_address', '')
                allergies = customer.get('allergies', '')

                if not (first_name and last_name and passport_number and email and phone and date_of_birth):
                    raise ValueError("Required fields are missing or empty")

                new_customer = Customer(first_name=first_name,
                                        last_name=last_name,
                                        passport_number=passport_number,
                                        phone_number=phone,
                                        email_address=email,
                                        date_of_birth=date_of_birth,
                                        home_address=home_address,
                                        allergies=allergies)
                new_customer.save()

    
                price = flight.price_per_seat


                booking_datetime = datetime.now()

                booking = Booking.objects.create(flight=flight, customer=new_customer, price=price, booking_datetime=booking_datetime, payment_provider=payment_provider)
                booking_ids.append(booking.id)

            return Response({"booking_ids": booking_ids}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response("Required data is missing", status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("An internal error occurred: " + str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)







def create_transaction(booking, psp_id):
    try:
        transaction_id = str(uuid.uuid4())

        booking.transaction_id = transaction_id
        booking.payment_provider_id = psp_id
        booking.booking_status = 'CONFIRMED'
        booking.save()

        return None, transaction_id
    except Exception as e:
        return f"Error in create_transaction: {e}", None


class PayBookingView(APIView):
    def post(self, request, booking_id):
        psp_id = request.data.get('psp_id')

        if not psp_id:
            return Response("PSP is required.", status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            return Response("Booking not found.", status=status.HTTP_404_NOT_FOUND)

        if not booking:
            return Response("Booking not found.", status=status.HTTP_404_NOT_FOUND)

        try:
            error_message, transaction_id = create_transaction(booking, psp_id)
            if error_message:
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            return Response({"transaction_id": transaction_id}, status=status.HTTP_201_CREATED)
        except Exception as e:

            return Response("Transaction failed to be created.", status=status.HTTP_503_SERVICE_UNAVAILABLE)







class PaymentProviderView(generics.RetrieveAPIView):
    def get(self, request):

        providers = PSP.objects.all()
        search_serializer = PaymentProvidersSerializer(data=request.GET)

        if not search_serializer.is_valid():
  
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        provider_serializer = PaymentProvidersSerializer(providers, many=True)
        return Response(provider_serializer.data)











class FlightDetailView(generics.RetrieveAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_object(self):
        try:
            return Flight.objects.get(id=self.kwargs['flight_id'])
        except Flight.DoesNotExist:
            raise NotFound("Flight not found : )))")
        




class FlightSearchView(APIView):
    def get(self, request):

        search_serializer = FlightSearchSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response("HTTP_400_BAD_REQUEST")

 
        flights = Flight.objects.filter(
            departure_airport__name=search_serializer.validated_data['departure_airport'],
            destination_airport__name=search_serializer.validated_data['destination_airport'],
            departure_datetime__date=search_serializer.validated_data['departure_datetime']
        )

 
        flight_serializer = FlightSerializer(flights, many=True)
        return Response(flight_serializer.data)
    

class BookingDetailsView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingDetailsSerializer

    def get_object(self):
        try:
            return Booking.objects.get(id=self.kwargs['booking_id'])
        except Booking.DoesNotExist:
            raise NotFound("Booking not found")

def my_view(request):
    return HttpResponse("Hello, world!")
