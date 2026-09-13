<!-- This file was generated with the assistance of an AI coding tool. -->

# Developer notes (in-progress features)

This directory holds **living design/working notes for unmerged feature branches**,
one Markdown file per feature, named after its branch (e.g.
`opening-template-on-type.md`).

## Purpose

A shared scratchpad so collaborators — and the AI agents they work with — can pick up
the context behind an in-progress branch: the problem, the design decisions and the
*why*, dead ends already ruled out, and what still needs testing. Because the note is
committed on the branch, it travels with the PR and shows up in the diff, so it is
discoverable without anyone being told where to look.

## How to use it (humans and agents)

- **Before working on a feature branch**, read its note here if one exists.
- **As the PR is refined**, keep the note current — append decisions, correct things
  that changed, update the test checklist.
- **One file per feature**, named after the branch.

## Lifecycle

These are *not* permanent user documentation. When a PR merges, either remove its note
or promote the durable parts (the load-bearing "why") into code comments or the regular
docs, so stale notes do not accumulate on the default branch.
