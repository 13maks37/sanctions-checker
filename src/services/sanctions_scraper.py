import requests
import re
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from tabulate import tabulate
from tqdm import tqdm
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from rapidfuzz.fuzz import partial_ratio


SANCTIONS_URLS = {
    "OFAC": "https://www.treasury.gov/ofac/downloads/sdn.csv",
    "EU": "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=fullSanctionsList.xml",
    "UK": "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1202359/Sanctions_Consolidated_List.csv",
    "UN": "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
    "BIS": "https://bis.doc.gov/index.php/documents/denied-persons-list/1140-dpl-pdf/file",
    "EU-Tracker": "https://data.europa.eu/apps/eusanctionstracker/entities/",
    "EU-SanctionsMap": "https://sanctionsmap.eu/#/main",
    "UN-SC": "https://main.un.org/securitycouncil/en/sanctions/information",
}


def download_file(url: str, filename: Path):
    print(f"Загрузка: {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename.write_bytes(response.content)
        print(f"Сохранено: {filename}")
    else:
        print(f"Ошибка при загрузке {url}: {response.status_code}")


def normalize_company_name(company_names: str):
    """
    Normalizes the company name by removing the content in parentheses
    """
    normalize_names = []
    for name in company_names:
        name = re.sub(r"\s*\([^()]*\)", "", name).strip()
        name = re.sub(r"\s+", " ", name).strip()
        normalize_names.append(name)
    return normalize_names


def is_similar(a: str, b: str, threshold: float = 85) -> bool:
    ratio = partial_ratio(a.lower(), b.lower())
    return ratio >= threshold


def load_companies_from_excel(filepath: str) -> List[str]:
    df = pd.read_excel(filepath)
    return df["Company"].dropna().astype(str).tolist()


def search_company_in_csv(file: Path, companies: List[str]) -> List[str]:
    try:
        df = pd.read_csv(file, encoding="utf-8", low_memory=False, header=None)
    except Exception:
        df = pd.read_csv(
            file, encoding="latin1", low_memory=False, header=None
        )
    company_names = df[1].astype(str).tolist()
    normalize_companies = normalize_company_name(company_names=companies)
    return [
        c
        for c in normalize_companies
        if any(is_similar(c, name) for name in company_names)
    ]


def search_company_in_xml(file: Path, companies: List[str]) -> List[str]:
    root = ET.parse(file).getroot()
    text = ET.tostring(root, encoding="utf-8", method="text").decode("utf-8")
    return [
        c
        for c in companies
        if any(is_similar(c, line) for line in text.splitlines())
    ]


def search_company_in_html(file: Path, companies: List[str]) -> List[str]:
    text = file.read_text(encoding="utf-8", errors="ignore")
    return [
        c
        for c in companies
        if any(is_similar(c, line) for line in text.splitlines())
    ]


def get_next_output_filename(base: str = "suppliers_output.xlsx") -> str:
    i = 1
    while Path(base).exists():
        base = f"suppliers_output_{i}.xlsx"
        i += 1
    return base


def save_results_to_excel(
    results: dict, companies: List[str], output_file: str
):
    data = []
    for company in companies:
        status = {
            key: "Yes" if company in matches else "No"
            for key, matches in results.items()
        }
        matched_lists = [k for k, v in status.items() if v == "Yes"]
        info = (
            f"Есть санкции — {matched_lists}"
            if matched_lists
            else "Нет санкций"
        )
        data.append({"Company": company, **status, "Sanctions Info": info})
    df_out = pd.DataFrame(data)
    df_out.to_excel(output_file, index=False)

    wb = load_workbook(output_file)
    ws = wb.active
    fill_yes = PatternFill(
        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
    )
    fill_no = PatternFill(
        start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"
    )
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=ws.max_column - 1):
        for cell in row:
            if cell.value == "Yes":
                cell.fill = fill_yes
            elif cell.value == "No":
                cell.fill = fill_no
    wb.save(output_file)
    print(f"Результаты сохранены в файл: {output_file}")


def search_company_in_opensanctions(companies: List[str]) -> List[str]:
    found = []
    for company in tqdm(companies, desc="OpenSanctions API"):
        try:
            url = f"https://api.opensanctions.org/match?q={company}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and res.json().get("match") is not None:
                found.append(company)
        except Exception as e:
            print(f"[!] Ошибка при запросе к OpenSanctions: {e}")
    return found


def scrape_sanctions_companies():
    input_file = "suppliers.xlsx"
    output_file = get_next_output_filename()
    companies = load_companies_from_excel(input_file)
    results = {}
    Path("sanctions").mkdir(exist_ok=True)

    for name, url in tqdm(
        SANCTIONS_URLS.items(), desc="Обработка списков", unit="источник"
    ):
        ext = (
            ".html"
            if "Tracker" in name or "Map" in name or "UN-SC" in name
            else (".xml" if name in ["EU", "UN"] else ".csv")
        )
        path = Path(f"sanctions/{name}{ext}")
        try:
            download_file(url, path)
            if ext == ".csv":
                matches = search_company_in_csv(
                    path, tqdm(companies, desc=f"{name}")
                )
            elif ext == ".xml":
                matches = search_company_in_xml(
                    path, tqdm(companies, desc=f"{name}")
                )
            else:
                matches = search_company_in_html(
                    path, tqdm(companies, desc=f"{name}")
                )
            results[name] = matches
        except Exception as e:
            print(f"[!] Ошибка при обработке {name}: {e}")
            results[name] = []

    headers = ["Company"] + list(SANCTIONS_URLS.keys()) + ["Sanctions Info"]
    table_data = []
    for company in companies:
        row = [company]
        matched = []
        normalized_company = normalize_company_name([company])[0]
        for key in SANCTIONS_URLS:
            if normalized_company in results.get(key, []):
                row.append("Yes")
                matched.append(key)
            else:
                row.append("No")
        row.append(f"Есть санкции — {matched}" if matched else "Нет санкций")
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Проверка через OpenSanctions API
    try:
        matches = search_company_in_opensanctions(companies)
        results["OpenSanctions"] = matches
    except Exception as e:
        print(f"[!] Ошибка OpenSanctions API: {e}")
        results["OpenSanctions"] = []

    save_results_to_excel(results, companies, output_file)
    input("\nПроверка завершена. Нажмите Enter для выхода...")


if __name__ == "__main__":
    scrape_sanctions_companies()
