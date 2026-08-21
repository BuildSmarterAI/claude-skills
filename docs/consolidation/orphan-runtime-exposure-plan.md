# Orphan Runtime Exposure Plan — PROPOSED, NOT APPLIED

> **No exposure change was applied in D4.2.** This session assigned ownership; exposure is a
> separate decision requiring evidence this session could not obtain. See the blocker below.

## Blocker: is a disabled skill still reachable by name?

`ads/SKILL.md` invokes the thirteen channel skills **by name**. Turning them off via
`skillOverrides` would reclaim real budget, but it is unproven whether a skill marked `"off"`
is merely hidden from discovery or is genuinely unavailable when another skill names it.
If it is the latter, disabling them silently breaks the documented `ads` workflow - the exact
failure D4.2 exists to prevent. **Verify that semantic before applying any row below.**

## Proposed changes

| Skill | Current | Proposed | Consumer | Reason | Token delta |
|---|---|---|---|---|---:|
| `ads-audit` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −94 |
| `ads-budget` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −107 |
| `ads-competitor` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −99 |
| `ads-creative` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −97 |
| `ads-google` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −94 |
| `ads-hyros` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −104 |
| `ads-landing` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −93 |
| `ads-linkedin` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −101 |
| `ads-meta` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −92 |
| `ads-microsoft` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −96 |
| `ads-plan` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −90 |
| `ads-tiktok` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −95 |
| `ads-youtube` | ACTIVE | ON_DEMAND | `ads` orchestrator | Deep-dive layer; reached through `ads`, not discovered independently | −94 |

**Total if applied: −1,255 tokens (12.6 percentage points).**
Claude would fall from 68.4% to about 55.8% of the description budget.

## Explicitly NOT proposed

| Skill | Keep | Why |
|---|---|---|
| `ads` | **ACTIVE** | Entry point that spawns all seven audit-* agents. Disabling it removes the only route into the fleet. The only orphan with recorded use. |
| `construction-industry` | **ACTIVE** | Shared domain knowledge across four construction products; 582 description chars is cheap for that reach. |

## Rollback

Every proposed change is one `skillOverrides` key on the Claude side and one directory move on
the Codex side. Canonical source is unaffected either way, and snapshot `8a756b95` remains the
backstop.
