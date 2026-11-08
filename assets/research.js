(() => {
  const $ = (id) => document.getElementById(id);
  const isEn = document.documentElement.lang === "en";
  const tr = (ar, en) => isEn ? en : ar;
  const form = $("research-query"), button = $("research-submit");
  const status = $("research-status"), results = $("research-results");
  const count = $("results-count"), title = $("results-title");
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const terms = (q) => q.trim().split(/\s+/).filter(Boolean).slice(0,8);
  function card(source, heading, description, url, meta="") {
    return '<article class="research-card"><span class="source-tag">'+esc(source)+'</span><h3>'+esc(heading)+'</h3>' +
      (description ? '<p>'+esc(description)+'</p>' : '') + (meta ? '<p>'+esc(meta)+'</p>' : '') +
      '<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">افتح المصدر الأصلي ↗</a></article>';
  }
  async function searchSite(q) {
    const sitemap = await fetch("/sitemap.xml",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("تعذر قراءة فهرس الموقع");return r.text();});
    const doc = new DOMParser().parseFromString(sitemap,"application/xml");
    const urls = [...doc.querySelectorAll("loc")].map(n=>n.textContent.trim()).filter(u=>new URL(u).origin===location.origin);
    const selected = urls.filter(u=>/\/articles\/|\/tests\/|\/paths\/|\/platform\//.test(new URL(u).pathname)).slice(0,35);
    const words = terms(q).map(w=>w.toLowerCase());
    const pages = await Promise.all(selected.map(async url=>{
      try {
        const html=await fetch(url,{signal:AbortSignal.timeout(7000)}).then(r=>r.ok?r.text():"");
        const d=new DOMParser().parseFromString(html,"text/html");
        const heading=d.querySelector("h1")?.textContent?.trim() || d.title;
        const desc=d.querySelector('meta[name="description"]')?.content || "";
        const body=(d.querySelector("main")?.textContent || d.body.textContent || "").replace(/\s+/g," ").slice(0,600);
        const hay=(heading+" "+desc+" "+body).toLowerCase();
        const score=words.reduce((n,w)=>n+(hay.includes(w)?1:0),0);
        return score?{heading,desc,url,score}:null;
      } catch { return null; }
    }));
    return pages.filter(Boolean).sort((a,b)=>b.score-a.score).slice(0,8)
      .map(x=>card(tr("محتوى الموقع","Site content"),x.heading,x.desc,x.url));
  }
  async function searchPubMed(q) {
    const base="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/";
    const ids=await fetch(base+"esearch.fcgi?db=pubmed&retmode=json&retmax=8&sort=relevance&term="+encodeURIComponent(q))
      .then(r=>{if(!r.ok)throw Error("PubMed غير متاح مؤقتًا");return r.json();});
    const list=ids.esearchresult?.idlist||[];
    if(!list.length)return [];
    const data=await fetch(base+"esummary.fcgi?db=pubmed&retmode=json&id="+list.join(",")).then(r=>r.json());
    return list.map(id=>{const x=data.result?.[id];if(!x)return "";const authors=(x.authors||[]).slice(0,3).map(a=>a.name).join(", ");
      return card("PubMed",x.title||"Untitled study","", "https://pubmed.ncbi.nlm.nih.gov/"+id+"/", [x.fulljournalname||x.source,x.pubdate,authors].filter(Boolean).join(" · "));}).filter(Boolean);
  }
  async function searchCrossref(q) {
    const data=await fetch("https://api.crossref.org/works?rows=8&select=title,author,published,container-title,DOI,type&query.bibliographic="+encodeURIComponent(q),{headers:{"Accept":"application/json"}})
      .then(r=>{if(!r.ok)throw Error("Crossref غير متاح مؤقتًا");return r.json();});
    return (data.message?.items||[]).map(x=>{
      const heading=x.title?.[0]||"Untitled publication", authors=(x.author||[]).slice(0,3).map(a=>[a.given,a.family].filter(Boolean).join(" ")).join(", ");
      const date=x.published?.["date-parts"]?.[0]?.join("-")||"";
      const doi=x.DOI;
      return card("Crossref",heading,"",doi?"https://doi.org/"+doi:"https://search.crossref.org/?q="+encodeURIComponent(heading),[x["container-title"]?.[0],date,authors].filter(Boolean).join(" · "));
    });
  }
  async function run() {
    const q=form.value.trim();
    if(q.length<3){status.textContent=tr("اكتب سؤالًا أو موضوعًا من 3 أحرف على الأقل.","Enter a topic or question with at least 3 characters.");form.focus();return;}
    button.disabled=true;button.textContent=tr("جارٍ البحث…","Searching…");results.innerHTML="";status.className="research-status";status.textContent=tr("بنبحث في المصادر المحددة. قد يستغرق الأمر عدة ثوانٍ.","Searching the selected sources. This may take a few seconds.");
    const scope=$("research-scope").value;
    const tasks=[];
    if(scope!=="papers")tasks.push(searchSite(q).then(x=>({name:"site",items:x})).catch(e=>({name:"site",error:e.message,items:[]})));
    if(scope!=="site"){tasks.push(searchPubMed(q).then(x=>({name:"pubmed",items:x})).catch(e=>({name:"pubmed",error:e.message,items:[]})));
      tasks.push(searchCrossref(q).then(x=>({name:"crossref",items:x})).catch(e=>({name:"crossref",error:e.message,items:[]})));}
    const settled=await Promise.all(tasks);
    const html=settled.flatMap(x=>x.items);
    results.innerHTML=html.join("");
    count.textContent=html.length+(isEn?" results":" نتيجة");
    title.textContent=tr("نتائج البحث عن: ","Search results for: ")+q;
    const errors=settled.filter(x=>x.error).map(x=>x.error);
    if(html.length)status.textContent=tr("تم العثور على نتائج. راجع كل مصدر وافتح الدراسة الأصلية؛ لا تعرض هذه النسخة التجريبية ملخصًا مولّدًا بالذكاء الاصطناعي بعد.","Results found. Review each source and open the original publication. AI-generated summaries are not included in this prototype yet.");
    else status.textContent=errors.length?tr("لم نتمكن من جلب نتائج من بعض المصادر. حاول مرة أخرى أو غيّر صياغة البحث.","Some sources could not be reached. Try again or rephrase your search."):tr("لم نعثر على نتائج مطابقة. جرّب كلمات مفتاحية أوسع أو باللغة الإنجليزية.","No matching results. Try broader keywords or search in English.");
    if(errors.length)status.textContent+=" ("+errors.join(isEn?"; ":"؛ ")+")";
    button.disabled=false;button.textContent=tr("ابدأ البحث","Search");
  }
  button.addEventListener("click",run);
  form.addEventListener("keydown",e=>{if(e.key==="Enter"&&(e.metaKey||e.ctrlKey)){e.preventDefault();run();}});
})();