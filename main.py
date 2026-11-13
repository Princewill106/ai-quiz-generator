"""AI Quiz Generator."""
import argparse
import csv
import random
import re
from pathlib import Path

import llm

PATTERN = re.compile(r"^(?:(?:An?|The)\s+)?([A-Za-z][\w\s-]{1,40}?)\s+(is|are|refers to|means)\s+(.+?)\.$")


def facts(text):
    out = []
    for s in re.split(r"(?<=\.)\s+|\n+", text):
        m = PATTERN.match(s.strip())
        if m:
            term = m.group(1).strip()
            out.append({"term": term[0].upper() + term[1:], "verb": m.group(2),
                        "definition": m.group(3).strip()})
    return out


def build(fs, count, seed=7):
    rng = random.Random(seed)
    terms = [f["term"] for f in fs]
    questions = []
    for i, f in enumerate(fs[:count]):
        others = [t for t in terms if t != f["term"]]
        if i % 2 == 0 and len(others) >= 3:
            opts = rng.sample(others, 3) + [f["term"]]
            rng.shuffle(opts)
            q = {"type": "MCQ", "question": f"Which term {f['verb']} {f['definition']}?",
                 "options": opts, "answer": f["term"]}
        else:
            q = {"type": "Fill in the blank",
                 "question": f"________ {f['verb']} {f['definition']}.", "options": [],
                 "answer": f["term"]}
        questions.append(q)
    return questions


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="sample_notes.txt")
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    text = Path(a.input).read_text(encoding="utf-8")
    qs = build(facts(text), a.count)
    extra = llm.complete("Write 2 higher-order thinking questions (why/how) based on these notes, "
                         f"each on one line:\n{text}")
    sheet, key = ["# Quiz", ""], ["# Answer key", ""]
    for i, q in enumerate(qs, 1):
        sheet.append(f"{i}. {q['question']}")
        for j, o in enumerate(q["options"]):
            sheet.append(f"   {'ABCD'[j]}. {o}")
        key.append(f"{i}. {q['answer']}")
        sheet.append("")
    if extra:
        sheet += ["## Discussion", ""] + [l for l in extra.splitlines() if l.strip()]
    Path("output").mkdir(exist_ok=True)
    Path("output/quiz.md").write_text("\n".join(sheet))
    Path("output/answer_key.md").write_text("\n".join(key))
    with open("output/quiz_forms.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question", "type", "option_a", "option_b", "option_c", "option_d", "answer"])
        for q in qs:
            w.writerow([q["question"], q["type"]] + (q["options"] + [""] * 4)[:4] + [q["answer"]])
    print("\n".join(sheet))
    print("\n".join(key))
    print("\nSaved output/quiz.md, output/answer_key.md, output/quiz_forms.csv")


if __name__ == "__main__":
    main()
