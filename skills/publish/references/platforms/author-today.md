# author.today

Adapter for `publish` (and later `feedback`). **Describe the flow in words, not CSS selectors** —
the site's markup changes; a step written as "the «Добавить часть» button under the chapter list"
survives a redesign that renames a class. Every fact below is marked **known** (from the user or
observed) or **to map** (Phase 2, with the user watching their own Chrome).

## Project settings

| Key | Value | Source |
|---|---|---|
| Work edit page | `https://author.today/work/657773/edit/content` | known — the user, 2026-09-25 |
| Export format | `author-today` in `export_chapter.py` — HTML fragment, `<p>` per paragraph, centred `* * *`, `<img>` in place | built; whether the editor accepts it **to map** |
| Images | inside the chapter text, at their place | known — the user's decision |
| Cadence | 2 chapters a week | known — the user |
| Edits after publication | typos only | known — the user |

## Facts about the site

Observed 2026-09-25 in the user's Chrome, signed in (work «Ядро души 4», status черновик).

| Fact | Status |
|---|---|
| A work is split into chapters ("части"), added with «Добавить часть» → `/work/<id>/add/chapter` | known — observed |
| **A work in черновик is invisible to everyone**; it can be published only once at least one chapter is. Publishing the first chapter published the work with it (b01/ch01, 2026-09-25, done by the user) | known — observed |
| Reader URL of a chapter: `https://author.today/reader/<workId>/<chapterId>` — the same `chapterId` as the edit page; the work page lists published chapters | known — observed |
| Chapter page: «Заголовок» field (pre-filled «Глава N»), rich-text editor, buttons «Опубликовать» and «Сохранить как черновик» | known — observed |
| Editor: **Froala (jQuery plugin) on `textarea#Text`**; form posts to `/work/savechapter` with `Title`, `Text`, `Id`=work id, `ChapterId` (empty for a new chapter) | known — observed |
| Allowed HTML: `p, br, b, strong, i, em, u, del, strike, blockquote, img, div, span, hr, ol/ul/li, table, pre, sub, sup, small, cite` — our export uses only `p`, `img` | known — editor options |
| Images: toolbar «Вставить изображение» → upload or by URL; jpeg/png/gif/webp/svg, **≤ 5 MB**; uploaded to the site through the editor | known — editor options |
| «Оттипографить» — a **manual** typography button. Never press it: it would rewrite the author's dashes and quotes | known — observed |
| «Просмотр HTML-кода» — source view exists | known — observed |
| «Перезагрузка текста из FB2» on the work's Текст tab — whole-work import | observed; not used |
| Delayed publication of a chapter | a checkbox **«Опубликовать автоматически»** under the editor, next to «Опубликовать» / «Сохранить как черновик»; what it opens (date/time?) **to map** |
| Saved chapter | listed on the Текст tab as «Глава 1. Слух — не опубликовано (8 796 знаков)»; edit page `/work/edit/chapter/<chapterId>` (ch01 = 6304685); row icons: edit, read, preview, delete. The site's character counter equals `verify`'s character count | known — observed |
| Images on save | uploaded to `cm.author.today/content_temp/…`, moved to `…/content/…` on save; dimensions kept (1176×786) | known — observed |
| Editing a published chapter: notifies readers? | to map |
| Work's Текст tab shows «до следующего обновления: N зн.» — an update threshold of **15 000 characters** since the last update (after ch02: 16 209 total, 7 587 to go). What crossing it does for readers (feed, notifications) | observed; effect **to map** — it may favour publishing in ~15k-character batches |
| Chapter edit page buttons: «Опубликовать» (submit), «Сохранить черновик», «Отмена». Success toast: «Часть … была успешно опубликована» | known — observed, b01/ch02 |
| The browser's `find` tool uses model calls and fails at the usage limit; locate elements with page JS and `read_page` instead | known — hit 2026-09-25 |
| Where comments live (per chapter / per work), pagination | to map (feedback) |

## Flow

Steps observed so far; **STOP: user** marks points that need the user's yes in chat.

1. Open `/work/<id>/edit/content`. Signed-out page → **STOP: user** signs in. Never type credentials.
2. `/work/<id>/add/chapter`. Set «Заголовок» to the sidecar's `title`.
3. Text through the editor's own API, not by typing or pasting:
   `jQuery('#Text').froalaEditor('html.set', <export html>)` — then read it back with
   `jQuery('#Text').froalaEditor('html.get')` for `verify`.
4. Images: upload each file from the sidecar through the image button's upload input (the file-upload
   tool on the input Froala creates), take the site URL the editor inserts, and put it in the
   export's `<img src>` at its place before step 3. Local paths never reach the site.
5. «Сохранить как черновик» — hidden save. **STOP: user** approves this upload in chat. The site
   confirms «Часть … была успешно сохранена в черновике» and returns to the Текст tab.
6. Read back (below). 7. «Опубликовать» — **STOP: user**, per chapter, every time.

**Moving text in and out of the page.** Never retype chapter text into a script call — 9 KB of
hand-copied Cyrillic is where a letter changes. Load files through a temporary
`<input type=file>` the script adds and removes, filled with the browser tool's file upload, then
`file.text()`. Used for the export HTML (in) and the plain export (for the read-back compare).

**Stale element references navigate.** A reference from an earlier page can land on another
element — once it hit the site logo and left the editor. Re-`find` after every page change.

## Read-back

Open the saved chapter's edit page, take `jQuery('#Text').froalaEditor('html.get')`, and compare it
**in the page** against the `plain` export loaded through a temporary file input, with
`export_chapter.py`'s normalisation: drop `<img>`, `</p>`/`<br>` → newline, strip tags, unescape,
NBSP → space, collapse whitespace, drop empty lines. Report paragraphs, characters and each
differing paragraph with the first differing character. Record the result in
`publish/readback/author-today/b<NN>-ch<NN>.md`. (Copying the site's HTML back out through the
model would reintroduce the transcription risk the check exists to rule out.)

b01/ch01, 2026-09-25: **identical** — 32/32 paragraphs, 8796/8796 characters; the editor changed
nothing (no autocorrect of `-` or `"`).
