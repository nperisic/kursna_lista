import urllib
import urllib.request
import re
import cx_Oracle
import datetime

open_par = open("parametri.txt", "r+")
parametri = open_par.readlines()
conn = cx_Oracle.connect(parametri[0][19:])
c = conn.cursor()

datum = datetime.datetime.now()
currency = ['978', '840', '756']

def main():
    global datum
    ##insert kursnu listu zaglavlje
    try:
        c.callfunc('co_kurs_frm.n_kurs', cx_Oracle.NUMBER, (900, datum.date(), 'Automatically created by Python'))
    except cx_Oracle.DatabaseError as err:
        greska(err)
    else:
        print('Else')
    finally:
        ##select max listu
        c.execute('select ID from co_kursna_lista where id = (select max(id)from co_kursna_lista)')
        print('Molim sacekajte !')
        print('Ubacujem listu 900 (NBS)!!!')
        for row in c:
            lista = row[0]
        for i in currency:
            ##Insert kursna lista detalji
            valute = (exchange_rates(i)) #uzima kursnu listu
            try:
                c.callfunc('co_kurs_frm.n_kurs_det', cx_Oracle.NUMBER,
                           (lista, valute[0], valute[1], valute[2], valute[3], valute[4]))
            except cx_Oracle.DatabaseError as err_val:
                greska(err_val)



def menjacnica():
    global datum
    ##insert kursnu listu zaglavlje
    try:
        c.callfunc('co_kurs_frm.n_kurs', cx_Oracle.NUMBER, (905, datum.date(), 'Automatically created by Python'))
    except cx_Oracle.DatabaseError as err:
        greska(err)
    else:
        print ('Molim sacekajte !')
        print ('Ubacujem listu 905 (Menjacnica)!!!')
        ##select max listu
        c.execute('select ID from co_kursna_lista where id = (select max(id)from co_kursna_lista)')
        for row in c:
            lista = row[0]
            ##Insert kursna lista detalji
        valute = (
            exchange_rates(978)) # valuta samo euro (ako trebaju ostale valute samo promeniti (978) u (i) postaviti petlju)
        srednji = round((valute[2] - 0.5), 1)# kreira srednji kurs, uzima donji kurs i umanjuje ga za 0.5 din
        c.callfunc('co_kurs_frm.n_kurs_det', cx_Oracle.NUMBER, (lista, valute[0], valute[1], 0, srednji, 0))


def exchange_rates(valute):
    global lista

    ## url for exchange rates
    url_exch = 'http://www.nbs.rs/kursnaListaModul/zaDevize.faces'
    url_middle = 'http://www.nbs.rs/kursnaListaModul/srednjiKurs.faces'

    ## open url
    htmlfile = urllib.request.urlopen(url_exch)
    html = htmlfile.read().decode('utf8')

    htmlfile_mid = urllib.request.urlopen(url_middle)
    html_mid = htmlfile_mid.read().decode('utf8')

    ##scraping data from url
    currency_val = '<tr><td class="tableCell" style="text-align:center;">' + str(
        valute) + '</td><td class="tableCell" style="text-align:left;">(.*)</td><td class="tableCell" style="text-align:center;">(.*)</td><td class="tableCell" style="text-align:center;">(.*)</td><td class="tableCell" style="text-align:right;">(.*)</td><td class="tableCell" style="text-align:right;">(.*)</td></tr>'
    #pattern = re.compile(currency_val)
    ext_val = re.findall(currency_val, html)
    ext_val_list_exc = list(ext_val[0]) #convert to list
    lista = ext_val_list_exc[3:5] # exclude currency designation and country
    paritet = ext_val_list_exc[2]
    new_lista = []
    for n in lista: # pretvara str u listi u float
        new_lista.append(float(n));
    lista = new_lista;

    ##scraping mid data from url
    currency_mid = '<tr><td class="tableCell" style="text-align:center;">' + str(
        valute) + '</td><td class="tableCell" style="text-align:left;">(.*)</td><td class="tableCell" style="text-align:center;">(.*)</td><td class="tableCell" style="text-align:center;">(.*)</td><td class="tableCell" style="text-align:right;">(.*)</td></tr>'
    #pattern = re.compile(currency_mid)
    ext_val_mid = re.findall(currency_mid, html_mid)
    ext_val_list_mid = list(ext_val_mid[0]) #convert to list
    mid_exc = (ext_val_list_mid[-1]) # exclude currency designation and country

    ##scraping date from url
    date = '<td><span class="bold"><span id="index:id1">EXCHANGE RATE LIST NO.</span><span id="index:id12">(.*)</span><br/><span id="index:id2">OFFICIAL MIDDLE RSD EXCHANGE RATE</span><br/><br/><span id="index:id3">FORMED ON</span> <span id="index:id31">(.*)</span> <span id="index:id32">YEAR</span></span></td>'
    ext_date = re.findall(date, html_mid)
    ext_date_list = list(ext_date[0]) #convert to list
    date = (ext_date_list[-1]) # extract only date

    lista.insert(0, int(valute)) #add currency no
    lista.insert(1, int(paritet)) #add currency no
    lista.insert(3, float(mid_exc)) #add mid exchange rate
    ##lista.insert(0, str(date)) # add date at position 0

    return lista
def greska(err):
    print(err)
    file_w = open('error.txt','a')
    file_w.write(str(datum.date())+'--'+str(datum.time())+'\n')
    file_w.write(str(err))
    file_w.closed

if __name__ == '__main__':
    main()
    menjacnica()
    conn.close()