---
title: "Design Intent — AI-Assisted Frost in VFX"
course: "AI-201"
project: "Project 1 / Capstone — Frost"
status: draft
last_updated: 2026-04-03
---

# Design Intent: AI-Assisted Frost in VFX

Living document for scope and ethics; edit as the Houdini tool and comp evolve.

## My stance

I will be creating a frost simulation in Houdini, assisted by AI tools. The final output will be a Houdini render composited together in Nuke.

## What matters most

What I value most is using AI as a tool to achieve the final visual, not to generate the final image itself.

In the case of code, I should be able to understand all code generated for Houdini VEX, in order to troubleshoot and further my artistic control. The code will generate tools to help the product be art-directed by the user.

Generative imagery using models in ComfyUI will be used for streamlined iteration and ideation of composition, lighting textures, and small fixes such as paint-overs and masking. ComfyUI will not generate a final output.

## What I will not compromise on

AI will not generate a final image or output. The tool in Houdini will be used alongside other nodes and workflows. ComfyUI will also not create a final image. Generative AI will only be used for ideation and combining or slightly adjusting assets created by the user.

---

## Pipeline sketch

### Houdini VEX (code assist)

| Stage | Description |
|--------|-------------|
| **Input** | Directed instructions for sections of the Houdini VEX code |
| **Process** | Generated code that implements those instructions |
| **Output** | Code placed in a Houdini VEX Wrangle node to be troubleshot and art-directed further |

### ComfyUI (ideation loop)

| Stage | Description |
|--------|-------------|
| **Perceive** | Gather playblasts and slap comps to feed to ComfyUI; prompt different iterations and adjustments |
| **Decide** | ComfyUI models produce quick iterations for pre-visualization |
| **Act** | Compare visuals and decide how to continue processing artistically in Houdini and Nuke |

---

## Quarter question tie-in

*What happens when generated code and AI-assisted imagery are used to streamline VFX production?*

This intent keeps **streamlining** in tool-building and look iteration while **production truth** stays in Houdini renders and Nuke comp.
