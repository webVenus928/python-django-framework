from ..models import Notification


def notify_saving_complete(saving):
    notification = Notification.objects.create(
        type='saving_complete',
        title='Saving Complete!',
        body='You completed your savings goal for {}'.format(saving.name),
        user=saving.user,
        alert='success'
    )
    notification.save()
