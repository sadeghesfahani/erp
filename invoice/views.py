import json
import os

import requests
from django.http import JsonResponse

TRYTON_URL = "http://192.168.178.31:8080"

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def tryton_login():
    """Authenticate with Tryton and return session ID (caching for efficiency)."""
    global session_id_cache
    if session_id_cache:
        return session_id_cache  # Use cached session
    tryton_password = os.getenv("TRYTOND_DB_PASSWORD")
    url = f"{TRYTON_URL}/common"
    payload = {
        "method": "login",
        "params": ["tryton_db", "tryton_user", tryton_password]
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        session_id_cache = response.json().get("result")
        return session_id_cache
    return None  # Authentication failed
# Create your views here.
@csrf_exempt
def create_invoice(request):
    """Create an invoice in Tryton from Django API"""
    if request.method == "POST":
        data = json.loads(request.body)

        # Get invoice data from request
        client_id = data.get("client_id")
        items = data.get("items")  # List of items [{product_id, quantity, price}]
        currency = data.get("currency", "EUR")  # Default to EUR


        url = f"http://192.168.178.31:8080/model/account.invoice"

        # Get Session ID
        session_id = tryton_login()
        if not session_id:
            return JsonResponse({"error": "Authentication failed"}, status=403)

        payload = {
            "method": "create",
            "params": [session_id, [{
                "party": client_id,
                "lines": [
                    {
                        "product": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["price"],
                    }
                    for item in items
                ],
                "currency": currency,
            }]]
        }

        response = requests.post(url, json=payload)
        return JsonResponse(response.json())

    return JsonResponse({"error": "Invalid request"}, status=400)