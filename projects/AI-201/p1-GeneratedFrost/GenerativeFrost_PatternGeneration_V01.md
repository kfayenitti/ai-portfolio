# Generative Frost Pattern Generation — V01

This version generates frost **units** directly from scattered points, without manual control sliders.

- Input: scattered points on a grid/surface
- Method: each point emits a small set of rays
- Lengths are computed from nearby points so rays naturally avoid intersections
- No animation in this version

## Node Context

- Use an **Attribute Wrangle**
- Set **Run Over** to **Detail (only once)**
- Feed your `Scatter` output into input 0

## VEX (paste into the detail wrangle)

```vex
// Auto unit rays from scatter points (no external controls)
// Assumes placement on ZX plane (Y up)

int seed = 12345;              // optional: change for different pattern
float TWO_PI = 2.0 * M_PI;

int n = npoints(0);
if (n < 2) return;

addattrib(0, "point", "pscale", 0.0);

for (int i = 0; i < n; i++)
{
    vector Pi = point(0, "P", i);

    // Local spacing from nearest neighbor (auto scale)
    int near2[] = nearpoints(0, Pi, 1e9, 2); // self + nearest
    if (len(near2) < 2) continue;

    int n1 = near2[1];
    vector P1 = point(0, "P", n1);
    float d1 = distance(Pi, P1);

    // Auto unit sizing from local density
    float max_len       = max(d1 * 0.48, 1e-4);
    float min_len       = d1 * 0.20;
    float clearance     = d1 * 0.22;
    float safety_margin = d1 * 0.08;
    float search_radius = d1 * 2.2;

    // Auto ray count per unit (3-6), deterministic per point
    int rays = int(floor(fit01(rand(set(i, seed, 7)), 3.0, 6.999)));

    // Random local orientation
    float base_ang = rand(set(i, seed, 101)) * TWO_PI;

    // Candidate blockers
    int near[] = nearpoints(0, Pi, search_radius);

    // Root width
    setpointattrib(0, "pscale", i, d1 * 0.06, "set");

    for (int r = 0; r < rays; r++)
    {
        float t = float(r) / float(rays);
        float ang = base_ang + t * TWO_PI;
        ang += fit01(rand(set(i, r, seed + 17)), -0.20, 0.20); // subtle jitter (radians)

        // ZX plane direction
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

            // Neighbor blocks this ray if close to its axis
            if (lat < clearance)
            {
                float stop = fwd - safety_margin;
                if (stop < allowed) allowed = stop;
            }
        }

        float L = clamp(allowed, min_len, max_len);
        if (L <= 1e-6) continue;

        int tip = addpoint(0, Pi + dir * L);
        setpointattrib(0, "pscale", tip, d1 * 0.025, "set");
        addprim(0, "polyline", i, tip);
    }
}
```

## Notes

- This is a **pattern layout pass** only (main unit rays).
- Side-branches are intentionally not generated yet.
- Works well as a foundation for a later branch/twig pass.

