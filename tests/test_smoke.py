# -*- coding: utf-8 -*-
"""冒烟测试：验证 chargstation 包可正常导入、路径正确、核心流水线可运行。

用法：
    python tests/test_smoke.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_imports() -> None:
    from chargstation import config
    from chargstation.crawlers import ACNCrawler, BilibiliBv, WeiboCrawler
    from chargstation.pipeline import DataLoader, DataProcessor, MLModelTrainer, PaperVisualizer

    assert config.PROJECT_ROOT.exists()
    assert config.RAW_DATA_DIR.exists()
    assert config.FIGURES_DIR.exists()
    print("包导入与路径配置正常")


def test_pipeline() -> None:
    from chargstation.pipeline import DataLoader, DataProcessor, MLModelTrainer

    loader = DataLoader()
    df_raw = loader.load_all()
    assert len(df_raw) > 0, "原始数据为空"
    print(f"数据加载成功：{len(df_raw)} 条")

    df_clean = DataProcessor().process(df_raw)
    assert len(df_clean) > 0, "清洗后数据为空"
    print(f"数据清洗成功：{len(df_clean)} 条")


if __name__ == "__main__":
    test_imports()
    test_pipeline()
    print("\n全部冒烟测试通过")
