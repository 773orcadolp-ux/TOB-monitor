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

            doc_id = doc.get("docID", "")
            filer_name = doc.get("filerName", "")
            subject_company = doc.get("issuerName", "") or doc.get("subjectEdinetCode", "")
            submit_datetime = doc.get("submitDateTime", "")
            period_start = doc.get("periodStart", "")
            doc_description = doc.get("docDescription", "")

            submit_date = parse_date(submit_datetime)
            if not submit_date:
                continue

            base_date = parse_date(period_start)
            if not base_date:
                base_date = extract_base_date_from_description(doc_description)
            if not base_date:
                logger.debug(f"基準日不明: {doc_id} / {filer_name}")
                continue

            business_days = count_business_days(base_date, submit_date)

            if business_days > LATE_THRESHOLD_DAYS:
                detection = {
                    "condition": "条件2",
                    "condition_detail": (
                        f"大量保有報告書の遅延提出 "
                        f"{TAIRYOU_HOYUU_FORM_CODES[form_code]} "
                        f"基準日から{business_days}営業日後に提出"
                    ),
                    "doc_id": doc_id,
                    "form_code": form_code,
                    "form_name": TAIRYOU_HOYUU_FORM_CODES[form_code],
                    "filer_name": filer_name,
                    "subject_company": subject_company,
                    "base_date": str(base_date),
                    "submit_datetime": submit_datetime,
                    "business_days_late": business_days,
                    "source_url": f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{doc_id}",
                }
                detections.append(detection)
                logger.info(
                    f"[条件2 HIT] {filer_name} / "
                    f"基準日:{base_date} 提出:{submit_datetime[:10]} "
                    f"({business_days}営業日遅延)"
                )

    logger.info(f"EDINET検知完了: {len(detections)}件")
    return detections
