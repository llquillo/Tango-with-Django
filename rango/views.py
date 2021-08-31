from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from registration.backends.simple.views import RegistrationView 
from django.urls import reverse

from datetime import datetime

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page, UserProfile

from django.contrib.auth.models import User 
from rango.models import UserProfile

from django.http import HttpResponse

from googleapiclient.discovery import build
import pprint

my_api_key = "AIzaSyBzCi7V_dW7NsbrNPu4YzXLI2OJ6kBlKG0"
my_cse_id = "6bcfc873145ebdc58"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

class SearchAddPageView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')

        p = Page.objects.get_or_create(category=category,
                                            title=title,
                                            url=url)
        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})


def get_category_list(max_results=0, starts_with=''): 
    category_list = []
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results] 
    return category_list

class CategorySuggestionView(View): 
    def get(self, request):
        suggestion = request.GET['suggestion']
        category_list = get_category_list(max_results=8,
                                          starts_with=suggestion)
        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')
        return render(request, 'rango/categories.html',
                    {'categories': category_list})


class LikeCategoryView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        category_id = request.GET['category_id'] 
        try:
            category = Category.objects.get(id=int(category_id)) 
        except Category.DoesNotExist:
            return HttpResponse(-1) 
        except ValueError:
            return HttpResponse(-1) 
        category.likes = category.likes + 1
        category.save()
        return HttpResponse(category.likes)

class AboutView(View):
    def get(self, request):
        context_dict = {}
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context_dict)

class AddCategoryView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required) 
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid(): 
            form.save(commit=True) 
            return index(request)
        else: 
            print(form.errors)
        return render(request, 'rango/add_category.html', {'form': form})

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist: 
            return None

        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': userprofile.website, 
                                'picture': userprofile.picture}) 
        return (user, userprofile, form)

    @method_decorator(login_required) 
    def get(self, request, username):
        try:
            (user, userprofile, form) = self.get_user_details(username)
        except TypeError:
            return redirect('rango:index')

        context_dict = {'userprofile': userprofile, 
                        'selecteduser': user,
                        'form': form}
        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required) 
    def post(self, request, username):
        try:
            (user, userprofile, form) = self.get_user_details(username)
        except TypeError:
            return redirect('rango:index')

        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else: 
            print(form.errors)

        context_dict = {'userprofile': userprofile,
                        'selecteduser': user,
                        'form': form}
        return render(request, 'rango/profile.html', context_dict)



def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list


    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)

    return response

def about(request):
    # prints out whether the method is a GET or a POST
    print(request.method)
    # prints out the user name, if no one is logged in it prints `AnonymousUser` 
    print(request.user)

    request.session.set_test_cookie()
    if request.session.test_cookie_worked(): 
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass # to the template rendering engine. 
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception. 
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list. 
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
    
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists. 
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us. 
        context_dict['category'] = None
        context_dict['pages'] = None

    context_dict['home'] = '/rango/'

    if request.method == 'POST':
        if request.method == 'POST':
            query = request.POST['query'].strip()
            if query:
                context_dict['result_list'] = run_query(query)

    return render(request, 'rango/category.html', context=context_dict)


def add_category(request): 
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
                # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database. 
            cat = form.save(commit=True)
            print(cat, cat.slug)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page # Then we can direct the user back to the index page.
            return index(request)
        else:
        # The supplied form contained errors - # just print them to the terminal. 
            print(form.errors)

    # Will handle the bad form, new form, or no form supplied cases. 
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug): 
    def clean(self):
        cleaned_data = self.cleaned_data 
        url = cleaned_data.get('url')
        # If url is not empty and doesn't start with 'http://', # then prepend 'http://'.
        if url and not url.startswith('http://'):
                    url = 'http://' + url
                    cleaned_data['url'] = url
        return cleaned_data

    try:
        category = Category.objects.get(slug=category_name_slug) 
    except Category.DoesNotExist:
            category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST) 
        if form.is_valid():
            if category:
                page = form.save(commit=False) 
                page.category = category 
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', 
                kwargs={'category_name_slug': category_name_slug}))
    else: 
        print(form.errors)
        context_dict = {'form':form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

@login_required
def register_profile(request): 
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False) 
            user_profile.user = request.user 
            user_profile.save()
            return redirect('rango:index') 
        else:
            print(form.errors) 
    
    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)



def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                profile.save()
                registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password)) 
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

@login_required
def register_profile(request): 
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False) 
            user_profile.user = request.user 
            user_profile.save()
            return redirect('rango:index') 
        else:
            print(form.errors) 

    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # response.set_cookie('last_visit', str(datetime.now()))
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit']= last_visit_cookie

    request.session['visits'] = visits

# def search(request):
#     result_list = []
#     if request.method == 'POST':
#         query = request.POST['query'].strip() 
#         if query:
#                     # Run our Bing function to get the results list!
#         # result_list = run_query(query)
#             return render(request, 'rango/search.html', {'result_list': result_list})

def search(request):
    # if request.method == 'GET':
    #     query = request.GET('q')
    #     if query:
    return render(request, 'rango/search.html')

def results(request):
    return render(request, 'rango/results.html')

def goto_url(request):
    if request.method == 'GET':
        page_id = request.GET.get('page_id') 
        try:
            selected_page = Page.objects.get(id=page_id) 
        except Page.DoesNotExist:
            return redirect(reverse('rango:index')) 

        selected_page.views = selected_page.views + 1
        selected_page.save()
        return redirect(selected_page.url) 

    return redirect(reverse('rango:index'))

class ListProfilesView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, 'rango/list_profiles.html',
                      {'userprofile_list': profiles})