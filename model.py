import yfinance as yf
import json
import datetime as dt


class Model:
    def __init__(self):
        self.moje_valute = []
        self.trenutna_valuta = None

    def dodaj_valuto(self, valuta):
        if valuta not in self.moje_valute:
            self.moje_valute.append(valuta)
        if not self.trenutna_valuta:
            self.trenutna_valuta = valuta

    # def kolicina_valute(self, kolicina=None):
    #    self.kolicina = kolicina

    def zamenjaj_valuto(self, valuta):
        self.trenutna_valuta = valuta

    def kupi_vec(self, kolicina):
        self.trenutna_valuta.dodaj_nakup(kolicina)

    # def skupaj(self, valuta):
    #    pass

    def total(self):
        return sum([valuta.skupna_vrednost() for valuta in self.moje_valute])

    def prodaj_vse(self, valuta):
        self.moje_valute.remove(valuta)

    def v_slovar(self):
        return {
            'moje_valute': [valuta.v_slovar() for valuta in self.moje_valute],
            'trenutna_valuta': self.moje_valute.index(self.trenutna_valuta) if self.trenutna_valuta else None,

        }

    @staticmethod
    def iz_slovarja(slovar):
        portfelj = Model()
        portfelj.moje_valute = [
            Valuta.iz_slovarja(s_valuta) for s_valuta in slovar['moje_valute']
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
            return Model.iz_slovarja(slovar)

    # def preveri_podatke_novega_spiska(self, kratica):
    #    napake = {}
    #    if not kratica:
    #        napake["kratica"] = "Ime mora biti neprazno."
    #    for valuta in self.spiski:
    #        if valuta.kratica == kratica:
    #            napake["kratica"] = "Kratica je že zasedena."
    #    return napake
    # ta del najverjetneje ne bo uporaben


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = []
        self.vrednosti = []

    def dodaj_nakup(self, kolicina):
        self.kupljeno += kolicina
        self.vrednosti += Transakcija.trenutna_cena_valute(self.kratica)

    def skupna_vrednost(self):
        return (sum(self.kupljeno[i] * self.vrednosti[i] for i in range(
            len(self.kupljeno))) - Transakcija.trenutna_cena_valute(self.kratica) * sum(self.kupljeno))

    def prodaj_vse(self):
        self.kupljeno = None

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kolicina': [kolicina.v_slovar() for kolicina in self.kupljeno],
            'vrednosti': [vrednost.v_slovar() for vrednost in self.vrednosti],

        }

    @staticmethod
    def iz_slovarja(slovar):
        valuta = Valuta(slovar['kratica'])
        valuta.kolicina = [
            Transakcija.iz_slovarja(s_kolicina) for s_kolicina in slovar['kolicina']
        ]
        valuta.vrednost = [
            Transakcija.iz_slovarja(s_vrednost) for s_vrednost in slovar['vrednosti']
        ]
        return valuta


class Transakcija:
    def __init__(self, kratica, kolicina, limit=None, stop=None):
        self.kolicina_delna = kolicina
        self.limit = limit
        self.stop = stop
        self.kratica = kratica

    @staticmethod
    def trenutna_cena_valute(kratica):
        kratica_x = ''.join(kratica.split('/'))
        # moral boš še naredit, da vmesnik pretvori vse kratice v obliko "ABC/DEF"
        kazalec = yf.Ticker(f'{kratica_x}=X')
        podatki = kazalec.history(period='1d')
        return podatki['Close'][0]

    def vrednost(self):
        return self.kolicina_delna * Transakcija.trenutna_cena_valute(self.kratica)

    def prodaj(self):
        self.kolicina_delna = None

    def cas_zdaj(self):
        t = dt.datetime.now()
        s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        return s[:-10]

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kolicina': self.kolicina_delna,
            'vrednost': self.vrednost(),
            'limit': self.limit,
            'stop': self.stop,
            'cas': self.cas_zdaj(),
        }

    @staticmethod
    def iz_slovarja(slovar):
        return Transakcija(
            slovar['kratica'],
            slovar['kolicina'],
            slovar['vrednost'],
            slovar['limit'],
            slovar['stop'],
            slovar['cas'],
        )
