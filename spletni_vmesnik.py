import bottle
import plotly
import poskus
import os
import datetime as dt


def nalozi_portfelj():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    if uporabnisko_ime:
        return poskus.Portfelj.preberi_iz_datoteke(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")


def shrani_portfelj(portfelj):
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    portfelj.shrani_v_datoteko(uporabnisko_ime)

# potem spremeni nazaj na zacetna.html


@bottle.get("/")
def zacetna_stran():
    portfelj = nalozi_portfelj()
    return bottle.template(
        'zacetna.html',
        moje_valute=portfelj.moje_valute,
        uporabnisko_ime=bottle.request.get_cookie('uporabnisko_ime'),
        kupljeno=portfelj.trenutna_valuta.kupljeno if portfelj.trenutna_valuta else [],
    )


@bottle.get("/valuta/")
def valuta():
    portfelj = nalozi_portfelj()
    return bottle.template(
        'valuta.html',
        moje_valute=portfelj.moje_valute,
        trenutna_valuta=portfelj.trenutna_valuta,
        uporabnisko_ime=bottle.request.get_cookie('uporabnisko_ime'),
        kupljeno=portfelj.trenutna_valuta.kupljeno if portfelj.trenutna_valuta else [],
    )


@bottle.get("/registracija/")
def registracija_get():
    return bottle.template('registracija.html', napake={}, polja={}, uporabnisko_ime=None)


@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    if os.path.exists(uporabnisko_ime):
        napake = {'uporabnisko_ime': 'Uporabniško ime že obstaja.'}
        return bottle.template('registracija.html', napake=napake, polja={'uporabnisko_ime': uporabnisko_ime}, uporabnisko_ime=None)
    else:
        bottle.response.set_cookie(
            'uporabnisko_ime', uporabnisko_ime, path="/")
        poskus.Portfelj().shrani_v_datoteko(uporabnisko_ime)
        bottle.redirect("/")


@bottle.get("/prijava/")
def prijava_get():
    return bottle.template('prijava.html', napake={}, polja={}, uporabnisko_ime=None)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    if not os.path.exists(uporabnisko_ime):
        napake = {'uporabnisko_ime': 'Uporabniško ime ne obstaja.'}
        return bottle.template('prijava.html', napake=napake, polja={'uporabnisko_ime': uporabnisko_ime}, uporabnisko_ime=None)
    else:
        bottle.response.set_cookie(
            'uporabnisko_ime', uporabnisko_ime, path="/")
        bottle.redirect("/")


@bottle.post("/odjava/")
def odjava():
    bottle.response.delete_cookie('uporabnisko_ime', path="/")
    print('Piškotek uspešno pobrisan.')
    bottle.redirect("/")


@bottle.post("/dodaj/")
def dodaj_nakup():
    portfelj = nalozi_portfelj()
    valuta = portfelj.trenutna_valuta
    kratica_del = valuta.kratica
    kolicina_delna = bottle.request.forms['kolicina_delna']
    kupna_cena = bottle.request.forms['kupna_cena']
    cas_nakupa = dt.datetime.fromisoformat(bottle.request.forms['cas_nakupa'])
    if bottle.request.forms['stop']:
        stop = bottle.request.forms['stop']
    else:
        stop = None
    if bottle.request.forms['limit']:
        limit = bottle.request.forms['limit']
    else:
        limit = None
    nakup = poskus.Nakup(kratica_del, kolicina_delna,
                         kupna_cena, cas_nakupa, stop, limit)
    portfelj.kupi_vec(nakup)
    shrani_portfelj(portfelj)
    bottle.redirect("/valuta/")


@bottle.get("/dodaj-valuto/")
def dodaj_valuto_get():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    return bottle.template('dodaj_valuto.html', napake={}, polja={}, uporabnisko_ime=uporabnisko_ime)


@bottle.post("/dodaj-valuto/")
def dodaj_valuto_post():
    kratica = bottle.request.forms.getunicode('kratica')
    polja = {'kratica': kratica}
    portfelj = nalozi_portfelj()
    napake = portfelj.preveri_podatke_nove_valute(kratica)
    if napake:
        return bottle.template('dodaj_valuto.html', napake=napake, polja=polja)
    else:
        valuta = poskus.Valuta(kratica)
        portfelj.dodaj_valuto(valuta)
        portfelj.trenutna_valuta = valuta
        shrani_portfelj(portfelj)
        bottle.redirect("/valuta/")


@bottle.post("/prodaj-trenutno-valuto/")
def prodaj_trenutno_valuto():
    #indeks = bottle.request.forms.getunicode('indeks')
    portfelj = nalozi_portfelj()
    portfelj.prodaj_vse(portfelj.trenutna_valuta)
    if len(portfelj.moje_valute) > 0:
        portfelj.trenutna_valuta = portfelj.moje_valute[0]
    else:
        portfelj.trenutna_valuta = None
    shrani_portfelj(portfelj)
    bottle.redirect("/")


@bottle.post("/prodaj-valuto/")
def prodaj_valuto():
    portfelj = nalozi_portfelj()
    indeks = bottle.request.forms.getunicode('indeks')
    valuta = portfelj.moje_valute[int(indeks)]
    portfelj.trenutna_valuta = None
    portfelj.prodaj_vse(valuta)
    shrani_portfelj(portfelj)
    if len(portfelj.moje_valute) > 0:
        bottle.redirect("/")
    else:
        bottle.redirect("/dodaj-valuto/")


@bottle.post("/prodaj/")
def prodaj():
    portfelj = nalozi_portfelj()
    valuta = portfelj.trenutna_valuta
    indeks = bottle.request.forms.getunicode('indeks')
    nakup = valuta.kupljeno[int(indeks)]
    portfelj.prodaj_del(nakup)
    shrani_portfelj(portfelj)
    bottle.redirect("/valuta/")


@bottle.post("/zamenjaj-trenutno-valuto/")
def zamenjaj_trenutno_valuto():
    print(dict(bottle.request.forms))
    indeks = bottle.request.forms.getunicode('indeks')
    portfelj = nalozi_portfelj()
    valuta = portfelj.moje_valute[int(indeks)]
    portfelj.trenutna_valuta = valuta
    shrani_portfelj(portfelj)
    bottle.redirect("/valuta/")


@bottle.error(404)
def error_404(error):
    return 'Ta stran ne obstaja!'


bottle.run(reloader=True, debug=True)
