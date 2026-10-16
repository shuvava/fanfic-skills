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
| «Опубликовать автоматически» — a checkbox that opens a date-and-time picker (knockout `autoPublish` / `autoPublishTime`, a moment in the **browser's time zone**; hidden field `AutoPublishTime` in UTC). With it checked, «Опубликовать» becomes **«Запланировать публикацию»**; toast «…будет опубликована автоматически по таймеру»; the chapter list shows the date instead of «не опубликовано». **«Сохранить черновик» does not save the schedule** | known |
| Work's annotation: a field on the work's edit page, separate from the chapters; its length limit, whether it takes formatting, whether saving it notifies readers | to map |
| **Several forms on the chapter's edit page** (the first is the site search): the chapter form is the one that contains `#Text`, never `document.forms[0]` | known |
| `html.set` fills the editor, not the form: the form can post the old text. Before saving, `#Text.value = froalaEditor('html.get')`; `new FormData(<chapter form>).get('Text')` then holds the new text | known |
| Form buttons: a click by the browser tool's reference or coordinates sometimes sends nothing; `button.click()` from page JS on the button found by its label saves on the first press | known |
| Edit page of a chapter on a timer: buttons «Запланировать публикацию» and «Сохранить черновик». Saving with «Запланировать публикацию» keeps the timer and replaces the text — re-fetching the page shows the new text and the same `autoPublishTime` | known |
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
   **Delayed publication:** the user's yes names a date **and a time zone for readers** — the picker
   runs in the browser's zone, which may not be the readers'. Tick «Опубликовать автоматически», set
   the time on the page's own model, press «Запланировать публикацию», then confirm the saved UTC time
   by re-fetching the edit page (`autoPublishTime`). Record with `record --date <publication date>`.
   Until the timer fires the chapter is queued: it changes only at the user's request, by
   **Re-uploading a queued chapter** below.

**Re-uploading a queued chapter** (`SKILL.md` → Editing a queued chapter):

1. Open the chapter's edit page `/work/edit/chapter/<chapterId>` (chapter id from the project's
   notes or the ledger URL). Note the timer: re-fetch the page and read `autoPublishTime` — this is
   the value to keep.
2. Find the chapter form as the form containing `#Text` (not `document.forms[0]`).
3. Images first, as in step 3 of the flow, if the export's pictures changed; unchanged pictures
   keep their `content` URLs from the current text.
4. `jQuery('#Text').froalaEditor('html.set', <export html>)`, then
   `#Text.value = jQuery('#Text').froalaEditor('html.get')` so the form posts the new text. Check
   `new FormData(<chapter form>).get('Text')` holds it before pressing anything.
5. Press «Запланировать публикацию» from page JS (`button.click()` on the button with that label)
   — never «Сохранить черновик», which does not save the schedule.
6. Re-fetch the edit page: `autoPublishTime` equals step 1's value, and the chapter list still shows
   the date, not «не опубликовано». Different → **STOP**, restore the time (Moving a timer), report.
7. Read back (below) and compare a hash of the normalised text with the export's — equal, or the
   differing paragraphs.

**Moving a timer** (to map, first run): open the chapter's edit page while it still shows
«не опубликовано», set the new time on the same model as above, press «Запланировать публикацию»,
and re-fetch `autoPublishTime`. Record the exact controls in the table above once observed. Only
then `publication.py reschedule`.

**Annotation** (to map, first run): open the work's edit page, fill the annotation field from the
book's `SYNOPSIS.md` → `## Annotation` (**STOP: user** approves the text first), save, and reload
the page to read the field back. Record the limit and field behaviour above once observed.

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
