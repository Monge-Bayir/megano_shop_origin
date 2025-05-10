from django.urls import path, include

urlpatterns = [
    path('', include('shopapp.urls')),
    path('', include('userauth.urls'))
]