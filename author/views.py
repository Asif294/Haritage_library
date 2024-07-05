from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import FormView,CreateView
from .models import Deposite
from .forms import UserRegistrationFrom
from .forms import ProfileUpdateForm
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView
from .forms import UserUpdateForm,DepositeForm
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import  update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import  PasswordChangeForm

class UserRegistatinView(FormView):
    template_name='author/user_registation.html'
    form_class=UserRegistrationFrom
    success_url=reverse_lazy('profile')

    def form_valid(self, form):
        user=form.save()
        login( self.request, user)
        messages.success(self.request, 'User Registation  Successfully')
        return super().form_valid(form)
    
def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
    }) 

    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()


        

class UserLoginView(LoginView):
    template_name  ='author/user_login.html'
    def get_success_url(self):
        messages.success(self.request, 'User Login Successfully')
        return reverse_lazy('home')
    
class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.post(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        messages.success(self.request, 'User Logout Successfully')
        return reverse_lazy('home')
    
class UserLibraryAccountUpdateView(View):
    template_name = 'author/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
        messages.success(self.request, 'Profile Updated Successfully')
        return render(request, self.template_name, {'form': form})
    

class PassChangeView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'author/pass_change.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password Updated Successfully!!!')
        return super().form_valid(form)
    
       
class DeposteView(LoginRequiredMixin,CreateView):
    model=Deposite
    form_class=DepositeForm
    template_name='author/deposite.html'
    success_url=reverse_lazy('home')
    def get_form_kwargs(self):
        kwargs=super().get_form_kwargs()
        kwargs.update(
            {'account':self.request.user.account}
        )
        return kwargs
    
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance+=amount
        account.save(
            update_fields=[
                'balance'
            ]
        )
        messages.success(self.request,f'Your Deposite Amount {amount}$ Successflly!!!')

        send_transaction_email(self.request.user, amount, 'Deposit Message', 'book/deposite_email.html')

        return super().form_valid(form)
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['type']='Deposite Money'
        return context
    
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
            user.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'author/update_profile.html', {'form': form})