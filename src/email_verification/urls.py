from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("submit/", views.submit, name="submit"),
    path("thanks/", views.thanks, name="thanks"),
    path("verify/<str:connection_id>/", views.verify_redirect, name="verify_redirect"),
]
