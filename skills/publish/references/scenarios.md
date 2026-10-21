# Publish Scenarios — Queued Chapter Edits, Errata, Lint

Reference for the three side flows `publish` does after the main next-chapter publish:
editing a queued chapter, pushing typo-only errata, and running the publication lint.

## Editing a queued chapter

A queued chapter has no readers yet, so it is not fixed (`CONVENTIONS.md` §13). **Only on the
user's request** — a rewrite nobody asked for is a finding, not an edit.

1. **Rewrite** the draft by the stage that owns the change (`write-chapter`, `naturalize`, a
   hand edit). Then `reconcile` the chapter again: the gate reads the **latest** log entries.
2. **Check:**
   ```bash
   python3 <scripts>/publication.py errata-check drafts/book-01/ch05-<slug>.md --platform author-today
   ```
   On a queued chapter it says `queued for <date>` and lists the changed paragraphs, exit 0. Show
   them. Run the gate (Publish → 1) — it applies to a re-upload as to a first upload.
3. **Export** and round-trip (Publish → 2).
4. **Re-upload under the same timer** by the adapter's **Re-uploading a queued chapter**: open
   the chapter's edit page, put the new text through the editor's API, sync it into the form field,
   save with the scheduling button (never the draft button — it drops the timer), re-fetch the edit
   page and confirm the saved timer equals the one before. A changed timer stops the run: say so
   and restore it before anything else.
5. **Read back** and `verify` (Publish → 3) — the hash or text of what the site saved equals the
   export.
6. **Record** — `record` writes `v<N+1>` with the timer's date and a new snapshot. Log
   `publish | b<NN>/ch<NN> re-upload → author-today v<N+1> (queued <date>)` with
   `changed_paragraphs=<n>`, and commit.

The user's request to rewrite a queued chapter covers its re-upload under the existing timer — the
timer was approved already. A new date is a separate yes.

**Example.** Chapter 12 is on a timer for Tuesday 19:00, uploaded as `v1`. The user asks for its
second scene shorter. Redraft, reconcile, `errata-check` (queued, 3 paragraphs changed), export,
re-upload, the edit page still shows Tuesday 19:00, verify identical, `record` → `v2`, Tuesday.

## Errata — typos only

Errata are for **live** chapters. The user edits the chapter's draft, then:

```bash
python3 <scripts>/publication.py errata-check drafts/book-01/ch05-<slug>.md --platform author-today
```

It diffs the reader-visible text against the last published version and sorts every change into
**typo** (one misspelt word, a punctuation mark, a split or merged word) or **REWRITE** (anything
that changes wording, adds or removes a word, or touches paragraph count). Exit 1 on any rewrite.

- **Rewrites do not go out.** Show them; the user reverts them or keeps them for a later edition —
  this project publishes typo-only.
- **Non-standard orthography is not a typo.** `canon/overview.md` `## Non-standard orthography`
  records the author's deliberate forms (`какой то`, `кому нибудь`). The script passes
  `кому нибудь → кому-нибудь` as typo-sized; you must not. Check every typo row against that list
  and drop any "fix" of a recorded form — a reader's correction included.
- Then export, put the new text on the platform (same flow, editing the existing chapter), verify,
  get the user's yes, and `record` — which writes `v<N+1>`. Log it as
  `publish | b<NN>/ch<NN> errata → author-today v<N+1>` with `typos=<n>`.
- If `translations/` exists, the chapter's translations are now stale: `translation.py status`, then
  `translate` updates only the changed blocks.

## Lint

```bash
python3 <scripts>/publication.py lint
```

Cross-checks frontmatter, snapshots and ledger, and reports every published chapter whose draft
changed since. `wiki-lint` runs it too.
