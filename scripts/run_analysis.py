# -*- coding: utf-8 -*-
"""运行文本挖掘分析（LDA 主题 / 情感 / 词云）。

用法：
    python scripts/run_analysis.py lda
    python scripts/run_analysis.py sentiment
    python scripts/run_analysis.py wordcloud [txt路径]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    task = sys.argv[1].lower()

    if task == "lda":
        from chargstation.analysis.lda import lda_main
        lda_main()
    elif task == "sentiment":
        from chargstation.analysis.sentiment import sentiment_main
        sentiment_main()
    elif task == "wordcloud":
        from chargstation.analysis.wordcloud import wordcloud_main
        wordcloud_main(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(f"未知任务：{task}")
        print(__doc__)


if __name__ == "__main__":
    main()
