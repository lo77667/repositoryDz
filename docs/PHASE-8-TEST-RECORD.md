# سجل اختبار المرحلة 8 — التقوية والتوسع الآمن

## الحكم

**المرحلة 8 مكتملة.** تم تنفيذ التقوية الأمنية، وإضافة دورة حياة آمنة للأفكار والمنتجات، وتوحيد قفل النشر، ورفض stale `main`، وتثبيت Actions على SHAs موثقة، ثم اختبار المسارات الحقيقية على GitHub Actions وGitHub Pages وTelegram. **المرحلة 9 لم تبدأ.**

## نقطة البداية والتدقيق read-only

بدأت المرحلة من commit `41de56f` مع فرع `main` نظيف ومزامن. أظهر التدقيق 22 فكرة في backlog، منها 12 مبنية و10 في backlog، و12 artifact أسبوعيًا و13 مدخلًا في الكتالوج. كانت Pages في حالة `built` من `main` والجذر `/`.

كشفت المراجعة أن مساري Tier A وLLM يملكان `contents: write` لكن لكل منهما قفل concurrency مستقل، وأن Actions كانت مسموحة كلها دون SHA pinning. كما كان picker والكتالوج لا يعرضان دورة حياة `retired/revisit`، وكان workflow LLM يصدّر `model` دون حاجة تشغيلية. لم تُعرض قيم الأسرار؛ endpoint سرد الأسرار أعاد 403 من تكامل الجلسة، لذلك تمت مراجعة أسماء الاستخدام في YAML فقط.

## ما تم تنفيذه

| المجال | التنفيذ | الدليل |
|---|---|---|
| أمن HTML | سياسة مركزية في `automation/security_policy.py` تحظر APIs الشبكة، الإطارات والكائنات، redirects، event handlers، data HTML، `document.cookie`، والأنماط الشبيهة بالأسرار | commit `6ab3d26`، واختبارات regression محلية ناجحة |
| بوابات Tier A وLLM | ربط validatorين بالسياسة المركزية مع إبقاء CounterAPI الاستثناء الخارجي الوحيد بعد الحقن النهائي | منتجات w44 وw45 وw47 اجتازت static/browser gates |
| lifecycle | أداة `automation/manage_lifecycle.py` بانتقالات مقيدة، سبب إلزامي، history، رابط بديل داخلي، وكتابة atomic | commit `45d9025` |
| الكتالوج | عرض `متقاعد` أو `قيد المراجعة` مع السبب والبديل، مع إبقاء الرابط الأصلي والartifact القديم | الكتالوج العام يعرض 15 بطاقة |
| Workflow lifecycle | `phase-8-lifecycle.yml` يتطلب `confirm=true`، لا يحذف artifact، يعيد بناء الكتالوج، ينتظر Pages ويرسل Telegram | commit `1e4f0d4` ثم pinning في `a8d3dd0` |
| الاعتمادية | قفل كتابة موحد `repositoryDz-publish-main` وفحص `origin/main` قبل push ورفض stale push | commit `666183c` |
| supply chain | تثبيت `actions/checkout` و`actions/setup-python` على SHAs رسمية موثقة، وتفعيل `sha_pinning_required=true` | سياسة Actions بعد التحقق: `enabled=true`, `allowed_actions=all`, `sha_pinning_required=true` |
| outputs | إزالة `model` غير الضروري من مخرجات Workflow LLM | commit `6ab3d26` |

## الاختبارات المحلية

نجحت اختبارات YAML وPython وJSON و`git diff --check`. غطت regression الأمنية artifact صالحًا، ثم محاولات `fetch` و`document.cookie` وiframe وinline event handler ورابطًا خارجيًا وcredential-like literal. كما نجحت اختبارات lifecycle للـ dry-run، والانتقالات المسموحة والممنوعة، السبب القصير، والرابط البديل الخارجي، واختبار الكتالوج لحالة التقاعد والبديل.

بعد التغييرات، اجتاز المنتج `2026-w45` بوابة HTML وChromium مع عدم وجود console/page errors أو network requests غير CounterAPI. واجتاز المنتج `2026-w44` بوابة Tier A، واجتاز الكتالوج بوابتي HTML وChromium مع 15 بطاقة و15 رابطًا.

## التشغيلات الحقيقية

| التشغيل | الغرض | النتيجة |
|---|---|---|
| [32611679734][1] | Tier A جديد `2026-w46` بعد قفل النشر وstale-main | نجح؛ نشر «محول الوقت إلى دقائق»، حدّث backlog والكتالوج، واجتاز Pages وTelegram |
| [32611775661][2] | فحص فشل LLM عند عدم وجود فكرة generate | فشل آمن متوقع برسالة `No backlog ideas are available`; لم يُنشر شيء وأُرسلت رسالة الفشل |
| [32611883144][3] | LLM حقيقي بعد إضافة فكرة اختبار مستقلة `generate-009` | نجح؛ Gemini قبل الناتج في `generated` mode، نشر `2026-w47`، واجتاز gates وPages وTelegram |
| [32612039113][4] | lifecycle مع `confirm=false` | فشل مقصود؛ لم يُكتب backlog ولم يُبنَ catalog جديد، وأُرسلت رسالة الفشل |
| [32612061452][5] | تقاعد مؤكد لـ `generate-009` | نجح؛ الحالة `retired`، السبب والـ history والرابط البديل محفوظة، والartifact الأصلي بقي موجودًا |
| [32612214701][6] | Pages بعد تثبيت SHAs وسياسة Actions | نجح؛ Pages API بقي `built` من `main` والجذر `/` |
| [32612331756][7] | guard lifecycle بعد SHA pinning مع `confirm=false` | فشل مقصود وآمن؛ workflow المثبت اشتغل ورفض الكتابة ولم يغيّر metadata |

لم يُشغّل أي workflow نشر متوازٍ عمدًا؛ تم اختبار القفل المشترك عبر المسارات الفعلية، مع إبقاء التشغيل المتوازي للكتابة إلى `main` غير مفعّل.

## فحص GitHub Pages العام

فتح الكتالوج العام بنجاح وأظهر 15 منتجًا. بطاقة `2026-w47` ظهرت بشارة «متقاعد» وسبب التقاعد، مع رابط المنتج الأصلي ورابط البديل إلى `2026-w45`. فتح رابط البديل حمّل صفحة «مرتب أسباب الاسترجاع» بنجاح. التفاصيل محفوظة في [`PHASE-8-PUBLIC-BROWSER-FINDINGS.md`](PHASE-8-PUBLIC-BROWSER-FINDINGS.md).

## حدود وصيانة مؤجلة

تُرك `allowed_actions=all` كما هو حتى لا يتعطل workflow Pages الداخلي؛ التعويض الحالي هو تثبيت كل Actions التي يتحكم بها المستودع على SHAs وفرض `sha_pinning_required=true`. يمكن تضييق allowlist لاحقًا بعد جرد كامل لـ Pages actions. كما ظهر تنبيه GitHub غير حاجب بشأن Node.js 20 في Actions؛ لم يمنع أي تشغيل، وسُجل كصيانة مستقبلية. لا يوجد عطل يمنع إغلاق المرحلة 8.

## الحالة النهائية

آخر commit توثيقًا قبل هذا السجل هو `a8d3dd0`، ثم أضاف تشغيل lifecycle المؤكد commit `67edc0c`. بعد توثيق هذا السجل وREADME يجب أن يكون الفرع نظيفًا ومزامنًا مع `main`. لم تُحذف منتجات، ولم تُستبدل مسارات منشورة، ولم تُكشف أسرار، ولم تُستخدم استضافة Manus.

## References

[1]: https://github.com/lo77667/repositoryDz/actions/runs/32611679734 "Tier A hardening run 2026-w46"
[2]: https://github.com/lo77667/repositoryDz/actions/runs/32611775661 "Safe LLM no-backlog failure run"
[3]: https://github.com/lo77667/repositoryDz/actions/runs/32611883144 "LLM hardening run 2026-w47"
[4]: https://github.com/lo77667/repositoryDz/actions/runs/32612039113 "Lifecycle confirmation guard run"
[5]: https://github.com/lo77667/repositoryDz/actions/runs/32612061452 "Confirmed lifecycle retirement run"
[6]: https://github.com/lo77667/repositoryDz/actions/runs/32612214701 "Pages build after SHA pinning"
[7]: https://github.com/lo77667/repositoryDz/actions/runs/32612331756 "Post-pinning lifecycle confirmation guard"
