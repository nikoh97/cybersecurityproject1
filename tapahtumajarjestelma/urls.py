from django.urls import path
from .views import homePageView, ilmoittauduView, peruView, signupView, uusitapahtumaView, varauksetView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', homePageView, name='home'),
    path('signup/', signupView, name='signup'),
    path('login/', LoginView.as_view(template_name='kirjaudu.html')),
    path('logout/', LogoutView.as_view(next_page='/')),
    path('ilmoittaudu/', ilmoittauduView, name='ilmoittaudu'),
    path('peru/', peruView, name='peru'),
    path('varaukset/', varauksetView, name='peru'),
    path('uusitapahtuma/', uusitapahtumaView, name='uusitapahtuma'),
]
