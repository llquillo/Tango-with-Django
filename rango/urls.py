from django.urls import path 
from django.shortcuts import redirect, render
from rango import views

from django.views import View
from registration.backends.simple.views import RegistrationView 
from django.urls import reverse


class AboutView(View):
    def get(self, request):
        context_dict = {}
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context_dict)

class MyRegistrationView(RegistrationView): 
    def get_success_url(self, user):
        return reverse('rango:register_profile')

app_name = 'rango'
urlpatterns = [
    path('', views.index, name='index'),
    # path('about/', views.about, name='about'),
    path('about/', views.AboutView.as_view(), name='about'),
    # path('category/', views.show_category, name='category'),
    path('category/<slug:category_name_slug>/',
         views.show_category, name='show_category'),
    # path('add_category/', views.add_category, name='add_category'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', 
    views.add_page, 
    name='add_page'),
    # path('register/', views.register, name='register'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('goto/', views.goto_url, name='goto'),
    path('search/', views.search, name='googlesearch'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    path('like_category/', views.LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),

]