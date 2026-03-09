#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build minimal patch prompt from review.json")
    parser.add_argument("--review", default="review.json", help="Path to review json")
    parser.add_argument("--top-k", type=int, default=5, help="Max issues to include")
    parser.add_argument("--output", default="patch_prompt.md", help="Output markdown prompt")
    args = parser.parse_args()

    review_path = Path(args.review)
    data = json.loads(review_path.read_text(encoding="utf-8"))

    issues = data.get("issues", [])
    priority = {"high": 0, "medium": 1, "low": 2}
    issues = sorted(issues, key=lambda x: (priority.get(x.get("severity", "low"), 3), x.get("id", "")))
    selected = issues[: args.top_k]

    lines = [
        "# Patch Prompt",
        "",
        "你将根据 visual review 结果进行最小必要修改。",
        "",
        "规则：",
        "1. 仅修改与 issue 相关文件（Vue SFC/样式文件）。",
        "2. 按 high -> medium -> low 顺序处理。",
        "3. 不做无关重构。",
        "4. 输出变更文件和 issue 对应关系。",
        "",
        f"当前 global_score: {data.get('global_score', 'N/A')}",
        "",
        "## Top Issues",
    ]

    if not selected:
        lines.append("- 无问题，建议停止迭代。")
    else:
        for i, item in enumerate(selected, start=1):
            lines.extend(
                [
                    f"{i}. [{item.get('severity', 'low')}] {item.get('id', 'NO-ID')} ({item.get('category', 'unknown')} / {item.get('component', 'unknown')})",
                    f"   - 问题: {item.get('description', '').strip()}",
                    f"   - 建议: {item.get('suggestion', '').strip()}",
                ]
            )

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(selected)} issue(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
