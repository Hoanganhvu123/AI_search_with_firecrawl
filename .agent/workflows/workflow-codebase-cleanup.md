---
description: Cleancodebase
---

# /Codebase Cleanup Workflow (Senior Code Standards)

> **Mục tiêu:** Audit toàn bộ codebase, dọn hardcoded values, extract constants, loại bỏ code rác, đưa về chuẩn senior-level code quality.
> **Phạm vi:** `backend/` — Python codebase
> **Nguyên tắc:** Không refactor logic. Chỉ di chuyển constants, xoá dead code, chuẩn hoá imports.

---

## Phase 1: Extract Hardcoded DB Paths → Constants (Critical)

### Vấn đề phát hiện:
- `canifa_ai_dump.sqlite` được hardcode ở **7+ files** bằng `os.path.join(...)` inline
- `sqlite_gender_map` dict bị copy-paste **2 lần** trong cùng `stylist_engine.py`  
- `KID_SAFE_KEYWORDS` list bị duplicate **2 lần** trong `stylist_engine.py`
- `import sqlite3` nằm **bên trong method body** thay vì đầu file

### Hành động:
- [ ] 1.1: Tạo `backend/common/constants.py` chứa TẤT CẢ constants dùng chung
- [ ] 1.2: Định nghĩa `SQLITE_DB_PATH` trong `constants.py` — single source of truth cho DB path
- [ ] 1.3: Định nghĩa `SQLITE_GENDER_MAP` trong `constants.py`
- [ ] 1.4: Định nghĩa `KID_SAFE_KEYWORDS` trong `constants.py`
- [ ] 1.5: Định nghĩa `TABLE_NAMES` dict trong `constants.py` (mapping tên bảng SQLite)
- [ ] 1.6: Refactor `stylist_engine.py` — import constants, xoá inline defs, di chuyển `import sqlite3` lên đầu
- [ ] 1.7: Refactor `lead_search_tool.py` — import `SQLITE_DB_PATH` từ constants
- [ ] 1.8: Refactor `outfit_matcher_worker.py` — import `SQLITE_DB_PATH` từ constants
- [ ] 1.9: Refactor `sqlite_mock.py` — import `SQLITE_DB_PATH` từ constants
- [ ] 1.10: Refactor `outfit_db.py` — import `SQLITE_DB_PATH` từ constants
- [ ] 1.11: Smoke test — server khởi động không lỗi

---

## Phase 2: Extract Hardcoded IPs & URLs → config.py (Critical)

### Vấn đề phát hiện:
- `172.16.2.207`, `172.16.2.210`, `172.16.2.100`, `172.16.2.192` hardcode ở **25+ chỗ**
- `http://localhost:5000` hardcode trong test files, recover_links, prompt_optimizer
- API URLs (`/api/agent/chat-dev`, `/api/stock/check`) hardcode trực tiếp

### Hành động:
- [ ] 2.1: Thêm vào `config.py` các biến env mới:
  ```python
  # ====================== INTERNAL SERVICE URLS ======================
  CHATBOT_API_BASE: str = os.getenv("CHATBOT_API_BASE", "http://172.16.2.207:5000")
  LANGFUSE_BASE: str = os.getenv("LANGFUSE_BASE", "http://172.16.2.207:3009")
  N8N_BASE_URL: str = os.getenv("N8N_BASE_URL", "http://172.16.2.207:5678")
  LITELLM_BASE_URL: str = os.getenv("LITELLM_BASE_URL", "http://172.16.2.210:3002")
  STARROCKS_INGEST_HOST: str = os.getenv("STARROCKS_INGEST_HOST", "172.16.2.100")
  ```
- [ ] 2.2: Refactor `live_monitor_route.py` — `from config import LANGFUSE_BASE`
- [ ] 2.3: Refactor `prompt_optimizer_route.py` — `from config import CHATBOT_API_BASE`
- [ ] 2.4: Refactor `user_simulator_route.py` — `from config import CHATBOT_API_BASE`
- [ ] 2.5: Refactor `simulation_runner.py` — `from config import CHATBOT_API_BASE`
- [ ] 2.6: Refactor `faq_route.py` — `from config import LITELLM_BASE_URL`
- [ ] 2.7: Refactor `n8n_desc.py` — `from config import LITELLM_BASE_URL`
- [ ] 2.8: Refactor `ingest_knowledge.py` (cả 2 files) — `from config import STARROCKS_INGEST_HOST`
- [ ] 2.9: Test files (`tests/`) — tạo `tests/conftest.py` chứa `BASE_URL` fixture
- [ ] 2.10: Smoke test — tất cả routes load không lỗi import

---

## Phase 3: Cleanup Dead Code & Migration Scripts

### Vấn đề phát hiện:
- `123.db` vẫn được ref trong 3 migration scripts đã chạy xong
- `seed_rules.py` hardcode `sqlite3.connect('123.db')` — script 1 lần
- `check_tables.py` hardcode absolute path `C:\canifa-idea\...`
- `_get_fallback_mappings()` trong stylist_engine đã bị comment toàn bộ body

### Hành động:
- [ ] 3.1: Di chuyển các file migration/one-time scripts vào `backend/database/_archive/`:
  - `seed_rules.py`
  - `database/migrate_outfit_matches.py`
  - `database/check_outfit_tables.py`
  - `database/check_tables.py`
  - `database/inspect_db.py`
  - `recover_links.py`
- [ ] 3.2: Xoá method `_get_fallback_mappings()` đã bị comment trong `stylist_engine.py`
- [ ] 3.3: Xoá commented code blocks > 5 dòng liên tiếp (nếu không phải TODO)
- [ ] 3.4: Xoá file `123.db` nếu không còn được sử dụng

---

## Phase 4: Standardize Imports & Code Style

### Vấn đề phát hiện:
- `import sqlite3` nằm bên trong method body (stylist_engine.py line 183, 343)
- `import random` nằm bên trong method body (stylist_engine.py line 745)
- `import os as _os` alias naming inconsistency (lead_search_tool.py)
- Mix `os.path.join(os.path.dirname(...))` vs `Path(__file__).parent`

### Hành động:
- [ ] 4.1: Di chuyển tất cả `import` statements lên đầu file (PEP8)
- [ ] 4.2: Chuẩn hoá path construction: sử dụng `pathlib.Path` hoặc giữ `os.path` nhất quán
- [ ] 4.3: Xoá unused imports (chạy `ruff check --select F401`)
- [ ] 4.4: Sắp xếp imports theo thứ tự: stdlib → third-party → local (isort)

---

## Phase 5: Consolidate Duplicate Logic

### Vấn đề phát hiện:
- `_normalize_gender()` pattern duplicate: stylist_engine dùng inline, lead_search_tool dùng riêng
- `_fetch_allowed_mappings()` và `_fetch_rules_with_reason()` share 80% code (connect, gender map, query)
- `outfit_matcher_worker.py` tạo 2 connections tới cùng 1 DB file nhưng đặt tên `conn_dump` và `conn_123`

### Hành động:
- [ ] 5.1: Extract shared DB query logic vào `common/outfit_db.py` (đã có file này)
- [ ] 5.2: Gộp `_fetch_allowed_mappings` + `_fetch_rules_with_reason` thành 1 method có param `include_reason=True`
- [ ] 5.3: Refactor `outfit_matcher_worker.py` — xoá dual connection, dùng single `sqlite_db` instance
- [ ] 5.4: Extract `_normalize_gender()` vào `common/constants.py` hoặc `common/utils.py`

---

## Phase 6: Final Verification

- [ ] 6.1: Chạy `ruff check backend/` — 0 errors
- [ ] 6.2: Chạy server `uvicorn server:app` — khởi động thành công
- [ ] 6.3: Test endpoint `/api/agent/chat-dev` — phản hồi bình thường
- [ ] 6.4: Test endpoint `/api/fashion-matches/` — phối đồ hoạt động
- [ ] 6.5: Git commit: `refactor: extract constants, remove hardcoded values, cleanup dead code`
- [ ] 6.6: Push to GitLab

---

## Tóm tắt Audit Findings

| Category                          | Severity   | Count | Files Affected                                                                  |
| --------------------------------- | ---------- | ----- | ------------------------------------------------------------------------------- |
| Hardcoded DB paths                | 🔴 Critical | 7     | stylist_engine, lead_search_tool, outfit_matcher_worker, sqlite_mock, outfit_db |
| Hardcoded IPs/URLs                | 🔴 Critical | 25+   | prompt_optimizer, live_monitor, faq_route, n8n_desc, simulation_runner, tests/* |
| Duplicate constants               | 🟡 Medium   | 4     | stylist_engine (gender_map ×2, kid_keywords ×2)                                 |
| Dead code / commented blocks      | 🟡 Medium   | 3     | stylist_engine (_get_fallback_mappings), config.py (langsmith)                  |
| Migration scripts as runtime code | 🟢 Low      | 6     | seed_rules, migrate_*, check_*, inspect_db                                      |
| Inline imports (PEP8 violation)   | 🟢 Low      | 3     | stylist_engine (sqlite3 ×2, random ×1)                                          |

