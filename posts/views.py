import logging

from django.db.models import Count, Q
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CommentForm, PostForm
from .models import Post, Author, PostView
from marketing.forms import EmailSignupForm
from marketing.models import Signup

logger = logging.getLogger(__name__)


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def get_category_count():
    return Post.objects.values("categories__title").annotate(Count("categories__title"))


class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        queryset = Post.objects.all()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(overview__icontains=query)
            ).distinct()
            logger.debug("Search '%s' returned %d results", query, queryset.count())
        return render(request, "search_results.html", {"queryset": queryset, "query": query})


# URL alias so 'search' name still works
search = SearchView.as_view()


class IndexView(View):
    def get(self, request, *args, **kwargs):
        featured = Post.objects.filter(featured=True)
        latest = Post.objects.order_by("-timestamp")[:3]
        context = {
            "object_list": featured,
            "latest": latest,
            "form": EmailSignupForm(),
        }
        return render(request, "index.html", context)

    def post(self, request, *args, **kwargs):
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if Signup.objects.filter(email=email).exists():
                messages.warning(request, "You are already subscribed.")
            else:
                Signup.objects.create(email=email)
                messages.success(request, "Welcome aboard! You have successfully subscribed.")
                logger.info("Newsletter signup from home page: %s", email)
        else:
            messages.error(request, "Please enter a valid email address.")
        return redirect("home")


class PostListView(ListView):
    model = Post
    template_name = "blog.html"
    context_object_name = "queryset"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["most_recent"] = Post.objects.order_by("-timestamp")[:3]
        context["page_request_var"] = "page"
        context["category_count"] = get_category_count()
        context["form"] = EmailSignupForm()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(user=self.request.user, post=obj)
            logger.debug("View recorded: user=%s post=%d", self.request.user.username, obj.pk)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["most_recent"] = Post.objects.order_by("-timestamp")[:3]
        context["page_request_var"] = "page"
        context["category_count"] = get_category_count()
        context["form"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to post a comment.")
            return redirect(reverse("account_login"))
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            messages.success(request, "Your comment has been posted.")
            logger.info("Comment by %s on post %d", request.user.username, post.pk)
            return redirect(reverse("post-detail", kwargs={"pk": post.pk}))
        messages.error(request, "Could not post comment. Please try again.")
        return redirect(reverse("post-detail", kwargs={"pk": self.get_object().pk}))


class PostCreateView(CreateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create"
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        post = form.save()
        messages.success(self.request, "Post created successfully.")
        logger.info("Post created: '%s' by %s", post.title, self.request.user.username)
        return redirect(reverse("post-detail", kwargs={"pk": post.pk}))

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PostUpdateView(UpdateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update"
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        post = form.save()
        messages.success(self.request, "Post updated successfully.")
        logger.info("Post updated: '%s' by %s", post.title, self.request.user.username)
        return redirect(reverse("post-detail", kwargs={"pk": post.pk}))

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PostDeleteView(DeleteView):
    model = Post
    success_url = "/blog"
    template_name = "post_confirm_delete.html"

    def form_valid(self, form):
        post = self.get_object()
        logger.info("Post deleted: '%s' by %s", post.title, self.request.user.username)
        messages.success(self.request, "Post deleted successfully.")
        return super().form_valid(form)
