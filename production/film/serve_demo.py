"""Isolated real application with clearly fictional film fixtures; no provider stubs."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'services' / 'backend'))
TMP = ROOT / 'tmp'
TMP.mkdir(exist_ok=True)
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///' + (TMP / 'film.db').as_posix()
os.environ['LOCAL_STORAGE_DIR'] = (TMP / 'storage').as_posix()
os.environ['FRONTEND_ORIGIN'] = 'http://localhost:3002'
os.environ['ALLOWED_ORIGINS'] = '["http://localhost:3002","http://127.0.0.1:3002"]'

from app.main import app  # noqa: E402
from app.community import service as community  # noqa: E402
from app.merchants import service as merchants  # noqa: E402

community.COMMUNITY_POSTS_STORE[:] = [{
    'id': 'film-demo-01',
    'title': 'A missing phone, and the records I kept',
    'story': 'FICTIONAL DEMONSTRATION. I paid in two parts for a phone from Demo Nila Store. The delivery date passed. I kept both receipts and the seller messages, then prepared a clear written request. This is a sample experience, not a reported outcome.',
    'category': 'E-Commerce', 'merchant_name': 'Demo Nila Store (fictional)',
    'disputed_amount_bdt': 5500, 'author_name': 'Maya — fictional demo',
    'me_too_count': 0, 'created_at': '2026-11-05T09:00:00+06:00',
    'has_converted_case': False, 'is_pinned': False, 'is_hidden': False,
    'report_count': 0,
    'comments': [{'id':'film-comment-01','author_name':'Demo participant',
                 'content':'FICTIONAL DEMONSTRATION. Keep private receipts in your case. Share only the experience you are comfortable making public.',
                 'created_at':'2026-11-05T09:10:00+06:00','is_legal_volunteer':False}],
}]
# Keep merchant lookup honest: no invented risk probabilities or real-business allegations.
for name, value in vars(merchants).copy().items():
    if name.isupper() and isinstance(value, (list, dict)) and name != '__builtins__':
        value.clear()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8002)
