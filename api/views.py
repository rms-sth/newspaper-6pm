from django.contrib.auth.models import Group, User
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status, viewsets, exceptions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GroupSerializer,
    NewsletterSerializer,
    PostPublishSerializer,
    PostSerializer,
    TagSerializer,
    UserSerializer,
)
from newspaper_app.models import Category, Comment, Newsletter, Post, Tag

# application developers
# framework / library developers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            qs = qs.filter(status="active", published_at__isnull=False)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                permissions.AllowAny(),
            ]
        return super().get_permissions()


# class PostByCategoryListViewSet(ListAPIView):
#     serializer_class = PostSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         qs = Post.objects.filter(
#             status="active", published_at__isnull=False, category=self.kwargs["cat_id"]
#         )
#         return qs


class PostByTagListViewSet(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(
            status="active", published_at__isnull=False, tag=self.kwargs["tag_id"]
        )
        return qs


class PostByCategoryListViewSet(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(
            status="active", published_at__isnull=False, category=self.kwargs["cat_id"]
        )
        return qs


class DraftListViewSet(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status="active", published_at__isnull=True)
        return qs


class PostPublishViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostPublishSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data

            # publish the post
            post = Post.objects.get(pk=data["post"])
            post.published_at = timezone.now()
            post.save()

            serialized_post = PostSerializer(post)
            return Response(
                {
                    "success": "Post was successfully published.",
                    "data": serialized_post.data,
                },
                status=status.HTTP_200_OK,
            )


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    1. allows admin to view newsletter.
    2. allows anonymous user to create newsletter
    3. does not support update method
    """

    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                permissions.IsAuthenticated(),
            ]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)


class CommentViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer

    def get(self, request, post_id, *args, **kwargs):
        comments = Comment.objects.filter(post=post_id).order_by("-created_at")
        serializer = self.serializer_class(comments, many=True)
        return Response(
            {
                "success": "Comment was successfully fetched.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, post_id, *args, **kwargs):
        request.data.update({"post": post_id})
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "success": "Comment was successfully created.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )


# # homework:
# 1. ContactUs
