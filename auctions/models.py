from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max


class User(AbstractUser):
    pass

class listing(models.Model):

    categories = [
    ('EL', 'Electronics'),
    ('CL', 'Clothes'),
    ('TY', 'Toys'),
    ('HM', 'Home'),
    ('UT', 'Utility'),
    ('NS','Not specified')]

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    category = models.CharField(
        max_length=2,
        choices=categories,
        default='NS',
    )
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="userListings")
    startingPrice = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.99)])
    watched = models.ManyToManyField(User, related_name="watchlist",null=True,blank=True)
    currentBid = models.DecimalField(max_digits=8, decimal_places=2,default=0.99, validators=[MinValueValidator(0.99)])
    wineer = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name="wins")
    closed = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    imageUrl = models.URLField(null=True,blank=True)


    def save(self, *args, **kwargs):
        if self.closed:
            try:
                wineerBid = self.bids.order_by('price').reverse()[0]
                self.wineer = wineerBid.bider
            except IndexError:
                self.wineer = None
        super(listing,self).save(*args, **kwargs)

    def clean_closed(self):
        if self.wineer and not self.closed:
            raise ValidationError("can't reopen wineer already declared")

    def __str__(self):
        return self.title



class comment(models.Model):
    commenter = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    comment = models.TextField(max_length=500)
    product = models.ForeignKey(listing,on_delete=models.CASCADE, related_name="cmts")
    dateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} : {self.product.title}"



class bid(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=2,default=0)
    bider = models.ForeignKey(User,null=False,on_delete=models.CASCADE,related_name="userBids")
    listing = models.ForeignKey(listing ,null=False, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bider} / {self.listing.title} / ${self.price}"


    def clean(self):
        if self.listing.creator == self.bider:
            raise ValidationError("you cant bid on your listings")
        elif self.listing.startingPrice > self.price:
            raise ValidationError("your bid must be equal or larger than starting price")
        elif self.listing.currentBid >= self.price:
            raise ValidationError("your bid must be larger than current bid")

    def save(self, *args, **kwargs):
        self.bider.watchlist.add(self.listing)
        super(bid,self).save(*args, **kwargs)
