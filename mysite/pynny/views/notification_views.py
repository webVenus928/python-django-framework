from django.http import HttpResponse

from ..models import Notification


def dismiss_notice(request):
    """REST view for notifications"""
    if request.method == 'POST':
        notification_id = int(request.POST['id'])
        if request.POST.get('action', '').lower() == 'dismiss':
            try:
                notice = Notification.objects.get(id=notification_id)
                notice.dismissed = True
                notice.save()
            except Notification.DoesNotExist:
                pass

    return HttpResponse()
