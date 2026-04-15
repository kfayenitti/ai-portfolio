# Generated Frost — V02

Procedural frost stem + paired side branches + **growth animation** in a single **Detail Wrangle** (Run Over: **Detail only once**).

V02 fixes tip branches disappearing when `growth` tops out at 1: the slider stays **0→1**, but internally **`g_branch = growth × (1 + branch_grow)`** so tip knots (`t_stem == 1`) get a real extension phase like every other branch. Stem uses **`g_stem = min(g_branch, 1)`**.

## Parameters (create on the wrangle)

| Name | Type | Notes |
|------|------|--------|
| `main_length` | float | Main stem length along +X |
| `interior` | int | Number of interior subdivisions (root + interior points + tip) |
| `branch_length` | float | Base branch reach |
| `branch_splay` | float | Splay angle in degrees |
| `branch_jitter_deg` | float | Random orientation jitter per branch (degrees) |
| `seed` | int | Random seed |
| `pscale_ramp` | float ramp | Thickness along stem (0 = root, 1 = tip) for polywire |
| `branch_length_ramp` | float ramp | Branch length multiplier along stem |
| `growth` | float | **0→1** over the shot (do not multiply by `1+branch_grow` in expressions; wrangle handles it) |
| `branch_grow` | float | Branch extension window in **g_branch** space (try `0.08`–`0.2`) |

## Driving `growth`

Examples (keep **0→1**):

- Linear: `($FF - 1) / max($FEND - 1, 1)`
- Eased: `smooth(0, 1, ($FF - 1) / max($FEND - 1, 1))`

## VEX

```vex
// Detail Wrangle (Run Over: Detail only once)
// Key "growth" on 0..1. Internally stretches branch timeline so tip can finish like other knots.

float main_length = chf("main_length");
int interior = max(1, chi("interior"));
float branch_len = chf("branch_length");
float splay = radians(chf("branch_splay"));
float jitter = radians(chf("branch_jitter_deg"));
int seed = chi("seed");

float branch_grow = max(1e-5, chf("branch_grow"));
float u = clamp(chf("growth"), 0.0, 1.0);

float g_branch = u * (1.0 + branch_grow);
float g_stem   = min(g_branch, 1.0);

vector p0 = set(0, 0, 0);
vector p1 = set(main_length, 0, 0);
vector up = set(0, 0, 1);

addattrib(0, "point", "pscale", 0.0);

int pt_ids[];
vector P[];

for (int i = 0; i <= interior + 1; i++)
{
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);

    int pt = addpoint(0, p);
    append(pt_ids, pt);
    append(P, p);

    setpointattrib(0, "pscale", pt, float(chramp("pscale_ramp", t)), "set");
}

int main_prim = addprim(0, "polyline");
for (int i = 0; i <= interior + 1; i++)
{
    float t = float(i) / float(interior + 1);
    if (t <= g_stem + 1e-7)
    {
        addvertex(0, main_prim, pt_ids[i]);
    }
    else
    {
        if (i > 0)
        {
            float t0 = float(i - 1) / float(interior + 1);
            float t1 = t;
            if (g_stem > t0 && g_stem < t1 - 1e-7)
            {
                float f = (g_stem - t0) / (t1 - t0);
                vector Ppart = lerp(P[i - 1], P[i], f);
                float tpart = lerp(t0, t1, f);
                int ptg = addpoint(0, Ppart);
                setpointattrib(0, "pscale", ptg, float(chramp("pscale_ramp", tpart)), "set");
                addvertex(0, main_prim, ptg);
            }
        }
        break;
    }
}

for (int k = 1; k <= interior + 1; k++)
{
    float t_stem = float(k) / float(interior + 1);

    if (g_stem + 1e-6 < t_stem)
        continue;

    float br = clamp((g_branch - t_stem) / branch_grow, 0.0, 1.0);
    br = smooth(0.0, 1.0, br);

    vector curr_p = P[k];
    vector tangent;

    if (k == interior + 1)
        tangent = normalize(P[k] - P[k - 1]);
    else
        tangent = normalize(P[k + 1] - P[k - 1]);

    vector side = cross(tangent, up);
    if (length(side) < 1e-6)
        side = set(0, 1, 0);
    side = normalize(side);

    float j_a = fit01(rand(set(k, 11, seed)), -jitter, jitter);
    float j_b = fit01(rand(set(k, 29, seed)), -jitter, jitter);

    float ang_a = splay + j_a;
    float ang_b = splay + j_b;

    vector dir_a = normalize(cos(ang_a) * side + sin(ang_a) * tangent);
    vector dir_b = normalize(-cos(ang_b) * side + sin(ang_b) * tangent);

    int base = pt_ids[k];

    float root_ps = float(chramp("pscale_ramp", t_stem));
    float tip_ps  = float(chramp("pscale_ramp", 1.0));

    float len_mult = max(0.0, float(chramp("branch_length_ramp", t_stem)));
    float this_len = branch_len * len_mult * br;
    if (this_len < 1e-8)
        continue;

    int pa = addpoint(0, curr_p + dir_a * this_len);
    setpointattrib(0, "pscale", base, root_ps, "set");
    setpointattrib(0, "pscale", pa, tip_ps, "set");
    addprim(0, "polyline", base, pa);

    int pb = addpoint(0, curr_p + dir_b * this_len);
    setpointattrib(0, "pscale", pb, tip_ps, "set");
    addprim(0, "polyline", base, pb);
}
```

## Notes

- Feed into **PolyWire** using `pscale` for radius.
- **V01** (`generatedFrost_V01.md`) is the static snapshot (no growth). **V02** adds animation with correct tip behavior.
- If tip arms still look short on the last frame, confirm **`growth` reaches 1.0** and **`branch_grow`** is not huge (very large values compress the tail of the internal timeline).
