from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

#Problemi finestra modale
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time
import os

# Ottieni la cartella del programma
download_path = os.getcwd()



# Configura il browser con la cartella di download
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,  # Imposta la cartella di download
    "download.prompt_for_download": False,  # Non chiedere conferma
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,  # Evita blocchi di sicurezza
    "plugins.always_open_pdf_externally": True  # Disabilita il visualizzatore PDF integrato
})


chrome_options.add_argument("--headless")  # Esegui senza aprire il browser

# Inizializza il driver di Chrome con WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL della pagina di login di Fastweb
sorgenia_url = "https://areaclienti.sorgenia.it/login"

driver.get(sorgenia_url)
time.sleep(3)  # Aspetta il caricamento della pagina


# Prova a cliccare il bottone "Accetta" o simile (adatta il selettore al tuo caso)
try:
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "popin_tc_privacy")))

    accept_btn = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.ID, "popin_tc_privacy_button"))
                )
    accept_btn.click()
    print("✅ Cookie banner accettato.")
except:
    print("⚠️ Nessun bottone accetta trovato, forse già gestito.")

driver.refresh()
time.sleep(3)


# Effettua il login
username = "username"
password = "password"

driver.find_element(By.ID, "input-9").send_keys(username)
driver.find_element(By.ID, "input-12").send_keys(password)
# 1. Trova il pulsante
login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Accedi')]"))
)

# 2. Scrolla in vista
driver.execute_script("arguments[0].scrollIntoView(true);", login_button)

# 3. Aspetta che sia cliccabile
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accedi')]"))
)

# 4. Clicca (normale o via JS)
#login_button.click()
driver.execute_script("arguments[0].click();", login_button)
time.sleep(5)  # Attendi il completamento del login

print("Accesso effettuato")

# Naviga alla sezione delle bollette
driver.get("https://areaclienti.sorgenia.it/private/supply/5357668/PR6964274/archive")

    
time.sleep(5)

# Trova i link delle ultime due bollette
download_links = driver.find_elements(By.XPATH, "//a[h5[text()=' Bolletta sintetica ']]")

if len(download_links) >= 3:
    for i in range(3):
        try:
            
            #download_links = driver.find_elements(By.CLASS_NAME, "pdf_conto")
            download_button = download_links[i]
            
            driver.execute_script("arguments[0].scrollIntoView(true);", download_button)

            pdf_url = download_button.get_attribute('href')  # Ottieni l'URL del PDF

            # Ora apriamo il link del PDF per il download
            #driver.get("https://fastweb.it/myfastweb/abbonamento/le-mie-fatture/conto-fastweb/Conto-FASTWEB-M008647807-20250301.pdf")
            driver.get(pdf_url)
            time.sleep(2)

            # Supponiamo che la finestra modale abbia un pulsante con classe "modal-close"
            # Attendere che il pulsante di chiusura sia cliccabile
            # wait = WebDriverWait(driver, 10)
            # close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "modal-close")))  # Cambia il selettore se necessario

            # Clicca sul pulsante per chiudere la finestra modale
            # close_button.click()
            # print("Finestra modale chiusa!")
            # driver.refresh()
            
            print(f"Bolletta in download nella cartella: {download_path}")
        except Exception as e:
            print("Errore nel trovare il pulsante:", e)
else:
    print("Non sono state trovate abbastanza bollette.")

# Chiudi il browser
driver.quit()
