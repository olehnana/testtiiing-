// Newspaper interactive script: filtering, search, order modal
document.addEventListener('DOMContentLoaded', function () {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const drinkCards = document.querySelectorAll('.drink-card');
  const searchInput = document.getElementById('search-input');

  let currentCategory = 'all';
  let searchQuery = '';

  function filterCards() {
    drinkCards.forEach(card => {
      const category = card.getAttribute('data-category');
      const isAvailable = card.getAttribute('data-available') === '1';
      const name = (card.getAttribute('data-name') || '').toLowerCase();
      const ingredients = (card.getAttribute('data-ingredients') || '').toLowerCase();
      const description = (card.getAttribute('data-desc') || '').toLowerCase();

      let categoryMatch = false;
      if (currentCategory === 'all') {
        categoryMatch = true;
      } else if (currentCategory === 'available') {
        categoryMatch = isAvailable;
      } else if (currentCategory === category) {
        categoryMatch = true;
      }

      let searchMatch = true;
      if (searchQuery) {
        searchMatch = name.includes(searchQuery) ||
                      ingredients.includes(searchQuery) ||
                      description.includes(searchQuery);
      }

      card.style.display = (categoryMatch && searchMatch) ? 'flex' : 'none';
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      currentCategory = this.getAttribute('data-filter');
      filterCards();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', function (e) {
      searchQuery = e.target.value.trim().toLowerCase();
      filterCards();
    });
  }

  // ================= ORDER MODAL LOGIC =================
  const orderModal = document.getElementById('orderModal');
  const orderForm = document.getElementById('orderForm');
  const orderDrinkName = document.getElementById('order-drink-name');
  const orderDrinkDisplay = document.getElementById('order-drink-display');
  const btnCloseOrder = document.getElementById('btn-close-order');
  const btnCancelOrder = document.getElementById('btn-cancel-order');
  const btnSubmitOrder = document.getElementById('btn-submit-order');

  function openOrderModal(drinkName, volume) {
    if (!orderModal) return;
    orderDrinkName.value = drinkName;
    orderDrinkDisplay.textContent = volume ? `${drinkName} (${volume})` : drinkName;
    orderForm.reset();
    orderDrinkName.value = drinkName;
    document.getElementById('order-qty').value = 1;
    orderModal.style.display = 'flex';
  }

  function closeOrderModal() {
    if (orderModal) {
      orderModal.style.display = 'none';
    }
  }

  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.btn-order-trigger');
    if (trigger) {
      const name = trigger.getAttribute('data-name');
      const volume = trigger.getAttribute('data-volume') || '';
      openOrderModal(name, volume);
    }
  });

  if (btnCloseOrder) btnCloseOrder.addEventListener('click', closeOrderModal);
  if (btnCancelOrder) btnCancelOrder.addEventListener('click', closeOrderModal);

  if (orderForm) {
    orderForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      btnSubmitOrder.disabled = true;
      const originalText = btnSubmitOrder.textContent;
      btnSubmitOrder.textContent = 'Відправляємо...';

      const payload = {
        drink_name: orderDrinkName.value,
        table_number: document.getElementById('order-table').value.trim(),
        quantity: parseInt(document.getElementById('order-qty').value, 10) || 1,
        guest_name: document.getElementById('order-guest').value.trim(),
        comment: document.getElementById('order-comment').value.trim()
      };

      try {
        const res = await fetch('/api/order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          closeOrderModal();
          alert('✓ ' + data.message);
        } else {
          alert('Помилка: ' + (data.error || 'Не вдалося надіслати замовлення'));
        }
      } catch (err) {
        alert('Помилка мережі при оформленні замовлення.');
      } finally {
        btnSubmitOrder.disabled = false;
        btnSubmitOrder.textContent = originalText;
      }
    });
  }
});
