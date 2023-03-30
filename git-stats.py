from subprocess import run
from collections import defaultdict
from re import compile

merge_authors = []

repo_path = r""
cmd = rf'cd "{repo_path}"; $env:GIT_PAGER = "cat"; git log --numstat --pretty=format:"%aN"'
output = run(["powershell", "-Command", cmd],
             capture_output=True, text=True).stdout

authors = defaultdict(lambda: {"additions": 0, "deletions": 0})

filePattern = compile(r'^\s*(\d+|-)\s*(\d+|-)\s*(.*\S)\s*$')
authorPattern = compile(r'^\s*(.*\S)\s*$')

lines = output.split("\n")
current_author = ""
for line in lines:
    if not line.strip():
        continue
    filePatternMatch = filePattern.match(line)
    if not filePatternMatch:
        authorPatternMatch = authorPattern.match(line)
        if authorPattern:
            current_author = authorPatternMatch.group(1)
        else:
            raise Exception("Unknown line: " + line)
    else:
        additions = filePatternMatch.group(1)
        deletions = filePatternMatch.group(2)
        fileName = filePatternMatch.group(3)
        if additions != "-":
            authors[current_author]["additions"] += int(additions)
        if deletions != "-":
            authors[current_author]["deletions"] += int(deletions)

if merge_authors:
    key_author = merge_authors[0]
    for merge_author in merge_authors:
        author = authors[merge_author]
        if not author or merge_author.lower() == key_author.lower():
            continue
        authors[key_author]["additions"] += authors[merge_author]["additions"]
        authors[key_author]["deletions"] += authors[merge_author]["deletions"]
        del authors[merge_author]

sorted_authors = sorted(
    authors.items(), key=lambda x: x[1]["additions"], reverse=True)

for author, stats in sorted_authors:
    print(f"{author}:")
    print(f"  Additions: {stats['additions']}")
    print(f"  Deletions: {stats['deletions']}")
