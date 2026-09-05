from django.urls import path

from . import views


urlpatterns = [

    # Home
    path("",views.home,name="home"),
    path("yield-prediction/",views.yield_prediction,name="yield_prediction"),


]