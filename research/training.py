"""Local RP import and reproducible progression research. Python standard library only."""
import argparse, collections, hashlib, json, math, pathlib, sqlite3, zipfile

def load(path):
    path=pathlib.Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.endswith('.json') and not n.startswith('__MACOSX/')]
            if len(names)!=1: raise ValueError('Expected exactly one JSON file')
            if z.getinfo(names[0]).file_size>50_000_000: raise ValueError('Export too large')
            raw=z.read(names[0])
    else: raw=path.read_bytes()
    data=json.loads(raw)
    if not isinstance(data,list): raise ValueError('Expected a mesocycle list')
    seen=set()
    for m in data:
        if not isinstance(m,dict) or 'id' not in m or not isinstance(m.get('weeks'),list): raise ValueError('Invalid mesocycle')
        if m['id'] in seen: raise ValueError('Duplicate mesocycle ID')
        seen.add(m['id'])
        for w in m['weeks']:
            for d in w['days']:
                for e in d['exercises']:
                    for s in e['sets']:
                        if 'id' not in s or 'status' not in s: raise ValueError('Invalid set')
    return data,raw

def import_data(path,db):
    data,raw=load(path) # validate before opening transaction
    con=sqlite3.connect(db)
    con.executescript('CREATE TABLE IF NOT EXISTS imports(hash TEXT PRIMARY KEY,raw BLOB); CREATE TABLE IF NOT EXISTS mesos(id INTEGER PRIMARY KEY,payload TEXT NOT NULL);')
    with con:
        con.execute('INSERT OR IGNORE INTO imports VALUES (?,?)',(hashlib.sha256(raw).hexdigest(),raw))
        con.executemany('INSERT INTO mesos VALUES (?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',[(m['id'],json.dumps(m)) for m in data])
    con.close()
    return len(data)

def transitions(data):
    """Match same day slot/exercise/set position across adjacent non-deload weeks.
    Encoded RIR is deliberately not decoded until its format is verified.
    Last week excluded as a conservative deload assumption.
    """
    rows=[]
    for m in data:
        for wi in range(1,len(m['weeks'])-1):
            prev={d['position']:d for d in m['weeks'][wi-1]['days']}
            for d in m['weeks'][wi]['days']:
                p=prev.get(d['position'])
                if not p or p['status']!='complete': continue
                for e in d['exercises']:
                    matches=[x for x in p['exercises'] if x['exerciseId']==e['exerciseId']]
                    if len(matches)!=1: continue
                    pe=matches[0]
                    feedback=next((g for g in p['muscleGroups'] if g['muscleGroupId']==e['muscleGroupId']),{})
                    ps={s['position']:s for s in pe['sets']}
                    for s in e['sets']:
                        old=ps.get(s['position'])
                        if not old or old['status']!='complete': continue
                        if old.get('setType')!='regular' or s.get('setType')!='regular': continue
                        if old.get('unit')!=s.get('unit'): continue
                        weight=old.get('weight');target=s.get('weightTarget')
                        if not isinstance(weight,(int,float)) or weight<=0 or not isinstance(target,(int,float)) or target<=0: continue
                        rows.append(dict(meso=m['id'],created=m['createdAt'],week=wi+1,exercise=e['name'],previousWeight=weight,targetWeight=target,previousReps=old.get('reps'),targetReps=s.get('repsTarget'),pump=feedback.get('pump'),soreness=feedback.get('soreness'),workload=feedback.get('workload'),unit=s.get('unit')))
    return rows

def predict(weight,rate,step):
    return math.floor(weight*(1+rate)/step+0.5)*step

def analyze(data):
    rows=transitions(data)
    ids=[m['id'] for m in sorted(data,key=lambda m:m['createdAt'])]
    split=max(1,int(len(ids)*.7));train_ids=set(ids[:split])
    train=[r for r in rows if r['meso'] in train_ids];test=[r for r in rows if r['meso'] not in train_ids]
    def score(rs,rate,step):
        return sum(abs(predict(r['previousWeight'],rate,step)-r['targetWeight'])<1e-8 for r in rs)
    candidates=[(score(train,rate,step),rate,step) for rate in [0,.01,.02,.025,.03,.04,.05] for step in [1,2.5,5]]
    best=max(candidates)
    days=[d for m in data for w in m['weeks'] for d in w['days']]
    sets=[s for d in days for e in d['exercises'] for s in e['sets']]
    return {'blocks':len(data),'workoutStatuses':dict(collections.Counter(d['status'] for d in days)),'completedSets':sum(s['status']=='complete' for s in sets),'matchedTransitions':len(rows),'baseline':{'description':'Exploratory constant percentage + rounding; not RP algorithm or training advice','rate':best[1],'roundingStep':best[2],'trainMatches':best[0],'trainCount':len(train),'testMatches':score(test,best[1],best[2]),'testCount':len(test)},'limitations':['Observational final export, not an audit log; manual edits and target recalculations can confound results.','Feedback codes retained as raw values; -1 and null are not treated as ratings.','Last week excluded as presumed deload. RIR encoding remains unverified.','Historical algorithm versions differ. Fixed increment baseline ignores equipment and is a comparison only.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('export');p.add_argument('--db',default='training.sqlite');p.add_argument('--out',default='analysis.json');a=p.parse_args()
    data,_=load(a.export);import_data(a.export,a.db)
    report=analyze(data);pathlib.Path(a.out).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
