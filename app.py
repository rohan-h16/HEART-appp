from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lovesecret2024xoxo")

# ── Admin credentials (change these!) ──
ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "love1234")

DB = "visitors.db"

# ── Database setup ──
def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                visited_at TEXT NOT NULL
            )
        """)
        con.commit()

def save_visitor(name):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO visitors (name, visited_at) VALUES (?, ?)",
                    (name, datetime.now().strftime("%d %b %Y  %I:%M %p")))
        con.commit()

def get_all_visitors():
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT id, name, visited_at FROM visitors ORDER BY id DESC").fetchall()
    return rows

init_db()

# ══════════════════════════════════════════════
#  MAIN WEBSITE
# ══════════════════════════════════════════════
MAIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>A Heart for You 💕</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,300;0,500;1,300&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0008;
    background-image: radial-gradient(ellipse at 50% 60%, rgba(247,52,135,0.12) 0%, #0a0008 70%);
    color: #ffe8f0;
    font-family: 'Cormorant Garamond', serif;
    min-height: 100vh;
    overflow-x: hidden;
  }
  .petals { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .petal { position: absolute; top: -30px; font-size: 1.2rem; opacity: 0; animation: fall linear infinite; }
  @keyframes fall {
    0%   { transform: translateY(-30px) rotate(0deg); opacity: 0; }
    10%  { opacity: 0.6; }
    90%  { opacity: 0.3; }
    100% { transform: translateY(105vh) rotate(720deg); opacity: 0; }
  }
  #nameScreen {
    position: fixed; inset: 0; z-index: 100;
    display: flex; align-items: center; justify-content: center;
  }
  .gate-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(247,52,135,0.25);
    backdrop-filter: blur(18px);
    border-radius: 24px;
    padding: 3rem 3.5rem;
    text-align: center;
    max-width: 440px; width: 90%;
    box-shadow: 0 0 60px rgba(247,52,135,0.35);
    animation: cardIn 0.8s cubic-bezier(.22,1,.36,1) both;
  }
  @keyframes cardIn {
    from { opacity: 0; transform: translateY(40px) scale(0.95); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .gate-icon { font-size: 3rem; margin-bottom: 1rem; animation: pulse 1.8s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.12)} }
  .gate-card h1 { font-family: 'Playfair Display', serif; font-size: 2rem; color: #fff; margin-bottom: 0.4rem; }
  .gate-card p { font-size: 1.05rem; color: #c48fa0; margin-bottom: 2rem; font-style: italic; }
  .name-label { display: block; text-align: left; font-size: 0.78rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: #c48fa0; margin-bottom: 0.5rem; }
  .name-input {
    width: 100%; background: rgba(255,255,255,0.06);
    border: 1.5px solid rgba(247,52,135,0.3); border-radius: 10px;
    padding: 0.85rem 1.1rem; color: #fff;
    font-family: 'Cormorant Garamond', serif; font-size: 1.15rem;
    outline: none; transition: border-color 0.2s, box-shadow 0.2s;
  }
  .name-input::placeholder { color: rgba(196,143,160,0.5); }
  .name-input:focus { border-color: #f73487; box-shadow: 0 0 0 3px rgba(247,52,135,0.15); }
  .name-error { color: #ff6b8a; font-size: 0.82rem; margin-top: 0.4rem; min-height: 1.1em; text-align: left; }
  .gate-btn {
    margin-top: 1.5rem; width: 100%;
    background: linear-gradient(135deg, #f73487, #c2185b);
    border: none; border-radius: 10px; padding: 0.9rem;
    color: #fff; font-family: 'Playfair Display', serif;
    font-size: 1.1rem; font-weight: 700; letter-spacing: 0.05em;
    cursor: pointer; transition: transform 0.15s, box-shadow 0.2s;
    box-shadow: 0 4px 20px rgba(247,52,135,0.4);
  }
  .gate-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(247,52,135,0.55); }
  #heartScreen {
    display: none; min-height: 100vh;
    flex-direction: column; align-items: center;
    padding: 2.5rem 1rem 3rem; position: relative; z-index: 1;
  }
  #heartScreen.visible { display: flex; }
  .greeting {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.5rem, 4vw, 2.6rem);
    font-weight: 400; font-style: italic;
    text-align: center; margin-bottom: 0.3rem;
    animation: fadeUp 0.9s 0.1s both;
  }
  .greeting span { color: #f73487; font-weight: 700; font-style: normal; }
  .tagline { font-size: 1rem; color: #c48fa0; font-style: italic; margin-bottom: 2rem; animation: fadeUp 0.9s 0.2s both; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
  .color-section { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; margin-bottom: 1.8rem; animation: fadeUp 0.9s 0.35s both; }
  .color-label { font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: #c48fa0; }
  .swatches { display: flex; gap: 0.6rem; flex-wrap: wrap; justify-content: center; }
  .swatch {
    width: 36px; height: 36px; border-radius: 50%; cursor: pointer;
    border: 2px solid transparent;
    transition: transform 0.15s, border-color 0.15s, box-shadow 0.2s;
  }
  .swatch:hover { transform: scale(1.18); }
  .swatch.active { border-color: #fff; box-shadow: 0 0 0 3px #f73487, 0 0 14px rgba(247,52,135,0.35); transform: scale(1.22); }
  .canvas-wrap { position: relative; animation: fadeUp 0.9s 0.45s both; filter: drop-shadow(0 0 40px rgba(247,52,135,0.35)); }
  .restart-btn {
    margin-top: 1.6rem;
    background: transparent; border: 1.5px solid rgba(247,52,135,0.4);
    border-radius: 8px; padding: 0.55rem 1.4rem;
    color: #c48fa0; font-family: 'Cormorant Garamond', serif;
    font-size: 0.95rem; cursor: pointer;
    transition: border-color 0.2s, color 0.2s;
    animation: fadeUp 0.9s 0.55s both;
  }
  .restart-btn:hover { border-color: #f73487; color: #fff; }
</style>
</head>
<body>
<div class="petals" id="petals"></div>

<!-- Screen 1: Name Gate -->
<div id="nameScreen">
  <div class="gate-card">
    <div class="gate-icon">💕</div>
    <h1>A Heart for You</h1>
    <p>Tell me your name, and I'll paint a heart just for you.</p>
    <label class="name-label" for="nameInput">Your Name</label>
    <input class="name-input" id="nameInput" type="text" placeholder="e.g. Sofia…" autocomplete="off" maxlength="30"/>
    <div class="name-error" id="nameError"></div>
    <button class="gate-btn" id="goBtn">Open My Heart ♥</button>
  </div>
</div>

<!-- Screen 2: Heart -->
<div id="heartScreen">
  <h2 class="greeting">For <span id="displayName"></span>, with love 💗</h2>
  <p class="tagline">Every line drawn from the heart, back to the heart.</p>
  <div class="color-section">
    <span class="color-label">Choose your shade</span>
    <div class="swatches" id="swatches"></div>
  </div>
  <div class="canvas-wrap">
    <canvas id="heartCanvas" width="500" height="480"></canvas>
  </div>
  <button class="restart-btn" id="restartBtn">✦ Draw Again</button>
</div>

<script>
const petalEmojis = ['🌸','❤️','💕','🌹','💗','✿','♥'];
const petalContainer = document.getElementById('petals');
for (let i = 0; i < 22; i++) {
  const p = document.createElement('div');
  p.className = 'petal';
  p.textContent = petalEmojis[Math.floor(Math.random() * petalEmojis.length)];
  p.style.left = Math.random() * 100 + '%';
  p.style.animationDuration = (8 + Math.random() * 14) + 's';
  p.style.animationDelay = (Math.random() * 18) + 's';
  p.style.fontSize = (0.8 + Math.random() * 0.9) + 'rem';
  petalContainer.appendChild(p);
}

const palette = [
  { color: '#f73487', label: 'Hot Pink' },
  { color: '#ff1f61', label: 'Crimson Rose' },
  { color: '#ff6fa0', label: 'Blush' },
  { color: '#e91e8c', label: 'Magenta' },
  { color: '#c2185b', label: 'Deep Rose' },
  { color: '#ff80ab', label: 'Baby Pink' },
  { color: '#b71c4f', label: 'Burgundy' },
  { color: '#ff4757', label: 'Scarlet' },
  { color: '#ffa0c0', label: 'Petal' },
];

let chosenColor = palette[0].color;
const swatchContainer = document.getElementById('swatches');
palette.forEach((p, i) => {
  const el = document.createElement('div');
  el.className = 'swatch' + (i === 0 ? ' active' : '');
  el.style.background = p.color;
  el.title = p.label;
  el.addEventListener('click', () => {
    document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
    el.classList.add('active');
    chosenColor = p.color;
    drawHeart(chosenColor);
  });
  swatchContainer.appendChild(el);
});

function hearta(k) { return 15 * Math.pow(Math.sin(k), 3); }
function heartb(k) {
  return 12 * Math.cos(k) - 5 * Math.cos(2*k) - 2 * Math.cos(3*k) - Math.cos(4*k);
}

const canvas = document.getElementById('heartCanvas');
const ctx = canvas.getContext('2d');
let animId = null;

function drawHeart(color) {
  if (animId) cancelAnimationFrame(animId);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2, cy = canvas.height / 2 + 20, scale = 18, total = 1000;
  let i = 0;
  const r = parseInt(color.slice(1,3),16), g = parseInt(color.slice(3,5),16), b = parseInt(color.slice(5,7),16);
  function step() {
    for (let j = 0; j < 6 && i < total; j++, i++) {
      const t = (i / total) * Math.PI * 2;
      const x = cx + hearta(t) * scale, y = cy - heartb(t) * scale;
      ctx.beginPath();
      ctx.strokeStyle = color; ctx.lineWidth = 1.2;
      ctx.shadowColor = `rgba(${r},${g},${b},0.6)`; ctx.shadowBlur = 8;
      ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.moveTo(x, y); ctx.lineTo(cx, cy);
      ctx.stroke();
    }
    if (i < total) animId = requestAnimationFrame(step);
  }
  step();
}

const nameInput = document.getElementById('nameInput');
const nameError = document.getElementById('nameError');
const nameScreen = document.getElementById('nameScreen');
const heartScreen = document.getElementById('heartScreen');
const displayName = document.getElementById('displayName');

function proceed() {
  const name = nameInput.value.trim();
  if (!name) { nameError.textContent = '✦ Please enter your name to continue.'; nameInput.focus(); return; }
  nameError.textContent = '';

  // Save name to server
  fetch('/log_visitor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name })
  });

  displayName.textContent = name;
  nameScreen.style.opacity = '0';
  nameScreen.style.transition = 'opacity 0.5s';
  setTimeout(() => {
    nameScreen.style.display = 'none';
    heartScreen.classList.add('visible');
    drawHeart(chosenColor);
  }, 480);
}

document.getElementById('goBtn').addEventListener('click', proceed);
nameInput.addEventListener('keydown', e => { if (e.key === 'Enter') proceed(); });
document.getElementById('restartBtn').addEventListener('click', () => drawHeart(chosenColor));
</script>
</body>
</html>
"""

# ══════════════════════════════════════════════
#  ADMIN LOGIN PAGE
# ══════════════════════════════════════════════
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Admin Login 🔐</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Cormorant+Garamond:wght@300;500&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0008;
    background-image: radial-gradient(ellipse at 50% 50%, rgba(247,52,135,0.10) 0%, #0a0008 70%);
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; font-family: 'Cormorant Garamond', serif; color: #ffe8f0;
  }
  .card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(247,52,135,0.25);
    backdrop-filter: blur(18px);
    border-radius: 24px; padding: 3rem 3.5rem;
    text-align: center; max-width: 400px; width: 90%;
    box-shadow: 0 0 60px rgba(247,52,135,0.25);
  }
  .icon { font-size: 2.5rem; margin-bottom: 1rem; }
  h1 { font-family: 'Playfair Display', serif; font-size: 1.8rem; color: #fff; margin-bottom: 0.3rem; }
  p { color: #c48fa0; font-style: italic; margin-bottom: 2rem; }
  label { display: block; text-align: left; font-size: 0.75rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: #c48fa0; margin-bottom: 0.4rem; margin-top: 1rem; }
  input {
    width: 100%; background: rgba(255,255,255,0.06);
    border: 1.5px solid rgba(247,52,135,0.3); border-radius: 10px;
    padding: 0.8rem 1rem; color: #fff;
    font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; outline: none;
  }
  input:focus { border-color: #f73487; box-shadow: 0 0 0 3px rgba(247,52,135,0.15); }
  .btn {
    margin-top: 1.8rem; width: 100%;
    background: linear-gradient(135deg, #f73487, #c2185b);
    border: none; border-radius: 10px; padding: 0.85rem;
    color: #fff; font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700; cursor: pointer;
    box-shadow: 0 4px 20px rgba(247,52,135,0.4);
    transition: transform 0.15s;
  }
  .btn:hover { transform: translateY(-2px); }
  .error { color: #ff6b8a; font-size: 0.85rem; margin-top: 0.8rem; }
</style>
</head>
<body>
<div class="card">
  <div class="icon">🔐</div>
  <h1>Admin Access</h1>
  <p>Only you can see who opened your heart.</p>
  <form method="POST">
    <label>Username</label>
    <input type="text" name="username" placeholder="Enter username" autocomplete="off"/>
    <label>Password</label>
    <input type="password" name="password" placeholder="Enter password"/>
    <button class="btn" type="submit">Enter ♥</button>
    {% if error %}
    <div class="error">✦ {{ error }}</div>
    {% endif %}
  </form>
</div>
</body>
</html>
"""

# ══════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>💕 Name List — Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Cormorant+Garamond:wght@300;500&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0008;
    background-image: radial-gradient(ellipse at 50% 20%, rgba(247,52,135,0.10) 0%, #0a0008 60%);
    color: #ffe8f0; font-family: 'Cormorant Garamond', serif;
    min-height: 100vh; padding: 3rem 1rem;
  }
  .container { max-width: 700px; margin: 0 auto; }
  .header { text-align: center; margin-bottom: 2.5rem; }
  .header h1 { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: #fff; margin-bottom: 0.3rem; }
  .header p { color: #c48fa0; font-style: italic; }
  .stats {
    display: flex; gap: 1rem; justify-content: center; margin-bottom: 2rem; flex-wrap: wrap;
  }
  .stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(247,52,135,0.2);
    border-radius: 14px; padding: 1.2rem 2rem; text-align: center;
    box-shadow: 0 0 20px rgba(247,52,135,0.1);
  }
  .stat-box .num { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: #f73487; }
  .stat-box .lbl { font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; color: #c48fa0; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #c48fa0; padding: 0.7rem 1rem; text-align: left;
    border-bottom: 1px solid rgba(247,52,135,0.2);
  }
  tbody tr { transition: background 0.15s; }
  tbody tr:hover { background: rgba(247,52,135,0.06); }
  tbody td { padding: 0.85rem 1rem; font-size: 1.05rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
  .num-col { color: #c48fa0; font-size: 0.85rem; width: 40px; }
  .name-col { color: #fff; font-weight: 500; }
  .time-col { color: #c48fa0; font-size: 0.9rem; }
  .empty { text-align: center; color: #c48fa0; font-style: italic; padding: 3rem; }
  .logout {
    display: inline-block; margin-top: 2.5rem;
    background: transparent; border: 1.5px solid rgba(247,52,135,0.3);
    border-radius: 8px; padding: 0.5rem 1.4rem;
    color: #c48fa0; font-family: 'Cormorant Garamond', serif;
    font-size: 0.95rem; cursor: pointer; text-decoration: none;
    transition: border-color 0.2s, color 0.2s;
  }
  .logout:hover { border-color: #f73487; color: #fff; }
  .table-wrap {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(247,52,135,0.15);
    border-radius: 16px; overflow: hidden;
    box-shadow: 0 0 40px rgba(247,52,135,0.1);
  }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div style="font-size:2.5rem;margin-bottom:0.5rem;">💕</div>
    <h1>Your Secret Name List</h1>
    <p>Everyone who opened your heart — only visible to you.</p>
  </div>

  <div class="stats">
    <div class="stat-box">
      <div class="num">{{ visitors|length }}</div>
      <div class="lbl">Total Visitors</div>
    </div>
    <div class="stat-box">
      <div class="num">{{ visitors[0][2] if visitors else '—' }}</div>
      <div class="lbl">Latest Visit</div>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th class="num-col">#</th>
          <th>Name</th>
          <th>Date & Time</th>
        </tr>
      </thead>
      <tbody>
        {% if visitors %}
          {% for v in visitors %}
          <tr>
            <td class="num-col">{{ loop.index }}</td>
            <td class="name-col">{{ v[1] }}</td>
            <td class="time-col">{{ v[2] }}</td>
          </tr>
          {% endfor %}
        {% else %}
          <tr><td colspan="3" class="empty">No visitors yet — share your link! 💕</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>

  <div style="text-align:center">
    <a class="logout" href="/admin/logout">✦ Logout</a>
  </div>
</div>
</body>
</html>
"""

# ══════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════

@app.route("/")
def index():
    return render_template_string(MAIN_HTML)

@app.route("/log_visitor", methods=["POST"])
def log_visitor():
    data = request.get_json()
    name = data.get("name", "").strip()
    if name:
        save_visitor(name)
    return jsonify({"status": "ok"})

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("admin_logged_in"):
        visitors = get_all_visitors()
        return render_template_string(ADMIN_HTML, visitors=visitors)

    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Wrong username or password."

    return render_template_string(LOGIN_HTML, error=error)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"💕 Heart website running at: http://127.0.0.1:{port}")
    print(f"🔐 Admin panel at:           http://127.0.0.1:{port}/admin")
    app.run(host="0.0.0.0", port=port, debug=False)
