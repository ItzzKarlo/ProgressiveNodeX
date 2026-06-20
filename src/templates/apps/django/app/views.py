from django.http import JsonResponse


def home(_request):
    return JsonResponse({
        "name": "django",
        "status": "ok",
        "generated_by": "ProgressiveNodeX",
    })