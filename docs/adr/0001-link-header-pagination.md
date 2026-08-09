# 1. Paginate on the Link header, not X-Total-Count

Date: 2026-08-09

## Status

Accepted

## Context

`ToshlClient._get_all_pages` originally determined how many pages to
fetch by reading the `X-Total-Count` response header:

```python
total = int(response.headers.get("X-Total-Count", len(data)))
total_pages = math.ceil(total / _PER_PAGE)
```

Toshl never sends that header. It *advertises* it — every response
carries:

```http
access-control-expose-headers: Link, Location, Last-Modified,
  Toshl-Modified, Request-Id, Toshl-Node-Id, X-Total-Count
```

but the header itself is absent from the response. The `.get()` default
therefore collapsed `total` to the number of items on the first page,
`total_pages` evaluated to `1`, and the loop stopped immediately.

The failure was silent and boundary-dependent: any collection of
`_PER_PAGE` items or fewer returned correctly, so the bug stayed
invisible until a list crossed 200. Observed against the live API with
247 tags:

| request                     | items | `X-Total-Count` | `Link`               |
| --------------------------- | ----- | --------------- | -------------------- |
| `/tags?per_page=200&page=0` | 200   | absent          | `rel="next"` present |
| `/tags?per_page=200&page=1` | 47    | absent          | no `next`            |

`get_tags` returned 200 tags and dropped 47 with no error and no log
line. Every list endpoint shares this helper, so accounts, entries,
categories and budgets were all affected.

The Toshl API documents pagination via the RFC 5988 `Link` header,
carrying `rel="first"`, `rel="previous"`, `rel="next"` and `rel="last"`.

## Decision

Drive the pagination loop off `Link` `rel="next"`, following the URL the
server supplies verbatim — query string included — until no `next`
relation is present.

`httpx` parses the header natively via `response.links`, so this needs
no new dependency and no hand-rolled header parsing.

Because absence of a `next` link is also what a stripped or omitted
header looks like, log a warning when a page arrives that is exactly
`_PER_PAGE` items long *and* carries no `next` link. That is the one
response shape that is almost certainly truncation.

## Consequences

- All five list endpoints return complete results.
- The server owns pagination state; the client no longer computes page
  numbers, so it cannot disagree with the server about them.
- The warning is a heuristic, not a guarantee. A collection whose size
  is an exact multiple of `_PER_PAGE` will log a spurious warning on its
  final page. Accepted: a rare false positive is cheaper than the silent
  data loss this replaces.
- No runaway-loop guard. A server that returned a `next` link pointing
  at itself would loop indefinitely. Judged not worth pre-empting.
- `per_page` stays at 200 despite a documented maximum of 500. It no
  longer affects correctness, only request count.

## Notes

Do not reach for `X-Total-Count` because it appears in
`access-control-expose-headers`. It is listed there but never sent.
