import bottle
import plotly
import model


@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna.html')