---
name: factor-calendar-formulas
description: "Compute deterministic Factor Calendar formula values from long-form daily market and point-in-time fundamental data. Use when an agent needs selected or full Factors Directory formula columns, wide or long factor files, and skipped-factor metadata without LLM evaluation, IC calculation, signal direction, or backtesting."
metadata:
  quantSkills:
    organization: https://github.com/quantskills
    repository: quantskills/skill-factor-calendar-formulas
    repository_url: https://github.com/quantskills/skill-factor-calendar-formulas
    project_type: skill
    collection: factor-library
    license: GPL-3.0-only
    category: factor
    tags: [factor-library, factor-calendar, market-data, fundamental-data, factor-formulas]
    platforms: [codex]
    language: zh-en
    status: stable
    validation_level: verified
    maintainer_type: community
    requires: []
    summary_zh: 复现 Factors Directory 公开公式，支持 241 个量价、流动性、情绪与基本面因子的全量和指定运行。
    summary_en: Compute 241 Factor Calendar formula values from long-form daily market and point-in-time fundamental data.
---

```json qsh-form
{
  "version": 1,
  "task": {
    "placeholder": "说明行情与基本面数据文件、计算区间及输出要求；请上传或指明输入数据",
    "required": true
  },
  "fields": [
    {
      "key": "factor_names",
      "label": "指定因子",
      "type": "textarea",
      "placeholder": "留空计算全部；可填 amount_volatility、factor-calendar.book_to_market_ratio 等"
    },
    {
      "key": "exclude_factor_names",
      "label": "排除因子",
      "type": "textarea",
      "placeholder": "可选，填写不需要计算的因子名"
    }
  ],
  "prompt_template": "{{#task}}任务与材料：\n{{task}}\n\n{{/task}}{{#attachments}}用户上传的材料（已放入工作区）：\n{{attachments}}\n\n{{/attachments}}依据输入契约从长表日频行情与时点基本面数据确定性计算 Factor Calendar 因子值。{{#factor_names}}仅计算指定因子：{{factor_names}}；{{/factor_names}}{{#exclude_factor_names}}排除：{{exclude_factor_names}}；{{/exclude_factor_names}}导出因子值文件、运行配置、计算摘要和跳过因子清单，不执行 IC、信号方向、回测或投资判断，输出中文报告。"
}
```

# Factor Calendar Formulas

Use this skill to compute deterministic values for 241 bundled Factor Calendar formulas from long-form daily market and point-in-time fundamental data.

## Core Workflow

1. Read references/input_schema.md before preparing the input JSON.
2. Use factor_names and exclude_factor_names to select formulas. Both amount_volatility and factor-calendar.amount_volatility are accepted.
3. Include enough pre-window history through load_start_date and load_end_date before restricting results with start_date and end_date.
4. Run the unified CLI:

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json
```

5. Read references/output_contract.md before consuming generated artifacts.

## Output Contract

The skill writes factor values and JSON metadata under the configured output directory:

- factor_calendar_values.csv or .parquet for wide output
- factor_calendar_panel.csv or .parquet for long output
- factor_compute_summary.json
- skipped_factors.json
- factor_manifest.json
- run_config.json

## Boundaries

This is a factor-library computation skill. It does not compute IC, ICIR, empirical signal direction, portfolio returns, backtests, or trading recommendations. Use only user-provided or authorized data, and treat financial fields as point-in-time aligned.

## References

- Use references/input_schema.md for input fields and configuration.
- Use references/output_contract.md for artifact names and result fields.
- Use references/source_boundary.md for formula and data boundaries.
- Use references/validation_notes.md for implementation assumptions and limitations.
