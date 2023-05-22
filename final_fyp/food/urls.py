from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home, name='home'),
    path('signup/', views.sign_up, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('otp/', views.verifyotp, name='otp'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/<str:object_id>/', views.dashboard, name='dashboard'),
    path('dashboard/<str:object_id>/menu/', views.menu, name='menu'),
    path('dashboard/<str:object_id>/menu/create_menu', views.create_menu, name='create_menu'),
    path('dashboard/<str:object_id>/menu/update/<pk>', views.update_menu, name='update'),
    path('dashboard/<str:object_id>/menu/<pk>/delete/', views.delete_menu, name='delete'),
    path('dashboard/<str:object_id>/orders_requests/', views.manage_order, name='manage_order'),
    path('dashboard/<str:object_id>/orders_requests/approval', views.approval, name='approval'),
    path('owner_dashboard/', views.owner_dashboard, name='owner'),
    path('owner_dashboard/infomanager', views.owner_add_manager, name='addmanager'),
    path('owner_dashboard/infomanager/delete', views.delete_manager, name='deletemanager'),
    path('dashboard/<str:object_id>/menu/<pk>/added', views.add_order, name='order'),
    path('dashboard/<str:object_id>/menu/confirm', views.confirm_order, name='confirm'),
    path('dashboard/<str:object_id>/seen/<pk>/true', views.is_seen, name='seen_true'),
    path('dashboard/<str:object_id>/seen/<pk>/false', views.is_seen_false, name='seen_false'),
    path('dashboard/<str:object_id>/orders/', views.orders, name='orders'),
    path('dashboard/<str:object_id>/cart/', views.cart, name='cart'),
    path('dashboard/<str:object_id>/cart/delete?<pk>/', views.delete_order, name='delete_order'),
    path('dashboard/<str:object_id>/cart/cancel/<pk>/', views.cancel_order, name='cancel_order'),
    path('dashboard/<str:object_id>/orders/<pk>/payment', views.payment, name='payment'),
    path('dashboard/<str:object_id>/feedback/', views.feedback, name='feedback'),
    path('dashboard/<str:object_id>/about/', views.about, name='about'),
    path('dashboard/<str:object_id>/profile/', views.profile, name='profile'),
    path('dashboard/<str:object_id>/change_password/', views.change_password, name='change_password'),
    path('owner_dashboard/profile/', views.owner_profile, name='owner_profile'),
    path('owner_dashboard/change_password/', views.owner_change_password, name='owner_change_password'),
    path('reset/', views.reset_password, name='reset'),
    path('reset/otp/', views.enter_otp, name='enter_otp'),
    path('reset/otp/password_reset', views.reset_password_confirm, name='reset_password'),
    path('dashboard/<str:object_id>/search/', views.search_menu, name='search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)