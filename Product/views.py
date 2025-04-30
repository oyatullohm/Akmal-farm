from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .lotin_krill import krill_lotin_traslate
from django.views.generic import DetailView
from django.contrib import messages
from django.shortcuts import render
from unidecode import unidecode
from .models import *
from .forms import  *
import requests
import redis
import json

@login_required(login_url='/auth/send-otp/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    print(request.user)
   
    order, created = Order.objects.get_or_create(user=request.user, is_completed=False)

    
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        order_item.quantity += 1  
        order_item.save()
    messages.success(request, " mahsulot Savatchaga qo'shildi ")

    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required(login_url='/auth/send-otp/')
def cart_view(request):
    order = Order.objects.filter(user=request.user, is_completed=False).first()  
    return render(request, "cart.html", {"order": order})
    
def Index(request):
    from requests.auth import HTTPBasicAuth
    import time
    url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
    username = "Online"
    password = "cJXGLytPHb3nDNZf5gRh7jzwa"
    

    r = redis.Redis(host='localhost', port=6379, db=0)
    # # start_time = time.time()
   
    # # end_time = time.time()
    # # elapsed_time = end_time - start_time  
    # # print(f"Ma'lumot {elapsed_time:.2f} sekundda keldi")

    
    cached_data = r.get('data')

    if cached_data:

        data = json.loads(cached_data)
    else:
        response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={})
    
        if response.status_code == 200:
            data = response.json().get('array', [])[:10]
            r.setex('data', 3600, json.dumps(data))
        else:
            data = []
    
    
    uid_list = [item["UID"] for item in data]
    products = Product.objects.filter(uid__in=uid_list)

    result = []
    for item in data:
        p = products.filter(uid=item["UID"])
        if p.exists():
            result.append({
                "id":p[0].id,
                'name': item['Name'],
                'price': item["Price"],
                "image1": p[0].image1.url if p[0].image1 else None
            })

    context = {

        
        "data":result

    }
    return render(request,'index.html', context)

@login_required(login_url='/auth/send-otp/')
def increase_quantity(request, item_id):
    """Mahsulot miqdorini oshirish"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)
    order_item.quantity += 1
    order_item.save()
    return redirect("cart")


@login_required(login_url='/auth/send-otp/')
def decrease_quantity(request, item_id):
    """Mahsulot miqdorini kamaytirish (0 ga yetganda o‘chirish)"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()  
    return redirect("cart")

@login_required(login_url='/auth/send-otp/')
def DeleteProduct(request, product_id):
    """ Savatdan bitta mahsulot turini butunlay o‘chirish """
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    if order:
        order_item = OrderItem.objects.filter(order=order, product_id=product_id).first()
        if order_item:
            order_item.delete()
    return redirect("cart")  


def search_products(request):
    query = krill_lotin_traslate(request.GET.get('q', '')).lower()  
    category_id = request.GET.get('category', '')
    print(query)
    print(query)
    print(query)

    products = Product.objects.all()

    if query:
        normalized_query = unidecode(query) 
        products = products.filter(name__icontains=query) | products.filter(name__icontains=normalized_query)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()  

    return render(request, 'search_result.html', {
        'products': products,
        'query': query,
        'categories': categories,
        'selected_category': category_id
    })


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product-details.html'
    context_object_name = 'product'


def checkout_view(request):
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
           
            full_name = form.cleaned_data['full_name']
            phone_number = form.cleaned_data['phone_number']
            payment_method = form.cleaned_data['payment_method']
            address = form.cleaned_data['address']

            

            return redirect('order_success')  
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form})


def Myaccount(request):
    return render(request,'my-account.html')



@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, "Mahsulot wishlistdan olib tashlandi!")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Mahsulot wishlistga qo‘shildi!")

    return redirect(request.META.get('HTTP_REFERER', 'wishlist')) 


@login_required(login_url='/auth/send-otp/')
def wishlist_view(request):
    wishlist_items= Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request,'wishlist.html',context)


def Contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/contact/')
        else:
            messages.error('Iltimos Hamma Maydonlar Toldirilganligiga Etibor bering! ')
    else:
        form = ContactForm()

    context={
        'form':form
    }

    return render(request,'contact.html',context)


def checkout_view(request):
    cart_items = request.user.cart.items.all()  

    if not cart_items:
        messages.error(request, "Sizning savatingiz bo‘sh!")
        return redirect("cart")

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.is_completed = False
            order.save()

           
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            request.user.cart.items.all().delete()
            
            messages.success(request, "Buyurtmangiz rasmiylashtirildi!")
            return redirect("order_history")

    else:
        form = CheckoutForm()
    
    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items})