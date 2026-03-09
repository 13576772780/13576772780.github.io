# Claude Code 网页重建闭环方案（LLM + 多模态评审）

## 1. 目标与角色分工

你有两类模型：

- **强语言模型（LLM）**：负责代码生成与修改（HTML/CSS/JS、组件结构、布局逻辑、样式细节）。
- **较弱多模态模型（VLM）**：只做“图像对比评审”，输出结构化修改建议，不直接写代码。

核心思想：把 VLM 当作“视觉质检员”，把 LLM 当作“开发工程师”，通过自动化循环逐步逼近目标图。

---

## 2. 输入/输出规范（先定协议，后做流程）

### 2.1 输入

每个任务准备以下文件：

- `target.png`：目标网页截图（你已有）。
- `layout.json`：你提前生成的页面描述 JSON（结构与相对位置）。
- （可选）`constraints.json`：品牌色、字体、是否响应式、必须像素级一致等限制。

### 2.2 中间产物

- `run_screenshot.png`：当前代码运行后的截图。
- `review.json`：VLM 对比结果（差异 + 优先级 + 建议）。
- `patch_prompt.md`：喂给 LLM 的“下一轮修改提示词”。

### 2.3 输出

- 可运行网页代码。
- 若干轮迭代记录（建议保留日志，便于回溯）。

---

## 3. 统一 JSON 协议（建议）

让 VLM 每次严格输出如下格式，便于程序消费：

```json
{
  "round": 3,
  "global_score": 0.78,
  "layout_similarity": 0.82,
  "style_similarity": 0.73,
  "issues": [
    {
      "id": "ISSUE-001",
      "severity": "high",
      "category": "layout",
      "component": "hero.title",
      "description": "标题块垂直位置偏高，约上移了 24px",
      "evidence": {
        "target_bbox": [120, 180, 760, 260],
        "current_bbox": [120, 156, 760, 236]
      },
      "suggestion": "将 hero 容器的 top padding 增加 24px"
    }
  ],
  "next_actions": [
    "先修复 high 级别布局问题",
    "再调整主按钮颜色与圆角"
  ]
}
```

要点：

- **强制字段**：`severity/category/component/suggestion`。
- **可排序**：优先处理 `high`。
- **可追踪**：`id` 防止重复改同一个问题。

---

## 4. Claude Code 中的迭代流水线

## 4.1 初始化阶段（第 0 轮）

1. 把 `target.png`、`layout.json` 放到项目目录。
2. 让 LLM 首次生成页面骨架：
   - 先做结构和布局，再做视觉细节。
   - 明确要求组件命名（如 `hero`, `feature-card`, `cta-btn`），方便 VLM 指向具体组件。
3. 本地启动页面并截图。

### 4.2 单轮迭代（第 N 轮）

1. **截图**：自动得到 `run_screenshot.png`。
2. **多模态评审**：把 `target.png + run_screenshot.png + layout.json` 输入 VLM，产出 `review.json`。
3. **提示词编排器（关键）**：把 `review.json` 转成给 LLM 的“最小修改指令”：
   - 只列 Top-K 问题（如 5 条）。
   - 按优先级排序。
   - 要求“只改必要文件，不重构无关代码”。
4. **LLM 改码**：执行 patch。
5. **自动检查**：启动、截图、可选视觉指标评估。
6. 终止判断：达到阈值就停止，否则继续下一轮。

---

## 5. 终止条件（避免无限循环）

建议同时设置：

- 最大轮数：`max_rounds = 8~12`
- 达标阈值：`global_score >= 0.92`
- 收敛阈值：连续 2 轮提升 `< 0.01` 则停止
- 人工兜底：出现冲突建议或明显跑偏时人工介入

---

## 6. Claude Code Prompt 模板（可直接用）

## 6.1 初始生成 Prompt（给强 LLM）

```text
你是资深前端工程师。
目标：根据 target.png 与 layout.json 还原网页。
要求：
1) 先保证结构与相对位置正确，再做颜色/字体/阴影等细节。
2) 代码可运行，语义化命名，组件名需与 layout.json 对齐。
3) 不要引入不必要依赖。
4) 输出变更文件与关键样式决策说明。
```

## 6.2 迭代修复 Prompt（给强 LLM）

```text
你将根据视觉评审结果进行“最小必要修改”。
输入：
- 当前代码
- review.json（按优先级列出问题）

规则：
1) 仅修改与 issue 相关的文件。
2) 先修 high，再修 medium，low 可延后。
3) 保持现有可运行性，不做大规模重构。
4) 修改后列出：
   - 变更文件
   - 每个 issue 的对应修复点
   - 仍未解决的问题（如有）
```

## 6.3 多模态评审 Prompt（给较弱 VLM）

```text
请比较 target.png 与 current.png，并结合 layout.json。
仅输出 JSON，格式必须匹配给定 schema。
重点：
1) 布局偏差（位置、间距、尺寸）
2) 视觉偏差（颜色、字体、圆角、阴影）
3) 组件缺失/多余
4) 给出可执行的 CSS/布局级建议（不要泛泛而谈）
```

---

## 7. 工程实现建议（最小可用）

即使在 Claude Code 里，也建议你在仓库放一个脚本化入口：

- `scripts/screenshot.(js|py)`：启动页面并统一尺寸截图（如 1440x1024）。
- `scripts/review.(js|py)`：调用 VLM API，保存 `review.json`。
- `scripts/build_patch_prompt.(js|py)`：从 `review.json` 生成 `patch_prompt.md`。
- `scripts/loop.(js|py)`：串起多轮流程。

这样你每轮只需要一句：

```bash
npm run loop
```

或

```bash
python scripts/loop.py
```

---

## 8. 质量控制细节（非常关键）

- **固定截图环境**：同一浏览器、同一 viewport、同一缩放比、同一字体加载策略。
- **分层修复**：先布局后样式，防止样式改动掩盖布局问题。
- **限制修改范围**：每轮最多修 Top-5 问题，降低引入回归风险。
- **防漂移机制**：要求 LLM 每轮说明“为何改这里而不是重写”。
- **可解释日志**：保存每轮 `review.json` 和代码 diff。

---

## 9. 常见失败模式与对策

- VLM 建议太空泛：
  - 对策：强制输出 bbox 或像素偏移描述。
- LLM 过度重构：
  - 对策：Prompt 里加“最小必要修改 + 禁止无关重命名”。
- 来回震荡（本轮修好，下轮又坏）：
  - 对策：在 review 中加入“回归检查项”（上一轮已解决 issue 不得复发）。
- 字体/渲染不一致：
  - 对策：固定字体源，截图机装同字体，或改用 webfont 并等待加载完成再截图。

---

## 10. 推荐的落地顺序

1. 先手动跑通 2 轮（验证协议和 prompt）。
2. 再脚本化截图 + 评审 + prompt 生成。
3. 最后加自动停止条件与日志归档。

这样你能在 Claude Code 里快速得到一个“可控、可复现、可持续优化”的网页还原闭环。
