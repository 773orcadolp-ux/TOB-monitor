"""TOB予兆モニター メイン実行スクリプト"""

import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9))
RESULTS_FILE = Path("results/detections.json")
SEEN_IDS_FILE = Path("results/seen_ids.json")


def load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=​​​​​​​​​​​​​​​​
