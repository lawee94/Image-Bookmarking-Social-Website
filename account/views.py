from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import LoginForm, UserForm, UserEditForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CustomUser, Contact
from django.contrib import messages
from common.decorators import ajax_required
from actions.utils import create_action
from actions.models import Action

def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(request,username=cd['username'], password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponse("Authentication Succesful")
                    else:
                        return HttpResponse("DIsabled Account")
                else:
                    return HttpResponse("Invalid Login")
        else:
            form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':    
        form = UserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)
            user.set_password(cd['password'])
            user.save()
            create_action(user, 'has created an account')
            return render(request,'register_done.html',{'user': user})
    else:
        form = UserForm()
    return render(request,'register.html',{'form': form})

@login_required  
def update_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Updated Succesfully')
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = UserEditForm(instance=user)
    return render(request,'update.html',{'form': form})

@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    print(actions)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions[:10]
    return render(request, 'dashboard.html', {'section': "dashboard", 'actions': actions })

@login_required
def user_list(request):
    users = CustomUser.objects.filter(is_active=True)
    return render(request,'user/list.html', {'section': 'people', 'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(CustomUser, username=username, is_active=True)
    return render(request, 'user/detail.html', {'section': 'people', 'user': user})

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = CustomUser.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                create_action(request.user, 'unfollow', user)
            return JsonResponse({'status':'ok'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status':'ko'})
    return JsonResponse({'status':'ko'})