

import random



from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from api.taks import send_email_task, send_otp
from cart.models import Cart, CartItem
from cart.serializer import *

import merchant
from merchant.models import Merchant
from merchant.serializer import MerchantCreateSerializer, MerchantOtpResendSerializer, MerchantOtpSerializer, MerchantSerializer
from order.models import Order, OrderItem
from order.serializer import OrderSerializer, OrderPaymentSerializer
from product.models import Product, Category
from product.serializer import ProductSerializer, CategorySerializer
import user
from user.models import User
from user.serializer import UserPinCodeSerializer, UserRefreshTokenSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.tenancy import resolve_merchant
from inventory.models import StockItem, StockMovement, Location




# Create your views here.

class MerchantCreateView(generics.CreateAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantCreateSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.queryset.filter(email=serializer.validated_data['email'] , phone = serializer.validated_data['phone']).exists():
            return Response({'msg': "Merchant with this email or phone already exists"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            code = str(random.randint(100000, 999999))
            merchant=Merchant.objects.create(
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'],     
                phone =serializer.validated_data['phone'],  
                password=serializer.validated_data['password'],
                description=serializer.validated_data.get('description', ''),
                code=code,
                expair_code=timezone.now() + timezone.timedelta(minutes=2)
            )
        if merchant:
            # Never return OTP in response.
            return Response({'msg': f"Merchant created successfully. wait for approval merchant:{merchant.pk}"}, status=status.HTTP_201_CREATED)
        return Response({'msg': "Failed to create merchant"}, status=status.HTTP_400_BAD_REQUEST)
    
class MerchantVrifyOtpView(generics.GenericAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantOtpSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            merchant = get_object_or_404(Merchant, id=serializer.validated_data['merchant_id'] 
                                         ,expair_code__gt=timezone.now() , 
                                         used_code_at__isnull=True,code=serializer.validated_data['code'])
            
            merchant.used_code_at = timezone.now()
            merchant.is_approved = True
            merchant.save()
            return Response({'msg': "Merchant approved successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': "Invalid code or code expired"}, status=status.HTTP_400_BAD_REQUEST)
          
class MerchantVrifyOtpResendView(generics.GenericAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantOtpResendSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant_id = serializer.validated_data['merchant_id']
        try:
            merchant = get_object_or_404(Merchant, id=merchant_id , expair_code__lt=timezone.now() , used_code_at__isnull=True)
            if merchant.is_approved:
                return Response({'msg': "Merchant is already approved"}, status=status.HTTP_400_BAD_REQUEST)

            code = str(random.randint(100000, 999999))
            merchant.code = code
            merchant.expair_code = timezone.now() + timezone.timedelta(minutes=2)
            merchant.used_code_at = None
            merchant.save()

            return Response({'msg': "OTP resent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': "cant get new code wait after a few minutes try again"}, status=status.HTTP_404_NOT_FOUND)
        
class MerchantRetrieveView(generics.RetrieveAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        merchant_id = kwargs.get('pk')
        merchant = get_object_or_404(Merchant, id=merchant_id , is_active=True ,is_approved=True)
        serializer = self.get_serializer(merchant)
        
        return Response(serializer.data)


class UserLoginView(generics.GenericAPIView):


    queryset = User.objects.all()
    serializer_class = UserPinCodeSerializer
    permission_classes =[AllowAny]

    def post(self, request, *args, **kwargs):
       
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant_slug = kwargs.get('merchant_id')
        merchant = resolve_merchant(request=request, merchant_id=merchant_slug)
        pin_code = serializer.validated_data['pin_code']

        try:
            user = User.objects.select_related('merchant').get(pin_code=pin_code, merchant=merchant)
            # if user.check_password(pin_code):
            refresh = RefreshToken.for_user(user)
            user_data = {
                'id': user.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': str(refresh.access_token),
                'refresh_token': str(refresh),

                }


            response_serializer = UserSerializer(data=user_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'msg': "Invalid pin code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'msg': "User not found "}, status=status.HTTP_404_NOT_FOUND)
     


class CustomPagination(PageNumberPagination):
    # page_size_query_param = 'page'

    # max_page_size = 10
    page_size = 10

    def get_paginated_response(self, data):
        paginator = self.page.paginator if self.page else None
        
        total_pages = paginator.num_pages if paginator else 0
        current_page = self.page.number if self.page else 1

        return Response({
            "count": paginator.count if paginator else 0,
            "total_pages": total_pages,
            "current_page": current_page,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })



class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Category.objects.filter(merchant=merchant, is_active=True, is_delete=False).order_by('title')

    def list(self, request, *args, **kwargs):
        merchant = resolve_merchant(request=request, merchant_id=kwargs['merchant_id'])
        # Cache hot catalog reads; invalidation strategy to be added (versioned keys).
        cache_key = f"catalog:{merchant.id}:categories"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        resp = super().list(request, *args, **kwargs)
        cache.set(cache_key, resp.data, timeout=60)
        return resp

    
class CategoryCreate(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        serializer.save(merchant=merchant)


class CategoryDelete(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Category.objects.filter(merchant=merchant)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Product.objects.filter(merchant=merchant, is_active=True, is_delete=False).select_related('category').order_by('title')

    def list(self, request, *args, **kwargs):
        merchant = resolve_merchant(request=request, merchant_id=kwargs['merchant_id'])
        cache_key = f"catalog:{merchant.id}:products"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        resp = super().list(request, *args, **kwargs)
        cache.set(cache_key, resp.data, timeout=60)
        return resp


class ProductCreate(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        serializer.save(merchant=merchant)


class ProductDelete(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Product.objects.filter(merchant=merchant)


class CartRetrieveView(generics.RetrieveAPIView):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartViewSerializer

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Cart.objects.filter(user__merchant=merchant).prefetch_related('items__product')


class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartCreateSerializer

    def create(self, request, *args, **kwargs):
        merchant = resolve_merchant(request=request, merchant_id=kwargs['merchant_id'])
        user_id = request.data.get("user_id")
        try:
            if user_id:
                user = get_object_or_404(User, id=user_id, merchant=merchant)

                cart = Cart.objects.create(user=user)

                return Response({'cart_id': cart.pk}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
        return Response({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)


class CartItemAddView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemCreateSerializer

    def create(self, request, *args, **kwargs):
        merchant = resolve_merchant(request=request, merchant_id=kwargs['merchant_id'])
        cart_id = request.data.get("cart_id")
        cart = get_object_or_404(Cart, id=cart_id, user__merchant=merchant)
        if cart.is_active:
            product_id = request.data.get("product_id")
            try:
                quantity_to_add = int(str(request.data.get("quantity")))
            except (ValueError, TypeError):
                return Response({'error': 'Quantity must be integer'}, status=status.HTTP_400_BAD_REQUEST)

            cart_item = self.queryset.filter(cart=cart, product_id=product_id).select_related('product').first()

            if cart_item and quantity_to_add > 0:
                cart_item.quantity += quantity_to_add
                cart_item.save()
                serializer = CartItemViewSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer = CartItemCreateSerializer(data=request.data)

            if serializer.is_valid():
                product = get_object_or_404(Product, id=product_id, merchant=merchant)
                cart = CartItem.objects.create(cart=cart, product=product, quantity=quantity_to_add)
                final_serializer = CartItemViewSerializer(cart)
                return Response(final_serializer.data, status=status.HTTP_201_CREATED)
        return Response('bad request', status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        merchant = resolve_merchant(request=self.request, merchant_id=self.kwargs['merchant_id'])
        return Order.objects.filter(user__merchant=merchant).prefetch_related('items__product').order_by('-created_at')


class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderPaymentSerializer

    def create(self, request, *args, **kwargs):
        merchant = resolve_merchant(request=request, merchant_id=kwargs['merchant_id'])
        cart_id = request.data.get("cart_id")
        user_id = request.data.get("user_id")

        if cart_id is None and user_id is None:
            return Response({'error': 'Cart id or User id must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart: Cart = get_object_or_404(Cart, id=cart_id, user__merchant=merchant)
        user = get_object_or_404(User, id=user_id, merchant=merchant)
        if cart.is_active:
            try:
                cart_items = list(CartItem.objects.filter(cart=cart).select_related('product'))
                if not cart_items:
                    return Response({'error': 'cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    # Default location for merchant (create later via admin).
                    location = Location.objects.filter(merchant=merchant, is_default=True, is_active=True).first()
                    if location is None:
                        location = Location.objects.create(merchant=merchant, name='Default', is_default=True)

                    product_ids = [ci.product_id for ci in cart_items]
                    stock_rows = (
                        StockItem.objects.select_for_update()
                        .filter(merchant=merchant, location=location, product_id__in=product_ids)
                        .select_related('product')
                    )
                    stock_by_product = {s.product_id: s for s in stock_rows}

                    # Ensure all products have stock rows.
                    missing = [pid for pid in product_ids if pid not in stock_by_product]
                    if missing:
                        for pid in missing:
                            stock_by_product[pid] = StockItem.objects.create(
                                merchant=merchant,
                                location=location,
                                product_id=pid,
                                on_hand=0,
                            )

                    # Validate stock.
                    for ci in cart_items:
                        stock = stock_by_product[ci.product_id]
                        if stock.on_hand < ci.quantity:
                            return Response(
                                {'error': f'insufficient stock for product {ci.product_id}'},
                                status=status.HTTP_409_CONFLICT,
                            )

                    total_price = sum([ci.total_price for ci in cart_items])
                    order_data = {
                        'user': user.pk,
                        'status': Order.Status.PENDING,
                        'subtotal': total_price,
                        'shipping_cost': 0,
                        'total_amount': total_price,
                        'payment_ref': None,
                        'notes': request.data.get('notes'),
                    }
                    order_serializer = OrderSerializer(data=order_data)
                    order_serializer.is_valid(raise_exception=True)
                    new_order = order_serializer.save()

                    order_items_to_create = [
                        OrderItem(
                            order=new_order,
                            product=ci.product,
                            quantity=ci.quantity,
                            price=ci.price,
                            total_price=ci.total_price,
                        )
                        for ci in cart_items
                    ]
                    OrderItem.objects.bulk_create(order_items_to_create)

                    for ci in cart_items:
                        stock = stock_by_product[ci.product_id]
                        stock.on_hand -= ci.quantity
                        stock.save(update_fields=['on_hand', 'updated_at'])
                        StockMovement.objects.create(
                            merchant=merchant,
                            location=location,
                            product=ci.product,
                            qty_delta=-ci.quantity,
                            reason=StockMovement.Reason.SALE,
                            ref_type='order',
                            ref_id=str(new_order.pk),
                        )

                    cart.is_active = False
                    cart.save(update_fields=['is_active', 'updated_at'])

                final_order_serializer = OrderSerializer(new_order)
                return Response(final_order_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(e)
                return Response({'error': 'An unexpected error occurred while creating the order.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'this cart cant add payment'},status=status.HTTP_400_BAD_REQUEST)
