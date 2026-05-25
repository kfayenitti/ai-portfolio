# Week 7 - Process log

---

## What I Did

This week, I looked more into downloading and setting up the Houdini and ComfyUI linker by CapybaraCrowporation. I managed to connect it correctly, and have access to the ComfyUI nodes in Houdini. However, I would like to try on a stronger computer, as the models are taking long to run on my laptop. I installed release tag v0.6.6 (commit e686444b2d89cdaeb19d06e46bdaf84ba4c3b1e1).

I used ClaudeAI throughout this process to guide the installation and troubleshoot when things were not connecting correctly.

During the second session, I looked through Professor feedback on my repo and applied critique.

Over the weekend, I downloaded the ComfyUI Houdini link on my PC as well.

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

---


---

### Week 7, Session 2 - [05/08/2026]

This session, I spent the time organizing my repo according to Professors feedback. 

This included polishing position statement, making a document for leverage points, making a records of resistance documents, and adjusting the CLAUDE.md - as well as other cleanups.

I also set up the document for user testing, and provided the tool to friends to see how they utilized it, and discovered the following issues after their testing:

Testers:

Amelia McPartlin - ILLU
Eli Porter - GAME
Syd Relkin - VFX

- Degree sliders are confusing

I addressed this during my own break test, but it is confusing with the sliders for degree parameters being from 0-1, when they need much higher values to show visible change.

Code can not adjust parameter values directly, but I can adjust the wrangles myself before providing the tool to others. I can also add sticky notes to indicate this to users.


- Clearance multiplier is confusing when working with length multiplier

Since clearance mult is based on length, some users got confused when clearance mult was high, and then length mult was adjusted. This caused the branches to dissapear as they grew.

Since i do not want to get rid of one of the parameters, since they both function accordingly, just a bit confusing, I will clarify this by adding sticky note indicators for the user in the Houdini file.

- pscale ramp overlooked

Some users overlooked the pscale adjuster, since it is within the animation node despite not being a directly animatable parameter - also since it is a ramp. I believe adding titles to the wrangle can help make this parameter more noticable.


### AI INTERACTION

- **Prompt:** add comments in the new generative frost md v04 at the top of wrangle 2 node, clarifying to users that degree sliders need to be inputted with degrees and not ramped 0-1
- **Output** Claude annoted the code, adding notes on the doc 
- **Decision** I read through its additions and found they clarified well enough to users ( especially those familiar with code)
### What I Learned

This week I organized and troubleshooted the system and prepared for user interaction, optimizing for different artists and workflows.

### What's Next

I will finalize the visuals of the project and render out an example of how the tool can functon, intending to utilize and experiment with the Houdini and ComfyUI connection while doing so.
