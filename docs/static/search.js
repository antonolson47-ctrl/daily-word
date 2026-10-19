(function(){let I=[];const q=document.getElementById('q'),R=document.getElementById('res'),N=document.getElementById('cnt');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fold=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
function run(){const v=fold(q.value.trim());if(v.length<2){R.innerHTML='';N.textContent=I.length?I.length+' pages indexed. Type at least 2 letters.':'';return}
const w=v.split(/\s+/);const hits=[];for(const p of I){const T=fold(p.t),X=fold(p.d+' '+p.x);let sc=0,ok=true;for(const k of w){if(T.includes(k))sc+=10;else if(X.includes(k))sc+=1;else{ok=false;break}}if(ok)hits.push([sc,p])}
hits.sort((a,b)=>b[0]-a[0]);const top=hits.slice(0,40);
N.textContent=hits.length+' result'+(hits.length==1?'':'s')+(hits.length>40?' (showing 40)':'');
R.innerHTML=top.map(([s,p])=>{const X=p.x,i=fold(X).indexOf(w[0]);const sn=i>=0?'…'+X.slice(Math.max(0,i-60),i+120)+'…':p.d;return '<a class=card href="'+p.u+'"><span class=badge>'+esc(p.s)+'</span> <b>'+esc(p.t)+'</b><br><span class=src>'+esc(sn)+'</span></a>'}).join('')}
fetch('/search-index.json').then(r=>r.json()).then(j=>{I=j;const u=new URLSearchParams(location.search).get('q');if(u)q.value=u;run()});q.addEventListener('input',run);})();
