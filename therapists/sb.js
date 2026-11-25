/* Shared Supabase setup for therapist pages (profile + dashboard).
   The publishable key is public by design; all access rules live in the database (RLS). */
(function () {
  'use strict';
  var URL = 'https://putqeswsycwyxxrdcmyh.supabase.co';
  var KEY = 'sb_publishable_Yg7WovbSlye0T9CV8PHbYw_zBuhFR11';
  var BUCKET = 'therapist-photos';

  var client = null;
  try {
    if (window.supabase && window.supabase.createClient) {
      client = window.supabase.createClient(URL, KEY, {
        auth: { persistSession: true, detectSessionInUrl: true, autoRefreshToken: true }
      });
    }
  } catch (e) { client = null; }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'text') n.textContent = v;
      else if (k === 'class') n.className = v;
      else if (k.slice(0, 2) === 'on' && typeof v === 'function') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : String(v));
    });
    (children || []).forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return n;
  }

  function safeUrl(u) {
    u = String(u || '').trim();
    return /^https:\/\/[^\s<>"']+$/i.test(u) ? u : '';
  }

  function youtubeId(u) {
    u = safeUrl(u);
    if (!u) return '';
    var m = u.match(/^https:\/\/(?:www\.|m\.)?youtube\.com\/(?:watch\?(?:[^#]*&)?v=|shorts\/|embed\/|live\/)([A-Za-z0-9_-]{11})/) ||
            u.match(/^https:\/\/youtu\.be\/([A-Za-z0-9_-]{11})/);
    return m ? m[1] : '';
  }

  function youtubeEmbed(u, title) {
    var id = youtubeId(u);
    if (!id) return null;
    return el('div', { class: 'tp-video' }, [
      el('iframe', {
        src: 'https://www.youtube-nocookie.com/embed/' + id,
        title: title || 'فيديو',
        loading: 'lazy',
        allow: 'accelerometer; encrypted-media; gyroscope; picture-in-picture',
        allowfullscreen: true,
        referrerpolicy: 'strict-origin-when-cross-origin'
      })
    ]);
  }

  function photoUrl(path) {
    path = String(path || '');
    if (!/^[0-9a-f-]{36}\/[A-Za-z0-9._-]+$/.test(path)) return '';
    return URL + '/storage/v1/object/public/' + BUCKET + '/' + path;
  }

  function initial(name) {
    var rest = String(name || '').replace('د.', '');
    for (var i = 0; i < rest.length; i++) {
      if (/[؀-ۿA-Za-z]/.test(rest[i])) return rest[i];
    }
    return 'د';
  }

  var dateFmt;
  try { dateFmt = new Intl.DateTimeFormat('ar-EG', { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { dateFmt = null; }
  function date(iso) {
    try { return dateFmt ? dateFmt.format(new Date(iso)) : String(iso).slice(0, 10); } catch (e) { return ''; }
  }

  window.TP = {
    client: client, URL: URL, BUCKET: BUCKET,
    el: el, safeUrl: safeUrl, youtubeId: youtubeId, youtubeEmbed: youtubeEmbed,
    photoUrl: photoUrl, initial: initial, date: date
  };
})();
