(function(){
const MS=864e5,D=(y,m,d)=>new Date(y,m-1,d);
function easter(y){const a=y%19,b=Math.floor(y/100),c=y%100,d=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),g=Math.floor((b-f+1)/3),h=(19*a+b-d-g+15)%30,i=Math.floor(c/4),k=c%4,l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451),mo=Math.floor((h+l-7*m+114)/31),da=(h+l-7*m+114)%31+1;return D(y,mo,da)}
function advent1(y){const x=D(y,12,25);let back=x.getDay()||7;return new Date(x-(back+21)*MS)}
const add=(d,n)=>new Date(+d+n*MS),days=(a,b)=>Math.round((b-a)/MS);
const ord=n=>n+(['th','st','nd','rd'][(n%100>10&&n%100<14)?0:(n%10<4?n%10:0)]||'th');
const S={advent:['Advent','#5b3f8c','Violet / blue'],christmas:['Christmas','#d9c27a','White & gold'],epiphany:['Epiphany','#3f7d4a','White, then green'],lent:['Lent','#4a2f6e','Violet'],'holy-week':['Holy Week','#9b1c1c','Red & violet'],easter:['Easter','#e3cf7a','White & gold'],pentecost:['Pentecost','#c4291c','Red'],'ordinary-time':['Ordinary Time / after Pentecost','#2f6b3a','Green']};
window.churchYear=function(t){t=t||new Date();t=D(t.getFullYear(),t.getMonth()+1,t.getDate());
 let y=t.getFullYear(),a1=advent1(y);if(t<a1){y--;a1=advent1(y)}
 const ly={1:'A',2:'B',0:'C'}[(y+1)%3],E=easter(y+1),ash=add(E,-46),palm=add(E,-7),pent=add(E,49),xmas=D(y,12,25),epi=D(y+1,1,6),na1=advent1(y+1);
 const sun=add(t,(7-t.getDay())%7);let s,label;
 if(t<xmas){s='advent';label=ord(Math.floor(days(a1,sun)/7)+1)+' Sunday of Advent'}
 else if(t<epi){s='christmas';label=days(xmas,t)<1?'Christmas Day':'Christmastide (Twelve Days)'}
 else if(t<ash){s='epiphany';const n=Math.floor(days(epi,sun)/7);label=sun>=add(ash,-3)?'Transfiguration Sunday (Lutheran)':(n<1?'Baptism of the Lord':ord(n+1)+' Sunday after Epiphany')}
 else if(t<palm){s='lent';const n=Math.ceil(days(ash,sun)/7);label=t<add(ash,4)?'Ash Wednesday week':ord(n)+' Sunday in Lent'}
 else if(t<E){s='holy-week';label=['Palm Sunday','Holy Monday','Holy Tuesday','Holy Wednesday','Maundy Thursday','Good Friday','Holy Saturday'][days(palm,t)]}
 else if(t<pent){s='easter';label=days(E,t)===0?'Easter Day':ord(Math.floor(days(E,sun)/7)+1)+' Sunday of Easter'}
 else if(t<add(pent,7)){s='pentecost';label=days(pent,t)===0?'Day of Pentecost':'Week of Pentecost; Holy Trinity next Sunday'}
 else{s='ordinary-time';const ck=add(na1,-7);label=+sun===+ck?'Christ the King':ord(34-days(sun,ck)/7)+' Sunday in Ordinary Time · '+ord(days(pent,sun)/7)+' Sunday after Pentecost'}
 return {season:s,name:S[s][0],color:S[s][1],colname:S[s][2],label,year:ly,sunday:sun,easter:E}};
document.querySelectorAll('[data-cy]').forEach(el=>{const c=churchYear();const f=d=>d.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'});
 el.innerHTML=`<div class=k>This week in the Church Year</div><h2 style="border:0;margin:.2em 0"><span class=dot style="background:${c.color}"></span>${c.name}</h2><p style="margin:.2em 0"><b>${c.label}</b> (Sunday ${f(c.sunday)})<br><span class=src>Liturgical colour: ${c.colname} · Lectionary Year ${c.year} · Easter ${c.easter.getFullYear()}: ${f(c.easter)}</span></p><p style="margin:.4em 0 0"><a href="/church-year/${c.season}/">About ${c.name} →</a> &nbsp; <a href="/church-year/sundays/">Sunday readings →</a></p>`;
 el.style.borderLeft='8px solid '+c.color;
 document.querySelectorAll('.wheel [data-s="'+c.season+'"]').forEach(p=>p.classList.add('now'));});
})();
