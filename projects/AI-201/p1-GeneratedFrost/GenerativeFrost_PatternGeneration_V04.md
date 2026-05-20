# Generative Frost Pattern Generation — V04

V04 is the **three-wrangle pipeline** with **carve-style growth** and a single `growth` control on the final wrangle.

- **Wrangle 1:** scatter → main stems (static geometry + animation metadata on primitives).
- **Wrangle 2:** main stems → paired twigs (static + metadata; twig timing is forced after parent stem).
- **Resample + Facet:** subdivide polylines and unique points so carve animation is smooth.
- **Wrangle 3:** one `growth` parameter; slides points along each line (no geometry deletion pop).

Assumes placement on the **ZX plane** (Y up), same as earlier pattern versions.

---

## Network order (copy this chain)

1. `Grid` (or surface) → `Scatter` (points only).
2. **Attribute Wrangle — Wrangle 1** (Detail only once) — builds main stems.
3. **Attribute Wrangle — Wrangle 2** (Detail only once) — builds twigs on `is_main_stem == 1` prims.
4. **Resample** — uniform division length (e.g. `0.02`–`0.08` in your scene units; tune to scale).
5. **Facet** — enable **Unique Points** so each polyline vertex can move independently during carve.
6. **Attribute Wrangle — Wrangle 3** (Detail only once) — animate using `growth` only.

Optional after Wrangle 3: **PolyWire** (use `pscale` if you kept it from Wrangle 1/2).

---

## Wrangle 1 — Main stems (static + prim metadata)

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Input:** scattered points

### Parameters

| Name | Type | Notes |
|------|------|--------|
| `seed` | int | Random seed |
| `gap_mult` | float | `< 1` tighter, `> 1` wider gap vs neighbors |
| `rays_min` | int | Min rays per unit (e.g. 5) |
| `rays_max` | int | Max rays per unit (≥ `rays_min`) |

### Primitive attributes written

- `is_main_stem` = 1 on main rays.
- `prim_kind` = 1 (main).
- `grow_u` = 0..1 order along rays for staggered growth.
- `rest_root`, `rest_tip` = rest positions for Wrangle 3.

### VEX

```vex
// Wrangle 1 — Detail only once — main stems from scatter
// ZX plane (Y up)

int seed = chi("seed");
float gap_mult = max(chf("gap_mult"), 0.05);
int rays_min = max(3, chi("rays_min"));
int rays_max = max(rays_min, chi("rays_max"));

float TWO_PI = 2.0 * M_PI;

int n = npoints(0);
if (n < 2) return;

addattrib(0, "point", "pscale", 0.0);
addattrib(0, "prim", "is_main_stem", 0);
addattrib(0, "prim", "prim_kind", 0);
addattrib(0, "prim", "grow_u", 0.0);
addattrib(0, "prim", "parent_u", 0.0);
addattrib(0, "prim", "rest_root", {0,0,0});
addattrib(0, "prim", "rest_tip", {0,0,0});

for (int i = 0; i < n; i++)
{
    vector Pi = point(0, "P", i);

    int near2[] = nearpoints(0, Pi, 1e9, 2);
    if (len(near2) < 2) continue;

    int n1 = near2[1];
    vector P1 = point(0, "P", n1);
    float d1 = distance(Pi, P1);

    float tight = 1.0 / gap_mult;

    float max_len       = max(d1 * 0.48 * tight, 1e-4);
    float min_len       = d1 * 0.20;
    float clearance     = max(d1 * 0.22 * gap_mult, d1 * 0.03);
    float safety_margin = max(d1 * 0.08 * gap_mult, d1 * 0.01);
    float search_radius = d1 * 2.2;

    int rays = int(floor(fit01(rand(set(i, seed, 7)), float(rays_min), float(rays_max + 0.999))));
    rays = max(1, rays);

    float base_ang = rand(set(i, seed, 101)) * TWO_PI;
    int near[] = nearpoints(0, Pi, search_radius);

    setpointattrib(0, "pscale", i, d1 * 0.06, "set");

    for (int r = 0; r < rays; r++)
    {
        float t_ray = float(r) / float(max(1, rays - 1) + 1e-6);
        float ang = base_ang + (float(r) / float(rays)) * TWO_PI;
        ang += fit01(rand(set(i, r, seed + 17)), -0.08, 0.08);

        vector dir = normalize(set(cos(ang), 0.0, sin(ang)));

        float allowed = max_len;
        foreach (int j; near)
        {
            if (j == i) continue;
            vector Pj = point(0, "P", j);
            vector v = Pj - Pi;
            float fwd = dot(v, dir);
            if (fwd <= 0.0) continue;
            float lat = length(v - dir * fwd);
            if (lat < clearance)
            {
                float stop = max(0.0, fwd - safety_margin);
                allowed = min(allowed, stop);
            }
        }

        float ulen = rand(set(i, r, seed + 555));
        float len_bias = pow(ulen, 1.8);
        float desired = fit(len_bias, 0.0, 1.0, min_len, max_len);
        if (rand(set(i, r, seed + 777)) < 0.10) desired *= 1.25;

        float L = min(allowed, desired);
        if (L < min_len * 0.35) continue;

        vector tipP = Pi + dir * L;
        int tip = addpoint(0, tipP);
        setpointattrib(0, "pscale", tip, d1 * 0.025, "set");

        int pr = addprim(0, "polyline", i, tip);
        setprimattrib(0, "is_main_stem", pr, 1, "set");
        setprimattrib(0, "prim_kind", pr, 1, "set");
        setprimattrib(0, "grow_u", pr, t_ray, "set");
        setprimattrib(0, "parent_u", pr, 0.0, "set");
        setprimattrib(0, "rest_root", pr, Pi, "set");
        setprimattrib(0, "rest_tip", pr, tipP, "set");
    }
}
```

---

## Wrangle 2 — Twigs (static + twig after parent timing)

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Input:** output of Wrangle 1

Twigs use **`grow_u` strictly after** the parent stem’s `grow_u`, so Wrangle 3 will not show twigs before that stem has started.

### Parameters

| Name | Type | Notes |
|------|------|--------|
| `seed` | int | |
| `twigs_amount` | int | Pairs per main stem (e.g. 4) |
| `twig_len_mult` | float | e.g. 0.22 |
| `twig_splay_deg` | float | e.g. 40 |
| `twig_jitter_deg` | float | e.g. 8 |
| `clearance_mult` | float | e.g. 0.22 |
| `min_len_mult` | float | e.g. 0.12 |
| `twig_taper_ramp` | float ramp | Taper along stem parameter `u` |

### VEX

```vex
// Wrangle 2 — Detail only once — paired twigs on main stems
// ZX plane
// NOTE: Degree sliders are in real degrees, not 0-1 normalized ramps.
// Use values like 20, 40, 60 (not 0.2, 0.4, 0.6) for visible changes.

int seed = chi("seed");
int twigs_amount = max(1, chi("twigs_amount"));
float twig_len_mult = chf("twig_len_mult");
float twig_splay_deg = chf("twig_splay_deg");   // Degrees input (e.g. 20-60), not 0-1
float twig_jitter_deg = chf("twig_jitter_deg"); // Degrees input (e.g. 2-15), not 0-1
float clearance_mult = chf("clearance_mult");
float min_len_mult = chf("min_len_mult");

float splay = radians(twig_splay_deg);
float jitter = radians(twig_jitter_deg);

addattrib(0, "point", "pscale", 0.0);
addattrib(0, "prim", "is_main_stem", 0);
addattrib(0, "prim", "prim_kind", 0);
addattrib(0, "prim", "grow_u", 0.0);
addattrib(0, "prim", "parent_u", 0.0);
addattrib(0, "prim", "rest_root", {0,0,0});
addattrib(0, "prim", "rest_tip", {0,0,0});

int base_npr = nprimitives(0);
int has_main = hasprimattrib(0, "is_main_stem");

function int blocked_by_geo(int geo; vector A; vector B; int parent_prim; float clear_r)
{
    int samples = 4;
    for (int s = 0; s <= samples; s++)
    {
        float t = float(s) / float(samples);
        vector P = lerp(A, B, t);
        int hp = -1;
        vector uv = {0,0,0};
        float d = xyzdist(geo, P, hp, uv);
        if (hp >= 0 && hp != parent_prim && d < clear_r) return 1;
    }
    return 0;
}

for (int pr = 0; pr < base_npr; pr++)
{
    if (has_main && prim(0, "is_main_stem", pr) != 1) continue;

    int vtx[] = primvertices(0, pr);
    if (len(vtx) < 2) continue;

    int p0 = vertexpoint(0, vtx[0]);
    int p1 = vertexpoint(0, vtx[len(vtx)-1]);

    vector P0 = point(0, "P", p0);
    vector P1 = point(0, "P", p1);

    vector tangent = normalize(P1 - P0);
    float stem_len = distance(P0, P1);
    if (stem_len < 1e-6) continue;

    vector side = normalize(set(-tangent.z, 0.0, tangent.x));
    if (length(side) < 1e-6) side = {1,0,0};

    float clear_r = max(stem_len * clearance_mult, 1e-4);
    float min_L = stem_len * min_len_mult;

    float parent_u = prim(0, "grow_u", pr);

    for (int k = 0; k < twigs_amount; k++)
    {
        float slot = (float(k) + 1.0) / (float(twigs_amount) + 1.0);
        float ujit = fit01(rand(set(pr, k, seed + 101)), -0.03, 0.03);
        float u = clamp(slot + ujit, 0.14, 0.90);

        vector rootP = lerp(P0, P1, u);

        float taper = chramp("twig_taper_ramp", u);
        float Lbase = stem_len * twig_len_mult * max(0.0, taper);
        Lbase *= fit01(rand(set(pr, k, seed + 171)), 0.85, 1.15);
        if (Lbase < min_L) continue;

        float ja = fit01(rand(set(pr, k, seed + 211)), -jitter, jitter);
        float ang = splay + ja;

        vector dirL = normalize(-cos(ang) * side + sin(ang) * tangent);
        vector dirR = normalize( cos(ang) * side + sin(ang) * tangent);

        vector tipL = rootP + dirL * Lbase;
        vector tipR = rootP + dirR * Lbase;

        int blockL = blocked_by_geo(0, rootP, tipL, pr, clear_r);
        int blockR = blocked_by_geo(0, rootP, tipR, pr, clear_r);

        float ps0 = point(0, "pscale", p0);
        float ps1 = point(0, "pscale", p1);
        float psm = lerp(ps0, ps1, u);
        if (psm <= 0) psm = stem_len * 0.02;

        // Twigs always start after parent stem in growth space
        float twig_u = clamp(parent_u + 0.18 + u * 0.28, 0.0, 0.98);

        if (!blockL)
        {
            int rL = addpoint(0, rootP);
            int tL = addpoint(0, tipL);
            setpointattrib(0, "pscale", rL, psm * 0.90, "set");
            setpointattrib(0, "pscale", tL, psm * 0.55, "set");

            int prL = addprim(0, "polyline", rL, tL);
            setprimattrib(0, "is_main_stem", prL, 0, "set");
            setprimattrib(0, "prim_kind", prL, 2, "set");
            setprimattrib(0, "grow_u", prL, twig_u, "set");
            setprimattrib(0, "parent_u", prL, parent_u, "set");
            setprimattrib(0, "rest_root", prL, rootP, "set");
            setprimattrib(0, "rest_tip", prL, tipL, "set");
        }

        if (!blockR)
        {
            int rR = addpoint(0, rootP);
            int tR = addpoint(0, tipR);
            setpointattrib(0, "pscale", rR, psm * 0.90, "set");
            setpointattrib(0, "pscale", tR, psm * 0.55, "set");

            int prR = addprim(0, "polyline", rR, tR);
            setprimattrib(0, "is_main_stem", prR, 0, "set");
            setprimattrib(0, "prim_kind", prR, 2, "set");
            setprimattrib(0, "grow_u", prR, twig_u, "set");
            setprimattrib(0, "parent_u", prR, parent_u, "set");
            setprimattrib(0, "rest_root", prR, rootP, "set");
            setprimattrib(0, "rest_tip", prR, tipR, "set");
        }
    }
}
```

---

## Resample + Facet (required for smooth carve)

### Resample

- **Length:** set to a small fraction of your typical stem length (scene-scale dependent).
- Goal: enough points per line so the carve slide looks continuous.

### Facet

- Turn **Unique Points** **ON** for polygons/polylines (so each vertex is its own point and Wrangle 3 can move them independently).

---

## Wrangle 3 — Single `growth`, carve-style reveal

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Input:** geometry **after** Resample + Facet

### Parameters

| Name | Type | Notes |
|------|------|--------|
| `growth` | float | **0 → 1** over the shot |

Example expression on `growth`:

```text
($FF - 1) / max($FEND - 1, 1)
```

### VEX

```vex
// Wrangle 3 — Detail only once — carve-style growth, single parameter
// Input: geometry after Resample + Facet (Unique Points ON)
// Requires on each polyline prim: grow_u, rest_root, rest_tip, prim_kind

float growth = clamp(chf("growth"), 0.0, 1.0);

int npr = nprimitives(0);

for (int pr = 0; pr < npr; pr++)
{
    float gu = clamp(prim(0, "grow_u", pr), 0.0, 1.0);

    vector rootP = prim(0, "rest_root", pr);
    vector tipP0 = prim(0, "rest_tip", pr);

    // Normalized reveal: every prim reaches full rest_tip at growth == 1
    float br = clamp((growth - gu) / max(1e-5, 1.0 - gu), 0.0, 1.0);
    br = smooth(0.0, 1.0, br);

    int pts[] = primpoints(0, pr);
    int m = len(pts);
    if (m < 2) continue;

    for (int k = 0; k < m; k++)
    {
        float u = float(k) / float(m - 1);
        float u_clamped = min(u, br);
        vector Pnew = lerp(rootP, tipP0, u_clamped);
        setpointattrib(0, "P", pts[k], Pnew, "set");
    }
}
```

**Note:** After Resample, primitive `rest_tip` is still the original tip position from Wrangle 1/2; Wrangle 3 lerps along **root → rest_tip**, which matches the resampled polyline parameterization closely enough for a clean carve look. If you need pixel-perfect match to pre-resample length, store `rest_tip` on points instead and interpolate in a point wrangle.

---

## Version notes

- **V01 / V02:** static pattern only (see earlier markdown files).
- **V04:** this document — **three wrangles + Resample + Facet + one growth slider**.

If twigs still feel early relative to a specific stem, increase the offset in Wrangle 2 (`0.18` in `twig_u = parent_u + 0.18 + ...`).
