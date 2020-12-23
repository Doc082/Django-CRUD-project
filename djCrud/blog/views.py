import datetime
import redis
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .forms import UserRegistration, PostForm
from .models import Post


User = get_user_model()

client = redis.StrictRedis(host='127.0.0.1', port=6379, password='secret',db=0)

def index(request):
    message=False
    ip = request.META.get('REMOTE_ADDR')
    if request.user.is_authenticated:
        if client.get(request.user.username):
            if client.get(request.user.username).decode("utf-8") != ip:
                client.set(request.user.username, ip)
                message = "Il tuo numer IP è diverso dall'ultimo accesso"
        else:
            client.set(request.user.username, ip)

    return render(request, 'blog/index.html', {'message': message})


def newUser(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('/')
    else:
        form = UserRegistration()
    return render(request, 'registration/new_user.html', {'form': form})

@login_required
def newPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def postEdit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method=='POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def postDetail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def postView(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/posts_view.html', {'posts': posts})

@staff_member_required()
def adminPage(request, pk=0):
    message=False
    if pk>0:
        Post.objects.filter(pk=pk).delete()
        message = 'Post cancellato con successo'
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    postNumber = Post.objects.count()
    authorsName = Post.objects.all()
    numberPostAuthor = {}
    for authorName in authorsName:
       num = Post.objects.filter(author=authorName.author).count()
       temp = {authorName.author: num}
       numberPostAuthor.update(temp)

    authorNumber = len(numberPostAuthor)
    return render(request, 'blog/admin_page.html', {'posts': posts,
                                                    'postNumber': postNumber,
                                                    'authorNumber': authorNumber,
                                                    'numberPostAuthor': numberPostAuthor,
                                                    'message': message
                                                    })
@staff_member_required
def deletePost(request, pk):
    Post.objects.filter(pk=pk).delete()
    return redirect('admin_page')

@login_required
def userPage(request, pk):
    userName = get_object_or_404(User, pk=pk)
    posts = Post.objects.filter(author=userName).order_by('published_date')
    numberPosts = Post.objects.filter(author=userName).count()
    return render(request, 'blog/user_page.html', {'numberPosts': numberPosts,
                                                   'userName': userName,
                                                   'posts': posts})

@staff_member_required
def search(request):
    if request.method == 'GET' and request.GET.get('search'):
        search = request.GET.get('search')
        countTitle = Post.objects.filter(title__contains=search).count()
        countText = Post.objects.filter(text__contains=search).count()
        return render(request, 'blog/search.html', {'countTitle': countTitle,
                                                    'countText': countText})
    return redirect('admin_page')


def endpointJson(request):
    #post = list(Post.objects.values())
    #postJson = post
    posts = Post.objects.all()
    postJson = {}
    ora = timezone.now()
    for post in posts:
      if post.published_date > ora - datetime.timedelta(hours=1):
          temp = {post.id:{
                'author': post.author.username,
                'titolo_post' : post.title,
                'testo_post': post.text,
                'published_date': post.published_date}}
          postJson.update(temp)
    return JsonResponse(postJson, safe=False)
