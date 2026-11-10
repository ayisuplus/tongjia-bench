# -*- coding: utf-8 -*-
"""
TongJia-Bench pilot 数据生成脚本
生成 T2（拼音剖面）与 T3（机制归因）pilot 数据集。

依赖：pypinyin
运行：python scripts/generate_pilot.py
"""
import json
import os
import random
from pypinyin import pinyin, Style

random.seed(42)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "pilot")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 基础词表：成语 / 常用词，用于 T3 同音字替换
# 每条: (目标词, 替换位置, 替换用同音/近音字)
# 手工构造，保证: 1) 替换后语义不通; 2) 组合在语料中罕见(memorization-proof)
# ---------------------------------------------------------------------------
CHENGYU_ITEMS = [
    ("一劳永逸", 3, "遗"), ("按部就班", 1, "步"), ("变本加厉", 2, "利"),
    ("不计其数", 2, "记"), ("川流不息", 0, "穿"), ("再接再厉", 1, "励"),
    ("名副其实", 1, "付"), ("鬼斧神工", 1, "斧"), ("焕然一新", 0, "换"),
    ("矫枉过正", 0, "娇"), ("脍炙人口", 0, "脍"), ("滥竽充数", 3, "树"),
    ("莫名其妙", 1, "名"), ("呕心沥血", 3, "雪"), ("迫不及待", 2, "急"),
    ("恰如其分", 3, "份"), ("锲而不舍", 1, "而"), ("情不自禁", 3, "尽"),
    ("人云亦云", 2, "一"), ("肆无忌惮", 1, "弹"), ("铤而走险", 0, "挺"),
    ("委曲求全", 0, "委"), ("无所事事", 1, "是"), ("相形见绌", 3, "拙"),
    ("心无旁骛", 3, "鹜"), ("形影不离", 2, "离"), ("意气风发", 1, "气"),
    ("因地制宜", 3, "治"), ("有的放矢", 2, "地"), ("振聋发聩", 3, "馈"),
    ("直截了当", 1, "接"), ("炙手可热", 0, "灸"), ("走投无路", 1, "头"),
    ("变本加厉", 2, "利"), ("潸然泪下", 3, "下"), ("恪守不渝", 2, "不"),
    ("敝帚自珍", 3, "真"), ("草菅人命", 3, "明"), ("姹紫嫣红", 3, "洪"),
    ("瞠目结舌", 3, "蛇"), ("出类拔萃", 1, "翠"), ("咄咄逼人", 3, "人"),
    ("阿谀奉承", 3, "成"), ("刚愎自用", 3, "用"), ("孤陋寡闻", 3, "文"),
    ("含辛茹苦", 3, "古"), ("好高骛远", 3, "务"), ("怙恶不悛", 3, "圈"),
    ("讳疾忌医", 3, "一"), ("岌岌可危", 3, "微"), ("家喻户晓", 3, "小"),
]

WORD_ITEMS = [
    ("锻炼", 1, "练", "他每天早起{}身体", "强健体魄的方式"),
    ("化妆", 1, "装", "她出门前总要{}", "女性的日常"),
    ("暴躁", 0, "爆", "他的脾气很{}", "性格评价"),
    ("喧嚣", 0, "宣", "夜市里一片{}", "环境描写"),
    ("提纲", 1, "题", "写文章前先列{}", "写作准备"),
    ("脉搏", 1, "博", "医生按住了他的{}", "身体检查"),
    ("陷阱", 1, "井", "猎人设下了{}", "捕猎手段"),
    ("竣工", 0, "俊", "大桥终于{}", "工程进度"),
    ("感慨", 1, "概", "他不禁{}万分", "情绪表达"),
    ("寒暄", 1, "喧", "两人见面互相{}", "社交礼仪"),
    ("蜜饯", 1, "钱", "她买了一包{}", "零食种类"),
    ("缅怀", 0, "湎", "我们{}先烈", "纪念活动"),
    ("嘈杂", 1, "糟", "教室里很{}", "环境评价"),
    ("聒噪", 1, "燥", "蝉鸣十分{}", "夏日声音"),
    ("绮丽", 0, "起", "风光{}多彩", "景色描写"),
    ("瞌睡", 0, "磕", "上课他直打{}", "困倦表现"),
    ("谩骂", 1, "漫", "网上互相{}", "网络行为"),
    ("裨益", 1, "意", "读书大有{}", "学习收获"),
    ("信笺", 1, "件", "她展开一页{}", "书信往来"),
    ("躁动", 1, "燥", "人群开始{}", "场面失控"),
]

# T2 拼音剖面用的句子（拼音→汉字还原 & 拼音问答）
T2_SENTENCES = [
    "北京是中国的首都",
    "人工智能正在改变世界",
    "今天的天气非常适合郊游",
    "这本书的内容十分有趣",
    "科技创新推动社会进步",
    "他每天坚持锻炼身体",
    "中文是世界上最难的语言之一",
    "保护环境是每个人的责任",
    "这个问题需要认真研究",
    "音乐能够陶冶人的情操",
    "知识改变命运",
    "团结就是力量",
    "失败是成功之母",
    "时间就像海绵里的水",
    "读书破万卷下笔如有神",
]

T2_QA = [
    ("中国的首都是哪里", "北京"),
    ("一年有几个季节", "四个"),
    ("水的化学式是什么", "H2O"),
    ("太阳从哪个方向升起", "东方"),
    ("一周有几天", "七天"),
    ("汉字使用什么文字系统", "表意文字"),
    ("长江是中国第几长的河流", "第一"),
    ("地球绕什么公转", "太阳"),
    ("春节是中国的什么节日", "传统节日"),
    ("三角形有几个角", "三个"),
]

INITIALS_EXCEPTIONS = {"zh": "z", "ch": "c", "sh": "s"}


def to_pinyin(text, style):
    """整句转拼音，返回空格分隔的拼音串"""
    result = pinyin(text, style=style, errors="ignore")
    return " ".join(item[0] for item in result)


def to_initials(text):
    """转首字母缩写（声母），zh/ch/sh 取 z/c/s"""
    result = pinyin(text, style=Style.INITIALS, strict=False, errors="ignore")
    parts = []
    for item in result:
        ini = item[0]
        if ini in INITIALS_EXCEPTIONS:
            ini = INITIALS_EXCEPTIONS[ini]
        parts.append(ini if ini else "")
    return " ".join(parts)


def mixed_text(text, hanzi_ratio):
    """按汉字比例混合汉字与无声调拼音"""
    chars_pinyin = pinyin(text, style=Style.NORMAL, errors="ignore")
    out = []
    for ch, py in zip(text, chars_pinyin):
        if "\u4e00" <= ch <= "\u9fff":
            out.append(ch if random.random() < hanzi_ratio else py[0])
        else:
            out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------------------
# T2: 拼音剖面
# ---------------------------------------------------------------------------
def gen_t2():
    rows = []
    conditions = [
        ("tone_mark", Style.TONE),
        ("tone_number", Style.TONE3),
        ("no_tone", Style.NORMAL),
    ]
    idx = 0
    for sent in T2_SENTENCES:
        for cond, style in conditions:
            py = to_pinyin(sent, style)
            idx += 1
            rows.append({
                "id": f"t2-p2h-{idx:04d}",
                "track": "T2",
                "task": "pinyin2hanzi",
                "condition": cond,
                "input": f"请将以下拼音还原为正确的中文句子，只输出还原结果：\n{py}",
                "target": sent,
                "meta": {"tone_form": cond, "source": "t2_sentences_v1"},
            })
        # 首字母缩写
        idx += 1
        rows.append({
            "id": f"t2-p2h-{idx:04d}",
            "track": "T2",
            "task": "pinyin2hanzi",
            "condition": "initials",
            "input": f"以下是中文句子的拼音首字母缩写，请还原为最可能的中文句子，只输出还原结果：\n{to_initials(sent)}",
            "target": sent,
            "meta": {"tone_form": "initials", "source": "t2_sentences_v1"},
        })
        # 混写（汉字比例 0.5）
        idx += 1
        rows.append({
            "id": f"t2-p2h-{idx:04d}",
            "track": "T2",
            "task": "pinyin2hanzi",
            "condition": "mixed_50",
            "input": f"以下是汉字与拼音混写的句子，请还原为正确的中文句子，只输出还原结果：\n{mixed_text(sent, 0.5)}",
            "target": sent,
            "meta": {"tone_form": "no_tone", "mix_ratio": 0.5, "source": "t2_sentences_v1"},
        })
    # 拼音问答：用无声调拼音直接提问
    for i, (q, a) in enumerate(T2_QA, 1):
        py_q = to_pinyin(q, Style.NORMAL)
        rows.append({
            "id": f"t2-pqa-{i:04d}",
            "track": "T2",
            "task": "pinyin_qa",
            "condition": "no_tone",
            "input": f"请阅读以下拼音问题并用中文简要回答：\n{py_q}",
            "target": a,
            "meta": {"tone_form": "no_tone", "source": "t2_qa_v1"},
        })
    return rows


# ---------------------------------------------------------------------------
# T3: 机制归因（三条件 minimal pair）
# ---------------------------------------------------------------------------
def gen_t3():
    rows = []
    gid = 0
    # 成语组：C0 / C+ 两条件（成语本身就是强上下文）
    for word, pos, distractor in CHENGYU_ITEMS:
        gid += 1
        wrong = word[:pos] + distractor + word[pos + 1:]
        py = pinyin(word[pos], style=Style.TONE3)[0][0]
        # C0: 上下文抽空——只给错词，不给任何语义线索
        rows.append({
            "id": f"t3-idiom-{gid:04d}-c0",
            "track": "T3",
            "task": "homophone_recovery",
            "condition": "C0",
            "input": f"「{wrong}」中有一个错别字，请改正并只输出改正后的词语：",
            "target": word,
            "meta": {
                "group_id": f"idiom-{gid:04d}",
                "target_word": word,
                "perturbed_char": word[pos],
                "distractor_char": distractor,
                "pinyin": py,
                "context_condition": "neutral",
                "source": "chengyu_list_v1",
            },
        })
        # C+: 上下文强提示——给出释义
        rows.append({
            "id": f"t3-idiom-{gid:04d}-cp",
            "track": "T3",
            "task": "homophone_recovery",
            "condition": "C+",
            "input": f"「{wrong}」中有一个错别字。提示：这是一个四字成语。请改正并只输出改正后的成语：",
            "target": word,
            "meta": {
                "group_id": f"idiom-{gid:04d}",
                "target_word": word,
                "perturbed_char": word[pos],
                "distractor_char": distractor,
                "pinyin": py,
                "context_condition": "strong",
                "source": "chengyu_list_v1",
            },
        })
    # 词语组：C0 / C+ / C- 三条件
    for word, pos, distractor, template, hint in WORD_ITEMS:
        gid += 1
        wrong = word[:pos] + distractor + word[pos + 1:]
        py = pinyin(word[pos], style=Style.TONE3)[0][0]
        sent_wrong = template.format(wrong)
        base_meta = {
            "group_id": f"word-{gid:04d}",
            "target_word": word,
            "perturbed_char": word[pos],
            "distractor_char": distractor,
            "pinyin": py,
            "source": "word_list_v1",
        }
        # C0
        rows.append({
            "id": f"t3-word-{gid:04d}-c0",
            "track": "T3", "task": "homophone_recovery", "condition": "C0",
            "input": f"「{wrong}」中有一个错别字，请改正并只输出改正后的词语：",
            "target": word,
            "meta": {**base_meta, "context_condition": "neutral"},
        })
        # C+
        rows.append({
            "id": f"t3-word-{gid:04d}-cp",
            "track": "T3", "task": "homophone_recovery", "condition": "C+",
            "input": f"句子「{sent_wrong}」中有一个错别字，请改正并只输出改正后的完整词语：",
            "target": word,
            "meta": {**base_meta, "context_condition": "strong"},
        })
        # C-: 上下文误导——给出语义含糊的提示，指向 distractor 的常见搭配
        rows.append({
            "id": f"t3-word-{gid:04d}-cm",
            "track": "T3", "task": "homophone_recovery", "condition": "C-",
            "input": f"「{wrong}」中可能有一个错别字，也可能没有。{hint}。请判断并只输出你认为正确的词语：",
            "target": word,
            "meta": {**base_meta, "context_condition": "misleading"},
        })
    return rows


def write_jsonl(rows, filename):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {path}")


if __name__ == "__main__":
    t2 = gen_t2()
    t3 = gen_t3()
    write_jsonl(t2, "t2_pinyin_profile.jsonl")
    write_jsonl(t3, "t3_mechanism_attribution.jsonl")
    # 统计
    from collections import Counter
    print("T2 conditions:", Counter(r["condition"] for r in t2))
    print("T3 conditions:", Counter(r["condition"] for r in t3))
