/* «اختبارات توعية سريعة» on /tests/<slug>/ (built from content/quick-quizzes/<slug>.json by tools/build_tests.py).
   Scores in the browser only: nothing is sent or stored. Shows the first result whose rules match. */
(function () {
  "use strict";
  var box = document.querySelector(".aq");
  if (!box) return;
  var form = box.querySelector(".aq-form"), out = box.querySelector(".aq-out"), err = form.querySelector(".quiz-error");
  var results = box.querySelectorAll(".aq-res");

  function test(rule, sums) {
    var m = rule.trim().match(/^(\w+)\s*(>=|<=|=)\s*(\d+)$/);
    if (!m) return false;
    var v = sums[m[1]] || 0, n = +m[3];
    return m[2] === ">=" ? v >= n : m[2] === "<=" ? v <= n : v === n;
  }
  function matches(el, sums) {
    var all = (el.getAttribute("data-all") || "").split(";").filter(Boolean);
    var any = (el.getAttribute("data-any") || "").split(";").filter(Boolean);
    return all.every(function (r) { return test(r, sums); }) && (!any.length || any.some(function (r) { return test(r, sums); }));
  }

  form.addEventListener("change", function (e) {
    var fs = e.target.closest(".q");
    if (fs) { fs.classList.add("done"); fs.classList.remove("missing"); }
    if (err) err.hidden = true;
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var sums = { unknown: 0 }, missing = null;
    form.querySelectorAll(".q").forEach(function (q) {
      var c = q.querySelector("input:checked");
      q.classList.toggle("missing", !c);
      if (!c) { if (!missing) missing = q; return; }
      if (c.value === "u") { sums.unknown++; return; }
      var g = q.getAttribute("data-g");
      sums[g] = (sums[g] || 0) + (+c.value);
    });
    if (missing) {
      if (err) err.hidden = false;
      missing.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var shown = false;
    results.forEach(function (r) {
      var ok = !shown && matches(r, sums);
      r.hidden = !ok;
      if (ok) shown = true;
    });
    var after = box.querySelector(".aq-after");
    if (after) after.hidden = false;
    form.hidden = true;
    out.focus({ preventScroll: true });
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  box.addEventListener("click", function (e) {
    if (e.target.closest(".aq-again")) {
      results.forEach(function (r) { r.hidden = true; });
      var after = box.querySelector(".aq-after");
      if (after) after.hidden = true;
      form.reset();
      form.querySelectorAll(".q").forEach(function (q) { q.classList.remove("done", "missing"); });
      form.hidden = false;
      form.querySelector("input").focus();
    }
  });
})();
