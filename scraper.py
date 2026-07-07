import json
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_imdb():
    print("Kopplar upp systemen, herrn. Startar visuell webbläsare...")
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Kunde inte starta webbläsaren: {e}")
        return
        
    print("Navigerar till IMDb Top 250...")
    driver.get("https://www.imdb.com/chart/top/")
    
    print("Mjukskrollar igenom sidan för att ladda in alla 250 filmer och affischer...")
    # Genom att skrolla en fast sträcka många gånger tvingar vi IMDb att ladda hela listan
    for _ in range(80): 
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(0.2)
        
    print("Väntar några sekunder för att säkerställa fullständig nedladdning...")
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    movies = []
    items = soup.select('li.ipc-metadata-list-summary-item')
    print(f"Hittade {len(items)} filmer. Bygger er databas...")
    
    for item in items:
        try:
            # Titel
            title_elem = item.select_one('.ipc-title__text')
            full_title = title_elem.text if title_elem else "Okänd"
            title = full_title.split('. ', 1)[-1] if '. ' in full_title else full_title
            
            # Rank - Bulletproof metod: Vi räknar bara hur många filmer vi lagt till
            rank = len(movies) + 1
            
            # Årtal
            metadata_elem = item.select_one('.cli-title-metadata')
            year = 0
            if metadata_elem:
                match = re.search(r'(19\d{2}|20\d{2})', metadata_elem.text)
                if match:
                    year = int(match.group(1))
            
            # Betyg
            rating_elem = item.select_one('.ipc-rating-star--rating')
            rating = float(rating_elem.text) if rating_elem else 0.0
            
            # Affisch
            img_elem = item.select_one('img.ipc-image')
            poster = ""
            if img_elem:
                poster = img_elem.get('src', '')
                if "_V1_" in poster:
                    poster = poster.split("_V1_")[0] + "_V1_FMjpg_UX500_.jpg"
            
            movies.append({
                "rank": rank,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster
            })
            
            # Säkerhetsspärr ifall listan på skärmen är längre än 250
            if len(movies) >= 250:
                break
            
        except Exception as e:
            continue
            
    with open('imdb_top_250.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)
        
    print(f"Systemåterställning klar, herrn! Skapade en optimerad 'imdb_top_250.json' med {len(movies)} filmer.")

if __name__ == "__main__":
    scrape_imdb()