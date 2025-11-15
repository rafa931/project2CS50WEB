from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=63, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.title} - ${self.starting_bid} - Active: {self.is_active}"

class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} - {self.listing} - {self.amount} - {self.bid_time}"


class WacthList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatchlist")
    auctionItem = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="acutionItem")

    def __str__(self):
        return f"{self.user} - {self.auctionItem}"

class Commnets(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_user")
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} - {self.listing} - {self.comment_time} - {self.comment_text}"
