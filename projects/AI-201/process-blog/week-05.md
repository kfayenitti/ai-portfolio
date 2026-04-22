# Week 5 - Process log

---

## Week 5, Session 2 - 04/22/26

### What I Did

This week was dedicated to finishing the Claude-generated code for the Houdini VEX Frost generation code.

I polished up the code, and then began using it to create a visual. In order to do this, I inquired with Claude what parameter customizations can be best used to achieve my desired layout of frost. After using it's reccomendations, I then further customized the tool to generate a desired animation and procedural generation of frost.

From there, I began ideating for how to develop the final visual outcome. I began using different image generation models in Gemini, ChatGPT, and Claude, to brainstorm composition ideas.

I intend to continue ideating using ComfyUI.

### AI Interactions

- **Prompt:** (gemini) this is a model of frost in a 3d software. ideate what this composition can look like rendered on a window
- **Output:** Gemini Ideation V03 in ideated_images
- **Decision:** 
- **Tag:** @resist

- **Prompt:** (chatgpt) this is a model of frost in a 3d software. ideate what this composition can look like rendered on a window
- **Output:** ChatGPT_Ideation_V01 in ideated_Images
- **Decision:** 
- **Tag:** @shift

- **Prompt:** (figma weavy + seedance) generated a first frame, edited toward a last frame, then generated a short transition video from both frames
- **Output:** `research/Figma_Weave_Seedance_TestVideo_V01`
- **Decision:** 
- **Tag:** @default

---

## Week 5, Session 1 - 04/20/26

### AI Interactions

- **Prompt:** The latest issue is an error with the Growth parameter. some of the branches growth works well, but other times, some branches begin having their sub branches grow PRIOR to the main branch growing. the subbranches should all only start growing once their main branch grows
- **Output:**
your timing logic in Wrangle 2 is currently based on when the parent stem starts, not when the stem has grown far enough to reach the twig’s attachment point.

That’s why some twigs can start early.
...
- **Decision:** I applied this fix, which worked, but it created a snapping effect 
- **Tag:** @default

- **Prompt:** this is working, but there is a bit of a snap in the animtion on that last frost, and its movement is not as gradual as the rest when it grows its subbranches. 
- **Output:**
Your Wrangle 3 uses:

float br = clamp((growth - gu) / max(1e-5, 1.0 - gu), 0.0, 1.0);
If gu is near 1.0 (like 0.99), then 1.0 - gu is tiny, so the branch reveals very fast at the end.

Fix (best result): add a minimum reveal window
Use this updated Wrangle 3:
// Wrangle 3 — Detail only once — carve-style growth, single parameter
// Requires on each polyline prim: grow_u, rest_root, rest_tip, prim_kind

float growth = clamp(chf("growth"), 0.0, 1.0);

// New controls
float min_reveal_window = chf("min_reveal_window"); // try 0.06 to 0.12
float ease_power = chf("ease_power");               // try 1.0 to 1.6

int npr = nprimitives(0);

for (int pr = 0; pr < npr; pr++)
{
    float gu = clamp(prim(0, "grow_u", pr), 0.0, 0.999);

    vector rootP = prim(0, "rest_root", pr);
    vector tipP0 = prim(0, "rest_tip", pr);

    // Prevent ultra-short end-window snaps
    float window = max(1.0 - gu, min_reveal_window);

    float br = clamp((growth - gu) / window, 0.0, 1.0);
    br = smooth(0.0, 1.0, br);
    br = pow(br, ease_power); // optional artistic control

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
Add these parameters to Wrangle 3:

min_reveal_window (float): start at 0.08
ease_power (float): start at 1.2

- **Decision:** This created new parameters on the wrangle creating the growth animation, which I did not want - they also did not work very well.
- **Tag:** @resist

- **Prompt:** now the branches arent finishing, they are getting cut short before growing all the subbranches
- **Output:**That happened because my previous fix could make br < 1 at growth=1 for very late branches, so those branches never fully reached tip.

Use this corrected Wrangle 3 (still only one parameter: growth):
// Wrangle 3 — Detail only once — carve-style growth, single parameter
// Requires on each polyline prim: grow_u, rest_root, rest_tip
// Input: after Resample + Facet (Unique Points ON)

float growth = clamp(chf("growth"), 0.0, 1.0);

// Optional global smoothing of the single growth control
float g = smooth(0.0, 1.0, growth);

int npr = nprimitives(0);

for (int pr = 0; pr < npr; pr++)
{
    float gu = clamp(prim(0, "grow_u", pr), 0.0, 0.999);

    vector rootP = prim(0, "rest_root", pr);
    vector tipP0 = prim(0, "rest_tip", pr);

    // Guarantee a minimum reveal span by starting late branches a bit earlier,
    // but ALWAYS finish at growth=1.0
    float min_window = 0.08;
    float start_u = min(gu, 1.0 - min_window);   // shift start earlier if needed
    float window  = max(1e-5, 1.0 - start_u);    // always reaches full by end

    float br = clamp((g - start_u) / window, 0.0, 1.0);
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
- **Decision:** This worked well, and I moved on to the next issue to address.
- **Tag:** @default

- **Prompt:** can we make it so they begin to grow frost at different paces? right now, each unit chunk of frost begins to grow at once. however, it would be nice to see it staggered, or the growth being triggered by the ones near it beginning to grow
- **Output:**Yes — this is a great next step.

Right now your Wrangle 1 gives each scatter point similar timing structure, so many “frost islands” feel synchronized.
The clean fix is to make each scatter point get its own start time based on distance from a trigger point (wave propagation) plus a little random jitter (stagger), then write that into stem grow_u.

Use this full Wrangle 1 replacement:
- **Decision:** This worked a bit, but was not very noticable. I asked for it to create a parameter, which it did, but then had to inquire that the parameter not be clamped at 1 and allow for exaggeration.
- **Tag:** @shift

- **Prompt:** is there any way to have pscale related to when they have started growing? so they get wider as they grow more?
- **Output:**
Yes — and it works really well for frost.

You can drive pscale by each branch’s local growth amount (br), so branches are thin when they first appear and thicken as they mature.

Use this Wrangle 3 (single growth parameter, plus your pscale_ramp):
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

    // per-branch growth progress (0..1)
    float br = clamp((g - gu) / max(1e-5, 1.0 - gu), 0.0, 1.0);
    br = smooth(0.0, 1.0, br);

    // thickness maturity curve: starts very thin, thickens as branch matures
    float mature = pow(br, 0.7); // lower = thickens sooner, higher = thickens later

    int pts[] = primpoints(0, pr);
    int m = len(pts);
    if (m < 2) continue;

    for (int k = 0; k < m; k++)
    {
        float u = float(k) / float(m - 1);

        // carve position
        float u_clamped = min(u, br);
        vector Pnew = lerp(rootP, tipP0, u_clamped);
        setpointattrib(0, "P", pts[k], Pnew, "set");

        // pscale = original pscale * shape along branch * growth maturity
        float base_ps = point(0, "pscale", pts[k]);
        float ramp_mul = chramp("pscale_ramp", u);
        float pnew = base_ps * ramp_mul * mature;

        // keep a tiny non-zero floor for PolyWire stability
        pnew = max(pnew, 1e-4);
        setpointattrib(0, "pscale", pts[k], pnew, "set");
    }
}
- **Decision:** This worked well and I implemented it in to the code
- **Tag:** @default

After getting a functioning, satisfactory version of the frost generation code, I moved on to ideating for the final image. I turned to Gemini and ChatGPT briefly.

- **Prompt:** (gemini) ideate visuals for a project with a frost growing procedural animation on a window. generate a snowy scenery and ideate things that could be outside the window. the frost is the main focus in the foreground, growing on a window, but there are other details in the scene creating a snowy, wintery atmosphere
- **Output:** Gemini Ideation V01 in ideated_images
- **Decision:** This helped picture how the frost can look, but I did not like the composition or content of this ideation 
- **Tag:** @shift

- **Prompt:** (gemini) make another version, think of something other than a cabin. maybe a different angle on the window, too?
- **Output:** Gemini Ideation V02 in ideated_images
- **Decision:** I liked the content of this scenery a bit better, but still did not like the composition. the high angle outside the window gives a sense of distance from the environment and feeling of superiority, while i was hoping for a more casual, cozy, subtle exterior.
- **Tag:** @resist


### What I Learned

This session gave me further direction on the look and composition of the frost visual using AI generated references. I also experimented with attempting to achieve visuals in Houdini to be accurate to a reference.


### What's Next

- Next week I will dive further into finalizing the imagery. I will solidify textures and layout of the project
- I will also decide how I would like the background to look, and how I will use AI in its generation

### Quarter Question
I began to experiment with how models other than Claude can be used in the VFX pipeline, specifically in concept generation and pre-visualization of imagery.

