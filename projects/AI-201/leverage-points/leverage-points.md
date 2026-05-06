**Leverage Points**


**Surface Orientation**

This orients the frost to the surface the user inputs, making it realistically lie on the artists chosen geometry. It is a small and necessary detail, but complex to get functioning correctly, since it relies on calculating inputted normals and calculating them correctly with the equations to generate branches.

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




**Gap Multiplier**

This generates the parameter that lets the user control the gap between frost chunks. This code is not only fragile and easy to break, but can greatly determine the overall appearance as decided by the artist.

float tight = 1.0 / gap_mult;

float max_len       = max(d1 * 0.48 * tight, 1e-4);
float min_len       = d1 * 0.20;
float clearance     = max(d1 * 0.22 * gap_mult, d1 * 0.03);
float safety_margin = max(d1 * 0.08 * gap_mult, d1 * 0.01);
float search_radius = d1 * 2.2;





**Generation Randomization**

This is not a user input, but is just as important, as it does the opposite of artist tools: Provides randomization in order to avoid a generated and unnatural appearance. Generates random number to interpolate with base position of main branches in each chunk.

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





**Growth & Thickness Relation**

Layering relationships between parameters and attributes during animation for more realistic and natural blend between settings. These are the small details that you do not really notice are there, but notice when they are not.

float growth = clamp(chf("growth"), 0.0, 1.0);
float g = smooth(0.0, 1.0, growth);

// ... timing code omitted ...

float mature = pow(br, 0.7);

// ... point loop ...

float ramp_mul = chramp("pscale_ramp", u);
float pnew = max(base_ps * ramp_mul * mature, 1e-4);
setpointattrib(0, "pscale", pts[k], pnew, "set");
