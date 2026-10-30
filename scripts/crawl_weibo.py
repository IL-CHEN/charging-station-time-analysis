# -*- coding: utf-8 -*-
"""爬取微博推文。

用法：
    python scripts/crawl_weibo.py [关键词] [页数]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from chargstation.crawlers.weibo import weibo_main


def main() -> None:
    keyword = sys.argv[1] if len(sys.argv) > 1 else "江苏省充电桩"
    pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    weibo_main(keyword=keyword, pages=pages)


if __name__ == "__main__":
    main()
