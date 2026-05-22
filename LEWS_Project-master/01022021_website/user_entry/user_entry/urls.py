from django.contrib import admin
from django.urls import include, path
from user import views as user_view 
from django.contrib.auth import views as auth 

urlpatterns = [
    path('', include('login.urls')),
    path('admin/', admin.site.urls),
    path('', include('user.urls')), 
    path('login/', user_view.Login, name ='login'), 
    path('logout/', auth.LogoutView.as_view(next_page='/'), name ='logout'), 
    path('register/', user_view.register, name ='register'),
]
