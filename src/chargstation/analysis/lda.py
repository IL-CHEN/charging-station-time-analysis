# -*- coding: utf-8 -*-
"""LDA 主题模型分析：对全国与江苏省评论分别建模并对比主题分布。

输入：清洗后的评论 CSV（data/processed/all_comments_clean.csv、jiangsu_final.csv）
输出：主题-关键词热力图、各主题高频词条形图、全国 vs 江苏主题占比对比图。
"""

import os

import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from chargstation.config import OUTPUT_DIR, PROCESSED_DATA_DIR
from chargstation.utils import apply_chinese_font, load_stopwords

plt.rcParams["axes.unicode_minus"] = False
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300


def preprocess_text(text: str, stopwords) -> str:
    """jieba 分词 + 停用词过滤，返回空格分隔的干净文本。"""
    if pd.isna(text):
        return ""
    seg = jieba.cut(str(text))
    return " ".join(w for w in seg if len(w) > 1 and w not in stopwords)


def run_lda_analysis(corpus, name: str, n_topics: int = 4, n_top_words: int = 15):
    """训练单组 LDA 模型并绘制热力图与各主题关键词条形图。"""
    vectorizer = CountVectorizer(max_df=0.9, min_df=10)
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    topic_dist = lda.fit_transform(X)

    # 1. 主题-关键词热力图
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(lda.components_[:, :15], cmap="Blues",
                     xticklabels=feature_names[:15],
                     yticklabels=[f"主题 {i + 1}" for i in range(n_topics)])
    apply_chinese_font(ax, f"LDA主题-关键词热力图 ({name})")
    plt.tight_layout()
    plt.savefig(os.path.join(str(OUTPUT_DIR), f"LDA_{name}_热力图.png"), bbox_inches="tight")
    plt.close()

    # 2. 各主题 Top 词条形图
    for topic_idx, topic in enumerate(lda.components_):
        top_word_idx = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_word_idx]
        top_weights = [topic[i] for i in top_word_idx]

        plt.figure(figsize=(10, 5))
        ax = sns.barplot(x=top_weights, y=top_words, color="#1f77b4")
        apply_chinese_font(ax, f"{name} - 主题 {topic_idx + 1} 高频关键词")
        plt.tight_layout()
        plt.savefig(os.path.join(str(OUTPUT_DIR), f"LDA_{name}_主题{topic_idx + 1}.png"), bbox_inches="tight")
        plt.close()

    return topic_dist


def lda_main() -> None:
    """全国 vs 江苏省 LDA 主题对比分析入口。"""
    stopwords = load_stopwords()

    total_path = os.path.join(str(PROCESSED_DATA_DIR), "all_comments_clean.csv")
    js_path = os.path.join(str(PROCESSED_DATA_DIR), "jiangsu_final.csv")

    df_all = pd.read_csv(total_path, encoding="utf-8-sig")
    df_js = pd.read_csv(js_path, encoding="utf-8-sig")
    print(f"全国总评论：{len(df_all)} 条")
    print(f"江苏省评论：{len(df_js)} 条")

    df_all["clean_text"] = df_all["comment"].apply(lambda t: preprocess_text(t, stopwords))
    df_js["clean_text"] = df_js["comment"].apply(lambda t: preprocess_text(t, stopwords))

    print("正在训练全国样本...")
    topic_dist_all = run_lda_analysis(df_all["clean_text"], "全国样本")
    print("正在训练江苏省样本...")
    topic_dist_js = run_lda_analysis(df_js["clean_text"], "江苏省样本")

    # 3. 全国 vs 江苏 主题占比对比柱状图
    avg_all = topic_dist_all.mean(axis=0)
    avg_js = topic_dist_js.mean(axis=0)
    topic_labels = [f"主题 {i + 1}" for i in range(avg_all.shape[0])]

    plt.figure(figsize=(10, 6))
    x = np.arange(len(topic_labels))
    width = 0.35
    plt.bar(x - width / 2, avg_all, width, label="全国样本", color="#2E86AB")
    plt.bar(x + width / 2, avg_js, width, label="江苏省样本", color="#A23B72")
    ax = plt.gca()
    ax.set_xticks(x)
    ax.set_xticklabels(topic_labels)
    apply_chinese_font(ax, title_text="主题分布对比：全国 vs 江苏省")
    ax.set_ylabel("主题平均占比")
    plt.tight_layout()
    plt.savefig(os.path.join(str(OUTPUT_DIR), "LDA_全国江苏对比.png"), bbox_inches="tight")
    plt.close()

    print("LDA 主题分析全部完成！")


if __name__ == "__main__":
    lda_main()
