---
name: authorization
description: Authorization standard for an ASP.NET Core service, whatever decides access (an in-process role table, OpenFGA, Cedar, OPA) — identity-only tokens with authority resolved per request, permission checks never role checks, a closed typed permission catalog, deny by default, ASP.NET Core policies and resource handlers as the only enforcement path, object-level checks beside every function-level one, one decision point with an AuthZEN-shaped contract, immediate revocation, an exhaustively tested model, a generated client catalog, escalation guards, separate operator authority and audited decisions. Use when adding a permission, role or protected endpoint, designing or reviewing an authorization model, or deciding where an access check runs.
kind: contract
domain: dotnet
profile: aspnet
applicability: ASP.NET Core services that authorize users
requires: aspnet-core
provenance: framework, house
---

# Authorization

Owns how a service decides and enforces access. Rules held by domain types, such as what a role grants,
follow `dotnet:domain-ddd`.

## Applicability

This contract applies only to ASP.NET Core services. It requires `aspnet-core`. Installing `dotnet@tj-agents` makes this guidance available; it does not select those technologies for a consuming repository.

## Tokens carry identity; authority is resolved per request

A token carries the subject and nothing about what it may do. The service resolves the subject's authority
for the active scope, such as a tenant membership, on every request.

Why: role and permission claims stay valid until the token expires and cannot vary by tenant or resource.
Source: [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Check permissions, never roles

```csharp
[HasPermission(Permission.SettlementTriggerName)]
public Task<SettlementDto> Trigger(Guid concertId, CancellationToken ct) =>
    settlements.TriggerAsync(concertId, ct);
```

A role is a named bundle of permissions mapped in exactly one place. Endpoints, services and clients ask for
a permission. `IsInRole`, `[Authorize(Roles = …)]` and role comparisons in services are defects.

Why: changing what a role may do must be one edit to its mapping, never a search through every check.
Source: [NIST RBAC (INCITS 359)](https://csrc.nist.gov/projects/role-based-access-control).

## The permission catalog is closed and typed

```csharp
public readonly record struct Permission
{
    public const string SettlementTriggerName = "settlement.trigger";

    public static Permission SettlementTrigger { get; } = new(SettlementTriggerName);

    public static IReadOnlySet<Permission> All { get; } = new[] { SettlementTrigger }.ToFrozenSet();

    private Permission(string value) => Value = value;

    public string Value { get; }
}
```

Every permission is a member of one closed set with a stable `resource.action` wire name. Strings are parsed
once at the edge, and an unknown name fails at parse or startup. Policy, scope and audience vocabularies are
enums or equally closed types, never compared strings.

Why: a misspelt string permission is a silent denial or a silent grant.
Source: house.

## Deny by default

```csharp
services.AddAuthorizationBuilder()
    .SetFallbackPolicy(new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build());
```

Every endpoint declares a permission requirement or `[AllowAnonymous]`, and an architecture test fails an
endpoint that declares neither. Anonymous callers get 401; authenticated callers without the permission get 403.

Why: an endpoint added without a check is otherwise open to every signed-in user.
Source: [ASP.NET Core: require authenticated users](https://learn.microsoft.com/aspnet/core/security/authorization/secure-data#require-authenticated-users).

## ASP.NET Core authorization is the only enforcement path

Permission endpoints use a requirement, its handler and a policy provider that builds `perm:<name>` policies on
demand. Instance checks call `IAuthorizationService.AuthorizeAsync(user, resource, requirement)` or apply a
query filter built from the same decision. Services do not hand-roll checks beside this pipeline.

Why: one pipeline gives one place to audit, test and change enforcement.
Source: [policy-based](https://learn.microsoft.com/aspnet/core/security/authorization/policies) and
[resource-based](https://learn.microsoft.com/aspnet/core/security/authorization/resourcebased) authorization.

## Every function-level check has an object-level check

A permission on an endpoint never implies access to the instance it names. Each operation on an identified
resource also verifies the subject's relationship to that instance, by a resource handler or a query filter.

Why: broken object-level and function-level authorization are the first and fifth OWASP API risks.
Source: [OWASP API1:2023](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/),
[API5:2023](https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/).

## One decision point

```csharp
public sealed record AccessRequest(Permission Action, ResourceAddress Resource);

public interface IAccessDecision
{
    Task<bool> IsAllowedAsync(AccessRequest request, CancellationToken ct = default);
}
```

Policy handlers, resource handlers and query filters ask one decision service. The subject comes from the
request; the decision takes action, resource and context and returns allow or deny. When decisions move to a
separate service, that service speaks the OpenID AuthZEN Authorization API, so the engine behind it can change
without touching enforcement.

Why: several "may I" entry points drift apart, and an engine swap must not reach every caller.
Source: [OpenID AuthZEN Authorization API 1.0](https://openid.net/authorization-api-1-0-final-specification-approved/).

## Revocation takes effect immediately

Authority carries a version that changes on every role or grant change. Reads filter on the current version,
and a sensitive write re-verifies authority inside its transaction before commit.

Why: authority checked only at request start can be stale by the time the write commits.
Source: [CWE-367 time-of-check time-of-use](https://cwe.mitre.org/data/definitions/367.html).

## The model is tested exhaustively

The full role-to-permission table is a reviewed snapshot. Every rule has a case that grants and a case that
must not, every permission is held by at least one role, and every endpoint's requirement is enumerated.

Why: an authorization change must show up as a reviewable diff, not a spot check that still passes.
Source: [OpenFGA model testing](https://openfga.dev/docs/modeling/testing).

## Clients receive a generated catalog and the effective set

Client permission types are generated from the server catalog, and a CI check fails on a stale copy. The
server returns the subject's effective permissions for the active scope. A client check decides only what to
show.

Why: a hand-copied catalog drifts, and a client check is not enforcement.
Source: [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Guard escalation and separate operator authority

A subject cannot grant authority it does not hold, and a scope always keeps at least one owner. Platform
operators authorize through their own policy and principal, never through a tenant role.

Why: role management is itself a privileged operation, and operator access must not be grantable by a tenant.
Source: [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Audit decisions and authority changes

Log every denial and every role, grant or membership change with subject, scope, permission and resource.

Why: access incidents are investigated from these records.
Source: [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

## Split a permission only for a real role

Add or split a permission when an actual role needs part of an existing one, not for symmetry with CRUD verbs.

Why: unused granularity is catalog, UI and test surface with no user.
Source: house.
