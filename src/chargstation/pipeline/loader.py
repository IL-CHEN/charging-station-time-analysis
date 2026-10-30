# -*- coding: utf-8 -*-
"""数据加载器：批量读取 data/raw 下的原始 ACN JSON 文件。"""

import glob
import json
import os

import pandas as pd

from chargstation.config import RAW_DATA_DIR


class DataLoader:
    """仅负责批量读取原始 JSON 数据并合并为 DataFrame。"""

    def __init__(self, pattern: str = "acn_data_*.json"):
        self.file_pattern = os.path.join(str(RAW_DATA_DIR), pattern)

    def load_all(self) -> pd.DataFrame:
        file_list = sorted(glob.glob(self.file_pattern))
        if not file_list:
            raise FileNotFoundError(f"未找到数据文件，请检查：{RAW_DATA_DIR}")

        print(f"发现 {len(file_list)} 个数据文件")
        all_sessions = []
        for file_path in file_list:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                all_sessions.extend(raw_data["_items"])
            except Exception as exc:  # noqa: BLE001
                print(f"跳过文件 {os.path.basename(file_path)}：{exc}")
                continue

        df_raw = pd.DataFrame(all_sessions)
        print(f"原始数据加载完成：{len(df_raw)} 条记录")
        return df_raw
