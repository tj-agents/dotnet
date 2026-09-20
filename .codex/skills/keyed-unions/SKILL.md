---
name: keyed-unions
description: The standard shape for behaviour that varies by a closed key when the variants do NOT share one signature — a union resolved by key whose arms differ in parameters or return type, the sibling of `keyed-strategies` (N implementations of one identical interface). Covers the deciding question (declare a second arm only for a genuine difference in parameters or return type; identical headers are one interface with two implementations), the key going in and a capability coming out so business code never names the key, the registration block as the readable capability partition with completeness validation, arms growing with capabilities rather than keys, each arm matched exactly once, preconditions belonging in validation rather than arm implementations, arms carrying real payloads (no empty cases, marker-interface arms, or nullable fields standing in for absence), never inventing a parameter object to force differently-shaped arms into one signature, shared data living outside the union because C# 15 unions have no shared state across cases, and Dunet as the interim mechanism including the per-union implicit-conversion decision. Use when behaviour varies by a closed key and the variants take different inputs, when adding a key to such a family, when deciding between a union arm and another implementation of an existing interface, when a match arm needs a `when` guard or a discard, or when reviewing a keyed union registration.
kind: contract
domain: dotnet
profile: keyed-design
applicability: closed-key variants with different signatures
requires: dunet
provenance: library, pattern, house
---

# Keyed unions

Read and follow the [canonical shared definition](../../../.agents/contract/keyed-unions/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
