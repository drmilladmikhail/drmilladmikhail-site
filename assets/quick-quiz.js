// Daily psychology knowledge quiz. Answers stay in memory only; nothing is submitted or stored.
(function () {
  'use strict';
  var root = document.querySelector('[data-quick-quiz]');
  if (!root) return;
  var items = [
    { q: 'هل كل فكرة بتيجي في دماغك بتكون حقيقة؟', a: ['أيوه، غالباً', 'لأ، الأفكار مش دايماً حقائق'], correct: 1, why: 'الفكرة تفسير أو احتمال، مش دليل لوحدها. اسأل نفسك: إيه الدليل؟ وهل فيه تفسير تاني؟', link: '/feelings/', label: 'اكتشف مشاعرك كمان ←' },
    { q: 'هل تجاهل المشاعر بيخلّصنا منها بالضرورة؟', a: ['أيوه، بتختفي لوحدها', 'مش بالضرورة؛ فهمها بيساعدنا نتعامل معاها'], correct: 1, why: 'تسمية الشعور وفهم احتياجك ممكن يساعدك تختار استجابة أنسب، بدل ما تتصرف تلقائياً.', link: '/exercise/', label: 'جرّب تمرين الأسبوع ←' },
    { q: 'هل وضع الحدود الصحية معناه إنك أناني؟', a: ['لأ، الحدود بتنظم العلاقة وتحمي الاحتياجات', 'أيوه، لازم توافق على كل حاجة'], correct: 0, why: 'الحدود الواضحة مش عقاب للطرف التاني؛ هي طريقة محترمة لتوضيح ما يناسبك وما لا يناسبك.', link: '/challenges/', label: 'ابدأ تحدي الحدود الصحية ←' },
    { q: 'هل القلق دايماً معناه إن فيه خطر حقيقي؟', a: ['أيوه، القلق دليل أكيد', 'لأ، أحياناً بيكون إنذار مبالغ فيه'], correct: 1, why: 'القلق ممكن ينبهنا، لكنه مش مقياس دقيق للخطر. راجع الموقف والأدلة وخد خطوة مناسبة.', link: '/tests/', label: 'استكشف أدوات فهم الذات ←' },
    { q: 'هل طلب المساعدة علامة ضعف؟', a: ['لأ، ممكن يكون خطوة شجاعة وعملية', 'أيوه، المفروض أتعامل مع كل حاجة وحدي'], correct: 0, why: 'طلب الدعم وقت الحاجة مهارة مهمة، ومش معناه إنك فشلت أو إنك أقل قدرة.', link: '/articles/', label: 'اقرأ مقالات الصحة النفسية ←' }
  ];
  var now = new Date();
  var day = Math.floor(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) / 86400000);
  var item = items[((day % items.length) + items.length) % items.length];
  var question = root.querySelector('[data-quiz-question]');
  var options = root.querySelector('[data-quiz-options]');
  var feedback = root.querySelector('[data-quiz-feedback]');
  var link = root.querySelector('[data-quiz-link]');
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
      feedback.textContent = (index === item.correct ? 'إجابة صحيحة! 👏 ' : 'محاولة كويسة! خلّينا نفهمها. ') + item.why;
      link.href = item.link;
      link.textContent = item.label;
      link.hidden = false;
    });
    options.appendChild(button);
  });
})();
