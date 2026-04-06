from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "ultimate_erp_final_2026"

# --- 1. قاعدة البيانات الشاملة ---
def init_db():
    conn = sqlite3.connect('smart_erp_final.db')
    cursor = conn.cursor()
    # المنتجات (مع التكلفة والضريبة)
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
        (id INTEGER PRIMARY KEY, barcode TEXT, name TEXT, qty INTEGER, price REAL, cost REAL, tax_rate REAL DEFAULT 0.15)''')
    # دليل الحسابات الاحترافي
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts 
        (id INTEGER PRIMARY KEY, code TEXT UNIQUE, name TEXT, category TEXT, balance REAL DEFAULT 0.0)''')
    # سجل القيود اليومية (الدفتر المحاسبي)
    cursor.execute('''CREATE TABLE IF NOT EXISTS journal 
        (id INTEGER PRIMARY KEY, date TEXT, description TEXT, debit REAL, credit REAL, account_code TEXT)''')
    # نظام المستخدمين
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # إضافة البيانات الأساسية
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', '123', 'admin'), ('cashier', '123', 'cashier')")
    
    accounts = [
        ('1101', 'الصندوق الرئيسي', 'أصول'),
        ('1201', 'المخزون السلعي', 'أصول'),
        ('2101', 'حساب الموردين', 'خصوم'),
        ('2201', 'ضريبة القيمة المضافة', 'خصوم'),
        ('4101', 'إيرادات المبيعات', 'إيرادات'),
        ('5101', 'تكلفة المبيعات', 'مصروفات'),
        ('5102', 'المصاريف التشغيلية', 'مصروفات')
    ]
    cursor.executemany("INSERT OR IGNORE INTO accounts (code, name, category) VALUES (?,?,?)", accounts)
    conn.commit()
    conn.close()

init_db()

# --- 2. واجهة المستخدم الاحترافية (UI/UX) ---
LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>SMART ERP | النظام المتكامل 2026</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --sidebar-bg: #0f172a; --accent: #3b82f6; }
        body { background: #f8fafc; font-family: 'Segoe UI', sans-serif; }
        .sidebar { width: 280px; height: 100vh; background: var(--sidebar-bg); color: white; position: fixed; right: 0; transition: 0.3s; z-index: 1000; }
        .main-content { margin-right: 280px; padding: 30px; }
        .nav-link { color: #94a3b8; padding: 12px 20px; border-radius: 10px; margin: 4px 15px; display: block; text-decoration: none; }
        .nav-link:hover, .nav-link.active { background: #1e293b; color: white; border-right: 4px solid var(--accent); }
        .card-custom { border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); background: white; }
        @media print { .sidebar, .no-print { display: none !important; } .main-content { margin-right: 0; } }
    </style>
</head>
<body>
    <div class="sidebar shadow">
        <div class="p-4 text-center border-bottom border-secondary mb-3">
            <h3 class="fw-bold text-white">SMART <span class="text-primary">ERP</span></h3>
            <small class="text-info">نظام المؤسسة الشامل 🦅</small>
        </div>
        <a href="/" class="nav-link active"><i class="fas fa-chart-line me-2"></i> لوحة التحكم</a>
        <a href="/pos" class="nav-link"><i class="fas fa-cash-register me-2"></i> شاشة الكاشير</a>
        {% if session['role'] == 'admin' %}
        <a href="/accounts" class="nav-link"><i class="fas fa-university me-2"></i> دليل الحسابات</a>
        <a href="/products" class="nav-link"><i class="fas fa-boxes me-2"></i> إدارة المخزون</a>
        <a href="/reports" class="nav-link"><i class="fas fa-file-invoice-dollar me-2"></i> تقارير الأرباح</a>
        {% endif %}
        <div class="position-absolute bottom-0 w-100 p-3">
            <div class="bg-dark p-3 rounded small text-center border border-secondary">
                <span class="d-block mb-1 text-muted">المستخدم: {{ session['username'] }}</span>
                <a href="/logout" class="text-danger fw-bold text-decoration-none">خروج <i class="fas fa-sign-out-alt"></i></a>
            </div>
        </div>
    </div>
    <div class="main-content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- 3. المسارات الوظيفية ---

@app.route('/')
def dashboard():
    if not session.get('logged_in'): return redirect('/login')
    conn = sqlite3.connect('smart_erp_final.db')
    cash = conn.execute("SELECT balance FROM accounts WHERE code='1101'").fetchone()[0]
    sales = conn.execute("SELECT balance FROM accounts WHERE code='4101'").fetchone()[0]
    tax = conn.execute("SELECT balance FROM accounts WHERE code='2201'").fetchone()[0]
    conn.close()
    return render_template_string(LAYOUT + """
    {% block content %}
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold">ملخص الأداء المالي</h2>
        <span class="badge bg-primary px-3 py-2">مُحدث: {{ date }}</span>
    </div>
    <div class="row g-4 mb-5">
        <div class="col-md-4"><div class="card card-custom p-4 border-start border-primary border-5">
            <small class="text-muted">نقدية الصندوق</small><h2 class="fw-bold mt-2">{{ cash }} ريال</h2>
        </div></div>
        <div class="col-md-4"><div class="card card-custom p-4 border-start border-success border-5">
            <small class="text-muted">إجمالي المبيعات</small><h2 class="fw-bold text-success mt-2">{{ sales }} ريال</h2>
        </div></div>
        <div class="col-md-4"><div class="card card-custom p-4 border-start border-warning border-5">
            <small class="text-muted">ضريبة القيمة المضافة</small><h2 class="fw-bold text-warning mt-2">{{ tax }} ريال</h2>
        </div></div>
    </div>
    <div class="card card-custom p-4"><canvas id="mainChart" style="max-height: 350px;"></canvas></div>
    <script>
        new Chart(document.getElementById('mainChart'), {
            type: 'bar',
            data: { labels: ['المبيعات', 'الضرائب'], datasets: [{ label: 'الريال السعودي', data: [{{ sales }}, {{ tax }}], backgroundColor: ['#3b82f6', '#f59e0b'] }] }
        });
    </script>
    {% endblock %}
    """, cash=cash, sales=sales, tax=tax, date=datetime.date.today())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['u'], request.form['p']
        conn = sqlite3.connect('smart_erp_final.db')
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if user:
            session.update({'logged_in': True, 'username': user[1], 'role': user[3]})
            return redirect('/')
    return '<body><div style="text-align:center; padding-top:100px; font-family:sans-serif;"><h2>تسجيل الدخول للنظام</h2><form method="POST"><input name="u" placeholder="Admin"><br><input name="p" type="password" placeholder="123"><br><button>دخول</button></form></div></body>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
