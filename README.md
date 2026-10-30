# 江苏省充电桩充电行为分析与预测（chargstation）

基于 **ACN（Caltech EV）开放充电数据** 与 **机器学习** 的江苏省充电桩充电行为分析与预测研究项目。

项目从 ACN 充电会话原始数据出发，完成 **数据清洗 → 特征工程 → 随机森林 / XGBoost 建模 → 论文级图表** 的完整流程，输出充电量预测模型与江苏省峰谷时段、占位时长、工作日/周末差异等行为洞察。

---

## 项目结构

```
charging_station_time_analysis/
├── src/chargstation/          # 核心包
│   ├── config.py              # 路径、参数、环境变量加载（单一路径入口）
│   ├── utils.py               # 通用工具（JSON/TXT 保存、停用词、随机休眠、中文字体）
│   ├── pipeline/              # 机器学习流水线
│   │   ├── loader.py          # ACN 原始 JSON 批量加载
│   │   ├── processor.py       # 数据清洗与特征工程
│   │   ├── ml_models.py       # 随机森林 / XGBoost 训练与评估
│   │   └── visualizer.py      # 10 张论文图表生成
│   ├── crawlers/              # 数据采集
│   │   ├── acn.py             # ACN 美国充电桩
│   │   ├── bilibili.py        # B 站评论
│   │   └── weibo.py           # 微博推文
│   └── analysis/              # 文本挖掘
│       ├── lda.py             # LDA 主题分析
│       ├── sentiment.py       # SnowNLP 情感分析
│       └── wordcloud.py       # 词云
├── scripts/                   # 可直接运行的入口脚本
│   ├── run_pipeline.py        # 一键运行完整机器学习流程
│   ├── crawl_acn.py
│   ├── crawl_bilibili.py
│   ├── crawl_weibo.py
│   └── run_analysis.py        # lda / sentiment / wordcloud
├── data/                      # 数据与输出（已被 .gitignore 排除，本地运行时生成）
│   ├── raw/                   # 原始数据
│   ├── processed/             # 中间清洗结果
│   ├── outputs/               # 图表与模型结果
│   ├── stopwords/             # 停用词（入库）
│   ├── fonts/                 # 中文字体（入库时不提交）
│   └── background/            # 词云蒙版（入库）
├── tests/
│   └── test_smoke.py          # 冒烟测试
├── requirements.txt
├── pyproject.toml
├── .env.example               # 环境变量模板（复制为 .env 填写凭证）
└── .gitignore
```

> `data/` 目录存放大数据集、模型与输出，已通过 `.gitignore` 排除，不会上传到 GitHub。请自行将数据放入 `data/raw/` 后运行。

---

## 快速开始

### 1. 环境准备

```bash
pip install -r requirements.txt
```

### 2. 配置凭证（可选，仅爬虫需要）

```bash
cp .env.example .env
# 编辑 .env，填入 ACN_API_KEY / BILIBILI_COOKIE / WEIBO_COOKIE
```

### 3. 运行机器学习流水线

```bash
python scripts/run_pipeline.py
```

将依次完成数据加载 → 清洗 → 建模 → 评估 → 生成 10 张论文图表，结果保存到 `data/outputs/`。

### 4. 运行文本分析

```bash
python scripts/run_analysis.py lda         # LDA 主题分析
python scripts/run_analysis.py sentiment  # 情感分析（需 snownlp）
python scripts/run_analysis.py wordcloud  # 词云
```

### 5. 数据采集

```bash
python scripts/crawl_acn.py                # ACN 数据
python scripts/crawl_weibo.py 江苏省充电桩 50  # 微博推文
python scripts/crawl_bilibili.py --keyword 充电桩 --mode comments  # B 站评论
```

### 6. 冒烟测试

```bash
python tests/test_smoke.py
```

---

## 研究内容

- **充电量预测**：以 `kWhDelivered` 为目标，特征含接入时段、星期、是否周末、是否江苏峰时、站点、有效充电时长，对比随机森林与 XGBoost 的 MAE / RMSE / R²。
- **行为洞察**：江苏峰谷时段订单分布、工作日 vs 周末差异、充电量-时长关系、充电后占位时长、星期-小时充电量热力图。
- **文本挖掘**：对 B 站 / 微博相关评论做 LDA 主题、情感与词云分析，补充舆情视角。

---

## 技术栈

Python 3.9+ · pandas · scikit-learn · XGBoost · matplotlib · seaborn · jieba · requests

## License

[MIT](LICENSE)
