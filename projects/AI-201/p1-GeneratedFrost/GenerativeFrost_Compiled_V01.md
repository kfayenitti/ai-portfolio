# Generative Frost Compiled — V01

## Wrangle 1

```vex
// Detail Wrangle (Run Over: Detail only once)
// Base stem generation: even angular layout, random lengths, no big directional gaps
// Assumes ZX plane (Y up)

int seed = chi("seed");
float gap_mult = max(chf("gap_mult"), 0.05);   // 0.6 tighter, 1.0 default, 1.3 looser
int rays_per_unit = max(3, chi("rays_per_unit")); // fixed count per unit for even coverage

float TWO_PI = 2.0 * M_PI;

int n = npoints(0);
if (n < 2) return;

addattrib(0, "point", "pscale", 0.0);
addattrib(0, "prim", "is_main_stem", 0);

for (int i = 0; i < n; i++)
{
    vector Pi = point(0, "P", i);

    // local spacing from nearest neighbor
    int near2[] = nearpoints(0, Pi, 1e9, 2); // self + nearest
    if (len(near2) < 2) continue;

    int n1 = near2[1];
    vector P1 = point(0, "P", n1);
    float d1 = distance(Pi, P1);

    float tight = 1.0 / gap_mult;

    float max_len       = max(d1 * 0.48 * tight, 1e-4);
    float min_len       = d1 * 0.20;
    float clearance     = d1 * 0.22 * gap_mult;
    float safety_margin = d1 * 0.08 * gap_mult;
    float search_radius = d1 * 2.2;

    clearance     = max(clearance, d1 * 0.03);
    safety_margin = max(safety_margin, d1 * 0.01);

    // one random rotation per unit, but rays are evenly spaced
    float base_ang = rand(set(i, seed, 101)) * TWO_PI;

    int near[] = nearpoints(0, Pi, search_radius);

    setpointattrib(0, "pscale", i, d1 * 0.06, "set");

    for (int r = 0; r < rays_per_unit; r++)
    {
        // even angular distribution = no directional gaps
        float ang = base_ang + (float(r) / float(rays_per_unit)) * TWO_PI;

        // tiny jitter so it doesn't look too perfect
        ang += fit01(rand(set(i, r, seed + 17)), -0.08, 0.08);

        vector dir = normalize(set(cos(ang), 0.0, sin(ang))); // ZX plane

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

        // random desired length, collision-capped
        float ulen = rand(set(i, r, seed + 555));
        float len_bias = pow(ulen, 1.8); // bias toward shorter, occasional long
        float desired = fit(len_bias, 0.0, 1.0, min_len, max_len);

        if (rand(set(i, r, seed + 777)) < 0.10)
            desired *= 1.25;

        float L = min(allowed, desired);
        if (L < min_len * 0.35) continue;

        int tip = addpoint(0, Pi + dir * L);
        setpointattrib(0, "pscale", tip, d1 * 0.025, "set");

        int pr = addprim(0, "polyline", i, tip);
        setprimattrib(0, "is_main_stem", pr, 1, "set");
    }
}
```

## Wrangle 2

```vex
// Detail Wrangle (Run Over: Detail only once)
// Base stem generation: even angular layout, random lengths, no big directional gaps
// Assumes ZX plane (Y up)

int seed = chi("seed");
float gap_mult = max(chf("gap_mult"), 0.05);   // 0.6 tighter, 1.0 default, 1.3 looser
int rays_per_unit = max(3, chi("rays_per_unit")); // fixed count per unit for even coverage

float TWO_PI = 2.0 * M_PI;

int n = npoints(0);
if (n < 2) return;

addattrib(0, "point", "pscale", 0.0);
addattrib(0, "prim", "is_main_stem", 0);

for (int i = 0; i < n; i++)
{
    vector Pi = point(0, "P", i);

    // local spacing from nearest neighbor
    int near2[] = nearpoints(0, Pi, 1e9, 2); // self + nearest
    if (len(near2) < 2) continue;

    int n1 = near2[1];
    vector P1 = point(0, "P", n1);
    float d1 = distance(Pi, P1);

    float tight = 1.0 / gap_mult;

    float max_len       = max(d1 * 0.48 * tight, 1e-4);
    float min_len       = d1 * 0.20;
    float clearance     = d1 * 0.22 * gap_mult;
    float safety_margin = d1 * 0.08 * gap_mult;
    float search_radius = d1 * 2.2;

    clearance     = max(clearance, d1 * 0.03);
    safety_margin = max(safety_margin, d1 * 0.01);

    // one random rotation per unit, but rays are evenly spaced
    float base_ang = rand(set(i, seed, 101)) * TWO_PI;

    int near[] = nearpoints(0, Pi, search_radius);

    setpointattrib(0, "pscale", i, d1 * 0.06, "set");

    for (int r = 0; r < rays_per_unit; r++)
    {
        // even angular distribution = no directional gaps
        float ang = base_ang + (float(r) / float(rays_per_unit)) * TWO_PI;

        // tiny jitter so it doesn't look too perfect
        ang += fit01(rand(set(i, r, seed + 17)), -0.08, 0.08);

        vector dir = normalize(set(cos(ang), 0.0, sin(ang))); // ZX plane

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

        // random desired length, collision-capped
        float ulen = rand(set(i, r, seed + 555));
        float len_bias = pow(ulen, 1.8); // bias toward shorter, occasional long
        float desired = fit(len_bias, 0.0, 1.0, min_len, max_len);

        if (rand(set(i, r, seed + 777)) < 0.10)
            desired *= 1.25;

        float L = min(allowed, desired);
        if (L < min_len * 0.35) continue;

        int tip = addpoint(0, Pi + dir * L);
        setpointattrib(0, "pscale", tip, d1 * 0.025, "set");

        int pr = addprim(0, "polyline", i, tip);
        setprimattrib(0, "is_main_stem", pr, 1, "set");
    }
}
```
