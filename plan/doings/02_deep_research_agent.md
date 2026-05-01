# Epic: Tích hợp LangGraph Deep Research Agent

## Context
Dựa trên kiến trúc của `firecrawl/web-agent`, xây dựng một luồng Deep Research Agent bằng Python (LangGraph) với khả năng stream event (SSE) xuống frontend, tạo trải nghiệm Autonomous Agent với "Thinking Steps" UI.

## Checklists

### Giai đoạn 1: Backend Core (LangGraph)
- [ ] Cài đặt các thư viện `langgraph`, `langchain-core` vào `backend/.venv` (nếu chưa có).
- [ ] Tạo module `backend/deep_research/` với `__init__.py`.
- [ ] Viết `state.py`: Định nghĩa `AgentState` để LangGraph truyền dữ liệu giữa các node.
- [ ] Viết `tools.py`: Triển khai các công cụ như `web_search`, `scrape_url`, `format_output` sử dụng FreeLLMAPI hoặc Jina.
- [ ] Viết `graph.py`: Xây dựng State Graph với các Node: `agent` và `tools`. Định nghĩa luồng logic và Edge để điều phối chu trình vòng lặp.

### Giai đoạn 2: API & Streaming (FastAPI)
- [ ] Tạo endpoint `POST /api/deep-research` (hoặc sửa đổi endpoint `/api/search` hiện tại) trong `backend/server.py`.
- [ ] Tích hợp Graph vào endpoint, xử lý LangGraph stream output (`stream_mode="updates"`) thành SSE payload (format `{"type": "tool-call", ...}`).

### Giai đoạn 3: Frontend (UI/UX)
- [ ] Thêm nút Toggle chuyển đổi chế độ "Standard" và "Deep Research" trong `index.html`.
- [ ] Xây dựng UI component "Thinking Steps" bên phải hoặc trong cửa sổ chat (`docs.html` / `index.html` / `style.css`) để hiển thị logs (VD: *Đang cào dữ liệu từ...*).
- [ ] Cập nhật `app.js` để parse các dòng event `tool-call`, `tool-result` và render chúng ra UI realtime.
- [ ] Hoàn thiện bước cuối: Render Markdown kết quả khi có event `done`.

### Giai đoạn 4: QA & Verification (TDD)
- [ ] Kiểm tra lỗi Timeout hoặc Vòng lặp vô hạn của Graph.
- [ ] Đảm bảo UI Responsive không bị vỡ do bảng log Thinking Steps.
