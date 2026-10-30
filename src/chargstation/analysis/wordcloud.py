# -*- coding: utf-8 -*-
"""微博推文词云生成。

输入：微博爬虫产出的 TXT（data/raw/weibo/weibo_data_*.txt）
输出：词云图（默认保存到仓库根目录/当前工作目录）。
"""

import numpy as np
from PIL import Image

from chargstation.config import BACKGROUND_DIR, CN_FONT_PATH
from chargstation.utils import load_stopwords


def make_wordcloud(text_path: str, mask_path=None, font_path: str = CN_FONT_PATH, out_path: str | None = None):
    """基于停用词过滤生成词云图。

    :param text_path: 原始推文 TXT 路径
    :param mask_path: 词云蒙版图片路径（默认 data/background/img.png）
    :param font_path: 中文字体路径
    :param out_path: 输出图片路径（默认 `<关键词>词云图.png`）
    """
    import jieba
    import matplotlib.pyplot as plt
    from wordcloud import ImageColorGenerator, WordCloud

    stop_words = load_stopwords()
    with open(text_path, "r", encoding="utf-8") as f:
        words = jieba.cut("".join(f.readlines()))

    report_words = [w for w in words if len(w) >= 2 and w not in stop_words]
    content = " ".join(report_words)

    # 蒙版图片
    mask_path = mask_path or str(BACKGROUND_DIR / "img.png")
    mask_images = np.array(Image.open(mask_path))

    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=2000,
        height=2000,
        mask=mask_images,
    ).generate(content)

    # 用蒙版原图颜色重新着色
    image_colors = ImageColorGenerator(mask_images)
    wc.recolor(color_func=image_colors)

    if out_path is None:
        out_path = f"词云图_{text_path.split('/')[-1][11:-4]}.png"

    plt.figure(figsize=(12, 12))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"词云图已保存：{out_path}")


def wordcloud_main(text_path: str | None = None) -> None:
    """词云生成入口。"""
    text_path = text_path or "data/raw/weibo/weibo_data_江苏省充电桩.txt"
    make_wordcloud(text_path)


if __name__ == "__main__":
    wordcloud_main()
