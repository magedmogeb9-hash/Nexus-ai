from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Payment, User
from datetime import datetime, timedelta
import os, uuid, stripe, paypalrestsdk

payments_bp = Blueprint('payments', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.getenv('PAYPAL_CLIENT_ID'),
    "client_secret": os.getenv('PAYPAL_CLIENT_SECRET')
})

PLANS = {
    'pro': {'amount': 49, 'currency': 'USD', 'interval': 'month'},
    'enterprise': {'amount': 199, 'currency': 'USD', 'interval': 'month'}
}

@payments_bp.route('/payments')
@login_required
def payment_page():
    return render_template('payments.html', plans=PLANS)

@payments_bp.route('/create-payment', methods=['POST'])
@login_required
def create_payment():
    plan = request.form.get('plan')
    method = request.form.get('method')

    if plan not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400

    amount = PLANS[plan]['amount']
    currency = PLANS[plan]['currency']

    payment = Payment(
        user_id=current_user.id,
        amount=amount,
        currency=currency,
        method=method,
        reference=str(uuid.uuid4()),
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()

    if method == 'stripe':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {'name': f'AIForge {plan} Plan'},
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('payments.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('payments.payment_cancel', _external=True),
                metadata={'payment_id': str(payment.id)}
            )
            return redirect(checkout_session.url, 303)
        except Exception as e:
            flash(f'Stripe error: {str(e)}', 'danger')
            return redirect(url_for('payments.payment_page'))

    elif method == 'paypal':
        payment_paypal = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": url_for('payments.payment_success', _external=True),
                "cancel_url": url_for('payments.payment_cancel', _external=True)
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"AIForge {plan} Plan",
                        "sku": plan,
                        "price": str(amount),
                        "currency": currency,
                        "quantity": 1
                    }]
                },
                "amount": {"total": str(amount), "currency": currency},
                "description": f"AIForge {plan} Subscription"
            }]
        })
        if payment_paypal.create():
            for link in payment_paypal.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            flash('PayPal error', 'danger')
            return redirect(url_for('payments.payment_page'))

    elif method == 'paddle':
        flash('Paddle integration coming soon', 'info')
        return redirect(url_for('payments.payment_page'))

    else:
        flash('Payment method not supported', 'danger')
        return redirect(url_for('payments.payment_page'))

@payments_bp.route('/payment-success')
def payment_success():
    flash('Payment successful! Your subscription is activated.', 'success')
    return redirect(url_for('dashboard'))

@payments_bp.route('/payment-cancel')
def payment_cancel():
    flash('Payment cancelled', 'warning')
    return redirect(url_for('payments.payment_page'))

@payments_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET'))
    except:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_id = session.get('metadata', {}).get('payment_id')
        if payment_id:
            payment = Payment.query.get(int(payment_id))
            if payment:
                payment.status = 'completed'
                db.session.commit()
    return 'OK', 200
