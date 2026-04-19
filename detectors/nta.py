import re
import time
import logging
import requests
from datetime import date, timedelta

from pe_addresses import get_all_addresses

logger = logging.getLogger(__name__)

NTA_API_URL = "https://api.houjin-bangou.nta.go.jp/4/name"

SEARCH_NAMES = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y", "Z",
]

EXCLUDED_SUFFIXES = [
    "株式会社", "合同会社", "合名会社", "合資会社", "有限会社",
    "一般社団法人", "一般財団法人", "特定非営利活動法人", "NPO法人",
    "ホールディングス", "holdings", "Holdings", "HOLDINGS",
    "特別目的会社", "LLC", "Inc", "Corp", "Ltd", "GK",
    "投資事業有限責任組合", "有限責任事業組合",
]

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
    stripped = re.sub(r'[\s\u3000]+', '', stripped)
    return stripped.strip()


def is_alpha_numeric_only(name):
    core = strip_legal_suffix(name)
    return bool(core) and bool(re.fullmatch(r'[A-Za-z0-9]+', core))


def fetch_corps_by_name(search_char, pref_code, from_date, api_key):
    results = []
    try:
        params = {
            "id": api_key,
            "name": search_char,
            "mode": "2",
            "target": "1",
            "address": pref_code,
            "kind": "03",
            "from": from_date,
            "to": date.today().strftime("%Y-%m-%d"),
            "type": "12",
            "divide": "1",
        }
        resp = requests.get(NTA_API_URL, params=params, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"NTA API {search_char} pref={pref_code}: status={resp.status_code}")
            return []
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        for corp in root.findall("corporation"):
            results.append({
                "corporate_number": corp.findtext("corporateNumber") or "",
                "company_name": corp.findtext("name") or "",
                "address": (
                    (corp.findtext("prefectureName") or "") +
                    (corp.findtext("cityName") or "") +
                    (corp.findtext("streetNumber") or "")
                ),
                "assignment_date": corp.findtext("assignmentDate") or "",
            })
    except Exception as e:
        logger.error(f"NTA API error ({search_char}, pref={pref_code}): {e}")
    return results


def run_detection(api_key=None, lookback_days=1):
    if not api_key:
        logger.warning("NTA_API_KEY が未設定のため条件1をスキップします")
        return []

    all_addresses = get_all_addresses()
    from_date = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    watch_list = []
    for entry in all_addresses:
        watch_list.append({
            "name": entry["name"],
            "address": entry["address"],
            "pref_code": get_prefecture_code(entry["address"]),
        })

    pref_codes = list(set(w["pref_code"] for w in watch_list))

    detections = []
    seen_corp_nums = set()

    for pref_code in pref_codes:
        pref_watches = [w for w in watch_list if w["pref_code"] == pref_code]

        for search_char in SEARCH_NAMES:
            logger.info(f"NTA検索: {search_char} / 都道府県={pref_code}")
            corps = fetch_corps_by_name(search_char, pref_code, from_date, api_key)
            time.sleep(0.3)

            for corp in corps:
                corp_num = corp["corporate_number"]
                if corp_num in seen_corp_nums:
                    continue
                if not is_alpha_numeric_only(corp["company_name"]):
                    continue

                matched_watcher = None
                for w in pref_watches:
                    if w["address"] in corp["address"]:
                        matched_watcher = w["name"]
                        break

                if not matched_watcher:
                    continue

                seen_corp_nums.add(corp_num)
                detections.append({
                    "condition": "条件1",
                    "condition_detail": f"英字法人の新規設立（{matched_watcher}の住所近辺）",
                    "company_name": corp["company_name"],
                    "corporate_number": corp_num,
                    "address": corp["address"],
                    "assignment_date": corp["assignment_date"],
                    "matched_watcher": matched_watcher,
                    "source_url": f"https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo={corp_num}",
                })
                logger.info(f"[条件1 HIT] {corp['company_name']} / {matched_watcher}")

    logger.info(f"NTA検知完了: {len(detections)}件")
    return detections
