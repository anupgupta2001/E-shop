from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import *
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# def home(request):
#  return render(request, 'app/home.html')


class ProductViews(View):
    def get(self, request):
        totalitem = 0
        product=Product.objects.all()
        topwears = Product.objects.filter(url="topwears")
        bottomwears = Product.objects.filter(url="bottomwears")
        mobile = Product.objects.filter(url="mobiles")
        cats = Category.objects.all()
        print(topwears)
        print(bottomwears)
        print(mobile)
        print(cats)
        print(product)
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        context = {
           'product':product,
            "topwears": topwears,
            "bottomwears": bottomwears,
            "mobile": mobile,
            "totalitem": totalitem,
            "cats": cats,
        }

        return render(request, "app/home.html", context)


# def product_detail(request):
#  return render(request, 'app/productdetail.html')


class ProductDetailsView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)
            ).exists()

        context = {"product": product, "item_already_in_cart": item_already_in_cart}
        return render(request, "app/productdetail.html", context)


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    product = Product.objects.get(id=product_id)
    # print(product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('-id')
        print(cart)
        amount = 0.0
        shiping_amount = 40.00
        totle_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # print (cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
                totleamount = amount + shiping_amount
            return render(
                request,
                "app/addtocart.html",
                {"carts": cart, "totleamount": totleamount, "amount": amount},
            )
        else:
            return render(request, "app/empty.html")


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]

        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shiping_amount = 40.00

        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount

        data = {
            "quantity": c.quantity,
            "amount": amount,
            "totleamount": amount + shiping_amount,
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]

        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shiping_amount = 40.00

        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount

        data = {
            "quantity": c.quantity,
            "amount": amount,
            "totleamount": amount + shiping_amount,
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]

        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shiping_amount = 40.00

        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount

        data = {
            "amount": amount,
            "totleamount": amount + shiping_amount,
        }
        return JsonResponse(data)


def buy_now(request):
    return render(request, "app/buynow.html")


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, "app/address.html", {"add": add, "active": "btn-primary"})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user).order_by('-id')
    return render(request, "app/orders.html", {"order_plased": op})


# def change_password(request):
#  return render(request, 'app/changepassword.html')


def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(url="mobiles")
    # elif data == 'Realme' or data == 'Moto':
    #     mobiles = Product.objects.filter(url ='mobiles').filter(brand = data)
    elif data == "below":
        mobiles = Product.objects.filter(url="mobiles").filter(
            discounted_price__lt=10000
        )
    elif data == "above":
        mobiles = Product.objects.filter(url="mobiles").filter(
            discounted_price__gt=10000
        )
    return render(
        request,
        "app/mobile.html",
        {
            "mobiles": mobiles,
        },
    )


def login(request):
    return render(request, "app/login.html")


def customerregistration(request):
    return render(request, "app/customerregistration.html")


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations !! Registerd Successfully")
            form.save()
        return render(request, "app/customerregistration.html", {"form": form})


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_item = Cart.objects.filter(user=user)
    amount = 0.0
    shiping_amount = 70.00
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
    totalamount = amount + shiping_amount
    return render(
        request,
        "app/checkout.html",
        {"add": add, "totalamount": totalamount, "cart_item": cart_item},
    )


@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get("custid")
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(
            user=user, customer=customer, product=c.product, quantity=c.quantity
        ).save()
        c.delete()
    return redirect("orders")


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(
            request, "app/profile.html", {"form": form, "active": "btn-primary"}
        )

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data["name"]
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            zipcode = form.cleaned_data["zipcode"]
            reg = Customer(
                user=usr,
                name=name,
                locality=locality,
                city=city,
                state=state,
                zipcode=zipcode,
            )
            reg.save()
            messages.success(request, "Congratulation !! Profile Updated Successfully")
        return render(
            request, "app/profile.html", {"form": form, "active": "btn-primary"}
        )
