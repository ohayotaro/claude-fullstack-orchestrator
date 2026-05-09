# Fullstack Orchestrator — Specification

Version 0.3.0-draft | 2026-05-09

> v0.2 (frontend-only) からスコープを **fullstack** に拡張。Codex の v0.2 レビュー (`DESIGN_DECISIONS_codex_2026-05-09.md`) で確定した 4 決定を反映:
> 1. backend specialists 追加 (5 agents, 7 skills, Zone B 拡張)
> 2. リポジトリ名は **`claude-fullstack-orchestrator`** に改名 (後に family naming 統一のため `claude-fullstack` に簡略化)
> 3. Vue/Svelte は **extension** (将来の `rules/framework/{vue,svelte}/`)
> 4. `active_rules` は **CLAUDE.md Zone B** に宣言

## 1. Overview

Claude Code (Opus 4.7, 1M context) を orchestrator とし、Codex CLI / Gemini CLI / Opus subagents を統合する **fullstack 開発の汎用オーケストレーターテンプレート**。

**対象スタック**: ユーザーが選んだ任意のスタックに適応する:

- **Web**: Next.js / Remix / Vite / Astro / SvelteKit / etc.
- **iOS native**: Swift / SwiftUI / UIKit
- **Android native**: Kotlin / Jetpack Compose
- **Cross-platform mobile**: React Native / Flutter
- **Cross-platform desktop** (将来): Electron / Tauri
- **Backend**: Python (FastAPI/Django) / Node-TypeScript (Hono/Fastify/NestJS) (v0.1 同梱)。Go/Rust/Java/Kotlin-Spring は extension
- **API style**: REST / GraphQL / RPC / mixed
- **Data layer**: 任意の SQL/NoSQL + ORM/driver + migration tool
- **Infra**: 任意の deploy target / cache / message broker / blob storage / observability stack

スタックは固定しない。`/init-webdev` + `/backend-init` ウィザードで CLAUDE.md Zone B に確定し、agents・skills・hooks は Zone B + lang rules を読んで振る舞う。

**設計原則** (5):
1. Orchestrator は委譲のみ。自ら実装しない (Zone A 不変)
2. agents は **役割名ベース**で、特定スタックに紐付かない。スタック適応は Zone B + lang rules で
3. UI 正しさ = "コードの正しさ" + "描画の正しさ" の2層検証 / Backend 正しさ = "契約の正しさ" + "観測可能性" の2層検証
4. デザインは生成しない — 人間が決める。Gemini は **解析・比較・抽出** 専任
5. **言語プロトコル** (3層):
   - Orchestrator ↔ User: 日本語 or 英語
   - Agent ↔ Agent (Codex/Gemini/subagent): 英語固定
   - Code / commit / docs: 英語固定

**参照テンプレート**:
- `ohayotaro/claude-finance` (財務版、旧名 `claude-orchestrator`) — 3-Zone CLAUDE.md, hook-driven routing, `.claude/.codex/.gemini` パッケージング
- `DeL-TaiseiOzaki/claude-code-orchestra` — `/start-feature → /team-implement → /team-review` コアワークフロー
- `affaan-m/everything-claude-code` — 多言語 rules 配置 (`common/` + `lang/*` + 将来 `framework/*`)

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
│                  │ DB schema    │ ER図/構成図 解析    │
│                  │ infra設計    │                      │
└──────────────────┴──────────────┴──────────────────────┘
```

サブエージェントは Opus 統一 (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`)。Sonnet 不採用。

### 2.1 Routing Policy（task-semantic decision matrix）

| タスク種類 | 委譲先 | 根拠 |
|---|---|---|
| **設計判断**: アーキ・state設計・navigation・perf最適化・契約定義・DB schema・auth flow・infra topology | **Codex CLI** | 深推論 |
| **デバッグ**: エラー根本原因・再現性のないバグ | **Codex CLI** (`/codex-debugger` / `/incident-backend`) | 推論力 |
| **マルチモーダル**: スクショ比較・Figma export・PDF・動画・ER図・アーキ図 | **Gemini CLI** | マルチモーダル + 1M |
| **コードベース探索**: 構造分析・依存追跡・パターン抽出 | **Opus subagent** (`general-purpose`) | 1M context |
| **判断含む実装**: 新規コンポーネント / 新規 endpoint / 新規 worker | **Opus subagent** (役割別 agent) | judgment + 高品質 |
| **並列スループット**: 同種作業 N ファイル | **Opus subagent × N** (Agent Teams) | スループット |
| **描画検証**: UI が意図通りか | **Playwright/Detox/XCTest + Gemini diff** | コード→スクショ→画像比較 |
| **契約検証**: API/event 契約が破壊変更でないか | **Codex** + contract diff | spec drift 検出 |

### 2.2 Delegation Triggers

| トリガー条件 | 動作 |
|---|---|
| ユーザー要求に "設計" "アーキ" "選定" "比較" "schema" "endpoint" 含む | Codex CLI 委譲提案 |
| ユーザー要求にスクショ/Figma/動画/PDF/ER図パス含む | Gemini CLI 委譲提案 |
| ファイル変更が**契約境界** (api契約/state shape/package境界/DB migration/event schema) を含む | Codex review 必須化 (`warn`) |
| エラー出力に stack trace/uncaught/panic/SIGSEGV 含む | `/codex-debugger` 提案 |
| 本番ログに 5xx スパイク・error rate 増 | `/incident-backend` 提案 |
| 同種 edit が 3+ ファイル | Agent Teams 並列起動 |
| 連動 edit が 2+ ファイル | `/team-implement` 提案 |
| Bundle / Lighthouse / a11y 閾値超過 | `perf-optimizer` / `a11y-auditor` |
| DB migration ファイル新規 | `data-engineer` + Codex review (`warn`) |

### 2.3 Agent vs Tool Adapter の分離

- **Agent**: Opus subagent。判断・レビュー・実装。Codex/Gemini を呼ぶことはあるが本体は Opus
- **Tool Adapter (skill)**: `/codex-system` `/gemini-system` `/codex-debugger` 等。LLM への送信プロンプト整形と結果整形を担当

`codex-debugger` は **skill**（agent ではない）。内部で `general-purpose` agent → Codex CLI の流れ。

## 3. Agents（14 Opus subagents、役割名ベース）

`.claude/agents/` 配下。全て `model: claude-opus-4-7`。Zone B + lang rules を読んで振る舞う。

### Frontend / UI / Mobile (9)

| Agent | 役割 |
|---|---|
| `general-purpose` | 汎用ベース: コードベース探索・軽量実装・並列機械作業・onboarding |
| `ui-engineer` | コンポーネント・画面実装。Zone B 指定スタックで動く |
| `design-system-engineer` | tokens / primitives / Storybook / SwiftUI Preview / Compose Preview / a11y primitives |
| `state-architect` | クライアント側状態管理アーキ。Zone B の state lib に従う |
| `platform-integrator` | RN/Flutter native module / Tauri bridge / deep link / push / permissions |
| `qa-engineer` | unit/component/e2e/visual regression。Zone B の testing tool を使う |
| `a11y-auditor` | WCAG 2.2 / 各プラットフォーム a11y API |
| `perf-optimizer` | bundle / Core Web Vitals / RN startup / Compose recomposition / SwiftUI render |
| `visual-analyst` | Gemini 専任呼び出し: スクショ比較・Figma 解析・brand PDF |

### Backend (5) — Codex 推奨

| Agent | 役割 |
|---|---|
| `api-engineer` | HTTP/gRPC API 設計・実装・契約・handler・validation・service boundary。**`bff-engineer` を吸収**: `backend_scope=bff-only` で BFF mode、`full-backend` で広域 mode |
| `data-engineer` | schema 設計・migration・query パターン・transaction・data access perf |
| `auth-security-engineer` | authn/authz・session/token・secrets・backend security review |
| `infra-engineer` | deployment topology・runtime config・containers・CI/CD・observability・cloud primitives |
| `job-engineer` | background jobs・queues・schedulers・retries・idempotency・async workflow |

> **`bff-engineer` は廃止** — `api-engineer` のモードに統合。`bff_layer` は Zone B に残し、frontend ワークフロー側の関心事として参照される。

## 4. Skills（28 = 21 frontend + 7 backend）

```
Frontend feature pipeline:
  /start-feature → /team-implement → /team-review
                        ↓
                  /visual-verify

Design pipeline (analysis-only):
  /design-research → /design-extract → /component-build → /screen-build

Backend feature pipeline:
  /api-build → /data-design → /auth-design → /team-review
        ↓
  /job-design (任意)

Quality:
  /a11y-audit, /perf-audit, /visual-regression, /architecture-review, /infra-review

Operations:
  /init-webdev, /backend-init, /codex-debugger, /incident-backend, /incident-response,
  /checkpointing, /codex-system, /gemini-system, /parallel-batch
```

### 4.1 Skill catalog

| # | Skill | 概要 | 主要委譲 |
|---|---|---|---|
| 1 | `/init-webdev` | Frontend wizard: framework, languages, state lib, styling, testing, monorepo を確定 → Zone B 生成 | — |
| 2 | `/backend-init` | Backend wizard: scope, runtime, DB, ORM, broker, cache, deploy target, API style → Zone B 拡張 | — |
| 3 | `/start-feature` | 要件→リサーチ→設計→計画 (orchestra 踏襲、frontend/backend どちらでも) | general-purpose, Codex |
| 4 | `/team-implement` | Agent Teams 並列実装 | 各役割 agent |
| 5 | `/team-review` | **5並列**レビュー: Security / Quality / a11y / Perf / **Architecture** | Codex |
| 6 | `/architecture-review` | state / navigation / 共有 package 境界・サービス境界 専用 | state-architect, api-engineer, Codex |
| 7 | `/design-research` | 競合UIスクショ・brand 資料を Gemini が解析 | Gemini |
| 8 | `/design-extract` | スクショ/Figma → token JSON / screen schema 抽出 (出力契約あり, §4.2) | Gemini |
| 9 | `/component-build` | 単一コンポーネント実装 + preview/storybook + a11y test | design-system-engineer |
| 10 | `/screen-build` | 画面組み立て | ui-engineer |
| 11 | `/state-design` | client state lib アーキ判断 | state-architect, Codex |
| 12 | `/api-build` | API endpoint/service の設計→実装 (契約レビュー含む) | api-engineer, Codex |
| 13 | `/data-design` | schema・migration・indexing・access pattern review | data-engineer, Codex |
| 14 | `/auth-design` | authn/authz/session アーキ選定・検証 | auth-security-engineer, Codex |
| 15 | `/infra-review` | deployment/runtime/secret/observability review | infra-engineer, Codex |
| 16 | `/job-design` | queue・worker・retry・schedule design | job-engineer, Codex |
| 17 | `/visual-verify` | Playwright/Detox/XCTest screenshot → Gemini diff | qa-engineer, Gemini |
| 18 | `/visual-regression` | baseline 管理 + 差分検出 + 承認 | qa-engineer |
| 19 | `/a11y-audit` | axe-core / Lighthouse / iOS Accessibility Inspector / Android Accessibility Scanner | a11y-auditor |
| 20 | `/perf-audit` | Lighthouse / Bundle Analyzer / Xcode Instruments / Android Profiler / backend latency | perf-optimizer, Codex |
| 21 | `/e2e-test` | Playwright/Detox/XCTest UI/Espresso シナリオ生成 | qa-engineer |
| 22 | `/deploy` | (extension) Vercel/EAS/TestFlight/Play Console / backend container deploy | infra-engineer |
| 23 | `/codex-debugger` | エラー根本原因分析 (skill, agentではない) | general-purpose → Codex |
| 24 | `/incident-response` | フロントエンド本番障害対応フロー | Codex |
| 25 | `/incident-backend` | backend 本番障害対応 (5xx/データ整合性/queue滞留) | infra-engineer, Codex |
| 26 | `/checkpointing` | セッション snapshot + Drift Detection | — |
| 27 | `/codex-system`, `/gemini-system` | 直接呼び出しテンプレ | Codex/Gemini |
| 28 | `/parallel-batch` | general-purpose × N で並列機械作業 | general-purpose |

### 4.2 Gemini 出力契約

`/design-extract`, `/design-research`, `/visual-verify` の出力は構造化スキーマに従う（v0.2 から継続）。`confidence == low` で自動的にユーザー承認待ち（hook severity `warn`）。

**Token JSON / Screen decomposition / Visual diff** schema は §4.2 v0.2 と同一。詳細は本書または `.gemini/skills/` を参照。

## 5. Rules — 多層構造

```
.claude/rules/
├── common/                       # 全言語・全ロール共通
│   ├── design-system.md
│   ├── accessibility.md
│   ├── performance.md
│   ├── security.md
│   ├── testing.md
│   ├── state-management.md
│   ├── api-contracts.md          # NEW: 契約 (REST/GraphQL/RPC) 共通の不変条件
│   ├── data-modeling.md          # NEW: schema/migration の不変条件
│   ├── observability.md          # NEW: ログ/メトリクス/トレース共通
│   ├── language-protocol.md
│   ├── document-lifecycle.md
│   ├── codex-delegation.md
│   └── gemini-delegation.md
└── lang/
    ├── typescript/               # Frontend TS (React/Next/Vite)
    │   ├── coding-principles.md
    │   ├── react-patterns.md
    │   └── testing.md
    ├── node-typescript/          # NEW: Backend Node TS (Hono/Fastify/NestJS/Express)
    │   ├── coding-principles.md
    │   ├── server-patterns.md    # async, error boundary, middleware
    │   └── testing.md            # vitest/jest + supertest/integration
    ├── python/                   # NEW: Backend Python (FastAPI/Django/Litestar)
    │   ├── coding-principles.md  # ruff, mypy strict, naming
    │   ├── server-patterns.md    # async, dependency injection, ORM patterns
    │   └── testing.md            # pytest, async test
    ├── swift/
    │   ├── coding-principles.md
    │   ├── swiftui-patterns.md
    │   └── testing.md
    ├── kotlin/
    │   ├── coding-principles.md
    │   ├── compose-patterns.md
    │   └── testing.md
    └── dart/
        ├── coding-principles.md
        ├── flutter-patterns.md
        └── testing.md
```

### 5.1 Future extension layout

`Vue/Svelte/Go/Rust/Java/Kotlin-Spring` などは v0.1 では同梱しない。将来:

```
.claude/rules/
├── lang/                         # 言語そのもの
│   ├── go/, rust/, java/, kotlin-spring/    # backend
│   └── ...
└── framework/                    # フレームワーク特化（言語横断/UI 系）
    ├── vue/, svelte/, qwik/, solid/
    ├── nestjs/                   # NestJS 固有 conventions
    └── spring-boot/
```

`/init-webdev` でユーザーが選んだ言語・フレームワークのみ Zone B が `active_rules` で参照宣言する。

### 5.2 Hook severity

| severity | 挙動 |
|---|---|
| `suggest` | 提案メッセージのみ |
| `warn` | 警告。確認なしには進めない |
| `require-explicit-override` | block。`--dangerous` 等の override が必要 |

## 6. Hooks（10 Python hooks）

frontend 8 + backend 2 (NEW):

| Hook | Event | Severity | 動作 |
|---|---|---|---|
| `agent-router.py` | UserPromptSubmit | suggest | プロンプト解析 → Opus/Codex/Gemini ルーティング提案 |
| `check-codex-on-contract-edit.py` | PreToolUse (Edit/Write) | warn | api契約/state shape/package境界/DB migration/event schema 変更時に Codex review 要求 |
| `suggest-gemini-visual.py` | PreToolUse (Read/WebFetch) | suggest | スクショ/Figma/PDF/ER図 検出 → Gemini 提案 |
| `error-to-codex.py` | PostToolUse (Bash) | suggest | error pattern → `/codex-debugger` 提案 |
| `lint-on-save.py` | PostToolUse (Edit/Write) | warn | Zone B から lint tool を読み実行 |
| `bundle-budget-check.py` | PostToolUse (Bash, build後) | warn | bundle / app size 閾値監視 |
| `a11y-quick-check.py` | PostToolUse (Edit/Write on UI files) | suggest | jsx-a11y / SwiftUI a11y / Compose semantics |
| `migration-check.py` | PostToolUse (Edit/Write on migration) | **warn** | NEW: migration の destructive change 検出、Codex review 要求 |
| `secret-scan.py` | PreToolUse (Edit/Write) | **require-explicit-override** | NEW: secret/credentials の hard-coded を検出 → block |
| `log-cli-tools.py` | PostToolUse (Bash) | — | Codex/Gemini 使用ログ |

ルーティングキーワードは `.claude/routing-keywords.json` に外部化。

## 7. CLAUDE.md — 3-Zone Architecture

| Zone | 内容 | 変更方針 |
|---|---|---|
| **A** | オーケストレーション原則 / 委譲ポリシー / hook severity / 品質ゲート / 言語プロトコル | 不変 |
| **B** | プロジェクト固有: stack (frontend + backend) + active_rules | `/init-webdev` + `/backend-init` で対話設定 |
| **C** | アクティブ作業コンテキスト | セッションごと動的 |

### 7.1 Zone B Schema 例（Codex 仕様準拠）

```yaml
project:
  name: my-app
  monorepo: true
  product_mode: web+native+backend     # web-only | mobile-only | web+native | web+rn | web+flutter | backend-only | fullstack | desktop

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
    client: zustand
    server: tanstack-query

backend:
  backend_scope: full-backend          # none | bff-only | full-backend
  backend_languages: [python]          # python | node-typescript | go | rust | java | kotlin-spring
  backend_framework: fastapi           # fastapi | django | hono | fastify | nestjs | ...
  api_style: rest                      # rest | graphql | rpc | mixed
  bff_layer: nextjs-api                # frontend 観点の参照: nextjs-api | hono | trpc | none
  database:
    engine: postgres                   # postgres | mysql | sqlite | dynamodb | mongodb | ...
    orm_or_driver: sqlalchemy
    migration_tool: alembic
  cache: redis                         # none | redis | other
  message_broker: sqs                  # none | sqs | pubsub | kafka | rabbitmq | other
  blob_storage: s3                     # none | s3 | gcs | r2 | other
  auth_mode: oauth2-pkce               # session | jwt | oauth2-pkce | oidc | api-key | custom
  deployment_target: ecs-fargate       # vercel | cloudflare | ecs-fargate | gke | render | fly | k8s | ...
  observability:
    logs: cloudwatch
    metrics: prometheus
    tracing: opentelemetry
  runtime_envs: [local, staging, prod]

testing:
  unit: vitest                         # frontend
  backend_unit: pytest
  component: rtl
  e2e: playwright
  visual: playwright + gemini

active_rules:
  common: [all]
  lang: [typescript, python, swift, kotlin]   # init で選択された言語のみ
  framework: []                                 # v0.1 では空、将来 framework/* が入る
```

## 8. Directory Structure（テンプレ側）

```
claude-fullstack/
├── CLAUDE.md                           # 3-Zone contract
├── DESIGN.md                           # this file
├── README.md
├── .claude/
│   ├── settings.json
│   ├── agents/                         # 14 役割名 agent
│   ├── hooks/                          # 10 Python hooks
│   ├── rules/
│   │   ├── common/                     # 13 ルール
│   │   └── lang/
│   │       ├── typescript/             # 3
│   │       ├── node-typescript/        # 3 (NEW)
│   │       ├── python/                 # 3 (NEW)
│   │       ├── swift/                   # 3
│   │       ├── kotlin/                  # 3
│   │       └── dart/                    # 3
│   ├── skills/                          # 28 SKILL.md
│   ├── routing-keywords.json
│   ├── perf-thresholds.json             # web/iOS/Android/Flutter/backend (latency/RPS)
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

ユーザーのプロジェクトコード (`apps/`, `packages/`, `services/`, `src/` 等) は **テンプレに含めない**。`.claude .codex .gemini CLAUDE.md` のみコピーする (orchestra と同じ)。

## 9. Distribution

```bash
cd /path/to/your-project
git clone --depth 1 https://github.com/ohayotaro/claude-fullstack.git .starter \
  && cp -r .starter/.claude .starter/.codex .starter/.gemini .starter/CLAUDE.md . \
  && rm -rf .starter
claude
# Claude Code 内:
/init-webdev      # frontend Zone B
/backend-init     # backend Zone B (任意, backend_scope != none の時のみ)
```

更新は orchestra と同じく Zone B + カスタム設定をバックアップ → 上書き → 復元（`scripts/update.sh`）。

## 10. Workflow Examples

### 10.1 Project A: Next.js + Swift + FastAPI backend

```
/init-webdev   → framework=nextjs / languages=[typescript, swift] / product_mode=web+native+backend
/backend-init  → scope=full-backend / lang=python / framework=fastapi / db=postgres / api_style=rest
              → active_rules=[common, lang/typescript, lang/swift, lang/python]

ユーザー: 「ログイン機能を web/iOS/backend 全部で作る」
/start-feature
  ├─ general-purpose: codebase 探索 (1M)
  ├─ Gemini: competitor screenshot 解析 → token + screen schema
  ├─ Codex: アーキ判断 (auth flow / token storage / refresh / API contract)
  └─ orchestrator: 統合 → 承認

/team-implement
  ├─ design-system-engineer: token + iOS Color/Font
  ├─ ui-engineer × 2: Next + SwiftUI login screen (並列)
  ├─ api-engineer: /auth/login /auth/refresh endpoint (FastAPI)
  ├─ data-engineer: users table + sessions table migration
  ├─ auth-security-engineer: JWT + refresh token rotation 設計
  ├─ qa-engineer: Playwright + XCTest + pytest
  └─ platform-integrator: deep link, secure storage

/visual-verify (Playwright + XCTest screenshots → Gemini diff)
/team-review (Security / Quality / a11y / Perf / Architecture)
```

### 10.2 Project B: Backend-only Python service

```
/init-webdev   → product_mode=backend-only (frontend skip)
/backend-init  → scope=full-backend / lang=python / framework=fastapi / db=postgres / broker=sqs
              → active_rules=[common, lang/python]

→ frontend agents (ui/design-system/state/visual etc.) 無効化
→ /api-build, /data-design, /job-design, /infra-review が主軸
```

### 10.3 Project C: Vite SPA + Hono BFF

```
/init-webdev   → framework=vite / languages=[typescript] / product_mode=web-only
/backend-init  → scope=bff-only / lang=node-typescript / framework=hono
              → active_rules=[common, lang/typescript, lang/node-typescript]

→ api-engineer は BFF mode で動く
→ data-engineer / job-engineer は disabled
```

## 11. Quality Gates

応答前に検証:

1. 委譲すべきタスクを自分で抱えていないか
2. UI: コード正しさ + 描画正しさ (Zone B 閾値)
3. Backend: 契約安定性 + 観測可能性 (logs/metrics/traces)
4. a11y / perf / security 閾値を満たしているか
5. デザイン判断を勝手にしていないか
6. hook を未スキップで通過したか
7. lang rules に矛盾しないか
8. secret hard-coded していないか (`secret-scan.py`)

## 12. Configuration

| ファイル | 用途 |
|---|---|
| `.claude/routing-keywords.json` | task-semantic ルーティング |
| `.claude/perf-thresholds.json` | web/iOS/Android/Flutter/backend 閾値 |
| `.claude/visual-regression.json` | baseline 管理 |
| `.claude/contract-watch.json` | 契約境界 (api/state/db schema/event) パス指定 |
| `.claude/settings.json` | hooks / permissions / env |
| `.codex/config.toml` | `model = "gpt-5.4"` |
| `.gemini/settings.json` | `model.name = "gemini-2.5-pro"` |

## 13. Environment Variables

| 変数 | 値 |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `claude-opus-4-7` |

## 14. Resolved Decisions (v0.3 時点)

- [x] Stack-agnostic (web/iOS/Android/RN/Flutter/desktop/backend、`/init-webdev` + `/backend-init` で確定)
- [x] Agent 名前は役割ベース (14 個: 9 frontend + 5 backend)
- [x] **Repo name = `claude-fullstack-orchestrator`** (Codex H confidence) — 後に `claude-fullstack` へ簡略化 (sibling `claude-finance` と命名対称)
- [x] Backend scope: api / data / auth-security / infra / job (5 agents、7 skills)
- [x] **bff-engineer は廃止 → api-engineer に吸収** (`backend_scope` で mode 切替)
- [x] Lang rules v0.1 同梱: `common/` + `lang/{typescript, node-typescript, python, swift, kotlin, dart}/` (6 言語)
- [x] Lang rules extension: `go, rust, java, kotlin-spring`
- [x] **Vue/Svelte は extension** (将来 `rules/framework/{vue,svelte}/`、Codex M confidence)
- [x] **active_rules は CLAUDE.md Zone B** に宣言 (Codex H confidence)
- [x] State lib は Zone B 指定、テンプレデフォルトなし
- [x] Distribution: github clone → `.claude .codex .gemini CLAUDE.md` を cp
- [x] Hook severity 3 階層 (`suggest` / `warn` / `require-explicit-override`)
- [x] Routing は task-semantic 基準
- [x] Gemini 出力は構造化 schema + 確信度 + human_approval_required
- [x] 言語プロトコル: orchestrator↔user JP-or-EN / agent↔agent EN / code-docs EN

## 15. Implementation Order

1. CLAUDE.md (Zone A 不変部 + Zone B テンプレ schema)
2. `.claude/agents/*.md` × 14 (役割名、stack-agnostic)
3. `.claude/rules/common/` × 13
4. `.claude/rules/lang/typescript/` × 3
5. `.claude/rules/lang/node-typescript/` × 3 (NEW)
6. `.claude/rules/lang/python/` × 3 (NEW)
7. `.claude/rules/lang/swift/` × 3
8. `.claude/rules/lang/kotlin/` × 3
9. `.claude/rules/lang/dart/` × 3
10. `.claude/skills/init-webdev/` (frontend wizard)
11. `.claude/skills/backend-init/` (backend wizard, NEW)
12. `.claude/skills/start-feature, team-implement, team-review, visual-verify, design-extract, api-build, data-design, auth-design` (コア優先)
13. `.claude/hooks/` × 10 (10 個、`migration-check.py` `secret-scan.py` 含む)
14. `.codex/` `.gemini/` 契約書 (CODEX_HANDOFF_PLAYBOOK.md / GEMINI_HANDOFF_PLAYBOOK.md)
15. README + scripts/update.sh
16. 残り skills (component-build, screen-build, perf-audit, infra-review, job-design, incident-backend, ...)

各ステップは独立 commit、PR 単位。

## 16. Repository Migration

GitHub repo は `claude-webdev-orchestrator` → `claude-fullstack-orchestrator` → `claude-fullstack` の順で段階的に rename された。後者の簡略化は sibling repo `claude-finance` (旧 `claude-orchestrator`) と family naming を揃えるため。GitHub は各 rename 後に旧URL の redirect を維持する。local remote URL は最新URLに更新済み。
