from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.NewListing, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:ID>", views.product , name="product"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category")
]
