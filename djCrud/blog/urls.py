from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('user/new/', views.newUser, name='new_user'),
    path('user/<int:pk>/', views.userPage, name='user_page'),
    path('admin/page/', views.adminPage, name='admin_page')
]

#Post views
urlpatterns += [
    path('post/new/', views.newPost, name='new_post'),
    path('post/<int:pk>/', views.postDetail, name='post_detail'),
    path('posts/', views.postView, name='post_view'),
    path('post/<int:pk>/edit', views.postEdit, name='post_edit'),
    path('admin/page/<int:pk>/delete', views.adminPage, name='delete_post'),
    path('search/', views.search, name='search'),
    path('post/json/', views.endpointJson, name='post_json'),
]