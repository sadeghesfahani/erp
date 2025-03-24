import json
import os

import requests
from django.http import JsonResponse, HttpResponseNotAllowed

TRYTON_URL = "http://localhost:8080"

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def tryton_login():
    """Authenticate with Tryton and return session ID (caching for efficiency)."""
    tryton_password = os.getenv("TRYTOND_DB_PASSWORD")
    url = f"{TRYTON_URL}/common"
    payload = {
        "method": "login",
        "params": ["tryton_db", "tryton_user", tryton_password]
    }
    response = requests.post(url, json=payload)


    return None  # Authentication failed
# Create your views here.
@csrf_exempt
def invoice_list_create(request):
    session_id = tryton_login()
    if not session_id:
        return JsonResponse({"error": "Authentication failed"}, status=403)

    if request.method == "GET":
        payload = {
            "method": "search_read",
            "params": [session_id, [], ["id", "party", "currency"]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice", json=payload)
        return JsonResponse(response.json().get("result", []), safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        payload = {
            "method": "create",
            "params": [session_id, [{
                "party": data.get("client_id"),
                "currency": data.get("currency", "EUR"),
                "lines": [
                    {
                        "product": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["price"]
                    }
                    for item in data.get("items", [])
                ]
            }]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice", json=payload)
        return JsonResponse(response.json(), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt
def invoice_detail_update_delete(request, pk):
    session_id = tryton_login()
    if not session_id:
        return JsonResponse({"error": "Authentication failed"}, status=403)

    if request.method == "GET":
        payload = {
            "method": "read",
            "params": [session_id, [pk], ["id", "party", "currency", "lines"]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice", json=payload)
        return JsonResponse(response.json().get("result", [{}])[0])

    elif request.method == "DELETE":
        payload = {
            "method": "delete",
            "params": [session_id, [pk]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice", json=payload)
        return JsonResponse({"message": "Deleted"})

    return HttpResponseNotAllowed(["GET", "DELETE"])

@csrf_exempt
def invoice_item_list_create(request):
    return JsonResponse({"error": "Invoice items should be created through invoice creation"}, status=400)

@csrf_exempt
def invoice_item_detail_update_delete(request, pk):
    session_id = tryton_login()
    if not session_id:
        return JsonResponse({"error": "Authentication failed"}, status=403)

    if request.method == "GET":
        payload = {
            "method": "read",
            "params": [session_id, [pk], ["product", "quantity", "unit_price"]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice.line", json=payload)
        return JsonResponse(response.json().get("result", [{}])[0])

    elif request.method == "DELETE":
        payload = {
            "method": "delete",
            "params": [session_id, [pk]]
        }
        response = requests.post(f"{TRYTON_URL}/model/account.invoice.line", json=payload)
        return JsonResponse({"message": "Deleted"})

    return HttpResponseNotAllowed(["GET", "DELETE"])
