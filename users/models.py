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