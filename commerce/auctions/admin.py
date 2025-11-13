from django.contrib import admin
from .models import AuctionListings, User, Bids, WacthList

class AuctionListingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'starting_bid', 'is_active', 'owner', 'created_at')
    search_fields = ('title', 'description', 'category', 'owner__username')
    list_filter = ('is_active', 'category', 'created_at')

# Register your models here.
admin.site.register(AuctionListings, AuctionListingsAdmin)
admin.site.register(User)
admin.site.register(Bids)
admin.site.register(WacthList)
