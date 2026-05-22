from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('login', views.home, name=''),
    path('', views.index, name='landing'),
    path('regis_page', views.registration, name=''),
    path('regis.html', views.login_form, name='login_form'),
    path('home', views.home, name='home'),
    path('login_page', views.login_page, name=''),
    path('home.html', views.home, name=''),
    path('signin', views.login_form, name='signin'),
    path('register', views.register_form, name='register_form'),
    path('fetch_info',views.fetch_info, name='fetch_info'),
    path('add',views.secondPartNew, name='display_info'),
    path('check',views.fetch_info, name=''),
    path('download/',views.download, name = 'download'),
    #path('data.csv',views.downfile, name = 'down'),
    path('allow.html',views.allow, name=''),
    path('insert',views.insert, name=''),
    path('logout.html',views.logout, name='logout_legacy'),
    # New pages
    path('about', views.about, name='about'),
    path('mission', views.mission, name='mission'),
    path('contact', views.contact, name='contact'),
    path('coming-soon', views.coming_soon, name='coming_soon'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
]
