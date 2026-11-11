/* Google Analytics 4, loaded only when content/analytics.json has his Measurement ID (tools/add_analytics.py).
   No inline script (the site's CSP forbids it): this file sets up gtag and loads Google's library. */
(function () {
  var me = document.currentScript;
  var id = me && me.getAttribute('data-ga4');
  if (!id || !/^G-[A-Z0-9]+$/.test(id)) return;
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  /* IP anonymisation is automatic in GA4; no ad personalisation signals */
  gtag('config', id, { allow_google_signals: false, allow_ad_personalization_signals: false });
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.appendChild(s);
})();
