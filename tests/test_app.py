import unittest
import json
import os
from app import app
from database import init_db, get_db

class BarAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret'
        self.client = app.test_client()
        init_db()
        conn = get_db()
        conn.execute("UPDATE drinks SET is_available = 1 WHERE id = 1")
        conn.commit()
        conn.close()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('МЕНЮ', html)
        self.assertIn('Піна Колада', html)
        self.assertIn('Замовити', html)
        self.assertNotIn('грн', html.lower())
        self.assertNotIn('uah', html.lower())

    def test_api_drinks(self):
        response = self.client.get('/api/drinks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(len(data['drinks']), 11)

    def test_order_creation(self):
        # Create an order via API
        resp = self.client.post('/api/order', json={
            'drink_name': 'Піна Колада',
            'table_number': 'Стіл № 5',
            'quantity': 2,
            'guest_name': 'Олег',
            'comment': 'З колотим льодом'
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertIn('прийнято', data['message'])

        # Verify order in DB
        conn = get_db()
        row = conn.execute("SELECT * FROM orders WHERE table_number = 'Стіл № 5'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['drink_name'], 'Піна Колада')
        self.assertEqual(row['quantity'], 2)
        conn.close()

    def test_admin_auth_and_toggle(self):
        # Without login, toggle should fail with 403
        resp_unauth = self.client.post('/admin/api/toggle/1')
        self.assertEqual(resp_unauth.status_code, 403)

        # Login with correct password
        login_resp = self.client.post('/admin/login', data={'password': 'bar123'}, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('Панель керування закладом', login_resp.get_data(as_text=True))

        # Toggle drink 1 (Pina Colada): 1 -> 0
        toggle_resp = self.client.post('/admin/api/toggle/1')
        self.assertEqual(toggle_resp.status_code, 200)
        data = json.loads(toggle_resp.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(data['is_available'], 0)

        # Toggle back to 1: 0 -> 1
        toggle_resp2 = self.client.post('/admin/api/toggle/1')
        data2 = json.loads(toggle_resp2.get_data(as_text=True))
        self.assertEqual(data2['is_available'], 1)

    def test_admin_telegram_settings(self):
        self.client.post('/admin/login', data={'password': 'bar123'})
        resp = self.client.post('/admin/api/telegram_settings', data={
            'telegram_bot_token': '123456:FAKE_TOKEN',
            'telegram_chat_id': '987654321',
            'telegram_enabled': '1'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        conn = get_db()
        token = conn.execute("SELECT value FROM settings WHERE key = 'telegram_bot_token'").fetchone()['value']
        enabled = conn.execute("SELECT value FROM settings WHERE key = 'telegram_enabled'").fetchone()['value']
        self.assertEqual(token, '123456:FAKE_TOKEN')
        self.assertEqual(enabled, '1')
        conn.close()

    def test_order_with_payment_and_promocode(self):
        # 1. Order with Monobank payment
        resp1 = self.client.post('/api/order', json={
            'drink_name': 'Мохіто',
            'table_number': 'Бар 1',
            'quantity': 1,
            'payment_method': 'Картка (Монобанка)',
            'promocode': ''
        })
        self.assertEqual(resp1.status_code, 200)
        
        # 2. Order with РОДИНА promo code (-100%)
        resp2 = self.client.post('/api/order', json={
            'drink_name': 'Апероль Спрітц',
            'table_number': 'Стіл 2',
            'quantity': 2,
            'payment_method': 'Готівка',
            'promocode': 'родина'
        })
        self.assertEqual(resp2.status_code, 200)

        conn = get_db()
        row1 = conn.execute("SELECT * FROM orders WHERE table_number = 'Бар 1'").fetchone()
        self.assertEqual(row1['payment_method'], 'Картка (Монобанка)')
        
        row2 = conn.execute("SELECT * FROM orders WHERE table_number = 'Стіл 2'").fetchone()
        self.assertIn('Промокод РОДИНА', row2['payment_method'])
        self.assertEqual(row2['promocode'], 'родина')
        conn.close()

    def test_feedback_creation_and_admin_view(self):
        # 1. Post a review
        resp = self.client.post('/api/feedback', json={
            'feedback_type': 'Відгук',
            'guest_name': 'Іван',
            'rating': 5,
            'message': 'Чудовий бар та смачні коктейлі!'
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data(as_text=True))
        self.assertTrue(data['success'])

        # 2. Check DB
        conn = get_db()
        fb = conn.execute("SELECT * FROM feedback WHERE guest_name = 'Іван'").fetchone()
        self.assertIsNotNone(fb)
        self.assertEqual(fb['feedback_type'], 'Відгук')
        self.assertEqual(fb['rating'], 5)
        self.assertEqual(fb['message'], 'Чудовий бар та смачні коктейлі!')
        fb_id = fb['id']
        conn.close()

        # 3. Check admin view
        self.client.post('/admin/login', data={'password': 'bar123'})
        admin_resp = self.client.get('/admin')
        self.assertIn('Чудовий бар та смачні коктейлі!', admin_resp.get_data(as_text=True))

        # 4. Admin delete feedback
        del_resp = self.client.post(f'/admin/api/feedback/delete/{fb_id}')
        self.assertEqual(del_resp.status_code, 200)

        conn = get_db()
        fb_after = conn.execute("SELECT * FROM feedback WHERE id = ?", (fb_id,)).fetchone()
        self.assertIsNone(fb_after)
        conn.close()

if __name__ == '__main__':
    unittest.main()

