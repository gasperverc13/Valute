# Valute

Program je namenjen beleženju nakupov pri trgovanju z valutami (t.i. "Forex Trading").  

## Opis

Program beleži količino posamezne valute, za glavne pare pa prikazuje tudi trenutno ceno na trgu in razliko.  
Z uporabo zgodovinskih podatkov s strani [Yahoo!Finance](https://finance.yahoo.com/) lahko za podprte valute izriše grafe. Uporabnik lahko določi začetni in končni datum ter interval med podatki.  
Za vsako valuto je mogoče dodati več vnosov; zahtevana podatka za vnos sta količina in kupna cena, zabeležiti pa je mogoče tudi datum in uro nakupa, limit ter stop.  
Program omogoča delo več uporabnikov hkrati z uporabo piškotkov.  

## Navodila

Preden začnete uporabljati program, morate naložiti knjižnico yfinance.  
To lahko storite z ukazom `pip install yfinance`.  
Program začne delovati z zagonom spletnega vmesnika, ki ga najdete v datoteki `spletni_vmesnik.py`. V terminalu se vam nato pokaže povezava <http://127.0.0.1:8080/>; na njej dostopate do uporabniškega vmesnika.  

### Opozorilo

Podatki o trenutni ceni v programu niso vedno zanesljivi, saj jih Pythonova knjižnica yfinance pridobi z uporabo metode "web scraping".