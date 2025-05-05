from .views import *
from .lotin_krill import latin_to_cyrillic
from rapidfuzz import fuzz


@login_required(login_url='/auth/send-otp/')
def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result') 
    if result:
        result = json.loads(result.decode('utf-8'))
    
    
    result_dict = {item['id']: item for item in result}
    price = result_dict.get(product_id, {}).get('price', 0)

    
    order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order=order,      
                                    product=product,
                                    price =price,
                                   
                                    )

    if not created:
        order_item.quantity += 1
        order_item.save()
    cart =  cart_context(request)
    cart_count = len(cart['cart_items'])
    cart_total = cart['cart_total']
    messages.success(request, " mahsulot Savatchaga qo'shildi ")
    return JsonResponse({"status":200,'cart_count':cart_count, 'cart_total':cart_total})
    # return redirect(request.META.get("HTTP_REFERER", "home"))
    

def search_products(request):
    query = latin_to_cyrillic(request.GET.get('q', '')).strip().lower()

    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result')
    matched_items = []

    if result and query:
        result = json.loads(result.decode('utf-8'))
        print(query)
        print( result)
    for item in result:
        name = item.get('name', '')

        if query in name.lower():
            matched_items.append(item)
        else:
            score = fuzz.ratio(query, name)
            print(score)

            if score >= 20:
                matched_items.append(item)

    return JsonResponse(matched_items, safe=False)
