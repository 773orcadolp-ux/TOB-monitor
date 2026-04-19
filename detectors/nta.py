import re
import time
import logging
import requests
from datetime import date, timedelta

from pe_addresses import get_all_addresses

logger = logging.getLogger(__name__)

NTA_API_URL = "https://api.houjin-bangou.nta.go.jp/4/diff"

EXCLUDED_SUFFIXES = [
    "株式会社", "合同会社", "合名会社", "合資会社", "有限会社",
    "一般社団法人", "一般財団法人", "特定非営利活動法人", "NPO法人",
    "ホールディングス", "holdings", "Holdings", "HOLDINGS",
    "特別目的会社", "LLC", "Inc", "Corp", "Ltd", "GK",
    "投資事業有限責任組合", "有限責任事業組合",
]

ALPHA_ONLY_PATTERN = re.compile(r'^[A-Za-z0-9\s\-\.]+$')

PREFECTURE_CODE_MAP = {
    "北海道": "01", "青森県": "02", "岩手県": "03", "宮城県": "04",
    "秋田県": "05", "山形県": "06", "福島県": "07", "茨城県": "08",
    "栃木県": "09", "群馬県": "10", "埼玉県": "11", "千葉県": "12",
    "東京都": "13", "神奈川県": "14", "新潟県": "15", "富山県": "16",
    "石川県": "17", "福井県": "18", "山梨県": "19", "長野県": "20",
    "岐阜県": "21", "静岡県": "22", "愛知県": "23", "三重県": "24",
    "滋賀県": "25", "京都府": "26", "大阪府": "27", "兵庫県": "28",
    "奈良県": "29", "和歌山県": "30", "鳥取県": "31", "島根県": "32",
    "岡山県": "33", "広島県": "34", "山口県": "35", "徳島県": "36",
    "香川県": "37", "愛媛県": "38", "高知県": "39", "福岡県": "40",
    "佐賀県": "41", "長崎県": "42", "熊本県": "43", "大分県": "44",
    "宮崎県": "45", "鹿児島県": "46", "沖縄県": "47",
}


def get_prefecture_code(address):
    for pref, code in PREFECTURE_CODE_MAP.items():
        if address.startswith(pref):
            return code
    return "13"


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


def fetch_new_corporations(established_from, api_key, prefecture_code):
    results = []
    try:
        params = {
            "id": api_key,
            "from": established_from,
            "to": date.today().strftime("%Y-%m-%d"),
            "address": prefecture_code,
            "kind": "03",
            "type": "12",
            "divide": "1",
        }
        resp = requests.get(NTA_API_URL, params=params, timeout=20)
        resp.raise_for_status()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        for corp in root.findall("corporation"):
            corp_address = (
                (corp.findtext("prefectureName") or "") +
                (corp.findtext("cityName") or "") +
                (corp.findtext("streetNumber") or "")
            )
            results.append({
                "corporate_number": corp.findtext("corporateNumber") or "",
                "company_name": corp.findtext("name") or "",
                "address": corp_address,
                "assignment_date": corp.findtext("assignmentDate") or "",
            })
    except Exception as e:
        logger.error(f"NTA API error (prefecture={prefecture_code}): {e}")
    return results


def run_detection(api_key=None, lookback_days=1):
    if not api_key:
        logger.warning("NTA_API_KEY が未設定のため条件1をスキップします")
        return []

    all_addresses = get_all_addresses()
    established_from = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    detections = []

    pref_cache = {}
    for entry in all_addresses:
        address = entry["address"]
        watcher_name = entry["name"]
        pref_code = get_prefecture_code(address)

        if pref_code not in pref_cache:
            logger.info(f"NTA取得: 都道府県コード={pref_code}")
            pref_cache[pref_code] = fetch_new_corporations(
                established_from, api_key, pref_code
            )
            time.sleep(0.5)

        for corp in pref_cache[pref_code]:
            if not is_alpha_numeric_name(corp["company_name"]):
                continue
            detections.append({
                "condition": "条件1",
                "condition_detail": f"英字法人の新規設立（都道府県コード={pref_code}）",
                "company_name": corp["company_name"],
                "corporate_number": corp["corporate_number"],
                "address": corp["address"],
                "assignment_date": corp["assignment_date"],
                "matched_watcher": watcher_name,
                "source_url": f"https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo={corp['corporate_number']}",
            })
            logger.info(f"[条件1 HIT] {corp['company_name']} / {corp['address']}")

    logger.info(f"NTA検知完了: {len(detections)}件")
    return detections
