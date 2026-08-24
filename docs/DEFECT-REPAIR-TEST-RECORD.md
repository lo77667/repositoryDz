# سجل إصلاح عيوب repositoryDz

## نطاق الإصلاح

أُجريت المراجعة على المصنع الأسبوعي، مسار توليد LLM، الأدوات المساعدة، الكتالوج، القوالب، المنتجات المنشورة، وبوابات HTML وChromium. نُفذت الإصلاحات تدريجيًا مع الحفاظ على المنتجات والـworkflows والمحتوى القائم؛ لم يُحذف أي artifact أو backlog idea أو سجل تاريخي.

## مصفوفة العيوب والإصلاحات

| المعرّف | العيب المؤكد | الإصلاح | حالة التحقق |
|---|---|---|---|
| F-01 | مسار LLM لم يكن يمر عبر حارس الفترة، وكان provider/fallback يكتبان مباشرة إلى artifact النهائي | أضيف guard قبل picker في workflow LLM، وأضيف رفض overwrite إلى provider chain وfallback | مؤكد محليًا وفعليًا في التشغيلين [1] و[2] |
| F-02 | تحقق الفترة كان شكليًا ويقبل `w00` و`w54` و`w99` | أضيفت `period_utils.py` مع تحقق `date.fromisocalendar`، وربطت بالـguard وpicker وbuilder وweekly validator وcatalog | اختبارات ISO وYAML وcompileall ناجحة |
| F-03 | lifecycle يقبل صيغة replacement ثم لا يرسمها catalog بصيغتها المختلفة | أضيفت `replacement_utils.py` لتوحيد directory/index forms ورفض weekly root والفترات غير الحقيقية | اختبارات lifecycle وcatalog ناجحة |
| F-04 | validator الكتالوج كان يفحص شكل الرابط دون وجود الهدف | أضيف فحص وجود `index.html` لكل product/replacement link، ووسّعت بوابة Chromium لفتح كل الروابط | مصفوفة Chromium: 18 بطاقة و19 رابطًا فُتحت بنجاح |
| F-05 | صفحات w38 وw39 احتوت inline handlers | أزيلت attributes فقط، ووُصلت نفس الدوال بـ`addEventListener` | static وChromium gates ناجحة |
| F-06 | القوالب والمنتجات deterministic لم تكن تحمل primary marker المطلوب | أضيف marker واحد للزر الرئيسي في القوالب والمنتجات المتأثرة | جميع المنتجات الحالية تحمل marker DOM واحدًا |
| F-07 | artifact `2026-w35` لم يكن له سجل backlog مطابق | أضيف سجل legacy built مطابق للعنوان والpitch والفترة دون إعادة بناء الصفحة | إعادة بناء catalog في نسخة مؤقتة طابقت `index.html` و`catalog.json` |
| F-08 | تثبيت Playwright كان غير محدد الإصدار | أضيف `automation/browser-requirements.txt` بإصدار `playwright==1.62.0` وربطت به workflows Phase 2 وLLM وlifecycle | YAML validation وتشغيل Chromium ناجحان |
| F-09 | builder كان يضع title غير مهروب وpayload JSON غير محمي من `</script>` | هُرّب title، وأُغلقت محارف HTML الحساسة في JSON المضمّن | regression encoding ناجح |
| F-10 | فحص الوثيقة لم يكن يفرض حدود document كاملة أو protocol-relative URLs في كل المسارات | أضيف فحص doctype-to-closing-html وفحص `//...` في validators الأسبوعي وLLM | regression HTML contract ناجح |

## الاختبارات المحلية

نجحت الاختبارات التالية بعد الإصلاح: `test_period_utils.py`، `test_guard_weekly_period.py`، `test_llm_workflow_period_guard.py`، `test_no_overwrite.py`، `test_builder_output_encoding.py`، `test_generated_html_contract.py`، `test_manage_lifecycle.py`، `test_catalog_lifecycle.py`، `test_validate_catalog_links.py`، `test_pick_idea_diversity.py`، و`test_triage_idea.py`. كما نجحت بوابة YAML، وworkflow validation، و`compileall`، و`git diff --check`.

أُعيد بناء الكتالوج داخل نسخة مؤقتة، ثم أُضيف analytics pixel وقورِن الناتج بالنسخة الحالية؛ تطابق `index.html` و`catalog.json`. مرّت جميع صفحات `2026-w34` إلى `2026-w50` بالمدقق المناسب، ومرّت بوابة Chromium للكتالوج وكل المنتجات. الكتالوج عرض 18 بطاقة، وفتحت البوابة 19 رابطًا عند احتساب رابط البديل.

## الاختبارات الحقيقية

| الاختبار | التشغيل | النتيجة |
|---|---|---|
| LLM no-op بلا فترة صريحة | [32774375830][1] | نجاح. اكتشف `2026-w35` المنشورة، تخطى تثبيت المتصفح وpicker والمزودين والبناء والنشر، وأكمل إشعار `already-published` |
| LLM explicit collision | [32774533800][2] | فشل مقصود عند guard، تخطى picker والمزودين والبناء والنشر، وأكمل إشعار الفشل |
| guard Tier A no-op | [32767321437][3] | نجاح no-op موثق سابقًا |
| guard Tier A explicit collision | [32767380959][4] | فشل مقصود وموثق سابقًا |

في التشغيلين الجديدين كان `headSha` هو commit `5ccfd48`، وهو الإصلاح الرئيسي. وبعد ذلك دُفع التصحيح الإضافي الصغير `ccd17a8` لرفض `products/weekly/` كهدف ملتبس. لم يتغير `ideas/backlog.json` أو `catalog.json` أو artifact w35 بسبب التشغيلين الحقيقيين؛ بصماتها قبل وبعد مثبتة في سجل guard.

## حدود ما لم يُغيّر

لم تُفعّل حماية pull-request-only لفرع `main`؛ السبب أن التصميم الحالي يعتمد على publisher موثوق داخل GitHub Actions يدفع إلى `main`. بقيت حماية stale-main والتزامن المشترك وSHA pinning والصلاحيات المحدودة كما هي. تفعيل branch protection الكامل قرار تشغيلي مستقل يحتاج موافقة صريحة لأنه قد يمنع publisher الحالي من أداء مهمته.

## الخلاصة

الإصلاحات البرمجية المؤكدة مكتملة ومختبرة. لا يوجد تغيير غير متعمد في محتوى المنتجات، ولا حذف لملفات أو أفكار. نافذة مراقبة prompt w51–w54 تبقى مستقلة ولم تُعدّل عتبتها.

## References

[1]: https://github.com/lo77667/repositoryDz/actions/runs/32774375830 "Real LLM already-published no-op test"
[2]: https://github.com/lo77667/repositoryDz/actions/runs/32774533800 "Real LLM manual period reuse rejection test"
[3]: https://github.com/lo77667/repositoryDz/actions/runs/32767321437 "Real Tier A already-published no-op test"
[4]: https://github.com/lo77667/repositoryDz/actions/runs/32767380959 "Real Tier A manual period reuse rejection test"
