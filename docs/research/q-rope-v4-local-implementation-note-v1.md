# Q-RoPE V4 Local Implementation Note v1

## Scope completed
- Added `V4` config as a damped-and-clipped Q-RoPE variant
- Implemented the `V4` phase schedule in the shared variant-phase map
- Preserved the same hardware-cost structure as `V3`
- Verified that local and backend-translation paths accept `V4`

## Implementation details
- `V4` uses base phase `0.14`
- `V4` remains in the Q-RoPE family and changes only phase magnitude, not circuit family
- Photonic and IBM translation paths inherit the damped schedule through the shared phase map

## Validation intent
- Keep this step zero-credit
- Confirm the runner can execute `V4` locally before any broader local comparison or paid remote wave

## Next step
- Run the local `V3` vs `V4` comparison packet across datasets and seeds
