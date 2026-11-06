/* «علاقتك صحية؟» (/relationship-check/). Runs only in the browser: nothing is sent or stored.
   «اخرج بسرعة» replaces this page in history so the back button doesn't return here. */
(function () {
  var exit = document.querySelector(".quick-exit");
  if (exit) exit.addEventListener("click", function (e) { e.preventDefault(); location.replace(exit.href); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && exit) location.replace(exit.href); });

  var form = document.getElementById("rc"), out = document.getElementById("rc-result");
  if (!form || !out) return;
  var err = form.querySelector(".quiz-error");

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function list(arr) { return "<ul>" + arr.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>"; }

  form.addEventListener("change", function (e) {
    var fs = e.target.closest(".q");
    if (fs) { fs.classList.add("done"); fs.classList.remove("missing"); }
    if (err) err.hidden = true;
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var qs = form.querySelectorAll(".q"), missing = null, green = [], red = [], serious = [], greens = 0;
    qs.forEach(function (q) {
      var c = q.querySelector("input:checked");
      q.classList.toggle("missing", !c);
      if (!c) { if (!missing) missing = q; return; }
      var v = +c.value, type = q.getAttribute("data-type"), t = q.getAttribute("data-text");
      if (type === "green") { greens++; if (v === 2) green.push(t); }
      else if (v > 0) { (type === "serious" ? serious : red).push(t); }
    });
    if (missing) {
      if (err) err.hidden = false;
      missing.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var flags = red.length + serious.length, head, msg;
    if (serious.length) {
      head = "فيه علامات خطر محتاجة تاخدها بجد";
      msg = "اللي اخترته فيه علامات تحكم أو تهديد أو أذى. ده مش ذنبك، ومش «عادي في كل البيوت». مش لازم تاخد قرار كبير النهارده، بس مهم ماتبقاش لوحدك في ده.";
    } else if (flags >= 3) {
      head = "فيه علامات محتاجة تقف عندها";
      msg = "علاقتك فيها كذا حاجة بتقلل الأمان والاحترام. ده يستاهل كلام صريح، وممكن مساعدة من متخصص في العلاقات.";
    } else if (flags > 0) {
      head = "علاقتك فيها حاجات حلوة… وحاجات تتحسن";
      msg = "كل علاقة فيها نقط ضعف. المهم إنكم تقدروا تتكلموا عنها بهدوء، وإنها ماتكبرش.";
    } else {
      head = green.length >= Math.ceil(greens / 2) ? "علاقتك فيها علامات صحية كتير" : "مفيش علامات حمرا… بس فيه مساحة تقرّبوا أكتر";
      msg = "مفيش ولا علامة إنذار من اللي في القايمة. حافظوا على الكلام المفتوح والاحترام، دول أهم من أي حاجة.";
    }
    var html = '<p class="result-kicker">نتيجتك</p><h2>' + head + "</h2><p>" + msg + "</p>";
    if (serious.length || red.length) html += '<h3 class="rc-h rc-red">🚩 علامات محتاجة انتباه</h3>' + list(serious.concat(red));
    if (green.length) html += '<h3 class="rc-h rc-green">✅ علامات خضرا عندك</h3>' + list(green);
    if (serious.length) html += '<p class="result-alert"><b>لو حاسس إنك في خطر دلوقتي:</b> مصر: النجدة <a href="tel:122">122</a>، والمجلس القومي للمرأة <a href="tel:15115">15115</a>، والدعم النفسي <a href="tel:105">105</a>. أمريكا: <a href="tel:911">911</a>، والخط الوطني للعنف الأسري <a href="tel:18007997233" dir="ltr" class="nowrap">1-800-799-7233</a>. واتكلم مع حد بتثق فيه.</p>';
    html += '<p class="result-note">دي قايمة توعية، مش تشخيص ولا حكم على شريكك. لو محتار، اتكلم مع متخصص نفسي أو مستشار علاقات.</p>' +
      '<button type="button" class="btn again">جاوب تاني</button>';
    out.innerHTML = html;
    out.hidden = false;
    form.hidden = true;
    out.querySelector(".again").addEventListener("click", function () {
      form.reset();
      qs.forEach(function (q) { q.classList.remove("done", "missing"); });
      out.hidden = true; form.hidden = false;
      form.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    out.focus({ preventScroll: true });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  });
})();
