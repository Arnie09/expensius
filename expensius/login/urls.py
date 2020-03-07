from . import views
from django.urls import path

urlpatterns = [
    path('',views.home, name= 'home'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('register/',views.register_view, name='register')
    # path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
]