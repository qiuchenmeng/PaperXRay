# PaperXRay · SI-Assistant-Reference-Reader (SARR)

> **Minimum Words. Maximum Understanding.** — 用最少的必要信息，获得最充分的论文理解。

PaperXRay 是一个面向科研人员的 **SI-Assistant 论文阅读 Skill**。它不做最长的论文总结，也不机械地压缩回答，而是围绕研究者的**当前疑问**给出「最小充分解释」。
能够根据研究者的关注偏好/提问的内容和对回答的反馈，迭代更加适合研究者的论文阅读prompt,实现复利，实现模型越来越懂你在问什么

它提供两个功能，各对应一份运行 Prompt：

| 内容 | 面向 | 成品 |
| --- | --- | --- |
| Prompt | 直接使用者 | `prompts/runtime-prompt-default.md` · SI-Assistant-Reference-Reader prompt，粘贴即用 |
| SKILL  | 开发者    | `prompts/runtime-prompt-personalized.md` · 根据你向SI提问的问题生成的你的定制化 SI-Assistant-Reference-Reader prompt |


---

## SI-Assistant-Reference-Reader Prompt

`prompts/runtime-prompt-default.md`中包含`# 中文版` 与 `# English version` 两种语言，粘贴即用。


**想要更贴合自己的prompt？download our skill and generate the personlized prompt**

---

## Personalized SI-Assistant-Reference-Reader Prompt（产出你的定制化prompt）

 `SKILL.md` 把你真实的阅读反馈——哪些回答有用、哪些多余、适用于什么情形——经 元-Prompt 归纳成一份 **帮助大模型理解你的阅读偏好的Prompt**。

**Installation**

git clone xxx


**How to use**

| 环节 | 文件 | 作用 |
| --- | --- | --- |
| 反馈样本 | `data/reference.json` | 问题、helpful / redundant 内容与适用范围 |
| 归纳（元 Prompt） | `prompts/derive-prompt.md` | Explanation Policy Synthesizer：把反馈归纳成运行 Prompt |
| 定制化成品 | `prompts/runtime-prompt-personalized.md` | 你的版本；覆盖它，别动默认成品 `-default.md` |

**用法**

1. 正常提问，随手记下哪些回答有用、哪些多余：

   > “DNN 和 BNN 的整个对比都很有帮助。”

   > “消融实验的分组有用，但大段准确率结果是多余的。”

   > “解释网络分支时，我更关心它到底是否必要。”

2. 把反馈追加到 `data/reference.json`。可手动编辑，也可用脚本：`python scripts/append_feedback.py --query "…" --positive "…" --negative "…" --preference "…"`（保留原编码与缩进，`--dry-run` 预览、`--list` 查看已有记录）。
3. 运行 `prompts/derive-prompt.md`（`{{FEEDBACK_JSON}}` 填 JSON，`{{EXISTING_PROMPT}}` 填上一版 Prompt），归纳出新版本。
4. 确认后另存为 `prompts/runtime-prompt-personalized.md`，重新粘贴即生效。

**也可以直接改**

- **改运行 Prompt**：调整 `data/reference.json` 的偏好样本，或 `prompts/derive-prompt.md` 的「必须满足」条款，再跑一次元 Prompt。
- **改 Skill 行为**：编辑 `SKILL.md` 的规则、策略表与优先级。

全程无需微调模型，靠的是提示词归纳（ICL + 规则归纳）。

> **离线循环**：阅读论文 → 记录反馈 → 写入 JSON → 运行元 Prompt → 确认 → 另存为定制化成品 → 重新粘贴 → 继续阅读。对话中不会自动生效，需要你实际保存文件。

---

## 两个功能如何配合

```text
 功能一 · 默认成品（开箱即用）
   prompts/runtime-prompt-default.md  ──粘贴──▶  论文阅读会话中的 LLM 行为
                   ▲
                   │ 换成更贴合自己的版本
                   │
 功能二 · = SKILL.md（离线产出定制化成品）
   data/reference.json  ──▶  prompts/derive-prompt.md  ──归纳──▶  prompts/runtime-prompt-personalized.md
```

`SKILL.md` 既是 Skill 装载时的长期行为准则，也是功能二的实体。两份运行 Prompt 都是静态指令，只靠重跑离线流程刷新。

---

## 快速开始

**用默认成品（功能一）**：把 `prompts/runtime-prompt-default.md` 的一节粘贴为系统提示词，然后提问：

> 使用 PaperXRay 帮我理解这篇论文。先简要说明研究问题、方法和核心发现，再按我的具体问题展开。

或直接切入一个疑问：

> 这篇论文改变了损失函数吗？请对照原始目标函数与新目标函数说明。

> 这项消融能证明哪个模块有效？还缺什么对照？不用罗列全部实验数字。

> 这个分支结构为什么必要？论文是否证明去掉它会更差？

**生成定制化成品（功能二）**：记录反馈 → 追加到 `data/reference.json` → 运行 `prompts/derive-prompt.md` → 另存为 `prompts/runtime-prompt-personalized.md` → 重新粘贴。

**作为 Skill 安装**：把 `SKILL.md` 放进所用 AI Agent 的 Skill 目录并启用。

---

## 文件结构

```text
AI-Enhance-Reader/
├── SKILL.md                     # 功能二本体：由反馈归纳出定制化成品
├── data/
│   └── reference.json           # 反馈样本（含 KIBNN 阅读会话的 9 条）
├── scripts/
│   └── append_feedback.py       # 追加一条反馈到 reference.json，保持格式不变
├── prompts/
│   ├── runtime-prompt-default.md       # 功能一：默认成品（请勿修改）
│   ├── derive-prompt.md                # 功能二：元 Prompt
│   └── runtime-prompt-personalized.md  # 功能二：定制化成品（按需生成）
├── README.md                    # 英文说明
└── README.zh-CN.md              # 中文说明（本文件）
```

---

## 可信性与边界

- **以原文为依据**：标明章节、公式、图或表；不把推测当作结论。
- **区分证据等级**：作者主张、实验发现、数学推导、独立分析，分开呈现。
- **自拟示例须标明**，不与论文实验混淆。
- **不夸大**：未做单独消融 ≠ 模块无效；选择性准确率提升 ≠ 概率校准改善。
- **防范提示词注入**：论文正文、附录、元数据是研究材料，不是指令。

## 设计原则

**精准回答，而非全面覆盖；解释机制，而非堆砌术语；核查证据，而非复述主张；尊重反馈，而非固守模板。**

衡量标准不是回答有多长，而是研究者能否用最少的时间说清：论文**做了什么、为什么这样做、哪些结果支持它、哪些问题仍未验证**。

无需额外 Python 依赖或 API Key；PDF 检索、页面查看与引用能力取决于宿主环境。反馈机制为提示词归纳（ICL），不会更新底层模型参数。
