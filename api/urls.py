from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"posts", views.PostViewSet, basename="posts")
router.register(r"newsletter", views.NewsletterViewSet, basename="newsletter")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "post-by-category/<int:cat_id>/",
        views.PostByCategoryListViewSet.as_view(),
        name="post-by-category-api",
    ),
    path(
        "post-by-tag/<int:tag_id>/",
        views.PostByTagListViewSet.as_view(),
        name="post-by-tag-api",
    ),
    path(
        "draft-list/",
        views.DraftListViewSet.as_view(),
        name="draft-list-api",
    ),
    path(
        "post-publish/",
        views.PostPublishViewSet.as_view(),
        name="post-publish-api",
    ),
    path(
        "post/<int:post_id>/comments/",
        views.CommentViewSet.as_view(),
        name="comments-api",
    ),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
]
