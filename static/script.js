// --- Global State and Data Storage ---
let allData = [];
let selectedRegion = 'all';
let selectedYear = null;
let selectedWeek = null;
let selectedChartYear = null;
let selectedRegionalYear = null;
let selectedHeatYear = null;

// Chart and Map instances
let diseaseTrendChart;
let regionalChart;
let map;
let geojsonLayer;

// --- Main Initialization ---
document.addEventListener("DOMContentLoaded", function () {
  loadDataAndInitialize();
});

// Add this to your existing script.js file (at the end)

// --- BOT CHAT FUNCTIONALITY ---

// Add bot initialization to your existing DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
  loadDataAndInitialize();
  initializeBotChat(); // ✅ ADDED: Initialize bot functionality
});

// ✅ Bot Chat Initialization
function initializeBotChat() {
  const chatToggle = document.getElementById('chat-toggle-button');
  const chatPopup = document.getElementById('chat-popup');
  const closeBtn = document.getElementById('cp-close');
  const sendBtn = document.getElementById('cp-send');
  const chatInput = document.getElementById('cp-input');
  const chatBody = document.getElementById('cp-body');

  if (!chatToggle || !chatPopup) {
    console.error('❌ Chat elements not found in DOM');
    return;
  }

  console.log('✅ Initializing bot chat functionality');

  // Toggle chat popup
  chatToggle.addEventListener('click', function(e) {
    e.preventDefault();
    console.log('🤖 Bot button clicked');
    const isVisible = chatPopup.style.display === 'block' || chatPopup.getAttribute('aria-hidden') === 'false';
    
    if (isVisible) {
      closeChatPopup();
    } else {
      openChatPopup();
    }
  });

  // Close chat popup
  if (closeBtn) {
    closeBtn.addEventListener('click', closeChatPopup);
  }

  // Send message
  if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
  }

  // Send on Enter key
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Close on outside click
  chatPopup.addEventListener('click', function(e) {
    if (e.target === chatPopup) {
      closeChatPopup();
    }
  });
}

// ✅ Open Chat Popup
function openChatPopup() {
  const chatPopup = document.getElementById('chat-popup');
  const chatInput = document.getElementById('cp-input');
  
  if (chatPopup) {
    chatPopup.style.display = 'block';
    chatPopup.setAttribute('aria-hidden', 'false');
    
    // Focus on input
    if (chatInput) {
      setTimeout(() => chatInput.focus(), 100);
    }
    
    console.log('✅ Chat popup opened');
  }
}

// ✅ Close Chat Popup
function closeChatPopup() {
  const chatPopup = document.getElementById('chat-popup');
  
  if (chatPopup) {
    chatPopup.style.display = 'none';
    chatPopup.setAttribute('aria-hidden', 'true');
    console.log('✅ Chat popup closed');
  }
}

// ✅ Send Message Function
function sendMessage() {
  const chatInput = document.getElementById('cp-input');
  const chatBody = document.getElementById('cp-body');
  
  if (!chatInput || !chatBody) return;
  
  const message = chatInput.value.trim();
  if (!message) return;
  
  console.log('📤 Sending message:', message);
  
  // Add user message to chat
  addMessageToChat('user', message);
  
  // Clear input
  chatInput.value = '';
  
  // Show typing indicator
  showTypingIndicator();
  
  // Send to backend
  fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: message })
  })
  .then(response => {
    console.log('📡 Chat response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('📥 Chat response:', data);
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Add bot response
    if (data.response) {
      addMessageToChat('bot', data.response);
    } else {
      addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
    }
  })
  .catch(error => {
    console.error('❌ Chat error:', error);
    removeTypingIndicator();
    addMessageToChat('bot', 'Sorry, I\'m having trouble connecting. Please try again later.');
  });
}

// ✅ Add Message to Chat
function addMessageToChat(sender, message) {
  const chatBody = document.getElementById('cp-body');
  if (!chatBody) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `cp-msg ${sender}`;
  
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'cp-bubble';
  bubbleDiv.textContent = message;
  
  messageDiv.appendChild(bubbleDiv);
  chatBody.appendChild(messageDiv);
  
  // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;
  
  console.log(`✅ Added ${sender} message:`, message);
}

// ✅ Show Typing Indicator
function showTypingIndicator() {
  const chatBody = document.getElementById('cp-body');
  if (!chatBody) return;
  
  const typingDiv = document.createElement('div');
  typingDiv.className = 'cp-msg bot typing-indicator';
  typingDiv.id = 'typing-indicator';
  
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'cp-bubble';
  bubbleDiv.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
  
  typingDiv.appendChild(bubbleDiv);
  chatBody.appendChild(typingDiv);
  
  // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;
}

// ✅ Remove Typing Indicator
function removeTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

// ✅ Add CSS for chat popup (if not in your styles.css)
fdocument.addEventListener("DOMContentLoaded", function () {
  loadDataAndInitialize();
  initializeBotChat(); // ✅ ADDED: Initialize bot functionality
});

// ✅ Bot Chat Initialization
function initializeBotChat() {
  const chatToggle = document.getElementById('chat-toggle-button');
  const chatPopup = document.getElementById('chat-popup');
  const closeBtn = document.getElementById('cp-close');
  const sendBtn = document.getElementById('cp-send');
  const chatInput = document.getElementById('cp-input');
  const chatBody = document.getElementById('cp-body');

  if (!chatToggle || !chatPopup) {
    console.error('❌ Chat elements not found in DOM');
    return;
  }

  console.log('✅ Initializing bot chat functionality');

  // Toggle chat popup
  chatToggle.addEventListener('click', function(e) {
    e.preventDefault();
    console.log('🤖 Bot button clicked');
    const isVisible = chatPopup.style.display === 'block' || chatPopup.getAttribute('aria-hidden') === 'false';
    
    if (isVisible) {
      closeChatPopup();
    } else {
      openChatPopup();
    }
  });

  // Close chat popup
  if (closeBtn) {
    closeBtn.addEventListener('click', closeChatPopup);
  }

  // Send message
  if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
  }

  // Send on Enter key
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Close on outside click
  chatPopup.addEventListener('click', function(e) {
    if (e.target === chatPopup) {
      closeChatPopup();
    }
  });
}

// ✅ Open Chat Popup
function openChatPopup() {
  const chatPopup = document.getElementById('chat-popup');
  const chatInput = document.getElementById('cp-input');
  
  if (chatPopup) {
    chatPopup.style.display = 'block';
    chatPopup.setAttribute('aria-hidden', 'false');
    
    // Focus on input
    if (chatInput) {
      setTimeout(() => chatInput.focus(), 100);
    }
    
    console.log('✅ Chat popup opened');
  }
}

// ✅ Close Chat Popup
function closeChatPopup() {
  const chatPopup = document.getElementById('chat-popup');
  
  if (chatPopup) {
    chatPopup.style.display = 'none';
    chatPopup.setAttribute('aria-hidden', 'true');
    console.log('✅ Chat popup closed');
  }
}

// ✅ Send Message Function
function sendMessage() {
  const chatInput = document.getElementById('cp-input');
  const chatBody = document.getElementById('cp-body');
  
  if (!chatInput || !chatBody) return;
  
  const message = chatInput.value.trim();
  if (!message) return;
  
  console.log('📤 Sending message to Flask /chat endpoint:', message);
  
  // Add user message to chat
  addMessageToChat('user', message);
  
  // Clear input and disable send button
  chatInput.value = '';
  const sendBtn = document.getElementById('cp-send');
  if (sendBtn) sendBtn.disabled = true;
  
  // Show typing indicator
  showTypingIndicator();
  
  // Send to Flask backend - matches your app.py /chat route exactly
  fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({ message: message })
  })
  .then(response => {
    console.log('📡 Flask response status:', response.status, response.statusText);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('📥 Flask response data:', data);
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Re-enable send button
    if (sendBtn) sendBtn.disabled = false;
    
    // Add bot response - your Flask app returns { "response": "..." }
    if (data && data.response) {
      addMessageToChat('bot', data.response);
    } else {
      console.error('❌ Unexpected response format:', data);
      addMessageToChat('bot', 'Sorry, I received an unexpected response format.');
    }
  })
  .catch(error => {
    console.error('❌ Flask chat error:', error);
    removeTypingIndicator();
    
    // Re-enable send button
    if (sendBtn) sendBtn.disabled = false;
    
    // Show user-friendly error message
    if (error.message.includes('500')) {
      addMessageToChat('bot', 'Sorry, there was a server error. Please try again.');
    } else if (error.message.includes('404')) {
      addMessageToChat('bot', 'Chat service is not available right now.');
    } else {
      addMessageToChat('bot', 'Sorry, I\'m having trouble connecting. Please check your connection and try again.');
    }
  });
}

// ✅ Add Message to Chat
function addMessageToChat(sender, message) {
  const chatBody = document.getElementById('cp-body');
  if (!chatBody) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `cp-msg ${sender}`;
  
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'cp-bubble';
  bubbleDiv.textContent = message;
  
  messageDiv.appendChild(bubbleDiv);
  chatBody.appendChild(messageDiv);
  
  // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;
  
  console.log(`✅ Added ${sender} message:`, message);
}

// ✅ Show Typing Indicator
function showTypingIndicator() {
  const chatBody = document.getElementById('cp-body');
  if (!chatBody) return;
  
  const typingDiv = document.createElement('div');
  typingDiv.className = 'cp-msg bot typing-indicator';
  typingDiv.id = 'typing-indicator';
  
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'cp-bubble';
  bubbleDiv.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
  
  typingDiv.appendChild(bubbleDiv);
  chatBody.appendChild(typingDiv);
  
  // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;
}

// ✅ Remove Typing Indicator
function removeTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

// ✅ Add CSS for chat popup (if not in your styles.css)

// Initialize chat styles when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  addChatStyles();
});

console.log("✅ Bot chat functionality loaded");

// Initialize chat styles when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  addChatStyles();
});

console.log("✅ Bot chat functionality loaded");

// --- Data Loading and Processing ---
function loadDataAndInitialize() {
  fetch("/data")
    .then(response => {
      if (!response.ok) throw new Error("Could not fetch data from /data");
      return response.json();
    })
    .then(data => {
      console.log("Raw data from Supabase:", data.slice(0, 3));
      
      allData = data.map(d => ({
        year: parseInt(d.Year, 10),
        week: parseInt(d.Week, 10),
        area: d.Area?.trim() || "Unknown",
        disease: d.Disease?.trim() || "Unknown",
        cases: parseInt(d["No of cases"], 10) || 0,
        deaths: parseInt(d["No of deaths"], 10) || 0,
        uniqueId: d["Unique id"] || "",
        state: d.State || "",
        dateStart: d["Date of start"] || "",
        dateReporting: d["Date of reporting"] || ""
      }));

      console.log("Processed data:", allData.slice(0, 3));
      console.log(`Total records loaded: ${allData.length}`);
      
      // Debug: Show unique areas for map matching
      const uniqueAreas = [...new Set(allData.map(d => d.area))].filter(a => a !== "Unknown");
      console.log("🗺️ Unique areas in data:", uniqueAreas.slice(0, 10));

      populateFilters();
      initializeEventListeners();
      initMap();
      
      updateKeyIndicators();
      updateDiseaseChart();
      updateRegionalChart();
      updateMap();
    })
    .catch(error => {
      console.error("CRITICAL: Failed to load data:", error);
    });
}

// --- Populating UI Elements (Fixed for year sync) ---
function populateFilters() {
  const uniqueYears = [...new Set(allData.map(d => d.year))].filter(y => !isNaN(y)).sort((a, b) => b - a);
  console.log("Available years:", uniqueYears);

  const yearSelects = [
    document.getElementById("yearSelect"),
    document.getElementById("chartYearSelect"),
    document.getElementById("regionalYearSelect"),
    document.getElementById("heatYearSelect")
  ];

  yearSelects.forEach(sel => sel && (sel.innerHTML = ""));

  uniqueYears.forEach(year => {
    yearSelects.forEach(sel => {
      if (sel) {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        sel.appendChild(option);
      }
    });
  });

  // ✅ FIXED: Sync all year selects to same value and update visualizations
 if (uniqueYears.length > 0) {
    const defaultYear = uniqueYears[0];
    selectedYear = defaultYear;
    selectedChartYear = defaultYear;
    selectedRegionalYear = defaultYear;
    selectedHeatYear = defaultYear;

    yearSelects.forEach(sel => {
      if (sel) sel.value = defaultYear;
    });

    console.log(`🎯 Default year set to: ${defaultYear}`);

    // Immediately update all visualizations with default year
    updateKeyIndicators();
    updateDiseaseChart();
    updateRegionalChart();
    updateMap();
  }
  const uniqueWeeks = [...new Set(allData.map(d => d.week))].filter(w => !isNaN(w) && w > 0).sort((a, b) => a - b);
  const weekSelect = document.getElementById("weekSelect");
  if (weekSelect && uniqueWeeks.length > 0) {
    weekSelect.innerHTML = "";
    uniqueWeeks.forEach(week => {
      const option = document.createElement("option");
      option.value = week;
      option.textContent = "Week " + week;
      weekSelect.appendChild(option);
    });
    selectedWeek = uniqueWeeks[0];
    weekSelect.value = selectedWeek;
  }

  const uniqueAreas = [...new Set(allData.map(d => d.area))].filter(a => a && a !== "Unknown").sort();
  const regionSelect = document.getElementById("regionSelect");
  if (regionSelect) {
    regionSelect.innerHTML = '<option value="all">All Regions</option>';
    uniqueAreas.forEach(area => {
      const option = document.createElement("option");
      option.value = area;
      option.textContent = area;
      regionSelect.appendChild(option);
    });
  }
}

// --- Event Listeners Setup (Enhanced Debugging) ---
function initializeEventListeners() {
  const regionSelect = document.getElementById('regionSelect');
  if (regionSelect) regionSelect.addEventListener('change', e => {
    selectedRegion = e.target.value;
    console.log(`🔄 Region changed to: ${selectedRegion}`);
    updateKeyIndicators();
  });

  const yearSelect = document.getElementById('yearSelect');
  if (yearSelect) yearSelect.addEventListener('change', e => {
    selectedYear = parseInt(e.target.value);
    console.log(`🔄 Main year changed to: ${selectedYear}`);
    updateKeyIndicators();
  });

  const weekSelect = document.getElementById('weekSelect');
  if (weekSelect) weekSelect.addEventListener('change', e => {
    selectedWeek = parseInt(e.target.value);
    console.log(`🔄 Week changed to: ${selectedWeek}`);
    updateDiseaseChart();
    updateKeyIndicators();  // ✅ ADDED: Update key indicators on week change
  });

  const chartYearSelect = document.getElementById('chartYearSelect');
  if (chartYearSelect) chartYearSelect.addEventListener('change', e => {
    selectedChartYear = parseInt(e.target.value);
    console.log(`🔄 Chart year changed to: ${selectedChartYear}`);
    updateDiseaseChart();
  });

  const regionalYearSelect = document.getElementById('regionalYearSelect');
  if (regionalYearSelect) regionalYearSelect.addEventListener('change', e => {
    selectedRegionalYear = parseInt(e.target.value);
    console.log(`🔄 Regional year changed to: ${selectedRegionalYear}`);
    updateRegionalChart();
  });

  const heatYearSelect = document.getElementById('heatYearSelect');
  if (heatYearSelect) heatYearSelect.addEventListener('change', e => {
    selectedHeatYear = parseInt(e.target.value);
    console.log(`🔄 Heat map year changed to: ${selectedHeatYear}`);
    updateMap();
  });
}

// --- Key Indicator Update (Year-specific) ---
// --- Key Indicator Update (Year and Week specific) ---
function updateKeyIndicators() {
  if (!selectedYear || allData.length === 0) return;
  
  console.log(`📊 Calculating totals for year: ${selectedYear}, week: ${selectedWeek}, region: ${selectedRegion}`);
  
  const filteredData = allData.filter(d =>
    d.year === selectedYear &&
    (selectedWeek === null || d.week === selectedWeek) &&  // ✅ ADDED: Week filter
    (selectedRegion === 'all' || d.area === selectedRegion)
  );

  console.log(`📊 Filtered data: ${filteredData.length} rows for year ${selectedYear}, week ${selectedWeek}`);

  const totalCases = filteredData.reduce((sum, item) => sum + (item.cases || 0), 0);
  const totalCasesEl = document.querySelector('[data-id="total-cases"]');
  if (totalCasesEl) totalCasesEl.textContent = formatNumber(totalCases);

  const totalDeaths = filteredData.reduce((sum, item) => sum + (item.deaths || 0), 0);
  const totalDeathsEl = document.querySelector('[data-id="total-deaths"]');
  if (totalDeathsEl) totalDeathsEl.textContent = formatNumber(totalDeaths);

  console.log(`📊 Calculated totals: ${totalCases} cases, ${totalDeaths} deaths`);

  // Calculate top city by cases (for the selected year/week combination)
  const areaTotals = filteredData.reduce((acc, item) => {
    if (item.area && item.area !== "Unknown") {
      acc[item.area] = (acc[item.area] || 0) + item.cases;
    }
    return acc;
  }, {});

  let topCity = '–';
  let topCases = 0;
  for (const [area, cases] of Object.entries(areaTotals)) {
    if (cases > topCases) {
      topCity = area;
      topCases = cases;
    }
  }
  const topCityEl = document.querySelector('[data-id="top-city"]');
  if (topCityEl) {
    const displayText = topCity !== '–' ? 
      `${topCity} (${formatNumber(topCases)})` : 
      '–';
    topCityEl.textContent = displayText;
    
    // ✅ ADDED: Update title to show current filters
    const titleEl = document.querySelector('.key-indicators h3, .analytics-controls h3');
    if (titleEl) {
      const weekText = selectedWeek ? ` - Week ${selectedWeek}` : '';
      const regionText = selectedRegion !== 'all' ? ` - ${selectedRegion}` : '';
      titleEl.textContent = `Key Indicators ${selectedYear}${weekText}${regionText}`;
    }
  }
}
// --- Number Formatting Helper ---
function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toLocaleString();
}

// --- Disease Trend Chart (Fixed: Month-wise, straight lines, formatted) ---
function updateDiseaseChart() {
  console.log(`📈 Updating disease chart for year: ${selectedChartYear}`);
  
  if (!selectedChartYear || allData.length === 0) return;

  const ctx = document.getElementById('diseaseTrendChart');
  if (!ctx) return;

  if (diseaseTrendChart) {
    diseaseTrendChart.destroy();
    diseaseTrendChart = null;
  }

  const yearData = allData.filter(d => d.year === selectedChartYear);
  console.log(`📊 Chart data for ${selectedChartYear}: ${yearData.length} rows`);

  if (yearData.length === 0) {
    diseaseTrendChart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `No data for ${selectedChartYear}`
          }
        }
      }
    });
    return;
  }

  // Get top 5 diseases by total cases
  const diseaseCount = {};
  yearData.forEach(item => {
    if (item.disease && item.disease !== "Unknown") {
      diseaseCount[item.disease] = (diseaseCount[item.disease] || 0) + item.cases;
    }
  });

  const diseases = Object.entries(diseaseCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([disease]) => disease);

  console.log(`📊 Top diseases for ${selectedChartYear}:`, diseases);

  // Aggregate to monthly data
  const monthlyData = {};
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  monthNames.forEach((month, index) => monthlyData[month] = {});

  yearData.forEach(item => {
    // Approximate month from week (1-4=Jan, 5-8=Feb, etc.)
    const monthIndex = Math.min(11, Math.floor((item.week - 1) / 4));
    const monthName = monthNames[monthIndex];
    if (diseases.includes(item.disease)) {
      monthlyData[monthName][item.disease] = (monthlyData[monthName][item.disease] || 0) + item.cases;
    }
  });

  console.log(`📊 Monthly aggregated data:`, monthlyData);

  const datasets = diseases.map((disease, index) => ({
    label: disease,
    data: monthNames.map(month => monthlyData[month][disease] || 0),
    borderColor: `hsl(${index * 72}, 60%, 40%)`,
    backgroundColor: `hsla(${index * 72}, 70%, 50%, 0.1)`,
    tension: 0,  // ✅ Straight lines (no waves)
    fill: false  // ✅ No fill under lines
  }));

  console.log(`📊 Creating chart with ${datasets.length} datasets`);

  diseaseTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: monthNames,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `Disease Trends ${selectedChartYear}`
        },
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: formatNumber  // ✅ Format huge numbers
          }
        }
      }
    }
  });

  console.log("✅ Disease chart updated");
}

// --- Regional Chart (Year-specific, formatted) ---
function updateRegionalChart() {
  console.log(`📈 Updating regional chart for year: ${selectedRegionalYear}`);
  
  if (!selectedRegionalYear || allData.length === 0) return;

  const ctx = document.getElementById('regionalChart');
  if (!ctx) return;

  if (regionalChart) {
    regionalChart.destroy();
    regionalChart = null;
  }

  const yearData = allData.filter(d => d.year === selectedRegionalYear);
  console.log(`📊 Regional data for ${selectedRegionalYear}: ${yearData.length} rows`);

  if (yearData.length === 0) {
    regionalChart = new Chart(ctx, {
      type: 'bar',
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `No data for ${selectedRegionalYear}`
          }
        }
      }
    });
    return;
  }

  // Group by area and sum cases
  const areaTotals = {};
  yearData.forEach(item => {
    if (item.area && item.area !== "Unknown") {
      areaTotals[item.area] = (areaTotals[item.area] || 0) + item.cases;
    }
  });

  // Get top 5 areas
  const sortedAreas = Object.entries(areaTotals)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const labels = sortedAreas.map(([area]) => area);
  const data = sortedAreas.map(([, cases]) => cases);

  regionalChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Total Cases',
        data: data,
        backgroundColor: 'rgba(52, 152, 219, 0.8)',
        borderColor: 'rgba(52, 152, 219, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `Top 5 Districts by Cases ${selectedRegionalYear}`
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: formatNumber  // ✅ Format huge numbers
          }
        }
      }
    }
  });
}

// --- Map Functions (Fixed with point plotting) ---
function initMap() {
  const mapElement = document.getElementById('map');
  if (!mapElement) return;
  
  try {
    map = L.map('map').setView([19.7515, 75.7139], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    console.log("✅ Map initialized successfully");
  } catch (error) {
    console.error("❌ Map initialization error:", error);
  }
}

function updateMap() {
  if (!map || !selectedHeatYear) {
    console.log("❌ Map or selectedHeatYear not available");
    return;
  }
  
  console.log(`🗺️ Updating map for year: ${selectedHeatYear}`);
  
  fetch(`/map_data/${selectedHeatYear}`)
    .then(response => {
      console.log(`🗺️ Map data response status: ${response.status}`);
      return response.json();
    })
    .then(mapData => {
      console.log("🗺️ Map data received:", mapData);
      
      if (geojsonLayer) {
        map.removeLayer(geojsonLayer);
        geojsonLayer = null;
      }

      if (mapData.error) {
        console.error("❌ Map data error:", mapData.error);
        return;
      }

      if (!mapData.features || mapData.features.length === 0) {
        console.error("❌ No features in map data");
        return;
      }

      // Debug: Show what cases data we have
      const casesData = mapData.features.map(f => ({
        name: f.properties.district_display,
        cases: f.properties.cases
      }));
      console.log("🗺️ Cases by district:", casesData.slice(0, 10));

      const maxCases = Math.max(...mapData.features.map(f => f.properties.cases || 0));
      console.log(`🗺️ Max cases: ${maxCases}`);

      geojsonLayer = L.geoJSON(mapData, {
        // ✅ FIXED: Add pointToLayer for plotting points as circle markers
        pointToLayer: function (feature, latlng) {
          const cases = feature.properties.cases || 0;
          return L.circleMarker(latlng, {
            radius: Math.max(5, Math.min(20, cases / 100)),  // Size based on cases
            fillColor: cases > 0 ? 'red' : '#cccccc',
            color: 'white',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
          });
        },
        style: function (feature) {
          // For polygons (if any)
          const cases = feature.properties.cases || 0;
          const intensity = maxCases > 0 ? cases / maxCases : 0;
          return {
            fillColor: cases > 0 ? `hsl(${120 - intensity * 120}, 70%, 50%)` : '#cccccc',
            weight: 2,
            opacity: 1,
            color: 'white',
            fillOpacity: 0.7
          };
        },
        onEachFeature: (feature, layer) => {
          const props = feature.properties;
          layer.bindPopup(`
            <strong>${props.district_display || 'Unknown'}</strong><br>
            Cases: ${(props.cases || 0).toLocaleString()}<br>
            Year: ${selectedHeatYear}
          `);
        }
      }).addTo(map);

      console.log("✅ Map updated successfully");
    })
    .catch(error => {
      console.error("❌ Map data error:", error);
    });
}

// --- Rest of your code (chat, export, refresh) remains unchanged ---

// Add this to the bottom if needed
console.log("Script loaded successfully");
