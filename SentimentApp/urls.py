from django.urls import path
from . import views
urlpatterns = [
    path('',views.mainpage),
    path('mainpage',views.mainpage),
    path('initScoreCalc',views.initScoreCalc),
    path('updateScore',views.updateScore),
    path('register',views.register),
    path('registerEmail',views.registerEmail)
]