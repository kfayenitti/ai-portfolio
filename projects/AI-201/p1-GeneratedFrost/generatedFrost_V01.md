## Initial version of the generated frost code

------

// Detail Wrangle (Run Over: Detail only once)
// Parameters:
// float main_length = 1.0
// int   interior = 5
// float branch_length = 0.2
// float branch_splay = 25.0            // degrees
// float branch_jitter_deg = 5.0        // random orientation jitter per branch (degrees)
// int   seed = 123
// ramp  pscale_ramp                    // thickness along main stem (0=root, 1=tip)
// ramp  branch_length_ramp             // branch length multiplier along stem (0=root, 1=tip)

float main_length = chf("main_length");
int interior = max(1, chi("interior"));
float branch_len = chf("branch_length");
float splay = radians(chf("branch_splay"));
float jitter = radians(chf("branch_jitter_deg"));
int seed = chi("seed");

vector p0 = set(0, 0, 0);
vector p1 = set(main_length, 0, 0);
vector up = set(0, 0, 1);

addattrib(0, "point", "pscale", 0.0);

int pt_ids[];
vector P[];

// Build main points: root + interior + tip
for (int i = 0; i <= interior + 1; i++)
{
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);

    int pt = addpoint(0, p);
    append(pt_ids, pt);
    append(P, p);

    setpointattrib(0, "pscale", pt, float(chramp("pscale_ramp", t)), "set");
}

// Main stem
int main_prim = addprim(0, "polyline");
for (int i = 0; i < len(pt_ids); i++)
    addvertex(0, main_prim, pt_ids[i]);

// Branches on points 1..interior+1 (includes tip)
for (int k = 1; k <= interior + 1; k++)
{
    vector curr_p = P[k];
    vector tangent;

    if (k == interior + 1)
        tangent = normalize(P[k] - P[k - 1]); // endpoint-safe tangent
    else
        tangent = normalize(P[k + 1] - P[k - 1]);

    vector side = cross(tangent, up);
    if (length(side) < 1e-6)
        side = set(0, 1, 0);
    side = normalize(side);

    // Slight random orientation jitter per branch
    float j_a = fit01(rand(set(k, 11, seed)), -jitter, jitter);
    float j_b = fit01(rand(set(k, 29, seed)), -jitter, jitter);

    float ang_a = splay + j_a;
    float ang_b = splay + j_b;

    vector dir_a = normalize(cos(ang_a) * side + sin(ang_a) * tangent);
    vector dir_b = normalize(-cos(ang_b) * side + sin(ang_b) * tangent);

    int base = pt_ids[k];
    float t_stem = float(k) / float(interior + 1);

    float root_ps = float(chramp("pscale_ramp", t_stem));
    float tip_ps  = float(chramp("pscale_ramp", 1.0));

    float len_mult = max(0.0, float(chramp("branch_length_ramp", t_stem)));
    float this_len = branch_len * len_mult;

    int pa = addpoint(0, curr_p + dir_a * this_len);
    setpointattrib(0, "pscale", base, root_ps, "set");
    setpointattrib(0, "pscale", pa, tip_ps, "set");
    addprim(0, "polyline", base, pa);

    int pb = addpoint(0, curr_p + dir_b * this_len);
    setpointattrib(0, "pscale", pb, tip_ps, "set");
    addprim(0, "polyline", base, pb);
}
