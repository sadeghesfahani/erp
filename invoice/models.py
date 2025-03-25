import hashlib
import json
from datetime import datetime
from decimal import Decimal
from threading import Thread

import googlemaps
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ai.services import AI
from .date import parse_date

class Office(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    @property
    def address(self):
        return f"{self.street} {self.house_number}, {self.zip}, {self.city}, {self.country}"

class AddressAlias(models.Model):
    # this is used for the offices that the site you work is not the same as the address of the company
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    alias_street = models.CharField(max_length=100, blank=True, null=True)
    alias_city = models.CharField(max_length=100, blank=True, null=True)
    alias_zip = models.CharField(max_length=100, blank=True, null=True)
    alias_house_number = models.CharField(max_length=100, blank=True, null=True)
    alias_country = models.CharField(max_length=100, blank=True, null=True)


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    client = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='invoices/', blank=True, null=True)
    hash = models.CharField(max_length=255, blank=True, null=True)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    is_processed = models.BooleanField(default=False)
    vector_store_id = models.CharField(max_length=255, blank=True, null=True)
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    btw21 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw9 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw0 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw21_deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw9_deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw0_deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    client_street = models.CharField(max_length=100, blank=True, null=True)
    client_city = models.CharField(max_length=100, blank=True, null=True)
    client_zip = models.CharField(max_length=100, blank=True, null=True)
    client_house_number = models.CharField(max_length=100, blank=True, null=True)
    client_country = models.CharField(max_length=100, blank=True, null=True)
    open_ai_response = models.JSONField(blank=True, null=True)
    transportation_type = models.CharField(max_length=100, blank=True, null=True) # e.g., "Car", "Train", "Bus"
    direct_transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distance_to_office = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculate hash if the file is present
        if self.file:
            self.hash = self.calculate_hash(self.file)

        if self.client_street and self.client_city and self.client_zip:
            client_address = f"{self.client_street} {self.client_house_number}, {self.client_zip}, {self.client_city}, {self.client_country}"
            office = Office.objects.filter(name="self").first()
            if office:
                self.distance_to_office = Decimal(calculate_distance_for_invoice(self, office).split(" ")[0])
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_hash(file):
        md5_hash = hashlib.md5()
        for chunk in file.chunks():
            md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def __str__(self):
        return self.invoice_number or "Unprocessed Invoice"


def calculate_distance_for_invoice(instance : Invoice, office : Office):
    """
    Calculate the distance between the client address in the invoice and the office address.
    """
    if instance.client_street and instance.client_city and instance.client_zip and instance.client_country:
        alias = AddressAlias.objects.filter(street=instance.client_street, city=instance.client_city, zip=instance.client_zip, country=instance.client_country).first()
        if alias:
            client_address = f"{alias.alias_street} {alias.alias_house_number}, {alias.alias_zip}, {alias.alias_city}, {alias.alias_country}"
        else:
            client_address = f"{instance.client_street} {instance.client_house_number}, {instance.client_zip}, {instance.client_city}, {instance.client_country}"
        office_address = office.address
        return calculate_distance(client_address, office_address)
    return "Could not calculate distance. Please check the invoice client address."

def calculate_distance(address1, address2):
    # Replace 'YOUR_API_KEY' with your actual Google Maps API Key
    gmaps = googlemaps.Client(key="AIzaSyDhPO3ZoflzQSACroHWFDtMEDJ_-EvfLEA")

    # Use the Distance Matrix API to calculate the distance

    result = gmaps.distance_matrix(origins=address1,
                                   destinations=address2,
                                   mode='driving')  # Can also be 'walking', 'bicycling', 'transit'

    try:
        distance = result['rows'][0]['elements'][0]['distance']['text']
        duration = result['rows'][0]['elements'][0]['duration']['text']
        print(f"Distance: {distance}, Duration: {duration}")
        return distance
    except KeyError:
        return "Could not calculate distance. Please check the addresses or API configuration."

calculate_distance("Hengelosestraat 51, 7604TN Almelo, Netherlands", "resedastraat 39, 9713TN Groningen, Netherlands")


def process_invoice(instance : Invoice):
    """
    Function to handle file upload and vector store creation.
    This is executed in a separate thread for asynchronous behavior.
    """
    if instance.file and not instance.is_processed:
        ai = AI()
        [instance.vector_store_id, instance.file_id] = ai.add_file(instance.file.file,instance.file.file.open('rb').read())
        instance.thread_id = ai.create_thread()
        schema = {
  "invoice_number": "Y95960124009",
  "invoice_date": "31-01-2022",
  "due_date": "31-01-2022",
  "amount": 64.0,
  "client": "Asito B.V.",
  "status": "Pending",
  "btw21": 13.44,
    "btw9": 0,
    "btw0": 0,
            "deduction":2.25,
            "btw21_deduction": 0.47,
            "btw9_deduction": 0,
            "btw0_deduction": 0,
            "total": 74.72,
            "client_street": "Hengelosestraat",
            "client_city": "Almelo",
            "client_zip": "7604TN",
            "client_house_number": "51",
            "client_country": "Netherlands"

}
        ai.add_message_to_thread(instance.thread_id, "Hi, would you please tell me the BTW and total value to be paid?, this json format should be response: \n" + str(schema))
        # print("here")
        run = ai.run(instance.thread_id, additional_instructions="do you have access to the file of invoice? if yes, what do you see? if not what is the profblem you think")
        # print(run)
        json_respond = ai.process_ai_response(run)
        # print(json_respond)
        data = json.loads(json_respond)
        # print(data)
        instance.open_ai_response = data
        instance.save()
        invoice_date_str = data.get("invoice_date", None)
        due_date_str = data.get("due_date", None)
        # Safely assign invoice fields
        instance.invoice_number = data.get("invoice_number", "")
        print(f"invoice with number of {instance.invoice_number} is created")
        if invoice_date_str:
            date = parse_date(invoice_date_str)
            instance.invoice_date = date
        if due_date_str:
            date = parse_date(due_date_str)
            instance.due_date = date
        instance.amount = data.get("amount", None)
        instance.client = data.get("client", "")
        instance.btw21 = data.get("btw21", None)
        instance.btw9 = data.get("btw9", None)
        instance.btw0 = data.get("btw0", None)
        instance.deduction = data.get("deduction", None)
        instance.btw21_deduction = data.get("btw21_deduction", None)
        instance.btw9_deduction = data.get("btw9_deduction", None)
        instance.btw0_deduction = data.get("btw0_deduction", None)
        instance.total = data.get("total", None)
        instance.client_street = data.get("client_street", "")
        instance.client_city = data.get("client_city", "")
        instance.client_zip = data.get("client_zip", "")
        instance.client_house_number = data.get("client_house_number", "")
        instance.client_country = data.get("client_country", "")


        # Mark as processed
        instance.is_processed = True
        # print(instance.__dict__)
        instance.save()
        # print(instance.__dict__)

@receiver(post_save, sender=Invoice)
def post_save_invoice(sender, instance, created, **kwargs):
    """
    Signal to handle processing of an invoice after it is saved.
    """
    if created:  # Only process new invoices
        Thread(target=process_invoice, args=(instance,)).start()



class Tax(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="taxes")
    name = models.CharField(max_length=100)  # e.g., "VAT", "Service Tax"
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Manually entered tax amount

    def __str__(self):
        return f"{self.name} (+{self.amount})"

# Deduction model
class Deduction(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="deductions")
    name = models.CharField(max_length=100)  # e.g., "Discount", "Rebate"
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed deduction amount

    def __str__(self):
        return f"{self.name} (-{self.amount})"




class Cost(models.Model):
    file = models.FileField(upload_to='costs/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed cost amount
    extra_information = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateField(blank=True, null=True)
    hash = models.CharField(max_length=255, blank=True, null=True)


    def save(self, *args, **kwargs):
        # Calculate hash if the file is present
        if self.file:
            self.hash = self.calculate_hash(self.file)
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_hash(file):
        md5_hash = hashlib.md5()
        for chunk in file.chunks():
            md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def __str__(self):
        return f"{self.name} (+{self.amount})"