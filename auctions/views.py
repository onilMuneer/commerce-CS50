from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm , DecimalField
from .models import User , listing ,comment,bid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class NewListingForm(ModelForm):
    class Meta:
        model = listing
        fields = ['title', 'description', 'category','startingPrice','creator','imageUrl']

    def __init__(self, *args, **kwargs):
        super(NewListingForm, self).__init__(*args, **kwargs)
        self.fields['creator'].widget = forms.HiddenInput()

class NewBid(ModelForm):
    class Meta:
        model = bid
        fields = ['price','bider','listing']

    def __init__(self, *args, **kwargs):
        super(NewBid, self).__init__(*args, **kwargs)
        self.fields['bider'].widget = forms.HiddenInput()
        self.fields['listing'].widget = forms.HiddenInput()

# class NewComent(ModelForm):
#     class Meta:
#         model = comment
#         fields = ['title', 'description', 'category','startingPrice']

def index(request):
    return render(request, "auctions/index.html" , {"listings" : listing.objects.exclude(closed=True)})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def product(request, ID):
    if request.method == "POST":
        product = listing.objects.get(pk=ID)
        if "watch" in request.POST:
            if request.POST["watch"]=="Add to watchlist":
                request.user.watchlist.add(product)
            if request.POST["watch"]=="remove from watchlist":
                request.user.watchlist.remove(product)
            return HttpResponseRedirect(reverse("product",kwargs={"ID":product.id}))
        if "comment" in request.POST:
            com = request.POST["comment"]
            form = comment(commenter=request.user, comment=com, product=product)
            form.save()
            return HttpResponseRedirect(reverse("product",kwargs={"ID":product.id}))
        if "bid" in request.POST:
            bidForm = NewBid(request.POST)
            if bidForm.is_valid():
                product.currentBid = request.POST['price']
                product.save()
                bidForm.save()
                return HttpResponseRedirect(reverse("product",kwargs={"ID":product.id}))
            else:
                return render(request,"auctions/product.html",{"product":product,"bidForm":bidForm})

        if "close" in request.POST:
            if request.user == product.creator:
                product.closed = True
                product.save()
            return HttpResponseRedirect(reverse("product",kwargs={"ID":product.id}))
    else:
        try:
            return render(request,"auctions/product.html",{"product":listing.objects.get(id = ID),"bidForm":NewBid()})
        except:
            return HttpResponseNotFound('<h1>Page not found</h1>')

def NewListing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/newProduct.html", {"form": form})

    return render(request, "auctions/newProduct.html", {"form": NewListingForm()})

def watchlist(request):
    watchlist = request.user.watchlist.all
    return render(request, "auctions/watchlist.html",{"listings":watchlist})

def categories(request):
    return render(request,"auctions/categories.html",{"listings":listing.categories})

def category(request,category):
    cats = listing.categories
    for cat in cats:
        if cat[1] == category:
            filteredListings = listing.objects.filter(category=cat[0]).exclude(closed=True)
            return render(request,"auctions/category.html",{"listings":filteredListings})
