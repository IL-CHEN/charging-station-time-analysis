# -*- coding: utf-8 -*-
"""通用工具函数：JSON/TXT 保存、停用词加载、随机休眠与中文字体处理。"""

import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Set

from chargstation.config import STOPWORDS_DIR, CN_FONT_PATH


def save_formatted_json(data: Any, save_path: str | Path) -> None:
    """将数据格式化后保存为 UTF-8 JSON 文件（带缩进）。"""
    print("保存为 JSON 数据中...")
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"JSON 已格式化并保存到: {save_path}")
    except Exception as exc:  # noqa: BLE001
        raise Exception(f"保存文件失败：{exc}") from exc


def save_formatted_txt(data: str, save_path: str | Path) -> None:
    """将文本追加保存到 UTF-8 TXT 文件。"""
    print("保存为 TXT 数据中...")
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(save_path, "a", encoding="utf-8") as f:
            f.write(data)
        print(f"TXT 已格式化并保存到: {save_path}")
    except Exception as exc:  # noqa: BLE001
        raise Exception(f"保存文件失败：{exc}") from exc


def load_stopwords(path: str | Path | None = None) -> Set[str]:
    """加载停用词集合（默认读取 data/stopwords/baidu_stopwords.txt）。"""
    path = Path(path) if path else STOPWORDS_DIR / "baidu_stopwords.txt"
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def random_sleep(
    min_sec: float | None = None,
    max_sec: float | None = None,
    mode: str = "short",
    custom_tip: str | None = None,
) -> None:
    """无依赖的动态随机休息函数（模拟真人浏览，用于降低反爬风控风险）。"""
    mode_config = {
        "short": {"min": 1.5, "max": 4.0, "mid": 2.5},
        "long": {"min": 4.0, "max": 9.0, "mid": 6.0},
    }

    if mode not in mode_config:
        mode = "short"
    config = mode_config[mode]
    min_sec = min_sec if min_sec is not None else config["min"]
    max_sec = max_sec if max_sec is not None else config["max"]
    mid_sec = config["mid"]
    if min_sec > max_sec:
        min_sec, max_sec = max_sec, min_sec

    total_sleep = random.triangular(min_sec, max_sec, mid_sec)
    start_time = time.time()

    tip_list = [
        "休息中，模拟真人浏览",
        "安全限速中",
        "模拟真人浏览中",
        "防风控休息",
        "稍作等待",
    ]
    show_tip = custom_tip if custom_tip else random.choice(tip_list)

    bar_length = 20
    while True:
        elapsed = time.time() - start_time
        remain = max(total_sleep - elapsed, 0)
        filled = int(bar_length * (elapsed / total_sleep))
        bar = "█" * filled + "░" * (bar_length - filled)
        sys.stdout.write(f"\r{show_tip} |{bar}| 剩余 {remain:.1f}s / 总时长 {total_sleep:.1f}s")
        sys.stdout.flush()
        if remain <= 0:
            break
        time.sleep(0.1)

    sys.stdout.write("\n")
    print(f"休息结束，本次休息时长：{total_sleep:.2f}s，继续任务\n")


# ---------------------------------------------------------------------------
# 中文字体工具（绘图时使用，避免 matplotlib 中文乱码）
# ---------------------------------------------------------------------------
def get_chinese_font(size: int = 11, bold: bool = False):
    """返回可用于 matplotlib 的 FontProperties 对象。

    :param size: 字号
    :param bold: 是否加粗
    """
    from matplotlib.font_manager import FontProperties

    return FontProperties(fname=CN_FONT_PATH, size=size, weight="bold" if bold else "normal")


def apply_chinese_font(ax, title: str = ""):
    """将当前坐标轴的所有中文文本（标题/轴/刻度/图例）统一替换为仓库内置字体。"""
    font = get_chinese_font(size=11)
    font_bold = get_chinese_font(size=12, bold=True)
    if title:
        ax.set_title(title, fontproperties=font_bold)
    if ax.get_xlabel():
        ax.set_xlabel(ax.get_xlabel(), fontproperties=font)
    if ax.get_ylabel():
        ax.set_ylabel(ax.get_ylabel(), fontproperties=font)
    for label in ax.get_xticklabels():
        label.set_fontproperties(font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(font)
    if ax.get_legend():
        for text in ax.get_legend().get_texts():
            text.set_fontproperties(font)
