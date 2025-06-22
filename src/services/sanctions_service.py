import os
import asyncio
import logging.config
from datetime import datetime
from aiogram import Bot
from aiogram.types import FSInputFile
from pathlib import Path
from src.core.config import settings
from src.core.logger import logging_config
from src.utils.text_utils import normalize_company_name
from src.utils.file_handlers import (
    load_companies_from_excel,
    save_results_to_excel,
    clean_tmp_folders,
)
from src.utils.web_scraper import search_matches, download_file


logging.config.dictConfig(logging_config)
logger = logging.getLogger(name="sanctions_scraper")


async def check_sanctions(uploaded_file_path: str, chat_id: int, bot: Bot):
    """
    Downloads companies from an Excel file, checks them for sanctions lists,
    and sends the final report to the user.
    """
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{settings.RESULT_DIR}/sanctions_companies_{date_str}.xlsx"
    logger.info("Starting sanctions check process")
    original_companies = await asyncio.to_thread(
        load_companies_from_excel, uploaded_file_path
    )
    logger.info(f"Loaded {len(original_companies)} companies from input file")
    normalized_companies = await asyncio.to_thread(
        normalize_company_name, original_companies
    )
    os.makedirs(settings.TMP_DIR_SCRAPER, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)
    results = {}
    for name, source in settings.SANCTIONS_SOURCES.items():
        url = source["url"]
        ext = source["ext"]
        file_path = Path(f"{settings.TMP_DIR_SCRAPER}/{name}{ext}")
        logger.info(f"Processing {name} sanctions list from {url}")
        try:
            await asyncio.to_thread(download_file, url, file_path)
            matches = await asyncio.to_thread(
                search_matches,
                file=file_path,
                companies=normalized_companies,
                source_name=name,
                ext=ext,
            )
            results[name] = matches
            logger.info(f"Processed {name}.Found {len(matches)} matches")
        except Exception as e:
            logger.error(f"Failed to process {name}: {e}", exc_info=True)
            results[name] = []
    logger.info("Generating final report...")
    await asyncio.to_thread(
        save_results_to_excel,
        results=results,
        original_companies=original_companies,
        normalized_companies=normalized_companies,
        output_file=output_file,
    )
    ready_file = FSInputFile(path=output_file)
    await bot.send_document(
        chat_id=chat_id,
        caption="Sanctions check completed",
        document=ready_file,
    )
    logger.info("Results successfully sent to user")
    clean_tmp_folders(folders=[settings.TMP_DIR_BOT, settings.TMP_DIR_SCRAPER])
