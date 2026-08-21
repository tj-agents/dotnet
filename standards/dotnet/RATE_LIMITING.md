# Rate limiting

## Throttle an endpoint on the trust axis or the cost axis — nothing else earns a policy

Rate limiting defends two different things, and an endpoint earns a policy when it is exposed on **either**:

- **Trust / reachability.** An anonymous or pre-auth surface — public browse, login, signup, password
  reset, an inbound webhook — is reachable by callers you cannot identify, so a flood is the default
  threat. Partition on **client IP**.
- **Cost / blast-radius.** A single authenticated call is expensive (a multi-source read, a bulk export,
  image processing, an email/notification fan-out) or destructive and irreversible (a bulk delete or
  anonymise, a payment). Even a trusted caller looping it — a runaway client, a compromised token — is a
  cost or damage vector. Partition on the authenticated **subject**.

Everything else — a cheap, authenticated, workflow-bounded read or write — stays **unthrottled**, and that
is most endpoints. **Authentication is not a reason to throttle, and neither is admin-gating**; a low,
naturally-bounded call rate is not a reason to throttle. Only genuine exposure on one of the two axes is —
so a destructive admin operation is throttled while ordinary admin CRUD is not.

## No global limiter; policies are named and opt-in

Do not install a blanket limiter that every request pays. Declare one **named policy per surface** at the
host and opt an endpoint in explicitly (`[EnableRateLimiting("…")]`), so the throttled surfaces are the few
that are auditable at a glance and adding one is a deliberate act, not a default someone forgot to exempt.

Each policy is a fixed window (`PermitLimit` per `WindowSeconds`) whose numbers bind from configuration, so
an environment tightens them without a redeploy; rejection returns **429**. Set a destructive or expensive
policy **tight** — legitimate low-volume use never approaches it, and the cap is a safety net, not a quota.

## The partition key follows the axis

- A trust-axis (anonymous) policy partitions on **client IP** — there is no identity to key on.
- A cost-axis (authenticated) policy partitions on the caller's **subject**, falling back to IP when
  absent. Keying a per-user policy on IP instead would let one user behind a shared NAT throttle another,
  and let one user spread across many IPs slip the cap.
