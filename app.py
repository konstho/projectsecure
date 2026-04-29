from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'shop_secret_key'


app.config['SESSION_COOKIE_HTTPONLY'] = False

DATABASE = 'shop.db'


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()


@app.route('/')
def home():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('home.html', products=products)


# VULNERABILITY 1: SQL Injection
# User input is interpolated directly into the SQL query.
@app.route('/search')
def search():
    db = get_db()
    q = request.args.get('q', '')
    results = []
    if q:
        try:
            results = db.execute(
                f"SELECT * FROM products WHERE name LIKE '%{q}%'"
            ).fetchall()
        except Exception:
            results = []
    return render_template('search.html', results=results, query=q)


@app.route('/product/<int:pid>')
def product(pid):
    db = get_db()
    item = db.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
    if not item:
        return 'Not found', 404
    reviews = db.execute(
        'SELECT * FROM reviews WHERE product_id=?', (pid,)
    ).fetchall()
    return render_template('product.html', product=item, reviews=reviews)


# VULNERABILITY 2: Stored XSS
# Review content is stored raw and rendered with | safe, so any
# <script> in the review runs in every visitor's browser.
@app.route('/product/<int:pid>/review', methods=['POST'])
def add_review(pid):
    if 'user' not in session:
        return redirect(url_for('login'))
    content = request.form.get('content', '').strip()
    if content:
        db = get_db()
        db.execute(
            'INSERT INTO reviews (product_id, username, content) VALUES (?,?,?)',
            (pid, session['user'], content)
        )
        db.commit()
    return redirect(url_for('product', pid=pid))


@app.route('/orders')
def orders():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    rows = db.execute(
        'SELECT * FROM orders WHERE username=?', (session['user'],)
    ).fetchall()
    return render_template('orders.html', orders=rows)


# VULNERABILITY 3: IDOR
# The order ID comes straight from the URL and is never checked
# against the logged-in user. Anyone can read any order's PII.
@app.route('/order/<int:oid>')
def order_detail(oid):
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id=?', (oid,)).fetchone()
    if not order:
        return 'Order not found', 404
    return render_template('order_detail.html', order=order)


# Admin dashboard — only accessible when logged in as admin.
# This is the "prize" for a successful XSS session hijack.
@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return 'Access denied', 403
    db = get_db()
    all_orders = db.execute('SELECT * FROM orders').fetchall()
    revenue = sum(o['total'] for o in all_orders)
    user_count = db.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
    return render_template(
        'admin.html',
        orders=all_orders,
        revenue=revenue,
        user_count=user_count,
    )


# Simulates the attacker's server. In a real attack this would live
@app.route('/steal')
def steal():
    cookie = request.args.get('c', '')
    if cookie:
        with open('stolen.log', 'a') as f:
            f.write(cookie + '\n')
    return '', 204


# Attacker's dashboard, shows whatever was captured by /steal.
@app.route('/stolen')
def stolen():
    try:
        with open('stolen.log') as f:
            entries = [e for e in f.read().splitlines() if e]
    except FileNotFoundError:
        entries = []
    return render_template('stolen.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username=? AND password=?', (u, p)
        ).fetchone()
        if user:
            session['user'] = user['username']
            return redirect(url_for('home'))
        error = 'Wrong username or password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
