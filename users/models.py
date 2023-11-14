from django.db import models


# Create your models here.
class User(models.Model):
    firstName = models.CharField(max_length=65)
    lastName = models.CharField(max_length=65)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    emailAddress = models.EmailField()
    phoneNumber = models.CharField(max_length=10)
    countryCode = models.CharField(max_length=2)
    
    def __str__(self):
        return self.firstName + " " + self.lastName
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transactionId = models.AutoField(auto_created=True, primary_key=True)
    sender = User()
    receiver = User()
    timestamp = models.DateField(auto_now=True)
    amountInUSD = models.FloatField()
    amountInIRR = models.FloatField()
    def __str__(self):
        return self.transactionId
class Users(models.Model):
    userid = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=20)
    county = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    screen_name = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    fiatcode = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"



class TransactionRequests(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # Reference to Users table
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fiatcode = models.CharField(max_length=3)  # Renamed from currency_code
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    foreign_deposit_account_number = models.CharField(max_length=50)
    foreign_deposit_account_provider = models.CharField(max_length=50)

    def __str__(self):
        return f"Transaction Requests by {self.user.screen_name} in {self.fiatcode}"


class Transactions(models.Model):
    timestamp_transaction_created = models.DateTimeField(auto_now_add=True)
    timestamp_transaction_updated = models.DateTimeField(auto_now=True)
    transaction_status = models.CharField(max_length=20)
    transaction_request_1 = models.ForeignKey(
        TransactionRequests,
        on_delete=models.CASCADE,
        related_name='transactions_as_request_1'
    )
    transaction_request_2 = models.ForeignKey(
        TransactionRequests,
        on_delete=models.CASCADE,
        related_name='transactions_as_request_2'
    )

    def __str__(self):
        return f"Transactions {self.id} between request {self.transaction_request_1.id} and {self.transaction_request_2.id}"
