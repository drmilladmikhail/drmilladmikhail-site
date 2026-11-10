/* «إيه اللي بيتعبك في علاقتك؟» (/partner/). Runs only in the browser: nothing is sent or stored.
   Results describe BEHAVIOURS and point to an article — they never label the partner. */
(function () {
  var exit = document.querySelector(".quick-exit");
  if (exit) exit.addEventListener("click", function (e) { e.preventDefault(); location.replace(exit.href); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && exit) location.replace(exit.href); });

  var form = document.getElementById("pc"), out = document.getElementById("pc-result"), dataEl = document.getElementById("pc-data");
  if (!form || !out || !dataEl) return;
  var cats = JSON.parse(dataEl.textContent), err = form.querySelector(".quiz-error");

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  form.addEventListener("change", function (e) {
    var fs = e.target.closest(".q");
    if (fs) { fs.classList.add("done"); fs.classList.remove("missing"); }
    if (err) err.hidden = true;
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var qs = form.querySelectorAll(".q"), missing = null, sum = {}, max = {}, serious = 0;
    qs.forEach(function (q) {
      var c = q.querySelector("input:checked");
      q.classList.toggle("missing", !c);
      if (!c) { if (!missing) missing = q; return; }
      var cat = q.getAttribute("data-cat"), v = +c.value;
      if (cat === "serious") { serious += v; return; }
      sum[cat] = (sum[cat] || 0) + v;
      max[cat] = (max[cat] || 0) + 2;
    });
    if (missing) {
      if (err) err.hidden = false;
      missing.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var ranked = Object.keys(sum).map(function (k) { return { k: k, r: sum[k] / max[k] }; })
      .filter(function (o) { return o.r >= 0.5; })
      .sort(function (a, b) { return b.r - a.r; });

    var html = '<p class="result-kicker">نتيجتك</p>';
    if (ranked.length) {
      var top = cats[ranked[0].k];
      html += "<h2>أكتر حاجة بتتعبك: " + esc(top.name) + "</h2><p>" + esc(top.msg) + "</p>" +
        '<p><a class="btn primary" href="' + top.url + '">اقرا الحلقة: ' + esc(top.title) + "</a></p>";
      if (ranked.length > 1) {
        html += '<h3 class="rc-h rc-red">وكمان فيه علامات على:</h3><ul>' + ranked.slice(1).map(function (o) {
          var c = cats[o.k];
          return '<li><a href="' + c.url + '">' + esc(c.name) + "</a></li>";
        }).join("") + "</ul>";
      }
    } else {
      html += "<h2>مفيش نمط واضح بيتكرر</h2><p>من إجاباتك، مفيش سلوك من اللي في القايمة بيتكرر بشكل كبير. ده كويس! ولو حاسس إنكم بعيد عن بعض، ابدأ بمقال التواصل العاطفي.</p>" +
        '<p><a class="btn primary" href="/articles/emotional-communication-couples/">تحسين التواصل العاطفي بين الزوجين</a></p>';
    }
    if (serious > 0) {
      html += '<p class="result-alert"><b>اخترت إنك بتخاف أو اتعرضت لتهديد أو أذى، وده لوحده سبب كافي تطلب مساعدة.</b> مش ذنبك، ومتبقاش لوحدك في ده. مصر: النجدة <a href="tel:122">122</a>، والمجلس القومي للمرأة <a href="tel:15115">15115</a>، والدعم النفسي <a href="tel:16328">16328</a>. أمريكا: <a href="tel:911">911</a>، والخط الوطني للعنف الأسري <a href="tel:18007997233" dir="ltr" class="nowrap">1-800-799-7233</a>. وشوف <a href="/help-now/">محتاج مساعدة دلوقتي</a>.</p>';
    }
    html += '<p class="result-note">دي أداة توعية عن السلوكيات، مش تشخيص لشريكك ولا حكم عليه. التشخيص بيعمله متخصص بعد ما يقابل الشخص نفسه. ولو محتار، اتكلم مع متخصص نفسي.</p>' +
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
