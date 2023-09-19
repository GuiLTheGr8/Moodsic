"""
URL configuration for Moodsic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from Moodsic.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('searchPlaylist/', searchPlaylist, name='search_playlist'),
    path('result/', result, name='result'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
    path('save_results/', save_results, name='save_results'),
    path('moodsic-delete/<int:pk>', MoodsicDelete.as_view(), name='moodsic-delete'),
    path('accounts/login/', LoginView.as_view(template_name="Moodsic/login.html"), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page = reverse_lazy('homepage')), name='logout'),
    path('accounts/register/', register, name = 'register'),
]
