# Helvetia vehicle rights policy — original fictional designs

**Decision date:** 28 October 2026. **Selected approach:** original, independently created vehicles for the commercially sold Helvetia and GundeliTheftAuto games.

## What counts as an approved asset

Only original cars with a distinct overall design, created from scratch by our team or commissioned under a signed agreement explicitly allowing commercial game use, adaptation, distribution, and transfer/assignment of necessary rights. Keep the creator agreement, source files, materials provenance, modification log, and approval evidence linked to each asset.

**No approval can guarantee that a third party won't make a claim.** Before release, seek an appropriately qualified lawyer's trademark / design / copyright review in the countries where the game will be sold.

## Strict sourcing rules

- **NO** Porsche, Macan, Cayenne, 911, RWB or other OEM nameplates, badges, crests, decals or exact recognisable styling clones in a ship-ready game vehicle.
- **NO** rebranded 1:1 OEM clones. A fake name such as “Borsche” on Porsche-shaped bodywork does not eliminate design or other legal risks.
- **NO** copied or ripped game meshes; **NO** unverified AI-generated derivatives of protected car artwork; **NO** marketplace/Sketchfab third-party models unless their complete provenance, rights, and identifiable vehicle design exposure are reviewed and approved.
- **YES** independently authored proportions, surfaces, lighting signatures, grilles, cabin layouts, rims, trim, interiors, chassis, and visual engine components.
- **YES** self-created procedural geometry and textures; licensed generic components may be incorporated only when their licenses expressly allow the intended commercial distribution, and their provenance is retained.
- Mark all proposed names as **working design codes**, not trademark-cleared brand names. Search relevant markets and obtain clearance before publishing names/logos.
- Reproduce no external maker's model from CAD, game files, scans, photography-traced meshes or copyrighted source drawings. Real-world general engineering principles may guide physically plausible construction.

## Quality requirements — Helvetia photorealism

- Realistic real-world dimensions and proportions; distinctive silhouette in front, rear, profile and three-quarter angles.
- Smooth continuous body panels, physically plausible edge radii, properly seated glass/lights, intentional panel seams only; no floating geometry or accidental gaps.
- Custom PBR paint/clearcoat, metal, glass, rubber, carbon, textiles; authored UVs and consistent texel density.
- Complete visible exterior and detailed cockpit; plausible underbody, suspensions, brakes, wheel hubs, exhaust/energy system and visible engine or EV drivetrain as appropriate.
- Clean object hierarchy, pivots, wheel separation, normals, collision and tiered LODs for Unreal 5.7.
- Reference QA: rendered views alongside independently created design sheets and factual dimensional specs; check against third-party models to avoid close visual copying.
- **No “AAA-ready” claim** without inspection of the exported actual mesh and texture set.

## Release controls

- Only files under `original_vehicles/` can be candidates for release. Existing `third_party/`, `Borsche_911_1981/`, `BATCHES/`, and research collections are **blocked from game packaging**.
- Original vehicles in `original_vehicles/manifest.json` start `concept_only` and cannot be distributed as final models.
- To change to `approved_for_release`, require project owner + legal approval, recorded authorship, asset hashes, complete QA, provenance, rights evidence and approved brand naming. No assistant should silently mark approvals.
- Do not delete legacy GitHub files without an explicit user request. Since this is a public repo, exclusion from packaging alone does **not** eliminate the risks of publishing legacy third-party meshes. Remove or privatize them once you authorize that operation.
