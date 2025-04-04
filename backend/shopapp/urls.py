from django.urls import path

from .views import CategoryView, ProductListView, BannerListApiView, PopularListApiView, LimitedListApiView

app_name = 'shopapp'

urlpatterns = [
    path('categories/', CategoryView.as_view()),
    path('catalog/', ProductListView.as_view()),
    path('banners/', BannerListApiView.as_view()),
    path('products/limited', LimitedListApiView.as_view()),
    path('products/popular', PopularListApiView.as_view()),

]