import yfinance as yf
import json
import datetime as dt
import plotly.graph_objs as go


class Portfelj:
    def __init__(self):
        self.moje_valute = []
        self.trenutna_valuta = None

    def dodaj_valuto(self, valuta):
        # if valuta not in self.moje_valute:
        self.moje_valute.append(valuta)
        if not self.trenutna_valuta:
            self.trenutna_valuta = valuta

    # def kolicina_valute(self, kolicina=None):
    #    self.kolicina = kolicina

    def prodaj_vse(self, valuta):
        self.moje_valute.remove(valuta)

    def zamenjaj_valuto(self, valuta):
        self.trenutna_valuta = valuta

    def kupi_vec(self, nakup):
        self.trenutna_valuta.dodaj_nakup(nakup)

    def prodaj_del(self, nakup):
        self.trenutna_valuta.prodaj_del(nakup)

    # def total(self):
    #    return sum([valuta.skupna_vrednost() for valuta in self.moje_valute])

    def zgodovina(self, zacetek, konec, interval):
        kratica = self.trenutna_valuta.kratica
        if kratica[:3] == 'USD':
            kratica_x = kratica[-3:]
        else:
            kratica_x = ''.join(kratica.split('/'))
        graf = go.Figure()
        podatki = yf.download(
            tickers=f'{kratica_x}=X', start=zacetek, end=konec, interval=interval)
        graf.add_trace(go.Candlestick(
            x=podatki.index, open=podatki['Open'], high=podatki['High'], low=podatki['Low'], close=podatki['Close']))
        graf.update_layout(title=kratica)
        graf.show()

    def v_slovar(self):
        return {
            'moje_valute': [valuta.v_slovar() for valuta in self.moje_valute],
            'trenutna_valuta': self.moje_valute.index(self.trenutna_valuta) if self.trenutna_valuta else None,

        }

    @staticmethod
    def iz_slovarja(slovar):
        portfelj = Portfelj()
        portfelj.moje_valute = [
            Valuta.iz_slovarja(sl_valuta) for sl_valuta in slovar['moje_valute']
        ]
        if slovar['trenutna_valuta'] is not None:
            portfelj.trenutna_valuta = portfelj.moje_valute[slovar['trenutna_valuta']]
        return portfelj

    def shrani_v_datoteko(self, ime_dat):
        with open(ime_dat, 'w', encoding='utf-8') as dat:
            slovar = self.v_slovar()
            json.dump(slovar, dat)

    @staticmethod
    def preberi_iz_datoteke(ime_dat):
        with open(ime_dat, 'r', encoding='utf-8') as dat:
            slovar = json.load(dat)
            return Portfelj.iz_slovarja(slovar)

    def preveri_podatke_nove_valute(self, kratica):
        napake = {}
        if not kratica:
            napake['kratica'] = 'Ime mora biti neprazno.'
        elif len(kratica) != 7 or '/' not in kratica:
            napake['kratica'] = 'Napačen format vnosa.'
        for valuta in self.moje_valute:
            if valuta.kratica == kratica:
                napake['kratica'] = 'Ta kratica je že vpisana.'
        return napake
    # ta del najverjetneje ne bo uporaben


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = []
        self.trenutna_cena = Nakup.trenutna_cena_valute(self.kratica)
        self.skupna_razlika = Valuta.razlika(self.kupljeno, self.trenutna_cena)
        self.skupna_kolicina = Valuta.kolicina_skupna(self.kupljeno)

    def dodaj_nakup(self, nakup):
        self.kupljeno.append(nakup)

    def prodaj_del(self, nakup):
        self.kupljeno.remove(nakup)

    # def skupna_vrednost(self):
    #    return (sum(self.kupljeno[i] * self.vrednosti[i] for i in range(
    #        len(self.kupljeno))) - Nakup.trenutna_cena_valute(self.kratica) * sum(self.kupljeno))

    @staticmethod
    def kolicina_skupna(kupljeno):
        skupna = 0
        for nakup in kupljeno:
            kolicina = nakup['kolicina_delna']
            skupna += kolicina
        return skupna

    @staticmethod
    def razlika(kupljeno, trenutna_cena):
        skupna = 0
        for nakup in kupljeno:
            skupna += nakup['kupna_cena'] * nakup['kolicina_delna']
        if type(trenutna_cena) == str:
            return 'Ni podatka'
        else:
            return float(f'{Valuta.kolicina_skupna(kupljeno) * trenutna_cena - skupna:.4f}')

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kupljeno': [nakup.v_slovar() for nakup in self.kupljeno],
            'skupna_kolicina': self.skupna_kolicina,
            'trenutna_cena': self.trenutna_cena,
            'skupna_razlika': self.skupna_razlika,
        }

    @staticmethod
    def iz_slovarja(slovar):
        valuta = Valuta(slovar['kratica'])
        valuta.kupljeno = [
            Nakup.iz_slovarja(sl_kupljeno) for sl_kupljeno in slovar['kupljeno']
        ]
        # valuta.skupna_kolicina =
        return valuta


class Nakup:
    def __init__(self, kratica_del, kolicina_delna, kupna_cena, cas_nakupa, stop, limit):
        self.kratica_del = kratica_del
        self.kolicina_delna = int(kolicina_delna)
        self.kupna_cena = float(kupna_cena)
        self.cas_nakupa = cas_nakupa
        self.stop = stop
        self.limit = limit
        self.razlika_delna = Nakup.razlika_delna(
            self.kratica_del, self.kupna_cena, self.kolicina_delna)

    @staticmethod
    def razlika_delna(kratica_del, kupna_cena, kolicina_delna):
        if type(Nakup.trenutna_cena_valute(kratica_del)) == str:
            return 'Ni podatka'
        else:
            return float(f'{(Nakup.trenutna_cena_valute(kratica_del) - kupna_cena) * kolicina_delna:.4f}')

    # def prodaj(self):
    #    self.kolicina_delna = None
    # ugotovi, ali je treba 'cas_zdaj', 'trenutna_cena_valute? in 'vrednost' premakniti v drug class

    @staticmethod
    def trenutna_cena_valute(kratica):
        if kratica[:3] == 'USD':
            kratica_x = kratica[-3:]
        else:
            kratica_x = ''.join(kratica.split('/'))
        valuta = yf.Ticker(f'{kratica_x}=X')
        try:
            cena = valuta.info['regularMarketPrice']
            #cena = si.get_live_price(f'{kratica_x}=X')
            # je hitrejša in ima več kratic vendar je podatek drugačen, poskusi ko je market open
            return float(f'{cena:.4f}')
        except TypeError:
            return 'Ni podatka'

    def v_slovar(self):
        return {
            'kratica_del': self.kratica_del,
            'kolicina_delna': self.kolicina_delna,
            'kupna_cena': self.kupna_cena,
            'cas_nakupa': dt.datetime.isoformat(self.cas_nakupa) if self.cas_nakupa else None,
            'stop': self.stop,
            'limit': self.limit,
            'razlika_delna': self.razlika_delna,
        }

    @staticmethod
    def iz_slovarja(slovar):
        return Nakup(
            slovar['kratica_del'],
            slovar['kolicina_delna'],
            slovar['kupna_cena'],
            dt.datetime.fromisoformat(
                slovar['cas_nakupa']) if slovar['cas_nakupa'] else None,
            slovar['stop'],
            slovar['limit'],
        )
