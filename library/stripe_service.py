import stripe
from decouple import config

from library.models import Borrowing

stripe.api_key = config("STRIPE_SECRET_KEY")

def stripe_checkout_session(borrowing: Borrowing):

    days = (borrowing.expected_date - borrowing.borrow_date).days
    money_to_pay = days * borrowing.book.daily_fee
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(money_to_pay * 100),
                    "product_data": {"name": borrowing.book.title}
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/api/library/payments/success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/api/library/payments/cancel/",
    )
    return checkout_session