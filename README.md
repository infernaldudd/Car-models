# Car Models

## Current release direction — original fictional vehicles

**Helvetia / GundeliTheftAuto has selected independent original car designs rather than lookalikes of Porsche or other commercial manufacturers.**

- [Original-vehicle legal / quality / source policy](ORIGINAL_VEHICLE_RIGHTS_POLICY.md)
- [Five original sports-car design briefs](original_vehicles/SPORTS_BATCH_01.md)
- [Original vehicle manifest — all currently concepts, zero approved](original_vehicles/manifest.json)

**RELEASE WARNING:** Existing Porsche-sourced GLBs in `third_party/`, the procedural `Borsche_911_1981/` and earlier `BATCHES/` content are **legacy research only, blocked from distribution as game vehicles**. No car assets in this repository are currently cleared for a commercial Helvetia release. Third-party media must not be included in a build merely because a Creative Commons or other license allows commercial mesh use. Porsche branding and vehicle-design issues require separate review.

> Legacy files remain publicly present; they have NOT been deleted, made private, or legally cleared. Public hosting itself should be reviewed and addressed.

---

## Historical asset experiments (not approved for release)

Original game-ready car assets for the GundeliTheftAuto / Helvetia projects.

## Licensed sports-car sources — Batch 02 (5 GLBs)

[Browse five imported sports-car models and attribution](third_party/Sports_Batch_02/) · [Geometry validation](third_party/Sports_Batch_02/VALIDATION.json)

Five independently sourced Porsche sports-car meshes with original artist listings under **CC BY 4.0** or **CC BY-SA 4.0**. The GLBs have had upstream Meshopt compression removed for easier Unreal/Blender import. File integrity and structure are verified; **photorealism, parts gaps, interior and Porsche-logo/design rights are not yet cleared for final game shipping**. Keep [attribution and license notes](third_party/Sports_Batch_02/README.md) with the game's credits.

## Models

### Borsche 911 1981 — Smooth

A custom, unlicensed early-1980s rear-engine coupe inspired by the supplied reference photo, not an OEM Porsche mesh.

- **Smoothed higher-density curved panels:** body, roof, bonnet, rear engine lid, headlights, window glazing, wheel/tire profiles, mirrors, and rounded chrome details
- **3 GLB exports:** complete closed car, open rear engine lid, and standalone air-cooled flat-six visual engine
- Editable procedural Python source in `Borsche_911_1981/build_borsche.py`
- Approximately **317,794 triangles** for either full-car variant; approximate dimensions 4.29m × 1.65m × 1.32m, wheelbase 2.271m

See [Borsche_911_1981/README.md](Borsche_911_1981/README.md).

> This is a detailed game-art interpretation, not a photogrammetric scan, OEM engineering replica, or finished LOD/rigged vehicle.
