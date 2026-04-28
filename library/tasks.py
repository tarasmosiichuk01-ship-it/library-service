from datetime import date

from celery import shared_task

from library.models import Borrowing
from notifications_service.services import send_telegram_notification


@shared_task
def notify_new_borrowing(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = f"New borrowing: title: {borrowing.book.title}, borrow date: {borrowing.borrow_date}, expected date: {borrowing.expected_date}"
    send_telegram_notification(message)

@shared_task
def notify_overdue_borrowings():
    overdue_borrowings = Borrowing.objects.filter(
        expected_date__lt=date.today(),
        actual_return_date=None
    ).select_related("book", "user")

    if overdue_borrowings.exists():
        overdue_message = [f"Found {overdue_borrowings.count()} overdue borrowings:"]
        for borrowing in overdue_borrowings:
            overdue_message.append(
                f"Book: {borrowing.book.title}, "
                f"Expected date: {borrowing.expected_date}, "
                f"Days overdue: {(date.today() - borrowing.expected_date).days}, "
                f"User: {borrowing.user.email}"
            )
        send_telegram_notification("\n".join(overdue_message))

    else:
        message = "No overdue borrowings today!"
        send_telegram_notification(message)


@shared_task
def notify_successful_payment():
    pass
