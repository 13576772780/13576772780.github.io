# Claude Code Skills for Vue Visual Rebuild

## Included skill

- `vue-iterative-page-rebuild`: 使用目标图 + layout JSON + 多模态评审结果，迭代修复 Vue 页面。

## Suggested usage in Claude Code

1. 将 `skills/vue-iterative-page-rebuild` 复制到你的 skills 目录。
2. 在任务中明确提到该 skill 名称或描述你的场景（Vue 页面截图对齐、多轮评审修复）。
3. 使用 skill 内脚本生成 patch prompt 和停止判断：
   - `python scripts/build_patch_prompt.py --review review.json --output patch_prompt.md`
   - `python scripts/evaluate_stop.py --history scores.json`
