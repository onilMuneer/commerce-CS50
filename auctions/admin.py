from django.contrib import admin
from .models import listing,comment,bid



class listingAdmin(admin.ModelAdmin):
    readonly_fields = ('creator','get_comments')

    def get_comments(self, obj):
        return obj.cmts.count()

    # get_commenter.admin_order_field = 'post_stats__view_count'
    get_comments.short_description = 'comments count'


# Register your models here.
admin.site.register(listing, listingAdmin)
admin.site.register(comment)
admin.site.register(bid)
