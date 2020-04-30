from . import views
from django.urls import path,include

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('register/',views.register_view, name='register'),
    path('register/account/', views.account_info, name='account'),
    path('change_password/', views.change_pass, name = 'change_password'),
    path('delete_profile/', views.delete_profile, name = 'delete_profile'),
    path('about/', views.about, name = 'about'),
    path('/', include('engine.urls'))
    # path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
]