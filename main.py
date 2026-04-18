edinet_api_key = os.environ.get("EDINET_API_KEY", "")
nta_api_key = os.environ.get("NTA_API_KEY", "")
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")

if not edinet_api_key:
    logger.warning("EDINET_API_KEY が未設定のため条件2をスキップします")

seen_ids = set(load_json(SEEN_IDS_FILE, []))
all_new_detections = []

# 条件1: NTA
try:
    from detectors.nta import run_detection as nta_detect
    mode = "API版" if nta_api_key else "スクレイピング版"
    logger.info(f"条件1（NTA {mode}）実行中...")
    nta_results = nta_detect(api_key=nta_api_key or None, lookback_days=1)
except Exception as e:
    logger.error(f"NTA検知エラー: {e}")
    nta_results = []

# 条件2: EDINET（遅延提出）
try:
    from detectors.edinet import run_detection as edinet_detect
    logger.info("条件2（EDINET 遅延提出）実行中...")
    edinet_results = edinet_detect(api_key=edinet_api_key, lookback_days=1)
except Exception as e:
    logger.error(f"EDINET検知エラー: {e}")
    edinet_results = []

# 新規のみ抽出
for detection in nta_results + edinet_results:
    det_id = make_detection_id(detection)
    if det_id not in seen_ids:
        detection["detected_at"] = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        detection["id"] = det_id
        all_new_detections.append(detection)
        seen_ids.add(det_id)

logger.info(f"新規検知: {len(all_new_detections)}件")

if all_new_detections:
    existing = load_json(RESULTS_FILE, [])
    updated = (all_new_detections + existing)[:500]
    save_json(RESULTS_FILE, updated)

    if slack_webhook_url:
        from notifier import send_slack_notification
        send_slack_notification(all_new_detections, slack_webhook_url)
else:
    if not RESULTS_FILE.exists():
        save_json(RESULTS_FILE, [])

save_json(SEEN_IDS_FILE, list(seen_ids)[-10000:])
logger.info(f"TOB予兆モニター 完了: {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S JST')}")
