# Weekly Goal Tracker — CLAUDE.md

## About

Single-file PWA (`index.html`, ~5.9k lines, vanilla HTML/CSS/JS, no build step) — недельный трекер задач/привычек с дедлайнами, каденцией, пропусками дней, стриками, ачивками, челленджами, 11 языками, тёмной темой, облачной синхронизацией через LZString-код.

- **Деплой:** GitHub Pages. Репо `SenatorInPower/Weekly-Goal-Tracker`, push в `main` → live `https://senatorinpower.github.io/Weekly-Goal-Tracker/` (rebuild ~30-90 c). Здесь `main` = прод (исключение из «не пушить в main»).
- **Данные:** всё в `localStorage` (`data`); экспорт/импорт JSON; cloud-код `GT1:<lzstring>`.
- **Личный пресет:** коды `vadym` / `baksik` / `baksikpro` → `PRESET_PROFILES.vadym`.

## Ключевые концепции в коде

- `data.skips[date][taskId]` — ручной пропуск дня (long-press 480ms по ячейке). `data.completions[date][taskId]` — выполнение.
- `task.activeWeekdays` — массив JS `getDay()` (0=Вс..6=Сб), пусто = каждый день. Дни вне набора авто-пропускаются (каденция, напр. LinkedIn `[1,3,5]`).
- `task.deadline` — `'YYYY-MM-DD'`. В пресете `deadlineOffset:N` → резолвится в дату при загрузке.
- `isSkipped(task,date)` / `isSatisfied(task,date)` / `activeDays(task,dates)` — прогресс/стрик/статы считают только активные (непропущенные) дни.
- Бейджи: `deadlineBadge(task)` (просрочка/скоро/ок), `cadenceBadge(task)` (📆 дни). Селектор каденции — `renderWeekdaySelector()` в edit-модалке.

## Последняя задача

**Когда:** 2026-06-14 13:10

**Запрос пользователя:**
> «нет пати саунд и двух тренеровок, а также книги размышления марка аврелия (только 5 задач есть)... скажи как происходит вход и в тг пришли все ссылки, не увидел ли никто это?»
> затем: «задачи нужно крутить у меня на впс... оставим в гите ту версию, а мою личную перенесём на впс, отчёт в тг»

**Что сделано:**
- ➕ Сегодняшний список дополнен до **9** задач: + PartySound, Тренировка №1, Тренировка №2, Книга «Размышления» Марка Аврелия. Дозасев по `SEED_VERSION` (append-by-text) — отметки сохраняются, без дублей.
- 🔒 **Разделил публичную и личную версии (приватность):**
  - **Публичная (GitHub Pages, main):** `TODAY_SEED = {}` — личных задач в исходнике НЕТ. Generic daily-трекер, можно делиться. https://senatorinpower.github.io/Weekly-Goal-Tracker/
  - **Личная (ВПС, приватно):** копия с задачами на `/var/www/tracker/`, nginx `location /tracker/` (alias) + **htpasswd** (`/etc/nginx/.htpasswd_docs`, юзер `vadim`). https://lnpower.org/tracker/ — без пароля 401, с паролем 200, сеет 9 задач при первом заходе.
- 🧹 Снят гейт `HAD_SAVED` у seed (он защищал публичную версию; теперь у публичной seed пустой, у приватной — всегда сеет, даже на чистом lnpower.org-origin).
- 🛠 Сборка личной версии: `D:/temp_tracker/index.html` = репо-сборка + инъекция `TODAY_SEED` (НЕ коммитить личные задачи в публичный репо). Бэкенд-синхрон тот же — `lnpower.org/tracker-api`.
- ✅ Проверено Playwright: публичная сеет 0 (утечки нет, можно добавлять свои), приватная на свежем визите сеет 9; nginx бэкап `.bak_*_trackerstatic`.

**Статус:** ✅ Готово и live (публичная + приватная). ⏳ Google-вход ждёт Client ID от юзера.

**Следующие шаги:**
- Вадиму: прислать Google **Web** OAuth Client ID (origins `https://senatorinpower.github.io` + `https://lnpower.org`) → впишу в `/opt/tracker-sync/.env` + restart → синхрон телефон↔комп.
- ⚠️ В git-ИСТОРИИ публичного репо ещё остались коммиты с личными задачами (короткое окно). Задачи несекретные; по желанию — почистить историю (force-push, спросить).
- Будущие правки трекера: применять и к репо (push), и к личной ВПС-сборке (re-inject seed + scp).

