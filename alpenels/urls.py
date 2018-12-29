from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='alpenels/forms.html', extra_context={'form_title':'Login'}), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    # path('admin/', admin.site.urls),
]
