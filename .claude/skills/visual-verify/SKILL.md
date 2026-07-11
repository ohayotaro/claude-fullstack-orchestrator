---
name: visual-verify
description: PM visual acceptance of UI changes from captured screenshots and previews.
allowed-tools: "Read Bash(python3 *) Glob Grep Write Edit"
---

# Visual Verify

Visual acceptance is a PM activity (T0). Claude reads captured images directly; no external multimodal agent is involved.

## Procedure

1. The task brief's Required Validation lists screenshot/preview capture (Playwright screenshots, Storybook, simulator captures) and the output paths.
2. Codex captures the images during implementation and lists the paths in the result artifact.
3. Claude reads each image and judges against the brief's visual expectations: layout, states (loading/empty/error/populated), responsive behavior, theme variants.
4. Verdict per surface: `pass` / `review` (surface uncertainty to the user with the image) / `fail` (reject with specific findings; Codex fixes under the same brief).

## Rules

- A UI task is not accepted until every surface in scope has a `pass` or an explicit user-approved `review`.
- Baseline images for regression comparison live with the project's e2e assets; judgments compare candidate vs baseline plus the brief.
- Record the verdict and image paths in the task acceptance note.
