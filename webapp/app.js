// Telegram Web App Client Logic
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

let allServices = [];
let currentCurrency = 'INR';
let usdRate = 85.0;
let selectedService = null;

const themeColors = {
  BLUE: { primary: '#2b92e4', hover: '#1e7bc6', shadow: 'rgba(43, 146, 228, 0.35)' },
  PURPLE: { primary: '#9b51e0', hover: '#7b2cbf', shadow: 'rgba(155, 81, 224, 0.35)' },
  GREEN: { primary: '#27ae60', hover: '#219653', shadow: 'rgba(39, 174, 96, 0.35)' },
  GOLD: { primary: '#e67e22', hover: '#d35400', shadow: 'rgba(230, 126, 34, 0.35)' },
  RED: { primary: '#e74c3c', hover: '#c0392b', shadow: 'rgba(231, 76, 60, 0.35)' }
};

// DOM Elements
const servicesListEl = document.getElementById('servicesList');
const searchInput = document.getElementById('searchInput');
const currencyToggleBtn = document.getElementById('currencyToggleBtn');
const currencyFlag = document.getElementById('currencyFlag');
const currencyText = document.getElementById('currencyText');

const modal = document.getElementById('serviceModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalTitle = document.getElementById('modalTitle');
const modalPrice = document.getElementById('modalPrice');
const modalDuration = document.getElementById('modalDuration');
const modalDesc = document.getElementById('modalDesc');
const orderRequirements = document.getElementById('orderRequirements');
const submitOrderBtn = document.getElementById('submitOrderBtn');
const orderStatusMsg = document.getElementById('orderStatusMsg');

// Apply Theme
function applyTheme(themeKey) {
  const theme = themeColors[themeKey] || themeColors.BLUE;
  document.documentElement.style.setProperty('--primary-color', theme.primary);
  document.documentElement.style.setProperty('--primary-hover', theme.hover);
  document.documentElement.style.setProperty('--primary-shadow', theme.shadow);
}

// Format Price
function formatPrice(priceInr) {
  if (currentCurrency === 'USD') {
    const usd = priceInr / usdRate;
    return `$${usd.toFixed(2)}`;
  }
  return `₹${Number(priceInr).toLocaleString('en-IN')}`;
}

// Render Services List (Solid Buttons matching screenshot)
function renderServices(services) {
  if (!services || services.length === 0) {
    servicesListEl.innerHTML = '<div class="loading-state"><p>No services found.</p></div>';
    return;
  }

  servicesListEl.innerHTML = '';
  services.forEach((service, index) => {
    const btn = document.createElement('button');
    btn.className = 'service-btn';
    
    // Highlight one item randomly or for special styling (just like screenshot green bar)
    if (index === 4) {
      btn.classList.add('highlight');
    }

    const titleSpan = document.createElement('span');
    titleSpan.className = 'service-btn-title';
    titleSpan.textContent = service.name;

    const priceSpan = document.createElement('span');
    priceSpan.className = 'service-btn-price';
    priceSpan.textContent = formatPrice(service.price);

    btn.appendChild(titleSpan);
    btn.appendChild(priceSpan);

    btn.addEventListener('click', () => openModal(service));
    servicesListEl.appendChild(btn);
  });
}

// Open Order Modal
function openModal(service) {
  selectedService = service;
  modalTitle.textContent = service.name;
  modalPrice.textContent = formatPrice(service.price);
  modalDuration.textContent = `⏱️ ${service.duration}`;
  modalDesc.textContent = service.description;
  orderRequirements.value = '';
  orderStatusMsg.className = 'status-msg hidden';
  orderStatusMsg.textContent = '';
  submitOrderBtn.disabled = false;
  submitOrderBtn.textContent = '⚡ Submit Order Now';
  modal.classList.remove('hidden');
}

// Close Modal
function closeModal() {
  modal.classList.add('hidden');
  selectedService = null;
}

modalCloseBtn.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});

// Toggle Currency
currencyToggleBtn.addEventListener('click', () => {
  if (currentCurrency === 'INR') {
    currentCurrency = 'USD';
    currencyFlag.textContent = '🌍';
    currencyText.textContent = 'USD ($)';
  } else {
    currentCurrency = 'INR';
    currencyFlag.textContent = '🇮🇳';
    currencyText.textContent = 'INR (₹)';
  }
  renderServices(getFilteredServices());
  if (selectedService) {
    modalPrice.textContent = formatPrice(selectedService.price);
  }
});

// Search Filter
function getFilteredServices() {
  const query = searchInput.value.toLowerCase().trim();
  if (!query) return allServices;
  return allServices.filter(s => 
    s.name.toLowerCase().includes(query) || 
    s.description.toLowerCase().includes(query)
  );
}

searchInput.addEventListener('input', () => {
  renderServices(getFilteredServices());
});

// Submit Order via API
submitOrderBtn.addEventListener('click', async () => {
  if (!selectedService) return;

  const requirements = orderRequirements.value.trim();
  if (requirements.length < 3) {
    orderStatusMsg.className = 'status-msg error';
    orderStatusMsg.textContent = '⚠️ Please enter brief project requirements.';
    return;
  }

  submitOrderBtn.disabled = true;
  submitOrderBtn.textContent = '⏳ Processing...';

  const user = tg?.initDataUnsafe?.user || { id: 0, first_name: 'Guest' };

  try {
    const response = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user.id,
        username: user.username || null,
        full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Telegram User',
        service_id: selectedService.id,
        requirements: requirements,
        currency: currentCurrency
      })
    });

    const result = await response.json();

    if (result.success) {
      orderStatusMsg.className = 'status-msg success';
      orderStatusMsg.textContent = `🎉 Order #${result.order_id} Placed Successfully! Check your Telegram chat.`;
      
      // If run inside Telegram WebApp, notify or close
      if (tg) {
        tg.HapticFeedback?.notificationOccurred('success');
        setTimeout(() => {
          tg.close();
        }, 2200);
      }
    } else {
      throw new Error(result.error || 'Failed to place order.');
    }
  } catch (err) {
    orderStatusMsg.className = 'status-msg error';
    orderStatusMsg.textContent = `❌ ${err.message}`;
    submitOrderBtn.disabled = false;
    submitOrderBtn.textContent = '⚡ Submit Order Now';
  }
});

// Initial Data Fetch
async function initApp() {
  try {
    // 1. Fetch Theme
    const themeRes = await fetch('/api/theme');
    const themeData = await themeRes.json();
    if (themeData.theme) {
      applyTheme(themeData.theme);
    }
    if (themeData.usd_rate) {
      usdRate = themeData.usd_rate;
    }

    // 2. Fetch Services
    const servicesRes = await fetch('/api/services');
    const servicesData = await servicesRes.json();
    allServices = servicesData.services || [];
    renderServices(allServices);

  } catch (err) {
    console.error('Failed to load store data:', err);
    servicesListEl.innerHTML = '<div class="loading-state"><p>⚠️ Failed to load services. Please retry.</p></div>';
  }
}

initApp();
