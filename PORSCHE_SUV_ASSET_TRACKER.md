# Porsche SUV photorealism and commercial clearance tracker

Updated 28 October 2026.

## Accepted for Helvetia / GundeliTheftAuto

**None yet.** A model is accepted only once its actual exported mesh is inspected from multiple directions, matched against real photo references, checked for textures and accurate proportions, and cleared for commercial game use. For public GitHub storage, raw-asset redistribution must also be permitted by the original artist.

## Realistic candidates to acquire and inspect

| Priority | Vehicle | Original source | License claimed | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Cayenne Turbo 955, 2005 | [CCamo / nicocarmo05 — game-ready PBR](https://sketchfab.com/3d-models/game-ready-pbr-porsche-cayenne-turbo-2005-0c21727cc75e4ecbb39c4eb5c78991ad) | CC BY | Artist describes realistic proportions, real-world scale, PBR materials, clean topology and separated body, wheels, doors, cabin; 28k triangles. Exterior quality not independently inspected yet. | **Candidate, no raw upload**; official download requires accessible Sketchfab session |
| 2 | Cayenne 2019 | [Mona x Supercars — Cayenne](https://sketchfab.com/3d-models/porsche-cayenne-d1fd357faf314607afc39a67d5b4f4f1) | CC BY | 985.5k triangles; listing specifies year and detailed finish. The mesh origin is **not established**. | **HOLD: prove author ownership** |
| 3 | Macan Turbo | [Nieve5677 — Macan Turbo](https://sketchfab.com/3d-models/porsche-macan-turbo-6ec30e99fc3d4b42b5eea0d77edc74ad) | CC BY | 391.3k triangles. Uploader provides no provenance or process description. | **HOLD: prove authorship and inspect mesh** |
| 4 | Macan with HQ interior | [Nieve5677 — Macan HQ](https://sketchfab.com/3d-models/porsche-macan-with-hq-interior-2eaf5997e49445db938643e298fec98c) | CC BY | 2.3M triangles, interior indicated; uploader provides no provenance. Big mesh does not equal realism. | **HOLD: prove authorship and inspect mesh** |

## Existing files not approved

- `third_party/Porsche_Macan_Kaban/Porsche_Macan_Kaban_CC_BY.glb` is **REJECTED FOR HELVETIA**. It is a stylized/custom Macan, not photorealistic. Retained only as an existing raw source, and must not be added to the game, the realistic car shortlist, or marketing screenshots.
- `Borsche_911_1981` procedural body is also not accepted as a faithful, photorealistic 1981 911 replica.

## Do not import

- Models extracted from CSR2, Forza, Need for Speed, Racing Master, Assetto Corsa, etc., absent a **real, independently verified right from the original game's rights holder**. A reuploader cannot grant a valid CC license for third-party game assets.
- Sketchfab 'NonCommercial' models.
- 'Editorial use only' models for a commercially sold open-world game.
- Marketplace 'royalty free' assets into **public GitHub raw folders** unless the publisher also expressly permits raw redistribution. Commercial in-game use is a different permission.

## Required acceptance gates (all must pass)

1. Distinctive body shape accurately matches the real vehicle: front/rear silhouettes, headlights, roof, beltline, wheelbase, track, windows, side panels, wheels, tail lamps.
2. **No cartoon/stylized reinterpretations**: credible photo realism, real materials, sensible normals and UVs, sufficiently detailed cockpit.
3. No floating panels, open cracks, randomly missing sections, unintentional intersections, or black voids; intentional seams, doors, windows and wheel wells remain modeled.
4. Realistic PBR layers: paint clearcoat, glass, metal, rubber, plastics, lights, interior materials; intact maps and UVs.
5. Vehicle scale and 4+ directional checks in a 3D viewer, plus side-by-side real photo references.
6. Original source creator provenance and the exact license of all meshes, decals and materials documented; original proper attribution preserved.
7. Commercial use and **public raw-asset redistribution** independently cleared. Porsche logo, brand/trade dress and vehicle-design rights separately reviewed; fictional rebranding does not automatically erase rights issues.
8. Importable GLB/FBX/OBJ for Unreal Engine 5.7, sensible scene hierarchy, separated rotating wheels, LOD planning and collision notes.
9. Exact exported file checked; no upload of README-only candidates as if they were finished car files.

Only mark an asset APPROVED once all conditions are tested. No fake quality scores.

## Next realistic-asset sourcing pass (28 October 2026)

**Important:** These are external source leads, **not** newly imported assets. The repo is public; do not upload models from royalty-free marketplaces unless the license explicitly permits public raw-mesh redistribution. Original Porsche branding rights are separately unresolved.

| SUV | Source | Realism evidence | Commercial release / GitHub status |
| --- | --- | --- | --- |
| 2024 Cayenne | [CGTrader: photorealistic Cayenne with interior and detached structure](https://www.cgtrader.com/3d-models/car/suv/2024-porsche-cayenne) | Description says 150–200 detached pieces, separate body/wheels/doors, several renderer formats and Blender/FBX/OBJ; seller claims high accuracy; actual GLB not inspected | Requires purchase, original-license and brand-rights review; **raw mesh cannot be committed to public repository under ordinary royalty-free terms**. Availability requires checking on storefront. |
| 2024 Cayenne | [CGTrader: zifir3d Cayenne 2024](https://www.cgtrader.com/3d-models/car/suv/porsche-cayenne-2024) | High-res surface geometry, 258,776 polygons and texture package; no authored interior confirmation | Archived page says $69 Royalty Free but also 'model not available'; don't assume purchasable. Even if obtained, no public raw source uploads. |
| 2025 Macan 4 | [TurboSquid: HKV Studios](https://www.turbosquid.com/3d-models/2025-porsche-macan-3d-2210522) | 332,670 polygons, PBR, high-detail interior, bonnet/trunk operations | **REJECT for commercial Helvetia**: item explicitly says 'Editorial Uses Only' notwithstanding standard license option. |
| 2005 Cayenne Turbo 955 | [Sketchfab CCamo author listing](https://sketchfab.com/3d-models/game-ready-pbr-porsche-cayenne-turbo-2005-0c21727cc75e4ecbb39c4eb5c78991ad) | 28,000-triangle CC BY author model, visible image shows comparatively simple wheels and interior; artist states real-world scale and separated parts | **NOT ACCEPTED as AAA** without real mesh import and realism QA; downloadable only by standard authorized account download, not obtained here. |

For normal CGTrader Royalty Free licensing, **commercial embedded game use may be permitted but uploading extracted models to public GitHub is not**. [CGTrader license explanation](https://help.cgtrader.com/hc/en-us/articles/360015124437-Royalty-Free-License). For TurboSquid, editorial-only restriction is additional and overriding: [license FAQ](https://www.turbosquid.com/help/en/articles/9937423-royalty-free-license-faq).
