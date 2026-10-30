# -*- coding: utf-8 -*-
"""爬取 B 站视频评论。

用法：
    python scripts/crawl_bilibili.py --keyword 充电桩 --start 1 --end 3
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from chargstation.config import RAW_DATA_DIR
from chargstation.crawlers.bilibili import BilibiliBv, BilibiliComments


def main() -> None:
    parser = argparse.ArgumentParser(description="爬取 B 站充电桩相关视频评论")
    parser.add_argument("--keyword", default="充电桩")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=3)
    parser.add_argument("--mode", choices=["bv", "comments"], default="bv",
                        help="bv=只获取 bv 码；comments=爬取评论")
    args = parser.parse_args()

    bvs_dir = RAW_DATA_DIR / "bilibili"
    bvs_path = bvs_dir / "bilibili_data_bvs.txt"

    if args.mode == "bv":
        bv = BilibiliBv(keyword=args.keyword)
        bvs_dir.mkdir(parents=True, exist_ok=True)
        bvs_path.write_text(bv.get_bilibili_bvs(args.start, args.end), encoding="utf-8")
        print(f"bv 码已保存到：{bvs_path}")
    else:
        comments = BilibiliComments(bvs_path=str(bvs_path), save_path=str(bvs_dir))
        comments.run()


if __name__ == "__main__":
    main()
