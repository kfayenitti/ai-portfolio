# Generative Frost Pattern Generation — V04

V04 is the updated three-wrangle pipeline with:

- Surface-orientation support from source geometry normals.
- Unit-level stagger timing for clustered growth.
- Strict parent-before-child twig timing.
- Single `growth` control with carve reveal.
- `pscale_ramp` plus growth-driven thickness for PolyWire.

This version preserves V03 structure while integrating all latest fixes.

---

## Network order (copy this chain)

1. `Grid` (or any source surface, can be rotated).
2. `Scatter` (points on source surface).
3. **Attribute Wrangle 1** (Detail only once):
   - Input 0: scatter points
   - Input 1: original source surface (for robust normal sampling)
4. **Attribute Wrangle 2** (Detail only once):
   - Input 0: output of Wrangle 1
5. `Resample` (small segment length for smooth reveal).
6. `Facet` with **Unique Points** ON.
7. **Attribute Wrangle 3** (Detail only once):
   - Input 0: output of Facet
8. Optional: `PolyWire` using point `pscale`.

---

## Wrangle 1 — Main stems (stagger + source orientation)

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Inputs:**  
- Input 0: scattered points  
- Input 1: source surface (same one used for scatter)

### Parameters

| Name | Type | Notes |
|------|------|-------|
| `seed` | int | Random seed |
| `gap_mult` | float | `< 1` tighter, `> 1` wider branch clearance |
| `rays_min` | int | Minimum main rays per seed |
| `rays_max` | int | Maximum main rays per seed |
| `unit_stagger` | float | Timing spread strength (`1..8` recommended) |

### VEX

```vex
// Wrangle 1 — Detail only once — main stems from scatter
// Surface-oriented version using source geometry normal sampling from input 1.

int seed = chi("seed");
float gap_mult = max(chf("gap_mult"), 0.05);
int rays_min = max(3, chi("rays_min"));
int rays_max = max(rays_min, chi("rays_max"));
float unit_stagger = max(chf("unit_stagger"), 0.001);

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
addattrib(0, "prim", "surfaceN", {0,1,0}); // used by Wrangle 2

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

    // Balanced stagger shaping (avoids end pile-up)
    float phase = rand(set(i, seed, 9001));
    float p = phase;
    if (unit_stagger > 1.0)
    {
        float invk = 1.0 / unit_stagger;
        if (p < 0.5) p = 0.5 * pow(p * 2.0, invk);
        else         p = 1.0 - 0.5 * pow((1.0 - p) * 2.0, invk);
    }
    else
    {
        p = pow(p, unit_stagger);
    }

    float start_max = fit(clamp(unit_stagger, 1.0, 8.0), 1.0, 8.0, 0.72, 0.90);
    float point_start = p * start_max;
    float local_span = fit(clamp(unit_stagger, 1.0, 8.0), 1.0, 8.0, 0.12, 0.08);

    // Robust orientation: sample normal from source surface on input 1
    int srcprim = -1;
    vector srcuv = {0,0,0};
    float dsrc = xyzdist(1, Pi, srcprim, srcuv);

    vector Np = {0,1,0};
    if (srcprim >= 0)
        Np = normalize(prim_normal(1, srcprim, srcuv.x, srcuv.y));
    if (length2(Np) < 1e-8)
        Np = {0,1,0};

    // Local tangent basis on the source surface
    vector ref = (abs(dot(Np, {0,1,0})) < 0.99) ? set(0,1,0) : set(1,0,0);
    vector Tx = normalize(cross(Np, ref));
    vector Tz = normalize(cross(Np, Tx));

    for (int r = 0; r < rays; r++)
    {
        float t_ray = float(r) / float(max(1, rays - 1) + 1e-6);
        float ang = base_ang + (float(r) / float(rays)) * TWO_PI;
        ang += fit01(rand(set(i, r, seed + 17)), -0.08, 0.08);

        // Direction follows source surface orientation
        vector dir = normalize(cos(ang) * Tx + sin(ang) * Tz);

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

        float stem_grow_u = clamp(point_start + t_ray * local_span, 0.0, 0.94);

        int pr = addprim(0, "polyline", i, tip);
        setprimattrib(0, "is_main_stem", pr, 1, "set");
        setprimattrib(0, "prim_kind", pr, 1, "set");
        setprimattrib(0, "grow_u", pr, stem_grow_u, "set");
        setprimattrib(0, "parent_u", pr, 0.0, "set");
        setprimattrib(0, "rest_root", pr, Pi, "set");
        setprimattrib(0, "rest_tip", pr, tipP, "set");
        setprimattrib(0, "surfaceN", pr, Np, "set");
    }
}
```

---

## Wrangle 2 — Twigs (strict parent timing + anti-bunching)

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Input:** output of Wrangle 1

### Parameters

| Name | Type | Notes |
|------|------|-------|
| `seed` | int | Random seed |
| `twigs_amount` | int | Twig pairs per main stem |
| `twig_len_mult` | float | Twig length multiplier from stem length |
| `twig_splay_deg` | float | Twig splay angle |
| `twig_jitter_deg` | float | Angular noise for twig direction |
| `clearance_mult` | float | Collision clearance factor |
| `min_len_mult` | float | Minimum twig length threshold |
| `twig_taper_ramp` | float ramp | Length taper along stem parameter |

### VEX

```vex
// Wrangle 2 — Detail only once — paired twigs on main stems
// Surface-oriented side vector + strict parent->child timing + anti-bunching

int seed = chi("seed");
int twigs_amount = max(1, chi("twigs_amount"));
float twig_len_mult = chf("twig_len_mult");
float twig_splay_deg = chf("twig_splay_deg");
float twig_jitter_deg = chf("twig_jitter_deg");
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

    // Use surface normal from parent stem (from Wrangle 1)
    vector surfN = {0,1,0};
    if (hasprimattrib(0, "surfaceN")) surfN = normalize(prim(0, "surfaceN", pr));
    if (length2(surfN) < 1e-8) surfN = {0,1,0};

    vector side = normalize(cross(surfN, tangent));
    if (length(side) < 1e-6)
    {
        vector alt = (abs(dot(tangent, {0,1,0})) < 0.99) ? set(0,1,0) : set(1,0,0);
        side = normalize(cross(alt, tangent));
    }

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

        float parent_reach_u = clamp(parent_u + u * (1.0 - parent_u), 0.0, 0.999);
        float stylistic_u = parent_u + 0.14 + u * 0.22;
        float twig_jit = fit01(rand(set(pr, k, seed + 9991)), -0.04, 0.04);

        float after_parent_delay = 0.015;
        float twig_u = max(stylistic_u + twig_jit, parent_reach_u + after_parent_delay);
        twig_u = clamp(twig_u, 0.0, 0.94); // avoid end clumping

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

## Resample + Facet

### Resample

- Set a small segment `Length` to give each polyline enough points for smooth carve.

### Facet

- Turn **Unique Points** ON.

This is required so Wrangle 3 can move each polyline independently.

---

## Wrangle 3 — Single growth + pscale ramp growth

**Node:** Attribute Wrangle  
**Run Over:** Detail (only once)  
**Input:** after Resample + Facet

### Parameters

| Name | Type | Notes |
|------|------|-------|
| `growth` | float | Animate 0 to 1 over shot |
| `pscale_ramp` | float ramp | Radius profile root to tip |

### VEX

```vex
// Wrangle 3 — Detail only once — carve-style growth + growth-driven pscale
// Input: after Resample + Facet (Unique Points ON)
// Requires per-prim: grow_u, rest_root, rest_tip

float growth = clamp(chf("growth"), 0.0, 1.0);
float g = smooth(0.0, 1.0, growth);

int npr = nprimitives(0);

for (int pr = 0; pr < npr; pr++)
{
    float gu = clamp(prim(0, "grow_u", pr), 0.0, 0.999);

    vector rootP = prim(0, "rest_root", pr);
    vector tipP0 = prim(0, "rest_tip", pr);

    // Order-safe timing
    float br = clamp((g - gu) / max(1e-5, 1.0 - gu), 0.0, 1.0);
    br = smooth(0.0, 1.0, br);

    // Thickness maturity as branch grows
    float mature = pow(br, 0.7);

    int pts[] = primpoints(0, pr);
    int m = len(pts);
    if (m < 2) continue;

    for (int k = 0; k < m; k++)
    {
        float u = float(k) / float(m - 1);

        float u_clamped = min(u, br);
        vector Pnew = lerp(rootP, tipP0, u_clamped);
        setpointattrib(0, "P", pts[k], Pnew, "set");

        float base_ps = point(0, "pscale", pts[k]);
        float ramp_mul = chramp("pscale_ramp", u);
        float pnew = max(base_ps * ramp_mul * mature, 1e-4);
        setpointattrib(0, "pscale", pts[k], pnew, "set");
    }
}
```

---

## Version notes

- V04 keeps the V03 pipeline pattern but resolves:
  - rotated surface orientation mismatch,
  - late twig end-bunching,
  - timing consistency under higher stagger values.
- If surface orientation still appears wrong, confirm Wrangle 1 input 1 is connected to the same source surface used to generate scatter points.
