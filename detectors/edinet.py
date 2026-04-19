import re
import time
import logging
import requests
from datetime import date, timedelta, datetime

logger = logging.getLogger(__name__)

EDINET_API_BASE = "https://disclosure.edinet-fsa.go.jp/api/v2"

TAIRYOU_HOYUU_FORM_CODES = {
    "43A000": "大量保有報告書（新規）",
    "43A001": "大量保有報告書（変更）",
    "43A002": "大量保有報告書（特例）",
    "43A003": "大量保有報告書（特例変更）",
}

LEGAL_DEADLINE_BUSINESS_DAYS = 5
LATE_THRESHOLD_DAYS = LEGAL_DEADLINE_BUSINESS_DAYS


def count_business_days(start, end):
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str[:10], fmt).date()
        except ValueError:
            continue
    return None


def extract_base_date_from_description(doc_description):
    if not doc_description:
        return None
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", doc_description)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    m = re.search(r"(\d{4}-\d{2}-\d{2})", doc_description)
    if m:
        return parse_date(m.group(1))
    return None


def fetch_edinet_documents(target_date, api_key):
    headers = {}
    if api_key:
        headers["Ocp-Apim-Subscription-Key"] = api_key
    try:
        resp = requests.get(
            f"{EDINET_API_BASE}/documents.json",
            params={"date": target_date, "type": 2},
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 401:
            logger.error("EDINET APIキーが無効です（401）")
            return []
        if resp.status_code != 200:
            logger.warning(f"EDINET API {target_date}: status={resp.status_code}")
            return []
        return resp.json().get("results", []) or []
    except Exception as e:
        logger.error(f"EDINET API エラー ({target_date}): {e}")
        return []


def run_detection(api_key, lookback_days=1):
    if not api_key:
        logger.warning("EDINET_API_KEY が未設定のためスキップします")
        return []

    detections = []
    target_dates = [
        (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(lookback_days + 1)
    ]

    for target_date in target_dates:
        logger.info(f"EDINET検知: {target_date} の書類を取得中")
        docs = fetch_edinet_documents(target_date, api_key)
        time.sleep(1)

        for doc in docs:
            form_code = doc.get("formCode", "")
            if form_code not in TAIRYOU_HOYUU_FORM_CODES:
                continue
            logger.info(
                f"formCode={form_code} "
                f"filer={doc.get('filerName','')[:20]} "
                f"periodStart={doc.get('periodStart','EMPTY')} "
                f"submitDateTime={doc.get('submitDateTime','')}"
            )

    logger.info(f"EDINET検知完了: {len(detections)}件")
    return detections
