# سجل اختبار تنويع الأفكار

## الحكم

تم تطبيق واختبار تنويع الاختيار الحتمي بنجاح. قبل التعديل، كانت كل أفكار `generate` التسع في التاريخ من فئة `ecommerce`، وكانت سجلات الكتالوج بلا `shape`. بعد التعديل، يقرأ picker آخر أربع منتجات أسبوعية نشطة من `catalog.json` ويستبعد الفئة والshape الحديثة عندما يوجد بديل.

هذا التعديل لا يغير prompt أو provider chain أو بوابات HTML وChromium. الاختبار الحقيقي أثبت نجاح **اختيار الفكرة المتنوعة**، لكنه لم يثبت نجاح توليد LLM في نفس التشغيل لأن Groq وصل إلى حد TPM المجاني؛ لذلك سُجل التشغيل كـ fallback وليس كنجاح LLM.

## التغييرات

| الملف | التغيير |
|---|---|
| `automation/pick_idea.py` | ذاكرة catalog، آخر أربع فترات نشطة، استبعاد category ثم shape، وfallback آمن عند غياب البديل أو فساد catalog |
| `automation/build_catalog.py` | نسخ `shape` من backlog إلى `catalog.json` |
| `ideas/backlog.json` | إضافة shape إلى السجلات الحالية وإضافة أربع أفكار generate متنوعة من `services` و`design` و`content` و`wellbeing` |
| `automation/test_pick_idea_diversity.py` | اختبارات الاستبعاد، fallback، فساد catalog، وعدم تأثير القوالب |
| `docs/DIVERSITY-HARDENING-DESIGN.md` | عقد التنويع وقواعد السلامة |

## الاختبارات المحلية

نجحت اختبارات Python وYAML وJSON و`git diff --check`، واختبار picker للفترة `2026-w48` أعاد:

| الذاكرة الحديثة | القيمة |
|---|---|
| الفترات المستخدمة | `2026-w46`, `2026-w45`, `2026-w44`, `2026-w43` |
| الفئات المستبعدة | `ecommerce`, `productivity` |
| الأشكال المستبعدة | `checker`, `converter`, `sorter` |
| المرشح المختار في dry-run | `generate-010` — `services` / `comparator` |
| fallback category | `false` |
| fallback shape | `false` |

كما بقي اختيار Tier A مستقلًا عن ذاكرة التنويع؛ dry-run لقوالب `template:` لم يستبعد فئة ecommerce، وهو السلوك المقصود.

## التشغيل الحقيقي

[التشغيل 32612951967][1] للفترة `2026-w48` اختار فعلًا:

```text
id=generate-010
category=services
shape=comparator
```

وهذا يكسر تكتل `ecommerce` ويفصل البنية عن `checker/sorter/converter` الحديثة. الفكرة انتقلت إلى `built`، وظهر shape في `catalog.json`، ونُشر المنتج في `products/weekly/2026-w48/`، وأصبح الكتالوج يحتوي 16 بطاقة.

الاختيار المتنوع اجتاز static HTML وChromium والكتالوج وPages وTelegram. أما نتيجة provider chain فكانت `mode=fallback` و`provider=deterministic-fallback`، لأن Groq أعاد حد TPM المجاني: المستخدم `7977` توكنًا وطلب `6852` ضمن حد `8000`. لذلك لا أعد هذا التشغيل دليلًا على نجاح LLM، بل دليلًا على أن تنويع picker يعمل وأن fallback الآمن لا يمنع النشر المتحقق.

## السلامة وعدم التراجع

لم تُلمس prompts أو بوابات الأمان، ولم تُعاد فكرة مبنية، ولم تُحذف صفحة منشورة. إذا غاب catalog أو أصبح غير صالح، يختار picker من backlog الأصلي بدل إيقاف المصنع. وإذا لم يوجد مرشح خارج الفئة أو shape الحديثة، يتراجع تدريجيًا إلى قائمة مرشحين أوسع بدل الفشل أو اختيار duplicate مبني.

## References

[1]: https://github.com/lo77667/repositoryDz/actions/runs/32612951967 "Diversity selection run 2026-w48"
