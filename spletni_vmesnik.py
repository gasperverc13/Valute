import bottle
import plotly
import model


@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna.tpl')


@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napake={}, polja={}, uporabnisko_ime=None)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/")
    bottle.redirect("/")