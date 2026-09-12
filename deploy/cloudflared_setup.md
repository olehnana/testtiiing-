# Налаштування Cloudflare Tunnel на Raspberry Pi 5

**Cloudflare Tunnel (`cloudflared`)** дозволяє відкрити сайт усьому інтернету без білого IP, без відкриття портів на роутері та з безкоштовним автоматичним HTTPS (SSL).

---

## 1. Встановлення `cloudflared` на Raspberry Pi 5 (ARM64)

Підключіться до Raspberry Pi 5 по SSH і виконайте команди:

```bash
# Завантаження офіційного пакету для архітектури arm64 (Raspberry Pi 5)
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Встановлення deb-пакету
sudo dpkg -i cloudflared.deb

# Перевірка версії
cloudflared --version
```

---

## Варіант 1: Швидкий безкоштовний тунель (Без власного домену, за 30 секунд)

Якщо у вас ще немає власного домену, Cloudflare дає випадкову публічну адресу `https://*.trycloudflare.com`:

```bash
cloudflared tunnel --url http://localhost:8000
```

У консолі з'явиться посилання на кшталт:
`https://your-bar-newspaper-sample.trycloudflare.com`

Будь-хто в світі може відкрити це посилання зі свого смартфона!

---

## Варіант 2: Постійний тунель зі своїм доменом через веб-панель Cloudflare (Рекомендовано)

Це найнадійніший варіант, який працює завжди у фоні:

1. Зайдіть у безкоштовну панель [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/).
2. Перейдіть у розділ: **Networks** $\rightarrow$ **Tunnels** $\rightarrow$ натисніть **Add a tunnel**.
3. Оберіть тип **Cloudflared** $\rightarrow$ назвіть тунель (наприклад, `bar-pi5`).
4. На екрані оберіть вашу систему: **Debian 64-bit**.
5. Cloudflare згенерує одну готову команду зі спеціальним токеном. Просто скопіюйте її та вставте в термінал Raspberry Pi 5:
   ```bash
   sudo cloudflared service install eyJhIjoi...
   ```
6. У панелі Cloudflare на вкладці **Public Hostnames**:
   - Вкажіть ваш піддомен (наприклад, `menu.yourdomain.com`).
   - Service Type: `HTTP`.
   - URL: `localhost:8000`.
   - Натисніть **Save hostname**.

Після цього сайт вашого бару буде цілодобово доступний за захищеною адресою `https://menu.yourdomain.com` з будь-якого пристрою!
