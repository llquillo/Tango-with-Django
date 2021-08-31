from django import forms
from django.conf.urls import url 
from django.contrib.auth.models import User 
from rango.models import UserProfile

from rango.models import Category, Page, User, UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
# An inline class to provide additional information on the form.
    class Meta:
    # Provide an association  between the ModelForm and a model
        model = Category
        fields = ('name',)
    
class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                                help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,
                        help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
    # Provide an association between the ModelForm and a model 
        model = Page
    # What fields do we want to include in our form?
    # This way we don't need every field in the model present.
    # Some fields may allow NULL values; we may not want to include them. # Here, we are hiding the foreign key.
    # we can either exclude the category field from the form,
        exclude = ('category',)
# or specify the fields to include (don't include the category field). #fields = ('title', 'url', 'views')

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta: 
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm): 
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


# class PageForm(forms.ModelForm):
#     category = forms.CharField(widget=forms.HiddenInput())
#     title = forms.CharField(max_length=128, help_text="Please enter page title.")
#     url = forms.CharField(help_text="Please enter URL.")
#     views = forms.IntegerField(widget=forms.HiddenInput())

#     class Meta:
#         model = Page
#         fields = ('category','title','url','views')

