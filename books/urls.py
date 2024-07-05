from django.urls import path,include
from .import views
urlpatterns = [
    
    
    path('review/<int:id>/', views.ReviewView, name='submit_review'),
    path('books/borrow_book/<int:id>/', views.BorrowBookView, name='borrow_book'),
     path('profile/',views.ProfileView.as_view(), name='profile' ),
    path('return_book/<int:id>/',views.ReturnBook,name='return_book'),
    path('book/<int:id>/', views.BookDetailsView.as_view(), name='book_details'),
    path('book/<int:book_id>/review/', views.submit_review, name='submit_review'),
    path('delete_borrowed_book/<int:book_id>/', views.DeleteBorrowedBookView.as_view(), name='delete_borrowed_book'),
]