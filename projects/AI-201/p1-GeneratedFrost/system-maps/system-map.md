# Generated Frost - System Map

INPUT
├── [User-inputted VEX tool parameters]
│   ├── [Wrangle 1: seed, gap_mult, rays_min, rays_max, rays_min / rays_max]
│   ├── [Wrangle 2: seed, twigs_amount, twig_len_mult, twig_splay_deg, twig_jitter_deg, clearance_mult, min_len_mult, twig_taper_ramp]
│   └── [Wrangle 3: growth, pscale]
└── [AI ideation inputs (Houdini Playblasts / Screenshots)]
    ├── [Text prompts]
    └── [Houdini playblasts / reference screenshots]

PROCESS
├── [Houdini VEX generation]
│   ├── [Wrangle 1: generate main branches from scatter points on source surface]
│   │   Rule: [parameters determine branch count, spacing, orientation, and start timing]
│   ├── [Wrangle 2: generate sub-branches from each main stem]
│   │   Rule: [parameters determine sub-branch amount, length, angle, jitter, and collision-safe placement - the overall appearance of sub-branches]
│   └── [Wrangle 3: animate shapes]
│       Rule: [parameters determine the timed creation of geometry]
└── [Post-processing]
    ├── [Resample + Facet for smooth independent deformation]
    └── [PolyWire for renderable thickness]

OUTPUT
├── [Procedurally generated frost geometry]
├── [Paramater controlled growth animation (keyframed via growth)]
│   └── [Customizable look via VEX parameters]
└── [AI-generated ideation imagery for look development]
