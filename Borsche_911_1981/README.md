# Borsche 911 1981 (Smooth)

Original procedural 1981 G-body-inspired sports coupe model, branded **Borsche**.

## Exports

| File | Description |
| --- | --- |
| `Borsche_911_1981_Smooth_Closed.glb` | Complete closed-lid car, PBR materials included |
| `Borsche_911_1981_Smooth_Engine_Open.glb` | Same car, rear lid raised to reveal flat-six |
| `Borsche_911_1981_Smooth_Flat_Six_Engine.glb` | Standalone air-cooled flat-six visual representation |
| `build_borsche.py` | Editable generator source |

The GitHub Actions workflow rebuilds all GLBs from `source/build_borsche.py.zlib.b64`. It unpacks the source, installs Python dependencies, generates assets, validates them, and commits the outputs.

## Smoothing pass

- Sculpted body sides: 481 × 27 parametric samples, rather than 281 × 12
- Bonnet / raised fenders: 159 × 73, rather than 83 × 39
- Coupe roof: 109 × 75, rather than 39 × 29
- Additional subdivisions for rear-quarter deck, service lid, front/rear windshields
- Denser headlamp buckets/lenses, mirror geometry, tires, chrome rings and tubes
- Preserve panels, shut lines, separate rear hatch and tire openings without indiscriminate welds

**Triangle count:** ~317,794 full car with either lid state. Materials are embedded in GLB. Model units are meters, axes +X front, +Y vehicle left, +Z up.

## Usage

Import the GLB to Blender, Unreal with its supported importer, or other glTF-capable software. In Blender you can save an editable `.blend` file after import.

To regenerate locally:

```bash
python -m pip install numpy scipy trimesh Pillow networkx
python Borsche_911_1981/build_borsche.py
```

## Remaining work

This is a close-range high-density asset. It still needs authored LODs, vehicle rigging / collision, realistic texture maps, and visual reference QA before being considered release-ready for a AAA production game. The engine is an appearance model rather than a mechanically verified 1981 SC drivetrain.
