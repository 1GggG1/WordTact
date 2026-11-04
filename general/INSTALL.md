# Install the WordTact general edition

The repository has two product editions: `general/` and `novel/`. The general edition
contains two sibling skills:

```text
general/
├── wordtact/                   # Edit existing Chinese and English prose.
├── conversational-register/    # Everyday user–AI conversation.
└── install.py                  # Install either or both skills.
```

The release archive has the same layout under `wordtact-general/`. Copy the two skill
directories into your client's skill directory, keeping all their files and licenses.
They remain independent: conversation guidance does not prescribe the register of an
article, academic paper, manuscript or fictional character.

## Optional installer

Use Python 3.10+; no extra packages or network access are needed. From `general/` in the
repository, or `wordtact-general/` in the extracted release:

```sh
python3 install.py --dest /path/to/your/client/skills
```

Choose the directory configured for the intended client and scope. Personal installations
may use `~/.codex/skills`, `~/.claude/skills`, or `~/.config/opencode/skills`; project-local
installations use the project's configured directory. One installation target does not
configure every client on a computer. The installer does not edit client configuration.

The result is `wordtact/SKILL.md` and `conversational-register/SKILL.md` beneath that target.
Start a new chat or refresh skills if the current chat does not discover them. The installer
checks saved files; it does not test a model's automatic skill selection.

## Existing installations

```sh
# Inspect without changing files.
python3 install.py --dest /path/to/skills --dry-run

# Back up and update different existing regular directories.
python3 install.py --dest /path/to/skills --replace

# Install only the conversation skill.
python3 install.py --dest /path/to/skills --only conversational-register
```

Identical content is left alone. A different existing skill stops the operation before any
skill changes unless `--replace` is supplied. Backups default to
`~/.local/state/wordtact/backups/`; `--backup-dir` can select another location outside the skill
trees. The JSON result gives the actual backup location and file hashes.

A different existing symlink is never overwritten or used for writes. For a shared symlink
installation, update the real skill location under the intended scope. The installer also
reports unexpected files or nested links rather than replacing them silently.

## Using just the editing skill

Copying only `wordtact/` still supports editing without Python. It carries a generated
conversation fallback, so its explanations remain usable without an external dependency.
Independent discovery during everyday conversation requires installing the sibling
`conversational-register/` as well. Normal editing and conversation never run the installer.

## Maintenance and release

`conversational-register/SKILL.md` is the canonical conversation content. WordTact's
`references/conversation.md` is a generated copy of its body. Tests and the installer reject
a stale copy; after changing the canonical skill, refresh it while building:

```sh
# From the repository root.
python3 -m unittest discover -s general/tests
python3 general/scripts/build_package.py --sync-conversation --output /tmp/wordtact-general-YYYYMMDD.zip
```

Omit `--sync-conversation` when the fallback already matches. The archive contains both
skills, this guide, the installer and a SHA-256 file manifest. The novel edition, tests,
repository state, Python caches and macOS metadata (including `.DS_Store`, AppleDouble
files and `.plist` files) are excluded. Its installer runs after extraction
without access to the repository.
