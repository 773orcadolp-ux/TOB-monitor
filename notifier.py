"""Slack通知モジュール"""

import requests
import logging

logger = logging.getLogger(__name__)

CONDITION_COLOR = {
    "条件1": "#FF6B6B",
    "条件2": "#FF9F1C",
}

CONDITION_EMOJI = {
    "条件1": "🏢",
    "条件2": "⏰",
}


def build_attachment(detection: dict) -> dict:
    condition = detection.get("condition", "")
    emoji = CONDITION_EMOJI.get(condition, "🔍")
    color = CONDITION_COLOR.get(condition, "#cccccc")

    if condition == "条件1":
        fields = [
            {"title": "法人名", "value": detection.get("company_name", "-"), "short": True},
            {"title": "一致した監視先", "value": detection.get("matched_watcher", "-"), "short": True},
            {"title": "設立日", "value": detection.get("assignment_date", "-"), "short": True},
            {"title": "法人番号", "value": detection.get("corporate_number", "-"), "short": True},
            {"title": "住所", "value": detection.get("address", "-"), "short": False},
        ]
    else:  # 条件2
        fields = [
            {"title": "提出者", "value": detection.get("filer_name", "-"), "short": True},
            {"title": "対象会社", "value": detection.get("subject_company", "-") or "—", "short": True},
            {"title": "保有基準日", "value": detection.get("base_date", "-"), "short": True},
            {"title": "遅延営業日数", "value": f"{detection.get('business_days_late', '-')}営業日遅延", "short": True},
            {"title": "実際の提出日時", "value": detection.get("submit_datetime", "-"), "short": True},
        ]

    source_url = detection.get("source_url", "")
    footer = f"<{source_url}|ソースを確認 ↗>" if source_url else ""

    return {
        "color": color,
        "title": f"{emoji} TOB予兆検知: {detection.get('condition_detail', condition)}",
        "fields": fields,
        "footer": footer,
        "mrkdwn_in": ["text", "fields"],
    }


def send_slack_notification(detections: list, webhook_url: str) -> bool:
    if not detections or not webhook_url:
        return False

    payload = {
        "text": f"🚨 *TOB予兆モニター: {len(detections)}件の新規検知*",
        "attachments": [build_attachment(d) for d in detections],
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code == 200:
            logger.info(f"Slack通知成功: {len(detections)}件")
            return True
        else:
            logger.error(f"Slack通知失敗: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Slack通知エラー: {e}")
        return False
