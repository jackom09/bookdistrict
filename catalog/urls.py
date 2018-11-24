from django.urls import path
from catalog import views


urlpatterns = [
    path('', views.Index.as_view(), name='index'),

    path('books/', views.BookList.as_view(), name='book_list'),
    path('books/my_books/', views.MyBookList.as_view(), name='my_book_list'),
    path('books/<int:pk>/', views.BookDetail.as_view(), name='book_detail'),
    path('books/add/', views.BookCreate.as_view(), name='book_add'),
    path('books/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('books/<int:pk>/update/status', views.BookUpdateStatus.as_view(), name='book_status_change'),
    path('books/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),

    path('members/', views.MemberList.as_view(), name='member_list'),
    path('members/<int:pk>/', views.MemberDetail.as_view(), name='member_detail'),

    # akcje po stronie zainteresowanego
    path('books/<int:pk>/reservation/interest', views.ShowInterest.as_view(), name='show_interest'),
    path('books/<int:pk>/reservation/resignation', views.WithdrawInterest.as_view(), name='withdraw_interest'),

    # akcje po stronie właściciela
    path('books/<int:book_pk>/reservation/<int:member_pk>/borrow', views.BorrowBook.as_view(), name='borrow_book'),
    path('books/<int:book_pk>/reservation/<int:member_pk>/return', views.ReturnBook.as_view(), name='return_book'),

    path('signup/', views.SignUp.as_view(), name='signup'),
    path('edit_personal_data/<int:pk>/', views.UserEdit.as_view(), name='user_edit'),
    path('membership/<int:pk>/accept_member', views.AcceptNewMember.as_view(), name='accept_member'),
    path('membership/<int:pk>/delete_member', views.DeleteMember.as_view(), name='delete_member'),
]
