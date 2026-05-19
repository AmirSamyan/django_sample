from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.views import *

urlpatterns = [
    path('merchant/', MerchantCreateView.as_view(), name='merchant-create'),
    path('merchant/<int:pk>/', MerchantRetrieveView.as_view(), name='merchant-retrieve'),


    path('categories/', CategoryListView.as_view(), name='categories'),
    path('category/', CategoryCreate.as_view(), name='category'),
    path('category/<int:pk>', CategoryDelete.as_view(), name='category'),

    path('products/', ProductListView.as_view(), name='products'),
    path('product/', ProductCreate.as_view(), name='product'),
    path('product/<int:pk>', ProductDelete.as_view(), name='product'),

    path('orders/', OrderListView.as_view(), name='orders'),
    path('order/', CreateOrderView.as_view(), name='order'),

    path('cart_item/', CartItemAddView.as_view(), name='cart_item'),
    path('cart/', CartCreateView.as_view(), name='cart'),
    path('cart/<int:pk>', CartRetrieveView.as_view(), name='cart'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
