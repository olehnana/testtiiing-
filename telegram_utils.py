import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(bot_token, chat_id, text):
    """
    Sends a message via Telegram Bot API using standard urllib.
    Returns (success: bool, error_message: str)
    """
    if not bot_token or not chat_id:
        return False, "Токен бота або ID чату не налаштовано"
        
    clean_token = bot_token.strip()
    clean_chat_id = str(chat_id).strip()
    url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
    
    payload = {
        "chat_id": clean_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'BarMenuApp/1.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            res_body = json.loads(resp.read().decode('utf-8'))
            if res_body.get('ok'):
                return True, "Повідомлення надіслано успішно!"
            else:
                return False, res_body.get('description', 'Помилка Telegram API')
    except urllib.error.HTTPError as e:
        err_text = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json.loads(err_text)
            return False, err_json.get('description', f"HTTP {e.code}")
        except:
            return False, f"HTTP Error {e.code}"
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return False, str(e)

def format_order_message(order):
    """
    Formats an order object into a clear Telegram message for the bartender.
    """
    lines = [
        "🛎 <b>НОВЕ ЗАМОВЛЕННЯ З САЙТУ!</b>",
        "────────────────────",
        f"🍸 <b>Напій:</b> {order.get('drink_name')}",
        f"🔢 <b>Кількість:</b> {order.get('quantity', 1)} шт.",
        f"📍 <b>Стіл / Місце:</b> {order.get('table_number')}",
    ]
    
    if order.get('guest_name'):
        lines.append(f"👤 <b>Гість:</b> {order.get('guest_name')}")
        
    if order.get('comment'):
        lines.append(f"💬 <b>Побажання:</b> <i>{order.get('comment')}</i>")
        
    if order.get('payment_method'):
        lines.append(f"💳 <b>Оплата:</b> {order.get('payment_method')}")
        
    if order.get('promocode'):
        lines.append(f"🎁 <b>Промокод:</b> <code>{order.get('promocode')}</code> (Знижка -100% — За рахунок закладу)")

    lines.append("────────────────────")
    lines.append("⏰ <i>Замовлення зафіксовано в системі</i>")
    
    return "\n".join(lines)
