"""b_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('', views.index),
    path('index/', views.index),
    path('logout/', views.logout),
    re_path('homesite/(?P<username>\w+)/$', views.homesite),
    re_path('homesite/(?P<username>\w+)/(?P<kind>article|tag|category)/(?P<id>\d+)', views.homesite),
    path('check/',views.check),
    path('comment/',views.comment),
    re_path('delete/(\d+)',views.delete),
    re_path('change/(\d+)',views.change),
    path('backend/', views.backend),
    path('backend/add_article/', views.add_article),
    path('code/', views.code)
]
