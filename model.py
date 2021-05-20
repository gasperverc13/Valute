import yfinance as yf
import json
import datetime as dt


class Model:
    def __init__(self):
        self.moje_valute = {}

    def kolicina_valute(self, kolicina=None):
        self.kolicina = kolicina

    def dodaj_valuto(self, valuta):
        if valuta not in self.moje_valute:
            self.moje_valute[valuta] = (self.kolicina)
        else:
            self.moje_valute[valuta] += (self.kolicina)

    def skupaj(self, valuta):
        pass

    def total(self):
        pass


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = []
        self.vrednosti = []

    def dodaj_nakup(self, kolicina):
        self.kupljeno += kolicina
        self.vrednosti += self.vrednost_valute()

    def skupna_vrednost(self):
        self.skupna_vrednost = (sum(self.kupljeno[i] * self.vrednosti[i] for i in range(
            len(self.kupljeno))) - self.vrednost_valute() * sum(self.kupljeno))

    def prodaj_vse(self):
        self.kupljeno = None


class Transakcija:
    def __init__(self, kratica, kolicina, limit=None, stop=None):
        self.kratica = kratica
        self.kolicina = kolicina
        self.limit = limit
        self.stop = stop

    @staticmethod
    def vrednost_valute(kratica):
        kratica_x = ''.join(kratica.split('/'))
        kazalec = yf.Ticker(f'{kratica_x}=X')
        podatki = kazalec.history(period='1d')
        return podatki['Close'][0]

    def vrednost(self):
        self.vrednost = self.kolicina * self.trenutna_vrednost

    def cas_zdaj(self):
        t = dt.datetime.now()
        s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.cas = s[:-7]

    def zdruzi(self):
        return {
            'kolicina': self.kolicina,
            'vrednost': self.vrednost,
            'limit': self.limit,
            'stop': self.stop,
            'cas': self.cas,
        }
