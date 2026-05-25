# Week 6 - Process log

---

## What I Did

This week I focused on:

- Researched Houdini MCP and AI Integrated Assistance (as I move towards end of pipeline and product finalization)
- Presentation of tool
- Using AI generation for ideation - and visually matching ideation in Houdini


### AI Interactions

### Week 6, Session 1 - 04/27/2026

#### AI Interactions

- **Prompt:** what parameters can i use in houdini karma material x to make a texture that renders this frost with that appearance


- **Output:**
base                    0.05–0.1      (ice is mostly specular, not diffuse)
base_color              #ccdeff       (desaturated blue-white)
diffuse_roughness       0.3

specular                1.0
specular_color          #ffffff
specular_roughness      0.08–0.12     (slightly rough — frost ≠ polished ice)
specular_IOR            1.31          (real ice IOR)
specular_anisotropy     0.3–0.45      (crystal structure causes anisotropic glint)
specular_rotation       drive from noise or AO

coat                    0.6
coat_roughness          0.05
coat_IOR                1.31

subsurface              0.4–0.6
subsurface_color        #a8cce8       (deeper blue for SSS)
subsurface_radius       0.15 0.2 0.3  (RGB, blue channel wider = ice tint)
subsurface_scale        0.08

thin_walled             1             (arms are thin — use thin_film instead of volume SSS)
thin_film_thickness     180–320 nm    (iridescence, subtle)
thin_film_IOR           1.31
- **Decision:** This was a very good start and brought up ideas for texturing I had not done yet.I adjusted a few parameters such as increasing transmission and adding displacement
- **Tag:** @shift

- **Prompt:** (chatGPT) imagine what this frost model could look like rendered, textured, and lit
- **Output:** in ideated_images/Chat_Ideation_V01
- **Decision:** This was a very nice reference. I used to ask Claude how to achieve these materials
- **Tag:** @shift

- **Prompt:** (gemini)  imagine what this frost model could look like rendered, textured, and lit
- **Output:** in ideated_images/Gemini_Ideation_V06
- **Decision:** This was a very nice reference. I used to ask Claude how to achieve these materials
- **Tag:** @default

### What I Learned

This week I learned:

- Continued research on how to bring projects through end of pipeline using AI tools
- Continued finalizing appearance of tool-generated frost using guidance from AI imagery

### What's Next

- Continue finalizing appearance of frost using AI guidance and ideation
- 

### Quarter Question

This week I shifted to exploring AI integration in parts of the VFX pipeline other than tool creation and coding assistance, learning of ways to integrate it into softwares and guide artists visually.




---

### Week 6, Session 2 - 04/29/2026

### RESEARCH

This week, I continued to research Houdini MCP's and what people in the community are creating to integrate different models and systems into the software itself, especially with end-of-pipeline workflows.

I am looking into integrating these into my project, but am facing some roadblocks with expenses and technical capabilities.

- **Houdini AI Assistant**
- Created by  Radu Cius
- https://rart.gumroad.com/l/HoudiniAIAssistant
- Puts ChatGPT, Claude, and Deepseek directly into Houdini
- Generates VEX and can analyze workflow
- Costs $129


- **Houdini ComfyUI Bridge**
- Created by Rafael Drelich Valentim and Anatolii Iudanov
- https://www.sidefx.com/products/houdini/pipeline-ai/machine-learning-ai/
- https://github.com/CapybaraCrowporation/houdini-comfyui-bridge/commit/e686444b2d89cdaeb19d06e46bdaf84ba4c3b1e1
- Puts ComfyUI in Houdini Cops
- Can link with SOPS / geometry creation
- Generate images in COPS
- Example uses mo-cap driven by AI


I also continued to apply the AI guidance on materials from last session, and adjusted lights and parameters to match the imagery generated in ideated_images.