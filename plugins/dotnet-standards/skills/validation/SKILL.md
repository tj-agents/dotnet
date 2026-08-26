---
name: validation
description: Validation standard for .NET services — FluentValidation for input shape versus a hand-written domain-eligibility validator returning Reunion's `ValidationResult`, invariant-owning entity and value normalization, whether a validator is auto-validated by the MVC filter or injected and called explicitly (and why injecting one for an MVC-arriving type is unreachable code), accumulating independent field failures with `Combine`, mapping validation into an operation's own error at one boundary, and the validation-aware `Ensure` overload that preserves an existing success value. Use when adding or reviewing a validator, normalizing domain text, deciding which validation tool a rule belongs to, wiring validation into a worker/handler/gRPC path, or carrying field errors through a Result chain.
---

# validation

The standard is `../../standards/dotnet/VALIDATION.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
