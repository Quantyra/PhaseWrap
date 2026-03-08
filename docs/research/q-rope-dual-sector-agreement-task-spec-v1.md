# Q-RoPE Dual-Sector Agreement Task Specification v1

## Scope
- Story: `S173`
- Task id: `synthetic_dual_sector_agreement_binary`
- Status: memo-only

## Sample schema
Each sample contains two relational observations:
- observation `A`
- observation `B`

Each observation is itself a synthetic pair instance with fields of the same type as earlier tasks:
- left token
- right token
- left position
- right position
- signed offset

But the task label is not taken from either observation alone.

## Derived sector variables
For each observation derive exactly one sector:
- `sector_a in {P_small, P_large, N_small, N_large}`
- `sector_b in {P_small, P_large, N_small, N_large}`

Where:
- positive sectors are `{P_small, P_large}`
- negative sectors are `{N_small, N_large}`

## Label rule
Binary label:
- `1` if `sector_a` and `sector_b` belong to the same sign family
- `0` otherwise

So the label depends on relational agreement across two sector assignments.

## Allowed symbolic control
One bounded symbolic baseline only.

### Allowed inputs
Two separate one-hot blocks:
- block `A`: `secA_P_small`, `secA_P_large`, `secA_N_small`, `secA_N_large`
- block `B`: `secB_P_small`, `secB_P_large`, `secB_N_small`, `secB_N_large`

### Forbidden inputs
- cross terms between block `A` and block `B`
- token identity
- absolute positions
- direct numeric offset sign or magnitude
- any handcrafted same-sign indicator

### Allowed head
- logistic-regression-equivalent only

## Why the bounded symbolic control should fail linearly
The label is an agreement-style interaction over two categorical blocks.

An additive linear model over separate one-hot blocks can score:
- what `sector_a` is
- what `sector_b` is

But not the interaction pattern:
- same-sign vs mixed-sign

without explicit cross terms or a nonlinearity.

That is the whole point of this task.

## Alignment-safe requirements
The task must preserve all of these:
- no token-dependent labeling
- no direct numeric offset label shortcut
- no single-sector shortcut
- balanced positive and negative classes
- balanced sampling across all sector-pair combinations that map to each class

## Balancing rule
The generator must approximately balance:
- class labels
- small vs large magnitude presence across both observations
- positive vs negative sector frequency within each observation slot

## Minimal future packet
If later approved, the first packet must remain:
- local-only
- zero-credit
- seeds `42`, `123`, `777`
- `V_future_relational_witness` against the bounded symbolic control only

## Bottom line
This task is the correct next differentiating test because it preserves the relational structure while making the label depend on interaction between two relational sector assignments rather than on one explicit sector identity.
