#!/usr/bin/env python3
"""Deterministic Batch G structure generator. Run from any directory.

All identifiers are allocated after collecting the batch's dated events, without
persona-based number ranges. Unlisted events remain in the private event ledger.
Existing bundles are read only to avoid identifier collisions, never modified.
"""
import calendar
import importlib.util
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from content import PEOPLE, CVS, WORK, TICKETS, REVIEWS
from documents import DOCS
from requests import REQUESTS

R = random.Random(70110342)
ASOF = date(2026, 10, 31)
SPRINT_EPOCH = date(2020, 1, 6)
HOLIDAYS = {date(y,m,d) for y in range(2020,2027) for m,d in [(1,26),(8,15),(10,2)]}
HOLIDAYS |= {date(2025,10,20),date(2025,10,21),date(2026,3,4)}
PRS, ISSUES, REV_TARGETS, LOG = [], [], [], []
PACK = {pid: dict(prs=[],issues=[],reviews=[],sources=[]) for pid in PEOPLE}
OUT = ROOT/'data'/'bundles'


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def d(s): return date.fromisoformat(s)

def sprint(day):
    number = (day-SPRINT_EPOCH).days//14
    start = SPRINT_EPOCH + timedelta(days=number*14)
    return {'name': f'Iteration {number+1}', 'start': str(start), 'end':str(start+timedelta(days=11))}

def workday(day):
    while day.weekday()>4 or day in HOLIDAYS:
        day += timedelta(days=1)
    return min(day, ASOF)

def weight(day):
    if day in HOLIDAYS: return 0
    if day.weekday()>4: return .055
    phase = (day-SPRINT_EPOCH).days%14
    # Second-week completion rush, a quieter start to the next sprint.
    return (2.3 if 8<=phase<=11 else .85) * (1.12 if day.weekday()==3 else 1)

def choose_day(lo, hi):
    days = [lo+timedelta(days=i) for i in range((hi-lo).days+1)]
    weights=[weight(x) for x in days]
    assert sum(weights)>0, (lo,hi)
    return R.choices(days, weights, k=1)[0]

def months(start):
    y,m = start.year,start.month
    while (y,m)<=(2026,10):
        lo=max(start,date(y,m,1)); hi=min(ASOF,date(y,m,calendar.monthrange(y,m)[1]))
        yield lo,hi
        m+=1
        if m==13:y,m=y+1,1

def file_counts(ext):
    return {x:(1 if x in ['Dockerfile','.md'] else R.choices([1,2,3,4,6],[40,28,18,10,4])[0]) for x in ext}

def add_source(pid, kind, path, sid=None, **meta):
    p=PEOPLE[pid]
    sid=sid or f'{kind}_{p["eid"]}'
    PACK[pid]['sources'].append(dict(source_id=sid,source_type=kind,path=path,**meta))
    return sid

def spread(items, count):
    """Stratified representative slots, with uneven gaps rather than fixed dates."""
    items=sorted(items,key=lambda e:e.get('created',e.get('date')))
    assert len(items)>=count,(len(items),count)
    indices=[]
    for i in range(count):
        low=math.floor(i*len(items)/count); high=math.floor((i+1)*len(items)/count)-1
        indices.append(R.randint(low,max(low,high)))
    return [items[i] for i in indices]

# Build the full monthly ledger first. Counts are later reduced from these events.
for pid,p in PEOPLE.items():
    for lo,hi in months(d(p['hire'])):
        fraction=(hi-lo).days/30+.033
        seasonal=.68 if lo.month in [5,10,12] else 1.08 if lo.month in [3,6,9] else 1
        leave=R.uniform(.72,1.23)
        rates=p['rates']
        if pid=='P042': rates=(8,5,6) if lo.year<2023 else (R.choice([0,0,1]),7,1)
        counts=[max(0,round(rate*fraction*seasonal*leave*R.triangular(.55,1.5,1))) for rate in rates]
        for _ in range(counts[0]):
            created=choose_day(lo,hi)
            end=workday(created+timedelta(days=R.choice([1,1,2,2,3,4,6])))
            repo=p['repo']
            if pid=='P034' and R.random()<.36:repo='analytics-dbt'
            if pid=='P038' and R.random()<.22:repo='infra-live'
            ext=list(p['ext'])
            if pid=='P034':ext=['.sql','.yml'] if repo=='analytics-dbt' else ['.py','.yaml']
            if pid=='P042' and created.year<2023:ext=['.go']
            if R.random()<.35:ext=R.sample(ext,1)
            state=R.choices(['merged','closed','open'],[94,5,1 if created>=date(2026,10,1) else 0])[0]
            event=dict(pid=pid, repo=f'kestrel-cloud/{repo}',created=str(created), state=state,files_ext=file_counts(ext), listed=False)
            event['merged' if state=='merged' else 'closed' if state=='closed' else 'updated']=str(end)
            PRS.append(event)
        for _ in range(counts[2]):
            created=choose_day(lo,hi)
            resolved=workday(created+timedelta(days=R.randint(2,13)))
            ISSUES.append(dict(pid=pid,project=p['project_key'],created=str(created),resolved=str(resolved),listed=False,reporter_is_self=(pid=='P042' or R.random()<.17),resolved_by_self=pid!='P042'))
        # Reviews target other people's PRs in the same repo; allocate those PR IDs too.
        for _ in range(counts[1]):
            when=choose_day(lo,hi)
            target=dict(repo='kestrel-cloud/'+p['repo'],created=str(max(d(p['hire']),when-timedelta(days=R.randint(0,4)))),pid=None,listed=False)
            REV_TARGETS.append(target)
            PACK[pid]['reviews'].append(dict(date=str(when),_target=target,listed=False))

# Assign prose to representative work records. These are all genuine authored work.
for pid,rows in WORK.items():
    candidates=[e for e in PRS if e['pid']==pid and e['state']=='merged']
    if pid=='P042':
        selected=spread([e for e in candidates if e['created']<'2023-01-01'],10)+spread([e for e in candidates if e['created']>='2023-01-01'],6)
    else:selected=spread(candidates,len(rows))
    for i,(event,row) in enumerate(zip(selected,rows)):
        title,summary,body,extensions=row
        repo=event['repo']
        if pid=='P034':
            repo='kestrel-cloud/analytics-dbt' if ('dbt' in body or extensions.startswith('.sql')) else 'kestrel-cloud/data-platform'
        if pid=='P038':repo='kestrel-cloud/infra-live' if '.sh' in extensions else 'kestrel-cloud/platform-k8s'
        event.update(repo=repo,listed=True,title=title,body=body,files_ext=file_counts(extensions.split(',')))
        issue_created=workday(max(d(PEOPLE[pid]['hire']),d(event['created'])-timedelta(days=R.randint(2,12))))
        issue_created=min(issue_created,d(event['created']))
        issue=dict(pid=pid,project=PEOPLE[pid]['project_key'],created=str(issue_created),resolved=str(workday(d(event['merged'])+timedelta(days=R.randint(0,3)))),listed=True,summary=summary,description_excerpt=REQUESTS[pid][i],outcome=body.rsplit('. ',1)[-1],reporter_is_self=False,resolved_by_self=True,_pr=event)
        if pid=='P042':issue.update(reporter_is_self=True,resolved_by_self=False)
        ISSUES.append(issue);event['_issue']=issue
        PACK[pid]['prs'].append(event);PACK[pid]['issues'].append(issue)
    if pid!='P042':
        # A current open housekeeping change, kept out of capability calibration.
        created=choose_day(date(2026,10,23),date(2026,10,29))
        repo=PEOPLE[pid]['repo']
        e=dict(pid=pid,repo='kestrel-cloud/'+repo,created=str(created),updated=str(workday(created+timedelta(days=1))),state='open',listed=True,title={'P033':'chore: test image refresh','P034':'remove old bank D fixtures','P038':'docs: local validation setup','P039':'split slow browser job','P040':'chore: update preview script'}[pid],body='Opened for the next iteration. Waiting for maintainer review.',files_ext=file_counts(['.md'] if pid=='P038' else ['.yml']),_issue=None)
        PRS.append(e);PACK[pid]['prs'].append(e)
        if pid in ['P033','P040']:
            closed=sorted([x for x in PRS if x['pid']==pid and x['state']=='closed' and x['created']>='2025-01-01'],key=lambda x:x['created'])[-1]
            closed.update(listed=True,title='chore: switch test cache key' if pid=='P033' else 'try separate preview cache',body='Closing this; the current runner setup already keys the cache on the lockfile.',_issue=None)
            PACK[pid]['prs'].append(closed)

# Non-code work: select dates first, then write content into the slots.
for pid,rows in TICKETS.items():
    candidates=[e for e in ISSUES if e['pid']==pid and not e['listed']]
    if pid=='P042':candidates=[e for e in candidates if e['created']>='2025-01-01']
    if pid=='P037':
        selected=spread([e for e in candidates if '2024-08-01'<=e['created']<='2025-03-01'],5)+spread([e for e in candidates if e['created']>='2026-01-01'],1)
    else:selected=spread(candidates,len(rows))
    for e,(summary,desc,outcome,project) in zip(selected,rows):
        if pid=='P035':outcome=re.sub(r'(release )20[0-9]{2}\.[0-9]{2}',lambda m:m.group(1)+e['resolved'][:7].replace('-','.'),outcome)
        if pid=='P036' and e['resolved']<'2024-06-10':outcome=outcome.replace('Sravya','Leena')
        e.update(listed=True,project=project,summary=summary,description_excerpt=desc,outcome=outcome)
        if pid=='P042':
            e.update(reporter_is_self=True,resolved_by_self=False)
            if 'two sprints' in outcome:e['resolved']=str(workday(d(e['created'])+timedelta(days=R.randint(28,34))))
        PACK[pid]['issues'].append(e)

# Employer-controlled review/validation records for published procedures.
for pid,project,lo,hi,title,desc,comment in [
 ('P036','RECON','2026-07-14','2026-07-21','Partner replay guide review','Review SALES-218 before the next pilot.','Priyanka reviewed Aman replay procedure, corrected the key reuse after timeout and checked the revised request sequence against the smoke collection. Draft accepted for partner handoff.'),
 ('P041','PM','2026-06-16','2026-06-23','Close extract procedure review','Review ENG-2891 extraction steps.','Meenal reviewed Ritika technical procedure. Parked and posted documents were mixed in the first draft; separate lists and company-code check added. Revised steps checked on the close extract and accepted.'),
 ('P042','RECON','2026-09-24','2026-09-30','Handover guide validation','Use ENG-2936 in the staging handover exercise.','Deepak and Aditi completed the handover tasks using Vivek guide version 3. Aditi missed the flag path; version 4 added it and she repeated the step successfully. Team accepted the guide link for on-call handover.')]:
    when=choose_day(d(lo),d(hi))
    created=workday(when-timedelta(days=R.randint(2,5)))
    e=dict(pid=pid,project=project,created=str(created),resolved=str(when),listed=True,reporter_is_self=pid=='P042',resolved_by_self=pid!='P042',summary=title,description_excerpt=desc,outcome=comment)
    ISSUES.append(e);PACK[pid]['issues'].append(e)

# Older A-F data already contains contradictory chronology. Avoid its numeric keys;
# enforce strict chronology for the whole newly generated world, including unlisted work.
old_prs=defaultdict(set);old_issues=defaultdict(set)
for folder in sorted(OUT.glob('P*')):
    if folder.name in PEOPLE:continue
    for fn,key,registry in [('github.json','pull_requests',old_prs),('jira.json','issues',old_issues)]:
        path=folder/fn
        if not path.exists():continue
        for row in json.loads(path.read_text()).get(key,[]):
            if fn=='github.json':registry[row['repo']].add(row['number'])
            elif '-' in row.get('key',''):
                project,num=row['key'].rsplit('-',1)
                if num.isdigit():registry[project].add(int(num))
    path=folder/'github.json'
    if path.exists():
        for row in json.loads(path.read_text()).get('reviews_given',[]):
            if row.get('repo') and row.get('pr_number'):old_prs[row['repo']].add(row['pr_number'])

counters={}
for repo in sorted({e['repo'] for e in PRS+REV_TARGETS}):
    events=sorted([e for e in PRS+REV_TARGETS if e['repo']==repo],key=lambda e:e['created'])
    number=R.randint(2000,2280)
    for e in events:
        # gaps represent the rest of a 1,800-person organisation
        number+=R.choices([1,2,3,5],[55,27,14,4])[0]
        while number in old_prs[repo]:number+=1
        assert 2000<=number<=9000,(repo,number)
        e['number']=number
    counters[repo]=number
for project in sorted({e['project'] for e in ISSUES}):
    number=R.randint(11000,12800)
    for e in sorted([e for e in ISSUES if e['project']==project],key=lambda e:e['created']):
        number+=R.randint(1,9)
        while number in old_issues[project]:number+=1
        e['key']=f'{project}-{number}'

# Render exports. Derive totals from the same ledger that holds all listed records.
for pid,p in PEOPLE.items():
    folder=OUT/pid;folder.mkdir(parents=True,exist_ok=True)
    login=p['name'].lower().replace(' ','-')+'-kc'
    email=p['name'].lower().replace(' ','.')+'@kestrelcloud.com'
    hcm=dict(employee_id=p['eid'],legacy_ids=[],worker_type='employee',legal_name=p['name'],preferred_name=p['name'].split()[0],emails=[dict(email=email,**{'from':p['hire'][:7],'to':None})],gender=p['gender'],location=p['city'],country='IN',department=p['department'],manager_employee_id=p['manager'],hire_date=p['hire'],rehire_dates=[],job_history=[dict(title=p['title'],grade=p['grade'],**{'from':p['hire'][:7],'to':None})],project_allocations=[dict(project=p['project'],role=p['title'],**{'from':p['hire'][:7],'to':None},allocation_pct=100)],messaging_consent=dict(notice_given=True,opted_out=False,eu_opt_in=None),education=[dict(institution=p['institution'],degree=p['degree'],field=p['field'],year=p['year'])],exported='2026-10-31')
    if pid=='P042':
        hcm['job_history']=[dict(title='Software Engineer',grade='P3',**{'from':'2020-11','to':'2022-12'}),dict(title='Engineering Manager',grade='M1',**{'from':'2023-01','to':None})]
    if pid=='P033':
        hcm['job_history']=[dict(title='Software Development Engineer I',grade='P2',**{'from':'2022-11','to':'2024-10'}),dict(title=p['title'],grade=p['grade'],**{'from':'2024-11','to':None})]
    if pid=='P037':
        hcm['project_allocations']=[
            dict(project='Pune workplace operations',role='Facilities Engineer',allocation_pct=100,**{'from':'2023-02','to':'2024-07'}),
            dict(project='Pune office fit-out',role='Facilities Engineer',allocation_pct=100,**{'from':'2024-08','to':'2025-03'}),
            dict(project='Pune facilities operations',role='Facilities Engineer',allocation_pct=100,**{'from':'2025-04','to':None})]
    selfskills={'P033':[('Java',3),('Spring Boot',3),('SQL',3)],'P034':[('Python',3),('SQL',3),('Airflow',3)],'P035':[('Figma',3),('UX Research',3)],'P039':[('Selenium',3),('API testing',3)],'P041':[('Excel financial modelling',3),('SAP FI',3),('SQL',2)]}
    if pid in selfskills:hcm['self_declared_skills']=[dict(skill_text=s,self_level=l,declared_on='2026-07') for s,l in selfskills[pid]]
    dump(folder/'hcm.json',hcm);add_source(pid,'hcm','hcm.json',f'hcm_{p["eid"]}')
    for i,(received,cv) in enumerate(CVS[pid],1):
        path=f'cv_v{i}.md';(folder/path).write_text(cv)
        meta=dict(lineage_key='cv-'+pid,received=received)
        if pid=='P035':meta['lineage_key']='self-tanvi-design'
        if pid in ['P038','P040']:meta.update(original_format='scanned_pdf' if pid=='P038' else 'two_column_pdf',extraction_quality='low' if pid=='P038' else 'mixed')
        add_source(pid,'cv',path,f'cv_{login}_{i}',**meta)
    if pid in WORK:
        pr_out=[]
        for i,e in enumerate(sorted(PACK[pid]['prs'],key=lambda x:x['created'])):
            issue=e.get('_issue');title=e['title']
            if issue and R.random()<.33:title=issue['key']+' '+title
            row=dict(repo=e['repo'],number=e['number'],title=title,body=e['body'],state=e['state'],created=e['created'],merged=e.get('merged'),merged_by='other' if e['state']=='merged' else None,author_type='human',files_ext=e['files_ext'],additions=R.randint(10,370),deletions=R.randint(0,105),co_authors=[],review_comments_received=R.choice([1,1,2,3,4,6]),labels=R.choice([[],['bug'],['tests'],['maintenance']]),commits=R.randint(1,5))
            # Diff sizes follow the change's scope rather than a persona-wide range.
            text=e['title'].lower()
            if '.md' in e['files_ext'] and len(e['files_ext'])==1:
                row.update(additions=R.randint(9,63),deletions=R.randint(1,24))
            elif 'Dockerfile' in e['files_ext']:
                row.update(additions=R.randint(4,19),deletions=R.randint(2,12))
            elif any(x in text for x in ['remove unused','remove legacy','rename']):
                row.update(additions=R.randint(0,14),deletions=R.randint(24,167))
            elif any(x in text for x in ['test','checks','fixture','assertions']):
                row.update(additions=R.randint(29,185),deletions=R.randint(0,44))
            elif pid=='P038' or any(x in text for x in ['pipeline','artifact','report retention','image refresh']):
                row.update(additions=R.randint(7,48),deletions=R.randint(1,19))
            else:
                row.update(additions=R.randint(13,144),deletions=R.randint(2,70))
            row['labels']=['tests'] if text.startswith('test') else ['documentation'] if '.md' in e['files_ext'] else ['bug'] if text.startswith('fix:') else []
            if issue:row['issue_keys']=[issue['key']]
            if e['state']=='open':row.update(draft=pid=='P034',updated=e['updated'],review_comments_received=0)
            if e['state']=='closed':row['closed']=e['closed']
            feedback={
                'add quota for sandbox-a':'Memory unit should be Mi, not MB; please attach the quota output.',
                'validate team labels':'Please reject whitespace-only owner as well, add that input to the test.',
                'docs: kube context setup':'Use the actual training context name and print current-context after switching.',
                'sandbox service restart notes':'The unit is config-helper.service. Capture status and journal output after the restart.',
                'run manifest check on PR':'Pin kubeconform before running this; latest does not work on this runner.',
                'fix: missing label value':'Strip first, then check. Keep the whitespace input as a regression test.',
                'quota for sandbox-b':'Check the over-limit pod is rejected too, not just that the quota exists.',
                'correct staging probe path':'Readiness and liveness route differ in the training app. Use /ready for readiness.',
                'check service user in setup':'Quote the username and check the command output as that user.',
                'docs: log directory permissions':'777 is too open here. Use the service group and verify write access.',
                'add fixture for yaml null':'Catch the empty document before dereferencing it, not every parse error.',
                'test sandbox namespace limits':'Create a pod without requests and inspect the default values.',
                'fix pipeline artifact path':'The tool writes under reports/validation. Please test a failed run as well.',
                'return nonzero for missing owner':'Assert the exit code in the script test, not just stderr text.',
                'add staging service check example':'Keep a short output example so the next starter can check the unit name.',
            }
            if pid=='P038' and e['state']=='merged':
                row['review_comments']=[dict(user='nilesh-kamat-kc',date=e['merged'],body=feedback[e['title']],path=next(iter(e['files_ext'])))]
            guided={
                'Bump runtime base to 21':('nilesh-kamat-kc','Keep tzdata in the runtime stage as well, then check /actuator/health in the image.'),
                'healthcheck port in image':('nilesh-kamat-kc','Use management port 9091 for this check, the app port does not expose health.'),
                'fixture api: reject negative totals':('deepak-basu-kc','Check null before comparing amount; null should return 400 too.'),
                'handle missing bank id in fixture API':('deepak-basu-kc','Do the null check before isEmpty. Add separate tests for both.'),
                'upload test report on failure':('deepak-basu-kc','Use always() on upload, otherwise the failed run has no report.'),
                'retry only the browser setup step':('deepak-basu-kc','Put retry around setup only. An assertion failure must stay failed.'),
                'fix test report retention':('deepak-basu-kc','Use the QA signoff retention value and check it on the next nightly.'),
                'run typecheck before preview':('deepak-basu-kc','Run this from the console workspace, root does not have that command.'),
                'artifact name for preview build':('deepak-basu-kc','Include the PR ref so two preview runs do not overwrite each other.'),
            }
            if e['title'] in guided:
                user,feedback_text=guided[e['title']]
                row['review_comments']=[dict(user=user,date=e['merged'],body=feedback_text,path=next(iter(e['files_ext'])))]
            pr_out.append(row)
        selected_reviews=spread(PACK[pid]['reviews'],len(REVIEWS[pid]))
        reviews=[]
        for rv,(comment,reply) in zip(selected_reviews,REVIEWS[pid]):
            rv['listed']=True;t=rv['_target'];rv['sample_comment']=comment
            row=dict(repo=t['repo'],pr_number=t['number'],date=rv['date'],state='CHANGES_REQUESTED',comment_count=R.randint(1,4),sample_comment=comment,author_reply_excerpt=reply,thread_resolved=True)
            if pid in ['P034','P038']:row['second_reviewer_comment']='Confirmed, please apply that change.' if pid=='P038' else 'Agreed with Sravya on the key and reconciliation check.'
            reviews.append(row)
        monthly=[]
        for lo,hi in months(d(p['hire'])):
            mon=str(lo)[:7]
            merged=[e for e in PRS if e['pid']==pid and e['state']=='merged' and e['merged'][:7]==mon]
            ext=Counter()
            for e in merged:ext.update(e['files_ext'])
            monthly.append(dict(month=mon,merged_prs=len(merged),reviews=sum(rv['date'][:7]==mon for rv in PACK[pid]['reviews']),by_ext=dict(sorted(ext.items()))))
        dump(folder/'github.json',dict(login=login,account_type='enterprise',linked_employee_id=p['eid'],pull_requests=pr_out,reviews_given=reviews,monthly_activity=monthly,exported='2026-10-31'))
        add_source(pid,'github','github.json',f'gh_{login}')
    issues=[]
    for e in sorted(PACK[pid]['issues'],key=lambda x:x['created']):
        sp=sprint(d(e['created']))
        row=dict(key=e['key'],type='Task' if pid in TICKETS or pid=='P042' else R.choice(['Story','Bug','Task']),summary=e['summary'],description_excerpt=e['description_excerpt'],component=p['project'],priority=R.choice(['Medium','Medium','High','Low']),status='Done',resolution='Done',reporter_is_self=e['reporter_is_self'],assignee_history=[dict(assignee='other' if pid=='P042' else 'self',**{'from':e['created']})],resolved_by_self=e['resolved_by_self'],created=e['created'],resolved=e['resolved'],story_points=R.choice([1,2,3,3,5]),labels=[],sprint=sp,comments=[dict(author=p['name'] if pid!='P042' else 'Deepak Basu',date=e['resolved'],body=e['outcome'])])
        if e.get('_pr'):row['issue_links']=[dict(type='implements',url=f'https://github.com/{e["_pr"]["repo"]}/pull/{e["_pr"]["number"]}')]
        if pid=='P041':
            # The ticket is an employer-controlled acceptance record. Workbooks themselves
            # are not attached to this bundle; exact CV savings numbers stay unverified.
            row['comments'][0]['author']='Meenal Shah' if any(s in e['outcome'] for s in ['FCST','FI','agreed']) else 'Sravya Dutta'
        if pid=='P035':row['comments'][0]['author']='Rhea Thomas'
        if pid=='P036':row['comments'][0]['author']=('Leena Varma' if e['resolved']<'2024-06-10' else 'Sravya Dutta') if 'SQL' in e['outcome'] else 'Priyanka Rao'
        issues.append(row)
    monthly=[]
    for lo,hi in months(d(p['hire'])):
        mon=str(lo)[:7];events=[e for e in ISSUES if e['pid']==pid]
        monthly.append(dict(month=mon,resolved_as_assignee=sum(e['resolved'][:7]==mon and e['resolved_by_self'] for e in events),reported=sum(e['created'][:7]==mon and e['reporter_is_self'] for e in events)))
    dump(folder/'jira.json',dict(linked_employee_id=p['eid'],issues=issues,monthly_activity=monthly,exported='2026-10-31'))
    add_source(pid,'jira','jira.json',f'jira_{p["eid"]}')
    for key,space,title,created,body in DOCS.get(pid,[]):
        path=f'docs/{key}.md';(folder/'docs').mkdir(exist_ok=True)
        last={'P035':'2026-09-03','P036':'2026-07-14','P041':'2026-06-16'}.get(pid,'2026-06-02' if key=='bank-isolation' else '2026-09-24')
        docid={'review-flow':'PM-1841','partner-replay':'SALES-218','fi-close':'ENG-2891','bank-isolation':'ARCH-407','oncall-guide':'ENG-2936'}[key]
        contributors=[] if pid=='P035' else ['Priyanka Rao'] if pid=='P036' else ['Meenal Shah'] if pid=='P041' else ['Deepak Basu','Aditi Jain']
        front=f'---\ndoc_id: {docid}\nspace: {space}\ntitle: "{title}"\ncreated: {created}\nlast_edited: {last}\nauthor: {p["name"]}\ncontributors: {json.dumps(contributors)}\npage_views_90d: {R.randint(12,86)}\n---\n\n'
        (folder/path).write_text(front+body+'\n')
        add_source(pid,'authored_doc',path,f'doc_{docid}',**({'lineage_key':'self-tanvi-design'} if pid=='P035' else {}))

# Source mixes vary by role. No compulsory LMS/certificate row for everybody.
for pid,entries in {
 'P034':[('ETL in Python and SQL','LinkedIn Learning','2025-02-21',244,88),('internal: Settlement model review','Kestrel Learn','2026-06-18',95,85)],
 'P035':[('Google UX Design Professional Certificate','Coursera','2023-08-30',7020,92)],
 'P038':[('internal: Platform starter lab','Kestrel Learn','2026-04-10',210,76),('Git Essential Training','LinkedIn Learning','2026-04-22',87,85)],
 'P042':[('internal: First time manager workshop','Kestrel Learn','2023-02-23',360,86),('internal: Feedback conversations','Kestrel Learn','2025-07-10',140,90),('internal: Hiring panel calibration','Kestrel Learn','2026-08-06',120,88)]
}.items():
    dump(OUT/pid/'lms.json',dict(linked_employee_id=PEOPLE[pid]['eid'],completions=[dict(course_title=t,provider=pr,completed=dt,time_spent_minutes=mins,quiz_score_pct=score,assigned_by='manager') for t,pr,dt,mins,score in entries]))
    add_source(pid,'lms','lms.json')

# This is a faithfully entered self-report, not a verified issuer record.
dump(OUT/'P039'/'certs.json',dict(linked_employee_id=PEOPLE['P039']['eid'],certificates=[dict(name='Certified Tester Foundation Level (CTFL) v4.0',issuer='Udemy',issued='2024-06',evidence_form='self_reported',verification_status='unverifiable')],recorded='2026-10-08'))
add_source('P039','certs','certs.json')

# CRM records are complete opportunities over the last two years, not sample prose
# claiming someone owned all revenue. SE overlay credit is ordinary CRM accounting.
pid='P036';opps=[]
notes=[
 ('Retail','Closed Won','Buyer needs two merchant IDs in one daily view. Aman mapped the file flow and agreed T+1 acceptance with finance. Objection on replay time resolved with a scheduled recovery demo. Technical acceptance signed.'),
 ('Logistics','Closed Won','Aman ran discovery with controller and integration lead. Proposed file-first pilot rather than webhook-only after checking bank delays. Buyer accepted the new plan; pilot complete.'),
 ('Healthcare','Closed Lost','Aman mapped the payment channels and proposed daily batch recon. Buyer requires on-prem deployment; product gap recorded at decision review. Evaluation closed.'),
 ('Manufacturing','Closed Won','Aman owned implementation plan with source totals, daily activation check and signoff owner. Partner completed five daily reconciliations, customer accepted production activation.'),
 ('Retail','Closed Won','Changed solution after buyer objected to manual reversal entries. Aman demonstrated the reversal workflow, recorded acceptance conditions and closed technical actions before AE commercial handoff.'),
 ('Financial Services','Closed Won','Aman coordinated onboarding: token scopes, opening balance, replay and daily acceptance. Controller signed the activation sheet after source totals agreed for five days.'),
]
for lo,hi in months(date(2024,11,1)):
    for _ in range(R.choice([1,2,2,3,3])):
        close=choose_day(lo,hi);industry,stage,note=R.choice(notes)
        chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        oid='006'+''.join(R.choice(chars) for _ in range(15))
        created=max(d(PEOPLE[pid]['hire']),close-timedelta(days=R.randint(32,108)))
        detail=R.choice([f'Bank cutoff {R.choice([15,16,17])}:{R.choice([0,15,30]):02d}; buyer accepted the next-morning replay window.',f'Acceptance batch has {R.randint(180,970)} payments and {R.randint(2,18)} reversals; finance asked for net and gross totals.',f'Partner has {R.randint(2,9)} merchant IDs; agreed a separate acceptance total for each.',f'Pilot owner wants {R.randint(3,7)} consecutive daily runs before activation.'])
        note=note+' '+detail+' Technical checkpoint '+str(close)+'.'
        opps.append(dict(opp_id=oid,account_industry=industry,stage=stage,amount_band=R.choice(['5L-15L INR','15L-40L INR','40L-90L INR']),role='overlay_se',credit_split_pct=20,created=str(created),close_date=str(close),products=['Payments Recon'],notes_excerpt=note,stage_history=[dict(date=str(created),stage='Discovery',changed_by='aman.bhatia@kestrelcloud.com'),dict(date=str(workday(created+timedelta(days=14))),stage='Technical Evaluation',changed_by='aman.bhatia@kestrelcloud.com'),dict(date=str(close),stage=stage,changed_by='priyanka.rao@kestrelcloud.com')],forecast_review=dict(date=str(close),reviewer='Priyanka Rao',result='Stage, close date and next action checked against technical acceptance; no change needed.')))
dump(OUT/pid/'salesforce.json',dict(linked_employee_id=PEOPLE[pid]['eid'],user='aman.bhatia@kestrelcloud.com',exported='2026-10-31',export_scope=dict(closed_from='2024-11-01',closed_through='2026-10-31'),opportunities=sorted(opps,key=lambda o:o['created']),monthly_activity=[dict(month=str(lo)[:7],opps_created=sum(o['created'][:7]==str(lo)[:7] for o in opps),opps_closed=sum(o['close_date'][:7]==str(lo)[:7] for o in opps)) for lo,hi in months(min(d(o['created']) for o in opps))]))
add_source(pid,'salesforce','salesforce.json')

for pid in PEOPLE:
    dump(OUT/pid/'manifest.json',dict(person_ref=pid,customer='kestrel-cloud',as_of='2026-10-31',sources=PACK[pid]['sources']))

# Retain the underlying structure for independent aggregate/chronology checks.
ledger_prs=[{k:v for k,v in e.items() if not k.startswith('_')} for e in PRS]
ledger_issues=[{k:v for k,v in e.items() if not k.startswith('_')} for e in ISSUES]
ledger_reviews=[dict(pid=pid,date=rv['date'],repo=rv['_target']['repo'],pr_number=rv['_target']['number'],listed=rv['listed']) for pid in PEOPLE for rv in PACK[pid]['reviews']]
dump(HERE/'event_ledger.json',dict(seed=70110342,as_of=str(ASOF),holidays=sorted(map(str,HOLIDAYS)),pull_requests=ledger_prs,issues=ledger_issues,reviews=ledger_reviews,review_targets=REV_TARGETS))
dump(HERE/'registry.json',dict(pr_final_counters=counters,numbering_scope='All Batch G listed/unlisted PRs and review targets, globally ordered per repository; A-F keys reserved against collisions.',sources={pid:PACK[pid]['sources'] for pid in PEOPLE}))

# Import labels only after the bundle files are complete.
from truth import write_truth
write_truth(ROOT, PEOPLE)
print(f'Generated {len(PEOPLE)} bundles, {len(PRS)} PR ledger events, {len(ISSUES)} Jira events, {len(ledger_reviews)} reviews.')
