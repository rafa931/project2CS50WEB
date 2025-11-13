from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import User, AuctionListings, Bids, WacthList


def index(request):
    listings = AuctionListings.objects.all()
    return render(request, "auctions/index.html",
                  {"listings": listings})


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

# add auction
def addAuction(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        aucTitle = request.POST.get("title")
        aucDesc = request.POST.get("desc")
        aucPrice = Decimal(request.POST.get("price"))
        aucURL = request.POST.get("url")
        aucCat = request.POST.get("cat")
        if not aucTitle or not aucDesc or not aucPrice:
            return render(request, "auctions/addAuction.html")
        else:
            new_auction = AuctionListings(
                title=aucTitle,
                description=aucDesc,
                starting_bid=aucPrice,
                image_url=aucURL,
                category=aucCat,
                owner=request.user
            )
            new_auction.save()
            return render(request, "auctions/addAuction.html")
    else:
        return render(request, "auctions/addAuction.html")
    
def listingView(request, listing_id):
    auctionItem = AuctionListings.objects.get(pk=listing_id)
    user = request.user
    is_in_watchList = False
    if user.is_authenticated:
        is_in_watchList = WacthList.objects.filter(user=user, auctionItem=auctionItem).exists()
    if request.method == "POST":
        if request.POST.get("rm"):  
            WacthList.objects.filter(user=user, auctionItem=auctionItem).delete()
            is_in_watchList = False
            return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "message": "You have remove this auction from your Watchlist"    
                          })
        elif request.POST.get("add"):
             watchListItem = WacthList(user=user, auctionItem=auctionItem)
             watchListItem.save()
             is_in_watchList = True
             return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "message": "You have added this auction to your Watchlist"    
                          })

    return render(request, "auctions/auction.html",
                  {
                      "listing": auctionItem,
                      "is_in_watchList": is_in_watchList
                  })

def watchListView(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("login"))
    
    elif request.user.is_authenticated:
        watchList = AuctionListings.objects.filter(acutionItem__user=request.user)
        return render(request, "auctions/watchlist.html",
                    {"watchlist": watchList})
        
    else:
        return HttpResponseRedirect(reverse("login"))