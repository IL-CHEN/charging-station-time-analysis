# -*- coding: utf-8 -*-
"""论文级图表可视化：生成 10 张高质量分析图。"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chargstation.config import FIGURES_DIR, JIANGSU_PARAMS
from chargstation.utils import apply_chinese_font

WEEKDAY_ORDER = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


class PaperVisualizer:
    """负责生成论文级高质量图表（中文字体自动应用，可跨平台）。"""

    def __init__(self):
        plt.rcParams["figure.dpi"] = 300
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.unicode_minus"] = False
        sns.set_style("whitegrid")

    def plot_all(self, df: pd.DataFrame, results_df: pd.DataFrame, feature_importance_list: list) -> None:
        """一键生成全部 10 张论文图表。"""
        print("\n开始生成 10 张论文图表...")
        self._plot_kwh_distribution(df)
        self._plot_duration_distribution(df)
        self._plot_peak_hour_distribution(df)
        self._plot_weekend_comparison(df)
        self._plot_kwh_vs_duration(df)
        self._plot_idle_time_distribution(df)
        self._plot_model_comparison(results_df)
        self._plot_feature_importance(feature_importance_list)
        self._plot_hourly_heatmap(df)
        self._plot_weekly_boxplot(df)
        print("所有 10 张论文图表生成完成！")

    # ------------------------------------------------------------------
    def _plot_kwh_distribution(self, df: pd.DataFrame) -> None:
        plt.figure(figsize=(12, 6))
        ax = sns.histplot(df["kWhDelivered"], bins=50, kde=True, color="#1f77b4")
        ax.set_xlabel("单次充电量 (kWh)")
        ax.set_ylabel("频次")
        apply_chinese_font(ax, "单次充电量分布特征")
        plt.savefig(os.path.join(str(FIGURES_DIR), "01_充电量分布.png"), bbox_inches="tight")
        plt.close()

    def _plot_duration_distribution(self, df: pd.DataFrame) -> None:
        plt.figure(figsize=(12, 6))
        ax = sns.histplot(df["effective_charging_h"], bins=50, kde=True, color="#ff7f0e")
        ax.set_xlabel("有效充电时长 (小时)")
        ax.set_ylabel("频次")
        apply_chinese_font(ax, "有效充电时长分布特征")
        plt.savefig(os.path.join(str(FIGURES_DIR), "02_充电时长分布.png"), bbox_inches="tight")
        plt.close()

    def _plot_peak_hour_distribution(self, df: pd.DataFrame) -> None:
        hourly_stats = df.groupby("connect_hour").size().reset_index(name="order_count")
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x="connect_hour", y="order_count", data=hourly_stats, color="#1f77b4")
        for hour in JIANGSU_PARAMS["peak_hours"]:
            ax.axvspan(hour - 0.5, hour + 0.5, alpha=0.2, color="red",
                       label="江苏峰时" if hour == JIANGSU_PARAMS["peak_hours"][0] else "")
        ax.set_xlabel("充电连接小时 (北京时间)")
        ax.set_ylabel("充电订单数量")
        ax.legend()
        apply_chinese_font(ax, "江苏峰谷时段充电订单分布")
        plt.savefig(os.path.join(str(FIGURES_DIR), "03_峰谷时段分布.png"), bbox_inches="tight")
        plt.close()

    def _plot_weekend_comparison(self, df: pd.DataFrame) -> None:
        df = df.copy()
        df["is_weekend_label"] = df["is_weekend"].map({0: "工作日", 1: "周末"})
        plt.figure(figsize=(12, 6))
        ax = sns.boxplot(x="is_weekend_label", y="kWhDelivered", data=df, palette=["#1f77b4", "#ff7f0e"])
        ax.set_xlabel("")
        ax.set_ylabel("单次充电量 (kWh)")
        apply_chinese_font(ax, "工作日与周末充电行为差异对比")
        plt.savefig(os.path.join(str(FIGURES_DIR), "04_工作日周末对比.png"), bbox_inches="tight")
        plt.close()

    def _plot_kwh_vs_duration(self, df: pd.DataFrame) -> None:
        sample_df = df.sample(min(5000, len(df)), random_state=42)
        plt.figure(figsize=(12, 6))
        ax = sns.scatterplot(x="effective_charging_h", y="kWhDelivered",
                             data=sample_df, alpha=0.3, s=10, color="#1f77b4")
        ax.set_xlabel("有效充电时长 (小时)")
        ax.set_ylabel("单次充电量 (kWh)")
        apply_chinese_font(ax, "充电量与充电时长关系散点图")
        plt.savefig(os.path.join(str(FIGURES_DIR), "05_充电量vs时长散点图.png"), bbox_inches="tight")
        plt.close()

    def _plot_idle_time_distribution(self, df: pd.DataFrame) -> None:
        idle_df = df[df["idle_occupy_h"] > 0]
        plt.figure(figsize=(12, 6))
        ax = sns.histplot(idle_df["idle_occupy_h"], bins=50, kde=True, color="#2ca02c")
        ax.set_xlabel("充电后占位时长 (小时)")
        ax.set_ylabel("频次")
        apply_chinese_font(ax, "充电完成后占位时长分布")
        plt.savefig(os.path.join(str(FIGURES_DIR), "06_占位时长分布.png"), bbox_inches="tight")
        plt.close()

    def _plot_model_comparison(self, results_df: pd.DataFrame) -> None:
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x="Model", y="R²", data=results_df, palette=["#1f77b4", "#ff7f0e"])
        ax.set_xlabel("")
        ax.set_ylabel("R² Score")
        apply_chinese_font(ax, "机器学习模型预测性能对比 (R²)")
        plt.savefig(os.path.join(str(FIGURES_DIR), "07_模型性能对比.png"), bbox_inches="tight")
        plt.close()

    def _plot_feature_importance(self, feature_importance_list: list) -> None:
        if not feature_importance_list:
            return
        xgb_fi = [fi for fi in feature_importance_list if fi["Model"].iloc[0] == "XGBoost"][0]
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x="Importance", y="Feature", data=xgb_fi, color="#ff7f0e")
        ax.set_xlabel("特征重要性")
        ax.set_ylabel("")
        apply_chinese_font(ax, "XGBoost 模型特征重要性排序")
        plt.savefig(os.path.join(str(FIGURES_DIR), "08_特征重要性.png"), bbox_inches="tight")
        plt.close()

    def _plot_hourly_heatmap(self, df: pd.DataFrame) -> None:
        df_plot = df.copy()
        df_plot["weekday_name"] = df_plot["connect_weekday"].map(
            {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"})
        heatmap_data = df_plot.groupby(["weekday_name", "connect_hour"])["kWhDelivered"].mean().unstack()
        heatmap_data = heatmap_data.reindex(WEEKDAY_ORDER)
        plt.figure(figsize=(16, 8))
        ax = sns.heatmap(heatmap_data, cmap="YlOrRd", annot=False, fmt=".1f")
        ax.set_xlabel("小时")
        ax.set_ylabel("")
        apply_chinese_font(ax, "星期-小时充电量热力图")
        plt.savefig(os.path.join(str(FIGURES_DIR), "09_充电量热力图.png"), bbox_inches="tight")
        plt.close()

    def _plot_weekly_boxplot(self, df: pd.DataFrame) -> None:
        df = df.copy()
        df["weekday_name"] = df["connect_weekday"].map(
            {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"})
        plt.figure(figsize=(12, 6))
        ax = sns.boxplot(x="weekday_name", y="kWhDelivered", data=df,
                         order=WEEKDAY_ORDER, palette="viridis")
        ax.set_xlabel("")
        ax.set_ylabel("单次充电量 (kWh)")
        apply_chinese_font(ax, "一周内每日充电量分布箱线图")
        plt.savefig(os.path.join(str(FIGURES_DIR), "10_周充电量箱线图.png"), bbox_inches="tight")
        plt.close()
