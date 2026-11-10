# TongJia-Bench 数据 Schema v0.1

所有数据文件为 JSONL（每行一个 JSON 对象）。

## 通用字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 唯一 ID，格式 `{track}-{task}-{序号}` |
| `track` | string | `T1` / `T2` / `T3` / `T4` |
| `task` | string | 任务名，见下 |
| `condition` | string | 实验条件标签（track 内自定义） |
| `input` | string | 给模型的完整输入（含指令） |
| `target` | string | 标准答案 |
| `meta` | object | 实验变量元数据 |

## Track 专属

### T1 容错理解
- `task`: `qa` / `nli` / `mrc`
- `meta.error_type`: `homophone` / `near_homophone` / `glyph` / `random`
- `meta.error_rate`: float, 0–0.5
- `meta.context_len`: `short` / `long`

### T2 拼音剖面
- `task`: `pinyin2hanzi` / `pinyin_qa`
- `condition`: `tone_mark` / `tone_number` / `no_tone` / `initials` / `mixed_25` / `mixed_50` / `mixed_75`
- `meta.tone_form`: 同上
- `meta.mix_ratio`: float（混写时为汉字比例）

### T3 机制归因
- `task`: `homophone_recovery`
- `condition`: `C+`（上下文强提示） / `C0`（上下文抽空） / `C-`（上下文误导）
- `meta.target_word`: 目标词（如"一劳永逸"）
- `meta.perturbed_char` / `meta.distractor_char`: 被替换字 / 替换用同音字
- `meta.pinyin`: 该字拼音（数字调）
- `meta.context_condition`: `strong` / `neutral` / `misleading`
- 三条件样本共享同一 `meta.group_id`，评测时按组对齐

### T4 同音伪装检测（v0.2 预留）
- `task`: `toxic_detect`
- `meta.cloak_type`: `homophone` / `initials` / `mixed`

## 派生指标定义

- **容错保持率** = Acc(噪声条件) / Acc(干净条件)，T1 使用
- **PTI（语音通道指数）** = Acc(C0) / Acc(C+)，T3 使用；按 `group_id` 对齐后先算组内再平均
- **声调敏感度** = Acc(tone_mark) − Acc(no_tone)，T2 使用
