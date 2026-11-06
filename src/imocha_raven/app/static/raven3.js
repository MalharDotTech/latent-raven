/* Presentation of recorded Raven 3 traces only. No inference or tuning happens here. */
(() => {
  'use strict';
  const $ = id => document.getElementById('r3-' + id);
  if (!$('dag')) return;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num = (value, digits = 4) => value == null ? '—' : Number(value).toFixed(digits);
  const pct = value => value == null ? '—' : (Number(value) * 100).toFixed(1) + '%';
  const signed = value => Number(value) >= 0 ? '+' + value : String(value);
  const owner = name => ({auto:'tuned by feedback loop', human:'human-owned', contract:'contract', formula:'formula · no knob'}[name] || name);
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width: 760px)');
  async function get(path, signal) {
    const response = await fetch('/scoreboard/raven3/' + path, {credentials:'same-origin', signal});
    if (!response.ok) {
      if (response.status === 403) throw new Error('Organiser session expired. Open the engine room and unlock it again.');
      let detail;
      if (response.headers.get('content-type')?.includes('application/json')) detail = (await response.json()).detail;
      throw new Error(detail || (response.status === 404 ? 'No cached evidence is available for this selection. Choose another person or skill.' : 'Could not load this section. Please retry.'));
    }
    return response.json();
  }
  const state = {params:[], selected:'P1', detail:null, steps:[], step:0, timer:null, playing:false, request:0,
    controller:null, replay:null, round:0, fbTimer:null, fbPlaying:false, tab:'sim', expanded:false};
  const shortNames = {IN1:'Verified quote', IN2:'Type + level', IN3:'Trust group', P1:'Evidence Q', P2:'Group cap', P3:'Recency decay', P4:'Dependence', P5:'P(has)', P6:'Level noise', P7:'shift', P8:'Level posterior', P9:'Accepted band', P10:'Best level l*', P11:'p_yes', P12:'No level → hold', P13:'tau gate', POL:'Send policy', OUT:'Send / hold'};
  const stages = ['input','evidence','possession','level','decision','policy','OUT'];
  const svgText = (x,y,content,attrs='') => `<text x="${x}" y="${y}" ${attrs}>${esc(content)}</text>`;
  function drawDag() {
    if (!state.params.length) return;
    const narrow = mobile.matches, w = narrow ? 370 : 1430;
    const positions = {}, headings = [];
    let y = 32;
    stages.forEach((stage, column) => {
      const nodes = stage === 'OUT' ? [{id:'OUT',owner:'contract',name:'Send / hold'}] : state.params.filter(p => p.stage === stage);
      if (narrow) {
        headings.push(svgText(12,y,stage.toUpperCase(),'class="r3-dag-heading"'));
        nodes.forEach((p,i) => { positions[p.id] = {x:12+(i%2)*180,y:y+18+Math.floor(i/2)*90,w:166,h:70,p}; });
        y += 55 + Math.ceil(nodes.length/2)*90;
      } else {
        headings.push(svgText(12+column*203,24,stage.toUpperCase(),'class="r3-dag-heading"'));
        nodes.forEach((p,i) => { positions[p.id] = {x:12+column*203,y:52+i*96,w:178,h:76,p}; });
      }
    });
    const h = narrow ? y+110 : 750;
    positions.FB = {x:narrow?100:650,y:h-82,w:178,h:66,p:{id:'FB',name:'Feedback loop',owner:'auto'}};
    const path = (from,to,dashed=false) => {
      const a=positions[from], b=positions[to]; if (!a || !b) return '';
      let d;
      if (narrow) { const ax=a.x+a.w/2, bx=b.x+b.w/2; d=`M${ax} ${a.y+a.h} C${ax} ${a.y+a.h+24},${bx} ${b.y-24},${bx} ${b.y}`; }
      else { const ax=a.x+a.w, by=b.y+b.h/2, ay=a.y+a.h/2; d=`M${ax} ${ay} C${ax+38} ${ay},${b.x-38} ${by},${b.x} ${by}`; }
      if (dashed) d=narrow?`M${a.x} ${a.y+30} C0 ${a.y},0 ${b.y},${b.x} ${b.y+35}`:`M${a.x+a.w/2} ${a.y} C${a.x+a.w/2} ${a.y-45},${b.x+b.w/2} ${a.y-45},${b.x+b.w/2} ${b.y+b.h}`;
      return `<path d="${d}" class="r3-edge ${dashed?'feedback-edge':''}" marker-end="url(#r3-arrow)"><title>${esc(from)} → ${esc(to)}</title></path>`;
    };
    const edges=state.params.flatMap(p=>p.feeds.map(id=>path(p.id,id))).join('')+path('FB','P7',true)+path('FB','P13',true);
    const nodes=Object.values(positions).map(({x,y,w,h,p}) => `<g class="r3-dag-node owner-${esc(p.owner)} ${state.selected===p.id?'selected':''}" transform="translate(${x},${y})" ${['OUT','FB'].includes(p.id)?'':`role="button" tabindex="0" data-node="${esc(p.id)}" aria-label="${esc(p.id+' '+p.name+', '+owner(p.owner))}" aria-pressed="${state.selected===p.id}"`}><rect width="${w}" height="${h}" rx="8"/>${svgText(10,19,p.id==='FB'?'FEEDBACK LOOP':p.id,'class="r3-dag-id"')}${svgText(10,40,shortNames[p.id]||p.name,'class="r3-dag-name"')}${svgText(10,h-9,p.id==='FB'?'Latent answers':p.owner==='auto'?'tuned by feedback loop':p.owner,'class="r3-dag-owner"')}</g>`).join('');
    $('dag').innerHTML=`<svg viewBox="0 0 ${w} ${h}" class="r3-dag-svg" aria-label="Parameter dependency graph. Select a parameter to inspect it."><defs><marker id="r3-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>${headings.join('')}${edges}${nodes}</svg>`;
  }
  function selectNode(id) {
    const p=state.params.find(p=>p.id===id); if (!p) return;
    state.selected=id;
    $('node').innerHTML=`<p class="eyebrow">${esc(p.id)} / ${esc(p.stage)}</p><h3>${esc(p.name)}</h3><span class="r3-owner owner-${esc(p.owner)}">${esc(owner(p.owner))}</span><h4>Value</h4><pre>${esc(p.value)}</pre><p>${esc(p.does)}</p><h4>Where it came from</h4><p class="tiny muted">${esc(p.source)}</p><p class="tiny muted">Feeds: ${p.feeds.map(esc).join(' → ')}</p>`;
    $('dag').querySelectorAll('[data-node]').forEach(node=>{const chosen=node.dataset.node===id;node.classList.toggle('selected',chosen);node.setAttribute('aria-pressed',String(chosen));});
  }
  $('dag').addEventListener('click',event=>{const node=event.target.closest('[data-node]');if(node)selectNode(node.dataset.node);});
  $('dag').addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){const node=event.target.closest('[data-node]');if(node){event.preventDefault();selectNode(node.dataset.node);}}});
  mobile.addEventListener('change',()=>{drawDag();if(state.replay){const s=scenario();const r=s?.rounds?.[Math.max(0,state.round-1)];drawChart('sim-chart',s?.curve||[],r?(state.round?r.tau_to:r.tau_from):.75,s?.target??state.replay.target);drawChart('live-chart',state.replay.live.curve,state.replay.live.current.tau,state.replay.target);}});
  async function loadParams() {
    try {
      const data=await get('params');state.params=data.params;drawDag();selectNode(state.selected);
      $('map-status').textContent='Select a node to inspect it. Solid edges follow the registry’s feeds.';
      $('not-yet').innerHTML=data.not_yet.map(row=>`<article><h4>${esc(row.idea)}</h4><p>${esc(row.status)}</p><small class="muted">${esc(row.source)}</small></article>`).join('');
      $('sources').innerHTML=Object.entries(data.sources).map(([key,value])=>`<dt>${esc(key)}</dt><dd>${esc(value)}</dd>`).join('');
    } catch(error) { $('map-status').textContent=error.message; }
  }
  function pause() { clearTimeout(state.timer); state.playing=false; $('play').textContent='Play'; }
  function pauseFeedback() { clearTimeout(state.fbTimer);state.fbPlaying=false;$('fb-play').textContent='Play'; }
  function schedule() {clearTimeout(state.timer);if(state.playing)state.timer=setTimeout(()=>{move(1);schedule();},Number($('speed').value));}
  function move(delta) {state.step=Math.max(0,Math.min(state.steps.length-1,state.step+delta));if(state.step===state.steps.length-1)pause();renderDecision();}
  function buildSteps(detail) {
    const steps=[{kind:'intro',ids:[],caption:'IN1–IN3 · Verified quotes arrive with a type, a source and a trust group.'}];
    detail.records.forEach((r,index)=>{
      steps.push({kind:'record',index,phase:0,ids:['P1','P2','P3'],caption:`P1–P3 · Record ${index+1}: read its type, cap its trust group and age its evidence.`});
      steps.push({kind:'record',index,phase:1,ids:['P1','P2','P3'],caption:'P1–P3 · q = min(Q, group cap) × decay. A cap is a ceiling, not a second multiplier.'});
      steps.push({kind:'record',index,phase:2,ids:['P4','P5'],caption:'P4–P5 · Discount dependence, then combine the remaining weight with noisy-OR.'});
    });
    detail.records.forEach((r,index)=>{if(r.level_used!=null)steps.push({kind:'level',index,ids:['P6','P7','P8'],caption:`P6–P8 · Record ${index+1}: a noisy level reading updates the posterior; shift corrects applied work.`});});
    if (!detail.level_evidence) steps.push({kind:'no-level',ids:['P12'],caption:'P12 · No usable record shows a level. A flat distribution is not a level reading.'});
    Object.keys(detail.band_prob).forEach(level=>steps.push({kind:'band',level:Number(level),ids:['P9','P10'],caption:`P9–P10 · Candidate L${level}: sum its accepted band; l* holds the most probability.`}));
    steps.push({kind:'gate',ids:['P11','P12','P13'],caption:'P11–P13 · Multiply possession by the winning band probability, then check the no-level rule and tau.'});
    steps.push({kind:'final',ids:['P12','P13','POL'],caption:'P12–P13 + POL · The threshold, level-evidence rule and shared send policy produce the verdict.'});
    return steps;
  }
  function probabilities(loglik) {const peak=Math.max(...loglik);const values=loglik.map(v=>Math.exp(v-peak));const total=values.reduce((a,b)=>a+b,0);return values.map(v=>v/total);}
  function mini(ids) {
    $('mini').innerHTML=Array.from({length:13},(_,i)=>'P'+(i+1)).map(id=>`<button data-param="${id}" class="${ids.includes(id)?'active':''}" aria-label="Inspect ${id}: ${esc(shortNames[id])}" ${ids.includes(id)?'aria-current="step"':''}>${id}</button>`).join('<span aria-hidden="true">→</span>');
  }
  function renderDecision() {
    const d=state.detail;if(!d)return;const s=state.steps[state.step];mini(s.ids);
    $('counter').textContent=`${state.step+1} / ${state.steps.length}`;$('caption').textContent=s.caption;
    $('prev').disabled=state.step===0;$('next').disabled=state.step===state.steps.length-1;$('play').disabled=state.step===state.steps.length-1;
    const recordPhase=s.kind==='record';
    const count=s.kind==='intro'?0:recordPhase?s.index+(s.phase===2?1:0):d.records.length;
    const ph=count?d.records[count-1].p_has_so_far:0;
    $('ph-number').textContent=pct(ph);$('ph-fill').style.width=(ph*100)+'%';$('ph-meter').setAttribute('aria-valuenow',num(ph*100,1));
    let pl=Array(d.scale_max).fill(1/d.scale_max);
    if(s.kind==='level')pl=probabilities(d.records[s.index].loglik_so_far);
    else if(['band','gate','final'].includes(s.kind))pl=d.level_dist;
    // Keep bar elements mounted so widths interpolate between recorded readings.
    if($('level-bars').children.length!==d.scale_max)$('level-bars').innerHTML=pl.map((_,i)=>`<div class="r3-prob-row"><span>L${i+1}</span><div><i></i></div><b></b></div>`).join('');
    [...$('level-bars').children].forEach((row,i)=>{row.querySelector('i').style.width=(pl[i]*100)+'%';row.querySelector('b').textContent=pct(pl[i]);row.setAttribute('aria-label',`Level ${i+1}: ${pct(pl[i])}`);});
    let html='';
    if(s.kind==='intro')html=`<p class="eyebrow">THE INPUT</p><h3>${esc(d.skill_name)}</h3><p>${d.records.length} verified records. Noisy-OR starts at zero; the level prior starts flat.</p><p class="muted">Press Next to let the first record enter. Every number comes from the explain endpoint.</p>`;
    if(recordPhase) {
      const r=d.records[s.index];html=`<p class="eyebrow">RECORD ${s.index+1} / ${d.records.length}</p><div class="chips"><span class="chip">${esc(r.type)}</span><span class="chip">${esc(r.group)}</span><span class="chip">${esc(r.cluster)}</span></div><blockquote>“${esc(r.quote)}”</blockquote><span class="source">${esc(r.source_id)} · ${num(r.age_years,2)} years old</span><div class="r3-calculation ${s.phase>=1?'revealed':''}"><span>min(Q ${num(r.base_q)}, cap ${num(r.group_cap)}) × decay ${num(r.decay)}</span><strong>= q ${s.phase>=1?num(r.q):'…'}</strong></div>${s.phase>=2?`<div class="r3-discount"><span class="badge">${esc(r.discount_why)} × ${r.discount}</span><p>q ${num(r.q)} × ${r.discount} = <strong>weight ${num(r.weight)}</strong></p></div><p class="tiny muted">P(has) = 1 − (1 − ${num(s.index?d.records[s.index-1].p_has_so_far:0)}) × (1 − ${num(r.weight)}) = ${num(r.p_has_so_far)}</p>`:'<p class="tiny muted">Next: '+(s.phase===0?'compute this record’s q.':'discount repetition before combining it.')+'</p>'}`;
    }
    if(s.kind==='level') {
      const r=d.records[s.index],shifted=r.level_used!==r.level_seen;
      html=`<p class="eyebrow">LEVEL READING / RECORD ${s.index+1}</p><h3>L${r.level_seen} → L${r.level_used}</h3><span class="badge">${shifted?'shift '+signed(d.shift)+' applied':r.type==='applied'?'shift '+signed(d.shift)+' · limited by scale ceiling':'No applied-work correction'}</span><blockquote>“${esc(r.quote)}”</blockquote><p>Weight ${num(r.weight)} scales this record’s level likelihood. The bars show the normalized accumulated log-likelihoods.</p><p class="tiny muted">P6 level noise × P7 correction → P8 posterior. Duplicates with zero weight contribute no reading.</p>`;
    }
    if(s.kind==='no-level')html='<p class="eyebrow">P12 / CONTRACT RULE</p><h3>No level evidence → hold.</h3><p>Evidence can establish the skill without establishing a level. A middle-level guess is not a reading.</p>';
    if(s.kind==='band') html=`<p class="eyebrow">P9 + P10 / PICK THE MESSAGE LEVEL</p><h3>${d.scale_max<=3?'K3 · exact level':'K4 · within ±1 level'}</h3><div class="r3-bands">${Object.entries(d.band_prob).map(([level,prob])=>`<div class="r3-band ${Number(level)===s.level?'current':''} ${Number(level)===d.best?'winner':''}"><b>L${level}${Number(level)===d.best?' · l*':''}</b><span>P(accepted) ${pct(prob)}</span><small>${d.scale_max<=3?'Exact: L'+level:'Band: '+[Number(level)-1,Number(level),Number(level)+1].filter(k=>k>=1&&k<=d.scale_max).map(k=>'L'+k).join(', ')}</small></div>`).join('')}</div><p>The winner is L${d.best}: its band [${d.accepted.map(k=>'L'+k).join(', ')}] holds ${pct(d.band_prob[d.best])} of the level probability.</p>`;
    if(['gate','final'].includes(s.kind)) {
      html=`<p class="eyebrow">P11 / THE PROBABILITY OF A YES</p><div class="r3-equation">${num(d.p_has)} <span>×</span> ${num(d.band_prob[d.best])}<strong>= ${num(d.p_yes)}</strong></div><p class="tiny muted">P(has) × P(accepted at L${d.best}) = p_yes</p><div class="r3-gauge" role="img" aria-label="p_yes ${pct(d.p_yes)}, tau ${pct(d.tau)}"><span style="width:${d.p_yes*100}%"></span><i style="left:${d.tau*100}%"></i></div><div class="r3-gauge-labels"><span>p_yes ${pct(d.p_yes)}</span><span>τ ${num(d.tau,3)}</span></div>${!d.level_evidence?'<div class="notice">P12 RULE STAMP · No record shows a level → hold, regardless of p_yes.</div>':''}`;
      if(s.kind==='final')html+=`<div class="r3-verdict ${d.action==='send'?'send':'hold'}"><p class="eyebrow">FINAL VERDICT / AFTER SEND POLICY</p><h3>${esc(d.action.toUpperCase().replaceAll('_',' '))}${d.level!=null?' · L'+esc(d.level):' · no level'}</h3><p>${esc(interpretation(d))}</p><details><summary>Recorded engine reason</summary><p class="tiny">${esc(d.reason)}</p></details></div>`;
    }
    $('decision-stage').innerHTML=html;
    const shown=d.records.slice(0,count);const rows=state.expanded?shown:shown.length>8?[...shown.slice(0,7),shown[shown.length-1]]:shown;
    $('record-history').innerHTML=shown.length?`${recordPhase&&s.index>=7&&s.index<d.records.length-1?`<button class="button secondary full r3-forward" data-forward>+${d.records.length-s.index-1} more records · fast-forward to level readings</button>`:''}<details class="r3-research" open><summary>${count} records combined · P(has) ${pct(ph)}</summary><div class="r3-record-stack" tabindex="0" role="region" aria-label="Combined evidence records">${rows.map(r=>`<article class="r3-record-mini"><div class="chips"><span class="chip">${esc(r.type)} / ${esc(r.group)}</span><span class="chip">${esc(r.discount_why)} × ${r.discount}</span></div><blockquote>“${esc(r.quote)}”</blockquote><span class="source">${esc(r.source_id)}</span><p>q ${num(r.q)} × ${r.discount} = <strong>weight ${num(r.weight)}</strong></p></article>`).join('')}</div>${shown.length>8?`<button class="button secondary" data-expand>${state.expanded?'Collapse':`+${shown.length-8} more records`}</button>`:''}</details>`:'';
  }
  function interpretation(d) {
    if(d.action==='send')return d.scale_max<=3?'Send: confident in the skill and its exact level.':'Send: confident in the skill and its level within ±1.';
    if(!d.level_evidence)return 'Hold: no record shows a level.';
    if(d.action==='hold'&&d.p_yes<d.tau)return 'Hold: below tau, bring stronger proof.';
    return 'The shared send policy stops this message. '+d.reason;
  }
  function clearDecision(message) {
    pause();state.detail=null;state.steps=[];$('decision-stage').textContent=message;$('record-history').replaceChildren();$('mini').replaceChildren();$('counter').textContent='';$('caption').textContent='Choose a person and skill with cached evidence.';$('ph-number').textContent='0%';$('ph-fill').style.width='0%';$('ph-meter').setAttribute('aria-valuenow','0');$('level-bars').replaceChildren();
    ['prev','next','play','restart'].forEach(id=>$(id).disabled=true);
  }
  async function loadDecision(changePerson=false) {
    state.controller?.abort();state.controller=new AbortController();const signal=state.controller.signal;const request=++state.request;
    clearDecision('Loading recorded calculations…');$('decision-status').textContent='Opening cached evidence…';
    const person=$('person').value;if(!person){$('decision-status').textContent='Choose a person to begin.';$('skill').disabled=true;clearDecision('No person selected.');return;}
    try {
      if(changePerson) {
        $('skill').disabled=true;$('skill').replaceChildren(new Option('Loading skills…',''));
        const result=await get('explain?'+new URLSearchParams({person}),signal);if(request!==state.request)return;
        $('skill').replaceChildren(...result.skills.map(id=>new Option(id.replaceAll('_',' '),id)));
        if(result.skills.includes('kubernetes'))$('skill').value='kubernetes';
        if(!result.skills.length)throw new Error('This person has no skills with verified evidence.');
      }
      const skill=$('skill').value;if(!skill)throw new Error('Choose a skill with verified evidence.');
      $('skill').disabled=false;
      const result=await get('explain?'+new URLSearchParams({person,skill}),signal);if(request!==state.request)return;
      state.detail=result;state.steps=buildSteps(result);state.step=0;state.expanded=false;
      $('restart').disabled=false;$('decision-status').textContent=`${result.skill_name} · ${result.records.length} records · τ ${num(result.tau,3)} · shift ${signed(result.shift)}`;renderDecision();
    } catch(error) {if(error.name==='AbortError'||request!==state.request)return;$('decision-status').textContent=error.message;clearDecision(error.message);}
  }
  $('person').addEventListener('change',()=>loadDecision(true));
  document.addEventListener('r3-picker-filtered',()=>{if(!$('person').value){state.controller?.abort();state.request++;clearDecision('Select a person from the filtered results.');$('skill').disabled=true;$('decision-status').textContent='Select a person from the filtered results.';}});
  $('skill').addEventListener('change',()=>loadDecision());
  $('prev').onclick=()=>{pause();move(-1);};$('next').onclick=()=>{pause();move(1);};
  $('restart').onclick=()=>{pause();state.step=0;renderDecision();};
  $('play').onclick=()=>{if(state.playing)pause();else{pauseFeedback();state.playing=true;$('play').textContent='Pause';schedule();}};
  $('speed').onchange=schedule;
  $('record-history').onclick=event=>{if(event.target.closest('[data-expand]')){state.expanded=!state.expanded;renderDecision();$('record-history').querySelector('details').open=true;}if(event.target.closest('[data-forward]')){pause();state.step=state.steps.findIndex(s=>['level','no-level','band'].includes(s.kind));renderDecision();}};
  $('mini').onclick=event=>{const button=event.target.closest('[data-param]');if(button){pause();selectNode(button.dataset.param);document.getElementById('parameters').scrollIntoView({behavior:motion.matches?'instant':'smooth'});}};
  function scenario() {return state.replay?.simulated?.[$('labels').value+'_'+$('start').value];}
  const chartDimensions=()=>mobile.matches?{width:400,left:44,right:340}:{width:800,left:58,right:738};
  const chartX=t=>{const d=chartDimensions();return d.left+(Math.max(.05,Math.min(.95,Number(t)))-.05)/.9*(d.right-d.left);};
  const chartY=p=>276-Number(p)*240;
  function segments(curve,key) {
    const parts=[];let points=[];
    curve.forEach(pt=>{if(pt[key]==null){if(points.length)parts.push(points);points=[];}else points.push(`${chartX(pt.tau)},${chartY(pt[key])}`);});
    if(points.length)parts.push(points);
    return parts.map(points=>`<polyline class="${key}" points="${points.join(' ')}"/>`).join('');
  }
  function drawChart(id,curve,tau,target) {
    if(!curve?.some(pt=>pt.precision!=null||pt.lower_bound!=null)){$(id).innerHTML='<div class="empty compact"><p>No labelled sends yet, so there is no precision curve to draw.</p></div>';return;}
    const dims=chartDimensions(),zoneWidth=(dims.right-dims.left)/90;
    const zones=curve.filter(pt=>pt.lower_bound!=null&&pt.lower_bound>=target).map(pt=>`<rect x="${Math.max(dims.left,chartX(pt.tau)-zoneWidth/2)}" y="36" width="${zoneWidth}" height="240" class="r3-safe-zone"/>`).join('');
    $(id).innerHTML=`<p class="tiny muted">Precision and its lower confidence bound · target ${pct(target)}</p><svg viewBox="0 0 ${dims.width} 332" role="img" aria-label="Precision and its lower confidence bound against tau from 0.05 to 0.95. Target ${pct(target)}. Current tau ${num(tau,3)}."><g class="r3-grid">${[0,.25,.5,.75,1].map(p=>`<line x1="${dims.left}" x2="${dims.right}" y1="${chartY(p)}" y2="${chartY(p)}"/>${svgText(3,chartY(p)+4,Math.round(p*100)+'%')}`).join('')}</g>${zones}<line x1="${dims.left}" x2="${dims.right}" y1="${chartY(target)}" y2="${chartY(target)}" class="r3-target"/>${svgText(dims.right+5,chartY(target)+5,Math.round(target*100)+'%','class="r3-target-label"')}${segments(curve,'precision')}${segments(curve,'lower_bound')}<g class="r3-tau-marker" style="transform:translateX(${chartX(tau)}px)"><line x1="0" x2="0" y1="28" y2="276"/>${svgText(0,18,'τ '+num(tau,3),'text-anchor="middle"')}</g>${[.05,.25,.5,.75,.95].map(t=>svgText(chartX(t),299,t.toFixed(2),'text-anchor="middle"')).join('')}${svgText(dims.width/2,325,'τ / SEND THRESHOLD','text-anchor="middle"')}</svg><details class="r3-chart-table"><summary>Inspect curve values</summary><div class="table-scroll" tabindex="0" role="region" aria-label="Feedback curve values"><table><thead><tr><th>Tau</th><th>Sends</th><th>Precision</th><th>Lower bound</th></tr></thead><tbody>${curve.map(pt=>`<tr><td>${num(pt.tau,2)}</td><td>${pt.sends}</td><td>${pct(pt.precision)}</td><td>${pct(pt.lower_bound)}</td></tr>`).join('')}</tbody></table></div></details>`;
  }
  function updateChartTau(id,tau) {
    const marker=$(id).querySelector('.r3-tau-marker');if(!marker)return;
    marker.style.transform=`translateX(${chartX(tau)}px)`;marker.querySelector('text').textContent='τ '+num(tau,3);
    const svg=$(id).querySelector('svg');svg.setAttribute('aria-label',svg.getAttribute('aria-label').replace(/Current tau .*/,`Current tau ${num(tau,3)}.`));
  }
  function feedbackSchedule() {clearTimeout(state.fbTimer);if(state.fbPlaying)state.fbTimer=setTimeout(()=>{moveRound(1);feedbackSchedule();},Number($('fb-speed').value));}
  function moveRound(delta) {const s=scenario();if(!s?.rounds?.length)return;state.round=Math.max(0,Math.min(s.rounds.length,state.round+delta));if(state.round===s.rounds.length)pauseFeedback();renderRound();}
  function renderRound() {
    const s=scenario(),rounds=s?.rounds||[];
    $('fb-prev').disabled=state.round===0;$('fb-next').disabled=!rounds.length||state.round===rounds.length;$('fb-play').disabled=!rounds.length||state.round===rounds.length;$('fb-restart').disabled=!rounds.length;
    $('fb-counter').textContent=`Round ${state.round} / ${rounds.length}`;
    if(!rounds.length){$('round').innerHTML='<p class="notice">No saved rounds for this scenario. The live tab remains available.</p>';return;}
    const r=rounds[Math.max(0,state.round-1)],initial=state.round===0,tau=initial?r.tau_from:r.tau_to;
    const guard=s.guardrails||state.replay.guardrails,max=guard.tau.max_step;
    updateChartTau('sim-chart',tau);
    const low=Math.max(guard.tau.min,r.tau_from-max),high=Math.min(guard.tau.max,r.tau_from+max);
    $('round').innerHTML=`<div class="r3-tau-round"><p class="eyebrow">P13 / ${initial?'STARTING POINT':'ROUND '+esc(r.round)}</p><h3>τ ${num(r.tau_from,3)} ${initial?'':'→ '+num(r.tau_to,3)}</h3><div class="r3-clamp" role="img" aria-label="This round may move at most ${max}; allowed interval ${num(low,2)} to ${num(high,2)}"><span style="left:${(low-.05)/.9*100}%;width:${(high-low)/.9*100}%"></span><i class="from" style="left:${(r.tau_from-.05)/.9*100}%"></i><i class="to" style="left:${(tau-.05)/.9*100}%"></i></div><p class="tiny muted">Clamp: ±${num(max,2)} per round · allowed ${num(low,2)}–${num(high,2)}</p><p>${initial?'Press Next to reveal the first bounded update.':esc(r.tau_why)}</p>${initial?'':`<p class="tiny muted">Precision at updated tau: ${pct(r.precision_at_tau)}. The lower bound, rather than this point estimate, governs the proposal.</p>`}</div><div class="r3-shift-round"><p class="eyebrow">P7 / APPLIED-WORK CORRECTION</p><h3>shift ${signed(r.shift_from)} ${initial?'':'→ '+signed(r.shift_to)}</h3><div class="r3-shift-dial" role="img" aria-label="Shift ${initial?r.shift_from:r.shift_to}; allowed ${guard.shift.min} to ${guard.shift.max}">${Array.from({length:guard.shift.max-guard.shift.min+1},(_,i)=>i+guard.shift.min).map(n=>`<span class="${n===(initial?r.shift_from:r.shift_to)?'active':''}">${signed(n)}</span>`).join('')}</div><p>${initial?'Only misses outside the accepted band can move shift.':esc(r.shift_why)}</p></div>`;
    // Transition from the previous values, also when stepping backwards or restarting.
    const to=$('round').querySelector('.r3-clamp .to');if(!motion.matches&&to&&!initial){to.style.left=((r.tau_from-.05)/.9*100)+'%';requestAnimationFrame(()=>requestAnimationFrame(()=>{if(to.isConnected)to.style.left=((r.tau_to-.05)/.9*100)+'%';}));}
  }
  function chooseScenario() {
    pauseFeedback();state.round=0;const s=scenario();
    $('scenario-meta').textContent=s?`${s.n} labels · ${s.labels} · simulated, not live`:'Saved scenario unavailable';
    drawChart('sim-chart',s?.curve||[],s?.rounds?.[0]?.tau_from||.75,s?.target??state.replay?.target??.95);renderRound();
    const simulations=state.replay?.simulated||{};const ending=key=>{const rounds=simulations[key]?.rounds||[];return rounds.length?signed(rounds[rounds.length-1].shift_to):'unavailable';};
    $('comparison').innerHTML=`<strong>Same engine, opposite shift conclusions.</strong> Self-reports can reward flattering levels; ability audits can reveal over-levelling. That is why audits outrank self-reports.<br><span class="tiny">Recorded final shift · said: ${esc(ending('said_'+$('start').value))} · ability: ${esc(ending('ability_'+$('start').value))}. Compare both label sets using the selector above.</span>`;
  }
  function renderLive(data) {
    const live=data.live,cur=live.current,dry=live.dry_run;
    $('live-content').innerHTML=`<div class="r3-live-numbers"><article><p class="eyebrow">CURRENT τ</p><strong>${num(cur.tau,3)}</strong><p>Baseline ${num(cur.baseline.tau,3)}</p></article><article><p class="eyebrow">CURRENT SHIFT</p><strong>${signed(cur.shift)}</strong><p>Baseline ${signed(cur.baseline.shift)}</p></article></div><div class="notice"><strong>Live dry run · ${dry.labels} labels · no update applied</strong><p>P13 τ ${num(dry.tau.from,3)} → ${num(dry.tau.to,3)}<br>${esc(dry.tau.why)}</p><p>P7 shift ${signed(dry.shift.from)} → ${signed(dry.shift.to)}<br>${esc(dry.shift.why)}</p><small>Snapshot ${esc(dry.at)} · precision at current tau ${pct(dry.precision_at_current_tau)}</small></div><h3>Applied history</h3>${cur.history?.length?`<ol class="r3-history">${[...cur.history].reverse().map(row=>`<li><strong>${esc(row.at)} · ${esc(row.labels)} labels</strong><p>τ ${num(row.tau?.from,3)} → ${num(row.tau?.to,3)} · ${esc(row.tau?.why)}<br>shift ${signed(row.shift?.from)} → ${signed(row.shift?.to)} · ${esc(row.shift?.why)}</p></li>`).join('')}</ol>`:'<p class="muted">No applied updates yet. The offline baseline is still the reference.</p>'}`;
    drawChart('live-chart',live.curve,cur.tau,data.target);
  }
  async function loadFeedback() {
    try {
      const data=await get('replay');state.replay=data;$('feedback-status').textContent='Simulation is precomputed. Live shows a read-only snapshot from the same feedback code.';
      $('human-only').innerHTML=Object.entries(data.human_only).map(([key,value])=>`<dt>${esc(key)}</dt><dd>${esc(value)}</dd>`).join('');
      $('guardrails').innerHTML=Object.entries(data.guardrails).map(([key,values])=>`<article><h4>${esc(key)}</h4><dl>${Object.entries(values).map(([k,v])=>`<dt>${esc(k.replaceAll('_',' '))}</dt><dd>${esc(v)}</dd>`).join('')}</dl></article>`).join('');
      chooseScenario();renderLive(data);
    }catch(error){$('feedback-status').textContent=error.message;}
  }
  function tab(name,focus=false) {
    pauseFeedback();state.tab=name;['sim','live'].forEach(key=>{const active=key===name;$(key).hidden=!active;$(key+'-tab').setAttribute('aria-selected',String(active));$(key+'-tab').tabIndex=active?0:-1;});if(focus)$(name+'-tab').focus();
  }
  ['sim','live'].forEach(name=>{$(name+'-tab').onclick=()=>tab(name);$(name+'-tab').onkeydown=event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();tab(event.key==='Home'?'sim':event.key==='End'?'live':state.tab==='sim'?'live':'sim',true);}};});
  $('labels').onchange=chooseScenario;$('start').onchange=chooseScenario;
  $('fb-prev').onclick=()=>{pauseFeedback();moveRound(-1);};$('fb-next').onclick=()=>{pauseFeedback();moveRound(1);};$('fb-restart').onclick=()=>{pauseFeedback();state.round=0;renderRound();};
  $('fb-play').onclick=()=>{if(state.fbPlaying)pauseFeedback();else{pause();state.fbPlaying=true;$('fb-play').textContent='Pause';feedbackSchedule();}};
  $('fb-speed').onchange=feedbackSchedule;
  document.addEventListener('visibilitychange',()=>{if(document.hidden){pause();pauseFeedback();}});
  motion.addEventListener('change',()=>{pause();pauseFeedback();});
  window.addEventListener('pagehide',()=>{pause();pauseFeedback();state.controller?.abort();});
  loadParams();loadDecision(true);loadFeedback();
})();
