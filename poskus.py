import yfinance as yf
import json
import datetime as dt


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

    def prodaj_vse(self):
        self.moje_valute.remove(self.trenutna_valuta)
        # ko jo pobriše ne skoči nikamor in kaže error, bo treba dodati na roke popravek

    def zamenjaj_valuto(self, valuta):
        self.trenutna_valuta = valuta

    def kupi_vec(self, nakup):
        self.trenutna_valuta.dodaj_nakup(nakup)

    def prodaj_del(self, nakup):
        self.trenutna_valuta.prodaj_del(nakup)

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

    def dodaj_nakup(self, nakup):
        self.kupljeno.append(nakup)

    def prodaj_del(self, nakup):
        self.kupljeno.remove(nakup)

    def kolicina_skupna(self):
        skupna = 0
        for nakup in self.kupljeno:
            kolicina = nakup['kolicina_delna']
            skupna += kolicina
        return skupna

    def razlika(self):
        skupna = 0
        for nakup in self.kupljeno:
            skupna += nakup['kupna_cena'] * nakup['kolicina_delna']
        if Nakup.trenutna_cena_valute(self.kratica).isnumeric():
            return self.kolicina_skupna() * Nakup.trenutna_cena_valute(self.kratica) - skupna
        else:
            return 'Ni podatka'

    def v_slovar(self):
        return {
            'kratica': self.kratica,
            'kupljeno': [nakup.v_slovar() for nakup in self.kupljeno],
            'skupna_kolicina': self.kolicina_skupna(),
            'trenutna_cena': Nakup.trenutna_cena_valute(self.kratica),
            'skupna_razlika': self.razlika(),
        }

    @staticmethod
    def iz_slovarja(slovar):
        valuta = Valuta(slovar['kratica'])
        valuta.kupljeno = [
            Nakup.iz_slovarja(sl_kupljeno) for sl_kupljeno in slovar['kupljeno']
        ]
        return valuta


class Nakup:
    def __init__(self, kratica_del, kolicina_delna, kupna_cena, cas_nakupa, stop, limit):
        self.kratica_del = kratica_del
        self.kolicina_delna = int(kolicina_delna)
        self.kupna_cena = float(kupna_cena)
        self.cas_nakupa = cas_nakupa
        self.stop = stop
        self.limit = limit

    def razlika_delna(self):
        if Nakup.trenutna_cena_valute(self.kratica_del).isnumeric():
            return (Nakup.trenutna_cena_valute(self.kratica_del) - self.kupna_cena) * self.kolicina_delna
        else:
            return 'Ni podatka'

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
            return cena
        except KeyError:
            return 'Ni podatka'

    def v_slovar(self):
        return {
            'kratica_del': self.kratica_del,
            'kolicina_delna': self.kolicina_delna,
            'kupna_cena': self.kupna_cena,
            'cas_nakupa': dt.datetime.isoformat(self.cas_nakupa),
            'stop': self.stop,
            'limit': self.limit,
            'trenutna_cena_del': Nakup.trenutna_cena_valute(self.kratica_del),
            'razlika_delna': self.razlika_delna()
        }
    # vrednost in cas nista zahtevana v init, ugotovi ali je to problem

    @staticmethod
    def iz_slovarja(slovar):
        return Nakup(
            slovar['kratica_del'],
            slovar['kolicina_delna'],
            slovar['kupna_cena'],
            dt.datetime.fromisoformat(slovar['cas_nakupa']),
            slovar['stop'],
            slovar['limit'],
        )
