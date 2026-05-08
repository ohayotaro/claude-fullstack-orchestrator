# Codex Review — DESIGN.md v0.1.0-draft

Reviewer: Codex CLI (gpt-5.4) | Date: 2026-05-09 | Sandbox: read-only

## 1. TL;DR
Skeleton is directionally sound: the 3-lane routing, 3-zone contract, and quality-gate framing are strong. The weak points are policy coherence and platform abstraction: web/mobile/shared design are underspecified where implementation choices become irreversible.

## 2. Strengths: what to keep
- **Clear routing split** in §2.1: Codex for architecture/debugging, Gemini for multimodal analysis, Opus agents for throughput is a sensible control plane.
- **Language protocol** in §1 is load-bearing and correct for mixed human/agent workflows. Keep it strict.
- **3-Zone CLAUDE.md** in §7 is the right backbone; `/init-webdev` populating Zone B is a good fit.
- **Quality model** in §10 correctly treats UI as code correctness + rendering correctness.
- **Agent taxonomy** in §3 mostly maps to actual delivery concerns; `design-system-engineer`, `state-architect`, `qa-engineer`, `perf-optimizer` are especially useful.
- **Monorepo-first directory shape** in §8 is reasonable for shared tokens/UI/contracts across web+mobile.

## 3. Gaps / Risks
- **Routing triggers are too heuristic** (§2.2). "3 files read" or "10 lines output" are brittle and will misroute often; task semantics matter more than volume.
- **Agent/tool overlap is blurry** (§2.1, §3, §6). `codex-debugger` is described as "Opus + Codex", while hooks also escalate to Codex. Ownership is unclear.
- **Cross-platform UI abstraction is underdefined** (§3, §8). A shared `packages/ui` for Next + RN + Flutter is not one architecture; RN and Flutter cannot share component code the same way.
- **Platform choice policy conflicts with scope** (§1, §8, §13). Spec says React/Next + React Native/Flutter, but also includes Vite/Remix in §1 and mixed styling options in §8 without platform-specific guardrails.
- **BFF is simultaneously out-of-scope and first-class** (§1, §3, §4, §13). That is internally inconsistent.
- **Design analysis pipeline lacks artifact contracts** (§4). Gemini outputs are mentioned, but no schema for tokens, layout annotations, confidence thresholds, or handoff format.
- **Hooks assume enforcement power they may not have** (§6). "Recommend" vs "block" behavior is not specified, which matters for policy reliability.
- **Review coverage is incomplete** (§4). `/team-review` says Security/Quality/a11y/Perf, but mobile-specific review and architecture/regression review are absent.

## 4. Concrete suggestions
1. **§2.2**: Replace volume-based triggers with a decision matrix keyed by task type, ambiguity, and required evidence.
2. **§3 + §6**: Split "agent" from "external tool adapter." Make `codex-debugger` either an Opus agent that calls Codex, or remove it and route directly to Codex via skill/hook.
3. **§8**: Define three supported product modes explicitly: `web-only`, `web+RN`, `web+Flutter`. Do not imply a single shared UI package works for Flutter.
4. **§1 + §8**: Narrow web scope to the user-confirmed platform default. If this template is "specialized for Next.js/React", move Vite/Remix to future extensions.
5. **§1 + §4 + §13**: Decide whether BFF is in-scope. If optional, mark it as an extension path, not a core agent/skill set.
6. **§4**: Add structured output contracts for Gemini skills: token JSON schema, screen decomposition schema, confidence rubric, and "human approval required" checkpoints.
7. **§6 + §10**: Define hook severity levels: `suggest`, `warn`, `require-explicit-override`. Without this, policy enforcement will drift.
8. **§3 + §4**: Add a dedicated `architecture-review` path in `/team-review`, especially for state, navigation, and shared-package boundaries.

## 5. Decision points before implementation
- **Monorepo vs single repo** (§13.1): this affects every path and should be fixed first.
- **Supported mobile mode** (§13.2): supporting both RN and Flutter materially changes agents, skills, and shared-package design.
- **Default state stack** (§13.3): make this explicit in Zone B contracts and review rules.
- **Whether BFF is core or extension** (§13.4): current spec is inconsistent.
- **Distribution model** (§13.6): copy-in template vs generator impacts `/init-webdev`, updates, and hook assumptions.
- Add one missing decision: **supported product modes** (`web-only`, `web+RN`, `web+Flutter`).

## 6. Confidence
- Routing trigger redesign: **High**
- Split agent vs tool-adapter ownership: **High**
- Rework cross-platform shared UI assumptions: **High**
- Narrow web framework scope: **Medium**
- Reclassify BFF as core vs extension: **High**
- Add Gemini artifact schemas and hook severity levels: **High**
