# SKU RCA

基于 Unit / Regular Price / Promotion Price 的 SKU 月度根因分析批处理管线。

- 双价值轨：`regular_value = unit × regular_price`，`promotion_value = unit × promo_price`（共用 unit）
- Shapley 价量分解（无残差），双轨加权
- 全体涨跌方向 `market_sign` 统一驱动 contribution 排序、abnormal、trend、priority、主因选择（不取绝对值）
- 日期格式：`YYYY14MM`（例：`20261407` = 2026 年 7 月）
- 输入列名由 `config/default.yaml` 配置

## 安装

```bash
pip install -r requirements.txt
pip install -e .
```

## 运行

```bash
python scripts/run_rca.py --input data/sample/sku_monthly.csv --period 20261407 --config config/default.yaml --out output/priority_20261407.csv
```

## 测试

```bash
pytest
```

## 配置要点

- `columns`：业务列名 → 内部标准名
- `weights.regular` / `weights.promotion`：之和须为 1
- `period.format`：固定 `YYYY14MM`
