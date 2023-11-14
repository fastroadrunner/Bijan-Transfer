
import json
from datetime import datetime
from urllib.parse import quote_plus, urlencode

import jwt
import requests
from authlib.integrations.django_client import OAuth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from jwt.exceptions import ExpiredSignatureError
from utilities.currency import convert_currency
# from authlib.integrations.django_oauth2 import requests
from . import settings
from users.models import  TransactionRequests
from decimal import Decimal

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )
    
def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    #print("Token:", token)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
    



# Existing index view
def index(request):
    if request.user.is_authenticated:
        # Redirect to dashboard view if the user is already logged in
        return redirect('dashboard')
    else:
        # Existing logic for rendering login page
        return render(
            request,
            "login.html",
            context={
                "session": request.session.get("user"),
                # Remove or comment out "pretty" if not needed
                "pretty": json.dumps(request.session.get("user"), indent=4),
            },
        )


@login_required
def dashboard(request):
    user_ip = get_client_ip(request)

    try:
        # Use the IP address to get location data from ipinfo.io
        response = requests.get(f'https://ipinfo.io/{user_ip}/json?token=8f9ed60662dc05')
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API request
        print(e)
        location_data = {}  # Set location data to empty if there was an error
    else:
        # Parse the location data if the request was successful
        location_data = response.json()
        if location_data["ip"] == '127.0.0.1':
            location_data = "Orlando, FL"



    try:
        converted_amount,timestamp = convert_currency(1.00, 'USD', 'IRR')
        conversion_rate = Decimal(converted_amount)
        # Convert Unix timestamp to a human-readable string
        human_readable_timestamp = datetime.utcfromtimestamp(timestamp).strftime('%B %d, %Y\n%H:%M:%S GMT')

        user_info = request.session.get("user")
        username = None


        if user_info:
            # Decode the token to get user details
            try:
                decoded = jwt.decode(
                    user_info['id_token'],
                    options={"verify_signature": False},
                    audience=settings.AUTH0_CLIENT_ID
                )
                username = decoded.get('name') or decoded.get('nickname')
            except (jwt.DecodeError, jwt.InvalidAudienceError) as e:
                print("JWT Decode Failed:", e)
                return redirect('login')  # Updated here
            except ExpiredSignatureError:
                # If the token is expired, redirect to the login page
                return redirect('login')  # Updated here

        if not username:
            username = 'unknown user'

        # Filter transactions for Zelle and PayPal
        zelle_transactions = TransactionRequests.objects.filter(foreign_deposit_account_provider='ZELLE')
        paypal_transactions = TransactionRequests.objects.filter(foreign_deposit_account_provider='PAYPAL')

        # Convert amounts from RIAL to USD
        for transaction in zelle_transactions:
            print(transaction.created_at)
            transaction.converted_amount = (transaction.amount / conversion_rate).quantize(Decimal('0.01'))

        for transaction in paypal_transactions:
            transaction.converted_amount = (transaction.amount / conversion_rate).quantize(Decimal('0.01'))


        context = {
            'username': username,
            'logout_url': reverse('logout'),
            'location' : location_data,
            'conversion' : converted_amount,
            'timestamp'  : human_readable_timestamp,
            'zelle_transactions': zelle_transactions,
            'paypal_transactions' : paypal_transactions
        }


        return render(request, 'dashboard.html', context)
            # You can now pass the location data to your template
        #return render(request, 'dashboard.html', {'location': location_data})
    except ExpiredSignatureError:
        return redirect('login')  # Updated here
def get_client_ip(request):
    """Get the client IP address from the request object"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
