# Stage 157 - First-provider live-run approval packet

- Decision: `FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY`
- First provider: `ibm_runtime`
- Authorized runner commands: `2`
- Authorized job count: `328`
- Required approval phrase: `APPROVE IBM RUNTIME STAGE133 LIVE RUN`
- Hardware submitted by this stage: `false`
- Runnable command strings recorded here: `false`

## Authorized Windows
- `ibm_runtime__independent_window_00`: `164` jobs, command source `logs/automated_stage_gates/stage133_authorized_runner_command_packet/results.json`
- `ibm_runtime__independent_window_01`: `164` jobs, command source `logs/automated_stage_gates/stage133_authorized_runner_command_packet/results.json`

## Next Gate
Only after the user explicitly says `APPROVE IBM RUNTIME STAGE133 LIVE RUN`, read the runnable live-submit commands from Stage 133, execute only the authorized first-provider commands, then collect Stage 114 shards through Stage 115 and assemble Stage 113 evidence.
