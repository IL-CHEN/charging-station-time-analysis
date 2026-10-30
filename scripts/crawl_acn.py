# -*- coding: utf-8 -*-
"""爬取 ACN 美国充电桩数据。

用法：
    python scripts/crawl_acn.py [起始页] [结束页]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from chargstation.crawlers.acn import ACNCrawler


def main() -> None:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1226
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 1257
    ACNCrawler().crawl_range(start, end)


if __name__ == "__main__":
    main()
