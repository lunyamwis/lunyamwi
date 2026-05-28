from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from posts.views import (
    search,
    IndexView,
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
)
from marketing.views import email_list_signup

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="home"),
    path("blog/", PostListView.as_view(), name="post-list"),
    path("search/", search, name="search"),
    path("email-signup/", email_list_signup, name="email-list-signup"),
    path("create/", PostCreateView.as_view(), name="post-create"),
    path("post/<pk>/", PostDetailView.as_view(), name="post-detail"),
    path("post/<pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("post/<pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
