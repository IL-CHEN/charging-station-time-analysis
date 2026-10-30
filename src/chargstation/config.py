# -*- coding: utf-8 -*-
"""全局配置：项目路径、数据目录、江苏公开参数与环境变量加载。

本模块是整个包的单一配置入口：
- 所有路径都基于仓库根目录（PROJECT_ROOT）计算，保证在任何工作目录下运行都不出错；
- 所有密钥/凭证都从环境变量或 .env 文件读取，绝不硬编码在代码中。
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
# 仓库根目录 = 本文件 (src/chargstation/config.py) 的上三级
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"                       # 原始 ACN JSON
PROCESSED_DATA_DIR = DATA_DIR / "processed"           # 中间清洗结果
OUTPUT_DIR = DATA_DIR / "outputs"                     # 一切输出
FIGURES_DIR = OUTPUT_DIR / "figures"                  # 论文图表
OUTPUT_PROCESSED_DIR = OUTPUT_DIR / "processed"       # 清洗后的主表
RESULTS_DIR = OUTPUT_DIR / "results"                  # 模型与评估结果
STOPWORDS_DIR = DATA_DIR / "stopwords"                # 停用词
FONTS_DIR = DATA_DIR / "fonts"                        # 中文字体
BACKGROUND_DIR = DATA_DIR / "background"              # 词云蒙版图

# 自动创建所有输出目录（幂等）
for _dir in (RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR,
             OUTPUT_PROCESSED_DIR, RESULTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 中文字体路径
# ---------------------------------------------------------------------------
# 优先使用仓库内置字体（可移植），缺失时回退到 Windows 系统字体
_SYSTEM_CN_FONT = Path("C:/Windows/Fonts/simhei.ttf")
_default_font = FONTS_DIR / "simhei.ttf"
CN_FONT_PATH = str(_default_font if _default_font.exists() else _SYSTEM_CN_FONT)


# ---------------------------------------------------------------------------
# 江苏官方公开参数（论文口径）
# ---------------------------------------------------------------------------
JIANGSU_PARAMS = {
    "peak_hours": [8, 9, 10, 11, 17, 18, 19, 20, 21],
    "avg_utilization": 0.12,
    "fast_charge_ratio": 0.32,
}


# ---------------------------------------------------------------------------
# 环境变量 / 密钥加载
# ---------------------------------------------------------------------------
def _load_dotenv(path: Path | None = None) -> None:
    """极简 .env 加载器，避免引入 python-dotenv 依赖。

    规则：每行 ``KEY=VALUE``，支持 ``#`` 注释与引号包裹的值；
    已存在的环境变量不会被覆盖。
    """
    path = path or (PROJECT_ROOT / ".env")
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

# 凭证一律从环境变量读取（.env 已被 .gitignore 排除，严禁提交到仓库）
ACN_API_KEY = os.getenv("ACN_API_KEY", "").strip()
BILIBILI_COOKIE = os.getenv("BILIBILI_COOKIE", "").strip()
WEIBO_COOKIE = os.getenv("WEIBO_COOKIE", "").strip()

# 通用请求头（不含任何私有凭证）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
    )
}
