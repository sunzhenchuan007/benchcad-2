# PR #353 geometry error analysis and validation plan

## 1. Corrected conclusion

The previous reconstruction was not a small directional error. It assigned the
wrong component topology to the reference: two separate thin clamp straps, a
stud fused into one strap, a tightening axis along Y, and lower feet folded
toward the centre. Those statements are withdrawn.

Exact partition of the supplied HoldRite `HR100100-4-555` STEP recovers four
logical parts:

1. one continuous `steel_strut_clamp`;
2. one D-shaped `cushion_insert`;
3. one independent `cross_bolt`;
4. one independent `lock_nut`.

The pipe axis is Y, the bolt axis is X, and the rail-facing direction is -Z.
The correction therefore rebuilds all four components independently and makes
their mating faces construction inputs, not visual afterthoughts.

## 2. Evidence boundary

- The target remains the STAUFF STC/SPC family from Issue #343 / PR #353.
  Printed D1/B/C/D/E/thread values come only from STAUFF Catalogue 1,
  06/2026, pp. 172--173.
- The homologous reference is the official Reliance Worldwide Corporation /
  HoldRite `HR100100-4-555` AP242 STEP exported by TraceParts.
- The reference is not a STAUFF part. Its dimensions are not copied into the
  parameter table; it supplies evidence for otherwise-unmarked topology,
  axes, component separation, and contact relationships.
- The STEP contains one fused `MANIFOLD_SOLID_BREP`, not an assembly tree.
  Component names and manufacturing semantics therefore require product
  documentation plus mechanical interpretation. Geometry alone proves the
  exact partition and interfaces, not the original CAD feature history.

The recovered four bodies have zero pairwise volume overlap and their union
reproduces the fused source. The cushion extends 3.175 mm beyond each Y end of
the steel. This axial overhang is an assembly relationship, not a rendering
detail.

## 3. Contact graph recovered from the STEP

| Component A | Component B | Nominal shared boundary | Mechanical role |
|---|---|---:|---|
| steel clamp | cushion | 6 faces, 2459.106 mm2 | curved wrap, side bearing, lower seats |
| steel clamp | cross-bolt | 2 faces, 272.235 mm2 | ear-hole guidance and head bearing |
| steel clamp | lock nut | 1 face, 76.500 mm2 | nut bearing against the opposite ear |
| cross-bolt | lock nut | 1 face, 116.543 mm2 | coaxial shank/thread interface |
| cushion | cross-bolt | none | required clearance |
| cushion | lock nut | none | required clearance |

The first steel/cushion contact consists of two curved patches, two vertical
side patches, and two local lower supports. The fastener relationship is not
merely "a bolt near the top": its axis, two bearing planes, and the threaded
mate all have distinct mechanical roles.

## 4. What went wrong

### 4.1 Silhouette completion replaced topology recovery

The earlier model selected a familiar clamp silhouette and completed hidden
geometry with a plausible two-strap pattern. Several different assemblies can
produce a similar isometric outline. Once that early component guess was made,
later edits only improved the wrong hypothesis.

### 4.2 A fused STEP was treated as either no evidence or full BOM evidence

Both extremes are incorrect. A fused BRep does not expose an assembly tree,
but it still contains exact surfaces, axes, limiting planes, and separable
mechanical regions. The previous analysis stopped at "one solid" instead of
performing geometric partition and contact recovery.

### 4.3 Components were named before their interfaces were identified

Calling shapes "left half", "right half", or "stud" encouraged the code to
preserve those nouns even when the contact geometry contradicted them. A safer
order is: recover axes and interfaces, partition volumes, verify union and
overlap, and only then assign component names.

### 4.4 Contact was inferred from proximity in a render

An opaque render cannot prove that a shank is coaxial with a hole, that a nut
face bears on an ear, or that two parts do not interpenetrate. The old workflow
counted solids and checked appearance but did not require an expected contact
matrix. That allowed mechanically impossible arrangements to look acceptable.

### 4.5 Axis language was not bound to measurable geometry

"Vertical", "outward", and "toward the rail" were used without a fixed global
frame. The reference gives measurable axes: the bore cylinder is Y, the
fastener cylinder is X, and rail/down is -Z. Mechanical words should always be
recorded together with those vectors before code is written.

### 4.6 The analogous reference was transferred too literally in some places

A homologous STEP is strong evidence for topology but not for STAUFF dimensions
or every manufacturing detail. Similarity must be split into categories:
catalogue dimensions, exact reference topology, documented product semantics,
and explicitly labelled proportions. Mixing these categories creates false
precision.

## 5. Is this a general AI failure?

One PR cannot establish a universal failure. It supports testable hypotheses:

1. **single-view topology ambiguity**: models optimize visible silhouette and
   hallucinate hidden connections;
2. **semantic anchoring**: an early component name makes later contradictory
   evidence less likely to be accepted;
3. **assembly-collapse error**: models confuse a fused exchange BRep with both
   "one manufactured part" and "no recoverable assembly information";
4. **contact blindness**: image similarity is over-weighted relative to
   coincident faces, clearances, axes, and interference volume;
5. **frame errors**: local and global direction words drift after rotations;
6. **boolean convenience bias**: easy primitives are preferred even when they
   do not reproduce the load path or mating surface.

These should be called cross-model failure modes only if they recur across
independent model families, product families, and random seeds.

## 6. Experiments to test generality

### 6.1 Dataset

Use 30--50 industrial assemblies with official CAD, including clamps, hinges,
split housings, sheet-metal hooks, threaded joints, and hidden inserts. Preserve
assembly-tree ground truth where available. Add fused exports of the same
models so the experiment can separate representation effects from geometry.

### 6.2 Paired evidence conditions

| Condition | Evidence supplied |
|---|---|
| A | one isometric image |
| B | front/side/top/isometric images |
| C | B plus dimensions and fixed global axes |
| D | C plus component count but no contact graph |
| E | C plus expected contact/clearance graph |
| F | E plus native assembly STEP |
| G | E plus deliberately fused STEP |
| H | G plus automatic partition/contact feedback |

Run every condition with a standard prompt and a contact-first prompt. Repeat
with structural few-shot examples and with visually similar but mechanically
different distractor examples. This separates prompt effects, case-retrieval
effects, and tool-feedback effects.

### 6.3 Required intermediate answer

Before CAD generation, require a machine-readable plan:

```text
component -> axis -> bounding region -> mates -> clearances -> load path
known dimension -> source
inferred proportion -> justification
expected solid count -> allowed coincident faces -> forbidden shared volume
```

This lets the evaluator distinguish understanding errors from CAD coding
errors.

### 6.4 Metrics

- component-count accuracy and component-graph F1;
- axis angular/sign error;
- expected-contact precision and recall;
- unexpected-contact count;
- pairwise interference volume;
- symmetric-difference volume against reference geometry after alignment;
- solid count and BRep validity after STEP export;
- key-section silhouette IoU and surface distance;
- blinded engineer rating of assembly function and load path.

The key test for this case is not generic visual similarity. It is whether the
model recovers four parts, X/Y/Z axis roles, four required contacts, two required
clearances, and zero shared volume.

### 6.5 Generality criterion

Use paired comparisons on the same model/part/seed and report bootstrap
confidence intervals. Treat model family and product family as hierarchical
factors. A failure is plausibly general only when it appears in at least three
independent model families and several held-out product families, not merely
in repeated prompts to one model.

## 7. Prevention: prompt, cases, and tooling

Prompting helps by forcing explicit components, axes, contacts, and uncertainty,
but it cannot recover hidden geometry absent from the evidence. Few-shot cases
help only when retrieved by mechanical structure; retrieval by silhouette can
strengthen the wrong analogy.

The strongest prevention is a CAD evidence loop:

1. freeze the global coordinate frame;
2. inspect STEP metadata and determine whether an assembly tree exists;
3. inspect each candidate component separately;
4. recover or declare the contact/clearance matrix before modeling;
5. build mating surfaces from shared datums;
6. check pairwise common volume and coincident-face area;
7. export STEP and recheck body count/BRep validity;
8. inspect orthographic, component, contact-highlight, and section views;
9. run small, middle, and extreme catalogue rows;
10. require human approval of the resulting geometry.

## 8. Correction implemented in PR #353 worktree

The revised `part.py` now constructs one continuous steel frame, one D-shaped
cushion, one independent X-axis cross-bolt, and one independent lock nut. The
steel cavity and cushion use one shared D-profile datum. The bolt shank and lug
hole share one radius; the head and nut bearing faces are placed on the two lug
planes; and the nut thread is cut by the exact bolt thread.

For representative smallest, middle, and largest catalogue rows, the local
contact audit finds four valid one-solid components, zero pairwise overlap, all
four required contact pairs, and no cushion/fastener contact. `bench2 validate`
passes easy / medium / hard at 4/4 seeds each; exported instances retain four
positive, BRep-valid bodies with no component overlap. The overview, benchmark
views, hard section, extremes, and component-highlight previews were regenerated
after this correction. These checks must be repeated after any further geometry
change, and human visual acceptance remains the final gate.
