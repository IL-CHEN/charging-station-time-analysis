# -*- coding: utf-8 -*-
"""B 站（bilibili）视频评论爬虫。

功能：
- ``BilibiliBv``：按关键词搜索获取视频 bv 码；
- ``BilibiliComments``：批量爬取主评论与子评论（含 IP 归属地）并保存为 CSV。

登录凭证（Cookie）通过环境变量 ``BILIBILI_COOKIE`` 提供，未配置时给出明确提示。
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import quote

import pandas as pd
import requests

from chargstation.config import BILIBILI_COOKIE, HEADERS, RAW_DATA_DIR
from chargstation.utils import random_sleep, save_formatted_txt


class BilibiliBv:
    """获取搜索结果的视频 bv 码。"""

    def __init__(self, keyword: str, cookie: str | None = None):
        self.keyword = keyword.strip()
        self.cookie = cookie or BILIBILI_COOKIE
        self.base_url = f"https://search.bilibili.com/all?keyword={quote(self.keyword)}"

    @property
    def headers(self) -> Dict[str, str]:
        headers = dict(HEADERS)
        if self.cookie:
            headers["Cookie"] = self.cookie
        return headers

    def get_bilibili_html(self, page: int) -> str:
        """获取单页搜索 HTML。"""
        params = {"page": str(page), "o": str(42 * (page - 1))}
        print(f"正在获取第 {page} 页有关 {self.keyword} 的 HTML 文本...")
        try:
            response = requests.get(url=self.base_url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            print("获取成功！")
            return response.text
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"请求失败: {exc}") from exc

    def get_bilibili_bv(self, page: int) -> Set[str]:
        """从单页 HTML 中提取视频 bv 码。"""
        data = self.get_bilibili_html(page)
        print("正在解析 HTML 文本为视频 bv 码...")
        bvs = set(re.findall(r'bvid:"(.*?)"', data, re.S))
        print("解析成功！")
        return bvs

    def get_bilibili_bvs(self, start_page: int, end_page: int) -> str:
        """获取 [start_page, end_page] 所有页的视频 bv 码（去重）。"""
        bvs: Set[str] = set()
        for page in range(start_page, end_page + 1):
            bv = self.get_bilibili_bv(page=page)
            if not bv:
                print("bv 码集合为空，界面元素不存在或出现验证码反爬！")
                break
            bvs |= bv
        print(f"共获取到 {len(bvs)} 条 bv 码！")
        return "\n".join(bvs) + "\n"


class BilibiliComments:
    """批量爬取视频主评论与子评论。"""

    def __init__(self, bvs_path: str, save_path: str | Path, cookie: str | None = None):
        self.bvs_path = bvs_path
        self.save_path = Path(save_path)
        self.cookie = cookie or BILIBILI_COOKIE
        self.temp_rpids: List[str] = []
        self.data: List[Dict[str, str]] = []
        self.save_path.mkdir(parents=True, exist_ok=True)

    @property
    def headers(self) -> Dict[str, str]:
        headers = dict(HEADERS)
        if self.cookie:
            headers["Cookie"] = self.cookie
        return headers

    def _load_bvs(self) -> List[str]:
        with open(self.bvs_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def _clean_comment(comment: str) -> str:
        """清洗单条评论：去除回复前缀、表情包、空白字符。"""
        if not comment:
            return ""
        match = re.search(r"回复 @[^:]+\s*:(.*)", comment)
        text = match.group(1) if match else comment
        text = re.sub(r"\[.*?]", "", text)
        text = re.sub(r"[\n\r\s]+", "", text)
        return text.strip()

    def _collect(self, replies: list) -> None:
        """把一页评论写入内存，并记录有子评论的主评论 rpid。"""
        for reply in replies:
            comment = self._clean_comment(reply["content"]["message"])
            try:
                ip = reply["reply_control"]["location"].split("：")[-1]
            except KeyError:
                ip = ""
            self.data.append({"comment": comment, "ip": ip})
            if reply.get("replies"):
                self.temp_rpids.append(str(reply["rpid"]))

    def _get_bilibili_main_comment(self, bv: str, page: int) -> int:
        """爬取一页主评论；无评论或出错返回 0。"""
        print(f"正在爬取视频 {bv} 的第 {page} 页主评论...")
        params = {"next": page, "type": 1, "oid": bv, "mode": 3}
        try:
            data = requests.get(
                url="https://api.bilibili.com/x/v2/reply/main?",
                headers=self.headers, params=params, timeout=30,
            ).json()
            if data["code"] != 0:
                raise Exception(f"主评论 API 报错: {data['message']}")
            replies = data["data"]["replies"]
            if not replies:
                return 0
            self._collect(replies)
            return 1
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"爬取主评论异常: {exc}") from exc

    def _get_bilibili_sub_comment(self, bv: str, rpid: str, page: int) -> int:
        """爬取一页子评论；无评论或出错返回 0。"""
        print(f"正在爬取视频 {bv} 下用户 {rpid} 的第 {page} 页子评论...")
        params = {"oid": bv, "type": 1, "ps": 20, "root": rpid, "pn": page}
        try:
            data = requests.get(
                url="https://api.bilibili.com/x/v2/reply/reply?",
                headers=self.headers, params=params, timeout=30,
            ).json()
            if data["code"] != 0:
                raise Exception(f"子评论 API 报错: {data['message']}")
            replies = data["data"]["replies"]
            if not replies:
                return 0
            self._collect(replies)
            return 1
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"爬取子评论异常: {exc}") from exc

    def _save_data(self, bv: str) -> None:
        filepath = self.save_path / f"bilibili_comments_ip_{bv}.csv"
        df = pd.DataFrame(self.data)
        df.to_csv(filepath, mode="w", encoding="utf-8-sig",
                  header=True, index=False, quoting=1, quotechar='"', escapechar="\\")
        print(f"保存成功！本次共保存 {len(df)} 条数据")
        self.data.clear()
        self.temp_rpids.clear()

    def run(self) -> None:
        """主流程：逐视频爬取主评论及其子评论。"""
        bvs = self._load_bvs()
        count = 0
        for bv in bvs:
            count += 1
            print(f"\n正在爬取视频 {bv} ... 进度 {count}/{len(bvs)}")
            main_page = 0
            while True:
                random_sleep(min_sec=1, max_sec=2)
                main_page += 1
                if self._get_bilibili_main_comment(bv=bv, page=main_page) == 0:
                    break
            for rpid in self.temp_rpids:
                sub_page = 0
                while True:
                    random_sleep(min_sec=1, max_sec=2)
                    sub_page += 1
                    if self._get_bilibili_sub_comment(bv=bv, rpid=rpid, page=sub_page) == 0:
                        break
            self._save_data(bv=bv)
            print(f"视频 {bv} 爬取完成")


def bilibili_bv_main(keyword: str = "充电桩", start_page: int = 1, end_page: int = 200) -> None:
    """B 站视频 bv 码爬取入口。"""
    bilibili_bv = BilibiliBv(keyword=keyword)
    save_formatted_txt(
        data=bilibili_bv.get_bilibili_bvs(start_page, end_page),
        save_path=RAW_DATA_DIR / "bilibili" / "bilibili_data_bvs.txt",
    )


if __name__ == "__main__":
    # bilibili_bv_main()
    comments = BilibiliComments(
        bvs_path=str(RAW_DATA_DIR / "bilibili" / "bilibili_data_bvs_test.txt"),
        save_path=str(RAW_DATA_DIR / "bilibili"),
    )
    comments.run()
