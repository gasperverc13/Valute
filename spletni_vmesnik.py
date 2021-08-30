import bottle
import plotly
import model
import os
import datetime as dt


def nalozi_portfelj():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    if uporabnisko_ime:
        return model.Portfelj.preberi_iz_datoteke(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")


def shrani_portfelj(portfelj):
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    portfelj.shrani_v_datoteko(uporabnisko_ime)

# potem spremeni nazaj na zacetna.html


@bottle.get("/")
def zacetna_stran():
    portfelj = nalozi_portfelj()
    if len(portfelj.moje_valute) > 0:
        return bottle.template(
            'zacetna.html',
            moje_valute=portfelj.moje_valute,
            uporabnisko_ime=bottle.request.get_cookie('uporabnisko_ime'),
            kupljeno=portfelj.trenutna_valuta.kupljeno if portfelj.trenutna_valuta else [],
        )
    else:
        bottle.redirect("/dodaj-valuto/")


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
        model.Portfelj().shrani_v_datoteko(uporabnisko_ime)
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
    if bottle.request.forms['cas_nakupa']:
        cas_nakupa = dt.datetime.fromisoformat(bottle.request.forms['cas_nakupa'])
    else:
        cas_nakupa = None
    if bottle.request.forms['stop']:
        stop = bottle.request.forms['stop']
    else:
        stop = 'Ni podatka'
    if bottle.request.forms['limit']:
        limit = bottle.request.forms['limit']
    else:
        limit = 'Ni podatka'
    if (kolicina_delna and kupna_cena) != '':
        nakup = model.Nakup(kratica_del, kolicina_delna,
                            kupna_cena, cas_nakupa, stop, limit)
        portfelj.kupi_vec(nakup)
        shrani_portfelj(portfelj)
    bottle.redirect("/valuta/")


@bottle.get("/dodaj-valuto/")
def dodaj_valuto_get():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    return bottle.template('dodaj_valuto.html', napake={}, polja={}, uporabnisko_ime=uporabnisko_ime)
#get prikaže stran, post prebere vpisane podatke
#napake so napake v vnosu, polja so prazna oz. izpolnjena polja v obrazcu

@bottle.post("/dodaj-valuto/")
def dodaj_valuto_post():
    kratica = bottle.request.forms.getunicode('kratica')
    polja = {'kratica': kratica}
    portfelj = nalozi_portfelj()
    napake = portfelj.preveri_podatke_nove_valute(kratica)
    if napake:
        return bottle.template('dodaj_valuto.html', napake=napake, polja=polja)
    else:
        valuta = model.Valuta(kratica)
        portfelj.dodaj_valuto(valuta)
        portfelj.trenutna_valuta = valuta
        shrani_portfelj(portfelj)
        bottle.redirect("/valuta/")


@bottle.post("/prodaj-trenutno-valuto/")
def prodaj_trenutno_valuto():
    portfelj = nalozi_portfelj()
    portfelj.prodaj_vse(portfelj.trenutna_valuta)
    if len(portfelj.moje_valute) > 0:
        portfelj.trenutna_valuta = portfelj.moje_valute[0]
    else:
        portfelj.trenutna_valuta = None
    shrani_portfelj(portfelj)
    bottle.redirect("/")


@bottle.get("/pokazi-graf/")
def pokazi_graf_get():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    return bottle.template('pokazi_graf.html', napake={}, polja={}, uporabnisko_ime=uporabnisko_ime)
    

@bottle.post("/pokazi-graf/")
def pokazi_graf():
    portfelj = nalozi_portfelj()
    if bottle.request.forms['zacetek']:
        zacetek = dt.date.fromisoformat(bottle.request.forms['zacetek'])
    else:
        zacetek = '2021-01-01'
    if bottle.request.forms['konec']:
        konec = dt.date.fromisoformat(bottle.request.forms['konec'])
    else:
        konec = None
    if bottle.request.forms['interval']:
        interval = bottle.request.forms['interval']
    else:
        interval = '1d'
    portfelj.zgodovina(zacetek, konec, interval)
    shrani_portfelj(portfelj)
    bottle.redirect("/valuta/")



@bottle.post("/prodaj-valuto/")
def prodaj_valuto():
    print(dict(bottle.request.forms))
    portfelj = nalozi_portfelj()
    indeks = bottle.request.forms.getunicode('indeks')
    valuta = portfelj.moje_valute[int(indeks)]
    portfelj.prodaj_vse(valuta)
    portfelj.trenutna_valuta = None
    shrani_portfelj(portfelj)
    if len(portfelj.moje_valute) > 0:
        bottle.redirect("/")
    else:
        bottle.redirect("/dodaj-valuto/")
    # odstrani valuto z indeksom 0 for some reason?!


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
