# سجل اختبار المرحلة 7 — استقبال الأفكار وفرزها

**الحالة:** مكتملة بعد تشغيل GitHub حقيقي ومراجعة محلية.

**النطاق:** فتح قناة عامة عبر GitHub Issue Forms، وفرز القضايا آليًا دون تعديل `ideas/backlog.json` أو نشر أي منتج. القرار النهائي بإضافة الفكرة إلى backlog أو بناء منتج بقي بشريًا.

## النتيجة المختصرة

| الفحص | النتيجة | الدليل |
|---|---|---|
| Issue Form عربية | نجح التعريف والمخطط | `.github/ISSUE_TEMPLATE/product-idea.yml`، وفحص YAML محلي |
| قضية صحيحة | نجحت | [Issue #1](https://github.com/lo77667/repositoryDz/issues/1)، [Run 32610704529](https://github.com/lo77667/repositoryDz/actions/runs/32610704529) |
| قضية ناقصة | نجحت | [Issue #2](https://github.com/lo77667/repositoryDz/issues/2)، [Run 32610788025](https://github.com/lo77667/repositoryDz/actions/runs/32610788025) |
| قضية مكررة | نجحت | [Issue #3](https://github.com/lo77667/repositoryDz/issues/3)، [Run 32610788444](https://github.com/lo77667/repositoryDz/actions/runs/32610788444) |
| قضية غير آمنة | نجحت | [Issue #4](https://github.com/lo77667/repositoryDz/issues/4)، [Run 32610788924](https://github.com/lo77667/repositoryDz/actions/runs/32610788924) |
| التعليقات والتصنيفات | نجحت | كل قضية حصلت على تعليق فرز واحد وتصنيف حالة صحيح |
| Telegram | نجح | خطوة `Send triage notification` انتهت بنجاح في التشغيلات الأربعة |
| backlog والنشر | سليم | SHA لملف backlog بقي `6b8fdbfd...`، ولا توجد خطوات `git push` أو نشر منتجات في Workflow |
| الأسرار | سليم | السجلات أظهرت القيم الحساسة مقنّعة، ولم تُطبع مفاتيح أو أجسام أسرار |
| الاختبارات المحلية | نجحت | Python syntax، Issue Form schema، YAML، Workflow، renderer، حالات الفرز الأربع |

## التشغيل الصحيح

أنشئت [القضية #1](https://github.com/lo77667/repositoryDz/issues/1) بعنوان **مراجع وضوح عرض الشحن** مع الحقول المطلوبة والتصنيفات `idea:submitted` و`idea:triage`. نجح [التشغيل 32610704529](https://github.com/lo77667/repositoryDz/actions/runs/32610704529)، وأعطى الحالة `ready-for-review` والدرجة `94/100` والاستراتيجية المقترحة `template:text-tool` والتصنيف `ecommerce`.

أضاف Workflow تعليقًا واحدًا بعلامة ثابتة، واقترح معرّفًا من الشكل `community-1-43d594be`. بقيت القضية مفتوحة وموسومة `idea:ready-for-review`. لم تُضف الفكرة إلى backlog، ولم يُبنَ منتج، ولم يحدث نشر تلقائي.

## الحالات السلبية

أُنشئت ثلاث قضايا عامة مستقلة لاختبار البوابات. القضية #2 تركت دليل الحاجة فارغًا، فصُنفت `needs-info` وحصلت على `idea:needs-info`. القضية #3 استخدمت عنوانًا ووصفًا قريبين جدًا من **بطاقات القرار** الموجودة في backlog، فصُنفت `duplicate` وحصلت على `idea:duplicate`. القضية #4 احتوت رابط HTTP ونداء `fetch()` نصيًا، فصُنفت `rejected` وحصلت على `idea:rejected`.

نجحت التشغيلات الثلاثة، وأُرسلت رسائل Telegram، ولم تغير أي منها backlog. لا تنفذ الأداة النصوص الواردة من القضايا، ولا تزور الروابط، ولا تحولها إلى HTML أو JavaScript قابل للتشغيل.

## الصلاحيات ومسار الفشل

يحدد Workflow المرحلة 7 الصلاحيات `contents: read` و`issues: write` فقط. يستخدم `GH_TOKEN` لجلب القضية وتحديث تعليقها وتصنيفها، لكنه لا يملك صلاحية الكتابة إلى محتوى المستودع. عند فشل المعالجة، يضيف تعليق فشل ويحاول إرسال إشعار Telegram، مع التصريح بأن backlog لم يتغير ولم يُنشر منتج.

تُحدّث التعليقات بواسطة marker واحد هو `repositoryDz:phase7-triage`، لذلك لا تتراكم تعليقات الفرز عند إعادة تشغيل القضية. يظل `idea:accepted` قرارًا بشريًا ولا يضيفه Workflow تلقائيًا.

## فحص واجهة الهاتف

تعريف النموذج موجود في المسار العام للمستودع، لكن جلسة المتصفح المستخدمة للفحص لم تكن مسجلة الدخول وأُعيد توجيهها إلى صفحة GitHub Login. لم تُطلب بيانات الدخول ولم تُرسل قضية من المتصفح. هذا لا يلغي الاختبار الحقيقي؛ فقد أُنشئت القضايا الأربع عبر GitHub API بصيغة Issue Form نفسها، ونجحت Actions في معالجتها. سيستطيع المستخدم رؤية النموذج من GitHub Mobile أو المتصفح بعد تسجيل الدخول إلى حسابه.

## قرار الإغلاق

المرحلة 7 **مكتملة**: قناة الاستقبال موجودة، الفرز والتصنيف والتسجيل في Telegram تعمل، التكرار والمحتوى غير الآمن يُعالجان بأمان، والمراجعة البشرية قبل backlog أو النشر مضمونة. **المرحلة 8 لم تبدأ.**

## المرجع

[1]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms "GitHub Docs — Syntax for issue forms"
