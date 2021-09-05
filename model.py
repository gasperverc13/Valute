import yfinance as yf
import json
import datetime as dt
import plotly.graph_objs as go


class Portfelj:
    def __init__(self):
        self.moje_valute = []
        self.trenutna_valuta = None

    def dodaj_valuto(self, valuta):
        self.moje_valute.append(valuta)
        if not self.trenutna_valuta:
            self.trenutna_valuta = valuta

    def prodaj_vse(self, valuta):
        self.moje_valute.remove(valuta)

    def zamenjaj_valuto(self, valuta):
        self.trenutna_valuta = valuta

    def kupi_vec(self, nakup):
        self.trenutna_valuta.dodaj_nakup(nakup)

    def prodaj_del(self, nakup):
        self.trenutna_valuta.prodaj_del(nakup)

    def graf(self, zacetek, konec, interval):
        kratica = self.trenutna_valuta.kratica
        if kratica[:3] == ('USD' or 'usd'):
            kratica_x = kratica[-3:]
        else:
            kratica_x = ''.join(kratica.split('/'))
        kratica_x = f'{kratica_x}=X'
        if zacetek is not None:
            if konec is not None:
                if konec < zacetek:
                    t = konec
                    konec = zacetek
                    zacetek = t
            elif zacetek > dt.date.today():
                zacetek = dt.date.today()
        try:
            yf.Ticker(kratica_x).history(start=zacetek)
        except OverflowError:
            zacetek = None
        try:
            yf.Ticker(kratica_x).history(start=zacetek, end=konec)
        except OverflowError:
            konec = None
        graf = go.Figure()
        podatki = yf.download(
            tickers=kratica_x, start=zacetek, end=konec, interval=interval)
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
            napake['kratica'] = 'Vpišite kratico.'
        elif len(kratica) != 7 or '/' != kratica[3]:
            napake['kratica'] = 'Napačen format vnosa.'
        for valuta in self.moje_valute:
            obratno = '/'.join([kratica[-3:].upper(), kratica[:3].upper()])
            if (valuta.kratica == kratica.upper()) or (valuta.kratica == obratno):
                napake['kratica'] = 'Ta kratica je že vpisana.'
        return napake

    def preveri_podatke_nakupa(self, kolicina_delna, kupna_cena, stop, limit):
        napake = {}
        for podatek in [kolicina_delna, kupna_cena, stop, limit]:
            try:
                float(podatek)
                if float(podatek) == 0:
                    napake['nakup'] = 'Vrednosti ne smejo biti 0.'
                    break
            except ValueError:
                napake['nakup'] = 'Vnešeni podatki niso ustrezni.'
                break
            except TypeError:
                continue
        return napake

    def preveri_podatke_grafa(self, interval):
        kratica = self.trenutna_valuta.kratica
        napake = {}
        if interval not in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']:
            napake['graf'] = 'Vnesite ustrezen interval.'
            return napake
        if kratica[:3] == 'USD':
            kratica_x = kratica[-3:]
        else:
            kratica_x = ''.join(kratica.split('/'))
        kratica_x = f'{kratica_x}=X'
        poskus = yf.Ticker(kratica_x).history(start='2021-01-01')
        if len(poskus) == 0:
            napake['graf'] = 'Grafa za ta par ni mogoče prikazati.'
        return napake


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = []
        self.trenutna_cena = Valuta.trenutna_cena_valute(self.kratica)
        self.skupna_razlika = 0
        self.skupna_kolicina = 0

    def dodaj_nakup(self, nakup):
        self.kupljeno.append(nakup)
        self.kolicina_skupna(nakup, 'dodaj')
        self.razlika(nakup, 'dodaj')

    def prodaj_del(self, nakup):
        self.kupljeno.remove(nakup)
        self.kolicina_skupna(nakup, 'prodaj')
        self.razlika(nakup, 'prodaj')

    def kolicina_skupna(self, nakup, naredi):
        if naredi == 'dodaj':
            self.skupna_kolicina += nakup.kolicina_delna
        elif naredi == 'prodaj':
            self.skupna_kolicina -= nakup.kolicina_delna

    def razlika(self, nakup, naredi):
        trenutna_cena = self.trenutna_cena
        if type(trenutna_cena) == float:
            if naredi == 'dodaj':
                self.skupna_razlika += float(
                    f'{(trenutna_cena - nakup.kupna_cena) * nakup.kolicina_delna:.4f}')
            elif naredi == 'prodaj':
                self.skupna_razlika -= float(
                    f'{(trenutna_cena - nakup.kupna_cena) * nakup.kolicina_delna:.4f}')
        else:
            self.skupna_razlika = 'Ni podatka'

    @staticmethod
    def trenutna_cena_valute(kratica):
        if kratica[:3] == 'USD':
            kratica_x = kratica[-3:]
        else:
            kratica_x = ''.join(kratica.split('/'))
        kratica_x = f'{kratica_x}=X'
        valuta = yf.Ticker(kratica_x)
        try:
            cena = valuta.info['regularMarketPrice']
            return float(f'{cena:.4f}')
        except TypeError:
            return 'Ni podatka'
        except TimeoutError:
            return 'Trenutno ni podatka'

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
        valuta.skupna_kolicina = slovar['skupna_kolicina']
        valuta.skupna_razlika = slovar['skupna_razlika']
        return valuta


class Nakup:
    def __init__(self, kratica_del, kolicina_delna, kupna_cena, cas_nakupa, stop, limit):
        self.kratica_del = kratica_del
        self.kolicina_delna = float(kolicina_delna)
        self.kupna_cena = float(kupna_cena)
        self.cas_nakupa = cas_nakupa
        self.stop = float(stop) if stop is not None else None
        self.limit = float(limit) if limit is not None else None
        self.razlika_delna = Nakup.razlika_delna(
            self.kratica_del, self.kupna_cena, self.kolicina_delna)

    @staticmethod
    def razlika_delna(kratica_del, kupna_cena, kolicina_delna):
        if type(Valuta.trenutna_cena_valute(kratica_del)) == float:
            return float(f'{(Valuta.trenutna_cena_valute(kratica_del) - kupna_cena) * kolicina_delna:.4f}')
        else:
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
