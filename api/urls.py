from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.views import *

urlpatterns = [
    # Merchant onboarding (not tenant-scoped)
    path('merchant/', MerchantCreateView.as_view(), name='merchant-create'),
    path('merchant/otp/', MerchantVrifyOtpView.as_view(), name='merchant-otp'),
    path('merchant/otp/resend/', MerchantVrifyOtpResendView.as_view(), name='merchant-otp-resend'),
    path('merchant/<int:pk>/', MerchantRetrieveView.as_view(), name='merchant-retrieve'),

    # Tenant-scoped POS APIs
    path('m/<slug:merchant_id>/login', UserLoginView.as_view(), name='user-login'),

    path('m/<slug:merchant_id>/categories/', CategoryListView.as_view(), name='categories'),
    path('m/<slug:merchant_id>/category/', CategoryCreate.as_view(), name='category'),
    path('m/<slug:merchant_id>/category/<int:pk>', CategoryDelete.as_view(), name='category-delete'),

    path('m/<slug:merchant_id>/products/', ProductListView.as_view(), name='products'),
    path('m/<slug:merchant_id>/product/', ProductCreate.as_view(), name='product'),
    path('m/<slug:merchant_id>/product/<int:pk>', ProductDelete.as_view(), name='product-delete'),

    path('m/<slug:merchant_id>/orders/', OrderListView.as_view(), name='orders'),
    path('m/<slug:merchant_id>/order/', CreateOrderView.as_view(), name='order'),

    path('m/<slug:merchant_id>/cart_item/', CartItemAddView.as_view(), name='cart_item'),
    path('m/<slug:merchant_id>/cart/', CartCreateView.as_view(), name='cart'),
    path('m/<slug:merchant_id>/cart/<int:pk>', CartRetrieveView.as_view(), name='cart-retrieve'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
