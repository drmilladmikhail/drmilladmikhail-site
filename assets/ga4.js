/* Google Analytics 4, loaded only when content/analytics.json has his Measurement ID (tools/add_analytics.py).
   No inline script (the site's CSP forbids it): this file sets up gtag and loads Google's library. */
(function () {
  var me = document.currentScript;
  var id = me && me.getAttribute('data-ga4');
  if (!id || !/^G-[A-Z0-9]+$/.test(id)) return;
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  /* Consent Mode: no advertising storage anywhere; for visitors in the EU/EEA, UK and Switzerland
     analytics runs cookieless (no _ga cookie) because the site has no consent banner. */
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
  gtag('consent', 'default', { analytics_storage: 'denied', region: ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH'] });
  gtag('js', new Date());
  /* IP anonymisation is automatic in GA4; no ad personalisation signals */
  gtag('config', id, { allow_google_signals: false, allow_ad_personalization_signals: false });
  /* 2026-11-24 (batch 2, his approval): count taps on the booking links only, so we can tell which
     part of the site brings people to «احجز جلسة». The event carries where on the page the link sat
     (header, hero, article, test, footer, page) and nothing else: no text, no answers, no scores. */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var h = a.getAttribute('href') || '';
    var ev = /^\/sessions\/?(#.*)?$/.test(h) ? 'book_click' : (/^https:\/\/wa\.me\/12012758490/.test(h) ? 'whatsapp_book' : '');
    if (!ev) return;
    var place = a.closest('.topbar') ? 'header' : a.closest('.clarity-hero') ? 'hero' : a.closest('.session-box') ? 'article' :
      a.closest('.result') ? 'test' : a.closest('.footer') ? 'footer' : 'page';
    gtag('event', ev, { place: place, transport_type: 'beacon' });
  }, true);
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.appendChild(s);
})();
