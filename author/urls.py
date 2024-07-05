from django.urls import path,include
from .import views
urlpatterns = [
    path('register/',views.UserRegistatinView.as_view(),name='register'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    path('logout/',views.UserLogoutView.as_view(),name='logout'),
    path('pass_change/', views.PassChangeView.as_view(), name='pass_change'),
    path('deposite/',views.DeposteView.as_view(),name='deposite'),
    path('profile/update/', views.update_profile, name='update_profile'),

]