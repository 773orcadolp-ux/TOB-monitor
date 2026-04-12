import re
import time
import logging
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

from pe_addresses import get_all_addresses

logger = logging.getLogger(__name__)

NTA_RESULT_URL = "https://www.houjin-bangou.nta.go.jp/kekka-ichiran.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TOBMonitor/1.0; research purpose)",
    "Accept-Language": "ja,en;q=0.9",
}

EXCLUDED_SUFFIXES = [
    "株式会社", "合同会社", "合名会社", "合資会社", "有限会社",
    "一般社団法人", "一般財団法人", "特定非営利活動法人", "NPO法人",
    "ホールディングス", "holdings", "Holdings", "HOLDINGS",
    "特別目的会社", "LLC", "Inc", "Corp", "Ltd", "GK",
    "投資事業有限責任組合", "有限責任事業組合",
]

ALPHA_ONLY_PATTERN = re.compile(r'^[A-Za-z0-9\s\-\.]+$')


def strip_legal_suffix(name):
    stripped = name
    for suffix in EXCLUDED_SUFFIXES:
        stripped = stripped.replace(suffix, "")
    return stripped.strip()


def is_alpha_numeric_name(company_name):
    core_name = strip_legal_suffix(company_name)
    if not core_name:
        return False
    return bool(ALPHA_ONLY_PATTERN.match(core_name))


def fetch_corporations_by_address(address, established_from):
    results = []
    try:
        params = {
            "selMode": "2",
            "txtAddress": address,
            "selKind": "1",
            "txtSetupDateFrom": established_from.replace("-", "/"),
            "txtSetupDateTo": date.today().strftime("%Y/%m/%d"),
            "btn​​​​​​​​​​​​​​​​

