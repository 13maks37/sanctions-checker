import requests
import pandas as pd
import xml.etree.ElementTree as ET
import logging.config
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
from src.utils.text_utils import is_similar, normalize_company_name
from src.core.logger import logging_config


logging.config.dictConfig(logging_config)
logger = logging.getLogger(name="web_sсraper")


def download_file(url: str, filename: Path):
    """Downloads a file from a given URL and saves it to disk."""
    logger.info(f"Downloading: {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename.write_bytes(response.content)
        logger.info(f"Saved: {filename}")
    else:
        logger.error(f"Error downloading {url}: {response.status_code}")


def search_matches(
    file: Path,
    companies: List[str],
    source_name: str,
    ext: str,
):
    """Determines the file type and calls the appropriate match function."""
    if ext == ".csv":
        return _search_csv(file, companies, source_name)
    elif ext == ".xml":
        return _search_xml(file, companies, source_name)
    elif ext == ".html":
        return _search_html(file, companies, source_name)
    else:
        logger.info("This format is not supported")
        return []


def _search_csv(
    file: Path,
    companies: List[str],
    source_name: str,
):
    """Searches for company matches in a sanctions list CSV file."""
    try:
        df = pd.read_csv(
            file,
            encoding="utf-8",
            low_memory=False,
            header=None,
        )
    except Exception:
        df = pd.read_csv(
            file,
            encoding="latin1",
            low_memory=False,
            header=None,
        )
    if source_name == "OFAC":
        candidates = df[1].astype(str).tolist()
    else:
        candidates = df.astype(str).agg(" ".join, axis=1).tolist()

    normalize_companies = normalize_company_name(companies)
    found = []
    for c in normalize_companies:
        if any(is_similar(c, candidate) for candidate in candidates):
            found.append(c)
    return found


def _search_xml(
    file: Path,
    companies: List[str],
    source_name: str,
):
    """Searches for company matches in a sanctions list XML file."""
    root = ET.parse(file).getroot()
    if source_name == "UK":
        candidates = []
        for name_elem in root.findall(".//Names/Name/Name6"):
            if name_elem.text:
                candidates.append(name_elem.text.strip())
    elif source_name == "UN" or source_name == "UN-SC":
        candidates = []
        for individual in root.findall(".//INDIVIDUAL"):
            first_name = individual.findtext("FIRST_NAME")
            second_name = individual.findtext("SECOND_NAME")
            if first_name:
                candidates.append(first_name.strip())
            if second_name:
                candidates.append(second_name.strip())
            for alias in individual.findall("INDIVIDUAL_ALIAS"):
                alias_name = alias.findtext("ALIAS_NAME")
                if alias_name and alias_name.strip():
                    candidates.append(alias_name.strip())
    else:
        text = ET.tostring(root, encoding="utf-8", method="text").decode(
            "utf-8"
        )
        candidates = [
            line.strip() for line in text.splitlines() if line.strip()
        ]
    normalize_companies = normalize_company_name(companies)
    found = []
    for c in normalize_companies:
        if any(is_similar(c, candidate) for candidate in candidates):
            found.append(c)
    return found


def _search_html(
    file: Path,
    companies: List[str],
    source_name: str,
):
    """Searches for company matches in a sanctions list HTML file."""
    text = file.read_text(encoding="utf-8", errors="ignore")
    if source_name == "EU-Tracker":
        soup = BeautifulSoup(text, "html.parser")
        candidates = [a["title"] for a in soup.select("ul li a[title]")]
    else:
        candidates = text.splitlines()
    normalize_companies = normalize_company_name(companies)
    found = []
    for c in normalize_companies:
        if any(is_similar(c, candidate) for candidate in candidates):
            found.append(c)
    return found
