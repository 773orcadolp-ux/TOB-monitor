import requests
import logging
from datetime import date, timedelta, datetime

logger = logging.getLogger(__name__)

EDINET_API_BASE = "https://disclosure.edinet-fsa.go.jp/api/v2"

TAIRYOU_HOYUU_FORM_CODES = {
    "120": "大量保有報告書（新規）",
    "121": "大量保有報告書（変更）",
    "122": "大量保有報告書（特例）",
    "123": "大量保有報告書（特例変更）",
}

LATE_SUBMISSION_THRESHOLD_DAYS = 5


def count_business_days(start, end):
    count = 0
    current = start
    while current < end:
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


def fetch_edinet_documents(target_date, api_key):
    try:
        params = {"date": target_date, "type": 2, "Subscription-Key": api_key}
        resp = requests.get(f"{EDINET_API_BASE}/documents.json", params=params, timeout=30)
        if resp.status_code != 200:
            return []
        return resp.json().get("results", [])
    except Exception as e:
        logger.error(f"EDINET API error: {e}")
        return []


def run_detection(api_key, lookback_days=1):
    detections = []
    target_dates = [
        (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(lookback_days + 2)
    ]
    for target_date in target_dates:
        logger.info(f"EDINET検知: {target_date}の書類を取得中")
        for doc in fetch_edinet_documents(target_date, api_key):
            form_code = doc.get("formCode", "")
            if form_code not in TAIRYOU_HOYUU_FORM_CODES:
                continue
            doc_id = doc.get("docID", "")
            filer_name = doc.get("filerName", "")
            subject_company = doc.get("issuerName", "")
            submit_datetime = doc.get("submitDateTime", "")
            period_start = doc.get("periodStart", "")
            submit_date = parse_date(submit_datetime)
            base_date = parse_date(period_start)
            if not (submit_date and base_date):
                continue
            business_days = count_business_days(base_date, submit_date)
            if business_days > LATE_SUBMISSION_THRESHOLD_DAYS:
                detections.append({
                    "condition": "条件2",
                    "condition_detail": f"大量保有報告書の遅延提出（基準日から{business_days}営業日後に提出）",
                    "doc_id": doc_id,
                    "filer_name": filer_name,
                    "subject_company": subject_company,
                    "submit_datetime": submit_datetime,
                    "base_date": period_start,
                    "business_days_late": business_days,
                    "source_url": f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?S1000{doc_id}",
                })
                logger.info(f"[条件2 HIT] {filer_name} / {business_days}営業日遅延")
    logger.info(f"EDINET検知完了: {len(detections)}件")
    return detections
