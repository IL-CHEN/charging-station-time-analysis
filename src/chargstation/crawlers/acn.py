# -*- coding: utf-8 -*-
"""ACN 美国充电桩（Caltech EV）数据爬虫。

原始接口：https://ev.caltech.edu/api/v1/sessions/caltech
凭证（API Key）通过环境变量 ``ACN_API_KEY`` 提供，未配置时给出明确提示。
"""

from typing import Any, Dict

import requests

from chargstation.config import ACN_API_KEY, HEADERS, RAW_DATA_DIR
from chargstation.utils import save_formatted_json


class ACNCrawler:
    """分页爬取 ACN 充电桩会话数据并保存为 JSON。"""

    BASE_URL = "https://ev.caltech.edu/api/v1/sessions/caltech"

    def __init__(self, page: int = 1):
        self.page = page
        if not ACN_API_KEY:
            raise ValueError(
                "未配置 ACN_API_KEY 环境变量。请在项目根目录 .env 中填入你的密钥。"
            )

    @property
    def headers(self) -> Dict[str, str]:
        headers = dict(HEADERS)
        headers["Authorization"] = f"Bearer {ACN_API_KEY}"
        return headers

    def get_charging_data(self) -> Dict[str, Any]:
        """爬取单页充电桩数据。"""
        params: Dict[str, str] = {"page": str(self.page)}
        print(f"正在获取第 {self.page} 页的充电记录...")
        try:
            response = requests.get(url=self.BASE_URL, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"请求成功！获取到 {len(data.get('_items', []))} 条充电记录")
            return data
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"请求失败: {exc}") from exc

    def crawl_range(self, start_page: int, end_page: int, out_dir=None) -> None:
        """爬取 [start_page, end_page] 范围内的所有页并保存到 data/raw。"""
        out_dir = out_dir or (RAW_DATA_DIR / "acn_data")
        out_dir.mkdir(parents=True, exist_ok=True)
        for page in range(start_page, end_page + 1):
            self.page = page
            data = self.get_charging_data()
            save_formatted_json(data=data, save_path=out_dir / f"acn_data_{page}.json")


def acn_main() -> None:
    """ACN 数据爬取入口。"""
    ACNCrawler().crawl_range(1226, 1257)


if __name__ == "__main__":
    acn_main()
