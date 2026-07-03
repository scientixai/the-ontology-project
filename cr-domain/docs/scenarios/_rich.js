<script>(function(){document.querySelectorAll('[role="tablist"]').forEach(function(l){l.addEventListener('click',function(e){var b=e.target.closest('[role="tab"]');if(!b)return;l.querySelectorAll('[role="tab"]').forEach(function(t){t.setAttribute('aria-selected','false');var p=document.getElementById(t.getAttribute('aria-controls'));if(p)p.hidden=true;});b.setAttribute('aria-selected','true');var p=document.getElementById(b.getAttribute('aria-controls'));if(p)p.hidden=false;});});})();</script>
<script>(function(){
 var m=document.getElementById('recModal'), sm=document.getElementById('sdtmModal');
 var sel=document.getElementById('rm-select'), inp=document.getElementById('rm-input');
 var OTHER='__other__';
 function esc(x){var d=document.createElement('div');d.textContent=x;return d.innerHTML;}
 function fill(b){
   ['term','match','conf','why','after','record','hint','sub'].forEach(function(k){
     var el=document.getElementById('rm-'+k); if(el){el.innerHTML=b.getAttribute('data-'+k)||'&mdash;';}
   });
   document.getElementById('rm-title').textContent='Reconcile — '+(b.getAttribute('data-term')||'');
   var cta=document.getElementById('rm-cta');
   cta.textContent=b.getAttribute('data-cta')||'Confirm mapping';
   cta.setAttribute('data-row', b.getAttribute('data-row')||'');
   cta.setAttribute('data-cell', b.getAttribute('data-concept-cell')||'');
   // build the candidate dropdown
   sel.innerHTML='';
   (b.getAttribute('data-options')||'').split('||').filter(Boolean).forEach(function(opt){
     var o=document.createElement('option'); o.value=opt; o.innerHTML=opt; sel.appendChild(o);
   });
   var o=document.createElement('option'); o.value=OTHER; o.textContent='Other — type it below…'; sel.appendChild(o);
   inp.hidden=true; inp.value='';
 }
 sel && sel.addEventListener('change',function(){
   inp.hidden=(sel.value!==OTHER); if(!inp.hidden){inp.focus();}
 });
 document.querySelectorAll('.rec-btn').forEach(function(b){
   b.addEventListener('click',function(){fill(b);m.classList.add('open');});
 });
 function chosen(){
   if(sel.value===OTHER){return inp.value.trim();}
   return sel.value;
 }
 document.getElementById('rm-cta').addEventListener('click',function(){
   var val=chosen(); if(!val){inp.hidden=false;inp.focus();return;}
   var cell=document.getElementById(this.getAttribute('data-row'));
   if(cell){cell.className='resolved-cell';cell.innerHTML='&#10003; reconciled';}
   var cc=document.getElementById(this.getAttribute('data-cell'));
   if(cc){cc.innerHTML=val; var tr=cc.closest('tr'); if(tr){tr.classList.remove('kri-site-active');}}
   var a=document.getElementById('cnt-auto'),c=document.getElementById('cnt-confirm');
   if(a&&c){a.textContent=(+a.textContent)+1;c.textContent=Math.max(0,(+c.textContent)-1);}
   m.classList.remove('open');
 });
 // SDTM projection modal
 var see=document.getElementById('see-sdtm');
 see && see.addEventListener('click',function(){sm.classList.add('open');});
 [m,sm].forEach(function(x){ x && x.addEventListener('click',function(e){
   if(e.target===x||e.target.hasAttribute('data-close')){x.classList.remove('open');}
 });});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'){m.classList.remove('open');sm.classList.remove('open');}});
})();</script>