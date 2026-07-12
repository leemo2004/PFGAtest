
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'), # ← 新增
    path('chatbot/', views.chatbot_view, name='chatbot'), # ← 新增

    # RESTful API
    path('api/books/', views.api_book_list, name='api_book_list'),
    path('api/books/<int:book_id>/', views.api_book_detail, name='api_book_detail'),
    path('api/borrow/', views.api_borrow_book, name='api_borrow_book'),
    path('api/return/<int:record_id>/', views.api_return_book, name='api_return_book'),
    path('api/my-books/', views.api_my_books, name='api_my_books'),
    path('api/overdue/', views.api_overdue_books, name='api_overdue_books'),
]
