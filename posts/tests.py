from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Post, Author, Category, Comment, PostView
from .views import get_author, get_category_count

User = get_user_model()


def make_user(username="testuser", is_staff=False):
    user = User.objects.create_user(username=username, password="testpass123", email=f"{username}@test.com")
    user.is_staff = is_staff
    user.save()
    return user


def make_author(user):
    return Author.objects.create(user=user)


def make_category(title="Data Engineering"):
    return Category.objects.create(title=title)


def make_post(author, title="Test Post", featured=False):
    return Post.objects.create(
        title=title,
        overview="An overview of the post.",
        content="Full content here.",
        author=author,
        featured=featured,
    )


class GetAuthorTest(TestCase):
    def test_returns_author_when_exists(self):
        user = make_user()
        author = make_author(user)
        result = get_author(user)
        self.assertEqual(result, author)

    def test_returns_none_when_no_author(self):
        user = make_user()
        result = get_author(user)
        self.assertIsNone(result)


class GetCategoryCountTest(TestCase):
    def setUp(self):
        user = make_user()
        author = make_author(user)
        cat = make_category("ETL")
        post = make_post(author)
        post.categories.add(cat)

    def test_returns_queryset_with_counts(self):
        result = list(get_category_count())
        self.assertGreater(len(result), 0)
        self.assertIn("categories__title", result[0])
        self.assertIn("categories__title__count", result[0])


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = make_user()
        self.author = make_author(user)

    def test_get_renders_homepage(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_context_has_form_and_lists(self):
        response = self.client.get(reverse("home"))
        self.assertIn("form", response.context)
        self.assertIn("object_list", response.context)
        self.assertIn("latest", response.context)

    def test_featured_posts_in_context(self):
        make_post(self.author, title="Featured", featured=True)
        make_post(self.author, title="Not Featured", featured=False)
        response = self.client.get(reverse("home"))
        featured = list(response.context["object_list"])
        self.assertEqual(len(featured), 1)
        self.assertEqual(featured[0].title, "Featured")


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = make_user()
        author = make_author(user)
        make_post(author, title="Data Pipeline Design")
        make_post(author, title="Machine Learning Ops")

    def test_search_returns_matching_posts(self):
        response = self.client.get(reverse("search"), {"q": "Data"})
        self.assertEqual(response.status_code, 200)
        qs = response.context["queryset"]
        self.assertEqual(qs.count(), 1)
        self.assertIn("Data", qs.first().title)

    def test_empty_query_returns_all(self):
        response = self.client.get(reverse("search"), {"q": ""})
        self.assertEqual(response.context["queryset"].count(), 2)

    def test_no_results_for_unknown_term(self):
        response = self.client.get(reverse("search"), {"q": "zzznomatch"})
        self.assertEqual(response.context["queryset"].count(), 0)


class PostListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = make_user()
        author = make_author(user)
        for i in range(6):
            make_post(author, title=f"Post {i}")

    def test_renders_blog_template(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog.html")

    def test_pagination_limits_per_page(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(len(response.context["queryset"]), 4)

    def test_context_has_sidebar_data(self):
        response = self.client.get(reverse("post-list"))
        self.assertIn("most_recent", response.context)
        self.assertIn("category_count", response.context)


class PostDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        author = make_author(self.user)
        self.post = make_post(author)

    def test_get_renders_post_template(self):
        response = self.client.get(reverse("post-detail", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "post.html")

    def test_authenticated_view_creates_postview(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.get(reverse("post-detail", kwargs={"pk": self.post.pk}))
        self.assertTrue(PostView.objects.filter(user=self.user, post=self.post).exists())

    def test_anonymous_view_does_not_create_postview(self):
        self.client.get(reverse("post-detail", kwargs={"pk": self.post.pk}))
        self.assertFalse(PostView.objects.filter(post=self.post).exists())

    def test_post_comment_requires_auth(self):
        response = self.client.post(
            reverse("post-detail", kwargs={"pk": self.post.pk}),
            {"content": "Nice post!"},
        )
        # Anonymous users are redirected to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_authenticated_comment_saved(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.post(
            reverse("post-detail", kwargs={"pk": self.post.pk}),
            {"content": "Great post!"},
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(is_staff=True)
        self.author = make_author(self.user)
        self.cat = make_category()

    def test_get_renders_form(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("post-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "post_create.html")

    def test_create_post_redirects_to_detail(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("post-create"),
            {
                "title": "New Post",
                "overview": "Overview text",
                "content": "Content text",
                "categories": [self.cat.pk],
                "featured": False,
            },
        )
        self.assertRedirects(response, reverse("post-detail", kwargs={"pk": Post.objects.last().pk}))


class PostUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(is_staff=True)
        self.author = make_author(self.user)
        self.post = make_post(self.author)
        self.cat = make_category()

    def test_update_post(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("post-update", kwargs={"pk": self.post.pk}),
            {
                "title": "Updated Title",
                "overview": "Updated overview",
                "content": "Updated content",
                "categories": [self.cat.pk],
                "featured": True,
            },
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")


class PostDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(is_staff=True)
        self.author = make_author(self.user)
        self.post = make_post(self.author)

    def test_delete_removes_post(self):
        self.client.login(username="testuser", password="testpass123")
        pk = self.post.pk
        self.client.post(reverse("post-delete", kwargs={"pk": pk}))
        self.assertFalse(Post.objects.filter(pk=pk).exists())


class PostModelTest(TestCase):
    def setUp(self):
        user = make_user()
        self.author = make_author(user)
        self.post = make_post(self.author)

    def test_str_returns_title(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertIn(str(self.post.pk), url)

    def test_comment_count_property(self):
        user = make_user("commenter")
        Comment.objects.create(user=user, post=self.post, content="Comment 1")
        Comment.objects.create(user=user, post=self.post, content="Comment 2")
        self.assertEqual(self.post.comment_count, 2)

    def test_view_count_property(self):
        user = make_user("viewer")
        PostView.objects.create(user=user, post=self.post)
        self.assertEqual(self.post.view_count, 1)

    def test_get_comments_ordered_by_newest_first(self):
        user = make_user("comm2")
        c1 = Comment.objects.create(user=user, post=self.post, content="First")
        c2 = Comment.objects.create(user=user, post=self.post, content="Second")
        comments = list(self.post.get_comments)
        self.assertEqual(comments[0].pk, c2.pk)
