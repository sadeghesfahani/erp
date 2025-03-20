from django.http import JsonResponse
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

        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)

        user, created = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={"username": username, "first_name": first_name, "last_name": last_name},
        )

        return JsonResponse({"message": "User saved", "created": created})

    return JsonResponse({"error": "Invalid request"}, status=400)