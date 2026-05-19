from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny


from cart.models import Cart, CartItem
from cart.serializer import *
import merchant
from merchant.models import Merchant
from merchant.serializer import MerchantCreateSerializer, MerchantSerializer
from order.models import Order, OrderItem
from order.serializer import OrderSerializer, OrderPaymentSerializer
from product.models import Product, Category
from product.serializer import ProductSerializer, CategorySerializer

User = get_user_model()


# Create your views here.

class MerchantCreateView(generics.CreateAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantCreateSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant=Merchant.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],       
            password=serializer.validated_data['password'],
            description=serializer.validated_data.get('description', '')
        )
        if merchant:
            return Response({'msg': "Merchant created successfully wait for approval"}, status=status.HTTP_201_CREATED)
        return Response({'msg': "Failed to create merchant"}, status=status.HTTP_400_BAD_REQUEST)

class MerchantRetrieveView(generics.RetrieveAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        merchant_id = kwargs.get('pk')
        merchant = get_object_or_404(Merchant, id=merchant_id , is_active=True ,is_approved=True)
        serializer = self.get_serializer(merchant)
        return Response(serializer.data)

     

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

    
class CategoryCreate(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDelete(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination


class ProductCreate(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDelete(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartRetrieveView(generics.RetrieveAPIView):
    queryset = Cart.objects.prefetch_related('items').all()
    serializer_class = CartViewSerializer


class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartCreateSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        try:
            if user_id:
                user = get_object_or_404(User, id=user_id)

                cart = Cart.objects.create(user=user)

                return Response({'cart_id': cart.pk}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
        return Response({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)


class CartItemAddView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemCreateSerializer

    def create(self, request, *args, **kwargs):
        cart_id = request.data.get("cart_id")
        cart = get_object_or_404(Cart, id=cart_id)
        if cart.is_active:
            product_id = request.data.get("product_id")
            try:
                quantity_to_add = int(str(request.data.get("quantity")))
            except (ValueError, TypeError):
                return Response({'error': 'Quantity must be integer'}, status=status.HTTP_400_BAD_REQUEST)

            cart_item = self.queryset.filter(cart=cart, product=product_id).first()  

            if cart_item and quantity_to_add > 0:
                cart_item.quantity += quantity_to_add
                cart_item.save()
                serializer = CartItemViewSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer = CartItemCreateSerializer(data=request.data)

            if serializer.is_valid():
                product = get_object_or_404(Product, id=product_id)
                cart = CartItem.objects.create(cart=cart, product=product, quantity=quantity_to_add)
                final_serializer = CartItemViewSerializer(cart)
                return Response(final_serializer.data, status=status.HTTP_201_CREATED)
        return Response('bad request', status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().prefetch_related('product')
    serializer_class = OrderSerializer
    pagination_class = CustomPagination


class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderPaymentSerializer

    def create(self, request, *args, **kwargs):

        cart_id = request.data.get("cart_id")
        user_id = request.data.get("user_id")

        if cart_id is None and user_id is None:
            return Response({'error': 'Cart id or User id must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart:Cart = get_object_or_404(Cart, id=cart_id)
        user = get_object_or_404(User, id=user_id)
        if cart.is_active:
            try:
               
                total_price = cart.items.all().aggregate(Sum('total_price'))['total_price__sum'] or 0
                order_data = {
                    'user': user.pk,
                    'status': Order.Status.PENDING,
                    'subtotal': total_price,
                    'shipping_cost': total_price,
                    'total_amount': total_price,
                    'payment_ref': None,
                    'notes': request.data.get('notes'),

                }
                order_serializer = OrderSerializer(data=order_data)

                order_serializer.is_valid(raise_exception=True)
                new_order = order_serializer.save()

                cart_items = CartItem.objects.filter(cart=cart)

                order_items_to_create = []
                for item in cart_items:
                    order_items_to_create.append(
                        OrderItem(
                            order=new_order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.price,
                            total_price=item.total_price,
                        )
                    )
                    OrderItem.objects.bulk_create(order_items_to_create)
                    final_order_serializer = OrderSerializer(new_order)
                    cart.is_active = False
                    cart.save()

                    return Response(final_order_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(e)
                return Response({'error': 'An unexpected error occurred while creating the order.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'this cart cant add payment'},status=status.HTTP_400_BAD_REQUEST)