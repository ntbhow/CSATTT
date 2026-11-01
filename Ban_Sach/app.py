"""Local-only, intentionally vulnerable XSS training application."""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

HOST, PORT = "127.0.0.1", 8000
COMMENTS: list[str] = []

CSS = r"""
:root{color-scheme:dark;--bg:#08101e;--panel:#111e31;--panel2:#14253b;--line:#29405b;--muted:#9fb2cb;--text:#edf5ff;--cyan:#5de1ed;--green:#69e3ae;--amber:#ffca82}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 74% 0%,#102d46 0,transparent 35%),var(--bg);color:var(--text);font:15px/1.65 system-ui,-apple-system,Segoe UI,sans-serif}
a{color:inherit;text-decoration:none}.shell{display:grid;grid-template-columns:255px minmax(0,1fr);min-height:100vh}.sidebar{background:#0b1728e9;border-right:1px solid var(--line);padding:29px 18px}.brand{display:flex;gap:12px;align-items:center;font-size:22px;font-weight:850;letter-spacing:-.5px}.brand-icon{display:grid;place-items:center;border-radius:13px;width:42px;height:42px;background:#173e53;color:var(--cyan)}.brand em{font-style:normal;color:var(--cyan)}.brand-sub{font-size:12px;color:var(--muted);padding:10px 0 28px}.nav-label{font-size:11px;letter-spacing:2px;color:#7891ae;font-weight:800;margin:23px 13px 10px}.nav a{display:flex;gap:11px;align-items:center;padding:13px 14px;border-radius:11px;color:#a9bfda;margin:3px 0;transition:.2s}.nav a:hover,.nav a.active{color:var(--cyan);background:#19334a}.nav a.active{box-shadow:inset 3px 0 var(--cyan)}.side-status{padding:17px;border:1px solid #31536a;background:#132b3c;border-radius:13px;margin-top:38px}.side-status strong{display:block;color:var(--green);font-size:12px;letter-spacing:1px}.side-status p{color:var(--muted);font-size:12px;margin:7px 0 0}.main{padding:37px clamp(18px,4vw,64px);max-width:1500px;width:100%;margin:auto}.eyebrow{font-size:12px;color:var(--cyan);font-weight:800;letter-spacing:2px;text-transform:uppercase}.top{display:flex;justify-content:space-between;gap:20px;align-items:center}.top h1{font-size:clamp(25px,3.5vw,37px);letter-spacing:-1.2px;margin:5px 0}.live{padding:8px 13px;border:1px solid #24604f;color:var(--green);border-radius:40px;background:#14352c;font-size:12px;font-weight:750;white-space:nowrap}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);margin-right:6px}.lead{color:var(--muted);max-width:720px;margin:5px 0 28px}.warning{color:#f7ce99;background:#35281d;border:1px solid #73523a;padding:12px 17px;border-radius:11px;font-size:13px;margin-bottom:24px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:23px}.metric,.card,.module,.tip{background:linear-gradient(145deg,var(--panel),#0e1a2b);border:1px solid var(--line);border-radius:17px}.metric{padding:20px}.metric b{font-size:28px;display:block;line-height:1.2}.metric span{font-size:12px;color:var(--muted)}.card{padding:clamp(20px,3vw,34px);margin-bottom:19px;overflow-wrap:anywhere}.card h2{font-size:22px;letter-spacing:-.5px;margin:0 0 8px}.card h3{color:var(--cyan);font-size:15px;margin-top:24px}.card p{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}.module{padding:25px;transition:transform .2s,border-color .2s;display:block}.module:hover{transform:translateY(-3px);border-color:var(--cyan)}.module .num{display:inline-block;border-radius:9px;background:#1b4052;color:var(--cyan);font-weight:800;font-size:12px;padding:5px 10px;margin-bottom:23px}.module h3{margin:0 0 8px;color:var(--text);font-size:19px}.module p{margin:0;color:var(--muted);font-size:13px}.module .go{display:block;color:var(--cyan);font-size:13px;font-weight:750;margin-top:22px}.tag{display:inline-block;border:1px solid #42637d;background:#1b3548;color:#aeeaf8;border-radius:50px;padding:5px 11px;font-size:11px;font-weight:800;letter-spacing:.6px}.form-label{display:block;margin:20px 0 6px;color:#cbdbee;font-size:13px;font-weight:700}input,textarea{display:block;width:100%;font:inherit;color:var(--text);background:#081526;border:1px solid #35506c;border-radius:10px;padding:13px 15px;outline:none}input:focus,textarea:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #5de1ed18}textarea{min-height:110px;resize:vertical}button{cursor:pointer;background:linear-gradient(125deg,#38c8da,#138daf);border:0;color:#061322;font:inherit;font-weight:850;padding:12px 20px;border-radius:10px;margin-top:15px;transition:filter .2s}button:hover{filter:brightness(1.12)}.result{min-height:70px;margin-top:15px;padding:18px;background:#091727;border:1px dashed #41617a;border-radius:11px;overflow-wrap:anywhere}.result:empty:before{content:'Chưa có dữ liệu hiển thị';color:#6988a7}.tip{padding:15px 18px;color:var(--muted);font-size:13px;margin-top:17px}.tip code,.card code{color:#9ff4ed;background:#1c3845;padding:2px 5px;border-radius:4px}.comments{padding-left:20px}.comments li{padding:10px 0;border-bottom:1px solid #253a50}.footer{text-align:center;color:#6883a3;font-size:12px;padding:30px}.safe{color:var(--green)}
@media(max-width:850px){.shell{display:block}.sidebar{position:static;padding:17px}.brand-sub,.side-status,.nav-label{display:none}.nav{display:flex;overflow-x:auto;gap:6px;margin-top:12px}.nav a{white-space:nowrap;font-size:12px;padding:9px}.main{padding:23px 16px}.metrics{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.live{display:none}}@media(max-width:480px){.metrics{grid-template-columns:1fr}}
"""


def page(title: str, active: str, inner: str, lead: str) -> str:
    links = [
        ("/", "◈", "Dashboard"),
        ("/reflected", "⌕", "Reflected XSS"),
        ("/stored", "▤", "Stored XSS"),
        ("/dom", "⌘", "DOM-based XSS"),
        ("/safe", "✓", "Safe Output"),
    ]
    nav = "".join(
        f'<a class="{"active" if url == active else ""}" href="{url}"><span>{symbol}</span>{escape(label)}</a>'
        for url, symbol, label in links
    )
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} • XSS Lab</title><style>{CSS}</style></head><body>
<div class="shell"><aside class="sidebar"><div class="brand"><span class="brand-icon">⬡</span><span>XSS <em>LAB</em></span></div>
<div class="brand-sub">CYBERSECURITY TRAINING PLATFORM</div>
<div class="nav-label">LABORATORY</div><nav class="nav">{nav}</nav>
<div class="side-status"><strong>● LOCAL ENVIRONMENT</strong><p>127.0.0.1:8000<br>Educational use only</p></div></aside>
<main class="main"><div class="top"><div><div class="eyebrow">Security / Training</div><h1>{escape(title)}</h1></div>
<span class="live"><span class="dot"></span>LAB ACTIVE</span></div>
<p class="lead">{escape(lead)}</p><div class="warning">⚠ Môi trường cố ý chứa lỗ hổng. Chỉ chạy trên localhost, không dùng tài khoản hoặc dữ liệu thật.</div>
{inner}<div class="footer">XSS Security Lab · Local training · Python standard library</div></main></div></body></html>"""


def dashboard() -> str:
    cards = [
        ("/reflected", "01", "Reflected XSS", "Payload trở lại ngay trong HTTP response và được trình duyệt diễn giải."),
        ("/stored", "02", "Stored XSS", "Bình luận lưu trong bộ nhớ server; thử tải lại trang để kiểm tra."),
        ("/dom", "03", "DOM-based XSS", "Mã JavaScript phía client đưa đầu vào vào innerHTML."),
        ("/safe", "04", "Safe Output", "Đối chiếu với cách xuất văn bản đã được HTML-escape."),
    ]
    modules = "".join(
        f'<a class="module" href="{url}"><span class="num">LAB {num}</span><h3>{title}</h3><p>{desc}</p><span class="go">Mở bài kiểm thử ↗</span></a>'
        for url, num, title, desc in cards
    )
    return '<div class="metrics"><div class="metric"><b>04</b><span>Training modules</span></div><div class="metric"><b>03</b><span>Intentionally vulnerable examples</span></div><div class="metric"><b>01</b><span>Safe comparison</span></div></div>' + f'<div class="grid">{modules}</div>'


class Handler(BaseHTTPRequestHandler):
    def send_html(self, content: str, status: int = 200) -> None:
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        path = url.path
        query = parse_qs(url.query).get("q", [""])[0]
        if path == "/":
            html = page("Security Dashboard", path, dashboard(), "Nắm bắt ba loại lỗ hổng XSS thông qua bài thử có kiểm soát, sau đó so sánh cách xử lý an toàn.")
        elif path == "/reflected":
            # DELIBERATELY VULNERABLE: unescaped user input in HTML response.
            inner = f'''<section class="card"><span class="tag">LAB 01 · SERVER-SIDE REFLECTION</span><h2>Search Playground</h2><p>Giả lập chức năng tìm kiếm phản chiếu từ khóa vào HTML.</p>
            <form method="get"><label class="form-label" for="q">Search query</label><input id="q" name="q" placeholder="Nhập từ khóa hoặc payload" autocomplete="off"><button type="submit">Tìm kiếm ↗</button></form>
            <h3>Kết quả tìm kiếm</h3><div class="result">{query}</div>
            <div class="tip">Gợi ý thử nghiệm: <code>&lt;script&gt;alert('Reflected XSS')&lt;/script&gt;</code></div></section>'''
            html = page("Reflected XSS", path, inner, "Quan sát một tham số URL được đưa trực tiếp trở lại HTML response.")
        elif path == "/stored":
            # DELIBERATELY VULNERABLE: stored comment values are not escaped.
            items = "".join(f"<li>{comment}</li>" for comment in COMMENTS)
            inner = f'''<section class="card"><span class="tag">LAB 02 · STORED CONTENT</span><h2>Community Comments</h2><p>Nhập bình luận, sau đó tải lại trang để xem nội dung đã được lưu tạm trong RAM.</p>
            <form method="post" action="/stored"><label class="form-label" for="comment">Bình luận</label><textarea id="comment" name="comment" maxlength="2000" placeholder="Viết bình luận tại đây..." required></textarea><button type="submit">Đăng bình luận ↗</button></form>
            <h3>Bình luận đã lưu ({len(COMMENTS)})</h3><div class="result"><ul class="comments">{items}</ul></div>
            <div class="tip">Payload thử: <code>&lt;script&gt;alert('Stored XSS')&lt;/script&gt;</code>. Tắt và mở lại server để xóa dữ liệu thử nghiệm.</div></section>'''
            html = page("Stored XSS", path, inner, "Xem tác động khi nội dung bình luận không được escape trước khi render.")
        elif path == "/dom":
            inner = '''<section class="card"><span class="tag">LAB 03 · CLIENT-SIDE DOM</span><h2>Dynamic Profile Preview</h2><p>Dữ liệu được trình duyệt xử lý trực tiếp, không gửi lên server.</p>
            <label class="form-label" for="nameInput">Tên hiển thị</label><input id="nameInput" placeholder="Nhập tên hoặc payload" autocomplete="off"><button type="button" id="showName">Hiển thị ↗</button>
            <h3>Live preview</h3><div class="result" id="output"></div>
            <div class="tip">Payload thử: <code>&lt;img src=x onerror=alert('DOM XSS')&gt;</code>. Hình ảnh cố ý không tải được để kích hoạt onerror.</div></section>
            <script>document.getElementById('showName').addEventListener('click', function () {
            const value = document.getElementById('nameInput').value;
            // DELIBERATELY VULNERABLE DOM sink:
            document.getElementById('output').innerHTML = value;
            });</script>'''
            html = page("DOM-based XSS", path, inner, "Tìm hiểu rủi ro của innerHTML khi được gán dữ liệu không đáng tin cậy.")
        elif path == "/safe":
            inner = f'''<section class="card"><span class="tag">LAB 04 · DEFENSIVE CODING</span><h2>Safe Output Encoding</h2><p>Thử payload tương tự Reflected XSS. Ở đây đầu ra được HTML-escape trước khi render.</p>
            <form method="get"><label class="form-label" for="q">Search query</label><input id="q" name="q" placeholder="Nhập payload để so sánh" autocomplete="off"><button type="submit">Kiểm tra an toàn ↗</button></form>
            <h3 class="safe">✓ Kết quả đã escape</h3><div class="result">{escape(query)}</div>
            <div class="tip">Giải pháp minh họa: <code>html.escape(query)</code>. Với các ngữ cảnh khác như URL, JavaScript hay HTML attribute, cần dùng giải pháp phù hợp với từng ngữ cảnh.</div></section>'''
            html = page("Safe Output", path, inner, "So sánh cách hiển thị an toàn cùng đầu vào với Reflected XSS.")
        else:
            self.send_html(page("Không tìm thấy trang", "", '<section class="card"><h2>404</h2><p>Đường dẫn không tồn tại.</p><a href="/">← Về Dashboard</a></section>', ""), 404)
            return
        self.send_html(html)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/stored":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if length < 0 or length > 4096:
            self.send_error(413)
            return
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        comment = parse_qs(raw).get("comment", [""])[0][:2000]
        if comment.strip():
            COMMENTS.append(comment)
        self.send_response(303)
        self.send_header("Location", "/stored")
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    print(f"XSS Lab running at http://{HOST}:{PORT} (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
