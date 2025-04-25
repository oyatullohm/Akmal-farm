from django.urls import path
from .views import *
urlpatterns=[
    path('operator/',Operator),
    path('vacancy/',Vacancy),
    path('pharm/',Pharm),
    

]