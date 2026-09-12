import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'bar.db')

DEFAULT_DRINKS = [
    {
        "name": "Піна Колада",
        "category": "Коктейлі",
        "strength": "12% об.",
        "volume": "250 мл",
        "ingredients": "Білий ром, кокосовий крем, ананасовий сік, ананас, лід",
        "description": "Легендарна карибська насолода. Густий, кремовий тропічний коктейль із ніжним поєднанням кокосового молока, сонячного ананасового соку та світлого витриманого рому. Подається крижаним у келиху ураган.",
        "image_path": "/static/images/drinks/pina_colada.jpg",
        "is_available": 1,
        "sort_order": 1
    },
    {
        "name": "Текіла Санрайз",
        "category": "Коктейлі",
        "strength": "14% об.",
        "volume": "200 мл",
        "ingredients": "Срібна текіла, натуральний апельсиновий сік, сироп гренадин, скибка апельсина",
        "description": "Справжній світанок у високому келиху. Градуйований перехід від глибокого рубінового гренадину до сонячного золота цитрусів. Освіжаючий, солодкувато-терпкий смак із виразним агавовим серцем.",
        "image_path": "/static/images/drinks/tequila_sunrise.jpg",
        "is_available": 1,
        "sort_order": 2
    },
    {
        "name": "Джин-тонік",
        "category": "Коктейлі",
        "strength": "15% об.",
        "volume": "200 мл",
        "ingredients": "Лондонський сухий джин, класичний індіан-тонік, свіжий лайм, ягоди ялівцю",
        "description": "Бездоганна британська строгість. Кришталево чистий мікс із пряно-ялівцевим характером джину, благородною хініновою гіркуватістю та бадьорим цитрусовим післясмаком.",
        "image_path": "/static/images/drinks/gin_tonic.jpg",
        "is_available": 1,
        "sort_order": 3
    },
    {
        "name": "Мохіто",
        "category": "Коктейлі",
        "strength": "13% об.",
        "volume": "300 мл",
        "ingredients": "Кубинський світлий ром, свіжа перцева м'ята, стиглий лайм, тростинний цукор, содова, колотий лід",
        "description": "Квінтесенція гаванського літа. Терпкий аромат розім'ятої м'яти, соковитий лайм та ігриста содова, що приборкують міць білого рому. Неперевершений рятівник від спраги.",
        "image_path": "/static/images/drinks/mojito.jpg",
        "is_available": 1,
        "sort_order": 4
    },
    {
        "name": "Блакитна Лагуна (Блю Курасао)",
        "category": "Коктейлі",
        "strength": "16% об.",
        "volume": "250 мл",
        "ingredients": "Очищена горілка, лікер Блю Кюрасао, лимонний сік, прозорий цитрусовий лимонад",
        "description": "Магічний колір тихоокеанських хвиль. Лікер з гірких апельсинів сорту Лараха надає напою не тільки фірмового ультрамаринового сяйва, але й вишуканих цитрусово-квіткових нюансів.",
        "image_path": "/static/images/drinks/blue_lagoon.jpg",
        "is_available": 1,
        "sort_order": 5
    },
    {
        "name": "Куба Лібре",
        "category": "Коктейлі",
        "strength": "14% об.",
        "volume": "200 мл",
        "ingredients": "Золотий ром, карамельна кола, сік половинки лайма, лід",
        "description": "Історичний коктейль свободи, народжений на початку ХХ століття. Глибокі пряні та ванільні ноти рому ідеально збалансовані гострою кислинкою свіжого лайма.",
        "image_path": "/static/images/drinks/cuba_libre.jpg",
        "is_available": 1,
        "sort_order": 6
    },
    {
        "name": "Лондонський сухий джин",
        "category": "Міцні напої",
        "strength": "40% об.",
        "volume": "50 мл",
        "ingredients": "Дистилят на диких ялівцевих ягодах, коріандрі, дягелі та лимонній цедрі",
        "description": "Сухий, аристократичний та виразний напій багатовікової традиції. Подається чистим охолодженим або з льодом та твістом із цитрусової шкірки.",
        "image_path": "/static/images/drinks/gin_dry.jpg",
        "is_available": 1,
        "sort_order": 7
    },
    {
        "name": "Бехерівка лимонна (Lemond)",
        "category": "Лікери та бітери",
        "strength": "20% об.",
        "volume": "50 мл",
        "ingredients": "Трав'яний екстракт Бехерівки, натуральний сік та екстракт лимонів і апельсинів",
        "description": "Сучасна, легка інтерпретація карловарської класики. М'яка міцність, вибуховий цитрусовий аромат та делікатний пряний трав'яний шлейф. П'ється виключно крижаною.",
        "image_path": "/static/images/drinks/becherovka_lemond.jpg",
        "is_available": 1,
        "sort_order": 8
    },
    {
        "name": "Бехерівка (Becherovka Original)",
        "category": "Лікери та бітери",
        "strength": "38% об.",
        "volume": "50 мл",
        "ingredients": "Секретний збір із 20 карловарських трав і спецій, пом'якшена мінеральна вода",
        "description": "Вічний чеський еліксир, що не змінював рецептуру з 1807 року. Теплий оксамитовий смак із виразними нотами кориці, анісу, гвоздики та цілющих карпатських трав.",
        "image_path": "/static/images/drinks/becherovka.jpg",
        "is_available": 1,
        "sort_order": 9
    },
    {
        "name": "Єгермейстер (Jägermeister)",
        "category": "Лікери та бітери",
        "strength": "35% об.",
        "volume": "50 мл",
        "ingredients": "56 трав, коріння, квітів та фруктів, витримані 12 місяців у дубових бочках",
        "description": "Знаменитий німецький лікер-краутерлікьор із Вольфенбюттеля. Потужний, трав'янисто-пряний букет із нотами шафрану, імбиру, лакриці та цитрусової цедри. Подається у шотах при температурі -18°C.",
        "image_path": "/static/images/drinks/jagermeister.jpg",
        "is_available": 1,
        "sort_order": 10
    },
    {
        "name": "Бурбон (American Bourbon)",
        "category": "Міцні напої",
        "strength": "40% об.",
        "volume": "50 мл",
        "ingredients": "Кукурудзяне сусло (не менше 51%), ячмінний солод, жито, витримка в обпаленому білому дубі",
        "description": "Шляхетний дистилят американського Півдня. Багатий, маслянистий профіль із солодкими тонами ванілі, кленового сиропу, карамелі та димного обпаленого дерева.",
        "image_path": "/static/images/drinks/bourbon.jpg",
        "is_available": 1,
        "sort_order": 11
    }
]

DEFAULT_SETTINGS = {
    "bar_name": "МЕНЮ",
    "bar_tagline": "Офіційне меню закладу",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "telegram_enabled": "0"
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    # Drinks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        strength TEXT,
        volume TEXT,
        ingredients TEXT,
        description TEXT NOT NULL,
        image_path TEXT NOT NULL,
        is_available INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)
    
    # Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drink_name TEXT NOT NULL,
        table_number TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        comment TEXT,
        guest_name TEXT,
        payment_method TEXT DEFAULT 'Готівка',
        promocode TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new'
    )
    """)
    
    # Safe column additions if table already existed
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'Готівка'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN promocode TEXT")
    except Exception:
        pass
    
    # Feedback & Suggestions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feedback_type TEXT DEFAULT 'Відгук',
        guest_name TEXT,
        rating INTEGER,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Insert default settings if empty
    for k, v in DEFAULT_SETTINGS.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
    # Populate drinks if table is empty
    cursor.execute("SELECT COUNT(*) FROM drinks")
    count = cursor.fetchone()[0]
    if count == 0:
        for d in DEFAULT_DRINKS:
            cursor.execute("""
            INSERT INTO drinks (name, category, strength, volume, ingredients, description, image_path, is_available, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["name"], d["category"], d["strength"], d["volume"],
                d["ingredients"], d["description"], d["image_path"],
                d["is_available"], d["sort_order"]
            ))
            
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at", DB_PATH)
