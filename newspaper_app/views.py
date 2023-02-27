from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from newspaper_app.forms import (
    CommentForm,
    TagForm,
    ContactForm,
    NewsletterForm,
    PostForm,
    CategoryForm
)
from newspaper_app.models import Category, Post, Tag, Category


class HomeView(ListView):
    model = Post
    template_name = "aznews/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="active", published_at__isnull=False
    ).order_by("-published_at")[:5]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["featured_post"] = (
            Post.objects.filter(status="active", published_at__isnull=False)
            .order_by("-views_count")
            .first()
        )
        context["featured_posts"] = Post.objects.filter(
            status="active", published_at__isnull=False
        ).order_by("-views_count")[2:5]
        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            status="active",
            published_at__isnull=False,
            published_at__gte=one_week_ago,
        ).order_by("-published_at")[:7]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status="active", published_at__isnull=False)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # get current post
        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        # id => 3
        # 2, 1
        context["previous_post"] = (
            Post.objects.filter(
                status="active", published_at__isnull=False, id__lt=obj.id
            )
            .order_by("-id")
            .first()
        )
        # id => 3
        # 4, 5, 6, 7, 8
        context["next_post"] = (
            Post.objects.filter(
                status="active", published_at__isnull=False, id__gt=obj.id
            )
            .order_by("id")
            .first()
        )
        context["recent_posts"] = Post.objects.filter(
            status="active", published_at__isnull=False
        ).order_by("-views_count")[:5]
        return context


class PostListView(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="active", published_at__isnull=False
    ).order_by("-published_at")
    paginate_by = 1


class PostByCategoryView(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["cat_id"],
        ).order_by("-published_at")
        return queryset


class PostByTagView(ListView):
    model = Post
    template_name = "aznews/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status="active",
            published_at__isnull=False,
            tag=self.kwargs["tag_id"],
        ).order_by("-published_at")
        return queryset


class AboutView(TemplateView):
    template_name = "aznews/about.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["posts"] = Post.objects.filter(
            status="active", published_at__isnull=False
        ).order_by("-published_at")[:5]
        return context


class PostSearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query")
        post_list = Post.objects.filter(
            (Q(status="active") & Q(published_at__isnull=False))
            & (Q(title__icontains=query) | Q(content__icontains=query)),
        )
        # pagination in function based views
        page = request.GET.get("page", 1)
        paginator = Paginator(post_list, 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(
            request,
            "aznews/search_list.html",
            {"page_obj": posts, "query": query},
        )


class ContactView(View):
    template_name = "aznews/contact.html"
    form_class = ContactForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Successfully submitted your query. We will contact you soon."
            )
        else:
            messages.error(request, "Cannot submit your query. Something went wrong.")

        return render(
            request,
            self.template_name,
            {"form": form},
        )


class NewsletterView(View):
    form_class = NewsletterForm

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":  # if ajax ho vane forms save gar
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully submitted to our newsletter.",
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Something went wrong.",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an ajax request.",
                },
                status=400,
            )


class CommentView(View):
    form_class = CommentForm
    template_name = "aznews/detail.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        post = request.POST["post"]  # get id of post
        if form.is_valid():
            form.save()
            return redirect("post-detail", post)
        else:
            post = Post.objects.get(pk=post)
            return render(
                request,
                self.template_name,
                {"post": post, "form": form},
            )


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "news_admin/draft_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published_at__isnull=True).order_by("-published_at")


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        messages.success(self.request, "Post was successfully deleted")
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "news_admin/post_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post was successfully created.")
        return super().form_valid(form)


class PostPublishView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        # post = Post.objects.get(pk=pk)
        post = get_object_or_404(Post, pk=pk)
        post.published_at = timezone.now()
        post.save()
        messages.success(request, "Post was successfully published")
        return redirect("post-detail", post.pk)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "news_admin/post_create.html"
    success_url = reverse_lazy("post-list")


def handler404(request, exception, template_name="404.html"):
    return render(request, template_name, status=404)


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "news_admin/draft_detail.html"
    context_object_name = "post"


##################### Tag  CRUD ###########################


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "news_admin/tag_list.html"
    context_object_name = "tags"


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "news_admin/tag_create.html"
    success_url = reverse_lazy("tag-list")


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "news_admin/tag_create.html"
    success_url = reverse_lazy("tag-list")


class TagDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        messages.success(self.request, "Tag was successfully deleted")
        return redirect("tag-list")


##################### Category  CRUD ###########################


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "news_admin/category_list.html"
    context_object_name = "categorys"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "news_admin/category_create.html"
    success_url = reverse_lazy("category-list")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "news_admin/category_create.html"
    success_url = reverse_lazy("category-list")


class CategoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        messages.success(self.request, "Category was successfully deleted")
        return redirect("category-list")
