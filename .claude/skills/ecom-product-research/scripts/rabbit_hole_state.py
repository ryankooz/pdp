#!/usr/bin/env python3
"""Durable state CLI for hourly rabbit-hole product research."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, sqlite3
from pathlib import Path

# Data root: ECOM_WIKI_ROOT, else the current working directory (run from the repo root).
ROOT = Path(os.environ.get("ECOM_WIKI_ROOT") or Path.cwd()) / "intel" / "product-research"
DB = ROOT / "_state" / "research.sqlite"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS keywords (
 id INTEGER PRIMARY KEY,
 literal_text TEXT NOT NULL,
 normalized_key TEXT NOT NULL UNIQUE,
 source_type TEXT NOT NULL,
 source_quote TEXT NOT NULL,
 source_url TEXT NOT NULL,
 shape_class TEXT NOT NULL,
 country TEXT NOT NULL DEFAULT 'US',
 status TEXT NOT NULL DEFAULT 'queued',
 priority INTEGER NOT NULL DEFAULT 0,
 attempts INTEGER NOT NULL DEFAULT 0,
 candidate_yield INTEGER NOT NULL DEFAULT 0,
 validated_yield INTEGER NOT NULL DEFAULT 0,
 not_before TEXT,
 last_searched_at TEXT,
 terminal_reason TEXT,
 parent_keyword_id INTEGER,
 branch_root_id INTEGER,
 branch_depth INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidates (
 id INTEGER PRIMARY KEY,
 canonical_host TEXT NOT NULL UNIQUE,
 product_name TEXT NOT NULL,
 landing_path TEXT,
 page_names_json TEXT NOT NULL DEFAULT '[]',
 discovery_keyword_id INTEGER REFERENCES keywords(id),
 status TEXT NOT NULL DEFAULT 'discovered',
 stage TEXT NOT NULL DEFAULT 'free_screen',
 gate_a TEXT NOT NULL DEFAULT 'unknown',
 gate_b TEXT NOT NULL DEFAULT 'unknown',
 gate_c TEXT NOT NULL DEFAULT 'unknown',
 gate_d TEXT NOT NULL DEFAULT 'unknown',
 gate_e TEXT NOT NULL DEFAULT 'unknown',
 disqualifier TEXT,
 next_action TEXT,
 evidence_json TEXT NOT NULL DEFAULT '[]',
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
 id INTEGER PRIMARY KEY,
 started_at TEXT NOT NULL,
 finished_at TEXT,
 stage TEXT NOT NULL,
 subject TEXT,
 outcome TEXT,
 summary TEXT,
 evidence_json TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS observations (
 id INTEGER PRIMARY KEY,
 candidate_id INTEGER REFERENCES candidates(id),
 keyword_id INTEGER REFERENCES keywords(id),
 predicate TEXT NOT NULL,
 value_json TEXT NOT NULL,
 epistemic TEXT NOT NULL CHECK(epistemic IN ('observed','derived','inferred','unknown','unavailable')),
 source_url TEXT,
 observed_at TEXT NOT NULL,
 evidence_hash TEXT NOT NULL
);
"""

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def norm(s): return " ".join(s.casefold().split())
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.executescript(SCHEMA)
    cols={r['name'] for r in c.execute('PRAGMA table_info(keywords)')}
    for name,definition in [('parent_keyword_id','INTEGER'),('branch_root_id','INTEGER'),('branch_depth','INTEGER NOT NULL DEFAULT 0')]:
      if name not in cols: c.execute(f'ALTER TABLE keywords ADD COLUMN {name} {definition}')
    c.execute('CREATE INDEX IF NOT EXISTS idx_keywords_parent ON keywords(parent_keyword_id)')
    c.commit(); return c

def add_keyword(c, text, source_type, quote, url, shape, priority=0, parent_id=None):
    t=now()
    root_id=None; depth=0
    if parent_id:
      parent=c.execute('SELECT id,branch_root_id,branch_depth FROM keywords WHERE id=?',(parent_id,)).fetchone()
      if parent: root_id=parent['branch_root_id'] or parent['id']; depth=(parent['branch_depth'] or 0)+1
    c.execute("""INSERT INTO keywords(literal_text,normalized_key,source_type,source_quote,source_url,shape_class,priority,parent_keyword_id,branch_root_id,branch_depth,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(normalized_key) DO NOTHING""",
      (text,norm(text),source_type,quote,url,shape,priority,parent_id,root_id,depth,t,t))

def seed(c):
    # Owner rule: scheduled research never seeds generic promotional terms.
    return

def cmd_init(_):
    with connect() as c: seed(c)
    print(json.dumps({"db":str(DB),"initialized":True}))
def cmd_add(a):
    with connect() as c:
      add_keyword(c,a.text,a.source_type,a.quote,a.url,a.shape,a.priority,a.parent_id)
      row=c.execute("SELECT * FROM keywords WHERE normalized_key=?",(norm(a.text),)).fetchone()
    print(json.dumps(dict(row),ensure_ascii=False))
def cmd_next(_):
    with connect() as c:
      row=c.execute("""SELECT * FROM keywords WHERE status='queued' AND (not_before IS NULL OR not_before<=?)
        ORDER BY priority DESC, created_at ASC LIMIT 1""",(now(),)).fetchone()
    print(json.dumps(dict(row) if row else None,ensure_ascii=False))
def cmd_next_many(a):
    limit=max(1,min(5,a.limit))
    with connect() as c:
      rows=c.execute("""SELECT * FROM keywords WHERE status='queued' AND (not_before IS NULL OR not_before<=?)
        ORDER BY priority DESC, created_at ASC LIMIT ?""",(now(),limit)).fetchall()
    print(json.dumps([dict(r) for r in rows],ensure_ascii=False))
def cmd_mark(a):
    allowed={'queued','leased','spent','productive','dead','cooldown','struck'}
    if a.status not in allowed: raise SystemExit(f"invalid status: {a.status}")
    with connect() as c:
      searched_at=now() if a.attempt else None
      c.execute("""UPDATE keywords SET status=?, attempts=attempts+?, candidate_yield=candidate_yield+?,
        validated_yield=validated_yield+?, terminal_reason=COALESCE(?,terminal_reason),
        last_searched_at=COALESCE(?,last_searched_at), updated_at=? WHERE id=?""",
        (a.status,1 if a.attempt else 0,a.candidates,a.validated,a.reason,searched_at,now(),a.id))
      row=c.execute("SELECT * FROM keywords WHERE id=?",(a.id,)).fetchone()
    print(json.dumps(dict(row) if row else None,ensure_ascii=False))
def cmd_run(a):
    with connect() as c:
      t=now(); cur=c.execute("INSERT INTO runs(started_at,finished_at,stage,subject,outcome,summary) VALUES(?,?,?,?,?,?)",
        (t,t,a.stage,a.subject,a.outcome,a.summary)); rid=cur.lastrowid
    print(json.dumps({"run_id":rid,"logged":True}))
def cmd_status(_):
    with connect() as c:
      kw={r['status']:r['n'] for r in c.execute("SELECT status,count(*) n FROM keywords GROUP BY status")}
      cand={r['status']:r['n'] for r in c.execute("SELECT status,count(*) n FROM candidates GROUP BY status")}
      recent=[dict(r) for r in c.execute("SELECT id,finished_at,stage,subject,outcome,summary FROM runs ORDER BY id DESC LIMIT 5")]
    print(json.dumps({"database":str(DB),"keywords":kw,"candidates":cand,"recent_runs":recent},ensure_ascii=False,indent=2))

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
    x=s.add_parser('init'); x.set_defaults(fn=cmd_init)
    x=s.add_parser('add-keyword'); x.add_argument('text'); x.add_argument('--source-type',required=True); x.add_argument('--quote',required=True); x.add_argument('--url',required=True); x.add_argument('--shape',required=True); x.add_argument('--priority',type=int,default=0); x.add_argument('--parent-id',type=int); x.set_defaults(fn=cmd_add)
    x=s.add_parser('next-keyword'); x.set_defaults(fn=cmd_next)
    x=s.add_parser('next-keywords'); x.add_argument('--limit',type=int,default=5); x.set_defaults(fn=cmd_next_many)
    x=s.add_parser('mark-keyword'); x.add_argument('id',type=int); x.add_argument('status'); x.add_argument('--attempt',action='store_true'); x.add_argument('--candidates',type=int,default=0); x.add_argument('--validated',type=int,default=0); x.add_argument('--reason'); x.set_defaults(fn=cmd_mark)
    x=s.add_parser('log-run'); x.add_argument('--stage',required=True); x.add_argument('--subject'); x.add_argument('--outcome',required=True); x.add_argument('--summary',required=True); x.set_defaults(fn=cmd_run)
    x=s.add_parser('status'); x.set_defaults(fn=cmd_status)
    a=p.parse_args(); a.fn(a)
if __name__=='__main__': main()
