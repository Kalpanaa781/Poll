from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Poll, Choice, Vote
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('poll_list')
        else:
            return render(request, 'pollapp/login.html', {'error': 'Invalid username or password'})
    return render(request, 'pollapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'pollapp/register.html', {'form': form})


@login_required
def poll_list(request):
    polls = Poll.objects.all()
    return render(request, 'pollapp/poll_list.html', {'polls': polls})


@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'pollapp/poll_detail.html', {'poll': poll})


@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.method == 'POST':
        try:
            choice_id = int(request.POST['choice'])
            choice = poll.choices.get(id=choice_id)
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'pollapp/poll_detail.html', {
                'poll': poll,
                'error': "You didn't select a valid choice."
            })

        # Save vote
        Vote.objects.create(user=request.user, poll=poll, choice=choice, voted_at=timezone.now())
        choice.votes += 1
        choice.save()

        return redirect('poll_result', poll_id=poll.id)


@login_required
def poll_result(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'pollapp/poll_result.html', {'poll': poll})
