# -*- coding: utf-8 -*-
"""微博（Weibo）推文爬虫。

功能：按关键词搜索微博推文并保存为 TXT。
登录凭证（Cookie）通过环境变量 ``WEIBO_COOKIE`` 提供，未配置时给出明确提示。
"""

import re
from typing import Dict, List

import requests

from chargstation.config import HEADERS, RAW_DATA_DIR, WEIBO_COOKIE
from chargstation.utils import save_formatted_txt


class WeiboCrawler:
    """分页爬取微博搜索结果推文。"""

    BASE_URL = "https://s.weibo.com/weibo"

    def __init__(self, keyword: str, cookie: str | None = None):
        self.keyword = keyword.strip()
        self.cookie = cookie or WEIBO_COOKIE
        self.base_url = f"{self.BASE_URL}?q={self.keyword}"
        print(f"当前搜索关键词：{self.keyword}")
        if not self.cookie:
            print("提示：未配置 WEIBO_COOKIE，部分内容可能无法抓取。")

    @property
    def headers(self) -> Dict[str, str]:
        headers = dict(HEADERS)
        if self.cookie:
            headers["Cookie"] = self.cookie
        return headers

    def get_charging_data(self, page: int) -> str:
        """爬取单页搜索结果 HTML。"""
        params: Dict[str, str] = {"page": str(page)}
        print(f"正在获取第 {page} 页有关 {self.keyword} 的推文...")
        try:
            response = requests.get(url=self.base_url, headers=self.headers,
                                    params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"请求失败: {exc}") from exc

    def data_processing(self, page: int) -> str:
        """解析单页 HTML，返回清洗后的推文文本。"""
        p_content = (
            r'<p class="txt" node-type="feed_list_content.*?" nick-name=".*?".*?>(.*?)</p>'
        )
        contents: List[str] = re.findall(p_content, self.get_charging_data(page), re.S)

        for i in range(len(contents)):
            contents[i] = re.sub("<.*?>", "", contents[i])
            contents[i] = re.sub("收起d", "", contents[i])
            contents[i] = contents[i].strip()

        # 删除含“展开c”的未完全加载内容
        contents = [c for c in contents if "展开c" not in c]

        print(f"请求成功！获取到 {len(contents)} 条推文")
        return "\n".join(contents) + "\n"


def weibo_main(keyword: str, pages: int = 50) -> None:
    """微博推文爬取入口。"""
    crawler = WeiboCrawler(keyword=keyword)
    out_path = RAW_DATA_DIR / "weibo" / f"weibo_data_{keyword}.txt"
    for page in range(1, pages + 1):
        data = crawler.data_processing(page)
        save_formatted_txt(data=data, save_path=out_path)


if __name__ == "__main__":
    weibo_main(keyword="江苏省充电桩")
