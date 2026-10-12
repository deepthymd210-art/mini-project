from django.urls import path

from . import views


urlpatterns = [

    # Home
    path("",views.index,name="home"),
    path("yield-prediction/",views.yield_prediction,name="yield_prediction"),

    path("production-land-calculator/",views.production_land_calculator,name="production_land_calculator"),
    path("get-weather/",views.get_weather,name="get_weather"),

]

