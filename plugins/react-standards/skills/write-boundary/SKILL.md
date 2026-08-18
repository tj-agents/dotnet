---
name: write-boundary
description: The client write boundary — every user-editable form validates its controlled-input buffer against a zod schema at submit and maps the *parsed* result, never the raw buffer, to the request type, so the parse narrows the type (removing the `!` bang and `?? fallback` that are the missing validation) and yields per-field messages rendered inline plus a real `isValid` submit gate; the schema lives in the feature's `schemas/` folder and is tied to the request with `z.infer` so drift is a compile error, and client validation is a UX affordance rather than a trust boundary. Use when building or reviewing a form, mapping a buffer to a request, seeing a non-null assertion on form data, or reporting a validation message.
---

# write-boundary

The standard is `../../standards/react/FORMS.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
