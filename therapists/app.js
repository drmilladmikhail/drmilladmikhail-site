(function(){
  var DOCS = {
    d1:{name:'د. (اسم الدكتور ١)', spec:'قلق وضغوط', tags:['قلق','ضغوط','نوبات هلع'], exp:'١٠ سنين', next:'الأربعاء ٨:٠٠ م', langs:'عربي'},
    d2:{name:'د. (اسم الدكتور ٢)', spec:'علاقات وأسرة', tags:['علاقات','تواصل','أسرة'], exp:'٧ سنين', next:'الخميس ٦:٣٠ م', langs:'عربي'},
    d3:{name:'د. (اسم الدكتور ٣)', spec:'اكتئاب ونوم', tags:['اكتئاب','نوم'], exp:'١٥ سنة', next:'الجمعة ٩:٠٠ ص', langs:'عربي'}
  };


  var SLUGS = {d1:'doctor-1', d2:'doctor-2', d3:'doctor-3'};
  var SLOTS = {tue:'الثلاثاء ٧:٠٠ م', wed:'الأربعاء ٨:٠٠ م', thu:'الخميس ٦:٣٠ م', sat:'السبت ٥:٠٠ م'};
  var state = {doc:'d1', dur:'60', slot:'wed'};

  function $(s){ return document.querySelector(s); }
  function $$(s){ return Array.prototype.slice.call(document.querySelectorAll(s)); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function currentDocKey(){ return state.doc === 'auto' ? 'd1' : state.doc; }

  function summaryParts(){
    var d = DOCS[currentDocKey()];
    return {
      doc: d.name + (state.doc === 'auto' ? ' (اقتراحنا لك)' : ''),
      dur: state.dur === '60' ? '٦٠ دقيقة · ١٠٠٠ جنيه' : '٣٠ دقيقة',
      slot: SLOTS[state.slot]
    };
  }

  function refresh(){
    $$('[data-group]').forEach(function(group){
      var key = group.getAttribute('data-group');
      var stateKey = key === 'doc' ? 'doc' : key === 'dur' ? 'dur' : 'slot';
      group.querySelectorAll('[data-value]').forEach(function(b){
        b.setAttribute('aria-pressed', String(b.getAttribute('data-value') === state[stateKey]));
      });
    });
    var p = summaryParts();
    $('#sumLine').textContent = p.doc + ' · ' + p.dur + ' · ' + p.slot;
  }

  $$('[data-group]').forEach(function(group){
    group.addEventListener('click', function(e){
      var b = e.target.closest('[data-value]');
      if(!b) return;
      var key = group.getAttribute('data-group');
      var stateKey = key === 'doc' ? 'doc' : key === 'dur' ? 'dur' : 'slot';
      state[stateKey] = b.getAttribute('data-value');
      refresh();
    });
  });

  function renderDoctors(){
    var list = $('#doctorList');
    list.innerHTML = '';
    Object.keys(DOCS).forEach(function(k){
      var d = DOCS[k];
      var card = document.createElement('article');
      card.className = 'doc-card';
      card.innerHTML =
        '<div class="doc-head"><div class="avatar" aria-hidden="true">د</div><div><h3>' + d.name + '</h3><p>معالج نفسي · جلسات أونلاين</p></div></div>' +
        '<div class="tags">' + d.tags.map(function(t){ return '<span class="tag">' + t + '</span>'; }).join('') + '</div>' +
        '<div class="meta-row"><span>الخبرة <b>' + d.exp + '</b></span><span>الجلسة <b>١٠٠٠ ج</b></span></div>' +
        '<div class="meta-row"><span>أقرب ميعاد</span><b>' + d.next + '</b></div>' +
        '<div class="card-actions">' +
          '<a class="btn btn-outline btn-block" href="/therapists/' + SLUGS[k] + '/">عرض البروفايل</a>' +
          '<a class="btn btn-gold btn-block" href="#booking" data-book="' + k + '">احجز مع ' + d.name + '</a>' +
        '</div>';
      list.appendChild(card);
    });
  }

  $('#doctorList').addEventListener('click', function(e){
    var b = e.target.closest('[data-book]');
    if(!b) return;
    state.doc = b.getAttribute('data-book');
    refresh();
  });

  $('#bookForm').addEventListener('submit', function(e){
    e.preventDefault();
    var f = e.target;
    var err = $('#formError');
    if(!f.fullname.value.trim() || !f.phone.value.trim() || !f.consent.checked){
      err.textContent = 'اكتب اسمك ورقم موبايلك، ووافق على استخدام البيانات عشان نكمل.';
      err.hidden = false;
      return;
    }
    err.hidden = true;
    var p = summaryParts();
    $('#successText').textContent = 'شكراً ' + f.fullname.value.trim() + '. طلبك: ' + p.doc + '، ' + p.dur + '، ' + p.slot + '.';
    f.hidden = true;
    var ok = $('#success');
    ok.hidden = false;
    ok.focus();
  });

  var VIEWS = ['home','team','booking'];
  function route(){
    var raw = (location.hash || '#home').slice(1);
    var view = 'home';
    if(raw.indexOf('doc-') === 0 && SLUGS[raw.slice(4)]){
      location.replace('/therapists/' + SLUGS[raw.slice(4)] + '/');
      return;
    } else if(VIEWS.indexOf(raw) !== -1){
      view = raw;
    }
    $$('[data-view]').forEach(function(s){ s.hidden = s.getAttribute('data-view') !== view; });
    var navId = view;
    $$('[data-nav]').forEach(function(a){ a.classList.toggle('active', a.getAttribute('data-nav') === navId); });
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route);

  renderDoctors();
  refresh();
  route();
})();
