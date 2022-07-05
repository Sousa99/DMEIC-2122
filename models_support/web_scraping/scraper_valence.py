import os
import json
import pickle

import driver
import scraper
import scraper_shein
import scraper_cinecartaz

from typing     import Any, Dict, List, Tuple

# ============================================================ CONSTANTS ============================================================

CURRENT_VERSION : str = 'V0.1'

SCORE_FLOOR : float = - 1.0
SCORE_CEIL  : float = + 1.0

STEPS_PER_CHECKPOINT    : int = 100

PATH_TO_EXPORTS             : str = '../exports/web_scraping/'
PATH_TO_EXPORT_INFORMATION  : str = PATH_TO_EXPORTS + f'{CURRENT_VERSION}_valence_information.json'
PATH_TO_EXPORT_CHECKPOINT   : str = PATH_TO_EXPORTS + f'{CURRENT_VERSION}_checkpoint.pkl'

# ============================================================ AUXILIARY FUNCTIONS ============================================================

def load_checkpoint() -> Tuple[List[scraper.WebScraper], List[Dict[str, Any]]]:

    # Save exported information
    file = open(PATH_TO_EXPORT_INFORMATION, "r")
    scraped_information = json.load(file)
    file.close()
    print(f"✅ Loaded '{PATH_TO_EXPORT_INFORMATION}' from checkpoint!")

    # Save iteration checkpoint
    file = open(PATH_TO_EXPORT_CHECKPOINT, "rb")
    scrapers_in_use = pickle.load(file)
    file.close()
    print(f"✅ Loaded '{PATH_TO_EXPORT_CHECKPOINT}' from checkpoint!")

    return (scrapers_in_use, scraped_information)

def create_checkpoint(scrapers_in_use: List[scraper.WebScraper], scraped_information : List[Dict[str, Any]]):

    # Save exported information
    file = open(PATH_TO_EXPORT_INFORMATION, "w")
    json.dump(scraped_information, file, indent=4, sort_keys=True, ensure_ascii=False)
    file.close()

    # Save iteration checkpoint
    file = open(PATH_TO_EXPORT_CHECKPOINT, "wb")
    pickle.dump(scrapers_in_use, file)
    file.close()

# ============================================================ MAIN FUNCTIONALITY ============================================================

request_driver : driver.Driver = driver.Driver(headless=False, rotate_proxies=True, rotate_user_agents=True, max_requests=200, max_attempts_driver=20)
if not os.path.exists(PATH_TO_EXPORTS): os.makedirs(PATH_TO_EXPORTS, exist_ok=True)

scraped_information : List[Dict[str, Any]] = []
scrapers_to_use : List[scraper.WebScraper] = [ scraper_cinecartaz.WebScraperCineCartaz(), scraper_shein.WebScraperShein() ]
if os.path.exists(PATH_TO_EXPORT_INFORMATION) and os.path.exists(PATH_TO_EXPORT_CHECKPOINT):
    scrapers_to_use, scraped_information = load_checkpoint()

for scraper_to_use in scrapers_to_use:
    request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
    for scraped_info in scraper_to_use.get_scraped_info(request_driver):

        scraped_information.append({
            'text': scraped_info.get_text(),
            'valence': scraped_info.get_valence_score(SCORE_FLOOR, SCORE_CEIL),
            'metadata': scraped_info.get_metadata(),
        })

        if len(scraped_information) % STEPS_PER_CHECKPOINT == 0:
            create_checkpoint(scrapers_to_use, scraped_information)

create_checkpoint(scrapers_to_use, scraped_info)
request_driver.driver_quit()