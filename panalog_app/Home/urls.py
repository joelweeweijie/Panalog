from django.urls import path
from .views import PostListView, PostDetailView, PostUpdateView, PostDeleteView, UserPostListView
from . import views


urlpatterns = [
    #path('', views.home, name='Pana-home'),
    path('', PostListView.as_view(), name='Pana-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-ticket'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='ticket-detail'),
    path('create/', views.createticket , name='ticket-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='ticket-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='ticket-delete'),
    path('about/', views.about, name='Pana-about'),
    path('search/', views.search, name='email-search'),
    path('hall/', views.hallnonlogger, name='Pana-hall'),
    path('uploadcsv/', views.uploadcsv, name='Pana-uploadcsv'),
    path('deletetables/', views.uploadrawcsv, name='Pana-uploadrawcsv'),
    path('uploadpandas/', views.pandasupload, name='Pana-pandas'),
    path('export/', views.export, name='Pana-export'),
    path('actmth/', views.month, name='Pana-actmonth'),
    path('allmem/', views.allmember, name='Pana-allmem'),
    path('flagticket/', views.flagtix, name='Pana-flagtix'),
    path('manage/', views.combine, name='Pana-combine'),
]