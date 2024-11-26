import requests
import socket
import ipaddress
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Account, Tapahtuma, Varaus


def tarkistaSalasana(salasana):
    if not salasana or len(salasana) < 8 or len(salasana) > 16:
        return False
    luku = any(char.isdigit() for char in salasana)
    erikoismerkki = any(char in set("!@#$^&*()_+[]{}|;:,.<>?/")
                        for char in salasana)
    isokirjain = any(char.isupper() for char in salasana)
    pienikirjain = any(char.islower() for char in salasana)
    return luku and erikoismerkki and isokirjain and pienikirjain


def teeKayttaja(request):
    kayttajanimi = request.POST.get('username', None)
    salasana = request.POST.get('password', None)
    email = request.POST.get('email', None)

    # Flaw: Identification and Authentication Failures
    # Fix:
    # if not tarkistaSalasana(salasana):
    #     return None

    if kayttajanimi and salasana and email:
        user = User.objects.filter(username=kayttajanimi, email=email).first()
        if not user:
            user = User.objects.create_user(username=kayttajanimi,
                                            email=email,
                                            password=salasana)
            kayttaja = Account.objects.create(user=user, balance=1000)
            return kayttaja
        else:
            kayttaja = Account.objects.filter(user=user).first()
            return kayttaja
    return None


def validoi_url(ks_url):
    url = urlparse(ks_url)
    if not ks_url or url.scheme not in ('http', 'https'):
        return False
    try:
        url = urlparse(ks_url)
        ip = socket.gethostbyname(url.hostname)
        if ipaddress.ip_address(ip).is_private:
            return False
        allowed_domains = ["wordpress.com", "wix.com", "squarespace.com"]
        if url.hostname not in allowed_domains:
            return False
    except Exception:
        return False
    return True


def verifioi_tapahtuma_url(url):
    # Flaw: SSRF
    res = requests.get(url)
    valid_url = res.status_code == 200
    return valid_url
    # Fix:
    # valid_url = validoi_url(url)
    # if valid_url:
    #     res = requests.get(url, timeout=5)
    #     return res.status_code == 200


@login_required
# @csrf_protect
def uusitapahtumaView(request):
    # Flaw: Broken Access Control
    # Fix:
    # user = request.user
    # kayttaja = Account.objects.filter().first()
    # if not user.is_superuser or not kayttaja.organizer:
    #     return redirect('/')

    if request.method == 'POST':
        nimi = request.POST.get('nimi', None)
        paikka_maara = request.POST.get('paikka_maara', None)
        kotisivu = request.POST.get('kotisivu', None)

        verified = verifioi_tapahtuma_url(kotisivu)
        if not verified:
            kotisivu = ""

        if nimi and paikka_maara and valid_url:
            Tapahtuma.objects.create(
                nimi=nimi, paikka_maara=paikka_maara, kotisivu=kotisivu)
    return render(request, 'uusitapahtuma.html')


# @csrf_protect
def signupView(request):
    if request.method == 'POST':
        acc = teeKayttaja(request)
        if acc:
            return redirect('/login')
    return render(request, 'rekisteroi.html')


@login_required
# @csrf_protect
def ilmoittauduView(request):
    if request.method == 'POST':
        tapahtuma_id = request.POST.get('id')
        onnistui = ilmoittaudu(request, tapahtuma_id)
        if onnistui:
            return render(request, 'varattu.html', {'tapahtuma': Tapahtuma.objects.filter(tapahtuma_id=tapahtuma_id).first()})
    return redirect('/')


@login_required
# @csrf_protect
def peruView(request):
    if request.method == 'POST':
        tapahtuma_id = request.POST.get('id')
        peru_ilmoittautuminen(request, tapahtuma_id)
    return redirect('/')


@login_required
def ilmoittaudu(request, tapahtuma_id):
    tapahtuma = Tapahtuma.get(tapahtuma_id)
    if not Tapahtuma.on_tilaa(tapahtuma_id):
        return False
    if Varaus.varattu(request.user, tapahtuma_id):
        return False
    Varaus.objects.create(
        user=request.user, tapahtuma_id=tapahtuma)
    return True


@login_required
def peru_ilmoittautuminen(request, tapahtuma_id):
    tapahtuma = Tapahtuma.get(tapahtuma_id)
    if not Varaus.varattu(request.user, tapahtuma_id):
        return False
    Varaus.peru(request.user, tapahtuma_id)
    return True


@login_required
def varauksetView(request):
    kayttaja = Account.objects.filter(user=request.user).first()
    varaukset = Varaus.get_varatut(request.user)
    varaukset_info = []
    for varaus in varaukset:
        nimi = varaus.tapahtuma_id.nimi
        print("nimi: ", nimi)
        v = {
            'nimi': nimi,
            'date': varaus.date
        }
        varaukset_info.append(v)

    return render(request, 'varaukset.html', {
        'varaukset': varaukset_info,
        'kayttaja': {
            'nimi': kayttaja.user.username,
            'email': kayttaja.user.email,
        }
    })


@login_required
def homePageView(request):
    kayttaja = Account.objects.filter(user=request.user).first()
    if not request.user.is_authenticated or not kayttaja:
        return redirect('login/')

    tapahtumat = Tapahtuma.objects.all()
    if len(tapahtumat) == 0:
        Tapahtuma.objects.create(nimi='Festivaali 1', paikka_maara=10)
        Tapahtuma.objects.create(nimi='Festivaali 2', paikka_maara=5)
        Tapahtuma.objects.create(nimi='Festivaali 3', paikka_maara=2)
        Tapahtuma.objects.create(nimi='Festivaali 4', paikka_maara=1)
        Tapahtuma.objects.create(nimi='Festivaali 5', paikka_maara=0)
        tapahtumat = Tapahtuma.objects.all()

    tapahtumat_info = []
    for tapahtuma in tapahtumat:
        varatut = len(Varaus.get_ilmoittautujat(tapahtuma))
        t = {
            'tapahtuma': tapahtuma,
            'varatut': varatut
        }
        tapahtumat_info.append(t)

    return render(request, 'index.html', {
        'tapahtumat': tapahtumat_info,
        'kayttaja': kayttaja.user.username,
    })
