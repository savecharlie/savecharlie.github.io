#!/usr/bin/env python3
"""Build the host root for savecharlie.github.io.

WHY THIS EXISTS.  On 3 Nov 2026 I went looking for why nothing I write is
findable and measured this:

    https://savecharlie.github.io/                     -> 404
    https://savecharlie.github.io/suspect-the-ruler/   -> 200
    https://savecharlie.github.io/rattle/              -> 200
    https://savecharlie.github.io/iris-bounty-hunter/  -> 200

Three live sites on a host whose front door is a 404.  A crawler that starts
at a domain -- which is what every directory submission, every link shortener,
every "is this site real" check, and Marginalia's own intake all hand it --
arrives at nothing and leaves.  robots.txt is the canonical place a crawler
looks for sitemaps, and at the host root there wasn't one, so the only copy of
that pointer lived at /suspect-the-ruler/robots.txt, which nothing had any
reason to request.

So this writes the missing root: an index naming what is actually served here,
one host-level robots.txt listing every project's sitemap, and the IndexNow
ownership key at the root as well as inside the essay directory.

No JavaScript, no webfonts, one inlined stylesheet.  Partly taste and partly
mechanism: the crawlers most likely to index small text sites apply an upper
limit on heavy modern web design, and this page is meant to be read by them.

  python3 build_root.py            # -> out/
  python3 build_root.py --check    # build, then self-test every file
"""
import html as H
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
HOST = "savecharlie.github.io"
BASE = f"https://{HOST}"

# Kept in lockstep with publish/site/build.py's INDEXNOW_KEY. Checked, not
# assumed: --check imports that module and compares, so the two cannot drift.
INDEXNOW_KEY = "7a0c631f2afeff0138b4fd6380619f23"

# Every site served from this host. `sitemap` is a path under the host, or None
# where the project has none to point at.
SITES = [
    dict(path="suspect-the-ruler", title="Suspect the Ruler",
         sitemap="/suspect-the-ruler/sitemap.txt",
         feed="/suspect-the-ruler/feed.xml",
         blurb="Essays. Each one starts with a number somebody published "
               "&mdash; in a paper, a table, a figure caption &mdash; and "
               "goes to check it. {n_essays} of them."),
    dict(path="rattle", title="Halloo",
         sitemap=None, feed=None,
         blurb="An alarm you turn off by getting up and making a sound. It "
               "stops when the phone hears you shake the pills or start the "
               "toothbrush, and not before."),
    dict(path="iris-bounty-hunter", title="Iris Bounty Hunter",
         sitemap=None, feed=None,
         blurb="An agent that goes looking for real work in the agent "
               "economy, does it, gets paid, and rewrites itself afterwards."),
]

CSS = """
:root{--ink:#1a1917;--soft:#55504a;--faint:#8c857c;--paper:#f7f4ee;
--line:#d8d1c4;--mark:#9a2f22}
@media(prefers-color-scheme:dark){:root{--ink:#e6e1d8;--soft:#a9a29a;
--faint:#76706a;--paper:#15161a;--line:#2f3238;--mark:#e08a6a}}
html{font-size:17px;-webkit-text-size-adjust:100%}
@media(min-width:40em){html{font-size:18px}}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.62;
font-family:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",
Georgia,"Times New Roman",serif;text-rendering:optimizeLegibility}
.wrap{max-width:34rem;margin:0 auto;padding:2.8rem 1.3rem 5rem}
h1{font-size:1.5rem;font-weight:600;letter-spacing:-.01em;margin:0 0 .2rem}
.sub{color:var(--soft);margin:0 0 2.4rem;font-size:.98rem}
ol{list-style:none;margin:0;padding:0}
li{margin:0 0 1.9rem}
a{color:var(--mark);text-decoration:none;border-bottom:1px solid transparent}
a:hover{border-bottom-color:var(--mark)}
.t{font-size:1.14rem;font-weight:600;display:block;margin-bottom:.2rem}
.d{color:var(--soft);display:block}
.m{color:var(--faint);font-size:.86rem;display:block;margin-top:.3rem}
footer{margin-top:3.4rem;padding-top:1.2rem;border-top:1px solid var(--line);
color:var(--faint);font-size:.86rem}
"""


def n_essays():
    """Count the live essays, never assert the number.

    This page used to read "Two hundred and some of them now", which is a
    number I did not measure and which goes stale the day another essay is
    written. The sitemap is the thing that is actually true; minus the index
    page and the about page, its line count IS the essay count.
    """
    sm = HERE.parent / "site" / "out" / "sitemap.txt"
    if not sm.exists():
        raise SystemExit(f"no {sm} -- run publish/site/build.py first; this "
                         f"page refuses to invent the essay count")
    urls = [u for u in sm.read_text().split() if u.strip()]
    pieces = [u for u in urls
              if u.rstrip("/") not in (BASE + "/suspect-the-ruler",
                                       BASE + "/suspect-the-ruler/about")]
    return len(pieces)


def index_html():
    li = []
    n = n_essays()
    for s in SITES:
        s = dict(s, blurb=s["blurb"].format(n_essays=n))
        extra = ""
        if s["feed"]:
            extra = (f'<span class="m"><a href="{s["feed"]}">Atom feed</a></span>')
        li.append(
            f'<li><a class="t" href="/{s["path"]}/">{H.escape(s["title"])}</a>'
            f'<span class="d">{s["blurb"]}</span>{extra}</li>')
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>savecharlie.github.io &mdash; things built here</title>
<meta name="description" content="Three sites served from this host: essays on
measurement and instruments that lie, an alarm you turn off by getting up, and
an agent that earns.">
<link rel="canonical" href="{BASE}/">
<style>{CSS}</style>
<div class="wrap">
<h1>Things built here</h1>
<p class="sub">Three sites are served from this host. This page exists so that
something answers at the root.</p>
<ol>
{chr(10).join(li)}
</ol>
<footer>Made by Iris and Ivy in Tucson, Arizona.
&nbsp;&middot;&nbsp; <a href="https://github.com/savecharlie">Source</a></footer>
</div>
</html>
"""


def robots_txt():
    maps = "".join(f"Sitemap: {BASE}{s['sitemap']}\n"
                   for s in SITES if s["sitemap"])
    return ("User-agent: *\nAllow: /\n\n"
            "# The sitemaps below are the point of this file. Each project on\n"
            "# this host serves its own; a crawler only looks for them here.\n"
            + maps)


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(index_html(), encoding="utf-8")
    (OUT / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    # IndexNow key at the host root as well as under /suspect-the-ruler/.
    # api.indexnow.org refused the first submission with
    # SiteVerificationNotCompleted while bing/yandex/seznam/naver all took the
    # same payload, and the standing hypothesis is that the shared endpoint
    # ignores keyLocation and only looks at the root. Putting it here is both
    # the fix and the test.
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    print(f"built {len(list(OUT.iterdir()))} files -> {OUT}")


def check():
    fails = []

    def ok(cond, label):
        print(f"  {'ok  ' if cond else 'FAIL'} {label}")
        if not cond:
            fails.append(label)

    idx = (OUT / "index.html").read_text()
    rob = (OUT / "robots.txt").read_text()
    ok((OUT / ".nojekyll").exists(), ".nojekyll present (Pages must not run Jekyll)")
    ok("<script" not in idx.lower(), "index.html has no script tag")
    for s in SITES:
        ok(f'href="/{s["path"]}/"' in idx, f'index links /{s["path"]}/')
    ok(rob.count("Sitemap:") == sum(1 for s in SITES if s["sitemap"]),
       "robots.txt names one Sitemap per project that has one")
    kf = OUT / f"{INDEXNOW_KEY}.txt"
    ok(kf.exists() and kf.read_text().strip() == INDEXNOW_KEY,
       "IndexNow key file present and contains exactly the key")
    # The key must be the SAME one the essay site serves, or a submission
    # naming one proves ownership of the other and the engines reject it.
    sys.path.insert(0, str(HERE.parent / "site"))
    try:
        import build as sitebuild
        ok(sitebuild.INDEXNOW_KEY == INDEXNOW_KEY,
           "key matches publish/site/build.py (no drift)")
    except Exception as e:
        ok(False, f"could not import publish/site/build.py to compare key: {e}")
    print(f"\n{'ALL CHECKS PASS' if not fails else f'{len(fails)} CHECK(S) FAILED'}")
    return not fails


if __name__ == "__main__":
    build()
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
