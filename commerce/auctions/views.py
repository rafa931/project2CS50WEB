from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import User, AuctionListings, Bids, WacthList, Commnets


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
        try:
            aucPrice = Decimal(request.POST.get("price"))
        except:
            return render(request, "auctions/addAuction.html", 
                          {"message": "The price must be a number"})
        aucURL = request.POST.get("url")
        aucCat = request.POST.get("cat")
        if not aucTitle or not aucDesc or not aucPrice:
            return render(request, "auctions/addAuction.html",
                          {"message": "There are empty fields"})
        elif -aucPrice.as_tuple().exponent > 2 or -aucPrice.as_tuple().exponent == 1:
            return render(request, "auctions/addAuction.html",
                          {"message": "The price must have two decimal places or none"})
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
            return render(request, "auctions/addAuction.html", 
                          {"message": "The element was added - you can add another one."})
    else:
        return render(request, "auctions/addAuction.html")
    
def listingView(request, listing_id):
    auctionItem = AuctionListings.objects.get(pk=listing_id)
    user = request.user
    is_in_watchList = False
    check_user = False
    getBid = Bids.objects.filter(listing=auctionItem).order_by('-amount').first()
    if getBid:
        auctionItem.starting_bid = getBid.amount    

    if user.is_authenticated:
        check_user = AuctionListings.objects.filter(pk=listing_id, owner=user).exists()
        is_in_watchList = WacthList.objects.filter(user=user, auctionItem=auctionItem).exists()

    comments = Commnets.objects.filter(listing=auctionItem).order_by('-comment_time')
    
    if request.method == "POST" and user.is_authenticated: 
        if request.POST.get("comment"):
            comment_text = request.POST.get("comment")
            if not comment_text:
                return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "messagee": "You cant add an empty comment",
                            "comments": comments
                          })
            
            new_comment = Commnets(
                commenter=user,
                listing=auctionItem,
                comment_text=comment_text
            )
            new_comment.save()

            return HttpResponseRedirect(reverse("listingView", args=(listing_id,)))

        if check_user and request.POST.get("rm-item"):
            auctionItem.delete()
            return HttpResponseRedirect(reverse("myAuctions"))

        elif check_user and request.POST.get("close-item"):
            auctionItem.is_active = False
            auctionItem.save()
            return HttpResponseRedirect(reverse("myAuctions"))
        
        elif check_user:
            return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "messagee": "You cant add this item to watchlist because is yours",
                            "comments": comments
                          })
        
        if request.POST.get("bid") and auctionItem.is_active:
            newbid = Decimal(request.POST.get("bid"))
            check_bid = Bids.objects.filter(listing=auctionItem).exists()
            # if bid exists already
            newBidObj = Bids(amount=newbid, listing=auctionItem, bidder=user)
            if check_bid:
                currentPriceBid = Bids.objects.filter(listing=auctionItem).order_by('-amount').first()
                if newbid <= currentPriceBid.amount:
                    return render(request, "auctions/auction.html",
                                  {"more": "You need to bid a higer price that already has",
                                    "listing": auctionItem,
                                    "comments": comments})
                else:
                    newBidObj.save()
                    return HttpResponseRedirect(reverse("listingView", args=(listing_id,)))
            # if there are no bids yet on the auction
            else:
                if newbid < auctionItem.starting_bid:
                    return render(request, "auctions/auction.html",
                                  {"more": "You need to bid a higer or equal price, that already has",
                                    "listing": auctionItem,
                                    "comments": comments})
                else:
                    newBidObj.save()
                    return render(request, "auctions/auction.html",
                                  {"more": "Your bid has been placed",
                                    "listing": auctionItem,
                                    "comments": comments})

        if request.POST.get("rm"):  
            WacthList.objects.filter(user=user, auctionItem=auctionItem).delete()
            is_in_watchList = False
            return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "messagee": "You have remove this auction from your Watchlist",
                            "comments": comments
                          })
        elif request.POST.get("add") and auctionItem.is_active:
             watchListItem = WacthList(user=user, auctionItem=auctionItem)
             watchListItem.save()
             is_in_watchList = True
             return render(request, "auctions/auction.html", 
                          {
                            "listing": auctionItem,
                            "is_in_watchList": is_in_watchList,
                            "messagee": "You have added this auction to your Watchlist",
                            "comments": comments
                          })

    
    return render(request, "auctions/auction.html",
                  {
                      "listing": auctionItem,
                      "is_in_watchList": is_in_watchList,
                      "check_user": check_user,
                      "message": "You added this item",
                      "active" : auctionItem.is_active,
                      "comments": comments
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

# my Auctions
def myAuctions(request):
    myAuctions = AuctionListings.objects.filter(owner=request.user)
    return render(request, "auctions/myAuction.html",
                  {"list": myAuctions})


def manageComments(request, listing_id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("login"))
    
    comment = Commnets.objects.get(pk=listing_id)
    user = request.user

    if request.method == "POST" and comment.commenter == user:
        if request.POST.get("delete-comment"):
            comment.delete()
            return HttpResponseRedirect(reverse("listingView", args=(comment.listing.id,)))
        elif request.POST.get("edit-comment"):
            comment_text = comment.comment_text
            is_in_watchList = WacthList.objects.filter(user=user, auctionItem=comment.listing).exists()
            print(comment_text)
            return render(request, "auctions/auction.html",
                          { "listing": comment.listing,
                           "comment": comment,
                           "comment_text": comment_text,
                           "is_in_watchList": is_in_watchList,
                           "active": comment.listing.is_active
                           })
        elif request.POST.get("edit-new-comm"):
            comment.comment_text  = request.POST.get("edit-new-comm")
            comment.save()
            return HttpResponseRedirect(reverse("listingView", args=(comment.listing.id,)))

    return HttpResponseRedirect(reverse("index"))


# edit acution
def editAuction(request, listing_id):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("login"))
    
    auction_item = AuctionListings.objects.get(pk=listing_id)
    user = request.user
    if auction_item.owner != user:
        return HttpResponseRedirect(reverse("index"))
    
    if request.method == "POST" and auction_item.owner == user:
        pass

    return render(request, "auction/editAuction.html",{
        
    })