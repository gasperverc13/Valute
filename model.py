import yfinance as yf
import json
import datetime as dt


class Portfelj:
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
        portfelj = Portfelj()
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
            return Portfelj.iz_slovarja(slovar)

    # def preveri_podatke_novega_spiska(self, kratica):
    #    napake = {}
    #    if not kratica:
    #        napake['kratica'] = 'Ime mora biti neprazno.'
    #    for valuta in self.spiski:
    #        if valuta.kratica == kratica:
    #            napake['kratica'] = 'Kratica je že zasedena.'
    #    return napake
    # ta del najverjetneje ne bo uporaben


class Valuta:
    def __init__(self, kratica):
        self.kratica = kratica
        self.kupljeno = []
        self.kupne_cene = []

    def dodaj_nakup(self, kolicina):
        self.kupljeno += kolicina
        self.kupne_cene += Nakup.trenutna_cena_valute(self.kratica)

    def skupna_vrednost(self):
        return (sum(self.kupljeno[i] * self.vrednosti[i] for i in range(
            len(self.kupljeno))) - Nakup.trenutna_cena_valute(self.kratica) * sum(self.kupljeno))

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
            Nakup.iz_slovarja(s_kolicina) for s_kolicina in slovar['kolicina']
        ]
        valuta.vrednost = [
            Nakup.iz_slovarja(s_vrednost) for s_vrednost in slovar['vrednosti']
        ]
        return valuta


class Nakup:
    def __init__(self, kratica, kolicina_delna, kupna_cena=None, cas_nakupa=None, limit=None, stop=None):
        self.kolicina_delna = kolicina_delna
        self.kupna_cena = kupna_cena
        self.limit = limit
        self.stop = stop
        self.kratica = kratica
        self.cas_nakupa = cas_nakupa

    @staticmethod
    def trenutna_cena_valute(kratica):
        kratica_x = ''.join(kratica.split('/'))
        # moral boš še naredit, da vmesnik pretvori vse kratice v obliko 'ABC/DEF'
        kazalec = yf.Ticker(f'{kratica_x}=X')
        podatki = kazalec.history(period='1d')
        return podatki['Close'][0]

    def kupi(self):
        self.kupna
    def vrednost(self):
        return self.kolicina_delna * Nakup.trenutna_cena_valute(self.kratica)

    def prodaj(self):
        self.kolicina_delna = None
    #ugotovi, ali je treba 'cas_zdaj', 'trenutna_cena_valute? in 'vrednost' premakniti v drug class

    def cas_zdaj(self):
        t = dt.datetime.now()
        s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.cas_nakupa = s[:-10]

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kolicina': self.kolicina_delna,
            'kupna_cena': self.kupna_cena,
            'limit': self.limit,
            'stop': self.stop,
            'cas_nakupa': self.cas_nakupa,
        }
    # vrednost in cas nista zahtevana v init, ugotovi ali je to problem
    @staticmethod
    def iz_slovarja(slovar):
        return Nakup(
            slovar['kratica'],
            slovar['kolicina'],
            slovar['kupna_cena'],
            slovar['limit'],
            slovar['stop'],
            slovar['cas_nakupa'],
        )
