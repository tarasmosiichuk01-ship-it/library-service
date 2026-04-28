from celery import shared_task

from library.models import Borrowing
from notifications_service.services import send_telegram_notification


@shared_task
def notify_new_borrowing(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = f"New borrowing: title: {borrowing.book.title}, borrow date: {borrowing.borrow_date}, expected date: {borrowing.expected_date}"
    send_telegram_notification(message)



