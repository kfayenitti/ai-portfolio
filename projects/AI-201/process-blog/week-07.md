# Week 7 - Process log

---

## What I Did

This week, I looked more into downloading and setting up the Houdini and ComfyUI linker by CapybaraCrowporation. I managed to connect it correctly, and have access to the ComfyUI nodes in Houdini. However, I would like to try on a stronger computer, as the models are taking long to run on my laptop.

During the second session, I looked through Professor feedback on my repo and applied critique.

### Week 7, Session 1 - [05/06/2026]

This session, I mainly organized my repo to the provided feedback.

As part of that, I did a breaking pass.

**Breaking Pass**

Changing Source Geometry:

This code was intended to function on a flat plane, but I experimented with complexity of of the base geo to see how the code would react.

When provided a sphere, it does not react naturally. The branches do not themselves stick, but it orients with the side of the sphere its on, adding spike-like appearances to the ball.

On more polygonal shapes like a cube, it functions better, since they have flat sides that the frost does not have to bend to. It orients correctly to be parallel with the side its on. The smaller and more numerous the frost, the better it looks, as the edge overhang is lss noticable.

However, since the code is not structed to calculate when a 3D shape's plane ends, it does not cut off as it reaches the end of objects, leading the frost to stick off the sides. With simple shapes like cubes this may be able to be fixed after generation.

But overall, the code functions best on a flat plane, mimicking shapes like a window or undisturbed water.

**GAP_MULT**

The gap_mult parameter in Wrangle 1 is a very sensitive parameter that allows overlap in frost units. It is very easy to create drastic overlap. However, this may be an artistic preference for some, so although it is sensitive I do not consider it broken.

**UNIT_STAGGER**

unit_stagger parameter in Wrangle 1 does not appear to do anything until the other wrangles are added, which may confuse users if they are working directly down the pipeline instead of visualizing the final output.

**Twig Splay and Jitter Degree**

The twig splay and jitter degree parameter naturally generates a control bar beteween values of 0-1. However, since this works in degrees, it needs much higher input to show change. If the user is not familiar with how degrees work, they may be confused as to why this parameter does not show much change.

This could maybe be adjusted by clamping the values and translating a 0-1 scale in degrees? but may lead to further confusion.

**Non-VEX Nodes**

The artist using this tool needs to understand not to touch or move the non-vex nodes in between and after the VEX Wrangles. These are essential to processing geometry and preparing the outputted pattern for converting to mesh.

After conducting these tests, I organized the file to send to other VFX artists to play test.


### AI Interactions

### Week 7, Session 1 - [05/04/2026]

#### AI Interactions

- **Prompt:** [Add your prompt here]
- **Output:** [Add the response, generated image set, or code notes]
- **Decision:** [What you used, changed, or rejected and why]
- **Tag:** @default

- **Prompt:** [Add your prompt here]
- **Output:** [Add the response, generated image set, or code notes]
- **Decision:** [What you used, changed, or rejected and why]
- **Tag:** @default

---

### Week 7, Session 2 - [MM/DD/2026]

### RESEARCH

### What I Learned

This week I learned:

### What's Next

### Quarter Question

