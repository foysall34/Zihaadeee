import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.utils import timezone

from .models import (
    CelebrityProfile, CelebrityFollow,
    PaidChatAccess, Message
)

stripe.api_key = settings.STRIPE_SECRET_KEY


# -------- A) Celebrity Upgrade ($25) -------------

class CelebrityUpgradePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = 25.00
        user = request.user

        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Celebrity Upgrade"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            metadata={"type": "celebrity_upgrade", "user_id": user.id},
            customer_email=user.email,
            success_url="https://yourdomained.com/success",
            cancel_url="https://yourdomain.com/cancel",
        )

        return Response({"checkout_url": checkout.url})





import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import CelebrityProfile, PaidChatAccess

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
print(endpoint_secret)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # 1) PAYMENT SUCCESS
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            payment_type = session["metadata"].get("type")

            # A) Celebrity Upgrade ($25)
            if payment_type == "celebrity_upgrade":
                user_id = session["metadata"]["user_id"]
                profile, created = CelebrityProfile.objects.get_or_create(user_id=user_id)
                profile.is_celebrity = True
                profile.is_paid_celeb = True
                profile.save()

            # B) 10-minute Chat ($4.99)
            if payment_type == "chat_access":
                user_id = session["metadata"]["user_id"]
                celeb_id = session["metadata"]["celebrity_id"]

                access = PaidChatAccess.objects.get(
                    user_id=user_id,
                    celebrity_id=celeb_id,
                    stripe_payment_intent=session["id"]
                )
                access.is_active = True
                access.expiry_time = timezone.now() + timezone.timedelta(minutes=10)
                access.save()

        return Response({"status": "success"}, status=200)







# -------- B) Auto-Celebrity: Follower reaches 100,000 -------------

class FollowCelebrity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        celeb_id = request.data.get("celebrity_id")
        celeb = get_object_or_404(CelebrityProfile, id=celeb_id)

        CelebrityFollow.objects.get_or_create(
            follower=request.user,
            celebrity=celeb
        )

        celeb.followers_count += 1
        celeb.save()

        # auto upgrade
        if celeb.followers_count >= 100000:
            celeb.is_celebrity = True
            celeb.is_follower_celeb = True
            celeb.save()

        return Response({"detail": "Followed successfully"})


# -------- C) $4.99 — 10-minute chat unlock -------------

class ChatAccessPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        celeb_id = request.data.get("celebrity_id")
        user = request.user
        celeb = get_object_or_404(CelebrityProfile, id=celeb_id)

        amount = 4.99

        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "10-Min Chat Access"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            metadata={
                "type": "chat_access",
                "user_id": user.id,
                "celebrity_id": celeb.id
            },
            customer_email=user.email,
            success_url="https://yourdomain.com/chat-success",
            cancel_url="https://yourdomain.com/cancel",
        )

        PaidChatAccess.objects.update_or_create(
            user=user,
            celebrity=celeb,
            defaults={
                "stripe_payment_intent": checkout.id,
                "is_active": False
            }
        )

        return Response({"checkout_url": checkout.url})


# -------- D) Send Message (only if chat unlocked & active) -------------

class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        celeb_id = request.data.get("celebrity_id")
        text = request.data.get("text")

        celeb = get_object_or_404(CelebrityProfile, id=celeb_id)
        sender = request.user

        # ----------------------------------
        # CASE 1: User sending TO celebrity
        # ----------------------------------
        if sender != celeb.user:

            # 50-message limit check (only user)
            user_sent_count = Message.objects.filter(
                sender=sender,
                celebrity=celeb
            ).count()

            if user_sent_count >= 50:
                return Response({
                    "detail": "Message limit reached. You have used your 50 messages."
                }, status=403)

            # Check paid chat access
            access = PaidChatAccess.objects.filter(
                user=sender,
                celebrity=celeb,
                is_active=True
            ).first()

            if not access:
                return Response({"detail": "Please pay $4.99 for chat access"}, status=403)

            # Time expiry check
            if access.expiry_time and access.expiry_time < timezone.now():
                access.is_active = False
                access.save()
                return Response({"detail": "Your 10-min chat expired"}, status=403)

        # ----------------------------------
        # CASE 2: Celebrity replying to user
        # ----------------------------------
        # Celebrity = celeb.user
        # No limit, no payment needed, no expiry

        msg = Message.objects.create(
            sender=sender,
            celebrity=celeb,
            text=text
        )

        return Response(MessageSerializer(msg).data)



class CreateDonationPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return Response({"detail": "Amount is required"}, status=400)

        amount = float(amount)
        stripe_amount = int(amount * 100)

        user = request.user

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "User Donation",
                        },
                        "unit_amount": stripe_amount,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "type": "donation",
                "user_id": user.id
            },

     
            customer_email=user.email,

            success_url="https://yourdomain.com/payment/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourdomain.com/payment/cancel/",
        )

        Donation.objects.create(
            user=user,
            amount=amount,
            stripe_payment_intent=checkout_session.id,
            payment_status="pending"
        )

        return Response({
            "checkout_url": checkout_session.url
        })










