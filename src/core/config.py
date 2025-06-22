from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    MAIN_MENU_BOT: dict = {
        "/start": "Start the bot",
        "/menu": "Main menu",
        "/help": "Technical support",
    }

    TMP_DIR_BOT: str = "tmp/bot_uploads"
    TMP_DIR_SCRAPER: str = "tmp/scraper_uploads"
    TMP_DIR_RESULT: str = "tmp/scraper_result"

    SANCTIONS_SOURCES: dict[str, dict] = {
        "OFAC": {
            "url": "https://www.treasury.gov/ofac/downloads/sdn.csv",
            "ext": ".csv",
        },
        "EU": {
            "url": (
                "https://ec.europa.eu/external_relations/cfsp/sanctions/"
                "list/version4/global/global.xml"
            ),
            "ext": ".xml",
        },
        "UK": {
            "url": (
                "https://assets.publishing.service.gov.uk/media/"
                "6852dd9adf3015b374b73638/UK_Sanctions_List.xml"
            ),
            "ext": ".xml",
        },
        "UN": {
            "url": (
                "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
            ),
            "ext": ".xml",
        },
        "EU-Tracker": {
            "url": "https://data.europa.eu/apps/eusanctionstracker/entities/",
            "ext": ".html",
        },
        "EU-SanctionsMap": {
            "url": "https://sanctionsmap.eu/#/main",
            "ext": ".html",
        },
        "UN-SC": {
            "url": (
                "https://main.un.org/securitycouncil/en/sanctions/information"
            ),
            "ext": ".html",
        },
    }

    model_config = ConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
