import os
from dotenv import load_dotenv

import requests
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from invoice.views import TRYTON_URL
load_dotenv()

# Create your models here.
class TelegramUser(models.Model):
    """Stores Telegram user data independently from Aiogram"""
    telegram_id = models.BigIntegerField(unique=True)  # Unique Telegram user ID
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    default_language = models.CharField(max_length=20, blank=True, null=True)

    # Optional link to Django user (for authenticated users)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} (@{self.username}) - {self.telegram_id}"



def tryton_login():
    tryton_user = os.getenv("TRYTON_USER", "tryton_user")
    tryton_password = os.getenv("TRYTOND_DB_PASSWORD")
    tryton_db = os.getenv("TRYTON_DB", "tryton_db")
    # url = f"http://127.0.0.1:8081/common"
    url = f"http://127.0.0.1:8080"

    # payload = {
    #     "method": "login",
    #     "params": [tryton_db, tryton_user, tryton_password]
    # }

    url = f"{TRYTON_URL}/common/"
    payload = {
        "method": "login",
        "params": [tryton_db, "sina@omnitechs.nl", tryton_password]
    }
    headers = {
        "Content-Type": "application/json"
    }

    print("🔐 Tryton login payload:", payload)
    print("url:", url)
    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)

    print(response.__dict__)
    print("📡 Tryton raw response:", response.status_code, response.text)

    if response.status_code != 200:
        return None

    try:
        data = response.json()
        return data.get("result")
    except Exception as e:
        print("⚠️ JSON decode failed:", e)
        return None




def create_party_in_tryton(name: str):
    session_id = tryton_login()
    if not session_id:
        raise ValueError("Failed to authenticate with Tryton")

    payload = {
        "method": "create",
        "params": [session_id, [{"name": name}]]
    }
    response = requests.post(f"{TRYTON_URL}/model/party.party", json=payload)

    # Check if response is valid and contains JSON
    if response.status_code != 200:
        raise ConnectionError(f"Failed to create party in Tryton: {response.status_code} - {response.text}")
    try:
        json_response = response.json()  # Safely parse JSON
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Tryton did not return valid JSON: {response.text}")

    # Safeguard against missing "result" in response
    return json_response.get("result", [None])[0]


@receiver(post_save, sender=TelegramUser)
def create_tryton_client(sender, instance, created, **kwargs):
    if instance.client_id is None:
        print("attempt to get client ID")
        try:
            party_id = create_party_in_tryton(instance.telegram_id)
            instance.client_id = party_id
            instance.save()
        except Exception as e:
            print(f"Failed to create party in Tryton: {e}")

