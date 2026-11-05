#!/usr/bin/env python3
"""Batch G semantic/structural checks beyond the repository validator."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PIDS=[f'P{i:03d}' for i in range(33,43)]
L=json.loads((HERE/'event_ledger.json').read_text())
TAX=json.loads((ROOT/'data/taxonomy/customer_taxonomy.json').read_text())
SKILLS={s['skill_id']:s for s in TAX['skills']}
PROJECTS={'BILL','RECON','DATA','WEB','MOB','PLAT','QA','SEC','PM'}
errors=[]
checks=0

def check(ok,message):
    global checks
    checks+=1
    if not ok:errors.append(message)

def load(p):return json.loads(p.read_text())

def chronology(events,namespace,key):
    grouped=defaultdict(list)
    for e in events:grouped[e[namespace]].append(e)
    for ns,rows in grouped.items():
        rows=sorted(rows,key=lambda e:(e['created'],e[key]))
        seen=set(); prev=None
        for row in rows:
            n=int(row[key].rsplit('-',1)[-1]) if isinstance(row[key],str) else row[key]
            check(n not in seen,f'duplicate {ns} {n}');seen.add(n)
            if prev:check(row['created']>=prev[0] and n>prev[1],f'order {ns} {n}')
            prev=(row['created'],n)
            if namespace=='repo':check(2000<=n<=9000,f'PR range {ns} {n}')

chronology(L['pull_requests']+L['review_targets'],'repo','number')
chronology(L['issues'],'project','key')
pr_index={(e['repo'],e['number']):e for e in L['pull_requests']+L['review_targets']}
issue_index={e['key']:e for e in L['issues']}
for rv in L['reviews']:
    check(pr_index[(rv['repo'],rv['pr_number'])]['created']<=rv['date'],f'review before PR {rv}')
for e in L['pull_requests']:
    check(e['created'] not in L['holidays'],f'holiday PR {e["created"]}')
for e in L['issues']:
    check(e['project'] in PROJECTS,f'bad Jira project {e["project"]}')
    check(e['created']<=e['resolved']<='2026-10-31',f'ticket timeline {e["key"]}')

summary=[]
for pid in PIDS:
    b=ROOT/'data/bundles'/pid
    m=load(b/'manifest.json');h=load(b/'hcm.json');t=load(ROOT/'data/truth'/f'{pid}.json')
    sources={s['source_id']:s for s in m['sources']}
    check(t['schema']=='truth-v2',pid+' truth schema')
    check(m['as_of']=='2026-10-31',pid+' asof')
    check(all((b/s['path']).is_file() for s in sources.values()),pid+' source exists')
    check(len(sources)==len(m['sources']),pid+' duplicate source id')
    actual={str(p.relative_to(b)) for p in b.rglob('*') if p.is_file()}
    check(actual=={'manifest.json'}|{s['path'] for s in sources.values()},pid+' undeclared files')
    for s in t['skills']:
        sid=s['skill_id'];o=s['oracle'];k3=SKILLS[sid]['family_id']=='sales_cs';top=3 if k3 else 4
        check(isinstance(s['has_skill'],bool),pid+' has_skill bool')
        check(0<=s['true_level']<=top,pid+' true level '+sid)
        check(o['action'] in ['send','hold','not_extract','do_not_message'],pid+' oracle action')
        check(all(x in sources for x in o['basis'].split('; ')),pid+' basis source ids '+sid)
        for ref in s['evidence_refs']:
            check(ref.split(':',1)[0] in sources,pid+' ref source '+ref)
            if ':#' in ref:
                n=int(ref.split(':#')[1]);gh=load(b/'github.json')
                check(any(x['number']==n for x in gh['pull_requests']),pid+' PR ref resolves '+ref)
            if ':review#' in ref:
                n=int(ref.split(':review#')[1]);gh=load(b/'github.json')
                check(any(x['pr_number']==n for x in gh['reviews_given']),pid+' review ref resolves '+ref)
        if o['action']=='send':
            check(1<=o['level']<=top,pid+' send level '+sid)
            tolerance={o['level']} if k3 else set(range(max(1,o['level']-1),min(top,o['level']+1)+1))
            check(o['accept_levels']==sorted(tolerance & set(s['would_accept_levels'])),pid+' accept intersection '+sid)
            check(o['missing_source'] is None,pid+' send missing '+sid)
        if o['action']=='hold' and s['has_skill']:check(bool(o['missing_source']),pid+' invisible skill missing source '+sid)
    by_skill={s['skill_id']:s for s in t['skills']}
    for tr in t['traps']:
        check(re.fullmatch(r'F\d{2}',tr['fault_id']) is not None,pid+' fault id')
        if tr.get('skill_id'):check(tr['expected_engine_behavior']==by_skill[tr['skill_id']]['oracle']['action'],pid+' trap/oracle agree')
    check(all(x.lower() not in [v['name'].lower() for v in SKILLS.values()] for x in t['unmatched_skills']),pid+' unmatched is outside tax')
    for src in sources.values():
        if src['source_type'] in ['github','jira','salesforce','certs','lms']:
            check(load(b/src['path']).get('linked_employee_id')==h['employee_id'],pid+' stable key '+src['path'])
        if src['source_type']=='authored_doc':
            text=(b/src['path']).read_text();body=text.split('---',2)[2]
            check(150<=len(body.split())<=600,pid+' document word length '+src['path'])
    gh=load(b/'github.json') if (b/'github.json').exists() else None
    if gh:
        check(15<=len(gh['pull_requests'])<=40,pid+' PR sample size')
        totals={r['month']:r for r in gh['monthly_activity']}
        for month,row in totals.items():
            merged=[e for e in L['pull_requests'] if e['pid']==pid and e['state']=='merged' and e['merged'][:7]==month]
            exts=Counter()
            for e in merged:exts.update(e['files_ext'])
            check(row['merged_prs']==len(merged),pid+' merged ledger total '+month)
            check(row['by_ext']==dict(exts),pid+' extension ledger total '+month)
            check(row['reviews']==sum(e['pid']==pid and e['date'][:7]==month for e in L['reviews']),pid+' review ledger total '+month)
        for pr in gh['pull_requests']:
            for key in pr.get('issue_keys',[]):
                check(issue_index[key]['created']<=pr['created'],pid+' ticket before PR')
                check(pr.get('merged') is None or pr['merged']<=issue_index[key]['resolved'],pid+' resolved after merge')
        # All the unlisted files have role-appropriate extensions too.
        if pid=='P042':
            check(all(not r['by_ext'].get('.go') for r in gh['monthly_activity'] if r['month']>='2023-02'),pid+' current Go edits contradict decay')
            check(all('.go' not in e['files_ext'] for e in L['pull_requests'] if e['pid']==pid and e['created']>='2023-01-01'),pid+' authored Go after IC role')
    j=load(b/'jira.json')
    for row in j['monthly_activity']:
        month=row['month'];items=[e for e in L['issues'] if e['pid']==pid]
        check(row['resolved_as_assignee']==sum(e['resolved'][:7]==month and e['resolved_by_self'] for e in items),pid+' Jira resolved ledger '+month)
        check(row['reported']==sum(e['created'][:7]==month and e['reporter_is_self'] for e in items),pid+' Jira reporter ledger '+month)
    for issue in j['issues']:
        for text in [c['body'] for c in issue['comments']]:
            for rel in re.findall(r'release (20\d{2})\.(\d{2})',text):
                check('-'.join(rel)<=issue['resolved'][:7],pid+' release claimed before release '+issue['key'])
            if 'Sravya' in text:check(issue['resolved']>='2024-06-10',pid+' reviewer before hire')
    counts=Counter(s['oracle']['action'] for s in t['skills'])
    if pid in ['P033','P039','P041','P042']:check(counts['send']>len(t['skills'])/2,pid+' ordinary sends majority')
    summary.append(dict(pid=pid,name=h['legal_name'],skills=len(t['skills']),oracle=dict(counts),prs=len(gh['pull_requests']) if gh else 0,tickets=len(j['issues'])))

check(not load(ROOT/'data/truth/P037.json')['skills'],'P037 no forced taxonomy mapping')
check(len(load(ROOT/'data/truth/P037.json')['unmatched_skills'])==6,'P037 unmatched skills')
m=load(ROOT/'data/bundles/P034/manifest.json')
check(len({s['lineage_key'] for s in m['sources'] if s['source_type']=='cv'})==1,'P034 lineage')
for pid in ['P036','P040']:
    cv=(ROOT/'data/bundles'/pid/'cv_v1.md').read_text()
    check('Mitti Cart' in cv,'shared business '+pid)
cv=(ROOT/'data/bundles/P038/cv_v1.md').read_text()
check('know l' not in cv and '\ufffd' in cv and 'devansh-\nsahu' in cv,'P038 damaged extraction')
weekends=sum(date.fromisoformat(e['created']).weekday()>4 for e in L['pull_requests'])
check(0<weekends/len(L['pull_requests'])<.05,'weekend volume reduced')
report=dict(checks=checks,errors=errors,summary=summary,listed_prs=sum(x['prs'] for x in summary),listed_issues=sum(x['tickets'] for x in summary),ledger_prs=len(L['pull_requests']),ledger_issues=len(L['issues']),ledger_reviews=len(L['reviews']),weekend_prs=weekends)
(HERE/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))
