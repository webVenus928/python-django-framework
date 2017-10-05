
from .models import Notification


def notifications(request):
    if request.user.is_authenticated():
        return {'notifications': Notification.objects.filter(user=request.user, dismissed=False)}
    return {}

