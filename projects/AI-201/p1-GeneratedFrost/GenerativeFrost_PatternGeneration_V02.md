# Generative Frost Pattern Generation — V02

V02 adds:

- `gap_mult` control for tighter or looser spacing
- stronger branch length variation
- collision-safe length capping so rays do not intersect neighbors

This is still the **no-animation, no-side-branches** pattern pass.

## Node Context

- Use an **Attribute Wrangle**
- Set **Run Over** to **Detail (only once)**
- Input 0 should be your `Scatter` points
- Grid orientation assumed to be **ZX plane** (Y up)

## Parameters (create on the wrangle)

- `seed` (int)
- `gap_mult` (float)

Suggested values:

- `seed = 12345`
- `gap_mult = 0.7` (tighter), `1.0` (default), `1.3` (looser)

## VEX

```vex
// Detail Wrangle (Run Over: Detail only once)
// Auto unit rays from scatter points
// Assumes placement on ZX plane (Y up)

int seed = chi("seed");
float gap_mult = max(chf("gap_mult"), 0.05); // 0.6 tighter, 1.0 default, 1.4 wider
float TWO_PI = 2.0 * M_PI;

int n = npoints(0);
if (n < 2) return;

// optional width attribute for PolyWire later
addattrib(0, "point", "pscale", 0.0);

for (int i = 0; i < n; i++)
{
    vector Pi = point(0, "P", i);

    // nearest-neighbor spacing (local density)
    int near2[] = nearpoints(0, Pi, 1e9, 2); // self + nearest
    if (len(near2) < 2) continue;

    int n1 = near2[1];
    vector P1 = point(0, "P", n1);
    float d1 = distance(Pi, P1);

    // lower gap_mult => tighter packing
    float tight = 1.0 / gap_mult;

    // reach + collision envelope
    float max_len       = max(d1 * 0.48 * tight, 1e-4);
    float min_len       = d1 * 0.20;
    float clearance     = d1 * 0.22 * gap_mult;
    float safety_margin = d1 * 0.08 * gap_mult;
    float search_radius = d1 * 2.2;

    // keep collision stable at extreme values
    clearance     = max(clearance, d1 * 0.03);
    safety_margin = max(safety_margin, d1 * 0.01);

    // per-unit ray count (3..6)
    int rays = int(floor(fit01(rand(set(i, seed, 7)), 3.0, 6.999)));

    // random local orientation
    float base_ang = rand(set(i, seed, 101)) * TWO_PI;

    // nearby candidate blockers
    int near[] = nearpoints(0, Pi, search_radius);

    // root width
    setpointattrib(0, "pscale", i, d1 * 0.06, "set");

    for (int r = 0; r < rays; r++)
    {
        float t = float(r) / float(rays);
        float ang = base_ang + t * TWO_PI;
        ang += fit01(rand(set(i, r, seed + 17)), -0.20, 0.20); // radians jitter

        // ZX plane direction
        vector dir = normalize(set(cos(ang), 0.0, sin(ang)));

        float allowed = max_len;

        // collision-limited reach along this direction
        foreach (int j; near)
        {
            if (j == i) continue;

            vector Pj = point(0, "P", j);
            vector v = Pj - Pi;

            float fwd = dot(v, dir);
            if (fwd <= 0.0) continue; // blocker behind root

            float lat = length(v - dir * fwd);

            if (lat < clearance)
            {
                float stop = max(0.0, fwd - safety_margin);
                allowed = min(allowed, stop);
            }
        }

        // branch length variation (still collision-safe)
        float ulen = rand(set(i, r, seed + 555));
        float len_bias = pow(ulen, 1.8); // >1 biases shorter rays
        float desired = fit(len_bias, 0.0, 1.0, min_len, max_len);

        // occasional hero-long ray, still capped by allowed
        if (rand(set(i, r, seed + 777)) < 0.12)
            desired *= 1.35;

        float L = min(allowed, desired);

        // skip micro fragments
        if (L < min_len * 0.35) continue;

        int tip = addpoint(0, Pi + dir * L);
        setpointattrib(0, "pscale", tip, d1 * 0.025, "set");
        addprim(0, "polyline", i, tip);
    }
}
```

## Notes

- V02 keeps the no-intersection behavior by always using `L = min(allowed, desired)`.
- Lowering `gap_mult` makes units grow closer while keeping collision checks active.
- Next step can be a V03 side-branch pass that inherits this same spacing logic.
