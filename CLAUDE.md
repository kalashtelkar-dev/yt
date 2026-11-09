# GEO Dismantled video workflow

When the user gives a topic, a place, or says "make the video" or "same workflow", run the `geo-film` skill (`~/.claude/skills/geo-film/SKILL.md`) end to end. Do not wait for them to say it. Do not ask for approvals. At the start of every stage, read the stage's reference file in `~/.claude/skills/geo-film/references/`. Read `02-mistakes-and-fixes.md` first, every run.

The user can also start it with `/geo-film <topic>`.
