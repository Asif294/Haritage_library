from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView,DetailView,ListView
from author.models import UserLibraryAccount
from .forms import ReviewForm
from .models import BookModel,Borrow
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import BookModel, Review
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django.views.generic.edit import FormView
from .models import Category
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.generic import TemplateView

class home(TemplateView):
    template_name='home.html'
    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data(*args,**kwargs)
        categorys=Category.objects.all()
        books=BookModel.objects.all()
        slug=self.kwargs.get('cat_slug',None)
        if slug is not None:
            cat=Category.objects.get(slug=slug)
            books=BookModel.objects.filter(category=cat)
        context['books']=books
        context['categorys']=categorys
        return context
def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        }) 

        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, 'text/html')
        send_email.send()

def ReviewView(request, id):
    book = get_object_or_404(BookModel, pk=id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Your Review Successfully Submitted')
            return redirect('book_detail', id=book.id)  # Adjust the redirect URL as necessary
    else:
        form = ReviewForm()
    return render(request, 'book/review.html', {'form': form, 'book': book})

class BookDetailsView(View):
    def get(self, request, id):
        book = get_object_or_404(BookModel, id=id)
        print(book.id)
        
        borrow_instance = None
        if request.user.is_authenticated:
            borrow_instance = Borrow.objects.filter(book=book, user=request.user, return_date__isnull=True).first()
        
        context = {
            'book': book,
            'is_borrowed': borrow_instance is not None,
        }
        return render(request, 'book/book_details.html', context)
    
@login_required
def BorrowBookView(request, id):
    book = get_object_or_404(BookModel, pk=id)
    requested_user = UserLibraryAccount.objects.get(user=request.user)

    if not Borrow.objects.filter(user=request.user, book=book).exists():
        if requested_user.balance >= book.borro_price:
            requested_user.balance -= book.borro_price
            requested_user.save()
            Borrow.objects.create(user=request.user, book=book)
            messages.success(request, 'This Book Successfully Borrowed.')
            send_transaction_email(request.user, requested_user.balance, 'Borrow Message', 'book/borrow_email.html')
            return redirect('profile')
        else:
            messages.error(request, 'You cannot borrow this book because your balance is less than the book price.')
    else:
        messages.error(request, 'This book is already borrowed.')

    return redirect('home')

def ReturnBook(request, id):
    book = get_object_or_404(BookModel, pk=id)
    borrow_instance = Borrow.objects.filter(book=book, user=request.user, return_date__isnull=True).first()

    if borrow_instance:
        usr = request.user  
        usr.account.balance += book.borro_price
        usr.account.save(update_fields=['balance'])

        borrow_instance.return_date = datetime.now()
        borrow_instance.save(update_fields=['return_date'])

        messages.success(request, 'Book Returned successfully!!!')
        send_transaction_email(request.user, book.borro_price, 'Book Return Message', 'book/return_book_email.html')
    else:
        messages.error(request, 'You have not borrowed this book or it has already been returned.')

    return redirect('profile') 



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'author/profile.html'  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('hi')
        borrowed_books = Borrow.objects.filter(user=self.request.user)
        print(borrowed_books)
        context['borrowed_books'] = borrowed_books
        return context
    

@login_required
def submit_review(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(BookModel, id=book_id)
        review_body = request.POST['review_body']
        rating = request.POST['rating']
        
        Review.objects.create(
            book=book,
            user=request.user,
            body=review_body,
            rating=rating
        )
        
        messages.success(request, 'Review submitted successfully!!!')
        return redirect('home') 

    return redirect('book_details', book_id=book_id)   

class DeleteBorrowedBookView(View):
    def get(self, request, book_id):
        book = get_object_or_404(Borrow, id=book_id, user=request.user)
        
        if book.return_date:
            book.delete()
            messages.success(request, 'Returned Book Record Deleted')
        else:
            messages.error(request, 'Cannot delete a book that has not been returned')
                
        return redirect('profile')