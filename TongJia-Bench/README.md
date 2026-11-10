# TongJia-Bench（通假基准）

> 大模型中文错别字容错与拼音理解基准 —— 不仅测"能不能容错"，还测"靠什么容错"。

"通假"是古人用同音字替代本字的现象。两千年后，用户在输入法里打出的同音错字，本质上是同一件事。TongJia-Bench 系统评测大语言模型在这个场景下的能力剖面。

## 任务体系

| Track | 名称 | 测什么 |
|---|---|---|
| T1 | 容错理解 | 注入同音/近音/形近错误后，下游理解任务的性能保持率 |
| T2 | 拼音剖面 | 带调/无声调/数字调/缩写/混写 五种拼音形态的理解与转换 |
| T3 | 机制归因 ⭐ | 三条件 minimal pair（上下文强提示/抽空/误导），计算 PTI 语音通道指数 |
| T4 | 同音伪装检测 | 内容安全向扩展（v0.2） |

## 目录结构

```
TongJia-Bench/
├── README.md
├── docs/
│   └── 设计方案.md          # 完整设计文档
├── data/
│   ├── schema.md            # 数据格式定义
│   └── pilot/               # pilot 数据集（JSONL）
│       ├── t2_pinyin_profile.jsonl
│       └── t3_mechanism_attribution.jsonl
├── scripts/
│   ├── generate_pilot.py    # pilot 数据生成脚本
│   └── eval_runner.py       # 评测运行器（骨架）
└── results/                 # 评测结果
```

## 快速开始

```bash
# 生成 pilot 数据
python scripts/generate_pilot.py

# 评测（待实现 API 接入）
python scripts/eval_runner.py --data data/pilot/t3_mechanism_attribution.jsonl --model deepseek-chat
```

## 状态

v0.1 pilot 阶段。详见 [docs/设计方案.md](docs/设计方案.md)。
