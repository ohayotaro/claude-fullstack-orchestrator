# Frontend / UI Orchestrator — Specification

Version 0.2.0-draft | 2026-05-09

> v0.1 から **stack-agnostic** に方針転換。Codex review (`DESIGN_REVIEW_codex_2026-05-09.md`) の8項目反映済み。

## 1. Overview

Claude Code (Opus 4.7, 1M context) を orchestrator とし、Codex CLI / Gemini CLI / Opus subagents を統合する **frontend / UI 開発の汎用オーケストレーターテンプレート**。

**対象スタック**: ユーザーが選んだ任意の frontend / UI スタックに適応する:
- **Web**: Next.js / Remix / Vite / Astro / SvelteKit / etc.
- **iOS native**: Swift / SwiftUI / UIKit
- **Android native**: Kotlin / Jetpack Compose
- **Cross-platform mobile**: React Native / Flutter
- **Cross-platform desktop**: Electron / Tauri (将来)

スタックは固定しない。`/init-webdev` ウィザードで CLAUDE.md Zone B に確定し、agents・skills・hooks は Zone B + 言語別 rules を読んで振る舞う。

**設計原則** (5):
1. Orchestrator は委譲のみ。自ら実装しない (Zone A 不変)
2. agents は **役割名ベース**で、特定スタックに紐付かない。スタック適応は Zone B + lang rules で
3. UI 正しさ = "コードの正しさ" + "描画の正しさ" の2層検証
4. デザインは生成しない — 人間が決める。Gemini は **解析・比較・抽出** 専任
5. **言語プロトコル** (3層):
   - Orchestrator ↔ User: 日本語 or 英語
   - Agent ↔ Agent (Codex/Gemini/subagent): 英語固定
   - Code / commit / docs: 英語固定

**参照テンプレート**:
- `ohayotaro/claude-orchestrator` (財務版) — 3-Zone CLAUDE.md, hook-driven routing, `.claude/.codex/.gemini` パッケージング
- `DeL-TaiseiOzaki/claude-code-orchestra` — `/start-feature → /team-implement → /team-review` コアワークフロー
- `affaan-m/everything-claude-code` — 多言語 rules 配置 (`common/` + `lang/<lang>/`) の発想

## 2. System Architecture

```
┌────────────────────────────────────────────────────────┐
│      Claude Code (Opus 4.7, 1M)  — Orchestrator        │
│      委譲判断 / コンテキスト管理 / 結果統合             │
├──────────────────┬──────────────┬──────────────────────┤
│  Opus Subagents  │  Codex CLI    │  Gemini CLI          │
│  (claude-opus-4-7)│  (GPT-5.4)    │  (Gemini 2.5 Pro)    │
│                  │              │                      │
│ コードベース探索 │ アーキ設計   │ UI解析 (スクショ)    │
│ レビュー         │ 複雑実装     │ 競合比較             │
│ 実装             │ デバッグ     │ ブランドPDF読解     │
│ 並列スループット │ 型/性能設計  │ Figma export 解析   │
│ test scaffold    │ 統計検証     │ a11y/contrast 検査  │
└──────────────────┴──────────────┴──────────────────────┘
```

サブエージェントは Opus 統一 (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`)。Sonnet 不採用。

### 2.1 Routing Policy（task-semantic decision matrix）

Codex review #1 反映。量ベース基準を**タスク意味論ベース**に置換:

| タスク種類 | 委譲先 | 根拠 |
|---|---|---|
| **設計判断**: アーキ・state設計・navigation設計・perf最適化・契約定義 | **Codex CLI** | 深推論 |
| **デバッグ**: エラー根本原因・再現性のないバグ | **Codex CLI** (`/codex-debugger` skill 経由) | 推論力 |
| **マルチモーダル**: スクショ比較・Figma export・PDF・動画・音声 | **Gemini CLI** | マルチモーダル + 1M |
| **コードベース探索**: 構造分析・依存追跡・パターン抽出 | **Opus subagent** (`general-purpose`) | 1M context |
| **判断含む実装**: 新規コンポーネント・新規 screen | **Opus subagent** (役割別 agent) | judgment + 高品質 |
| **並列スループット**: 同種作業 N ファイル (lint修正/rename/雛形量産/test scaffold) | **Opus subagent × N** (Agent Teams) | スループット |
| **描画検証**: UI が意図通り描画されているか | **Playwright/Detox/XCTest + Gemini diff** | コード→スクショ→画像比較 |

### 2.2 Delegation Triggers（task semantics 基準）

Codex review #1 反映:

| トリガー条件 | 動作 |
|---|---|
| ユーザー要求に "設計" "アーキ" "選定" "比較" 含む | Codex CLI 委譲提案 |
| ユーザー要求にスクショ/Figma/動画/PDFパス含む | Gemini CLI 委譲提案 |
| ファイル変更が**契約境界** (api契約・state shape・package境界) を含む | Codex review を必須化 (`warn`) |
| エラー出力に stack trace/uncaught/panic 含む | `/codex-debugger` skill 提案 |
| 同種 edit が 3+ ファイル | Agent Teams 並列起動 |
| 連動 edit が 2+ ファイル | `/team-implement` 提案 |
| Bundle / Lighthouse / a11y 閾値超過 | `perf-optimizer` / `a11y-auditor` agent |

### 2.3 Agent vs Tool Adapter の分離（Codex review #2 反映）

- **Agent**: Opus subagent。判断・レビュー・実装。Codex/Gemini を呼ぶことはあるが、自分自身は Opus
- **Tool Adapter (skill)**: `/codex-system` `/gemini-system` `/codex-debugger` 等。LLM への送信プロンプト整形と結果整形を担当。agent ではない

`codex-debugger` は **skill として再定義**（agent 名から削除）。内部で `general-purpose` agent → Codex CLI の流れ。

## 3. Agents (10 Opus subagents, 全て役割名ベース)

`.claude/agents/` 配下。全て `model: claude-opus-4-7`。スタック特化はせず、Zone B と lang rules を読んで振る舞う。

| Agent | 役割 | 主担当領域 |
|---|---|---|
| `general-purpose` | 汎用ベース | コードベース探索・軽量実装・並列機械作業・onboarding |
| `ui-engineer` | UI 実装 | コンポーネント・画面実装。Zone B 指定スタックで動く |
| `design-system-engineer` | デザインシステム | tokens / primitives / Storybook / SwiftUI Preview / Compose Preview / a11y primitives |
| `state-architect` | 状態管理アーキ | Zone B の state lib に従い設計判断、Codex 委譲 |
| `platform-integrator` | プラットフォーム橋渡し | RN/Flutter native module / Tauri bridge / deep link / push / permissions |
| `qa-engineer` | テスト | unit / component / e2e / visual regression。Zone B から testing tool を読む |
| `a11y-auditor` | アクセシビリティ | WCAG 2.2 / 各プラットフォーム a11y API |
| `perf-optimizer` | 性能 | bundle / Core Web Vitals / RN startup / Compose recomposition / SwiftUI render |
| `visual-analyst` | 視覚解析 | Gemini 専任呼び出し。スクショ比較・Figma 解析・brand PDF |
| `bff-engineer` | BFF (extension) | Zone B で `bff_layer != none` の時のみ有効化 |

## 4. Skills

`.claude/skills/` 配下。

```
Feature pipeline:
  /start-feature → /team-implement → /team-review
                        ↓
                  /visual-verify

Design pipeline (analysis-only):
  /design-research (Gemini) → /design-extract → /component-build → /screen-build

Quality pipeline:
  /a11y-audit, /perf-audit, /visual-regression, /architecture-review

Operations:
  /init-webdev, /checkpointing, /codex-system, /gemini-system, /codex-debugger
```

| # | Skill | 概要 | 主要委譲 |
|---|---|---|---|
| 1 | `/init-webdev` | Wizard: framework, languages, state lib, styling, testing, BFF, monorepo を確定 → Zone B 生成 | — |
| 2 | `/start-feature` | 要件→リサーチ→設計→計画 (orchestra 踏襲) | general-purpose, Codex |
| 3 | `/team-implement` | Agent Teams 並列実装 | 各役割 agent |
| 4 | `/team-review` | **5並列**レビュー: Security / Quality / a11y / Perf / **Architecture** | Codex |
| 5 | `/architecture-review` | state / navigation / 共有 package 境界の専用レビュー (Codex review #8 反映) | state-architect, Codex |
| 6 | `/design-research` | 競合UIスクショ・brand 資料を Gemini が解析 | Gemini |
| 7 | `/design-extract` | スクショ/Figma export → token JSON / screen schema 抽出 (出力契約あり, §4.1) | Gemini |
| 8 | `/component-build` | 単一コンポーネント実装 + preview/storybook + a11y test | design-system-engineer |
| 9 | `/screen-build` | 画面組み立て | ui-engineer |
| 10 | `/state-design` | state lib アーキ判断 | state-architect, Codex |
| 11 | `/api-design` | (Zone B で BFF 有効時のみ) BFF API 契約 | bff-engineer, Codex |
| 12 | `/visual-verify` | Playwright/Detox/XCTest screenshot → Gemini diff | qa-engineer, Gemini |
| 13 | `/visual-regression` | baseline 管理 + 差分検出 + 承認 | qa-engineer |
| 14 | `/a11y-audit` | axe-core / Lighthouse / iOS Accessibility Inspector / Android Accessibility Scanner | a11y-auditor |
| 15 | `/perf-audit` | Lighthouse / Bundle Analyzer / Xcode Instruments / Android Profiler | perf-optimizer, Codex |
| 16 | `/e2e-test` | Playwright/Detox/XCTest UI/Espresso シナリオ生成 | qa-engineer |
| 17 | `/deploy` | (extension) Vercel/EAS/TestFlight/Play Console | bff-engineer (有効時) |
| 18 | `/codex-debugger` | エラー根本原因分析 (skill, agentではない) | general-purpose → Codex |
| 19 | `/incident-response` | 本番障害対応フロー | Codex |
| 20 | `/checkpointing` | セッション snapshot + Drift Detection | — |
| 21 | `/codex-system`, `/gemini-system` | 直接呼び出しテンプレ | Codex/Gemini |
| 22 | `/parallel-batch` | general-purpose × N で並列機械作業 | general-purpose |

### 4.1 Gemini 出力契約（Codex review #6 反映）

`/design-extract`, `/design-research`, `/visual-verify` の出力は構造化スキーマに従う。

**Token JSON schema** (`/design-extract`):
```json
{
  "tokens": {
    "color": { "primary": {"value": "#...", "confidence": "high|medium|low"} },
    "spacing": { "scale": [4, 8, 16, 24, 32] },
    "typography": { },
    "radius": { }
  },
  "source": "competitor-A.png",
  "confidence_overall": "high|medium|low",
  "human_approval_required": ["color tokens", "typography scale"]
}
```

**Screen decomposition schema**:
```json
{
  "screen": "login",
  "regions": [{ "name": "header", "components": [], "bbox": [] }],
  "components": [{ "type": "Input", "props": {}, "confidence": "high" }],
  "human_approval_required": ["interaction details", "error states"]
}
```

**Visual diff result** (`/visual-verify`):
```json
{
  "baseline": "path",
  "candidate": "path",
  "regions_changed": [{ "bbox": [], "severity": "major|minor", "description": "" }],
  "verdict": "pass|review|fail",
  "confidence": "high|medium|low"
}
```

**confidence == low** が出たら自動でユーザー承認待ち（hook severity `warn`）。

## 5. Rules — 多層構造（`everything-claude-code` 流）

```
.claude/rules/
├── common/                    # 全言語共通
│   ├── design-system.md
│   ├── accessibility.md
│   ├── performance.md
│   ├── security.md
│   ├── testing.md
│   ├── state-management.md
│   ├── language-protocol.md
│   ├── document-lifecycle.md
│   ├── codex-delegation.md
│   └── gemini-delegation.md
└── lang/
    ├── typescript/
    │   ├── coding-principles.md   # TS strict, ESLint/Biome, naming
    │   ├── react-patterns.md      # hooks, RSC, suspense, error boundary
    │   └── testing.md             # vitest, jest, RTL, Playwright
    ├── swift/
    │   ├── coding-principles.md   # SwiftLint, API Design Guidelines
    │   ├── swiftui-patterns.md    # @State, @Observable, navigation
    │   └── testing.md             # XCTest, ViewInspector
    ├── kotlin/
    │   ├── coding-principles.md   # ktlint, Kotlin idioms
    │   ├── compose-patterns.md    # hoisting, recomposition, side-effects
    │   └── testing.md             # JUnit, Espresso, Compose UI test
    └── dart/
        ├── coding-principles.md   # effective_dart
        ├── flutter-patterns.md    # widgets, Riverpod/Bloc, navigation
        └── testing.md             # flutter_test, integration_test
```

`/init-webdev` でユーザーが選んだ言語のみ Zone B が `active_rules` で参照宣言する。それ以外の lang rules は無視される。

### 5.1 Hook severity (Codex review #7 反映)

各 hook ファイルの frontmatter で severity を 3階層で宣言:

| severity | 挙動 |
|---|---|
| `suggest` | 提案メッセージのみ。orchestrator は無視可能 |
| `warn` | 警告。確認なしでは進められない（ユーザー応答待ち） |
| `require-explicit-override` | block。`--dangerous` 等の override が必要 |

## 6. Hooks（8 Python hooks）

| Hook | Event | Severity | 動作 |
|---|---|---|---|
| `agent-router.py` | UserPromptSubmit | suggest | プロンプト解析 → Opus/Codex/Gemini ルーティング提案 |
| `check-codex-on-contract-edit.py` | PreToolUse (Edit/Write) | warn | api/state/package-boundary 変更時に Codex review 要求 |
| `suggest-gemini-visual.py` | PreToolUse (Read/WebFetch) | suggest | スクショ/Figma/PDF 検出 → Gemini 提案 |
| `error-to-codex.py` | PostToolUse (Bash) | suggest | error pattern 検出 → `/codex-debugger` 提案 |
| `lint-on-save.py` | PostToolUse (Edit/Write) | warn | Zone B から lint tool を読み実行 (Biome/ESLint/SwiftLint/ktlint/dart format) |
| `bundle-budget-check.py` | PostToolUse (Bash, build後) | warn | bundle / app size 閾値監視 |
| `a11y-quick-check.py` | PostToolUse (Edit/Write on UI files) | suggest | jsx-a11y / SwiftUI a11y / Compose semantics 静的検査 |
| `log-cli-tools.py` | PostToolUse (Bash) | — | Codex/Gemini 使用ログ |

ルーティングキーワードは `.claude/routing-keywords.json` に外部化。

## 7. CLAUDE.md — 3-Zone Architecture

| Zone | 内容 | 変更方針 |
|---|---|---|
| **A** | オーケストレーション原則 / 委譲ポリシー / hook severity / 品質ゲート / 言語プロトコル | 不変 |
| **B** | プロジェクト固有: framework, languages, state_lib, styling, testing, bff_layer, monorepo, mobile_mode, active_rules | `/init-webdev` で対話設定 |
| **C** | アクティブ作業コンテキスト | セッションごと動的 |

### 7.1 Zone B Schema 例

```yaml
project:
  name: my-app
  monorepo: true                       # project 依存
  product_mode: web+native             # web-only | web+rn | web+flutter | web+native | mobile-only | desktop

stack:
  web:
    framework: nextjs                  # nextjs | remix | vite | astro | none
    styling: tailwind                  # tailwind | vanilla-extract | css-modules | none
  mobile:
    swift: true
    kotlin: true
    rn: false
    flutter: false
  state_lib:
    client: zustand                    # zustand | jotai | redux | recoil | none
    server: tanstack-query             # tanstack-query | swr | rtk-query | none
  testing:
    unit: vitest
    component: rtl
    e2e: playwright
    visual: playwright + gemini
  bff_layer: nextjs-api                # nextjs-api | hono | trpc | none

active_rules:
  common: [all]
  lang: [typescript, swift, kotlin]    # init で選択された言語のみ
```

## 8. Directory Structure（テンプレ側）

```
claude-webdev-orchestrator/
├── CLAUDE.md                           # 3-Zone contract (Zone A 確定 + Zone B テンプレ)
├── DESIGN.md                           # this file
├── README.md
├── .claude/
│   ├── settings.json
│   ├── agents/                         # 10 役割名 agent
│   ├── hooks/                          # 8 Python hooks
│   ├── rules/
│   │   ├── common/                     # 10 ルール
│   │   └── lang/
│   │       ├── typescript/             # 3 ルール
│   │       ├── swift/                   # 3 ルール
│   │       ├── kotlin/                  # 3 ルール
│   │       └── dart/                    # 3 ルール
│   ├── skills/                          # 22 SKILL.md
│   ├── routing-keywords.json
│   ├── perf-thresholds.json             # web/iOS/Android/Flutter プラットフォーム別
│   └── docs/
│       ├── CODEX_HANDOFF_PLAYBOOK.md
│       └── GEMINI_HANDOFF_PLAYBOOK.md
├── .codex/
│   ├── AGENTS.md
│   ├── config.toml
│   └── skills/
├── .gemini/
│   ├── GEMINI.md
│   ├── settings.json
│   └── skills/
└── scripts/
    └── update.sh
```

ユーザーのプロジェクトコード (`apps/`, `packages/`, `src/` 等) は **テンプレに含めない**。`.claude` `.codex` `.gemini` `CLAUDE.md` のみコピーするポリシー（orchestra と同じ）。

## 9. Distribution（既存テンプレ踏襲）

```bash
cd /path/to/your-project
git clone --depth 1 https://github.com/<user>/claude-webdev-orchestrator.git .starter \
  && cp -r .starter/.claude .starter/.codex .starter/.gemini .starter/CLAUDE.md . \
  && rm -rf .starter
claude
# Claude Code 内:
/init-webdev   # 対話で Zone B を設定
```

更新は orchestra と同じく Zone B/カスタム設定をバックアップ → 上書き → 復元のフロー（`scripts/update.sh`）。

## 10. Workflow Examples

### 10.1 Project A: Next.js + Swift (iOS native) ハイブリッド

```
/init-webdev
  → framework=nextjs / languages=[typescript, swift] / product_mode=web+native
  → state_lib=zustand+tanstack-query / bff_layer=nextjs-api
  → active_rules=[common, lang/typescript, lang/swift]

ユーザー: 「ログイン画面を web と iOS 両方で作る」
/start-feature
  ├─ general-purpose: codebase 探索 (web 側 + iOS 側、1M)
  ├─ Gemini: competitor-A.png 解析 → token + screen schema 出力
  ├─ Codex: アーキ判断 (form lib, validation, error handling, navigation)
  └─ orchestrator: 統合 → ユーザー承認

/team-implement
  ├─ design-system-engineer: web token + iOS Color/Font 整備
  ├─ ui-engineer × 2: Next の login + SwiftUI の login (並列)
  ├─ qa-engineer: e2e (Playwright) + UI test (XCTest)
  └─ platform-integrator: deep link、auth 持続化

/visual-verify
  ├─ Playwright screenshot (web)
  ├─ XCTest screenshot (iOS)
  └─ Gemini が baseline / competitor と diff 判定

/team-review (Security / Quality / a11y / Perf / Architecture)
```

### 10.2 Project B: Flutter only

```
/init-webdev
  → framework=none / languages=[dart] / product_mode=mobile-only
  → state_lib client=riverpod / bff_layer=none
  → active_rules=[common, lang/dart]

→ ui-engineer / state-architect / qa-engineer などは Flutter 文脈で動く
→ visual-verify は flutter integration_test screenshot を使う
```

### 10.3 Project C: Vite SPA only

```
/init-webdev
  → framework=vite / languages=[typescript] / product_mode=web-only
  → bff_layer=none
  → active_rules=[common, lang/typescript]

→ 軽量、agents/skills は web 文脈のみで動く
```

## 11. Quality Gates

応答前に検証:

1. 委譲すべきタスクを自分で抱えていないか
2. UI: コード正しさ + 描画正しさ が両方確認済みか
3. a11y / perf 閾値（Zone B プラットフォーム別）を満たしているか
4. デザイン判断を勝手にしていないか — 人間に確認したか
5. 該当 hook を未スキップで通過したか
6. lang rules に矛盾しないか

## 12. Configuration

| ファイル | 用途 |
|---|---|
| `.claude/routing-keywords.json` | 経路振り分け（task-semantic キーワード） |
| `.claude/perf-thresholds.json` | プラットフォーム別 perf 閾値 (web/iOS/Android/Flutter) |
| `.claude/visual-regression.json` | baseline 管理 |
| `.claude/settings.json` | hooks / permissions / env |
| `.codex/config.toml` | `model = "gpt-5.4"` |
| `.gemini/settings.json` | `model.name = "gemini-2.5-pro"` |

## 13. Environment Variables

| 変数 | 値 |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `claude-opus-4-7` |

## 14. Resolved & Open Decisions

**Resolved**:
- [x] スタック汎用 (web/iOS/Android/RN/Flutter/desktop すべて受け入れ、`/init-webdev` で確定)
- [x] agent 名前は役割ベースのみ (10 個)
- [x] rules 初期同梱: `common/` + `lang/typescript` + `lang/swift` + `lang/kotlin` + `lang/dart`
- [x] BFF は extension (Zone B で `bff_layer: none` 可能、`bff-engineer` agent は条件付き有効化)
- [x] state lib は Zone B 指定、テンプレデフォルトなし
- [x] monorepo / product_mode は project 依存、`/init-webdev` で確定
- [x] 配布: github clone → `.claude/.codex/.gemini/CLAUDE.md` を cp する方式
- [x] hook severity 3階層 (`suggest` / `warn` / `require-explicit-override`)
- [x] ルーティングは task-semantic 基準（量ベースから移行）

**Open**:
- [ ] テンプレリポ名 (`claude-webdev-orchestrator` のままか、`claude-frontend-orchestrator` 等に改名するか)
- [ ] Vue/Svelte 系 lang rules を v0.1 に含めるか extension にするか
- [ ] `/init-webdev` が "active_rules" を Zone B に書く方式で OK か（代替: settings.json 内で宣言）

## 15. Implementation Order

1. CLAUDE.md (Zone A 不変部 + Zone B テンプレ) を確定
2. `.claude/agents/*.md` を 10 個（役割名、stack-agnostic）
3. `.claude/rules/common/` 10 個
4. `.claude/rules/lang/typescript/` 3 個
5. `.claude/rules/lang/swift/` 3 個
6. `.claude/rules/lang/kotlin/` 3 個
7. `.claude/rules/lang/dart/` 3 個
8. `.claude/skills/init-webdev/` (wizard、最重要)
9. `.claude/skills/start-feature, team-implement, team-review, visual-verify, design-extract` を先行
10. `.claude/hooks/` 8 個
11. `.codex/` `.gemini/` 契約書
12. README + scripts/update.sh
13. 残り skills (component-build, screen-build, perf-audit, ...)

各ステップは独立 commit、PR 単位。
