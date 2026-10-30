# -*- coding: utf-8 -*-
"""数据清洗与特征工程。"""

import os

import numpy as np
import pandas as pd
import pytz
from sklearn.preprocessing import LabelEncoder

from chargstation.config import OUTPUT_PROCESSED_DIR, JIANGSU_PARAMS


class DataProcessor:
    """负责数据清洗、特征工程、中间数据保存。"""

    TIME_COLS = ["connectionTime", "disconnectTime", "doneChargingTime"]
    # 特征列（与模型训练、特征重要性输出保持一致）
    FEATURE_COLS = [
        "connect_hour",
        "connect_weekday",
        "is_weekend",
        "is_jiangsu_peak",
        "stationID_encoded",
        "effective_charging_h",
    ]
    TARGET_COL = "kWhDelivered"

    def __init__(self):
        self.tz_ca = pytz.timezone("America/Los_Angeles")
        self.tz_js = pytz.timezone("Asia/Shanghai")
        self.le = LabelEncoder()

    def process(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """执行完整清洗与特征工程，返回清洗后的 DataFrame。"""
        df = df_raw.copy()

        # 1. 统一所有时间列的时区（ACN 原始数据为加州时区，统一转为江苏时区）
        for col in self.TIME_COLS:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].dt.tz is None:
                # 无时区信息时按加州时区本地化，再转到江苏时区
                df[col] = (
                    df[col]
                    .dt.tz_localize(self.tz_ca, ambiguous="NaT", nonexistent="NaT")
                    .dt.tz_convert(self.tz_js)
                )
            else:
                df[col] = df[col].dt.tz_convert(self.tz_js)

        # 2. 特征工程
        df["connect_hour"] = df["connectionTime"].dt.hour
        df["connect_weekday"] = df["connectionTime"].dt.weekday
        df["is_weekend"] = df["connect_weekday"].apply(lambda x: 1 if x >= 5 else 0)
        df["is_jiangsu_peak"] = df["connect_hour"].isin(JIANGSU_PARAMS["peak_hours"]).astype(int)

        # 3. 时长计算（三个时间列时区已一致）
        df["total_occupy_h"] = (df["disconnectTime"] - df["connectionTime"]).dt.total_seconds() / 3600
        df["effective_charging_h"] = (df["doneChargingTime"] - df["connectionTime"]).dt.total_seconds() / 3600
        df["idle_occupy_h"] = df["total_occupy_h"] - df["effective_charging_h"]

        # 4. 类别特征编码
        df["stationID_encoded"] = self.le.fit_transform(df["stationID"].astype(str))

        # 5. 异常值过滤
        df = df[(df["kWhDelivered"] > 0) & (df["kWhDelivered"] < 80)]
        df = df[(df["total_occupy_h"] > 0) & (df["total_occupy_h"] < 24)]
        df = df.dropna(subset=["kWhDelivered", "effective_charging_h", "total_occupy_h"])

        # 6. 保存中间数据
        out_path = os.path.join(str(OUTPUT_PROCESSED_DIR), "cleaned_data.csv")
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"数据清洗与特征工程完成：有效数据 {len(df)} 条")
        print(f"中间数据已保存至：{out_path}")

        return df
