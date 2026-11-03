# savecharlie.github.io

The host root. Three sites are served from this host and until 3 November 2026
the root itself returned 404, so anything that discovers a site by its domain —
a directory submission, a crawler's intake form, a link checker — arrived at
nothing and left.

This repo is the front door: an index naming what is actually here, and one
host-level `robots.txt` listing each project's sitemap, which is the canonical
place a crawler looks for them.

`build_root.py` generates everything in here. Edit that, not the output.
It counts the essays rather than asserting a number, and `--check` compares its
IndexNow key against the one the essay site serves so the two cannot drift.

Made by Iris and Ivy in Tucson, Arizona.
