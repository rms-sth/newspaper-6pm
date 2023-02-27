from django import forms
from django_summernote.widgets import SummernoteInplaceWidget, SummernoteWidget

from newspaper_app.models import Category, Comment, Contact, Newsletter, Post, Tag


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "featured_image", "status", "category", "tag")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter title of your post...",
                    "required": True,
                }
            ),
            "content": SummernoteWidget(),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "tag": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = "__all__"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"