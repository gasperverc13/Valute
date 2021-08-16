import bottle
import plotly
import poskus
import os
import datetime


def nalozi_portfelj():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    if uporabnisko_ime:
        return poskus.Portfelj.preberi_iz_datoteke(uporabnisko_ime)
    else:
        bottle.redirect('/prijava/')

def shrani_portfelj(portfelj):
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    portfelj.shrani_v_datoteko(uporabnisko_ime)


@bottle.get('/')
def zacetna_stran():
    portfelj = nalozi_portfelj()
    return bottle.template(
        'zacetna.html',
        moje_valute=portfelj.moje_valute,
        trenutna_valuta=portfelj.trenutna_valuta,
        uporabnisko_ime=bottle.request.get_cookie('uporabnisko_ime'),
        kupljeno=portfelj.trenutna_valuta.kupljeno if portfelj.trenutna_valuta else [],    
    )

@bottle.get('/registracija/')
def registracija_get():
    return bottle.template('registracija.html', napake={}, polja={}, uporabnisko_ime=None)


@bottle.post('/registracija/')
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    if os.path.exists(uporabnisko_ime):
        napake = {'uporabnisko_ime': 'Uporabniško ime že obstaja.'}
        return bottle.template('registracija.html', napake=napake, polja={'uporabnisko_ime': uporabnisko_ime}, uporabnisko_ime=None)
    else:
        bottle.response.set_cookie('uporabnisko_ime', uporabnisko_ime, path='/')
        poskus.Portfelj().shrani_v_datoteko(uporabnisko_ime)
        bottle.redirect('/')

@bottle.get('/prijava/')
def prijava_get():
    return bottle.template('prijava.html', napake={}, polja={}, uporabnisko_ime=None)


@bottle.post('/prijava/')
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    if not os.path.exists(uporabnisko_ime):
        napake = {'uporabnisko_ime': 'Uporabniško ime ne obstaja.'}
        return bottle.template('prijava.html', napake=napake, polja={'uporabnisko_ime': uporabnisko_ime}, uporabnisko_ime=None)
    else:
        bottle.response.set_cookie('uporabnisko_ime', uporabnisko_ime, path='/')
        bottle.redirect('/')


@bottle.post('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnisko_ime', path='/')
    print('piškotek uspešno pobrisan')
    bottle.redirect('/')


@bottle.post('/dodaj/')
def dodaj():
    #kratica = bottle.request.forms.getunicode('kratica')
    kolicina = bottle.request.forms.getunicode('kolicina')
    #if bottle.request.forms['datum']:
    #    datum = date.fromisoformat(bottle.request.forms['datum'])
    #else:
    #    datum = None
    vec_valute = poskus.Nakup(kolicina)
    portfelj = nalozi_portfelj()
    portfelj.kupi_vec(vec_valute)
    shrani_portfelj(portfelj)
    bottle.redirect('/')


@bottle.get('/dodaj-valuto/')
def dodaj_valuto_get():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    return bottle.template('dodaj_valuto.html', napake={}, polja={}, uporabnisko_ime=uporabnisko_ime)


@bottle.post('/dodaj-valuto/')
def dodaj_valuto_post():
    kratica = bottle.request.forms.getunicode('kratica')
    #polja = {'kratica': kratica}
    portfelj = nalozi_portfelj()
   # napake = stanje.preveri_podatke_novega_spiska(ime)
    #if napake:
    #    return bottle.template('dodaj_spisek.html', napake=napake, polja=polja)
    #else:
    valuta = poskus.Valuta(kratica)
    portfelj.dodaj_valuto(valuta)
    shrani_portfelj(portfelj)
    bottle.redirect('/')


@bottle.post('/prodaj-valuto/')
def prodaj_valuto():
    indeks = bottle.request.forms.getunicode('indeks')
    portfelj = nalozi_portfelj()
    valuta = portfelj.trenutna_valuta.kupljeno[int(indeks)]
    valuta.prodaj()
    shrani_portfelj(portfelj)
    bottle.redirect('/')

@bottle.post('/zamenjaj-trenuto-valuto/')
def zamenjaj_trenutno_valuto():
    print(dict(bottle.request.forms))
    indeks = bottle.request.forms.getunicode('indeks')
    portfelj = nalozi_portfelj()
    valuta = portfelj.moje_valute[int(indeks)]
    portfelj.trenutna_valuta = valuta
    shrani_portfelj(portfelj)
    bottle.redirect('/')


@bottle.error(404)
def error_404(error):
    return 'Ta stran ne obstaja!'


bottle.run(reloader=True, debug=True)
