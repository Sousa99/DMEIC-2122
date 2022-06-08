import os
import json

import driver
import scraper
import scraper_cinecartaz

from typing     import Any, Dict, List

# ============================================================ CONSTANTS ============================================================

SCORE_FLOOR : float = - 1.0
SCORE_CEIL  : float = + 1.0

PATH_TO_EXPORTS             : str = '../exports/web_scraping/'
PATH_TO_EXPORT_INFORMATION  : str = PATH_TO_EXPORTS + 'valence_information.json'

# ============================================================ MAIN FUNCTIONALITY ============================================================

request_driver : driver.Driver = driver.Driver()
if not os.path.exists(PATH_TO_EXPORTS): os.makedirs(PATH_TO_EXPORTS)

scraped_information : List[Dict[str, Any]] = []
scrapers_to_use : List[scraper.WebScraper] = [ scraper_cinecartaz.WebScraperCineCartaz() ]
for scraper_to_use in scrapers_to_use:
    for scraped_info in scraper_to_use.get_scraped_info(request_driver):
        scraped_information.append({
            'text': scraped_info.get_text(),
            'valence': scraped_info.get_valence_score(SCORE_FLOOR, SCORE_CEIL),
            'metadata': scraped_info.get_metadata(),
        })

file = open(PATH_TO_EXPORT_INFORMATION, "w")
json.dump(scraped_information, file, indent=4, sort_keys=True, ensure_ascii=False)
file.close()

request_driver.driver_quit()