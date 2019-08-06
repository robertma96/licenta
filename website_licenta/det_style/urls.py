from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/result/', views.style_image, name='style_image'),
    path('upload', views.upload, name='upload'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('myprofile', views.my_profile, name='myprofile')
]
