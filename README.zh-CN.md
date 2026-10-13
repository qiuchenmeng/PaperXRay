# PaperXRay 
## AI Assistant Reference Reading (SARR)

[insert a image to show the process]
> **用最少的必要信息，获得最充分的论文理解。**

PaperXRay 是一个面向科研人员的 **AI Assistant Reference Reading Skill**。它不做最长的论文总结，也不机械地压缩回答，而是围绕研究者的**当前疑问**给出「最小充分解释」。

它能够根据研究者的关注偏好/提问的内容和对回答的反馈，迭代更加适合研究者的论文阅读prompt,实现复利，让你的模型越来越懂你在问什么，你的关注点是什么

## Why PaperXRay?
 - 你是否也觉得 LLM 的回答过于冗长？
 - 你是否也觉得冗长回答中的核心信息有限，却充斥着大量冗余内容？
 - 你是否也担心冗余的信息会污染你的上下文信息？
 - 你是否也曾因为回答过长，而失去了认真阅读的耐心？
 
如果你也有这些困扰，不妨试试 PaperXRay！我们致力于让模型以最精炼的表达，传递最核心的信息，帮助你用最少的必要信息，实现最充分的论文理解。
## Quick Start

| 内容 | 面向 | 成品 |
| --- | --- | --- |
| Prompt | AI小白 | `prompts/default-prompt.md` · AI-Assistant-Reference-Reading prompt，**Just Paste it to your LLM** |
| SKILL  | 开发者 | `prompts/runtime-prompt-personalized.md` · 根据你向AI提问的问题生成的你的定制化 AI-Assistant-Reference-Reading prompt |

---

## SI-Assistant-Reference-Reading Prompt

`prompts/default-prompt.md`中包含`# 中文版` 与 `# English version` 两种语言，粘贴即用。


**想要更贴合自己的prompt？download our skill and generate the personlized prompt**

---

## Personalized SI-Assistant-Reference-Reader Prompt（产出你的定制化prompt）

 `SKILL.md` 把你真实的阅读反馈——哪些回答有用、哪些多余、适用于什么情形——经 元-Prompt 归纳成一份 **帮助大模型理解你的阅读偏好的Prompt**。

**安装**

git clone https://github.com/qiuchenmeng/PaperXRay.git

**交互用法**

1. 用 `@paperxray <论文.pdf> <你的问题>` 开始。Skill 会优先读取 `prompts/runtime-prompt-personalized.md`；如果该文件不存在，则自动使用 `prompts/default-prompt.md` 中的 Prompt 回答问题。
2. 继续提问即可；你可以自然地反馈上一条回答中哪些内容有帮助、哪些多余或以后希望如何调整。也可以在同一条消息里先反馈、再问新问题。
3. 当你明确评价回答或表达可复用偏好时，Skill 会自动将简洁记录追加到 `data/reference.json`：对应问题、明确有帮助/冗余的内容、适用范围和归纳出的偏好。普通追问和单纯致谢不会被误记为反馈；不会保存整篇论文或完整回答。
4. 归纳偏好并生成新版本。当你的输入表达归纳阅读偏好、整理反馈或生成新版 Prompt 的意思时，Skill 会先写入尚未保存的反馈，再按 `prompts/derive-prompt.md` 归纳，将定制化 Prompt 更新到 `prompts/runtime-prompt-personalized.md`。无需结束会话；“归纳论文方法”等针对论文内容的请求仍作为阅读问题处理。
5. 复用：`@paperxray <论文.pdf> <personalized prompt + 你的问题>` 开始，可以直接提供定制 Prompt 的正文或文件路径，Skill 会按它回答问题；不显式提供时，也会自动加载已保存的定制版。保存后的新版同样用于当前 Skill 会话的后续阅读回答。

以上文件路径均相对于 Skill 目录。运行需要宿主加载 Skill 并提供文件读写和 PDF 访问能力；读写失败时会说明未保存内容。默认 Prompt 内容保持不变。

**进阶用法**

- 个性化修改 Prompt：调整 `data/reference.json` 的偏好样本，或 `prompts/derive-prompt.md` 的「必须满足」条款，再跑一次元 Prompt。

**互动闭环**：`@paperxray` 读取论文并回答 → 读者追问、反馈 → Skill 自动整理反馈到 JSON → 读者请求归纳偏好时更新定制 Prompt → 当前或下一次阅读会话复用新版。

---

## 两个功能如何配合

```text
 **prompt**
   prompts/default-prompt.md  ──粘贴──▶  论文阅读会话中的 LLM 行为
                   ▲
                   │ 换成更贴合自己的版本
                   │
 **SKILL**（交互反馈并生成定制化成品）
   data/reference.json  ──▶  prompts/derive-prompt.md  ──归纳──▶  prompts/runtime-prompt-personalized.md
```
---

## 快速开始

**prompt**：把 `prompts/default-prompt.md` 的一节粘贴为系统提示词，然后提问：

> 使用 PaperXRay 帮我理解这篇论文。先简要说明研究问题、方法和核心发现，再按我的具体问题展开。

或直接切入一个疑问：

> 这篇论文改变了损失函数吗？请对照原始目标函数与新目标函数说明。

> 这项消融能证明哪个模块有效？还缺什么对照？不用罗列全部实验数字。

> 这个分支结构为什么必要？论文是否证明去掉它会更差？

**生成定制化成品（功能二）**：阅读时用 `@paperxray <论文.pdf> <问题>` 开始，继续提问并自然反馈；随时要求归纳偏好并生成新版。反馈自动追加到 `data/reference.json`，新版保存到 `prompts/runtime-prompt-personalized.md`，默认成品不变。

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
│   ├── default-prompt.md       # 功能一：默认成品（请勿修改）
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
