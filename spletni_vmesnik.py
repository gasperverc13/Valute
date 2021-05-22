import bottle
import plotly
import model


def nalozi_portfelj():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    if uporabnisko_ime:
        try:
            portfelj = model.Model.preberi_iz_datoteke(uporabnisko_ime)
        except FileNotFoundError:
            portfelj = model.Model()
        return portfelj
    else:
        bottle.redirect('/prijava/')


def shrani_portfelj(portfelj):
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime')
    portfelj.shrani_v_datoteko(uporabnisko_ime)


@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna.html')


@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napake={}, polja={}, uporabnisko_ime=None)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    bottle.response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/")
    bottle.redirect("/")


@bottle.error(404)
def error_404(error):
    return 'Ta stran ne obstaja!'


bottle.run(reloader=True, debug=True)
