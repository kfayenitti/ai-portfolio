# Pipeline Intent

## Ethics as Design Constraints

**Ethical question:** How can AI support VFX pipeline efficiency without reducing artist authorship or replacing creative judgment?

This question shapes the way AI is used throughout the pipeline. It ensures AI is controlled by the artist and supports the workflow without replacing creative authorship.

---

## Pipeline Sketch as Architecture Document


Perception layer: perceive, decide, act, with the human in the loop.

[Perceive] -> [Decide] -> [Act]

- **Perceive:** The system receives user-set Houdini parameters, test renders/playblasts, and AI-generated ideation references.
- **Decide:** The artist evaluates whether the tool is functioning correctly, whether visuals are satisfactory, and whether controls are sufficient for desired art direction.
- **Act:** The system generates procedural frost results based on selected parameters and adjustments
- **Human:** The artist drives the full loop by setting inputs, evaluating outputs, and deciding what to change next based on their own visual preferences and perspective.

---

### 1) My stance

Right now, my system receives user-defined parameters and procedural rules in Houdini to generate frost effects. With an ML layer, it will perceive references and ideation outputs, help decide useful look directions, and act through selected changes to tool settings and pipeline outputs based on previous creations and real life references

### 2) What matters most

What matters most is that this tool is customizable. It creates adjustable parameters, and helps an artist achieve their desired visuals. Additionally, at the end of the pipeline, AI is not used for final visual, only for ideation.

### 3) What I will not compromise on

I will not compromise on customizability, even if the code must be more complex to accommodate it. AI will not generate the final project output or replace human creative decision-making.
