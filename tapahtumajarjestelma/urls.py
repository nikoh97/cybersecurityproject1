from django.urls import path
from .views import homePageView, ilmoittauduView, peruView, signupView, uusitapahtumaView, varauksetView, loginView, logoutView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', homePageView, name='home'),
    path('signup/', signupView, name='signup'),
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('ilmoittaudu/', ilmoittauduView, name='ilmoittaudu'),
    path('peru/', peruView, name='peru'),
    path('varaukset/', varauksetView, name='peru'),
    path('uusitapahtuma/', uusitapahtumaView, name='uusitapahtuma'),
]
