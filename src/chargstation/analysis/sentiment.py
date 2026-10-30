# -*- coding: utf-8 -*-
"""评论情感分析（基于 SnowNLP）。

输入：清洗后的评论 CSV（data/processed/jiangsu_train.csv）
输出：情感得分/标签标注后的 jiangsu_final.csv，以及情感得分密度图。

依赖 ``snownlp``，未安装时可先 ``pip install snownlp``。
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chargstation.config import PROCESSED_DATA_DIR
from chargstation.utils import apply_chinese_font

plt.rcParams["axes.unicode_minus"] = False
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300

POSITIVE_THRESHOLD = 0.6
NEGATIVE_THRESHOLD = 0.4


def _score_to_label(score: float) -> tuple:
    """将情感得分映射为 (标签, 数值标签)。"""
    if score > POSITIVE_THRESHOLD:
        return "Positive", 2
    if score < NEGATIVE_THRESHOLD:
        return "Negative", 0
    return "Neutral", 1


def analyze_sentiment(text) -> pd.Series:
    """对单条文本做情感分析，返回 (score, label, numeric_label)。"""
    try:
        from snownlp import SnowNLP

        score = SnowNLP(str(text)).sentiments
        label, numeric = _score_to_label(score)
        return pd.Series([score, label, numeric])
    except Exception:  # noqa: BLE001
        return pd.Series([0.5, "Neutral", 1])


def sentiment_main() -> None:
    """对江苏省评论执行情感分析并绘图、保存结果。"""
    file_name = os.path.join(str(PROCESSED_DATA_DIR), "jiangsu_train.csv")
    output_file = os.path.join(str(PROCESSED_DATA_DIR), "jiangsu_final.csv")
    img_path = os.path.join(str(PROCESSED_DATA_DIR), "sentiment_distribution.png")

    df = pd.read_csv(file_name, encoding="utf-8-sig")
    print(f"Loaded comments: {len(df)}")

    df[["sentiment_score", "sentiment", "label"]] = (
        df["comment"].apply(analyze_sentiment)
    )

    print("\nSentiment Distribution:")
    print(df["sentiment"].value_counts())

    # 情感得分密度图
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=df, x="sentiment_score", fill=True, color="#2E86AB",
                alpha=0.6, linewidth=2.5)
    plt.axvline(NEGATIVE_THRESHOLD, color="#A23B72", linestyle="--", linewidth=2,
                label=f"Negative/Neutral ({NEGATIVE_THRESHOLD})")
    plt.axvline(POSITIVE_THRESHOLD, color="#F18F01", linestyle="--", linewidth=2,
                label=f"Neutral/Positive ({POSITIVE_THRESHOLD})")
    plt.axvline(df["sentiment_score"].mean(), color="#C73E1D", linewidth=2.5,
                label=f"Mean: {df['sentiment_score'].mean():.3f}")
    ax = plt.gca()
    apply_chinese_font(ax, "江苏充电相关评论情感得分分布")
    ax.set_xlabel("情感得分（0 = 负面，1 = 正面）")
    ax.set_ylabel("密度")
    ax.set_xlim(0, 1)
    plt.legend(fontsize=10, frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(img_path, bbox_inches="tight")
    plt.close()

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"情感分析完成，结果已保存至：{output_file}")


if __name__ == "__main__":
    sentiment_main()
