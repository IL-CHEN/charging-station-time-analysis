# -*- coding: utf-8 -*-
"""一键运行：ACN 数据 → 特征工程 → 随机森林/XGBoost 训练评估 → 生成 10 张论文图表。

用法：
    python scripts/run_pipeline.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from chargstation.pipeline import DataLoader, DataProcessor, MLModelTrainer, PaperVisualizer


def main() -> None:
    print("=" * 70)
    print("🚀 基于 ACN 数据与机器学习的江苏省充电桩充电行为分析与预测研究")
    print("=" * 70)

    # 1. 数据加载
    loader = DataLoader()
    df_raw = loader.load_all()

    # 2. 数据清洗与特征工程
    processor = DataProcessor()
    df_cleaned = processor.process(df_raw)

    # 3. 机器学习模型训练
    trainer = MLModelTrainer()
    X_train, X_test, y_train, y_test = trainer.prepare_data(df_cleaned)

    rf_model = trainer.train_random_forest(X_train, y_train)
    xgb_model = trainer.train_xgboost(X_train, y_train)

    models = {"Random Forest": rf_model, "XGBoost": xgb_model}
    results_df, feature_importance_list = trainer.evaluate_models(models, X_test, y_test)

    # 4. 生成 10 张论文图表
    visualizer = PaperVisualizer()
    visualizer.plot_all(df_cleaned, results_df, feature_importance_list)

    # 5. 最终结论
    print("\n" + "=" * 70)
    print("📝 研究核心结论（可直接写入论文）")
    print("=" * 70)
    print(f"1. 数据规模：共分析 {len(df_cleaned)} 条有效充电会话记录")
    print(f"2. 平均单次充电量：{df_cleaned['kWhDelivered'].mean():.2f} kWh")
    print(f"3. 平均有效充电时长：{df_cleaned['effective_charging_h'].mean():.2f} 小时")
    print(f"4. 平均充电后占位时长：{df_cleaned['idle_occupy_h'].mean():.2f} 小时")
    print(f"5. 江苏峰时充电订单占比：{df_cleaned['is_jiangsu_peak'].mean():.1%}")
    print(f"\n6. 最佳模型：{results_df.loc[results_df['R²'].idxmax(), 'Model']}")
    print(f"   最佳模型 MAE：{results_df['MAE (kWh)'].min():.2f} kWh")
    print(f"   最佳模型 R²：{results_df['R²'].max():.2f}")

    print("\n💡 针对江苏省的优化策略建议：")
    print("   - 扩大峰谷电价价差，引导用户错峰充电；")
    print("   - 推行阶梯式占位费机制，提高车位周转率；")
    print("   - 在产业园区、写字楼配套建设快充桩，匹配通勤需求。")

    print("\n✅ 全流程执行完成！所有结果已保存至 data/outputs/")


if __name__ == "__main__":
    main()
