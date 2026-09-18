# videforsleep — وثائقي النوم بمانغا سوداء

وثائقي نوم هادئ جداً، مصمم لمساعدتك على النوم.

## ما تم إنجازه

### 🎨 الصور — Black Manga Style
5 لوحات مانغا سوداء بأسلوب حبر ياباني، 16:9، أبيض وأسود فقط:
- `scene-village.png` — قرية نائمة تحت قمر كبير
- `scene-forest.png` — ثعلب نائم تحت شجرة مع يراعات
- `scene-lake.png` — بحيرة ساكنة وانعكاس القمر
- `scene-train.png` — محطة قطار ليلية مع مطر خفيف
- `scene-observatory.png` — مرصد قديم تحت سماء مليئة بالنجوم

### 🎙️ الصوت — Deep Calm Sophisticated Voice
- تم تجربة 10 أصوات (voice-00 إلى voice-09) للعثور على الأعمق والأهدأ
- تم اختيار **voice-09** كأعمق صوت
- تم إنشاء نسختين:
  1. **الأصلية**: `sleep_documentary_black_manga.mp4` — صوت مباشر
  2. **العميقة المريحة (موصى بها)**: `sleep_documentary_DEEP_CALM.mp4` — معالجة احترافية:
     - خفض الطبقة 12% (rubberband pitch 0.88)
     - إبطاء 6% (tempo 0.94)
     - فلتر دفء lowpass 3200Hz
     - ضغط ناعم compressor
     - صدى خفيف جداً aecho ليعطي إحساس غرفة هادئة

### 🎧 المؤثرات الصوتية
خلفية مولدة برمجياً:
- ضوضاء بنية Brown Noise (مريحة للنوم أكثر من White Noise)
- نغمة منخفضة 55Hz + 110Hz مع LFO بطيء 0.03Hz (نبض هادئ)
- ريح ليلية مصنوعة من filtered noise مع تموج 0.01Hz
- مستوى الخلفية 22% من صوت السرد — لا يغطي الكلام

### 📖 القصة — 6 فصول (3:28 دقيقة)
1. **مقدمة** (27ث) — تنفس ببطء، شهيق 4 ثوان، زفير 6 ثوان
2. **القرية النائمة** (34ث) — قرية تنطفئ مصباحاً بعد مصباح
3. **غابة الثعلب** (35ث) — ثعلب ملتّف، الغابة تتنفس معه
4. **البحيرة الساكنة** (32ث) — الماء يأخذ التوتر
5. **محطة المطر** (30ث) — لا قطار قادم، الزمن توقف
6. **المرصد والنجوم** (36ث) — نوم عميق تحت سماء واسعة

## الملفات

```
assets/
  scene-village.png
  scene-forest.png
  scene-lake.png
  scene-train.png
  scene-observatory.png
audio/
  01_intro.mp3 ... 06_observatory.mp3 (الأصلي)
output/
  sleep_documentary_black_manga.mp4 (17MB, 3:15)
  sleep_documentary_DEEP_CALM.mp4 (17MB, 3:28) ← موصى به
  ambient.wav (خلفية النوم)
  deep_*.wav (السرد المعالج الأعمق)
index.html (معاينة جميلة)
```

## التشغيل

افتح `index.html` في المتصفح، أو شغل الفيديو مباشرة:

```bash
ffplay output/sleep_documentary_DEEP_CALM.mp4
```

## كيف تم تحسين الصوت ليكون عميق وراقي

المستخدم طلب: "Both voices are bad; I want a calm, deep, and soothing voice—something deep, calming, and sophisticated."

الحل:
- تجربة 10 أصوات مختلفة
- اختيار أعمق صوت (voice-09 masculine narration)
- معالجة إضافية بـ FFmpeg rubberband لجعله أعمق وأبطأ وأكثر دفئاً
- إضافة lowpass لإزالة الحدة، وcompressor لجعله متساوي ومريح

النتيجة: صوت عميق جداً، بطيء، راقي، مناسب لوثائقي نوم احترافي.

## الترخيص

المشروع للاستخدام الشخصي للنوم والاسترخاء.
