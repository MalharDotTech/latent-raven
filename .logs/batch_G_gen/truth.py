"""Hidden ability, observable oracles, and private realism annotations for G.
No truth field is consumed while generating any employee prose.
"""
import json
from pathlib import Path

# skill, hidden level, observed level (None = hold), explanation, missing source
LABELS = {
'P033': [
 ('java',3,3,'JVM retention and pool exhaustion repairs establish independent service diagnosis.',None),
 ('spring_boot',3,3,'Transaction failure recovery and deployment readiness are operational service maintenance.',None),
 ('sql',3,3,'Production query repair includes a concrete execution-plan comparison.',None),
 ('api_testing',3,3,'Maintained failure-path suite finds contract and retry defects before release.',None),
 ('code_review',3,3,'Review threads identify correctness faults and show the corresponding author changes.',None),
 ('docker',2,2,'Container build changes have a named helper and recorded runtime verification.',None),
 ('kafka',1,None,'Basic retained knowledge is real; the exported material contains only a tool-list claim.','A scored Kafka exercise or reviewed broker/client work.'),
 ('kubernetes',1,None,'Some personal-lab knowledge, without an observable current application record.','Current assessed lab or a reviewed deployment change.'),
 ('aws',1,None,'Recognises core services privately; no cloud operation is established by this export.','Current cloud exercise or deployment/change record.'),
 ('python',1,None,'University familiarity persists but the listed workplace changes do not establish it.','A recent Python coding exercise or reviewed script.'),
],
'P034': [
 ('python',3,3,'Parser ownership includes runtime fault reproduction and production reruns.',None),
 ('sql',3,3,'Deployed transformations have balance reconciliation and query-profile evidence.',None),
 ('airflow',3,3,'Failed backfills are repaired with explicit manifest and run-history checks.',None),
 ('snowflake',3,3,'Warehouse binding and workload split changes are supported by operational query history.',None),
 ('dbt',2,2,'Models and source checks are built with analytics-lead corrections.',None),
 ('data_modeling',2,2,'Key grain and cardinality are corrected by the model reviewer before reconciliation.',None),
 ('code_review',2,2,'A second reviewer confirms the bounded data-key and count-check comments.',None),
],
'P035': [
 ('figma',3,3,'Employer acceptance records connect repeated component versions to released screens.',None),
 ('ux_research',3,None,'She can independently plan and synthesise research; the only detailed study here is self-authored.','Employer-controlled research plan, session notes and linked design decision.'),
 ('product_discovery',3,None,'The underlying discovery work changed the flow, but its experiment results are only self-report.','Product decision log and an independently reviewed experiment summary.'),
 ('stakeholder_management',2,None,'Can maintain a guided action log; no reviewed responsibility plan is exported.','Reviewed stakeholder action log with responsibility corrections.'),
 ('technical_writing',2,None,'Has written guided handoff procedures; portfolio narrative is not the required reviewed procedure.','Reviewed handoff or setup procedure and its revision comments.'),
 ('agile_delivery',2,None,'Assists iteration activities but this export has no facilitated activity or action tracking.','Iteration plan with facilitator review and completed follow-up actions.'),
],
'P036': [
 ('solution_selling',2,2,'Opportunity decisions show independent buyer-need mapping and handling of objections.',None),
 ('salesforce',2,2,'Dated stage changes and reconciled forecast reviews show regular independent CRM maintenance.',None),
 ('customer_onboarding',2,2,'Activation criteria, completed daily reconciliations and customer acceptance establish independent onboarding.',None),
 ('api_testing',3,3,'Maintained integration checks cover failures and block defective release candidates.',None),
 ('sql',2,2,'Acceptance queries have reviewer corrections and reconciliation to supplied control totals.',None),
 ('java',2,None,'Past applied Java ability remains, but a prior-job paragraph cannot determine current retained competence.','Recent reviewed Java endpoint change or current practical work sample.'),
 ('spring_boot',2,None,'Previous guided connector development is real; no current Spring service artefact is exported.','A reviewed recent controller/integration-test change or practical assessment.'),
 ('stakeholder_management',3,3,'Customer cutoff and replay decisions have agreed owners and completed actions.',None),
 ('technical_writing',2,2,'Integration procedure has a named reviewer correction to the retry-key sequence.',None),
],
'P037': [],
'P038': [
 ('python',2,2,'Merged scripts and tests have concrete mentor corrections; this is guided application.',None),
 ('kubernetes',2,2,'Sandbox manifests and rollout checks are applied under mentor supervision.',None),
 ('linux',2,2,'Guided service commands have reviewed output and corrected unit/user choices.',None),
 ('cicd',2,2,'Reviewed validation and artifact steps have passing pipeline runs.',None),
 ('technical_writing',2,2,'Setup procedure drafts are corrected and checked with a buddy.',None),
 ('docker',1,None,'Has limited conceptual familiarity; watching a deployment does not show a scored lab or build work.','A scored Docker lab, or a reviewed image build and successful run.'),
 ('go',0,0,'The seminar title denotes attendance/presentation, not demonstrated programming competence.',None),
],
'P039': [
 ('selenium',3,3,'Ongoing suite maintenance includes flaky-wait repairs and repeat-run results.',None),
 ('java',2,2,'Guided Java fixture endpoints include controller tests and reviewer corrections.',None),
 ('api_testing',3,3,'Independent failure-contract suite catches duplicate posting and response faults before shipment.',None),
 ('sql',2,2,'Test queries are reviewed for join and date semantics then compared with control totals.',None),
 ('cicd',2,2,'Report and retry stages are added with build-engineer checks and passing runs.',None),
 ('code_review',3,3,'Substantive test reviews catch shared-data and swallowed-assertion defects before merge.',None),
],
'P040': [
 ('react',3,3,'Released screens and profiler-backed rendering fixes show independent feature ownership.',None),
 ('typescript',3,3,'Module boundary narrowing removes unsafe casts with regression coverage.',None),
 ('javascript',3,3,'Production async defects have request-ordering and cleanup fixes with tests.',None),
 ('api_testing',2,2,'UI/API failure checks are corrected by QA and have recorded results.',None),
 ('code_review',3,3,'Review comments catch stale requests, unsafe casts and timer leaks, followed by author repairs.',None),
 ('cicd',2,2,'Workflow additions are guided by the release engineer with successful artifact checks.',None),
],
'P041': [
 ('excel_modeling',3,3,'Employer acceptance identifies successive scenario-model versions and reconciled finance outputs.',None),
 ('sap',3,3,'FI workflow faults are traced and cleared with document/ledger reconciliation, scoped to FI.',None),
 ('sql',2,2,'Reviewed finance queries have explicit join corrections and checked totals.',None),
 ('data_modeling',2,None,'Can draft a finance data model with guidance, but extract queries do not demonstrate a reviewed schema.','Reviewed model diagram with corrected grain and key definitions.'),
 ('stakeholder_management',3,3,'Budget-owner tradeoffs lead to signed decisions and completed revised plans.',None),
 ('technical_writing',2,2,'FI extraction procedure receives specific controller corrections.',None),
],
'P042': [
 ('technical_leadership',3,3,'Technical tradeoffs, rollout risks and team follow-ups are visible in decisions and completed tickets.',None),
 ('code_review',3,3,'Independent failure-mode reviews lead to explicit code and test repairs.',None),
 ('agile_delivery',3,3,'Dependency removal and retrospective actions are tracked through completed iterations.',None),
 ('stakeholder_management',3,3,'Cross-team windows and acceptance owners are negotiated and delivered.',None),
 ('system_design',3,3,'Accepted service isolation/capacity decisions have failure tests and production validation.',None),
 ('technical_writing',3,3,'A versioned guide has named users completing handover tasks and a repeated corrected step.',None),
 ('go',2,None,'Retained ability is below his former independent operating level; old service work cannot pin today’s level.','Current practical Go reassessment or reviewed recent handler work.'),
],
}
SUMMARIES = {
'P033':('Ordinary billing SDE II, nearly four years at Kestrel. Six of ten listed skills have concrete workplace support; the four others are familiar concepts rather than recent delivery.','ordinary_backend_control'),
'P034':('Three-year data engineer with two applications prepared for different target roles in the same month. The earlier TCS job starts three months later in the analytics version; the underlying employment began in August 2023.','ordinary_data_engineer_tailored_cvs'),
'P035':('Pharmacy graduate who moved into product design, with two years at Kestrel and small concurrent freelance projects. Design system delivery is externally recorded, while research metrics are repeated in her own portfolio.','career_pivot_designer'),
'P036':('Solutions engineer with six years across connector development and pre-sales integration work. The expansive CV hides fairly normal independent SE work, and a small home-linen shop is co-run with Isha Sethi.','payments_solutions_engineer'),
'P037':('Civil-trained workplace engineer responsible for the Pune fit-out. The useful domain capabilities sit outside this customer taxonomy; everyday Office use must not force a mapping.','off_taxonomy_facilities'),
'P038':('Graduate trainee with seven months of supervised platform delivery. A short observational internship and college seminars occupy much of a scanned CV; actual applied work still meets the guided application lines.','trainee_with_extraction_damage'),
'P039':('Five-year QA engineer with normal independent Selenium and API suite ownership. A certification entry names the preparation provider as issuer, without any credential identifier; actual ability comes from her work.','ordinary_qa'),
'P040':('Frontend engineer with three years of production React and typed JavaScript work. Maintains the website for Mitti Cart alongside Aman Bhatia; CV column order is lost during extraction.','frontend_concurrent_business'),
'P041':('Four-year finance analyst with good routine model, FI and reviewed-query evidence. Exact savings and forecasting claims in the CV lack supporting measurement artefacts; those numbers are not needed for ordinary core-skill sends.','ordinary_fp_and_a'),
'P042':('Nine-year engineer now managing the recon team. Leadership and review work remain current, while practical Go independence has declined since the 2022 IC role and is not recoverable at a current level from this export.','ordinary_engineering_manager'),
}
OBS = {'P033':['RO-03'],'P034':['RO-01','RO-02'],'P035':['RO-05','RO-07','RO-09','RO-14','RO-15'],'P036':['RO-06','RO-08'],'P037':['RO-11','RO-12'],'P038':['RO-10','RO-13'],'P039':['RO-04'],'P040':['RO-05','RO-06','RO-13'],'P041':['RO-14'],'P042':['RO-16']}
# literal phrase -> file match, for a small exact evidence index in addition to source IDs.
KEYWORDS = {
'java':['JVM','Heap dump','Java controller','Java stack','fixture controller'],
'spring_boot':['Spring Boot','Spring transaction'],
'sql':['SQL','EXPLAIN','query'],
'api_testing':['API','RestAssured','smoke'],
'docker':['Docker','docker run'],
'selenium':['Selenium'], 'python':['Python'], 'airflow':['Airflow'],'snowflake':['Snowflake'],'dbt':['dbt'],
'data_modeling':['diagram','cardinality'], 'figma':['Figma'],
'kubernetes':['Kubernetes','manifest'], 'linux':['systemctl','service user'],
'cicd':['pipeline','Pipeline','GitHub Actions','workflow'],
'react':['React'], 'typescript':['TypeScript'], 'javascript':['JavaScript'],
'excel_modeling':['FCST_'], 'sap':['FI'], 'stakeholder_management':['agreed','secured','negotiated'],
'agile_delivery':['sprint','Retro','board'], 'system_design':['capacity','Capacity'],
 'technical_leadership':['guided','decision'], 'technical_writing':['setup','procedure','Draft','draft','Wrote'],
}

def representative(items):
    return items if len(items)<=4 else items[:1]+items[-3:]

def write_truth(root, people):
    tax=json.loads((root/'data/taxonomy/customer_taxonomy.json').read_text())
    skills={s['skill_id']:s for s in tax['skills']}
    for pid,p in people.items():
        folder=root/'data/bundles'/pid
        manifest=json.loads((folder/'manifest.json').read_text())
        sources={s['source_type']:s['source_id'] for s in manifest['sources']}
        cv_ids=[s['source_id'] for s in manifest['sources'] if s['source_type']=='cv']
        docs=[s for s in manifest['sources'] if s['source_type']=='authored_doc']
        gh=json.loads((folder/'github.json').read_text()) if (folder/'github.json').exists() else {}
        jira=json.loads((folder/'jira.json').read_text())
        rows=[]
        for sid,hidden,observed,why,missing in LABELS[pid]:
            k3=skills[sid]['family_id']=='sales_cs';top=3 if k3 else 4
            accept=[n for n in range(max(1,hidden-1),min(top,hidden+1)+1)] if hidden else []
            if k3:accept=[hidden]
            action='hold' if observed is None else 'not_extract' if observed==0 else 'send'
            refs=[];basis_ids=[]
            if action=='hold':
                basis_ids=cv_ids.copy();refs=[f'{x}:skills/experience' for x in cv_ids]
                if pid=='P035' and sid in ['ux_research','product_discovery']:
                    basis_ids += [x['source_id'] for x in docs];refs += [f'{x["source_id"]}:case-study' for x in docs]
                if pid=='P042' and sid=='go':
                    basis_ids.append(sources['github']);refs += [f'{sources["github"]}:#{pr["number"]}' for pr in gh['pull_requests'] if '.go' in pr['files_ext']][:3]
            elif action=='not_extract':
                basis_ids=cv_ids.copy();refs=[f'{cv_ids[0]}:PRO JECTS']
            else:
                if sid=='code_review':
                    basis_ids=[sources['github']]
                    refs=[f'{sources["github"]}:review#{rv["pr_number"]}' for rv in representative(gh['reviews_given'])]
                elif sid in ['solution_selling','salesforce','customer_onboarding']:
                    basis_ids=[sources['salesforce']]
                    crm=json.loads((folder/'salesforce.json').read_text())
                    refs=[f'{sources["salesforce"]}:{o["opp_id"]}' for o in crm['opportunities'][:3]]
                elif sid=='technical_writing' and docs:
                    # Relevant procedure, rather than an unrelated portfolio or architecture page.
                    doc=next((s for s in docs if 'oncall-guide' in s['path']),docs[0])
                    basis_ids=[doc['source_id'],sources['jira']];refs=[doc['source_id']+':review/validation']
                    peer=[t for t in jira['issues'] if any(w in t['summary'].lower() for w in ['guide review','procedure review','guide validation'])]
                    refs += [f'{sources["jira"]}:{t["key"]}' for t in peer]
                else:
                    needles=KEYWORDS.get(sid,[])
                    hits=[pr for pr in gh.get('pull_requests',[]) if pr['state']=='merged' and any(word in pr['body'] for word in needles)]
                    if hits:
                        basis_ids.append(sources['github']);refs += [f'{sources["github"]}:#{pr["number"]}' for pr in representative(hits)]
                    tickets=[t for t in jira['issues'] if any(word in (t['description_excerpt']+' '+str(t['comments'])) for word in needles)]
                    if tickets:
                        basis_ids.append(sources['jira']);refs += [f'{sources["jira"]}:{t["key"]}' for t in representative(tickets)]
                    if not basis_ids:raise ValueError((pid,sid,'no applied evidence references'))
            if pid=='P042' and sid in ['system_design','technical_leadership']:
                architecture=next(x for x in docs if 'bank-isolation' in x['path'])
                basis_ids.append(architecture['source_id']);refs.append(architecture['source_id']+':decision/production-validation')
            level=observed if action=='send' else None
            oracle_accept=[n for n in accept if n==level] if k3 else [n for n in accept if level is not None and abs(n-level)<=1]
            last='2026-10'
            if action=='hold':
                last={'P033':'2022-05','P035':'2026-08','P036':'2022-08','P038':'2025-08','P041':'2026-06','P042':'2022-12'}.get(pid,last)
            if action=='send':
                dates=[]
                for ref in refs:
                    if ':#' in ref:
                        number=int(ref.split(':#')[1]); dates += [pr['merged'][:7] for pr in gh.get('pull_requests',[]) if pr['number']==number and pr.get('merged')]
                    elif ':review#' in ref:
                        number=int(ref.split(':review#')[1]); dates += [rv['date'][:7] for rv in gh.get('reviews_given',[]) if rv['pr_number']==number]
                    elif ':' in ref and ref.split(':',1)[1].startswith(('BILL-','RECON-','DATA-','PLAT-','QA-','WEB-','PM-')):
                        key=ref.split(':',1)[1]; dates += [t['resolved'][:7] for t in jira['issues'] if t['key']==key]
                if dates:last=max(dates)
            if sid=='go' and pid=='P038':last='2025-03'
            row=dict(skill_id=sid,has_skill=bool(hidden),true_level=hidden,self_perceived_level=hidden,would_accept_levels=accept,oracle=dict(action=action,level=level,accept_levels=oracle_accept,basis='; '.join(dict.fromkeys(basis_ids)),missing_source=missing),last_used=last,evidence_refs=refs,why=why)
            if pid=='P035' and sid=='figma':row['self_perceived_level']=4
            rows.append(row)
        summary,archetype=SUMMARIES[pid]
        truth=dict(pid=pid,schema='truth-v2',summary=summary,archetype=archetype,batch='G',generator='codex gpt-6',skills=rows,decoys=[],traps=[],unmatched_skills=[],realism_observations=OBS[pid],answer_behavior=dict(reply_probability=.78,yes_to_everything=False,flattery_bias=0,notes='Answers about the stated skill, asks for context if the scope is unclear.'),messaging_allowed=True)
        def trap(fid,sid,plant,row='level_off',**extra):
            action=next(s['oracle']['action'] for s in rows if s['skill_id']==sid)
            truth['traps'].append(dict(fault_id=fid,s11_row=row,skill_id=sid,plant=plant,expected_engine_behavior=action,**extra))
        if pid=='P033':
            trap('F05','kafka','Four of ten list entries have no applied evidence. They are ordinary list inflation, without fabricated work bullets.','skill_not_really_held',affected_skill_ids=['kafka','kubernetes','aws','python'])
        elif pid=='P034':
            trap('F02','data_modeling','Two role-targeted CVs share lineage and disagree by three months on the prior job start. Model level rests on reviewed schema work.',observation_ids=['RO-01','RO-02'])
        elif pid=='P035':
            trap('F07','figma','Three named freelance engagements overlap regular employment; keep each engagement attached to its author.',observation_ids=['RO-05'])
            trap('F29','ux_research','Self-rating bars and the same-author portfolio repeat study metrics; neither supplies independent research acceptance.',observation_ids=['RO-09','RO-15'])
            truth['unmatched_skills']=['Visual design','Information architecture']
        elif pid=='P036':
            trap('F06','solution_selling','Responsibility prose closely mirrors SE hiring language. Deal decisions, rather than prose density, establish independent K3 work.',observation_ids=['RO-08'])
            trap('F07','solution_selling','Aman co-runs Mitti Cart concurrently with Isha; shared brand does not make their technical work interchangeable.','wrong_person',observation_ids=['RO-06'])
        elif pid=='P037':
            truth['unmatched_skills']=['AutoCAD','Site supervision','Vendor management','Quantity surveying','BOQ estimation','Snagging']
            truth['decoys']=[dict(skill_text='MS Office',mapped_skill_id=None,has_skill=True,why='Everyday office use is excluded by the customer list.',oracle=dict(action='not_extract',level=None,accept_levels=[],basis=cv_ids[0],missing_source=None))]
            truth['traps']=[dict(fault_id='F06',s11_row='wrong_mapping',skill_text='MS Office',plant='Traditional biodata and a generic productivity-tool entry accompany civil/workplace skills outside the taxonomy.',expected_engine_behavior='not_extract',observation_ids=['RO-11','RO-12'])]
        elif pid=='P038':
            trap('F06','go','A seminar is filed under projects in an OCR-damaged CV; it demonstrates no programming work.','wrong_mapping',observation_ids=['RO-10','RO-13'])
            trap('F25','docker','A short internship describes observation of image deployment; no current lab or image change is present.','skill_not_really_held')
        elif pid=='P039':
            trap('F25','selenium','The self-reported CTFL entry names Udemy and omits credential identifiers. Workplace suite evidence supplies the level; exam prerequisites do not.',observation_ids=['RO-04'])
        elif pid=='P040':
            trap('F07','react','Concurrent Mitti Cart role is shared with Aman; frontend and supplier duties have different authors.','wrong_person',observation_ids=['RO-05','RO-06'])
            trap('F06','typescript','CV extraction interleaves education and work columns; quote spans must follow extracted text.',observation_ids=['RO-13'])
        elif pid=='P041':
            truth['calibration_notes']='No false savings claim was planted. Specific CV numbers are unverified; normal finance acceptance records independently support the core levels.'
        elif pid=='P042':
            trap('F28','go','Last full implementation evidence ends in the former IC period. Declared current duties are reviews and delivery; current retained Go ability is unobserved.','skill_decay')
        (root/'data/truth'/f'{pid}.json').write_text(json.dumps(truth,indent=2,ensure_ascii=False)+'\n')
