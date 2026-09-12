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
  const monobankBox = document.getElementById('monobank-info-box');
  const promoInput = document.getElementById('order-promocode');
  const btnApplyPromo = document.getElementById('btn-apply-promo');
  const promoStatus = document.getElementById('promo-status-msg');

  function updatePaymentVisibility() {
    const selectedMethod = document.querySelector('input[name="payment_method_choice"]:checked');
    if (monobankBox) {
      if (selectedMethod && selectedMethod.value === 'Картка (Монобанка)') {
        monobankBox.style.display = 'block';
      } else {
        monobankBox.style.display = 'none';
      }
    }
  }

  function checkPromoCode() {
    if (!promoInput || !promoStatus) return;
    const code = promoInput.value.trim().toUpperCase();
    if (code === 'РОДИНА') {
      promoStatus.style.display = 'block';
      promoStatus.style.backgroundColor = '#e8f5e9';
      promoStatus.style.border = '1px solid #4caf50';
      promoStatus.style.color = '#1b5e20';
      promoStatus.innerHTML = '🎉 Промокод <b>РОДИНА</b> активовано! Знижка <b>-100%</b> (За рахунок закладу) 🎁';
    } else if (code.length > 0) {
      promoStatus.style.display = 'block';
      promoStatus.style.backgroundColor = '#ffebee';
      promoStatus.style.border = '1px solid #ef5350';
      promoStatus.style.color = '#c62828';
      promoStatus.textContent = '❌ Невірний або недійсний промокод';
    } else {
      promoStatus.style.display = 'none';
      promoStatus.innerHTML = '';
    }
  }

  // Radio button listeners for payment
  const paymentRadios = document.querySelectorAll('input[name="payment_method_choice"]');
  paymentRadios.forEach(radio => {
    radio.addEventListener('change', updatePaymentVisibility);
  });

  if (btnApplyPromo) {
    btnApplyPromo.addEventListener('click', checkPromoCode);
  }
  if (promoInput) {
    promoInput.addEventListener('input', function () {
      if (promoInput.value.trim().toUpperCase() === 'РОДИНА') {
        checkPromoCode();
      }
    });
    promoInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        checkPromoCode();
      }
    });
  }

  function openOrderModal(drinkName, volume) {
    if (!orderModal) return;
    if (orderDrinkName) orderDrinkName.value = drinkName;
    if (orderDrinkDisplay) orderDrinkDisplay.textContent = volume ? `${drinkName} (${volume})` : drinkName;
    if (orderForm) orderForm.reset();
    if (orderDrinkName) orderDrinkName.value = drinkName;
    
    const qtyInput = document.getElementById('order-qty');
    if (qtyInput) qtyInput.value = 1;
    
    // Default radio
    const cashRadio = document.querySelector('input[name="payment_method_choice"][value="Готівка"]');
    if (cashRadio) cashRadio.checked = true;
    updatePaymentVisibility();

    if (promoStatus) {
      promoStatus.style.display = 'none';
      promoStatus.innerHTML = '';
    }

    orderModal.style.display = 'flex';
  }

  function closeOrderModal() {
    if (orderModal) {
      orderModal.style.display = 'none';
    }
  }

  // Expose globally
  window.openOrderModal = openOrderModal;
  window.closeOrderModal = closeOrderModal;

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

      let chosenPayment = 'Готівка';
      const selectedRadio = document.querySelector('input[name="payment_method_choice"]:checked');
      if (selectedRadio) {
        chosenPayment = selectedRadio.value;
      }

      const promocodeVal = (promoInput ? promoInput.value.trim() : '');
      if (promocodeVal.toUpperCase() === 'РОДИНА') {
        chosenPayment = 'Промокод РОДИНА (-100% Безкоштовно)';
      }

      const payload = {
        drink_name: orderDrinkName.value,
        table_number: document.getElementById('order-table').value.trim(),
        quantity: parseInt(document.getElementById('order-qty').value, 10) || 1,
        guest_name: document.getElementById('order-guest').value.trim(),
        comment: document.getElementById('order-comment').value.trim(),
        payment_method: chosenPayment,
        promocode: promocodeVal
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

  // ================= FEEDBACK & SUGGESTIONS MODAL LOGIC =================
  const feedbackModal = document.getElementById('feedbackModal');
  const feedbackForm = document.getElementById('feedbackForm');
  const btnCloseFeedback = document.getElementById('btn-close-feedback');
  const btnCancelFeedback = document.getElementById('btn-cancel-feedback');
  const btnSubmitFeedback = document.getElementById('btn-submit-feedback');

  function openFeedbackModal() {
    if (feedbackModal) {
      if (feedbackForm) feedbackForm.reset();
      feedbackModal.style.display = 'flex';
    }
  }

  function closeFeedbackModal() {
    if (feedbackModal) {
      feedbackModal.style.display = 'none';
    }
  }

  window.openFeedbackModal = openFeedbackModal;
  window.closeFeedbackModal = closeFeedbackModal;

  if (btnCloseFeedback) btnCloseFeedback.addEventListener('click', closeFeedbackModal);
  if (btnCancelFeedback) btnCancelFeedback.addEventListener('click', closeFeedbackModal);

  if (feedbackForm) {
    feedbackForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      btnSubmitFeedback.disabled = true;
      const originalText = btnSubmitFeedback.textContent;
      btnSubmitFeedback.textContent = 'Надсилаємо...';

      const typeChoice = document.querySelector('input[name="feedback_type_choice"]:checked');
      const ratingChoice = document.querySelector('input[name="feedback_rating_val"]:checked');

      const payload = {
        feedback_type: typeChoice ? typeChoice.value : 'Відгук',
        guest_name: document.getElementById('feedback-guest').value.trim(),
        rating: ratingChoice ? parseInt(ratingChoice.value, 10) : 5,
        message: document.getElementById('feedback-msg').value.trim()
      };

      try {
        const res = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          closeFeedbackModal();
          alert('✓ ' + data.message);
        } else {
          alert('Помилка: ' + (data.error || 'Не вдалося надіслати відгук'));
        }
      } catch (err) {
        alert('Помилка мережі при відправці відгуку.');
      } finally {
        btnSubmitFeedback.disabled = false;
        btnSubmitFeedback.textContent = originalText;
      }
    });
  }
});

