# Review JSON Schema (for multimodal comparison)

Use this structure for each review round:

```json
{
  "round": 1,
  "global_score": 0.0,
  "layout_similarity": 0.0,
  "style_similarity": 0.0,
  "issues": [
    {
      "id": "ISSUE-001",
      "severity": "high",
      "category": "layout",
      "component": "hero.title",
      "description": "具体偏差描述（尽量包含像素或相对位置）",
      "suggestion": "可执行的 CSS/布局建议"
    }
  ],
  "next_actions": ["下一步动作 1", "下一步动作 2"]
}
```

## Severity mapping

- `high`: breaks layout hierarchy, major positioning/size mismatch, missing key component.
- `medium`: noticeable style mismatch with acceptable structure.
- `low`: polish-level differences.

## Category values

- `layout`
- `style`
- `content`
- `component_missing`
- `component_extra`

## Validation checks

- Ensure all required fields exist.
- Ensure `issues` is an array (can be empty).
- Ensure `severity` uses only `high|medium|low`.
- Ensure `suggestion` is actionable.
