from django.urls import path

from . import views


urlpatterns = [

    # Home
    path("",views.index,name="home"),
    path("yield-prediction/",views.yield_prediction,name="yield_prediction"),

]