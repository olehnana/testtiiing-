// Admin Dashboard scripts: AJAX toggle, modals, settings updates
function showToast(message) {
  let toast = document.getElementById('admin-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'admin-toast';
    toast.className = 'toast-msg';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

// Get drinks data from embedded JSON script
function getDrinksMap() {
  const dataEl = document.getElementById('drinks-data');
  if (!dataEl) return {};
  try {
    const list = JSON.parse(dataEl.textContent);
    const map = {};
    list.forEach(item => {
      map[item.id] = item;
    });
    return map;
  } catch (e) {
    console.error('Failed to parse drinks-data JSON:', e);
    return {};
  }
}

// Instant toggle availability
async function toggleDrinkAvailability(btn, drinkId) {
  btn.disabled = true;
  const originalText = btn.innerHTML;
  btn.innerHTML = '⏳ Оновлюємо...';

  try {
    const res = await fetch(`/admin/api/toggle/${drinkId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const data = await res.json();
    if (data.success) {
      if (data.is_available === 1) {
        btn.className = 'toggle-stock-btn in-stock';
        btn.innerHTML = '✓ Є В НАЯВНОСТІ';
      } else {
        btn.className = 'toggle-stock-btn out-stock';
        btn.innerHTML = '✕ РОЗПРОДАНО';
      }
      showToast(data.message);
    } else {
      alert('Помилка: ' + (data.error || 'Не вдалося оновити'));
      btn.innerHTML = originalText;
    }
  } catch (err) {
    console.error(err);
    alert('Помилка мережі при спробі змінити статус');
    btn.innerHTML = originalText;
  } finally {
    btn.disabled = false;
  }
}

// Delete drink confirmation
async function deleteDrink(drinkId, drinkName) {
  if (!confirm(`Ви дійсно бажаєте видалити позицію «${drinkName}» з прейскуранту?`)) {
    return;
  }

  try {
    const res = await fetch(`/admin/api/delete/${drinkId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      const row = document.getElementById(`drink-row-${drinkId}`);
      if (row) row.remove();
    } else {
      alert('Помилка: ' + (data.error || 'Не вдалося видалити'));
    }
  } catch (err) {
    alert('Помилка мережі при видаленні');
  }
}

// Modal open for Edit / Add
function openDrinkModal(drink = null) {
  const modal = document.getElementById('drinkModal');
  const title = document.getElementById('modalTitle');
  const form = document.getElementById('drinkForm');

  if (drink) {
    title.textContent = 'Редагувати позицію: ' + drink.name;
    document.getElementById('form-id').value = drink.id;
    document.getElementById('form-name').value = drink.name;
    document.getElementById('form-category').value = drink.category;
    document.getElementById('form-strength').value = drink.strength || '';
    document.getElementById('form-volume').value = drink.volume || '';
    document.getElementById('form-ingredients').value = drink.ingredients || '';
    document.getElementById('form-description').value = drink.description || '';
    document.getElementById('form-image').value = drink.image_path || '';
    document.getElementById('form-available').checked = drink.is_available === 1;
    document.getElementById('form-sort').value = drink.sort_order || 0;
  } else {
    title.textContent = 'Додати новий напій до прейскуранту';
    form.reset();
    document.getElementById('form-id').value = '';
    document.getElementById('form-available').checked = true;
    document.getElementById('form-sort').value = 100;
  }

  modal.style.display = 'flex';
}

function closeDrinkModal() {
  document.getElementById('drinkModal').style.display = 'none';
}

// Initialize event listeners when DOM loads
document.addEventListener('DOMContentLoaded', function () {
  const drinksMap = getDrinksMap();

  // Add drink button
  const addBtn = document.getElementById('btn-add-drink');
  if (addBtn) {
    addBtn.addEventListener('click', () => openDrinkModal(null));
  }

  // Modal close buttons
  const closeBtn = document.getElementById('btn-close-modal');
  if (closeBtn) {
    closeBtn.addEventListener('click', closeDrinkModal);
  }
  const cancelBtn = document.getElementById('btn-cancel-modal');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeDrinkModal);
  }

  // Event delegation on table
  const table = document.getElementById('admin-drinks-table');
  if (table) {
    table.addEventListener('click', function (e) {
      const target = e.target.closest('[data-action]');
      if (!target) return;

      const action = target.getAttribute('data-action');
      const id = parseInt(target.getAttribute('data-id'), 10);

      if (action === 'toggle') {
        toggleDrinkAvailability(target, id);
      } else if (action === 'edit') {
        const drink = drinksMap[id];
        if (drink) {
          openDrinkModal(drink);
        } else {
          console.error('Drink not found in map for id:', id);
        }
      } else if (action === 'delete') {
        const name = target.getAttribute('data-name') || 'напій';
        deleteDrink(id, name);
      }
    });
  }

  // Submit drink form via AJAX
  const form = document.getElementById('drinkForm');
  if (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const formData = new FormData(form);

      try {
        const res = await fetch('/admin/api/save_drink', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message);
          setTimeout(() => {
            window.location.reload();
          }, 700);
        } else {
          alert('Помилка: ' + (data.error || 'Не вдалося зберегти'));
        }
      } catch (err) {
        alert('Помилка мережі при збереженні');
      }
    });
  }
});
