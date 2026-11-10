# -*- coding: utf-8 -*-
"""
TongJia-Bench 评测运行器（骨架 v0.1）

用法:
    python scripts/eval_runner.py --data data/pilot/t3_mechanism_attribution.jsonl \
        --model deepseek-chat --out results/t3_deepseek-chat.jsonl

模型接入：实现 call_model() 中的对应分支，或统一走 OpenAI 兼容接口。
"""
import argparse
import json
import os
import re
import time
from collections import defaultdict


def call_model(prompt: str, model: str) -> str:
    """统一模型调用入口。当前支持 OpenAI 兼容接口（环境变量 BASE_URL / API_KEY）。"""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("请先 pip install openai")
    client = OpenAI(
        base_url=os.environ.get("TONGJIA_BASE_URL", "https://api.deepseek.com"),
        api_key=os.environ.get("TONGJIA_API_KEY", ""),
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=float(os.environ.get("TONGJIA_TEMPERATURE", "0.0")),
    )
    return resp.choices[0].message.content.strip()


def normalize(text: str) -> str:
    """去掉标点、空白、引号，便于 EM 匹配"""
    return re.sub(r"[\s，。！？、「」『』\"'：:；;.\?!,]+", "", text)


def score_row(row: dict, output: str) -> bool:
    """按任务类型判分。T2/T3 均用归一化 EM；T2 pinyin_qa 用包含匹配。"""
    out_n = normalize(output)
    tgt_n = normalize(row["target"])
    if row["task"] == "pinyin_qa":
        return tgt_n in out_n
    return out_n == tgt_n or tgt_n in out_n


def aggregate(rows: list[dict]) -> dict:
    """按 condition 分组统计；T3 额外计算 PTI。"""
    by_cond = defaultdict(lambda: [0, 0])
    groups = defaultdict(dict)  # group_id -> {condition: correct}
    for r in rows:
        c = by_cond[r["condition"]]
        c[1] += 1
        c[0] += int(r["correct"])
        gid = r.get("meta", {}).get("group_id")
        if gid:
            groups[gid][r["condition"]] = bool(r["correct"])
    report = {cond: {"acc": v[0] / v[1], "n": v[1]} for cond, v in sorted(by_cond.items())}
    # PTI = Acc(C0) / Acc(C+)，按组对齐
    c0 = [g["C0"] for g in groups.values() if "C0" in g and "C+" in g]
    cp = [g["C+"] for g in groups.values() if "C0" in g and "C+" in g]
    if c0 and cp:
        acc0 = sum(c0) / len(c0)
        accp = sum(cp) / len(cp)
        report["PTI"] = round(acc0 / accp, 4) if accp > 0 else None
        report["Acc_C0"] = round(acc0, 4)
        report["Acc_C+"] = round(accp, 4)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 条（调试用）")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    if args.limit:
        rows = rows[: args.limit]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    results = []
    for i, row in enumerate(rows, 1):
        output = call_model(row["input"], args.model)
        correct = score_row(row, output)
        results.append({**row, "model": args.model, "output": output, "correct": correct})
        print(f"[{i}/{len(rows)}] {row['id']} correct={correct}")
        time.sleep(0.3)

    with open(args.out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    report = aggregate(results)
    report_path = args.out.replace(".jsonl", "_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "data": args.data, "metrics": report}, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
