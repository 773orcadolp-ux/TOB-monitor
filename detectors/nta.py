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
            "btnSearch": "検索",
        }
        resp = requests.get(NTA_RESULT_URL, params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table.result-table tr")
        for row in rows[1:]:
            cols = row.select("td")
            if len(cols) < 5:
                continue
            results.append({
                "corporate_number": cols[0].get_text(strip=True),
                "company_name": cols[1].get_text(strip=True),
                "address": cols[2].get_text(strip=True),
                "assignment_date": cols[3].get_text(strip=True),
            })
    except Exception as e:
        logger.error(f"NTA fetch error ({address}): {e}")
    return results


def run_detection(api_key=None, lookback_days=1):
    all_addresses = get_all_addresses()
    established_from = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    detections = []

    for entry in all_addresses:
        address = entry["address"]
        watcher_name = entry["name"]
        logger.info(f"NTA検知: {watcher_name} / {address}")

        corps = fetch_corporations_by_address(address, established_from)
        time.sleep(1)

        for corp in corps:
            if not is_alpha_numeric_name(corp["company_name"]):
                continue
            detections.append({
                "condition": "条件1",
                "condition_detail": f"英字法人の新規設立（{watcher_name}の住所近辺）",
                "company_name": corp["company_name"],
                "corporate_number": corp["corporate_number"],
                "address": corp["address"],
                "assignment_date": corp["assignment_date"],
                "matched_watcher": watcher_name,
                "source_url": f"https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo={corp['corporate_number']}",
            })
            logger.info(f"[条件1 HIT] {corp['company_name']} / {watcher_name}")

    logger.info(f"NTA検知完了: {len(detections)}件")
    return detections
