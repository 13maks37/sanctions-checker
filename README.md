# 🚨 Sanctions Bot

**Sanctions Bot** is a Telegram bot built with [aiogram](https://docs.aiogram.dev/) for checking company names against international sanctions lists. It accepts an Excel file with a list of companies, compares them against official sources (OFAC, EU, UN, UK, and others), and returns the results in Excel format.

---

## 🛠️ Technologies Used

- Python 3.12  
- Aiogram 3  
- Docker + Docker Compose  
- PostgreSQL 16  
- Redis 7  
- SQLAlchemy 2 + Alembic  
- Pandas, Openpyxl  
- RapidFuzz (for fuzzy name matching)  
- BeautifulSoup (for HTML source parsing)

---

## 🌐 Sanctions Data Sources

The bot fetches and processes data from the following official sources:

| Source         | Format | Link |
|----------------|--------|------|
| **OFAC (USA)** | `.csv` | [Download](https://www.treasury.gov/ofac/downloads/sdn.csv) |
| **EU**         | `.xml` | [Download](https://ec.europa.eu/external_relations/cfsp/sanctions/list/version4/global/global.xml) |
| **UK**         | `.xml` | [Download](https://assets.publishing.service.gov.uk/media/6852dd9adf3015b374b73638/UK_Sanctions_List.xml) |
| **UN**         | `.xml` | [Download](https://scsanctions.un.org/resources/xml/en/consolidated.xml) |
| **EU Tracker** | `.html`| [Download](https://data.europa.eu/apps/eusanctionstracker/entities/) |
| **UN-SC**      | `.xml` | [Download](https://scsanctions.un.org/resources/xml/en/consolidated.xml) |

---

## 🧑‍💻 Authors

- [burvelandrei](https://github.com/burvelandrei)  
- [13maks37](https://github.com/13maks37)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.


