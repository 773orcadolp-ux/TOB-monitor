“””
EDINET 大量保有報告書 検知モジュール
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
検知対象:
大量保有報告書（新規・変更・特例）の「遅延提出」
= 保有基準日（periodStart）から法定期限（5営業日）を超えて提出されたもの

過去分の遡り検知も可能（lookback_daysで調整）

APIキー:
Ocp-Apim-Subscription-Key ヘッダーで送信（クエリパラメータ不可）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
“””

import re
import time
import logging
import requests
from datetime import date, timedelta, datetime

logger = logging.getLogger(__name__)

EDINET_API_BASE = “https://disclosure.edinet-fsa.go.jp/api/v2”

# 大量保有報告書の formCode一覧（ordinanceCode=43 が大量保有）

# 新規・変更・特例をすべて対象とする

TAIRYOU_HOYUU_FORM_CODES = {
“43A000”: “大量保有報告書（新規）”,
“43A001”: “大量保有報告書（変更）”,
“43A002”: “大量保有報告書（特例）”,
“43A003”: “大量保有報告書（特例変更）”,
}

# 法定期限: 保有基準日から5営業日以内

LEGAL_DEADLINE_BUSINESS_DAYS = 5

# 遅延とみなす閾値（法定期限を1日でも超えたら検知）

LATE_THRESHOLD_DAYS = LEGAL_DEADLINE_BUSINESS_DAYS

def count_business_days(start: date, end: date) -> int:
“”“start（含まない）からend（含む）までの営業日数をカウント”””
count = 0
current = start + timedelta(days=1)
while current <= end:
if current.weekday() < 5:  # 月〜金
count += 1
current += timedelta(days=1)
return count

def parse_date(date_str: str) -> date | None:
“”“YYYY-MM-DD / YYYYMMDD / YYYY/MM/DD 形式をdateに変換”””
if not date_str:
return None
for fmt in (”%Y-%m-%d”, “%Y%m%d”, “%Y/%m/%d”):
try:
return datetime.strptime(date_str[:10], fmt).date()
except ValueError:
continue
return None

def extract_base_date_from_description(doc_description: str) -> date | None:
“””
docDescriptionから保有基準日を推定する。
例: “大量保有報告書－保有割合5%超（2024年03月15日現在）”
→ 2024-03-15
periodStartが空の場合のフォールバック。
“””
if not doc_description:
return None
# 「YYYY年MM月DD日」形式を探す
m = re.search(r”(\d{4})年(\d{1,2})月(\d{1,2})日”, doc_description)
if m:
try:
return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
except ValueError:
pass
# 「YYYY-MM-DD」形式を探す
m = re.search(r”(\d{4}-\d{2}-\d{2})”, doc_description)
if m:
return parse_date(m.group(1))
return None

def fetch_edinet_documents(target_date: str, api_key: str) -> list:
“””
EDINET書類一覧APIを叩いて指定日の書類一覧を返す。
APIキーは Ocp-Apim-Subscription-Key ヘッダーで送信。
“””
headers = {}
if api_key:
headers[“Ocp-Apim-Subscription-Key”] = api_key

```
try:
    resp = requests.get(
        f"{EDINET_API_BASE}/documents.json",
        params={"date": target_date, "type": 2},
        headers=headers,
        timeout=30,
    )
    if resp.status_code == 401:
        logger.error("EDINET APIキーが無効または未設定です（401）")
        return []
    if resp.status_code != 200:
        logger.warning(f"EDINET API {target_date}: status={resp.status_code}")
        return []
    return resp.json().get("results", []) or []
except Exception as e:
    logger.error(f"EDINET API エラー ({target_date}): {e}")
    return []
```

def run_detection(api_key: str, lookback_days: int = 1) -> list:
“””
大量保有報告書の遅延提出を検知する。

```
Parameters
----------
api_key : str
    EDINET APIキー（アプリケーションID）
lookback_days : int
    何日前まで遡るか。
    - 通常運用: 1〜2
    - 初回・過去分洗い出し: 30〜90（GitHub Actionsの実行時間に注意）

Returns
-------
list of dict  検知結果
"""
if not api_key:
    logger.warning("EDINET_API_KEY が未設定のため条件2をスキップします")
    return []

detections = []
# 当日 + lookback_days日前まで
target_dates = [
    (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    for i in range(lookback_days + 1)
]

for target_date in target_dates:
    logger.info(f"EDINET検知: {target_date} の書類を取得中")
    docs = fetch_edinet_documents(target_date, api_key)
    time.sleep(1)  # レート制限対策

    for doc in docs:
        form_code = doc.get("formCode", "")
        if form_code not in TAIRYOU_HOYUU_FORM_CODES:
            continue

        doc_id          = doc.get("docID", "")
        filer_name      = doc.get("filerName", "")
        subject_company = doc.get("issuerName", "") or doc.get("subjectEdinetCode", "")
        submit_datetime = doc.get("submitDateTime", "")
        period_start    = doc.get("periodStart", "")
        doc_description = doc.get("docDescription", "")

        submit_date = parse_date(submit_datetime)
        if not submit_date:
            continue

        # 保有基準日を取得（periodStart → docDescriptionの順でフォールバック）
        base_date = parse_date(period_start)
        if not base_date:
            base_date = extract_base_date_from_description(doc_description)
        if not base_date:
            # 基準日が特定できなければスキップせず、提出日ベースで記録
            logger.debug(f"基準日不明: {doc_id} / {filer_name} → 遅延判定スキップ")
            continue

        business_days = count_business_days(base_date, submit_date)

        if business_days > LATE_THRESHOLD_DAYS:
            detection = {
                "condition": "条件2",
                "condition_detail": (
                    f"大量保有報告書の遅延提出 — "
                    f"{TAIRYOU_HOYUU_FORM_CODES[form_code]}、"
                    f"基準日から {business_days} 営業日後に提出"
                    f"（法定期限: {LEGAL_DEADLINE_BUSINESS_DAYS}営業日以内）"
                ),
                "doc_id":            doc_id,
                "form_code":         form_code,
                "form_name":         TAIRYOU_HOYUU_FORM_CODES[form_code],
                "filer_name":        filer_name,
                "subject_company":   subject_company,
                "base_date":         str(base_date),
                "submit_datetime":   submit_datetime,
                "business_days_late": business_days,
                "source_url": (
                    f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{doc_id}"
                ),
            }
            detections.append(detection)
            logger.info(
                f"[条件2 HIT] {filer_name} → {subject_company or '不明'} / "
                f"基準日:{base_date} 提出:{submit_datetime[:10]} "
                f"({business_days}営業日遅延)"
            )

logger.info(f"EDINET検知完了: {len(detections)}件")
return detections
```
