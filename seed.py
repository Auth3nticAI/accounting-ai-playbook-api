"""Seed the database with realistic accounting pain points and AI solutions.

Run after `docker compose up -d db` and at least one app start (so tables exist).
Idempotent: clears existing rows before inserting.
"""

from database import Base, SessionLocal, engine
from models import AISolution, PainPoint


PAIN_POINTS = [
    {
        "title": "Manual AP invoice coding",
        "description": (
            "Bookkeepers re-key vendor invoices into the GL and tag each one with "
            "the right account, class, and dimensions. High-volume firms eat 20+ "
            "hours a week here, and errors flow downstream into close and tax."
        ),
        "category": "AP/AR",
        "firm_size_fit": "mid",
        "severity": "high",
        "solutions": [
            {
                "title": "Claude + Textract invoice extraction",
                "description": (
                    "Pipeline that OCRs vendor PDFs, then asks Claude to extract "
                    "line items and propose GL codes based on the firm's chart of "
                    "accounts and prior bookings. Surfaces low-confidence rows for "
                    "human review instead of silently misclassifying."
                ),
                "tech_stack": "Claude API, AWS Textract, FastAPI, Postgres",
                "maturity": "prototype",
                "setup_days": 14,
                "pricing_model": "monthly",
                "estimated_price_usd": 1500,
            },
            {
                "title": "n8n workflow with Claude classification",
                "description": (
                    "No-code n8n flow that pulls invoices from email/Drive, runs "
                    "Claude classification, and posts directly into QuickBooks "
                    "Online. Faster to ship than a custom pipeline for firms "
                    "already on the Intuit stack."
                ),
                "tech_stack": "n8n, Claude API, QuickBooks Online API",
                "maturity": "proven",
                "setup_days": 5,
                "pricing_model": "fixed",
                "estimated_price_usd": 4500,
            },
        ],
    },
    {
        "title": "Month-end close bottleneck",
        "description": (
            "Close drags 8-12 business days because reconciliations, accruals, "
            "and intercompany eliminations are tracked across spreadsheets and "
            "email. Nobody knows the true status until the controller chases it."
        ),
        "category": "Close cycle",
        "firm_size_fit": "mid",
        "severity": "high",
        "solutions": [
            {
                "title": "Claude-powered close checklist agent",
                "description": (
                    "Conversational agent that owns the close checklist: nudges "
                    "preparers, flags unreconciled accounts, drafts journal "
                    "entry narratives, and rolls up close status for the "
                    "controller in real time."
                ),
                "tech_stack": "Claude API, FastAPI, Postgres, Slack integration",
                "maturity": "concept",
                "setup_days": 30,
                "pricing_model": "monthly",
                "estimated_price_usd": 2500,
            }
        ],
    },
    {
        "title": "Audit prep document collection",
        "description": (
            "Pulling together PBC (provided by client) lists eats client face "
            "time and creates audit friction. Requests are restated, files come "
            "in late or in the wrong format, and the audit team waits."
        ),
        "category": "Audit",
        "firm_size_fit": "all",
        "severity": "high",
        "solutions": [
            {
                "title": "RAG over prior-year working papers",
                "description": (
                    "Indexes the firm's prior audit binders so this year's "
                    "preparer can ask 'how did we handle inventory reserves "
                    "last year?' and get a cited answer with the workpaper "
                    "reference."
                ),
                "tech_stack": "Claude API, Postgres + pgvector, FastAPI",
                "maturity": "prototype",
                "setup_days": 21,
                "pricing_model": "fixed",
                "estimated_price_usd": 8000,
            },
            {
                "title": "PBC request agent",
                "description": (
                    "Auto-generates the PBC list from prior engagement, sends "
                    "templated requests to client contacts, files responses to "
                    "the right binder section, and chases missing items."
                ),
                "tech_stack": "Claude API, SharePoint/Drive API, Postmark",
                "maturity": "concept",
                "setup_days": 18,
                "pricing_model": "monthly",
                "estimated_price_usd": 1200,
            },
        ],
    },
    {
        "title": "Tax research time sink",
        "description": (
            "Preparers spend hours searching IRC, regs, and prior-year memos for "
            "answers to client-specific questions. Knowledge stays in senior "
            "partners' heads, so juniors re-do the same research yearly."
        ),
        "category": "Tax",
        "firm_size_fit": "small",
        "severity": "medium",
        "solutions": [
            {
                "title": "Tax research assistant with firm memo corpus",
                "description": (
                    "Claude-backed chat that knows the firm's accumulated tax "
                    "memos and surfaces the relevant memo + citation in seconds. "
                    "Drafts a starter response so the preparer reviews and edits "
                    "rather than starts from scratch."
                ),
                "tech_stack": "Claude API, pgvector, FastAPI",
                "maturity": "prototype",
                "setup_days": 12,
                "pricing_model": "monthly",
                "estimated_price_usd": 900,
            }
        ],
    },
    {
        "title": "Client onboarding paperwork",
        "description": (
            "Engagement letters, W-9s, prior-year returns, bank statements - "
            "new clients drag through 2-3 weeks of back-and-forth before the "
            "firm has what it needs to start work."
        ),
        "category": "Client management",
        "firm_size_fit": "small",
        "severity": "medium",
        "solutions": [
            {
                "title": "Onboarding agent with checklist + secure intake",
                "description": (
                    "Customizes an onboarding packet per service line, collects "
                    "documents through a secure client portal, parses uploads, "
                    "and pre-fills the firm's client setup record."
                ),
                "tech_stack": "Claude API, Next.js, Postgres, S3",
                "maturity": "concept",
                "setup_days": 25,
                "pricing_model": "fixed",
                "estimated_price_usd": 6500,
            }
        ],
    },
    {
        "title": "Bank reconciliation matching",
        "description": (
            "Even with bank feeds, ~10% of transactions need manual matching - "
            "duplicate payments, partial payments, and uncategorized deposits "
            "that bank rules can't catch."
        ),
        "category": "AP/AR",
        "firm_size_fit": "small",
        "severity": "medium",
        "solutions": [
            {
                "title": "LLM-based reconciliation suggester",
                "description": (
                    "Reviews unmatched transactions and proposes likely matches "
                    "(or splits) with reasoning. Bookkeeper accepts/rejects "
                    "instead of hunting through the register."
                ),
                "tech_stack": "Claude API, Plaid, Postgres",
                "maturity": "prototype",
                "setup_days": 10,
                "pricing_model": "monthly",
                "estimated_price_usd": 600,
            }
        ],
    },
    {
        "title": "Advisory deliverable production",
        "description": (
            "CAS (Client Advisory Services) teams are billed for insight, but "
            "preparing monthly business reviews is mostly mechanical: pulling "
            "numbers, building variance commentary, formatting slides."
        ),
        "category": "Advisory",
        "firm_size_fit": "mid",
        "severity": "medium",
        "solutions": [
            {
                "title": "Monthly business review generator",
                "description": (
                    "Pulls the client's KPIs from QBO/Xero, computes variances "
                    "vs. plan, and drafts plain-English commentary on what "
                    "moved and why. Partner reviews and polishes instead of "
                    "writing from scratch."
                ),
                "tech_stack": "Claude API, QuickBooks API, Pandas, FastAPI",
                "maturity": "prototype",
                "setup_days": 20,
                "pricing_model": "per-seat",
                "estimated_price_usd": 150,
            }
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clear existing data (CASCADE on solutions handles the FK side)
        db.query(AISolution).delete()
        db.query(PainPoint).delete()
        db.commit()

        for pp_data in PAIN_POINTS:
            solutions = pp_data.pop("solutions", [])
            pp = PainPoint(**pp_data)
            db.add(pp)
            db.flush()  # need pp.id before we attach solutions

            for sol_data in solutions:
                db.add(AISolution(pain_point_id=pp.id, **sol_data))

        db.commit()
        pain_count = db.query(PainPoint).count()
        solution_count = db.query(AISolution).count()
        print(f"Seeded {pain_count} pain points and {solution_count} AI solutions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
