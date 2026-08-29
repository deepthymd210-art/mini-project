import os
import joblib

from django.shortcuts import render
from django.conf import settings



# ============================================================
# HOME
# ============================================================

def home(request):

    return render(request,"index.html")

