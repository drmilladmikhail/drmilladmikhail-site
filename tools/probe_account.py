#!/usr/bin/env python3
"""One-off helper: try to discover the Cloudflare account id from CF_API_TOKEN.
Prints only account ids (not secret) and error messages. Safe to delete."""
import json, os, urllib.request, urllib.error
T = os.environ.get("CF_API_TOKEN", "").strip()
def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {T}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"http": e.code, "body": e.read()[:300].decode("utf-8", "replace")}
G = "https://api.cloudflare.com/client/v4/graphql"
v = call("https://api.cloudflare.com/client/v4/user/tokens/verify")
print("verify:", v.get("success"), (v.get("result") or {}).get("status"), v.get("errors"))
for name, url in [("accounts", "https://api.cloudflare.com/client/v4/accounts"),
                  ("memberships", "https://api.cloudflare.com/client/v4/memberships")]:
    r = call(url)
    print(name, ":", [(a.get("id"), a.get("name")) for a in (r.get("result") or []) if isinstance(a, dict)] or r.get("errors") or r)
    if name == "memberships":
        print("membership accounts:", [((m.get("account") or {}).get("id")) for m in (r.get("result") or [])])
for q in ['{ viewer { accounts(filter: {}) { __typename } } }',
          '{ __type(name: "AccountFilter_InputObject") { inputFields { name } } }',
          '{ __type(name: "account") { fields { name } } }']:
    r = call(G, {"query": q})
    print("gql:", q[:60], "->", json.dumps(r)[:600])
