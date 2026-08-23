# سجل اختبار المرحلة 5 — سلسلة مزودي LLM البديلة

**الحالة: مكتملة بعد إثبات الانتقال الحقيقي من Gemini إلى Groq داخل GitHub Actions.** أُجري الاختبار على المستودع العام `lo77667/repositoryDz`، مع بقاء الاستضافة والنشر على GitHub Pages فقط، ومن دون استخدام Manus للاستضافة أو النشر.

## معيار الإغلاق

تنص المرحلة على أن مدير السلسلة يجرب Gemini ثم Groq ثم Mistral، ويتجاوز المزود غير المهيأ، وينتقل مباشرة إلى المزود التالي عند فشل الشبكة أو المزود، ويمنح كل مزود محاولة أولية ومحاولتي إصلاح كحد أقصى. لا يُنشر أي مرشح قبل اجتيازه بوابة HTML الثابتة وبوابة Chromium المعزول. عند رفض جميع المزودين يُنشر البديل الحتمي الآمن فقط، مع إبلاغ Telegram بالحالة الحقيقية.

## دليل السلسلة

| الترتيب | المزود | الإعداد المستخدم | النتيجة المثبتة |
|---|---|---|---|
| 1 | Gemini | `LLM_API_KEY`، والنموذج المعتاد `gemini-3-flash-preview` | التشغيل العادي `2026-w39` في [run 32606976173](https://github.com/lo77667/repositoryDz/actions/runs/32606976173) قبل السلسلة الكاملة أنتج `generate-003` في وضع `generated` عبر Gemini. وفي الاختبار القسري رُفض عمدًا بخطأ اتصال `Connection refused`. |
| 2 | Groq | `LLM_FALLBACK_API_KEY`، والنموذج `openai/gpt-oss-20b` | في [run 32608059785](https://github.com/lo77667/repositoryDz/actions/runs/32608059785)، وبعد إجبار فشل Gemini، ظهر السطر الآمن `Accepted candidate from provider groq.`، ثم `PRODUCT_MODE: generated` و`PRODUCT_PROVIDER: groq`. |
| 3 | Mistral | `LLM_SECONDARY_API_KEY` غير مهيأ | تم تخطيه كما صُمم، من دون فشل التشغيل أو ادعاء استخدامه. |
| 4 | البديل الحتمي | لا يحتاج مفتاحًا | بقي مسار أمان فعالًا، وثبت في التشغيلات الوسيطة، لكنه **ليس** دليل انتقال متعدد المزودين. لذلك لم تُعلن المرحلة مكتملة قبل نجاح تشغيل Groq في `2026-w43`. |

يوثق التشغيل القسري الحقيقي أن Gemini رُفض أولًا، ثم قُبل مرشح Groq بعد البوابات، وليس مجرد أن وظيفة GitHub انتهت بحالة نجاح. كما أن خطوة الإشعار الناجح في التشغيل نفسه انتهت بحالة `success`، بينما بقيت خطوة إشعار الفشل `skipped`.

## سجل المحاولات والتصحيحات

| التشغيل | الفترة | النتيجة | السبب أو التصحيح |
|---|---|---|---|
| [32607419667](https://github.com/lo77667/repositoryDz/actions/runs/32607419667) | `2026-w40` | fallback | Gemini فشل عمدًا، وGroq أعاد HTTP 403 مع رمز Cloudflare 1010؛ لم يُحتسب هذا انتقالًا ناجحًا. |
| [32607717137](https://github.com/lo77667/repositoryDz/actions/runs/32607717137) | `2026-w41` | fallback | بعد جعل JSON Schema غير صارم لـ Groq، بقي 403/1010؛ أضيف User-Agent وAccept صريحان. |
| [32607896395](https://github.com/lo77667/repositoryDz/actions/runs/32607896395) | `2026-w42` | fallback | زال 1010، لكن Groq رفض الطلب بسبب حد TPM المجاني: المطلوب `12462` مقابل حد `8000`. خُفّض `max_tokens` الخاص بـ Groq إلى `6000`. |
| [32608059785](https://github.com/lo77667/repositoryDz/actions/runs/32608059785) | `2026-w43` | **generated عبر Groq** | اجتاز Groq الطلب، ثم اجتاز المرشح البوابة الثابتة وبوابة Chromium، وقُبل ونُشر. |

تتوافق التصحيحات مع توثيق Groq: فالنموذج `openai/gpt-oss-20b` يدعم JSON Schema وJSON Object Mode [1]، وعنوان OpenAI-compatible الصحيح هو `https://api.groq.com/openai/v1` [2]. أما رمز Cloudflare 1010 فيعني حظرًا مبنيًا على توقيع عميل HTTP [3]، وقد عولج بإضافة رؤوس HTTP واضحة. ولم يكن 403 الأخير مشكلة صلاحية نموذج؛ السبب اللاحق الموثق في سجل Groq كان حد TPM، لذلك عولج بتقليل ميزانية الإخراج بدل اختلاق مفتاح أو نموذج آخر.

## الاختبارات المحلية

أُعيد تشغيل `python3 -m py_compile automation/*.py`، وفاحص YAML، وفاحص سير العمل، واختبار السلسلة المحلي الذي يحاكي Gemini متعطلًا ثم Groq صالحًا. أثبت الاختبار المحلي أن Gemini يُسجل `rejected` بسبب اتصال مرفوض، وأن Groq يُسجل `accepted` بمحاولة واحدة، وأن Mistral غير المهيأ يُسجل `skipped`. كما اجتاز المرشح المحلي بوابة HTML الثابتة وبوابة Chromium مع `console_errors=[]` و`page_errors=[]` و`network_requests=[]` و`primary_controls=1` و`clicked=true`. وأُضيف اختبار محلي منفصل لتثبيت أن Gemini يستخدم JSON Schema صارمًا، بينما يستخدم Groq JSON Schema غير صارمًا متوافقًا مع عقده.

## نتيجة التشغيل والنشر

اختار التشغيل [32608059785](https://github.com/lo77667/repositoryDz/actions/runs/32608059785) الفكرة `generate-007` بعنوان **مدقق براهين الكتالوج**. وبعد قبول Groq، نشر GitHub Actions المنتج في commit [`a23c24e3`](https://github.com/lo77667/repositoryDz/commit/a23c24e3d2371c78e205faf3d363d8851b0bb19a)، وسجل backlog أن `generate-007` أصبح `built` مع `built_period: 2026-w43`.

| البوابة | النتيجة | الدليل |
|---|---|---|
| قبول المزود | **Passed** | السجل يذكر `Accepted candidate from provider groq.` |
| HTML static safety gate | **Passed** | السجل يذكر `Generated HTML static safety gate passed`. |
| Chromium gate | **Passed** | التشغيل المحلي للـ artifact الملتزم أعاد أخطاء Console وPage وNetwork فارغة وزرًا أساسيًا واحدًا قابلًا للنقر. |
| GitHub Pages | **Passed** | [الرابط العام](https://lo77667.github.io/repositoryDz/products/weekly/2026-w43/) أعاد HTTP 200، وحالة آخر Pages build هي `built` على commit `a23c24e`. |
| التفاعل العام | **Passed** | الصفحة عربية RTL؛ زر `تحقق` عرض رسالة تحقق عربية عند النقر، ثم عرض نتيجة عربية منطقية بعد إدخال بيانات. |
| Telegram | **Passed** | خطوة `Send successful provider-chain notification` انتهت `success`، والسكربت تحقق من استجابة Telegram ذات `ok:true`. |
| الأسرار | **Passed** | لم يظهر في سجل التشغيل أي رمز اعتماد غير مقنع؛ بقيت القيم السرية مقنّعة، ولم تُكتب في المستودع. |

في الاختبار العام، ظهر العنوان **مدقق براهين الكتالوج**، وكان زر `تحقق` قابلًا للنقر. النقر من دون بيانات أظهر «الرجاء إدخال ميزة المنتج»، وبعد إدخال مثال ظهر رد عربي «معلومات غير كافية: لا توجد إشارة للميزة في المعلومات.» كما لم يُظهر Console العام أي مخرجات أو أخطاء.

## القيود والصيانة

ظهر في التشغيل تحذير GitHub غير حاجب بأن `actions/checkout@v4` و`actions/setup-python@v5` يستهدفان Node.js 20 وسيُجبران حاليًا على Node.js 24. لم يفشل التشغيل بسبب ذلك، لكنه بند صيانة مستقبلي مستقل ولا يغيّر نتيجة المرحلة 5.

ما زال سير توليد LLM يدوي التشغيل، ولا توجد جدولة جديدة أو خدمة خلفية أو استضافة خارج GitHub Pages. **المرحلة 6 لم تبدأ**، وسيبقى المشروع متوقفًا عند إغلاق المرحلة 5 إلى أن يطلب المستخدم صراحة بدء مرحلة لاحقة.

## المراجع

[1]: https://console.groq.com/docs/model/openai/gpt-oss-20b "Groq — GPT OSS 20B"
[2]: https://console.groq.com/docs/openai "Groq — OpenAI Compatibility"
[3]: https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/ "Cloudflare — Error 1010"
[4]: https://console.groq.com/docs/errors "Groq — API Error Codes and Responses"
