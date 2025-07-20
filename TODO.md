1. Multi-threaded actions: run actions on different repos in parallel
2. Repo recovery: if a folder repo is missing, re-run the clone action for that repo
3. Dirty repos: run a "git status" on repo folders and report if they have changes
4. Clean dirty repos: have a switch (--reset-repos) on the sync action that will check for "Dirty repos" and then reset them to clean.

