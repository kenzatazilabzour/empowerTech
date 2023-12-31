from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment
from .forms import CommentForm


# Create your views here.
def home(request):
  return render(request, 'home.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)


def posts_index(request):
  posts = Post.objects.all()
  return render(request, 'posts/index.html', {
    'posts': posts
  })

@login_required
def posts_detail(request, post_id):
  post = Post.objects.get(id=post_id)
  comment_form = CommentForm()
  return render(request, 'posts/detail.html', {
    'post': post, 'comment_form': comment_form
    })


class PostCreate(LoginRequiredMixin, CreateView):
  model = Post
  fields = ['title', 'description', 'category']

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
  model = Post
  fields = ['title', 'description', 'category']

class PostDelete(LoginRequiredMixin, DeleteView):
  model = Post
  success_url = '/posts'

@login_required
def add_comment(request, post_id):
  form = CommentForm(request.POST)
  if form.is_valid():
    new_comment = form.save(commit=False)
    new_comment.post_id = post_id
    new_comment.user = request.user 
    new_comment.save()
  return redirect('detail', post_id=post_id)


def delete_comment(request, post_id, comment_id):
  Comment.objects.get(id=comment_id).delete()
  return redirect('detail', post_id=post_id)
