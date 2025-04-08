##ESTRAZIONE DEI DATI

import os
import re
from PyPDF2 import PdfReader


regex_fastweb={"data":r"Abbonamenti anticipati\s+[0-9]+/\b([0-9]+)/","importo":r"Totale da Pagare €\s+([\d.,]+)"}
regex_sorgenia={"data":r"Consumi Fatturati\s+\b([A-ZÀ-ÿa-z]+)\s+","importo":r"TOTALE SPESA\s+([\d.,]+)"}
fornitori = {"sorgenia":regex_sorgenia, "fastweb":regex_fastweb}
SPESA_CONDOMINIO = 261.99

# Array principale dei dati: 12 mesi, ogni mese ha al max 5 voci
dati_bollette = [[] for _ in range(12)]

"""Scrivi qui tutti i possibili modi di scrivere le date nelle bollette"""
def nome_mese_a_numero(nome_mese):
    mesi = {
        "gennaio": 1,
        "febbraio": 2,
        "marzo": 3,
        "aprile": 4,
        "maggio": 5,
        "giugno": 6,
        "luglio": 7,
        "agosto": 8,
        "settembre": 9,
        "ottobre": 10,
        "novembre": 11,
        "dicembre": 12,
        "01": 1,
        "02": 2,
        "03": 3,
        "04": 4,
        "05": 5,
        "06": 6,
        "07": 7,
        "08": 8,
        "09": 9,
        "10": 10,
        "11": 11,
        "12": 12
    }
    return mesi.get(nome_mese.lower())



def trova_file_pdf(cartella="."):
    """Restituisce una lista di tutti i file .pdf nella cartella specificata."""
    return [f for f in os.listdir(cartella) if f.lower().endswith(".pdf")]

def estrai_dati_da_pdf(file_path, fornitore):
    """Estrae mese e importo da un file PDF usando regex."""
    try:
        reader = PdfReader(file_path)
        testo = ""
        
        """Basta leggere la prima pagina"""
        testo = reader.pages[0].extract_text();
        #for pagina in reader.pages:
        #    testo += pagina.extract_text()
        
        mese_match = re.search(fornitori.get(fornitore).get("data"), testo)
        importo_match = re.search(fornitori.get(fornitore).get("importo"), testo)

        if not mese_match or not importo_match:
            return None, None

        mese = nome_mese_a_numero(mese_match.group(1))
    
        #mese = int(mese_match.group(1)) if mese_match else None
        importo = float(importo_match.group(1).replace(",", ".")) if importo_match else None
        
        return mese, importo
    except Exception as e:
        print(f"Errore durante l'elaborazione di {file_path}: {e}")
        return None, None

def processa_documento(file_pdf):
    """Estrae i dati da un PDF e li inserisce nel contenitore globale dati_bollette."""
    global dati_bollette
    mese = 0
    importo = 0.0

    """Controlla il file"""
    fornitore = os.path.splitext(os.path.basename(file_pdf))[0]
    for nome in fornitori.keys():
        mese, importo = estrai_dati_da_pdf(file_pdf, nome)

        """Se il file esiste già non rinominarlo"""
        if mese is None or importo is None:
            continue
        if not os.path.exists( f"{mese}_"+nome+".pdf"):
            os.rename(file_pdf, f"{mese}_"+nome+".pdf")    
        if mese is not None and importo is not None and (1 <= mese <= 12):
            fornitore = nome
            break 

    """Se il fornitore non è stato cambiato questo file non ci interessa"""
    if fornitore == os.path.splitext(os.path.basename(file_pdf))[0]: return
    
    
    if mese is None or importo is None or not (1 <= mese <= 12):
        print(f"Dati non validi nel file {file_pdf}")
        return
    
    dati_bolletta = {
        "fornitore": fornitore,
        "mese": mese,
        "importo": importo
    }
    print(dati_bolletta)

    # Inserisce solo se la lista ha meno di 5 elementi
    if len(dati_bollette[mese - 1]) < 5:
        dati_bollette[mese - 1].append(dati_bolletta)
    else:
        print(f"Attenzione: già presenti 5 bollette per il mese {mese}")

# === ESEMPIO DI UTILIZZO ===
if __name__ == "__main__":

    lista_pdf = trova_file_pdf()

    for pdf in lista_pdf:
        processa_documento(pdf)

    # Stampa finale (opzionale)
    print("Dati estratti correttamente")



##CREAZIONE TABELLA E PDF

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def numero_a_nome_mese(numero):
    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    if 1 <= numero <= 12:
        return mesi[numero - 1]
    else:
        return None



def genera_pdf_spese(dati_bollette, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    mesi = list(dati_bollette.keys())

    # Header della tabella
    data = [
        ["Spese Paciotti"] + [numero_a_nome_mese(mese) for mese in mesi],
        ["", "", ""],
        ["LUCE", "", ""],
        ["Consumo", "", ""],
        ["Bolletta"] + [f"€ {dati_bollette[mese]['sorgenia']:.2f}" for mese in mesi],
        ["/4"] + [f"€ {dati_bollette[mese]['sorgenia'] / 4:.2f}" for mese in mesi],
        ["", "", ""],
        ["INTERNET", "", ""],
        ["Bolletta"] + [f"€ {dati_bollette[mese]['fastweb']:.2f}" for mese in mesi],
        ["", "", ""],
        ["CONDOMINIO", "", ""],
        ["Bolletta", SPESA_CONDOMINIO],  # valore fisso nel tuo esempio
        ["/mesi"] + [f"€ {dati_bollette[mese]['condominio']:.2f}" for mese in mesi],
        ["/4"] + [f"€ {dati_bollette[mese]['condominio'] / 4:.2f}" for mese in mesi],
        ["", "", ""],
        ["SPESE"] + [f"€ {dati_bollette[mese]['totale']:.2f}" for mese in mesi],
        ["Da versare"] + [f"€ {dati_bollette[mese]['totale']/4:.2f}" for mese in mesi],
    ]

    table = Table(data, colWidths=[120, 100, 100])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("BACKGROUND", (0, 2), (-1, 5), colors.lightgrey),
        ("BACKGROUND", (0, 7), (-1, 8), colors.lightgrey),
        ("BACKGROUND", (0, 10), (-1, 13), colors.lightgrey),
        ("BACKGROUND", (0, 15), (-1, 16), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN", (0,1),(-1,1)),
        ("SPAN", (0,2),(-1,2)),
        ("ALIGN", (0, 2), (-1, 2), "CENTER"),
        ("SPAN", (0,6),(-1,6)),
        ("SPAN", (0,7),(-1,7)),
        ("ALIGN", (0, 7), (-1, 7), "CENTER"),
        ("SPAN", (0,9),(-1,9)),
        ("SPAN", (0,10),(-1,10)),
        ("ALIGN", (0, 10), (-1, 10), "CENTER"),
        
        ("SPAN", (1,11),(-1,11)),

    ])

    table.setStyle(style)
    elements.append(table)
    doc.build(elements)

# === ESEMPIO DI USO ===


mese1 = nome_mese_a_numero(input("Inserisci il primo mese: "))
mese2 = nome_mese_a_numero(input("Inserisci il secondo mese: "))

print(dati_bollette)
dati_tabella = {}
dati_tabella[mese1] = {}
for dati in dati_bollette[mese1-1]:
    dati_tabella[mese1][dati.get("fornitore")] = dati.get("importo")
dati_tabella[mese1]["condominio"] = SPESA_CONDOMINIO/2
totale = 0
for fornitore in dati_tabella[mese1]:
    totale += dati_tabella[mese1][fornitore]
dati_tabella[mese1]["totale"] = totale

dati_tabella[mese2] = {}
for dati in dati_bollette[mese2-1]:
    dati_tabella[mese2][dati.get("fornitore")] = dati.get("importo")
dati_tabella[mese2]["condominio"] = SPESA_CONDOMINIO/2
totale = 0
for fornitore in dati_tabella[mese2]:
    totale += dati_tabella[mese2][fornitore]
dati_tabella[mese2]["totale"] = totale


outfile =  f"{mese1}{mese2}_Paciotti.pdf"
genera_pdf_spese(dati_tabella, outfile)

print("Tabella creata correttamente")

#CREAZIONE DEL PDF FINALE
import os
from PyPDF2 import PdfMerger  # usa PdfMerger al posto di PdfFileMerger (versioni nuove)

def unisci_pdf_con_stringa(cartella, output_pdf):
    merger = PdfMerger()
    merger.append(outfile)

    # Scansiona tutti i file PDF nella cartella
    for filename in os.listdir(cartella):
        if filename.endswith(".pdf") and (filename.startswith(f"{mese1}_") or filename.startswith(f"{mese2}_")or filename.startswith(f"{mese1}"+f"{mese2}_Condominio")):
            percorso_file = os.path.join(cartella, filename)
            print(f"Aggiungo: {filename}")
            merger.append(percorso_file)

    # Salva il PDF finale unito
    merger.write(os.path.join(cartella, output_pdf))
    merger.close()
    print(f"PDF unito salvato come: {output_pdf}")

# === ESEMPIO USO ===
cartella_corrente = os.getcwd()  # oppure un path assoluto come "C:/Documenti/Bollette"
unisci_pdf_con_stringa(cartella_corrente, f"{mese1}{mese2}_SpesePaciotti.pdf")



