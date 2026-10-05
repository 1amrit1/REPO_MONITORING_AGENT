# Scope

## What the agent does
- Issue triage: classifies new issues (bug/feature/question), applies a priority label
- PR descriptions: reads a PR diff, drafts a structured description (what changed, why, risk areas)
- Weekly health reports: summarizes repo activity (issues opened/closed, PR velocity) on a schedule

## What the agent does NOT do
- No automatic code fixes
- No auto-merging of PRs
- No deleting issues or PRs
- No actions outside the repo it's explicitly pointed at

## Definition of done (MVP)
Issue opened on a test repo → agent classifies it → applies the correct label → posts a structured triage comment — all without human input at any step.
