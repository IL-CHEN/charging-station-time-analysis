# -*- coding: utf-8 -*-
"""机器学习模型训练、评估与保存。"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from chargstation.config import RESULTS_DIR
from chargstation.pipeline.processor import DataProcessor


class MLModelTrainer:
    """负责模型训练、评估与结果保存。"""

    def __init__(self):
        self.feature_cols = DataProcessor.FEATURE_COLS
        self.target_col = DataProcessor.TARGET_COL

    def prepare_data(self, df: pd.DataFrame):
        """切分训练/测试集（默认 80/20，固定随机种子保证可复现）。"""
        X = df[self.feature_cols]
        y = df[self.target_col]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def train_random_forest(self, X_train, y_train) -> RandomForestRegressor:
        """训练随机森林模型并保存。"""
        print("\n开始训练随机森林模型...")
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            n_jobs=-1,
            random_state=42,
        )
        rf.fit(X_train, y_train)
        joblib.dump(rf, os.path.join(str(RESULTS_DIR), "random_forest_model.pkl"))
        print("随机森林模型已保存")
        return rf

    def train_xgboost(self, X_train, y_train) -> XGBRegressor:
        """训练 XGBoost 模型并保存。"""
        print("\n开始训练 XGBoost 模型...")
        xgb = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            n_jobs=-1,
            random_state=42,
        )
        xgb.fit(X_train, y_train)
        joblib.dump(xgb, os.path.join(str(RESULTS_DIR), "xgboost_model.pkl"))
        print("XGBoost 模型已保存")
        return xgb

    def evaluate_models(self, models: dict, X_test, y_test):
        """评估所有模型并保存评估结果与特征重要性。"""
        results = []
        feature_importance_list = []

        for name, model in models.items():
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            results.append({
                "Model": name,
                "MAE (kWh)": mae,
                "RMSE (kWh)": rmse,
                "R²": r2,
            })

            if hasattr(model, "feature_importances_"):
                fi = pd.DataFrame({
                    "Feature": self.feature_cols,
                    "Importance": model.feature_importances_,
                }).sort_values("Importance", ascending=False)
                fi["Model"] = name
                feature_importance_list.append(fi)

        results_df = pd.DataFrame(results)
        results_df.to_csv(
            os.path.join(str(RESULTS_DIR), "model_comparison.csv"),
            index=False, encoding="utf-8-sig",
        )

        if feature_importance_list:
            fi_df = pd.concat(feature_importance_list, ignore_index=True)
            fi_df.to_csv(
                os.path.join(str(RESULTS_DIR), "feature_importance.csv"),
                index=False, encoding="utf-8-sig",
            )

        print("\n模型评估结果：")
        print(results_df.to_string(index=False))
        print(f"\n模型结果已保存至：{RESULTS_DIR}")

        return results_df, feature_importance_list
