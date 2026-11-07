// Daily myth-or-fact learning card. No accounts, tracking, or answer collection.
(function () {
  'use strict';
  var root = document.querySelector('[data-myth-fact]');
  if (!root) return;
  var items = [
    { claim:'الشخص القوي نفسيًا لا يشعر بالحزن.', answer:'myth', why:'القوة النفسية لا تعني غياب الحزن. هي القدرة على الاعتراف بالمشاعر والتعامل معها وطلب الدعم عند الحاجة.' },
    { claim:'طلب المساعدة النفسية دليل على الضعف.', answer:'myth', why:'طلب المساعدة قد يكون خطوة واعية وشجاعة لفهم الصعوبات والتعامل معها، وليس حكمًا على قوة الشخص أو قيمته.' },
    { claim:'القلق قد يظهر في صورة أعراض جسدية.', answer:'fact', why:'القلق قد يصاحبه خفقان أو شد عضلي أو اضطراب في المعدة. لكن الأعراض الجسدية الجديدة أو الشديدة تستحق تقييمًا طبيًا ولا ينبغي افتراض أن سببها نفسي فقط.' },
    { claim:'كل من يمر بتجربة صعبة سيصاب حتمًا باضطراب نفسي.', answer:'myth', why:'استجابات الناس للأحداث الصعبة مختلفة. قد يتأثر البعض لفترة، ويتعافى آخرون، وقد يحتاج بعضهم إلى دعم متخصص. لا توجد نتيجة واحدة حتمية.' },
    { claim:'النوم المنتظم يمكن أن يدعم الصحة النفسية.', answer:'fact', why:'النوم الجيد يرتبط بتنظيم المزاج والانتباه والتعامل مع الضغوط. وهو عامل مساعد، وليس علاجًا منفردًا لكل مشكلة نفسية.' },
    { claim:'التفكير الإيجابي وحده كافٍ لعلاج الاكتئاب.', answer:'myth', why:'الاكتئاب حالة متعددة العوامل، وقد يحتاج إلى علاج نفسي أو دوائي أو كليهما وفق تقييم مختص. التفاؤل وحده ليس بديلًا عن الرعاية المناسبة.' },
    { claim:'المشاعر السلبية جزء طبيعي من الخبرة الإنسانية.', answer:'fact', why:'الحزن والخوف والغضب مشاعر إنسانية طبيعية. المهم فهمها والتعامل معها، والانتباه إذا أصبحت شديدة أو مستمرة أو عطلت الحياة.' },
    { claim:'الذاكرة تسجل الأحداث دائمًا كما حدثت تمامًا.', answer:'myth', why:'الذاكرة عملية إعادة بناء وقد تتأثر بالانتباه والمشاعر والمعلومات اللاحقة. لذلك قد تختلف التفاصيل التي يتذكرها أشخاص عاشوا الحدث نفسه.' },
    { claim:'وضع حدود واضحة في العلاقات قد يساعد على تقليل الاستنزاف.', answer:'fact', why:'التعبير الواضح والمحترم عن الاحتياجات والقدرات قد يدعم علاقات أكثر توازنًا. والحدود تختلف حسب طبيعة العلاقة والسياق.' },
    { claim:'كل شخص يعاني من نوبة هلع لديه اضطراب هلع بالضرورة.', answer:'myth', why:'قد تحدث نوبة هلع منفردة أو في سياقات مختلفة. تشخيص اضطراب الهلع يحتاج إلى تقييم نمط الأعراض وتكرارها وتأثيرها واستبعاد أسباب أخرى.' }
  ];
  var today = new Date();
  var day = Math.floor((new Date(today.getFullYear(), today.getMonth(), today.getDate()) - new Date(today.getFullYear(), 0, 0)) / 86400000);
  var index = (day - 1) % items.length;
  var claim = root.querySelector('[data-myth-claim]');
  var feedback = root.querySelector('[data-myth-feedback]');
  var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-myth-answer]'));
  var next = root.querySelector('[data-myth-next]');
  var share = root.querySelector('[data-myth-share]');
  var count = root.querySelector('[data-myth-count]');
  var current;
  function render() {
    current = items[index];
    claim.textContent = current.claim;
    count.textContent = 'معلومة ' + (index + 1) + ' من ' + items.length;
    feedback.hidden = true;
    feedback.textContent = '';
    buttons.forEach(function (button) { button.disabled = false; button.classList.remove('is-correct', 'is-wrong'); });
    next.hidden = true;
    share.hidden = true;
  }
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      if (button.disabled) return;
      var chosen = button.getAttribute('data-myth-answer');
      var correct = chosen === current.answer;
      buttons.forEach(function (b) {
        b.disabled = true;
        if (b.getAttribute('data-myth-answer') === current.answer) b.classList.add('is-correct');
        else if (b === button) b.classList.add('is-wrong');
      });
      feedback.textContent = (correct ? 'إجابتك صحيحة! 👏 ' : 'دي خرافة شائعة، والإجابة الصحيحة: ' + (current.answer === 'myth' ? 'خرافة. ' : 'حقيقة. ')) + current.why;
      feedback.hidden = false;
      next.hidden = false;
      share.hidden = false;
    });
  });
  next.addEventListener('click', function () { index = (index + 1) % items.length; render(); });
  share.addEventListener('click', function () {
    var message = 'خرافة أم حقيقة؟ ' + current.claim + '\n' + current.why + '\nالمزيد: https://drmilladmikhail.com/myth-fact/';
    if (navigator.share) navigator.share({ title:'خرافة أم حقيقة؟', text:message }).catch(function () {});
    else if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(message).then(function () { share.textContent = 'تم نسخ المعلومة'; }).catch(function () { share.textContent = 'انسخ رابط الصفحة وشاركه'; });
    else share.textContent = 'شارك رابط الصفحة مع أصحابك';
  });
  render();
})();