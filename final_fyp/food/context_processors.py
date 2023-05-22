from food.models import CustomUser, MenuItems, OrderItems, Basket, Notification

def orders(request):
    try:
        cust = CustomUser.objects.get(email=request.user)
        basket = Basket.objects.filter(customer_id = cust, status = 'Created').first()
        price = 0
        for items in OrderItems.objects.filter(basket_id=basket):
            price += items.price
        return {
            'orders':OrderItems.objects.filter(basket_id=basket),
            'total':price,
            'count':OrderItems.objects.filter(basket_id=basket).count()
        }
    except:
        return {}

def notifications(request):
    allnotifications = Notification.objects.all()
    return {'notification':allnotifications}

def top_food(request):
    top_ordered_food = OrderItems.objects.values('menu_id__item_name', 'menu_id__image', 'menu_id__description', 'menu_id__price').annotate(total_ordered=Sum('quantity')).order_by('-total_ordered')[:3]
    import os
    from django.conf import settings

    # assume that the string is "/media/my_image.png"
    for i in top_ordered_food:
        print(i['menu_id__image'])
        image_url = os.path.join(settings.MEDIA_URL, i['menu_id__image'])
        print(image_url)
        i['menu_id__image'] = image_url
        menu_item = MenuItems.objects.get(item_name=i['menu_id__item_name'])
        menu_item.is_top_ordered = True
        menu_item.save()

        new_items = MenuItems.objects.order_by('-creation_date')[:2]

        for item in new_items:
            item.is_new_item = True
            item.save()
        MenuItems.objects.exclude(pk__in=[item.pk for item in new_items]).update(is_new_item=False)
        context = {
            'newitems': new_items,
            'menu': MenuItems.objects.all(),
            'top_ordered_food':top_ordered_food
        }
    return context








