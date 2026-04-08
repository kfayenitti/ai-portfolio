## Week 3, Session 2 — 04/08/26

### What I Did
Continued organizing research and project intentions, including make/making/made board.

### AI Interactions

- **Prompt:** 

- **Output:** 

- **Decision:** 

- **Tag:** 


- **Prompt:** 

- **Output:** 

- **Decision:** 

- **Tag:** 

### What I Learned

### Quarter Question Connection

### What's Next



## Week 3, Session 1 — 04/07/26

### What I Did

This session, I mainly researched practitioners in the VFX industry who have implemented similar technologies to my desired project. I looked for practitioners in three different specialties:

- One who has created generated frost before in VEX - with or without Claude
- One who has used ClaudeAI in Houdini VEX to generate visuals
- One who has used ComfyUI specifically for VFX pipelines

I also organized my research, directories, and intentions for this project, using AI to help ideate explanations to later go back and adjust with my own specifications.

I also worked briefly on the prototype for the Frost code.

### AI Interactions

- **Prompt:** can you call back to the code we made to generate a line in houdini with 5 points on it, and lines interpolated onto those points?

- **Output:** Claude pulled up the previous code:
// Detail Wrangle
vector p0 = chv("point0");
vector p1 = chv("point1");
vector up = chv("up");
float branch_len = chf("branch_length");

const int interior = 5;
int stem_pts[];
vector stem_pos[];

append(stem_pts, addpoint(0, p0));
append(stem_pos, p0);

for (int i = 1; i <= interior; i++) {
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);
    append(stem_pts, addpoint(0, p));
    append(stem_pos, p);
}

append(stem_pts, addpoint(0, p1));
append(stem_pos, p1);

// main stem
int stem = addprim(0, "polyline", stem_pts[0], stem_pts[1]);
for (int i = 2; i < len(stem_pts); i++) addvertex(0, stem, stem_pts[i]);

// branch lines on each interior point
vector tangent = normalize(p1 - p0);
vector side = normalize(cross(up, tangent));

for (int i = 1; i <= interior; i++) {
    vector c = stem_pos[i];
    int a = addpoint(0, c - side * branch_len);
    int b = addpoint(0, c + side * branch_len);
    addprim(0, "polyline", a, b);
}

- **Decision:** I wanted to continue adjusting and adding parameters

- **Tag:** @shift



- **Prompt:** can you make the orientation/rotation of the interpolated lines adjustable? like frost

- **Output:** Claude adjusted the previous code:
// ----- Inputs / controls -----
vector p0 = chv("point0");
vector p1 = chv("point1");
vector up = normalize(chv("up"));               // reference up, e.g. {0,1,0}

int   interior      = chi("interior_points");   // e.g. 5
float branch_len    = chf("branch_length");     // branch size
float roll_deg      = chf("roll");              // rotates branch plane around stem
float spread_deg    = chf("spread");            // opening angle away from perpendicular
float twist_total   = chf("twist_total");       // extra roll from start->end
float rand_amp_deg  = chf("random_angle");      // random jitter per point
int   seed          = chi("seed");

// ----- Build stem points -----
int stem_pts[];
vector stem_pos[];

append(stem_pts, addpoint(0, p0));
append(stem_pos, p0);

for (int i = 1; i <= interior; i++)
{
    float t = float(i) / float(interior + 1);
    vector p = lerp(p0, p1, t);
    append(stem_pts, addpoint(0, p));
    append(stem_pos, p);
}

append(stem_pts, addpoint(0, p1));
append(stem_pos, p1);

// Stem polyline
int stem = addprim(0, "polyline", stem_pts[0], stem_pts[1]);
for (int i = 2; i < len(stem_pts); i++)
    addvertex(0, stem, stem_pts[i]);

// ----- Stable local frame -----
vector tangent = normalize(p1 - p0);

// If up is parallel to tangent, pick fallback axis
if (abs(dot(up, tangent)) > 0.999)
    up = {1,0,0};

vector side = normalize(cross(up, tangent));    // local X
vector nrm  = normalize(cross(tangent, side));  // local Y

// ----- Branches on interior points -----
for (int i = 1; i <= interior; i++)
{
    float u = float(i) / float(interior + 1);

    // Per-point orientation controls
    float twist_here = radians(roll_deg + twist_total * u);
    float jitter     = radians(fit01(rand(set(i, seed, 17.123)), -rand_amp_deg, rand_amp_deg));
    float rotA       = twist_here + jitter;

    // Rotate side/nrm around stem tangent (quaternion)
    vector4 q = quaternion(rotA, tangent);
    vector side_r = qrotate(q, side);
    vector nrm_r  = qrotate(q, nrm);

    // Spread tilts branches toward +tangent / -tangent
    float s = radians(spread_deg);
    vector dirL = normalize(side_r * cos(s) + tangent * sin(s));
    vector dirR = normalize(-side_r * cos(s) + tangent * sin(s));

    vector c = stem_pos[i];
    int a = addpoint(0, c + dirL * branch_len);
    int b = addpoint(0, c + dirR * branch_len);

    addprim(0, "polyline", c, a);
    addprim(0, "polyline", c, b);
}

- **Decision:** This returned an error message. Realized Claude needs a lot more instruction and customization, and can't make too large of strides without breaking

- **Tag:** @resist

### What I Learned 

Gathered more research and information to guide throughout project through industry practitioners. Also experimented with Claude's limits with VEX

### Quarter Question Connection

Industry-related practitioners. Claude-generated code for Frost

### What's Next

Begin to develop Frost code in-depth and guiding Claude to generate an operating tool. Use research from today in process.

