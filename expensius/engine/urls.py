from . import views
from django.urls import path,re_path

urlpatterns = [
    path('/?P<str:account>/',views.home, name= 'home'),
    path('',views.home, name= 'home'),
    path('add_transaction/', views.add_transacton, name='transaction'),
    path('delete_transaction/', views.delete_transaction, name='delete_transaction'),
    path('edit_transaction/', views.edit_transaction, name='edit_transaction'),
    path('search_transaction/', views.search_transaction, name='search_transaction'),
    path('delete_all_transaction/', views.delete_all_transaction, name = 'delete_all_transaction'),
    path('get_transaction/', views.get_transaction, name = 'get_transactions')
]