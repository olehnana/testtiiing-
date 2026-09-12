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
        # Reset drink 1 to available
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
        self.assertIn('Текіла Санрайз', html)
        self.assertIn('Джин-тонік', html)
        self.assertIn('Мохіто', html)
        self.assertIn('Блакитна Лагуна', html)
        self.assertIn('Куба Лібре', html)
        self.assertIn('Лондонський сухий джин', html)
        self.assertIn('Бехерівка лимонна', html)
        self.assertIn('Бехерівка (Becherovka Original)', html)
        self.assertIn('Єгермейстер', html)
        self.assertIn('Бурбон', html)
        # Ensure NO prices are shown
        self.assertNotIn('грн', html.lower())
        self.assertNotIn('uah', html.lower())

    def test_api_drinks(self):
        response = self.client.get('/api/drinks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(len(data['drinks']), 11)

    def test_admin_auth_and_toggle(self):
        # Without login, toggle should fail with 403
        resp_unauth = self.client.post('/admin/api/toggle/1')
        self.assertEqual(resp_unauth.status_code, 403)

        # Login with correct password
        login_resp = self.client.post('/admin/login', data={'password': 'bar123'}, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('Кабінет Редактора та Бармена', login_resp.get_data(as_text=True))

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

    def test_admin_save_and_delete_drink(self):
        # Login
        self.client.post('/admin/login', data={'password': 'bar123'})

        # Add new drink
        add_resp = self.client.post('/admin/api/save_drink', data={
            'name': 'Тестовий Коктейль',
            'category': 'Коктейлі',
            'strength': '20% об.',
            'volume': '150 мл',
            'ingredients': 'Тест, лимон',
            'description': 'Смачний тестовий напій для перевірки.',
            'image_path': '/static/images/drinks/mojito.jpg',
            'is_available': '1',
            'sort_order': '99'
        })
        self.assertEqual(add_resp.status_code, 200)

        # Check in DB
        conn = get_db()
        row = conn.execute("SELECT * FROM drinks WHERE name = 'Тестовий Коктейль'").fetchone()
        self.assertIsNotNone(row)
        drink_id = row['id']
        conn.close()

        # Delete it
        del_resp = self.client.post(f'/admin/api/delete/{drink_id}')
        self.assertEqual(del_resp.status_code, 200)

        conn = get_db()
        row_del = conn.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,)).fetchone()
        self.assertIsNone(row_del)
        conn.close()

if __name__ == '__main__':
    unittest.main()
