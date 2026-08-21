---
name: rate-limiting
description: Rate-limiting standard for a .NET web service — an endpoint earns a named policy only when it is exposed on the trust axis (anonymous/pre-auth surfaces, partitioned per client IP) or the cost axis (an expensive or destructive authenticated call, partitioned per subject); a cheap authenticated or admin-gated workflow endpoint stays unthrottled, since authentication is not a reason to throttle. No global limiter — policies are named and opt-in via `[EnableRateLimiting]`, fixed windows bound from config, rejection is 429, destructive policies set tight. Use when adding or reviewing an endpoint that might be an abuse or cost surface, deciding whether something needs throttling, choosing a partition key (per-IP vs per-subject), or wiring a new rate-limit policy at the host.
---

# rate-limiting

The standard is `../../standards/dotnet/RATE_LIMITING.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
