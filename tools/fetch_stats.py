#!/usr/bin/env python3
"""Fetch visitor statistics from Cloudflare Web Analytics (GraphQL API).

Used by .github/workflows/stats.yml (every 1st and 16th of the month). The
result is uploaded as a short-lived workflow artifact named "site-stats"
(NOT committed: the repo is public). The scheduled task «تقرير زوار الموقع»
downloads it, writes the report and updates content/PRIORITIES.md.

Needs:
  CF_API_TOKEN    Cloudflare API token with  Account > Account Analytics > Read
                  (GitHub secret, added by the site owner)
  CF_ACCOUNT_ID   Cloudflare account id (optional: if missing, it is looked up
                  from the token via GET /accounts)

Run:  python3 tools/fetch_stats.py [--days 15] [--out stats.json]
Each part is queried separately; a failing part is recorded under "errors"
instead of stopping everything, so a field rename at Cloudflare is easy to see
and fix.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.cloudflare.com/client/v4/graphql"

# name -> (dataset, selection, orderBy, limit)
PARTS = {
    "total": ("rumPageloadEventsAdaptiveGroups", "count sum { visits }", None, 1),
    "daily": ("rumPageloadEventsAdaptiveGroups", "count sum { visits } dimensions { date }", "[date_ASC]", 40),
    "pages": ("rumPageloadEventsAdaptiveGroups", "count sum { visits } dimensions { requestPath }", "[count_DESC]", 100),
    "referrers": ("rumPageloadEventsAdaptiveGroups", "count sum { visits } dimensions { refererHost }", "[count_DESC]", 30),
    "countries": ("rumPageloadEventsAdaptiveGroups", "count sum { visits } dimensions { countryName }", "[count_DESC]", 30),
    "devices": ("rumPageloadEventsAdaptiveGroups", "count sum { visits } dimensions { deviceType }", "[count_DESC]", 10),
    "hosts": ("rumPageloadEventsAdaptiveGroups", "count dimensions { requestHost }", "[count_DESC]", 10),
    "speed": ("rumPerformanceEventsAdaptiveGroups", "count avg { pageLoadTime } quantiles { pageLoadTimeP50 pageLoadTimeP90 }", None, 1),
    "vitals": ("rumWebVitalsEventsAdaptiveGroups",
               "count quantiles { largestContentfulPaintP75 interactionToNextPaintP75 cumulativeLayoutShiftP75 }", None, 1),
}


def gql(token, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"errors": [{"message": f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"}]}


def find_account(token):
    """Look up the account id the token can see (used when CF_ACCOUNT_ID is not set)."""
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/accounts?per_page=5",
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
        accts = res.get("result") or []
        return (accts[0]["id"], None) if accts else (None, "token sees no account")
    except urllib.error.HTTPError as e:
        return None, f"accounts lookup HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"


def part(token, account, start, end, dataset, selection, order, limit):
    order_arg = f", orderBy: {order}" if order else ""
    q = f"""query ($account: String!, $start: Time!, $end: Time!) {{
  viewer {{ accounts(filter: {{ accountTag: $account }}) {{
    rows: {dataset}(limit: {limit}{order_arg}, filter: {{ datetime_geq: $start, datetime_lt: $end }}) {{ {selection} }}
  }} }}
}}"""
    res = gql(token, q, {"account": account, "start": start, "end": end})
    if res.get("errors"):
        return None, "; ".join(e.get("message", "") for e in res["errors"])
    accts = (res.get("data") or {}).get("viewer", {}).get("accounts") or []
    if not accts:
        return None, "account not found (check CF_ACCOUNT_ID and token permissions)"
    return accts[0]["rows"], None


def period(token, account, start, end, names):
    out, errors = {}, {}
    iso = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
    for name in names:
        rows, err = part(token, account, iso(start), iso(end), *PARTS[name])
        if err:
            errors[name] = err
        else:
            out[name] = rows
    return out, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=15)
    ap.add_argument("--out", default="stats.json")
    a = ap.parse_args()
    token, account = os.environ.get("CF_API_TOKEN", "").strip(), os.environ.get("CF_ACCOUNT_ID", "").strip()
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - dt.timedelta(days=a.days)
    prev_start = start - dt.timedelta(days=a.days)
    result = {"generated": now.isoformat(), "period": {"start": start.isoformat(), "end": now.isoformat(), "days": a.days}}
    if token and not account:
        account, err = find_account(token)
        if err:
            result["errors"] = {"setup": f"CF_ACCOUNT_ID not set and lookup failed: {err}"}
    missing = [n for n, v in (("CF_API_TOKEN", token), ("CF_ACCOUNT_ID", account)) if not v]
    if missing:
        result.setdefault("errors", {}).setdefault("setup", "missing " + ", ".join(missing))
    else:
        cur, err = period(token, account, start, now, list(PARTS))
        prev, perr = period(token, account, prev_start, start, ["total", "pages"])
        result.update({"current": cur, "previous": prev})
        if err or perr:
            result["errors"] = {**err, **{f"previous.{k}": v for k, v in perr.items()}}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    tot = (result.get("current", {}).get("total") or [{}])
    print("visits:", (tot[0].get("sum") or {}).get("visits") if tot else None, "| page views:", tot[0].get("count") if tot else None)
    if result.get("errors"):
        print("errors:", json.dumps(result["errors"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
