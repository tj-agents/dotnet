# Stack defaults

**One library per job.** Adding a second library for a job an existing one already does is the violation,
even when the new one is better in isolation — two answers to one question is what makes a codebase
unlearnable. Replace, or don't add.

Each row below has a skill that covers *how* to use it well; this skill only decides *what* and *when*.

| Job | Reach for | Depth |
|---|---|---|
| Server state — anything fetched from an API | **React Query** | `server-state` |
| Shared client state | **Zustand** | `client-state` |
| Parsing and validating untrusted input | **zod** | `write-boundary` |
| Routing | **TanStack Router** | — |
| Styling | **Tailwind**, `cn()`, **cva** for variants | — |
| Dates and times | **dayjs**, behind one formatting module | — |
| HTTP | one typed client per backend service | `http-layer` |
| Tests | **Vitest** | — |
| Tables | **TanStack Table** | — |

## Zustand over a reducer, in most cases

Default to a Zustand store for state more than one component reads. It gives selector-scoped
re-rendering, actions that own their transitions, and access from outside React — all without a provider
in the tree.

**`useReducer` is still right in one narrow case:** a genuinely local state machine owned by a single
component, where the transitions are the component's own business and nothing outside it reads the state.
A wizard's step state inside one dialog is a reducer. The moment a second component needs the value, it
was a store.

**`Context` is for dependency injection, not state.** Passing a client, a theme, or a configuration object
down the tree is what it is for. Using it to hold mutating application state re-renders every consumer on
every change, which is the problem Zustand's selectors exist to solve.

Never reach for Redux, MobX, or a hand-rolled event emitter. For deep nested updates inside a store, use
immer rather than hand-written spread chains.

## zod at every untrusted boundary, not just forms

Anything crossing into the app from outside is parsed, and the **parsed** value is what the app uses:

- a form buffer at submit — see `write-boundary`;
- route **search params**, through the router's own validation hook, so a bad URL is a typed failure
  rather than an undefined read three components deep;
- environment configuration at startup, so a missing variable fails immediately and visibly instead of
  becoming `undefined` in a fetch URL;
- any third-party or webhook payload the app did not shape itself.

Tie the type to the schema with `z.infer` so drift is a compile error rather than a runtime surprise.

**A first-party API response is the exception.** It is already typed by the contract and re-parsing every
response buys latency and a second source of truth; a genuine mismatch there is a backend bug to fix at
the source. Parse untrusted input, not your own.

## Styling — utility classes, not a styling library

Tailwind for layout and appearance. Compose conditional classes through a single `cn()` helper (clsx plus
tailwind-merge, so a later class actually wins), and express component variants with **cva** rather than
ternaries stacked in the class string.

Do not add a CSS-in-JS library, and do not introduce a second component library alongside the primitives
already in use. Copy-in primitive components (the shadcn model) are **owned code** — edit them in place;
they are not vendored files to leave untouched.

## Dates behind one module

dayjs, and every format string lives in one formatting module the app calls. Ad-hoc `toLocaleString`
calls scattered across components are how the same date renders three ways on one screen. Never add
moment.

## Deliberately not used

Redux, MobX, moment, styled-components or another CSS-in-JS runtime, a second HTTP client, a second date
library, a utility library imported for one function. If one of these looks necessary, the interesting
question is why the incumbent cannot do it — answer that first, in the PR.
