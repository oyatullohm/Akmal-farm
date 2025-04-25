from django.contrib import messages


from django.shortcuts import render
from django.views.generic import DetailView
from .forms import  *
from .models import *
# Create your views here.


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

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
    
    product_xit = Product.objects.filter(category=1).all()
    product_sale = Product.objects.filter(category=2).all()
    category = Category.objects.first()
    category2 = Category.objects.last()
    context = {
        'product_xit': product_xit,
        'category': category,
        'category2': category2,

    }
    return render(request,'index.html',context)


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

login_required(login_url='/auth/send-otp/')
def DeleteProduct(request, product_id):
    """ Savatdan bitta mahsulot turini butunlay o‘chirish """
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    if order:
        order_item = OrderItem.objects.filter(order=order, product_id=product_id).first()
        if order_item:
            order_item.delete()
    return redirect("cart")  



from unidecode import unidecode

def search_products(request):
    query = request.GET.get('q', '')  
    category_id = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        normalized_query = unidecode(query.lower()) 
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



from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

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


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CheckoutForm



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