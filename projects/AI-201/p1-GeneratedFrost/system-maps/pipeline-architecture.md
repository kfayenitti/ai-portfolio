
## Map 2 - Pipeline Architecture



[SOURCE GEO: grid / surface]
        |
        v
[HOUDINI SOPs — VEX frost tool (AI-assisted, artist-owned)]
  Scatter → Wrangle1 → Wrangle2 → Resample → Facet → Wrangle3 (growth) → PolyWire
        |                    ^
        |                    |  [Claude: code + paramater guidance from prompts/refs]
        |                    +---- artist applies in wrangles
        |
        +--> [Playblast / slap render] ----------------------.
        |                                                       |
        |                                                      v
        |                                         [ComfyUI ideation — not final pixels]
        |                                          (lighting / comp / paint-over ideas)
        v                                                       |
[Karma/Mantra RENDER]                                           |
        |                                                       |
        v                                                       |
[NUKE COMP — artist-made]  <------------------------------------'
        |
        v
[FINAL: Houdini render + Nuke comp]