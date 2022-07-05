import os
import json
import pickle

import driver
import scraper
import scraper_shein
import scraper_cinecartaz

from typing     import Any, Dict, List

# ============================================================ CONSTANTS ============================================================

SCORE_FLOOR : float = - 1.0
SCORE_CEIL  : float = + 1.0

STEPS_PER_CHECKPOINT    : int = 100

PATH_TO_EXPORTS             : str = '../exports/web_scraping/'
PATH_TO_EXPORT_INFORMATION  : str = PATH_TO_EXPORTS + 'valence_information.json'
PATH_TO_EXPORT_CHECKPOINT   : str = PATH_TO_EXPORTS + 'checkpoint.pkl'

# ============================================================ AUXILIARY FUNCTIONS ============================================================

def create_checkpoint(scrapers_in_use: List[scraper.WebScraper], scraped_information : List[Dict[str, Any]]):

    # Save iteration checkpoint
    file = open(PATH_TO_EXPORT_CHECKPOINT, "wb")
    pickle.dump(scrapers_in_use, file)
    file.close()

    # Save exported information
    file = open(PATH_TO_EXPORT_INFORMATION, "w")
    json.dump(scraped_information, file, indent=4, sort_keys=True, ensure_ascii=False)
    file.close()

# ============================================================ MAIN FUNCTIONALITY ============================================================

request_driver : driver.Driver = driver.Driver(headless=False, rotate_proxies=True, rotate_user_agents=True, max_requests=200, max_attempts_driver=20)
if not os.path.exists(PATH_TO_EXPORTS): os.makedirs(PATH_TO_EXPORTS, exist_ok=True)

scraped_information : List[Dict[str, Any]] = []
scrapers_to_use : List[scraper.WebScraper] = [ scraper_cinecartaz.WebScraperCineCartaz(), scraper_shein.WebScraperShein() ]

for scraper_to_use in scrapers_to_use:
    request_driver.set_callback_accessible(scraper_to_use.callback_accessible)
    for scraped_info in scraper_to_use.get_scraped_info(request_driver):

        scraped_information.append({
            'text': scraped_info.get_text(),
            'valence': scraped_info.get_valence_score(SCORE_FLOOR, SCORE_CEIL),
            'metadata': scraped_info.get_metadata(),
        })

        if len(scraped_information) % STEPS_PER_CHECKPOINT == 0:
            create_checkpoint(scrapers_to_use, scraped_info)

create_checkpoint(scrapers_to_use, scraped_info)
request_driver.driver_quit()