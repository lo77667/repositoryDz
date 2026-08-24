# سجل حارس إعادة استخدام الفترة الأسبوعية

## الحكم

تم إصلاح فشل التشغيل `32719459833` بإضافة حارس idempotency قبل `pick_idea.py` في workflow الأسبوعي. الحارس يمنع استهلاك فكرة أو تعديل backlog عندما تكون الفترة منشورة مسبقًا، ويحافظ على رفض overwrite داخل `build_weekly_product.py` كخط دفاع أخير.

## السبب الأصلي

التشغيل [32719459833][1] كان تشغيلًا مجدولًا بلا فترة صريحة. حسب workflow الفترة الحالية `2026-w35`. كانت الصفحة `products/weekly/2026-w35/index.html` موجودة أصلًا لكنها تخص منتجًا مختلفًا، بينما اختار picker الفكرة `text-001` «مصقول وصف المنتج». أوقف مولد المنتج التنفيذ برسالة `Refusing to overwrite an existing different artifact` قبل أي بوابة أو نشر. لم يتغير backlog على `main`، وأُرسل إشعار فشل Telegram بنجاح.

## التغيير

أُضيفت `automation/guard_weekly_period.py`، وتعمل قبل picker:

| الحالة | السلوك |
|---|---|
| فترة جديدة | تكتب `decision=proceed`، ثم يستمر picker والبناء والبوابات والنشر كالمعتاد |
| فترة منشورة مع تشغيل بلا فترة صريحة | تنهي التشغيل بنجاح idempotent كـ `already_published`، ولا تختار فكرة ولا تعدل backlog، وترسل Telegram بإشعار واضح |
| فترة منشورة مع فترة يدوية صريحة | ترفض العملية قبل picker، ثم ترسل إشعار فشل مع رابط التشغيل |
| سباق أو خطأ لاحق | يبقى `build_weekly_product.py` رافضًا استبدال artifact مختلف |

## الاختبار المحلي

نجح `automation/test_guard_weekly_period.py` في اختبار الفترة الجديدة، no-op للفترة الحالية المنشورة، ورفض إعادة الاستخدام اليدوي. كما نجحت اختبارات Python وYAML وpicker وlifecycle والكتالوج والأمن.

## الاختبارات الحقيقية

| الاختبار | التشغيل | النتيجة |
|---|---|---|
| no-op بلا فترة صريحة | [32767321437][2] | نجح؛ اكتشف `2026-w35` المنشورة، أنهى المسار قبل picker، وأرسل إشعار `already-published` إلى Telegram |
| إعادة استخدام يدوي | [32767380959][3] | فشل مقصود؛ رفض `2026-w35` قبل picker، ولم يُنشئ artifact أو commit، وأرسل إشعار الفشل |
| الحالة الأصلية قبل الإصلاح | [32719459833][1] | فشل غير مرغوب سابقًا؛ وصل إلى build ثم اصطدم بحماية overwrite |
| مسار LLM بلا فترة صريحة | [32774375830][4] | نجح no-op؛ تخطى تثبيت المتصفح وpicker والمزودين والبناء والنشر، وأكمل إشعار `already-published` |
| إعادة استخدام يدوي عبر مسار LLM | [32774533800][5] | فشل مقصود؛ فشل guard، تخطى picker والمزودين والنشر، وأكمل إشعار الفشل |

حالة `main` بعد اختبارات الحارس الأصلية بقيت نظيفة على commit `a4c0556` قبل توثيق السجل الأول، ولم يتغير `ideas/backlog.json` بسبب أي من اختبارَي الحارس. GitHub Pages بقيت `built`. وبعد إضافة حارس مسار LLM في commit `5ccfd48` واختباريه الحقيقيين، بقيت بصمات `ideas/backlog.json` و`catalog.json` وartifact `2026-w35` ثابتة، وبقي remote `main` على commit `ccd17a8` بعد التصحيح الصغير الأخير.

## القرار التشغيلي

يظل اختيار فترة لاحقة تلقائيًا ممنوعًا، لأن ذلك سيشوّه معنى «منتج واحد لكل أسبوع». التشغيل المجدول الذي يجد الفترة الحالية منشورة يعامل الحالة كنجاح بلا تغيير، أما التشغيل اليدوي بفترة مستخدمة فيحتاج تصحيح الفترة أو طلب إعادة تحقق منفصلًا.

## References

[1]: https://github.com/lo77667/repositoryDz/actions/runs/32719459833 "Original failed weekly run"
[2]: https://github.com/lo77667/repositoryDz/actions/runs/32767321437 "Real already-published no-op test"
[3]: https://github.com/lo77667/repositoryDz/actions/runs/32767380959 "Real manual period reuse rejection test"
[4]: https://github.com/lo77667/repositoryDz/actions/runs/32774375830 "Real LLM already-published no-op test"
[5]: https://github.com/lo77667/repositoryDz/actions/runs/32774533800 "Real LLM manual period reuse rejection test"
