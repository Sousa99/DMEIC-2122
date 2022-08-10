import os
import json

import driver
import scraper

from typing     import Any, Dict, List, Tuple

# ============================================================ CONSTANTS ============================================================

SCORE_FLOOR : float = - 1.0
SCORE_CEIL  : float = + 1.0

STEPS_PER_CHECKPOINT    : int = 100

PATH_TO_EXPORTS             : str = '../exports/web_scraping/extracted/'
SUFFIX_EXPORT_INFORMATION   : str = 'valence_information.json'
SUFFIX_EXPORT_CHECKPOINT    : str = 'checkpoint.pkl'

# ============================================================ AUXILIARY FUNCTIONS ============================================================

def load_checkpoint(scraped_information : List[Dict[str, Any]], scraper: scraper.WebScraper) -> Tuple[List[Dict[str, Any]], scraper.WebScraper]:

    path_to_exported_information = os.path.join(PATH_TO_EXPORTS, f"{scraper.get_file_save_prefix()}{SUFFIX_EXPORT_INFORMATION}")
    path_to_exported_checkpoint = os.path.join(PATH_TO_EXPORTS, f"{scraper.get_file_save_prefix()}{SUFFIX_EXPORT_CHECKPOINT}")

    if os.path.exists(path_to_exported_information) and os.path.exists(path_to_exported_checkpoint):
        # Load iteration checkpoint
        file = open(path_to_exported_information, "r")
        scraped_information = json.load(file)
        file.close()
        print(f"✅ Loaded '{path_to_exported_information}' from checkpoint!")
        # Load scraper checkpoint
        scraper.load_state(path_to_exported_checkpoint)
        print(f"✅ Loaded '{path_to_exported_checkpoint}' from checkpoint!")
    else: print(f"❌ Checkpoint could not be loaded or does not exist!")

    return (scraped_information, scraper)

def create_checkpoint(scraped_information : List[Dict[str, Any]], scraper: scraper.WebScraper):

    path_to_export_information = os.path.join(PATH_TO_EXPORTS, f"{scraper.get_file_save_prefix()}{SUFFIX_EXPORT_INFORMATION}")
    path_to_export_checkpoint = os.path.join(PATH_TO_EXPORTS, f"{scraper.get_file_save_prefix()}{SUFFIX_EXPORT_CHECKPOINT}")

    # Save extracted information
    file = open(path_to_export_information, "w")
    json.dump(scraped_information, file, indent=4, sort_keys=True, ensure_ascii=False)
    file.close()
    # Save scraper checkpoint
    scraper.save_state(path_to_export_checkpoint)

# ============================================================ MAIN FUNCTIONALITY ============================================================

if not os.path.exists(PATH_TO_EXPORTS): os.makedirs(PATH_TO_EXPORTS, exist_ok=True)
def run_scraper(scraper: scraper.WebScraper, request_driver: driver.Driver):

    scraped_information : List[Dict[str, Any]] = []
    scraped_information, scraper = load_checkpoint(scraped_information, scraper)
    for scraped_info in scraper.get_scraped_info(request_driver):

        scraped_information.append({
            'text': scraped_info.get_text(),
            'valence': scraped_info.get_valence_score(SCORE_FLOOR, SCORE_CEIL),
            'metadata': scraped_info.get_metadata(),
        })

        if len(scraped_information) % STEPS_PER_CHECKPOINT == 0:
            create_checkpoint(scraped_information, scraper)

    create_checkpoint(scraped_information, scraper)
    request_driver.driver_quit()