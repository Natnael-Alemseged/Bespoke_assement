# Harbor jobs and difficulty evidence

## What belongs in the submission zip

Include this `jobs/` folder with the small **tracked** files below. They document oracle reliability and the required **terminus-2** / **Groq** / **kimi-k2** / **k=10** run.

Large Harbor outputs (Docker layers, full trial logs) are **not** committed: either they land in the **repository root** `./jobs/` when you run Harbor from the parent directory, or inside this folder if you run with `-p "."` from the task directory. Git ignores those timestamped trees via `.gitignore`.

## Tracked files

| File | Purpose |
|------|---------|
| `oracle-reliability.txt` | Repeated `oracle` runs (golden solution + verifier). |
| `EVIDENCE.md` | Grader summary: commands, model, artifact locations. |
| `terminus-2-k10-groq-kimi-k2.md` | Checklist and **results table** for the required terminus-2 k=10 run — **fill the table after you run it.** |

After your local `terminus-2` **k=10** run, paste Harbor’s summary metrics into `terminus-2-k10-groq-kimi-k2.md` before zipping the task folder.
