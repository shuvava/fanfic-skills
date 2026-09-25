# author.today

Adapter for `publish` (and later `feedback`): **what is true of the platform for every project**.
Nothing here names a work, a chapter or a run — those live in the project's
`publish/platforms/author-today.md` (see `SKILL.md` → Settings).

**Describe the flow in words, not CSS selectors** — the site's markup changes; a step written as
"the «Добавить часть» button under the chapter list" survives a redesign that renames a class.
Every fact is marked **known** (observed on a live run) or **to map**.

## Facts about the site

| Fact | Status |
|---|---|
| A work is split into chapters ("части"), added with «Добавить часть» → `/work/<workId>/add/chapter` | known |
| **A work in черновик is invisible to everyone**; it can be published only once at least one chapter is. Publishing the first chapter publishes the work with it | known |
| Reader URL of a chapter: `https://author.today/reader/<workId>/<chapterId>` — the same `chapterId` as the edit page; the work page lists published chapters | known |
| Chapter page: «Заголовок» field (pre-filled «Глава N»), rich-text editor, «Опубликовать автоматически» checkbox, buttons «Опубликовать» (submit) and «Сохранить как черновик» (on an existing chapter: «Сохранить черновик») and «Отмена» | known |
| Editor: **Froala (jQuery plugin) on `textarea#Text`**; form posts to `/work/savechapter` with `Title`, `Text`, `Id` = work id, `ChapterId` (empty for a new chapter) | known |
| Allowed HTML: `p, br, b, strong, i, em, u, del, strike, blockquote, img, div, span, hr, ol/ul/li, table, pre, sub, sup, small, cite` — the export uses only `p`, `img` | known — editor options |
| Images: toolbar «Вставить изображение» → upload or by URL; jpeg/png/gif/webp/svg, **≤ 5 MB**; uploaded to `cm.author.today/content_temp/…`, moved to `…/content/…` when the chapter is saved; dimensions kept | known |
| «Оттипографить» — a **manual** typography button. Never press it: it would rewrite the author's dashes and quotes | known |
| The editor itself changes nothing on save: no autocorrect of `-` or `"` — read-back compares identical | known |
| «Просмотр HTML-кода» — source view | known |
| «Перезагрузка текста из FB2» on the work's Текст tab — whole-work import | known; not used |
| Saved chapter: listed on the Текст tab as «<title> — не опубликовано / опубликовано (N знаков)»; edit page `/work/edit/chapter/<chapterId>`; row icons on hover: edit, read, preview, delete. The site's character counter equals `verify`'s character count | known |
| Toasts: «Часть "…" была успешно сохранена в черновике» / «…была успешно опубликована» | known |
| Work's Текст tab shows «до следующего обновления: N зн.» — an update threshold of **15 000 characters** since the last update. What crossing it does for readers (feed, notifications) | known threshold; effect **to map** — may favour publishing in ~15k-character batches |
| «Опубликовать автоматически» — what it opens (date/time?) | to map |
| Editing a published chapter: notifies readers? | to map |
| Where comments live (per chapter / per work), pagination | to map (feedback) |

## Flow

**STOP: user** marks points that need the user's yes in chat.

1. Open `/work/<workId>/edit/content` (the project's notes give `<workId>`). Signed-out page →
   **STOP: user** signs in. Never type credentials.
2. `/work/<workId>/add/chapter`. Set «Заголовок» to the sidecar's `title`.
3. Images first: open «Вставить изображение», upload each file from the sidecar through the upload
   input Froala creates (the browser tool's file upload), and take the `content_temp` URL the
   editor inserts. Put it in the export's `<img src>` at its place. Local paths never reach the site.
4. Text through the editor's own API, not by typing or pasting:
   `jQuery('#Text').froalaEditor('html.set', <export html>)`; set the title field and fire
   `input`/`change` on it.
5. «Сохранить как черновик» — hidden save. **STOP: user** approves the upload in chat (a request to
   publish covers it). Back on the Текст tab the chapter shows «не опубликовано».
6. Read back (below).
7. «Опубликовать» on the chapter's edit page — **STOP: user**, per chapter, every time. Record the
   reader URL with `publication.py record`.

**Moving text in and out of the page.** Never retype chapter text into a script call — kilobytes
of hand-copied Cyrillic is where a letter changes. Load files through a temporary
`<input type=file>` the script adds and removes, filled with the browser tool's file upload, then
`file.text()`. Used for the export HTML (in) and the plain export (for the read-back compare).

**Locating elements.** Prefer page JS and `read_page` over the browser's natural-language `find`:
`find` spends model calls and fails first when the usage limit is near. Re-locate after every page
change — a stale reference can land on another element (once the site logo, which left the editor).

## Read-back

Open the saved chapter's edit page, take `jQuery('#Text').froalaEditor('html.get')`, and compare it
**in the page** against the `plain` export loaded through a temporary file input, with
`export_chapter.py`'s normalisation: drop `<img>`, `</p>`/`<br>` → newline, strip tags, unescape,
NBSP → space, collapse whitespace, drop empty lines. Report paragraphs, characters, image URLs and
each differing paragraph with the first differing character. Record the result in the project's
`publish/readback/author-today/b<NN>-ch<NN>.md`. (Copying the site's HTML back out through the
model would reintroduce the transcription risk the check exists to rule out.)
