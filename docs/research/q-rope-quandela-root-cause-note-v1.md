# Q-RoPE Quandela Root Cause Note v1

## Finding
- Replaying the exact `RemoteJob` payload against the Quandela job-create endpoint returns:
  - `{"error":"Not enough credits"}`

## Interpretation
- The Perceval client currently masks useful error details by raising a generic `HTTPError` on non-200 responses.
- At least part of the observed direct-Quandela instability is explained by an account-credit problem rather than purely by circuit structure or local code defects.
- This does not prove every earlier failure had the same cause, but it is the clearest current root cause available from the provider response itself.

## Local fix status
- We can improve error surfacing locally.
- We cannot fix missing provider credits locally.
- For execution continuity, the choices remain:
  - add credits / upgrade access,
  - use a fallback photonic provider path,
  - or constrain direct Quandela usage to already-working limited evidence.
