# General DST (legacy)

!!! warning "Legacy application"
    The General DST (`pages/1_General_DST.py`) is a standalone page that predates the current Integrated DST. Its functionality — OSM infrastructure extraction, Köppen climate classification, AI context reports, Level 1 RAMS SHEEP scoring, and Level 2 PRI calculation — is fully provided by the **[Integrated DST](integrated_dst.md)** under the **Custom Site Analysis** mode, with additional features including authentication, multi-expert consensus, SSF/SEI NbS filtration, and analysis snapshot saving.

    The legacy page remains accessible at `/General_DST` but is no longer the primary deliverable.

For documentation of the current Custom Site Analysis workflow see **[Integrated DST — Mode 2: Custom Site Analysis](integrated_dst.md#mode-2-custom-site-analysis)**.

---

## Key differences from Integrated DST

| Feature | General DST (legacy) | Integrated DST |
|---------|---------------------|----------------|
| Authentication | None | Supabase (viewer / expert / admin roles) |
| NbS filtration | Basic hazard matching | Full SSF + SEI + HIA scoring and ranking |
| Analysis saving | None | Supabase snapshots with load / delete |
| Level 1 consensus | None | Multi-expert consensus, live averaging |
| Specific Site access | Separate page | Unified sidebar navigation |
| Level 3 (Specific Sites) | Not available | GitHub-hosted content per demo site |
