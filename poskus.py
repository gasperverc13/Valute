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
    def prodaj_vse(self, valuta):
        self.moje_valute.remove(valuta)

    def zamenjaj_valuto(self, valuta):
        self.trenutna_valuta = valuta

    def kupi_vec(self, kolicina):
        self.trenutna_valuta.dodaj_nakup(kolicina)

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

    def dodaj_nakup(self, nakup):
        self.kupljeno.append(nakup)

    def prodaj_vse(self):
        self.kupljeno = None

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kolicina': [kolicina.v_slovar() for kolicina in self.kupljeno],
        }

    @staticmethod
    def iz_slovarja(slovar):
        valuta = Valuta(slovar['kratica'])
        valuta.kolicina = [
            Nakup.iz_slovarja(s_kolicina) for s_kolicina in slovar['kolicina']
        ]
        return valuta


class Nakup:
    def __init__(self, kolicina_delna):
        self.kolicina_delna = kolicina_delna

    # @staticmethod
    # def trenutna_cena_valute(kratica):
    #    kratica_x = ''.join(kratica.split('/'))
    #    # moral boš še naredit, da vmesnik pretvori vse kratice v obliko 'ABC/DEF'
    #    kazalec = yf.Ticker(f'{kratica_x}=X')
    #    podatki = kazalec.history(period='1d')
    #    return podatki['Close'][0]

    def prodaj(self):
        self.kolicina_delna = None
    # ugotovi, ali je treba 'cas_zdaj', 'trenutna_cena_valute? in 'vrednost' premakniti v drug class

    def v_slovar(self):
        return {
            'kolicina': self.kolicina_delna,
        }
    # vrednost in cas nista zahtevana v init, ugotovi ali je to problem

    @staticmethod
    def iz_slovarja(slovar):
        return Nakup(
            slovar['kolicina'],
        )
