import os
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bar_newspaper_secret_key_raspberrypi5_2026')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'bar123')

# Ukrainian day and month names
UA_DAYS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця", 'Субота', 'Неділя']
UA_MONTHS = [
    '', 'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня',
    'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня'
]

def get_current_ua_date():
    now = datetime.datetime.now()
    day_name = UA_DAYS[now.weekday()]
    month_name = UA_MONTHS[now.month]
    return f"{day_name}, {now.day} {month_name} {now.year} року"

def is_local_request():
    # If request comes through Cloudflare Tunnel (public internet)
    if request.headers.get('CF-Ray') or request.headers.get('CF-Connecting-IP'):
        return False
    host = request.host.split(':')[0].lower()
    # Check if host is direct local IP or localhost
    if host in ['localhost', '127.0.0.1'] or host.startswith('192.168.') or host.startswith('10.') or host.startswith('172.'):
        return True
    return False

@app.before_request
def restrict_admin_to_local_ip():
    if request.path.startswith('/admin'):
        if not is_local_request():
            return render_template('403_local_only.html'), 403

def get_all_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}

@app.context_processor
def inject_global_vars():
    settings = get_all_settings()
    return {
        'settings': settings,
        'ua_date': get_current_ua_date(),
        'is_admin': session.get('is_admin', False),
        'is_local': is_local_request()
    }

# Ensure DB is created on app launch
init_db()

# ================= PUBLIC ROUTES =================

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drinks ORDER BY sort_order ASC, id ASC")
    drinks = cursor.fetchall()
    
    # Extract distinct categories
    cursor.execute("SELECT DISTINCT category FROM drinks ORDER BY category ASC")
    categories = [r['category'] for r in cursor.fetchall()]
    conn.close()
    
    total_count = len(drinks)
    available_count = sum(1 for d in drinks if d['is_available'])
    
    return render_template(
        'index.html',
        drinks=drinks,
        categories=categories,
        total_count=total_count,
        available_count=available_count
    )

@app.route('/api/drinks')
def api_drinks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drinks ORDER BY sort_order ASC, id ASC")
    drinks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'drinks': drinks})

# ================= ADMIN ROUTES =================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
        
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Ласкаво просимо до кабінету редактора прейскуранту!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Невірний пароль доступу. Спробуйте ще раз.'
            
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Ви вийшли з режиму редактора.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drinks ORDER BY sort_order ASC, id ASC")
    drinks = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT category FROM drinks ORDER BY category ASC")
    categories = [r['category'] for r in cursor.fetchall()]
    conn.close()
    
    return render_template(
        'admin_dashboard.html',
        drinks=drinks,
        categories=categories
    )

@app.route('/admin/api/toggle/<int:drink_id>', methods=['POST'])
def admin_toggle_availability(drink_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Неавторизовано'}), 403
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_available, name FROM drinks WHERE id = ?", (drink_id,))
    drink = cursor.fetchone()
    if not drink:
        conn.close()
        return jsonify({'success': False, 'error': 'Напій не знайдено'}), 404
        
    new_status = 0 if drink['is_available'] == 1 else 1
    cursor.execute("UPDATE drinks SET is_available = ? WHERE id = ?", (new_status, drink_id))
    conn.commit()
    conn.close()
    
    status_text = "В наявності" if new_status == 1 else "Тимчасово відсутнє"
    return jsonify({
        'success': True,
        'drink_id': drink_id,
        'is_available': new_status,
        'message': f"«{drink['name']}» тепер: {status_text}"
    })

@app.route('/admin/api/save_drink', methods=['POST'])
def admin_save_drink():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Неавторизовано'}), 403
        
    drink_id = request.form.get('id')
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    strength = request.form.get('strength', '').strip()
    volume = request.form.get('volume', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    description = request.form.get('description', '').strip()
    image_path = request.form.get('image_path', '').strip()
    is_available = 1 if request.form.get('is_available') in ['1', 'on', 'true'] else 0
    sort_order = int(request.form.get('sort_order', 0) or 0)
    
    if not name or not category or not description:
        return jsonify({'success': False, 'error': "Назва, категорія та опис є обов'язковими"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    if drink_id:
        cursor.execute("""
        UPDATE drinks SET
            name = ?, category = ?, strength = ?, volume = ?,
            ingredients = ?, description = ?, image_path = ?,
            is_available = ?, sort_order = ?
        WHERE id = ?
        """, (name, category, strength, volume, ingredients, description, image_path, is_available, sort_order, drink_id))
        msg = f"Позицію «{name}» успішно оновлено"
    else:
        cursor.execute("""
        INSERT INTO drinks (name, category, strength, volume, ingredients, description, image_path, is_available, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, strength, volume, ingredients, description, image_path, is_available, sort_order))
        msg = f"Нову позицію «{name}» успішно додано"
        
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': msg})

@app.route('/admin/api/delete/<int:drink_id>', methods=['POST'])
def admin_delete_drink(drink_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Неавторизовано'}), 403
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM drinks WHERE id = ?", (drink_id,))
    drink = cursor.fetchone()
    if not drink:
        conn.close()
        return jsonify({'success': False, 'error': 'Напій не знайдено'}), 404
        
    cursor.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f"Позицію «{drink['name']}» видалено"})

@app.route('/admin/api/settings', methods=['POST'])
def admin_update_settings():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Неавторизовано'}), 403
        
    conn = get_db()
    cursor = conn.cursor()
    for key in ['bar_name', 'bar_tagline', 'issue_info', 'announcement', 'motto', 'bar_hours', 'bar_address']:
        if key in request.form:
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, request.form[key].strip()))
            
    conn.commit()
    conn.close()
    flash('Налаштування газети успішно збережено!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
