# Week 8 - Process log

---

## What I Did

This week, I continued to move towards rendering and finalizing the look of the frost.

Due to tech setbacks with downloading the ComfyUI link, I relied one last time on feeding screenshots into different models like Nano Banana and ChatGPT for visual feedback before rendering out a visual example of how the tool can be used.

### Week 8, Session 2 - [05/13/2026]

There were render errors in the frost

### AI INTERACTION

- **Prompt:** The render completed for the frost animation, but it is very glitchy. I think there is an error with the polywire or pscale? it did not occur in the viewport, only when rendering
- **Output:** If motion blur is ruled out, the next most plausible buckets are thin-geometry shading, time/expression evaluation, and PolyWire input changing in ways the GL hides.

1. Overlapping / co-planar tubes (z-fighting)

2. Transmission, opacity, or nested glass

3. Displacement or round curves (only on the render object)


4. $F vs $T and cooked frame alignment


5. Real pscale / topology pops (single-frame)

- **Decision:** I double checked all of these, and conerted geometry as well to be safe.
- **Tag:** @shift

I continued to use Claude to troubleshoot, and it reccomended checking polywire node and makign sure I keep some attributes and dont deleter all of them.



---

### Week 8, Session 1 - [05/11/2026]

- **Prompt:** render this frost on a window, render realistically
- **Output:** NanoBanana_Ideation_V01 in ideated_images folder
- **Decision:** This was the first time in a while it provided a sunny day image in the background. I had kind of moved past this appearance, but didnt mind what it provided, and chose to explore it a bit more
- **Tag:** @shift

- **Prompt:** render this frost on a window, render realistically. background is darkish, real environment
- **Output:** NanoBanana_Ideation_V02 in ideated_images folder
- **Decision:** The background was darker, but it felt a bin unnarual with how bright the frost is. I decided to try a mix of both results
- **Tag:** @shift

### What I Learned

This week was some final troubleshooting, and solving some sudden issues with rendering using Claude as a guide.


### What's Next

I will prepare presentables for the project and gather findings
