# Sports Car Batch 02 — Five Porsche source meshes

**Created:** 28 October 2026. **Purpose:** source five *different* realistic sports-car base meshes to evaluate for the commercial Helvetia game. The model artists' listed CC BY or CC BY-SA licenses allow commercial mesh use and redistribution when all conditions are met. Mesh licensing does **not** clear third-party Porsche trademarks, protected logo/graphics, or other rights in vehicle designs.

## Files and source rights

**1. Porsche 911 Carrera 4S Lionsharp** — [Original artist's listing](https://sketchfab.com/3d-models/free-porsche-911-carrera-4s-d01b254483794de3819786d93e0e1ebf) · Lionsharp Studios · CC BY-SA 4.0 · [3D export](Porsche_911_Carrera_4S_Lionsharp/model.glb) · Original source description: web-configurator model by originating vehicle design studio; solid source.

**2. Porsche 911 GT3 ChevroletSS** — [Original artist's listing](https://sketchfab.com/3d-models/porsche-911-gt3-78d5c47ab2554c2592b7e499179a0792) · ChevroletSS · CC BY 4.0 · [3D export](Porsche_911_GT3_ChevroletSS/model.glb) · Original source description: creator calls it their first Sketchfab model and acknowledges modest materials; body + interior.

**3. Porsche 911 C4S 2020 JK3D** — [Original artist's listing](https://sketchfab.com/3d-models/porsche-911-c4s-2020-aerokit-ee69c474a1cc4085944cde4cb7ae87db) · JK3Dstudios · CC BY 4.0 · [3D export](Porsche_911_C4S_2020_JK3D/model.glb) · Original source description: uploader calls it 'my work'; materials and geometry to inspect.

**4. Porsche 959 Yakpower** — [Original artist's listing](https://sketchfab.com/3d-models/porsche-959-0530aa8fa4b74427a71c961a5bdd7087) · Yakpower · CC BY-SA 4.0 · [3D export](Porsche_959_Yakpower/model.glb) · Original source description: creator describes Fusion 360 modeling and Substance Painter texturing.

**5. Porsche 911 GT2 RS COOL601** — [Original artist's listing](https://sketchfab.com/3d-models/porsche-911-gt2-rs-with-angle-eyes-41419345868e406eaec8a271e33de3c1) · COOL601 · CC BY 4.0 · [3D export](Porsche_911_GT2_RS_COOL601/model.glb) · Original source description: uploader calls free rigged model and requests credits; full ownership requires further confirmation.

All 5 are independently named models from separate source listings; **not** color variants of one mesh. The original Sketchfab source, artist attribution and changes are recorded in [PROVENANCE.json](PROVENANCE.json). The meshes come from pinned [`pedrosoandre/carros`](https://github.com/pedrosoandre/carros) asset files, imported only after Git blob SHA and file-size verification.

## Modifications and license obligations

- The upstream `carros` library applied weld, simplification (~30% triangle target, varying by asset), prune and meshopt compression. These are **modified / optimized copies**, not original artist-resolution source files. The source author and original license still apply.
- Our workflow decompresses Meshopt to plain GLB for easier software import, where supported. It preserves mesh geometry from the upstream optimized copy and does not remove logos or alter the shape.
- Models with CC BY-SA (Carrera 4S / Porsche 959) remain **CC BY-SA 4.0** when you modify and redistribute their mesh; attributing them alone is not enough.
- Keep artist name, work title, source URL, CC license link and modifications in game credits. No original texture maps or third-party logos were independently rights-cleared in this batch.

## Commercial game release checklist (not yet approved)

- [ ] Inspect each GLB in Blender/Unreal from all angles and compare photo reference to silhouette.
- [ ] Inspect UV maps, textures and material fidelity; improve weak materials (GT3 in particular).
- [ ] Inspect door seals, window/body intersections, wheel gaps, panel topology and glass coverage.
- [ ] Check correct dimensions, distinct meshes, physics wheel separation, collision, interior and LODs.
- [ ] Remove or replace third-party Porsche badges/logos/graphics for a fictional marque; consult legal counsel if depicting recognizable protected vehicle designs.
- [ ] Ensure in-game attribution and the terms of CC BY-SA (if mesh adaptations distributed).
- [ ] Confirm no source assets were copied from proprietary racing games, and check all third-party texture rights.

**Note:** A CC license for the artist-authored 3D *mesh* is evidence of permission for commercial use under that license, but is **not** a Porsche AG license. The files should be treated as commercial-mesh-source assets pending model-specific QA and branding clearance, not as guaranteed lawsuit-proof production content.
