---
name: proto
description: gRPC and Protobuf standard for .NET services — proto message naming vs the C# payload type, XMappers extension methods for proto-to-domain conversion, what may cross the wire (open string code, published message, semantic kind — never a union type or Result), total client error mapping via a FrozenDictionary of reconstructible cases, contract-mismatch handling for unknown codes, and cancellation precedence. Use when adding or changing a .proto file, writing or reviewing a gRPC client or server implementation, mapping proto messages to domain types, mapping RpcException to a typed error, or deciding whether a failure case can cross a service boundary.
kind: contract
domain: dotnet
profile: distributed-services
applicability: services using gRPC and Protobuf
requires: grpc, protobuf
provenance: protocol, library, house
---

# gRPC and Protobuf standard

Read and follow the [canonical definition](../../../.agents/dotnet/contract/proto/SKILL.md) in full.
This discovery entry is generated; edit the referenced `.agents/` definition.
