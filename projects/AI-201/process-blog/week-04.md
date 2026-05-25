# Week 4 — Process log


## Week 4, Session 1 — 04/14/26

### What I Did

This session, I began working on writing working VEX in Houdini for generating a single branch of frost using ClaudeAI.

### AI Interactions

- **Prompt:**

I am making a frost generation code in houdini. Begin by creating a code that makes a simple line, this is the main line of one branch of frost. have its length customizable. and have a pscale attribute ramping, so its thinner at the tip to later be polywired.

- **Output:**

```vex
// Parameters to create on the wrangle:
// float length = 1.0
// int segments = 20
// float pscale_root = 0.03
// float pscale_tip = 0.002
// ramp  pscale_ramp (0->1 along line)

float length      = chf("length");
int   segments    = chi("segments");
float pscale_root = chf("pscale_root");
float pscale_tip  = chf("pscale_tip");

segments = max(1, segments);

// Create one polyline primitive
int prim = addprim(0, "polyline");

for (int i = 0; i <= segments; i++)
{
    float u = float(i) / float(segments);   // 0 at root, 1 at tip
    vector pos = set(u * length, 0, 0);     // line along +X

    int pt = addpoint(0, pos);
    addvertex(0, prim, pt);

    // Ramp controls profile shape; base->tip values define absolute thickness range
    float r = chramp("pscale_ramp", u);
    float pscale = lerp(pscale_root, pscale_tip, r);
    setpointattrib(0, "pscale", pt, pscale, "set");
}
```

- **Decision:** This worked, and I continued to add on to this line. I fell into a repetition momentarily of slowly adding to this code, until it broke.
- **Tag:** @default
- **Prompt:**

awesome. now, in the same wrangle, adjust it to add branches to each segment point along it, like how frost has branches coming off the main stem. these should also be adjustable

- **Output:**

```vex
// DETAIL WRANGLE (Run Over: Detail only once)
//
// Create these parameters:
//
// Main stem
// float length = 1.0
// int   segments = 20
// float pscale_root = 0.03
// float pscale_tip  = 0.002
// ramp  pscale_ramp
//
// Branches
// int   branch_points_start = 1      // first stem segment index that can branch
// int   branch_points_end   = 20     // last stem segment index that can branch
// int   branches_per_point  = 2
// float branch_length       = 0.2
// float branch_length_rand  = 0.5    // 0-1, % variation
// int   branch_segments     = 4
// float branch_angle_deg    = 45.0   // away from stem
// float branch_angle_rand   = 20.0   // random angle variation
// float twist_rand_deg      = 180.0  // random spin around stem axis
// int   seed                = 1234
//
// Branch thickness
// float branch_pscale_mult_root = 0.6
// float branch_pscale_mult_tip  = 0.5

float length      = chf("length");
int   segments    = max(1, chi("segments"));
float p_root      = chf("pscale_root");
float p_tip       = chf("pscale_tip");

int bstart        = chi("branch_points_start");
int bend          = chi("branch_points_end");
int bpp           = max(0, chi("branches_per_point"));
float b_len_base  = chf("branch_length");
float b_len_rand  = max(0.0, chf("branch_length_rand"));
int bsegs         = max(1, chi("branch_segments"));
float b_ang       = radians(chf("branch_angle_deg"));
float b_ang_rand  = radians(chf("branch_angle_rand"));
float twist_rand  = radians(chf("twist_rand_deg"));
int seed          = chi("seed");

float b_pmul_root = chf("branch_pscale_mult_root");
float b_pmul_tip  = chf("branch_pscale_mult_tip");

// Build stem points first so we can branch from them
int stem_pts[];
resize(stem_pts, segments + 1);

for (int i = 0; i <= segments; i++)
{
    float u = float(i) / float(segments);
    vector pos = set(u * length, 0, 0); // stem along +X

    int pt = addpoint(0, pos);
    stem_pts[i] = pt;

    float r = chramp("pscale_ramp", u);
    float pscale = lerp(p_root, p_tip, r);
    setpointattrib(0, "pscale", pt, pscale, "set");
}

// Create stem polyline
int stem_prim = addprim(0, "polyline");
for (int i = 0; i <= segments; i++)
{
    addvertex(0, stem_prim, stem_pts[i]);
}

// Clamp branch range to valid segment indices
bstart = clamp(bstart, 1, segments);
bend   = clamp(bend,   1, segments);
if (bend < bstart)
{
    int tmp = bstart;
    bstart = bend;
    bend = tmp;
}

// Branches from each chosen stem point
for (int i = bstart; i <= bend; i++)
{
    vector rootP = point(0, "P", stem_pts[i]);

    // stem-local thickness at this point
    float uStem = float(i) / float(segments);
    float rStem = chramp("pscale_ramp", uStem);
    float stem_pscale_here = lerp(p_root, p_tip, rStem);

    for (int b = 0; b < bpp; b++)
    {
        float h = rand(set(i, b, seed));

        // length variation
        float len_jit = fit01(rand(set(i, b, seed + 17)),
                              1.0 - b_len_rand,
                              1.0 + b_len_rand);
        float blen = max(1e-4, b_len_base * len_jit);

        // random side: +Y or -Y
        float side = (rand(set(i, b, seed + 31)) < 0.5) ? -1.0 : 1.0;

        // base direction roughly perpendicular to stem (+/-Y)
        vector dir = normalize(set(0, side, 0));

        // tilt away from stem by branch_angle around Z
        matrix3 m_tilt = ident();
        rotate(m_tilt, side * b_ang, set(0,0,1));
        dir *= m_tilt;

        // random extra angle around Z
        float a_jit = fit01(rand(set(i, b, seed + 47)), -b_ang_rand, b_ang_rand);
        matrix3 m_jit = ident();
        rotate(m_jit, a_jit, set(0,0,1));
        dir *= m_jit;

        // random twist around stem axis (X)
        float t = fit01(rand(set(i, b, seed + 59)), -twist_rand, twist_rand);
        matrix3 m_twist = ident();
        rotate(m_twist, t, set(1,0,0));
        dir *= m_twist;

        dir = normalize(dir);

        // Build one branch polyline, rooted on stem point
        int bprim = addprim(0, "polyline");

        for (int j = 0; j <= bsegs; j++)
        {
            float ub = float(j) / float(bsegs);
            vector p = rootP + dir * (ub * blen);

            int bpt;
            if (j == 0)
            {
                // Reuse stem point so branch is welded to stem
                bpt = stem_pts[i];
            }
            else
            {
                bpt = addpoint(0, p);

                // branch pscale tapers using same ramp
                float rb = chramp("pscale_ramp", ub);
                float bp_root = stem_pscale_here * b_pmul_root;
                float bp_tip  = stem_pscale_here * b_pmul_tip;
                float bpscale = lerp(bp_root, bp_tip, rb);
                setpointattrib(0, "pscale", bpt, bpscale, "set");
            }

            addvertex(0, bprim, bpt);
        }
    }
}
```

- **Decision:** This began the pattern of code with syntax errors or problems with geometry generation.
- **Tag:** @resist

- **Prompt:**

they are still all converging. its not a viewport thing. try simply interpolating lines along each of the points. they should be parallel

- **Output (summary — full revised VEX not saved in this log):** The model changed how branch directions were built so side branches read as parallel offsets along the stem instead of collapsing toward one meeting point. That fixed the convergence in the viewport. **Tradeoff:** the new version did not keep a clean line on the far end of the main stem (tip segment / topology), so I continued with smaller follow-up prompts to patch that.
- **Decision:** I moved forward with this method of generation and began fixing its errors slowly with specific prompts and customizing further.
- **Tag:** @shift
- **Prompt:**

is it possible to turn this generated small branch of frost into an animated frost, so it is growing and generating these branches. similar to these videos

- **Output (conceptual plan — no implementation in this exchange):**

Yes, it’s absolutely possible, and your wrangle is a good base for it. You don’t have to throw the setup away—you add a time-driven “growth” control and tie geometry to that.

Idea in plain terms
One scalar over time — e.g. growth from 0 → 1 across the shot (from $FF, $T, or a CHOP/channel). That number is “how far along the frost the growth has reached.”
Stem first — only draw the main polyline up to the point where t <= growth (or fade in points by distance along the stem).
Branches after the stem passes — for each branch at stem parameter t_stem, only show it (or only extend its length) when growth has passed that t_stem. You can ease with a small overlap so the tip of the stem arrives slightly before the side arms pop.
Optional “stretch” — multiply each branch’s this_len by a factor like smooth(0,1, (growth - t_stem) / width) so arms grow outward over a few frames instead of appearing at full length.
All of that is just extra if / max / lerp / smooth logic around the loops you already have—same directions, same ramps, same jitter.

- **Decision:** I reviewed this plan, which makes sense, but wanted to see it in action with the code prior. There are a few things I would do differently, such as using $FF instead of keyframing it for control.
- **Tag:** @shift

### What I Learned

- VEX detail wrangles that build geometry in one pass are powerful, but small ordering mistakes (branch range, tangent frames, welding vs new points) show up immediately in the viewport as “wrong” topology.
- When branches looked like they were converging, the fix was not viewport settings—it was revisiting how directions were constructed (parallel offsets along the stem vs ad-hoc rotations).
- Planning growth as a single scalar over time (`growth` 0→1) is straightforward in theory; implementing it cleanly means deciding *when* each knot appears and how tip behavior is handled (I noted the tip-timing issue for later patches like in `generatedFrost_V02.md`).

### Quarter Question Connection

This week’s work sits directly under *What happens when generated code and AI-assisted imagery are used to streamline VFX production?* The AI is acting as a coding partner for procedural Houdini setup—faster iteration on VEX—but the artistic and technical decisions (parallel branches, growth order, what “wrong” looks like) stay mine. The friction (syntax errors, convergence bugs) is part of the record: generated code still needs testing and reframing in the actual DCC context.

### What's Next

- Solidify the single-branch frost wrangle with growth animation (`generatedFrost_V02.md`) and PolyWire look-dev.
- Pivot from “one hero branch” to **pattern / layout**: many frost units from scatter, spacing, and non-intersection—documented in [`GenerativeFrost_PatternGeneration_V04.md`](../p1-GeneratedFrost/GenerativeFrost_PatternGeneration_V04.md) and [`code/frost_wrangle_*.vfl`](../p1-GeneratedFrost/code/) (V01–V03 are earlier pattern iterations).
- Keep a short log of prompts that *failed* vs *worked* so Week 05 art-direction controls are grounded in what the code can actually support.



---

## Week 4, Session 2 — 04/15/26 (Wednesday)

### What I Did

This session, I continued to work on creating the frost pattern. After creating a code previously that functioned to create a small branch, I shifted to creating a system using Claude and Houdini VEX to generate the larger, repeated pattern.

Throughout the process I shifted my approach several times, noticing reoccuring errors or unsatisfying visuals.



### AI Interactions

- **Prompt:** this is the code i have right now for my frost generation. this creates one branch. i would like it to create more frost, that is laid out in units, like in the image provided. dont worry about animation right now. just think of a system to generate groups and have them laid out without intersecting
- **Output:**

I’ll turn this into a clustered “frost patch” generator: multiple frost units, each built from your existing stem/branch logic, then distributed with a non-overlap layout pass so units don’t intersect. I’m going to edit `generatedFrost_V02.md` with a new static VEX version and clear parameters for group count, spacing, and layout area.I found a clean way to keep your current branch style but replicate it as many times as needed: a two-stage wrangle (1) place unit roots with rejection sampling for spacing, then (2) build one full frost unit at each accepted root with per-unit random scale/orientation. I’m applying that now in the doc so you can paste directly into Houdini.

- **Decision:** 

Claude began to edit the .md directly after this, which I had to stop it from doing as I wanted to experiment before making a new .md version

- **Tag:** @resist


### Quarter Question Connection

This week helped further solidify how AI coding can be used in proceduralism and customized processes in Houdini VEX. I look forward to seeing where these softwares integrate AI, especially when it comes to coding.

### What's Next

Next week, I will wrap up the generative code for creating the frost procedural system. Then I will continue to investigate using generative AI to assist in the production pipeline as I bring the project to a completed visual.