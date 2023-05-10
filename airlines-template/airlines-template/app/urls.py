from django.contrib import admin
from django.urls import path
from .view import my_view, FlightDetailView, FlightSearchView, BookingDetailsView \
    , PaymentProviderView, PayBookingView, BookFlightView, ConfirmBookingView, UpdateBookingView, CancelBookingView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('my-endpoint/', my_view, name='my_view'),
    path('api/flight/<int:flight_id>/', FlightDetailView.as_view(), name='flight_detail'),
    path('api/flights', FlightSearchView.as_view(), name='flight_search'),
    path('api/booking/<str:booking_id>/', BookingDetailsView.as_view(), name='booking_details'),
    path('api/paymentproviders/', PaymentProviderView.as_view(), name='payment_providers'),
    path('api/paybooking/<str:booking_id>', PayBookingView.as_view(), name='pay_booking'),
    path('api/book', BookFlightView.as_view(), name='book_flight'),
    path('api/confirmbooking', ConfirmBookingView.as_view(), name='confirm_booking'),
    path('api/booking/<str:booking_id>', UpdateBookingView.as_view(), name='update_biooking'),
    path('api/cancelbooking', CancelBookingView.as_view(), name='cancel_biooking'),

]
