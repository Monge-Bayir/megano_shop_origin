from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from shopapp.models import Basket, BasketItems

@receiver(user_logged_in)
def merge_guest_basket(sender, request, user, **kwargs):
    session_id = request.session.get('basket_id')
    if not session_id:
        return

    try:
        guest_basket = Basket.objects.get(session_id=session_id)
    except Basket.DoesNotExist:
        return

    user_basket, _ = Basket.objects.get_or_create(user=user)

    for item in BasketItems.objects.filter(basket=guest_basket):
        user_item, created = BasketItems.objects.get_or_create(
            basket=user_basket,
            product=item.product,
            defaults={'quantity': item.quantity}
        )
        if not created:
            user_item.quantity += item.quantity
            user_item.save()

    guest_basket.delete()
    del request.session['basket_id']