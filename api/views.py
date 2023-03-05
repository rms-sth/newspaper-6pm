from django.contrib.auth.models import Group, User
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    CategorySerializer,
    GroupSerializer,
    PostPublishSerializer,
    PostSerializer,
    TagSerializer,
    UserSerializer,
)
from newspaper_app.models import Category, Post, Tag

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


# # homework:
# 1. PostByCategory => done
# 2. PostByTag
# 3. PostPublish
