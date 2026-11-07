// Daily psychology question: scenario-based learning, no diagnosis or data collection.
(function () {
  'use strict';
  var root = document.querySelector('[data-quick-quiz]');
  if (!root) return;
  var items = [
    { q:'قبل مقابلة مهمة، حسّيت بقلق وبدأت تتخيل أسوأ نتيجة. إيه الخطوة الأكثر فائدة؟', a:['أعتبر التخيل دليل إن الفشل أكيد','ألاحظ الفكرة وأراجع الأدلة وأستعد خطوة خطوة','ألغي المقابلة فورًا'], correct:1, why:'تخيّل أسوأ احتمال مش معناه إنه هيحصل. مراجعة الأدلة والاستعداد العملي يساعدانك تفرّق بين الاحتمال والحقيقة.', link:'/exercise/', label:'جرّب تمرين الأسبوع ←' },
    { q:'صديقك اتأخر في الرد على رسالتك. أي تفسير أدق؟', a:['أكيد بيتجاهلني','ممكن يكون مشغول أو عنده أسباب تانية؛ ما نعرفش لسه','ده معناه إن العلاقة انتهت'], correct:1, why:'دي مثال على أهمية عدم القفز للاستنتاجات. فيه تفسيرات متعددة، والأفضل ما نحولش التخمين لحقيقة من غير دليل.', link:'/feelings/', label:'اكتشف مشاعرك ←' },
    { q:'شخص قريب طلب منك حاجة فوق طاقتك. إيه معنى وضع حد صحي؟', a:['أرفض باحترام وأوضح اللي أقدر عليه','أوافق رغم إني متضرر','أهاجمه عشان يفهم'], correct:0, why:'الحدود الصحية بتوضح إمكانياتك واحتياجاتك من غير إهانة أو عدوان. الرفض المحترم مش معناه قلة اهتمام.', link:'/challenges/', label:'ابدأ تحدي الحدود ←' },
    { q:'لما تحس بالغضب، إيه التصرف اللي يساعدك تستجيب بوعي؟', a:['أرد فورًا بأول كلام ييجي في بالي','أكتمه للأبد','أدي نفسي لحظة تهدئة وأسمي الشعور قبل ما أقرر'], correct:2, why:'التوقف القصير وتسمية الشعور ممكن يخلقوا مساحة بين الانفعال والتصرف، وده يساعدك تختار ردًا أنسب.', link:'/feelings/', label:'اكتشف عجلة المشاعر ←' },
    { q:'زميلك نجح في حاجة كنت بتتمناها. أي فكرة أكثر توازنًا؟', a:['نجاحه معناه إني فاشل','نجاحه لا يلغي فرصي، وممكن أتعلم من تجربته','مفيش فايدة إني أحاول'], correct:1, why:'مقارنة نفسك بالآخرين بشكل مطلق بتظلمك. نجاح شخص آخر مش دليل على فشلك ولا حكم على مستقبلك.', link:'/articles/', label:'اقرأ مقالات الصحة النفسية ←' },
    { q:'أنت مرهق ومش قادر تنجز كل المهام. تبدأ بإيه؟', a:['أجلد نفسي وأحاول أعمل كل حاجة مرة واحدة','أختار مهمة صغيرة وأرتب الأولويات','أعتبر نفسي كسولًا'], correct:1, why:'تقسيم المهام واختيار خطوة قابلة للتنفيذ يقلل الإرباك. الراحة وتنظيم الجهد جزء من الاستمرار، مش فشل.', link:'/challenges/', label:'جرّب تحدي الخطوات الصغيرة ←' },
    { q:'هل طلب الدعم من شخص موثوق وقت الضغط معناه ضعف؟', a:['نعم، لازم أواجه كل شيء وحدي','لا، طلب الدعم ممكن يكون مهارة للتكيف','نعم، لو طلبت المساعدة هفقد السيطرة'], correct:1, why:'طلب المساندة المناسبة يساعد على مواجهة الضغوط. الاستقلال لا يعني العزلة أو تحمل كل شيء بمفردك.', link:'/articles/', label:'اقرأ المزيد ←' },
    { q:'لما تلاحظ إنك بتفكر: «أنا عمري ما بنجح»، إيه السؤال المفيد؟', a:['إيه المواقف اللي بتدعم أو لا تدعم الفكرة دي؟','ليه أنا شخص فاشل؟','إزاي أمنع أي فكرة سلبية بالقوة؟'], correct:0, why:'فحص الأدلة والبحث عن استثناءات يساعد على التفكير بمرونة بدل التعميم من تجربة أو أكثر.', link:'/tests/', label:'استكشف أدوات فهم الذات ←' },
    { q:'حد انتقد شغلك. إيه رد الفعل الأكثر اتزانًا؟', a:['أعتبر النقد حكمًا على قيمتي','أرفض أي ملاحظة','أفصل بين الملاحظة على العمل وقيمتي كشخص، وأراجع المفيد منها'], correct:2, why:'ملاحظة على أداء أو مهمة لا تختصر قيمتك كشخص. خُد الجزء العملي المفيد واترك التعميمات الجارحة.', link:'/articles/', label:'اقرأ مقالاتنا ←' },
    { q:'هل الاهتمام بالنفس معناه إنك تتجاهل مسؤولياتك تجاه الآخرين؟', a:['نعم، اهتم بنفسي فقط','لا، التوازن يشمل احتياجاتي ومسؤولياتي','نعم، لازم أختار طرف واحد دائمًا'], correct:1, why:'الاهتمام بالنفس مش أنانية تلقائيًا؛ هو محاولة لتحقيق توازن واقعي بين احتياجاتك والتزاماتك تجاه الآخرين.', link:'/exercise/', label:'ابدأ تمرينًا عمليًا ←' }
  ];
  var today = new Date();
  var dayNumber = Math.floor((new Date(today.getFullYear(), today.getMonth(), today.getDate()) - new Date(today.getFullYear(), 0, 0)) / 86400000);
  var item = items[((dayNumber - 1) % items.length + items.length) % items.length];
  var question = root.querySelector('[data-quiz-question]');
  var options = root.querySelector('[data-quiz-options]');
  var feedback = root.querySelector('[data-quiz-feedback]');
  var link = root.querySelector('[data-quiz-link]');
  var share = root.querySelector('[data-quiz-share]');
  question.textContent = item.q;
  options.textContent = '';
  item.a.forEach(function (label, index) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'quiz-option';
    button.textContent = label;
    button.addEventListener('click', function () {
      if (options.getAttribute('data-answered') === 'true') return;
      options.setAttribute('data-answered', 'true');
      Array.prototype.forEach.call(options.querySelectorAll('button'), function (b, i) {
        b.disabled = true;
        if (i === item.correct) b.classList.add('is-correct');
        else if (i === index) b.classList.add('is-wrong');
      });
      feedback.hidden = false;
      feedback.textContent = (index === item.correct ? 'إجابة صحيحة! 👏 ' : 'شكرًا على المحاولة. ') + item.why + ' · المعلومة للتثقيف وليست تشخيصًا نفسيًا.';
      link.href = item.link;
      link.textContent = item.label;
      link.hidden = false;
      share.hidden = false;
    });
    options.appendChild(button);
  });
  share.addEventListener('click', function () {
    var message = 'سؤال اليوم النفسي: ' + item.q + '\nتعلمت معلومة نفسية جديدة على موقع د. ميلاد ميخائيل: https://drmilladmikhail.com/';
    if (navigator.share) {
      navigator.share({ title:'سؤال اليوم النفسي', text:message, url:'https://drmilladmikhail.com/' }).catch(function () {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(message).then(function () {
        share.textContent = 'تم نسخ السؤال — شاركه مع أصحابك';
      }).catch(function () {
        share.textContent = 'انسخ رابط الموقع وشارك سؤال اليوم';
      });
    } else {
      share.textContent = 'شارك رابط الموقع مع أصحابك';
    }
  });
})();