import yfinance as yf
import json
import datetime as dt


class Model:
    def __init__(self):
        self.moje_valute = {}

    def kolicina_valute(self, kolicina):
        self.kolicina = kolicina
    
    def dodaj_valuto(self, valuta):
        if valuta not in self.moje_valute:
            self.moje_valute[valuta] = (self.kolicina)
        else:
            self.moje_valute[valuta].append(self.kolicina)

#    def trenutna_vrednost(self):


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = ()
    
    def dodaj_nakup(self, kolicina):
        self.kupljeno += kolicina

    def vrednosti(self):
        self.vrednosti = []

   # def skupna_vrednost(self):
    #    self.skupna_vrednost = 

    def prodaj_vse(self):
        self.kupljeno = None

 #   def trenutna_vrednost(self):


class Transakcija:
    def __init__(self, kratica, kolicina, limit=None, stop=None):
        self.kratica = kratica
        self.kolicina = kolicina
        self.limit = limit
        self.stop = stop

    def vrednost_valute(self):
        kazalec = yf.Ticker(self.kratica)
        podatki = kazalec.history(period='1d')
        self.trenutna_vrednost = podatki['Close'][0]

    def vrednost(self):
        self.vrednost = self.kolicina *  self.trenutna_vrednost
    
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