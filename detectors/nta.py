import re
import time
import logging
import requests
from datetime import date, timedelta

from pe_addresses import get_all_addresses

logger = logging.getLogger(__name__)

NTA_API_URL = "https://api.houjin-bangou.nta.go.jp/4/name"

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


def fetch_corporations_by_address(address, established_from, api_key):
    results = []
    try:
        params = {
            "id": api_key,
            "address": address,
            "from": established_from.replace("-", ""),
            "to": date.today().strftime("%Y%m%d"),
            "kind": "01",
            "type": "02",
            "divide": "1",
        }
        resp = requests.get(NTA_API_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for corp in data.get("corporation", []) or []:
            results.append({
                "corporate_number": corp.get("corporateNumber", ""),
                "company_name": corp.get("name", ""),
                "address": (
                    corp.get("prefectureName", "") +
                    corp.get("cityName", "") +
                    corp.get("streetNumber", "")
                ),
                "assignment_date": corp.get("assignmentDate", ""),
            })
    except Exception as e:
        logger.error(f"NTA API error ({address}): {e}")
    return results


def run_detection(api_key=None, lookback_days=1):
    if not api_key:
        logger.warning("NTA_API_KEY が未設定のため条件1をスキップします")
        return []

    all_addresses = get_all_addresses()
    established_from = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    detections = []

    for entry in all_addresses:
        address = entry["address"]
        watcher_name = entry["name"]
        logger.info(f"NTA検知: {watcher_name} / {address}")

        corps = fetch_corporations_by_address(address, established_from, api_key)
        time.sleep(0.5)

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
