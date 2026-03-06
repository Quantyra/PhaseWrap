# Q-RoPE Formalization v1 (S003)

## Objective
Provide a precise mathematical formulation for relative-phase positional encoding in hybrid quantum attention and state theorem conditions for relative-offset dependence.

## Setup
Let:
- token index `i in {1, ..., n}`
- token embedding map `E: X -> U(2^q)` where `E(x_i)` prepares token state
- learnable query/key unitaries `U_q, U_k in U(2^q)`
- positional unitary family `P(i) in U(2^q)`

Define:
- `|q_i> = U_q P(i) E(x_i) |0^q>`
- `|k_j> = U_k P(j) E(x_j) |0^q>`

Similarity kernel (state-overlap form):
- `K(i,j) := <q_i|k_j>`

## Q-RoPE positional family (baseline)
Use commuting phase factors:
- `P(i) = prod_{l=1}^q RZ_l(omega_l i)`

Equivalent tensor form applies when factorized by qubit.

## Relative-phase proposition (core target)
If all positional factors commute and share frequency basis, then:
- `P(i)^dagger P(j) = P(j - i)`

Therefore positional contribution in `K(i,j)` depends on relative displacement `(j - i)` through:
- `K(i,j) = <0| E(x_i)^dagger P(i)^dagger U_q^dagger U_k P(j) E(x_j) |0>`

Under additional compatibility condition
- `[U_q^dagger U_k, P(t)] = 0` for all offsets `t`,
the kernel can be rewritten with explicit relative-offset operator `P(j - i)`.

## Failure modes
Relative-offset reduction can fail or weaken when:
1. Position blocks do not commute (entangling/non-abelian design without matching analysis).
2. Query/key transforms break compatibility (`U_q^dagger U_k` non-commuting with positional action).
3. Data encoding entangles position and token channels in a way that defeats separable phase interpretation.

## NISQ feasibility notes
- Baseline `RZ` family uses single-qubit gates only.
- No auxiliary positional qubits are required in the baseline construction.
- Measurement overhead depends on chosen overlap estimator and shot budget, not on positional family alone.

## Claim boundaries
- Taken from source: RoPE/group-action literature supports relative-position behavior under structured rotational/group operators.
- Inferred for repo: the above proposition is the candidate Q-RoPE theorem skeleton for hybrid quantum attention and requires empirical validation in S004.

## Next formal steps
1. Select overlap estimator definition for experiment alignment.
2. Prove/validate compatibility conditions in selected architecture template.
3. Add bounded-noise sensitivity discussion tied to shot-based estimation.
