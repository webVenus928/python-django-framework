
from .models import Notification


def notifications(request):
    return {'notifications': Notification.objects.filter(user=request.user, dismissed=False)}

