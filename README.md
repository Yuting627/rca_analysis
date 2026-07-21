# SKU RCA

基于 Unit / Regular Price / Promotion Price 的 SKU 月度根因分析批处理管线。

- 双价值轨：`regular_value = unit × regular_price`，`promotion_value = unit × promo_price`（共用 unit）
- Shapley 价量分解（无残差），双轨加权
- 全体涨跌方向 `market_sign` 统一驱动 contribution 排序、abnormal、trend、priority、主因选择（不取绝对值）
- 日期格式：`YYYY14MM`（例：`20261407` = 2026 年 7 月）
- **输入/输出路径、报告期、对比模式、列名等均在配置文件中设置**

## 安装

```bash
pip install -r requirements.txt
pip install -e .
```

## 配置

编辑 [`config/default.yaml`](config/default.yaml)：

```yaml
io:
  input: data/sample/sku_monthly.csv
  output: output/priority_20261407.csv
  mode: yoy          # mom | yoy（默认 yoy）

period:
  format: YYYY14MM
  report: "20261407"

columns:
  sku_id: sku_id
  # ...
```

相对路径相对于项目根目录（`config/` 的上一级）。

## 运行

只需指定配置文件（可省略，默认 `config/default.yaml`）：

```bash
python scripts/run_rca.py
python scripts/run_rca.py --config config/default.yaml
```

## 测试

```bash
python -m pytest
```

## 配置要点

- `io.input` / `io.output` / `io.mode`：输入输出与 MoM/YoY
- `period.report`：报告期
- `columns`：业务列名 → 内部标准名
- `weights.regular` / `weights.promotion`：之和须为 1
