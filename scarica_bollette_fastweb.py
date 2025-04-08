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
fastweb_url = "https://fastweb.it/myfastweb/accesso/login/"

driver.get(fastweb_url)
time.sleep(3)  # Aspetta il caricamento della pagina
WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe.ck_if")))

# Prova a cliccare il bottone "Accetta" o simile (adatta il selettore al tuo caso)
try:
    accept_btn = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accetta tutti')]"))
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

driver.find_element(By.ID, "login_nickname").send_keys(username)
driver.find_element(By.ID, "login_password").send_keys(password)
driver.find_element(By.ID, "handler_3707629584079b8e704b8e6be2bebfb2_8").click()
time.sleep(5)  # Attendi il completamento del login

print("Accesso effettuato")

# Naviga alla sezione delle bollette
driver.get("https://fastweb.it/myfastweb/abbonamento/le-mie-fatture/?from=chips")

time.sleep(2)


# Trova i link delle ultime due bollette
download_links = driver.find_elements(By.CLASS_NAME, "pdf_conto")

if len(download_links) >= 5:
    for i in range(5):
        try:
            driver.get("https://fastweb.it/myfastweb/abbonamento/le-mie-fatture/?from=chips")
            time.sleep(2)
            download_links = driver.find_elements(By.CLASS_NAME, "pdf_conto")

            
            download_button = download_links[i]
            driver.execute_script("arguments[0].click();", download_button)
            #download_button.click()
            time.sleep(2)
            download_button = driver.find_element(By.CLASS_NAME, "callback2")
            pdf_url = download_button.get_attribute('href')  # Ottieni l'URL del PDF
            print(f"URL della bolletta: {pdf_url}")

            # Ora apriamo il link del PDF per il download
            #driver.get("https://fastweb.it/myfastweb/abbonamento/le-mie-fatture/conto-fastweb/Conto-FASTWEB-M008647807-20250301.pdf")
            
            
            driver.execute_script("arguments[0].click();", download_button)
            #driver.get(pdf_url)
            time.sleep(2)  # Attendi che il file venga scaricato
            
            """Torniamo alla finestra principale"""
            #driver.get("https://fastweb.it/myfastweb/abbonamento/le-mie-fatture/?from=chips")
            #time.sleep(3)
            # Supponiamo che la finestra modale abbia un pulsante con classe "modal-close"
            # Attendere che il pulsante di chiusura sia cliccabile
            #wait = WebDriverWait(driver, 10)
            #close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "modal-close")))  # Cambia il selettore se necessario

            # Clicca sul pulsante per chiudere la finestra modale
            #close_button.click()
            #print("Finestra modale chiusa!")
            #driver.refresh()
            
            print(f"Bolletta in download nella cartella: {download_path}")
        except Exception as e:
            print("Errore nel trovare il pulsante:", e)
else:
    print("Non sono state trovate abbastanza bollette.")

# Chiudi il browser
driver.quit()
