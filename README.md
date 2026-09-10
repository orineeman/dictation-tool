# כלי הכתבה מקומי (Push-to-Talk)

## הרצה חד-פעמית להתקנה
לחץ פעמיים על **setup.command** (רק פעם ראשונה, או אחרי שינוי ב-requirements.txt).

## הפעלה קבועה ברקע (בלי טרמינל, עולה לבד עם ההתחברות)
לחץ פעמיים על **install_autostart.command**. זה מגדיר "LaunchAgent" של מקוס שמריץ
את הכלי בשקט ברקע, בלי חלון טרמינל גלוי, ומעלה אותו אוטומטית בכל פעם שאתה נכנס למחשב.

**חשוב:** בפעם הראשונה שמריצים ככה, מקוס עשוי לבקש שוב את שלוש ההרשאות (Microphone,
Accessibility, Input Monitoring) — הפעם עבור התוכנה הספציפית ולא עבור Terminal. אם
המקש לא עובד אחרי ההתקנה, פתח System Settings ← Privacy & Security, ובכל אחת משלוש
הקטגוריות לחץ **+** והוסף ידנית את:
`/opt/homebrew/opt/python@3.14/Frameworks/Python.framework/Versions/3.14/Resources/Python.app`
(אפשר להשתמש ב-Cmd+Shift+G בחלון הבחירה כדי להדביק את הנתיב ישירות).

**שימו לב:** למרות ש-`venv/bin/python3` הוא ה"קובץ" שה-LaunchAgent מריץ, הוא בסך הכל
symlink שמצביע על ה-Python של Homebrew, וזה בפועל מריץ את `Python.app` שבתוך ה-framework
(אפשר לוודא עם `ps aux | grep dictation.py`). מקוס מזהה הרשאות לפי הבינארי שבאמת רץ, אז
צריך להוסיף את *זה*, לא את `venv/bin/python3` — אחרת תמיד יופיע "not trusted" ב-
`dictation.err.log` וה-hotkey פשוט לא יגיב, גם שה-LaunchAgent עצמו רץ תקין. אחרי ההוספה
(ובדיקה שהמתג דלוק), הרץ שוב את install_autostart.command.

**חשוב גם:** ה-LaunchAgent (`install_autostart.command`) מגדיר כמה משתני סביבה שחיוניים
כדי שהכלי יעבוד כמו שצריך ברקע (בניגוד להרצה ידנית מ-Terminal, ש"יורשת" את זה אוטומטית
מהמעטפת שלך):
- `PATH` שכולל את `/opt/homebrew/bin` — כדי ש-`ffmpeg` (שדרוש לפענוח האודיו) יימצא. ל-launchd
  יש PATH מינימלי משלו שלא כולל את תיקיות Homebrew, אז בלעדי זה מקבלים
  `transcription error: [Errno 2] No such file or directory: 'ffmpeg'` גם אם ffmpeg מותקן.
- `HF_HUB_OFFLINE=1` — כדי שהכלי לא ינסה לפנות לאינטרנט (ל-huggingface.co) בכל תמלול כדי
  לבדוק עדכונים למודל. המודל כבר שמור מקומית אחרי ההורדה הראשונה, אז אין בכלל צורך ברשת —
  ובלי המשתנה הזה, כל חסימת רשת/פרוקסי (למשל פילטרים כמו Rimon/Netspark) תגרום לשגיאת
  `Expecting value: line 1 column 1 (char 0)` בכל לחיצה.
- `PYTHONUNBUFFERED=1` — כדי שהלוגים ב-`logs/dictation.log` ייכתבו מיד ולא יישארו ריקים.

אם אתה משנה את הקובץ הזה או בונה LaunchAgent בעצמך, כדאי לשמור על שלושתם.

לביטול ההפעלה האוטומטית: לחץ פעמיים על **stop_autostart.command**.

## הרצה ידנית (לבדיקות, עם טרמינל גלוי)
לחץ פעמיים על **run.command**.

## שימוש
- החזק את מקש ה-**Option** (ימני או שמאלי), דבר בעברית, שחרר.
- הטקסט המתומלל יוקלד אוטומטית בשדה שבו נמצא הסמן שלך (בכל אפליקציה) —
  **חשוב: השדה חייב להיות ה-focus הפעיל ברגע שאתה משחרר את המקש**, אז אל תעבור
  בין חלונות תוך כדי הדיבור.
- אם ההקלדה האוטומטית לא עובדת מסיבה כלשהי, הטקסט מועתק אוטומטית ללוח (Clipboard) — הדבק עם Cmd+V.
- ההקלדה עובדת בכל אפליקציה/דפדפן כי היא מדמה אירועי מקלדת אמיתיים ברמת המערכת (לא ספציפית
  לאפליקציה). היוצא מן הכלל היחיד: שדות "Secure Input" (סיסמאות, פרומפט sudo בטרמינל) —
  מקוס חוסם שם הזרקת מקשים סינתטית מטעמי אבטחה, לכל תוכנה שהיא, לא ניתן לעקוף.
- המיקרופון נפתח רק בזמן ההקלטה בפועל ונסגר מיד אח"כ, כדי לא לצרוך משאבים כשלא בשימוש.
- הכל רץ לגמרי מקומית ולא דורש אינטרנט (גם התמלול עצמו) — אפשר לכבות Wi-Fi ולהמשיך לעבוד
  רגיל, כל עוד המודל כבר הורד פעם אחת (הוא שוקל כ-1.5GB בדיסק, ב-
  `~/.cache/huggingface/hub/models--mlx-community--whisper-large-v3-turbo`).
- כשהכלי יושב ברקע בלי לעבוד (לא לוחצים על המקש) הוא לא צורך CPU כלל, ומחזיק קצת זיכרון
  (כ-300MB אחרי תמלול ראשון, כי המודל נשאר טעון בזיכרון כדי שתמלולים הבאים יהיו מהירים).

## בדיקת לוגים (כשרץ ברקע בלי טרמינל גלוי)
`~/dev/dictation-tool/logs/dictation.log` (פלט רגיל) ו-`dictation.err.log` (שגיאות).

## שינוי מקש הקיצור
פתח את `dictation.py`, שנה את השורה:
```python
HOTKEY_KEYS = {Key.alt, Key.alt_l, Key.alt_r}
```
לדוגמה ל-`{Key.cmd_r}` (⌘ ימני) או `{Key.ctrl_r}` (⌃ ימני). שמור, ואם מותקן כרקע קבוע — הרץ install_autostart.command שוב (או פשוט `run.command` אם רץ ידנית).

## שלבים הבאים (לא כלול עדיין)
- אייקון ב-menu bar עם אינדיקציה חזותית (מקליט/מתמלל/מוכן).
- הגדרות בלי לערוך קוד (מיקרופון, מודל, מקש קיצור).

## פתרון תקלות
- **"command not found: python3"** — התקן Python מ- https://www.python.org/downloads/ (3.10+), הרץ שוב את setup.command.
- **"ffmpeg not found"** — אם רץ ידנית (run.command): התקן Homebrew מ- https://brew.sh ואז
  `brew install ffmpeg`, או פשוט הרץ setup.command שוב. אם רץ כ-LaunchAgent ברקע וזה עדיין
  קורה למרות ש-ffmpeg מותקן — כנראה install_autostart.command לא כולל את משתנה ה-PATH עם
  `/opt/homebrew/bin` (ראה בסעיף ההפעלה ברקע למעלה); הרץ אותו שוב כדי לרענן את ה-plist.
- **שגיאת SSL בהורדת המודל** — נפוץ במחשבי עבודה עם פרוקסי/אנטי וירוס. `pip-system-certs` כבר ב-requirements.txt כדי לפתור את זה.
- **`transcription error: Expecting value: line 1 column 1 (char 0)`** — סימן שמשהו ברשת
  (פרוקסי, פילטר תוכן כמו Rimon/Netspark, אנטי וירוס) חוסם גישה ל-huggingface.co ומחזיר דף
  HTML במקום JSON. הפתרון: `HF_HUB_OFFLINE=1` (כבר מוגדר כברירת מחדל ב-run.command וב-
  install_autostart.command) — כך הכלי לא מנסה בכלל לפנות לרשת ומשתמש רק במודל שכבר שמור
  מקומית. אם עדכנת את הקבצים האלה ידנית ואיבדת את זה, החזר את המשתנה והרץ מחדש.
- **ההקלטה לא מתחילה / כלום לא קורה בלחיצה** — בדוק הרשאת Input Monitoring ב-System Settings
  ← Privacy & Security (עבור Terminal אם רץ ידנית, או עבור `Python.app` הספציפי בתוך
  Python.framework של Homebrew אם רץ כ-LaunchAgent — ראה הסבר מפורט בסעיף ההפעלה ברקע למעלה
  למה זה לא venv/bin/python3).
- **הטקסט לא מוקלד לשום מקום** — אותו דבר, בדוק הרשאת Accessibility (על אותו Python.app).
  הטקסט בכל מקרה יועתק ללוח כגיבוי, חוץ משדות Secure Input (סיסמאות) שחוסמים גם את זה.
- **תמלול איטי מדי** — אפשר להחליף במודל קטן יותר בקובץ dictation.py, לדוגמה `mlx-community/whisper-medium` (פחות מדויק אבל מהיר יותר).
