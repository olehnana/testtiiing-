// Newspaper interactive script: filtering, search, dynamic counts
document.addEventListener('DOMContentLoaded', function () {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const drinkCards = document.querySelectorAll('.drink-card');
  const searchInput = document.getElementById('search-input');
  const visibleCountEl = document.getElementById('visible-count');

  let currentCategory = 'all';
  let searchQuery = '';

  function filterCards() {
    let visibleCount = 0;

    drinkCards.forEach(card => {
      const category = card.getAttribute('data-category');
      const isAvailable = card.getAttribute('data-available') === '1';
      const name = (card.getAttribute('data-name') || '').toLowerCase();
      const ingredients = (card.getAttribute('data-ingredients') || '').toLowerCase();
      const description = (card.getAttribute('data-desc') || '').toLowerCase();

      // Check category filter
      let categoryMatch = false;
      if (currentCategory === 'all') {
        categoryMatch = true;
      } else if (currentCategory === 'available') {
        categoryMatch = isAvailable;
      } else if (currentCategory === category) {
        categoryMatch = true;
      }

      // Check search filter
      let searchMatch = true;
      if (searchQuery) {
        searchMatch = name.includes(searchQuery) ||
                      ingredients.includes(searchQuery) ||
                      description.includes(searchQuery);
      }

      if (categoryMatch && searchMatch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (visibleCountEl) {
      visibleCountEl.textContent = visibleCount;
    }
  }

  // Filter button click handler
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      currentCategory = this.getAttribute('data-filter');
      filterCards();
    });
  });

  // Search input handler
  if (searchInput) {
    searchInput.addEventListener('input', function (e) {
      searchQuery = e.target.value.trim().toLowerCase();
      filterCards();
    });
  }
});
