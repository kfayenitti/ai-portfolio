
## Week 2, Session 2 — 04/03/2026

### What I Did
I continued to narrow down the workflow for my desired project, and document findings along the way. Having settled on using ClaudeAI for coding in Houdini VEX, I began testing out its effectiveness with the language using prompts that slowly increased in their complexity. This helped me understand its way of working and allowed for easier troubleshooting.


- **Prompt:** generate a code in houdini that makes a line by connecting two points with customizable positions

- **Output:** Cursor suggested a **Detail** Attribute Wrangle using `chv("point0")` / `chv("point1")`, `addpoint`, and `addprim(..., "polyline", ...)`.

```vex
vector pos0 = chv("point0");
vector pos1 = chv("point1");

int pt0 = addpoint(0, pos0);
int pt1 = addpoint(0, pos1);

int prim = addprim(0, "polyline", pt0, pt1);
```

- **Decision:** Baseline geometry for a controllable stem; parameters live on the wrangle node.

- **Tag:** @shift


- **Prompt:** add five points interpolated along the line, between the two points

- **Output:** Five interior points at \(t = i/6\) for \(i = 1..5\), one polyline through all vertices.

```vex
vector p0 = chv("point0");
vector p1 = chv("point1");

const int interior = 5;

int pt_ids[];
append(pt_ids, addpoint(0, p0));

for (int i = 1; i <= interior; i++) {
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);
    append(pt_ids, addpoint(0, p));
}

append(pt_ids, addpoint(0, p1));

int prim = addprim(0, "polyline", pt_ids[0], pt_ids[1]);
for (int i = 2; i < len(pt_ids); i++) {
    addvertex(0, prim, pt_ids[i]);
}
```

- **Decision:** Even spacing along the segment for joints where branches can attach.

- **Tag:** @shift


- **Prompt:** on each of the points created in the middle, add two lines branching out on either side, like frost would, or a plant, or tree branches

- **Output:** At each interior point, tangent from neighbors; `cross` with `up` for a perpendicular “side” axis; two branch polylines; optional `branch_splay` to tilt arms along the stem.

```vex
vector p0 = chv("point0");
vector p1 = chv("point1");
vector up = chv("up");
float branch_len = chf("branch_length");
float splay = radians(chf("branch_splay"));

const int interior = 5;

int pt_ids[];
vector P[];

append(pt_ids, addpoint(0, p0));
append(P, p0);

for (int i = 1; i <= interior; i++) {
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);
    append(pt_ids, addpoint(0, p));
    append(P, p);
}

append(pt_ids, addpoint(0, p1));
append(P, p1);

{
    int prim = addprim(0, "polyline", pt_ids[0], pt_ids[1]);
    for (int i = 2; i < len(pt_ids); i++)
        addvertex(0, prim, pt_ids[i]);
}

for (int k = 1; k <= interior; k++) {
    vector prev_p = P[k - 1];
    vector curr_p = P[k];
    vector next_p = P[k + 1];
    vector tangent = normalize(next_p - prev_p);

    vector side = cross(tangent, normalize(up));
    if (length(side) < 1e-6)
        side = cross(tangent, {1, 0, 0});
    side = normalize(side);

    vector dir_a = normalize( cos(splay) * side + sin(splay) * tangent);
    vector dir_b = normalize(-cos(splay) * side + sin(splay) * tangent);

    int base = pt_ids[k];

    int pa = addpoint(0, curr_p + dir_a * branch_len);
    addprim(0, "polyline", base, pa);

    int pb = addpoint(0, curr_p + dir_b * branch_len);
    addprim(0, "polyline", base, pb);
}
```

- **Decision:** Starting point for a procedural frost / branch pattern in Houdini; I will test in my scene and adjust parameters (`up`, length, splay) and fold into the capstone tool as needed. As it gets more complex, it will need further instruction. This system works well for a basic branching tool, but it needs to handle more layers and movement—it glitches and breaks when parameters are pushed in certain directions. Claude also needs clearer guidance on VEX syntax; for example, it used `const` in patterns that VEX does not support (e.g., before type declarations).

- **Tag:** @shift


### What I Learned
These experiences helped me better understand the different models commonly used for VFX in the industry, and how to connect them in practice. They gave me insight into API keys and MCP setups. They also showed me the visual limits of different models and different model styles, and helped me practice troubleshooting.

### Quarter Question Connection
This connects to the quarter question as it clarifies what models may be helpful for what parts of the VFX pipeline, and how to integrate them properly. Prototyping procedural VEX in Cursor (line, subdivision, branches) adds another angle: AI-assisted coding can streamline setup while parameters stay artist-driven, without replacing final look development or creative choices.

### What's Next
I will be narrowing down my concept for Project 1. I am leaning towards using AI-generated code from claude at first to create a procedural work of art, likely frost. At the same time, I will continue to familiarize myself with generative models in ComfyUI to later down the line use them to bring a visual effects project to completion through iteration and ideation. 

I am using these tools because they both tie into some of the most common uses of AI in the vfx industry: Streamlined coding, and visual iteration. ClaudeAI for code was chosen due to its familiarity and more common success with Houdini VEX, which is a C++-like language customized to Houdini's software. While it at times confuses syntax, as seen with its use of "const" as a variable when Houdini VEX does not use that, it often remembers corrections well. 

Alongside Claude, ComfyUI is widely used in VFX because it makes many model types easy to access—especially ones useful for VFX, such as model generation, lighting changes, rotoscoping, and comp / layer separation. That gives me flexibility through the pipeline and lets me match tools to specific needs. It also links with Claude effectively.


## Week 2, Session 1 — 03/31/26

### What I Did
This week I continued to research different tools and their applications. After developing ideas for AI-generated coding projects in week 1, I shifted focus to researching more generative models. I began researching how generative AI could be used for streamlining parts of pipelines such as:

* Quick concept iteration
* Face-cam character pose live link
* Render and texture pre-visualization
* Relighting
* Replacement / Paint-overs
* Roto

I linked ComfyUI to Claude on my device by adding an MCP server and linking to an API key. I experimented below with generating an image with a ComfyUI model prompted solely through Claude to ensure the link worked.

Later in the week (04/03), I used Cursor to iterate on Houdini VEX for a procedural polyline with interior points and paired side branches, toward a frost / plant / branch look.

### AI Interactions

- **Prompt:** List the available models in my ComfyUI

- **Output:** Claude listed the files in my root, Checkpoints, LoRAs, Text Encoders, VAE, and Diffusion Models folders

- **Decision:** This was to test if ClaudeAI on my laptop could connect with my directories and ComfyUI. This proved that it could find the directory and my installed models.

- **Tag:** @shift


- **Prompt:** I have the Z-Image model. The files are in the correct folders. Build me a Z-Image text to image workflow and generate a photo of a sunset over the ocean.

- **Output:** Claude successfully connected to ComfyUI and my models from behind the scenes in my ComfyUI interface, and set up a model and prompt to render. The render in ComfyUI took around an hour and a half.

- **Decision:** This was to test if Claude could connect to Comfy, my models, and successfully queue up an image to render. It succeeded, but since I am on my laptop it took very long.

- **Tag:** @shift


- **Prompt:** Italy Venice Waterway. 3D render. Make render realistic. Maintain composition and colors. Add boat in the water. Boat in Venice waterway. Brown, small boat. Row boat in Venice waterway. Calm waters. Sunny day

- **Output:** Runway added the boat without touching any other part of the provided render.

- **Decision:** This was a test to see if Runway (Gen-4 Turbo) could alter a rendered image and add animation to it without compromising its integrity. The provided rendered image is a 3D render I had created in Houdini, completely without the use of generative AI. It successfully followed the task, but not to a level satisfactory for production (simple textures on the boat, poor light interactions, odd movement, composition does not lead the eye, no glass interaction, etc.).

- **Tag:** @shift

