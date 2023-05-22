from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from food.models import CustomUser, MenuItems, OrderItems, Basket, Notification, Feedback
from food.forms import CustomerForm
from django.conf import settings
import random
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
from django.contrib.auth import authenticate,login,logout
from bson import ObjectId
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import cv2
from django.core.files.storage import FileSystemStorage
import os
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import  json
from django.db.models import Count, F, Sum
from asgiref.sync import async_to_sync
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        if request.user.role != 'owner':
            return redirect(f'/dashboard/{request.user.id}/')
    return render(request, 'food-ordering/index.html')

def search_menu(request, object_id):
    context = {}
    if request.method == 'POST':
        search_item = request.POST.get('name')
        if MenuItems.objects.filter(item_name__icontains = search_item, is_seen=True).exists():
            search = MenuItems.objects.filter(item_name__icontains = search_item, is_seen=True)
            context['data'] = search
        else:
            messages.error(request, "The searched item does not exist.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'search_menu.html', context)

def sign_up(request):
    if request.method == "POST":
        # form = CustomerForm(request.POST)
        first_name = request.POST['Firstname']
        last_name = request.POST['Lastname']
        email = request.POST['email']
        contact_number = request.POST['contact']
        password = request.POST['password']
        confirm = request.POST['confirmPassword']
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,"Email already exists. Enter another email.")
        ### OTP verification ###
        else:
            try:
                current_site = get_current_site(request)
                subject = 'Food ordering system'
                otp = random.randint(100000, 999999)
                        # email_from = settings.EMAIL_HOST_USER

                message2 = f"Your otp is {otp}. Use it for verification in {current_site.domain}"
                        # First send OTP through email before saving data to Database

                send_mail(
                            subject,
                            message2,
                            settings.EMAIL_HOST_USER,
                            [email],
                            fail_silently = True

                )

                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                request.session['email'] = email
                request.session['password1'] = password
                request.session['password2'] = confirm
                request.session['contact'] = contact_number
                request.session['otp'] = str(otp)
                messages.success(request, "OTP has been sent to your mail for verification")
                return redirect('otp')

            except Exception as e:
                        messages.error(request,
                            "Failed to send OTP through Email."+str(e))

    return render(request, 'signup.html')

def verifyotp(request):
    first_name = request.session['first_name']
    last_name = request.session['last_name']
    email = request.session['email']
    password = request.session['password1']
    contact_number = request.session['contact']
    if request.method == 'POST':
        d = request.POST
        for k,v in d.items():
            if k == 'resend':
                try:
                    current_site = get_current_site(request)
                    subject = 'Food ordering system'
                    otp = random.randint(100000, 999999)
                            # email_from = settings.EMAIL_HOST_USER

                    message2 = f"Your otp is {otp}."
                            # First send OTP through email before saving data to Database

                    send_mail(
                                subject,
                                message2,
                                settings.EMAIL_HOST_USER,
                                [email],
                                fail_silently = True

                    )
                    request.session['otp'] = str(otp)
                except Exception as e:
                            messages.error(request,
                                "Failed to send OTP through Email."+str(e))

            if k == 'submit':
                myotp = request.POST.get('otp')
                otp = request.session['otp']

                if str(myotp) == otp:
                    messages.success(
                        request, "OTP verification successful. You may now login to use our services.")

                    CustomUser.objects.create_user(
                        email = email,
                        first_name =first_name,
                        last_name = last_name,
                        password = password,
                        contact_number = contact_number
                    )
                    return redirect('signin')
                else:
                    messages.error(request, 'OTP is incorrect, please try again')
    return render(request, 'otp.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        myuser = authenticate(request, username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            if CustomUser.objects.filter(email = myuser.email).first():
                user = CustomUser.objects.get(email = myuser.email)
                if user.role == 'owner':
                    messages.success(request, "Successfully logged in")
                    return redirect('owner')
                else:
                    messages.success(request, "Successfully logged in")
                    return redirect(f'/dashboard/{user.pk}')
            else:
                messages.error(request, "Email provided is not valid.")
        else:
            messages.error(request,"Incorrect Email or Password")
            return redirect('signin')
    return render(request, 'signin.html')
@login_required
def owner_dashboard(request):
    from django.db.models import Sum, Q, Count
    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    sales = OrderItems.objects.aggregate(total=Sum('quantity'))['total']
    revenue = Basket.objects.aggregate(total=Sum('bill'))['total']
    customers = CustomUser.objects.exclude(Q(role='manager') | Q(role='owner')).count()
    cancel = Basket.objects.filter(status = 'Cancel').count()
    top_selling = []
    month_list = []
    orders_in_month = []

    import datetime
    import calendar

    for i in Basket.objects.all():
        if i.order_date != None:
            dt = datetime.datetime(i.order_date.year,i.order_date.month,i.order_date.day,i.order_date.hour,i.order_date.minute,i.order_date.second,i.order_date.microsecond)
            month = dt.month
            num = 0
            if calendar.month_name[month] not in month_list:
                month_list.append(calendar.month_name[month])
                num = Basket.objects.filter(month = month).count()
                orders_in_month.append(num)

    for items in MenuItems.objects.all():
        item = OrderItems.objects.filter(item_name = items.item_name).aggregate(total=Sum('quantity'))['total']
        price = OrderItems.objects.filter(item_name = items.item_name).aggregate(total=Sum('price'))['total']
        top_selling.append({'item_name': items.item_name, 'quantity': item, 'price': price, 'image':items.image})
    print(top_selling)
    # order_counts = Basket.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(count=Count('id')).order_by('month')

    context = {
        'sales':sales,
        'revenue':revenue,
        'customers':customers,
        'cancel':cancel,
        'feedback':Feedback.objects.order_by('-id'),
        'top_selling':top_selling,
        'baskets':Basket.objects.all(),
        'months':month_list,
        'orders_in_month':orders_in_month
    }

    return render(request, 'owner_final/owner_dashboard.html', context)

@login_required
def owner_add_manager(request):
    data = ''
    if CustomUser.objects.filter(role='manager').first():
        data = CustomUser.objects.get(role='manager')
    if request.method == 'POST':
        d = request.POST
        for k,v in d.items():
            if k == 'edit':
                manager = CustomUser.objects.get(role = 'manager')
                first_name =request.POST['first_name'] if request.POST['first_name'] else  manager.first_name
                last_name = request.POST['last_name'] if request.POST['last_name'] else manager.last_name
                email = request.POST['email'] if request.POST['email'] else manager.email
                contact = request.POST['contact'] if request.POST['contact'] else manager.contact_number
                manager.first_name = first_name
                manager.last_name = last_name
                manager.email = email
                manager.contact_number = contact
                manager.save()
                messages.success(request, "Manager successfully Updated.")
                return redirect('addmanager')

            if k == 'add':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                email = request.POST['email']
                contact = request.POST['contact']
                password = request.POST['password']
                if CustomUser.objects.filter(role = 'manager').first():
                    messages.error(request, "Manager already exists in the system.")
                else:
                    CustomUser.objects.create_user(
                        first_name = first_name,
                        last_name = last_name,
                        email = email,
                        contact_number = contact,
                        password = password,
                        role = 'manager'
                    )
                    messages.success(request, "Manager successfully Added.")
                    return redirect('addmanager')
    context = {
        'data':data
    }
    return render(request, 'owner_final/add_manager.html', context)

@login_required
def delete_manager(request):
    CustomUser.objects.filter(role = 'manager').delete()
    messages.success(request, "Manager successfully deleted.")
    return redirect('addmanager')

@login_required
def owner_profile(request):
    profile = CustomUser.objects.get(email = request.user)
    if request.method == 'POST':
        profile.image =  request.FILES['image'] if 'image' in request.FILES else profile.image
        profile.first_name = request.POST['first_name'] if request.POST['first_name'] != "" else profile.first_name
        profile.last_name = request.POST['last_name'] if request.POST['last_name'] != "" else profile.last_name
        profile.email = request.POST['email'] if request.POST['email'] != "" else profile.email
        profile.contact_number = request.POST['contact'] if request.POST['contact'] != "" else profile.contact_number
        profile.save()
        messages.success(request, 'Your profile has been updated.')
    return render(request, 'owner_final/owner_profile.html')

@login_required
def owner_change_password(request):
    if request.method == 'POST':
        if profile.password == request.POST['current_password']:
            profile.password = request.POST['password']
            profile.save()
            messages.success(request, 'Your profile has been updated.')
        else:
            messages.error(request, 'Your current password does not match with any.')

    return render(request, 'owner_final/change_password.html')

@login_required
def dashboard(request,object_id):
    top_ordered_food = OrderItems.objects.values('menu_id__item_name', 'menu_id__image').annotate(total_ordered=Sum('quantity')).order_by('-total_ordered')[:10]
    import os
    from django.conf import settings

    # assume that the string is "/media/my_image.png"
    for i in top_ordered_food:
        print(i['menu_id__image'])
        image_url = os.path.join(settings.MEDIA_URL, i['menu_id__image'])
        print(image_url)
        i['menu_id__image'] = image_url

    context = {
        'menu': MenuItems.objects.filter(is_seen=True),
        'top_ordered_food':top_ordered_food
    }
    return render(request, 'food-ordering/dashboard.html', context)

@login_required
def menu(request, object_id):
    sort_option = request.GET.get('sort_option', None)

    default_sort_option = 'price'

    menus = MenuItems.objects.filter(is_seen=True) if request.user.role == 'customer' else MenuItems.objects.all()

    if sort_option == 'sortByOrders':
        menus = menus.annotate(num_orders=Count('orderitems')).order_by('-num_orders')
    elif sort_option == 'HighToLow':
        menus = menus.order_by('-price')
    elif sort_option == 'LowToHigh':
        menus = menus.order_by('price')
    else:
        menus = menus.order_by('price')
        sort_option = default_sort_option

    items_per_page = 2

    paginator = Paginator(menus, items_per_page)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    menu_count = menus.count()

    start_index = (page.number - 1) * items_per_page
    end_index = start_index + len(page)


    menu_per_page = end_index - start_index

    context = {'page': page, 'sort_option': sort_option, 'menu_count': menu_count, 'menu_per_page':menu_per_page}
    # data = MenuItems.objects.all()
    # context = {
    #     'data':data,
    # }
    return render(request, 'food-ordering/menu.html', context)
@login_required
def create_menu(request, object_id):
    if request.method == "POST":
        manager = CustomUser.objects.get(email = request.user)
        item_name = request.POST['name']
        image = request.FILES['image']
        description = request.POST['description']
        price = request.POST['price']
        MenuItems.objects.create(
            manager_id = manager,
            item_name = item_name,
            image = image,
            description = description,
            price = price
        )
        messages.success(request, "Menu successfully added.")
        return redirect(f'/dashboard/{object_id}/menu/')

    return render(request, 'Manager/create_menu.html')

@login_required
def delete_menu(request, object_id, pk):
    MenuItems.objects.filter(pk = pk).delete()
    messages.success(request, "Menu successfully deleted.")
    return redirect(f'/dashboard/{object_id}/menu/')

@login_required
def update_menu(request, object_id, pk):
    data = MenuItems.objects.get(pk = pk)
    if request.method == "POST":
        item_name = request.POST['name'] if request.POST['name'] else data.item_name
        price = request.POST['price'] if request.POST['price'] else data.price
        description = request.POST['description'] if request.POST['description'] else data.description
        item_image = request.FILES['image']  if 'image' in request.FILES else data.image
        data.item_name = item_name
        data.price = price
        data.description = description
        data.image = item_image
        data.save()
        messages.success(request, "Menu successfully updated.")
    context = {
        'data':data
    }
    return render(request, 'Manager/edit_menu.html', context)

def is_seen(request, object_id, pk):
    MenuItems.objects.filter(id = pk).update(is_seen = False)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def is_seen_false(request, object_id, pk):
    MenuItems.objects.filter(id = pk).update(is_seen = True)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def manage_order(request, object_id):
    all_order_items = []
    for order in Basket.objects.exclude(status = 'Created'):
        item = OrderItems.objects.filter(basket_id = order)
        all_order_items.append(item)
    context = {
        'orders_request':zip(Basket.objects.exclude(status = 'Created')[::-1],all_order_items[::-1]),
        'all_items':all_order_items
    }
    return render(request, 'Manager/order.html', context)

@login_required
def approval(request, object_id):
    cust = CustomUser.objects.get(email = request.user)
    if request.method == 'POST':
        d = request.POST
        for k,v in d.items():
            if k == 'accept':
                basket = Basket.objects.get(id = v )
                basket.status = 'In_progress'
                basket.save()
                message = "The manager has accepted your order."
                Notification.objects.create(
                    customer = cust,
                    notification = message
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)("notification", {
                "type": "notify_customer",
                "customer": f"food request:{message}",
                "status": 'In_progress'
                })
            if k == 'ready':
                basket = Basket.objects.get(id = v )
                basket.status = 'Ready'
                basket.save()
                message = "Your order is ready."
                Notification.objects.create(
                    customer = cust,
                    notification = message
                )

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)("notification", {
                "type": "notify_customer",
                "customer": f"food request:{message}",
                "status": 'Ready'
                })
            if k == 'decline':
                basket = Basket.objects.get(id = v )
                basket.status = 'Declined'
                basket.save()
                message = "The manager has declined your order due to insufficient of accessories."
                Notification.objects.create(
                    customer = cust,
                    notification = message
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)("notification", {
                "type": "notify_customer",
                "customer": f"food request:{message}",
                "status": 'Declined'
                })
            if k == 'cash':
                basket = Basket.objects.get(id = v )
                basket.payment_status = 'paid_by_cash'
                basket.status = 'Completed'
                basket.save()
            if k == 'online':
                basket = Basket.objects.get(id = v )
                basket.payment_status = 'paid_by_online'
                basket.status = 'Completed'
                basket.save()
    return redirect(f'/dashboard/{object_id}/orders_requests/')

@login_required
def add_order(request, object_id, pk):
    cust = CustomUser.objects.get(email = request.user)
    order = MenuItems.objects.get(pk = pk)
    basket = ''
    if Basket.objects.filter(customer_id = CustomUser.objects.get(email = request.user), status = 'Created').first():
        basket = Basket.objects.filter(customer_id = CustomUser.objects.get(email = request.user), status = 'Created').first()
    else:
        Basket.objects.create(customer_id = CustomUser.objects.get(email = request.user), status = 'Created')
        basket = Basket.objects.filter(customer_id = CustomUser.objects.get(email = request.user), status = 'Created').first()

    if request.method == 'POST':
        if OrderItems.objects.filter(basket_id = basket, item_name = order.item_name).first():
            messages.error(request, "The item already exists.")
        else:
            OrderItems.objects.create(
                basket_id = basket,
                menu_id = order,
                customer_id = cust,
                item_name = order.item_name,
                quantity = 1,
                image = order.image,
                menu_price = order.price,
                price = order.price
            )
            basket.bill = order.price
            basket.save()
            messages.success(request, "Order successfully added.")
    return redirect(f'/dashboard/{object_id}/menu/')

@login_required
def cart(request, object_id):
    return render(request, 'Cust/cart.html')

@login_required
def confirm_order(request, object_id):
    cust = CustomUser.objects.get(email = request.user)
    basket = Basket.objects.filter(customer_id = cust, status = 'Created').first()

    if request.method == 'POST':
        d = request.POST
        total = request.POST['total']
        current_month = datetime.now().month
        for k,v in d.items():
            if 'q' in k:
                quantity,pk = k.split('-')
                orders = OrderItems.objects.get(pk = pk)
                orders.quantity = v
                orders.price = int(v) * int(orders.menu_price)
                orders.save()
        basket.bill = total
        basket.status = 'Waiting'
        basket.order_date = datetime.now()
        basket.month = current_month
        basket.save()
        Notification.objects.create(
            customer = cust,
            notification = f"{request.user.first_name} {request.user.last_name} has made an order"
        )
        messages.success(request, "Order has been sent. Please wait the order to be ready.")
    return redirect(f'/dashboard/{object_id}/menu/')

@login_required
def delete_order(request, object_id, pk):
    OrderItems.objects.filter(pk=pk).delete()
    return redirect(f'/dashboard/{object_id}/cart/')

@login_required
def orders(request, object_id):
    customer = CustomUser.objects.get(email = request.user)
    orders = Basket.objects.filter(customer_id = customer)
    context = {
        'make_orders':orders[::-1]
        }
    return render(request,'food-ordering/order.html',context)

def cancel_order(request, object_id, pk):
    cust = CustomUser.objects.get(email = request.user)
    Basket.objects.filter(pk = pk).update(status = 'Cancel')
    message = 'Food order has been cancelled'
    Notification.objects.create(
            customer = cust,
            notification = f"{request.user.first_name} {request.user.last_name} has cancelled order"
        )
    messages.success(request, 'Order cancelled.')
    return redirect(f'/dashboard/{object_id}/orders/')

@login_required
def payment(request, object_id, pk):
    cust = CustomUser.objects.get(email = request.user)
    payment = Basket.objects.get(id = pk)
    if request.method == 'POST':
        journal = request.POST['jrnl_no']
        # scrn = request.FILES['scrn']
        # fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        # filename = fs.save(scrn.name, scrn)
        # file_path = os.path.join(settings.MEDIA_ROOT, filename)
        # # Read the image using OpenCV
        # img = cv2.imread(file_path)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # thresh = cv2.adaptiveThreshold(gray, 250, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11)
        # text = pytesseract.image_to_string(thresh)
        # journal = int(text[(text.index('From')-9):(text.index('From'))])
        payment.jrnl_no = journal
        # payment.screenshot = scrn
        payment.order_date = datetime.now()
        payment.payment_status = 'paid_by_online'
        payment.status = 'Completed'
        payment.save()
        messages.success(request, "Payment successful.")
        # os.remove(file_path)
    return redirect(f'/dashboard/{object_id}/orders_requests/')

@login_required
def feedback(request, object_id):
    if request.method == 'POST':
        description = request.POST['feedback']
        Feedback.objects.create(customer = request.user, description = description)
        messages.success(request, 'Feedback given successfully')
    return redirect(f'/dashboard/{object_id}/')

@login_required
def profile(request, object_id):
    profile = CustomUser.objects.get(email = request.user)
    if request.method == 'POST':
        profile.first_name = request.POST['first_name']
        profile.last_name = request.POST['last_name']
        profile.email = request.POST['email']
        profile.contact_number = request.POST['contact']
        profile.save()
        messages.success(request, 'Your profile has been updated.')
    return render(request, 'food-ordering/profile.html')

@login_required
def change_password(request, object_id):
    if request.method == 'POST':
        if profile.password == request.POST['current_password']:
            profile.password = request.POST['password']
            profile.save()
            messages.success(request, 'Your profile has been updated.')
        else:
            messages.error(request, 'Your current password does not match with any.')

    return render(request, 'food-ordering/change_password.html')

def about(request, object_id):
    return render(request, 'food-ordering/about.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            current_site = get_current_site(request)
            subject = 'Food ordering system'
            otp = random.randint(100000, 999999)
                    # email_from = settings.EMAIL_HOST_USER

            message2 = f"Your otp for resetting password is {otp}."
                    # First send OTP through email before saving data to Database

            send_mail(
                        subject,
                        message2,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently = True

            )
            request.session['email'] = email
            request.session['otp'] = str(otp)
            return render(request, "reset_okay.html")
        except Exception as e:
            messages.error(request,
                "Failed to send OTP through Email."+str(e))

    return render(request,"reset_password.html")

def enter_otp(request):
    email = request.session['email']
    if request.method == 'POST':
        d = request.POST
        for k,v in d.items():
            if k == 'resend':
                try:
                    current_site = get_current_site(request)
                    subject = 'Food ordering system'
                    otp = random.randint(100000, 999999)
                            # email_from = settings.EMAIL_HOST_USER

                    message2 = f"Your otp is {otp}."
                            # First send OTP through email before saving data to Database

                    send_mail(
                                subject,
                                message2,
                                settings.EMAIL_HOST_USER,
                                [email],
                                fail_silently = True

                    )
                    request.session['otp'] = str(otp)
                except Exception as e:
                            messages.error(request,
                                "Failed to send OTP through Email."+str(e))

            if k == 'submit':
                myotp = request.POST.get('otp')
                otp = request.session['otp']
                if str(myotp) == otp:
                    messages.success(request, "OTP verification successful. You may now reset your password.")
                    return redirect('reset_password')
                else:
                    messages.error(request, 'OTP is incorrect, please try again')
    return render(request, 'enter_otp.html')


def reset_password_confirm(request):
    email = request.session['email']
    if request.method == 'POST':
        password = request.POST['password']
        CustomUser.objects.filter(email = email).update(password = make_password(password))
        messages.success(request, 'Password has been reset.')
        return redirect('signin')
    return render(request, 'reset_password_confirm.html')\






