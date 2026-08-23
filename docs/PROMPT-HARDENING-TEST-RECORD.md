# سجل اختبار تقوية Prompt توليد HTML

## الحكم

تم تطبيق تقوية نصية فقط على `SYSTEM_PROMPT` في `automation/generate_html_with_llm.py`. لم تتغير سلسلة المزودات، أو البوابات، أو صيغ JSON، أو حدود التوكنات، أو مفاتيح GitHub.

التعديل أضاف قائمة حرجة مرقمة في بداية prompt، ثم أضاف تذكير تحقق ذاتي بصياغة مختلفة في نهايته. القواعد تشمل مستند HTML كاملًا من `<!DOCTYPE html>` إلى `</html>`، و`lang="ar" dir="rtl"`، ومنع كل `on*` inline handlers، ووجود primary واحد، والعمل offline دون شبكة.

## خط الأساس قبل التعديل

في [w48 run 32612951967][1]، قبل prompt hardening، استُدعي Gemini وفشل بمحاولتين: الأولى بسبب inline event handler، والثانية بسبب مستند HTML غير كامل. ثم استُدعي Groq وفشل بمحاولتين: الأولى بسبب مخالفات `lang/dir/primary` وخطأ JavaScript، والثانية بسبب HTTP 429 من حد TPM. هذه النتيجة سجلت فشل مزودين متتاليين ولم تُعد نجاح LLM.

## الاختبارات المحلية

نجح اختبار عقد prompt في التأكد من وجود الكتلة الحرجة في البداية وتذكير التحقق الذاتي في النهاية. كما نجحت اختبارات Python وYAML وJSON و`git diff --check` واختبارات الأمن وpicker وlifecycle والكتالوج. التغيير الملتزم قبل w49 كان في ملف prompt فقط، في commit `d4ee890`.

## النتائج الحقيقية

| التشغيل | الفكرة المختارة | سجل المزودين | الوضع النهائي | النتيجة |
|---|---|---|---|---|
| [w49 — 32614004936][2] | `generate-011` — لعبة نبرة العلامة، `design/game` | Gemini rejected بعد **محاولة واحدة** بسبب HTML غير كامل؛ Groq accepted بعد **محاولة واحدة** | `generated / groq` | نجاح LLM، static gate، Chromium، catalog، Pages، Telegram |
| [w50 — 32614120217][3] | `generate-013` — مخطط إعادة الضبط، `wellbeing/planner` | Gemini accepted من **المحاولة الأولى**؛ Groq لم يُستدعَ | `generated / gemini` | نجاح LLM، static gate، Chromium، catalog، Pages، Telegram |

في w50 فتح المنتج العام بنجاح على [صفحة مخطط إعادة الضبط][4]، ثم نُقر الزر الأساسي وظهرت خطة عربية تفاعلية مدتها 10 دقائق. لم تظهر أخطاء صفحة ظاهرة، والبوابة المحلية سجلت عدم وجود console/page errors أو طلبات شبكة غير CounterAPI.

## قراءة النتيجة

النتيجة لا تثبت إحصائيًا تحسنًا عامًا من تشغيلين فقط، لكنها تثبت تحسنًا تشغيليًا واضحًا في عينتين متتاليتين بعد التعديل: w49 لم يحتج Gemini إلى محاولة إصلاح ثانية، ثم نجح Groq من محاولته الأولى؛ w50 نجح Gemini من المحاولة الأولى مباشرة. بالمقابل، يجب إبقاء w48 كخط أساس فشل لاختبار لاحق، وعدم الادعاء بأن prompt وحده يعالج كل إخفاقات النماذج.

الإصلاح الموجه للخطأ و`shape` داخل `build_prompt()` لم يُنفذا بعد؛ وفق الخطة، ينتظران بيانات أكثر من w49/w50 قبل اعتبارهِما ضروريين. كما أن w49 أثبت أن Groq يمكن أن يقبل الناتج بعد فشل Gemini، بينما w50 أثبت عودة Gemini إلى قبول المحاولة الأولى.

## الحالة النهائية

الفرع بعد مزامنة تشغيل w50 كان نظيفًا على commit `c888e87`، وصفحة Pages في حالة `built`. لم تُكشف أسرار، ولم يتغير provider chain، ولم تبدأ مرحلة لاحقة.

## References

[1]: https://github.com/lo77667/repositoryDz/actions/runs/32612951967 "Baseline w48 provider-chain run"
[2]: https://github.com/lo77667/repositoryDz/actions/runs/32614004936 "Prompt hardening w49 run"
[3]: https://github.com/lo77667/repositoryDz/actions/runs/32614120217 "Prompt hardening w50 run"
[4]: https://lo77667.github.io/repositoryDz/products/weekly/2026-w50/ "Public w50 product"
