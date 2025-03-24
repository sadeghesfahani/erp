from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TelegramUser

@csrf_exempt  # Disable CSRF protection for simplicity
def save_telegram_user(request):
    """Receives Telegram user data from the Aiogram script and saves it"""
    if request.method == "POST":
        data = json.loads(request.body)
        telegram_id = data.get("telegram_id")
        username = data.get("username", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        default_language = data.get("default_language", "")
        client_id = data.get("client_id", None)


        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)

        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        print("User is: ",user)
        if user:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.default_language = default_language
            user.client_id = client_id
            user.save()
            return JsonResponse({"message": "User updated"})
        else:
            TelegramUser(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                default_language=default_language,
                client_id=client_id,).save()
            return JsonResponse({"message": "User saved"})


    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def get_telegram_user(request, telegram_id):
    """Retrieve a Telegram user's data from Django"""
    print(telegram_id)
    user = get_object_or_404(TelegramUser, telegram_id=telegram_id)

    data = {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "client_id": user.client_id,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return JsonResponse(data)