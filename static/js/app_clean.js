/**
 * Restaurant AI - Enhanced JavaScript Application
 * 
 * Features:
 * - Clickable avatar to activate voice
 * - Speech interruption capability
 * - Warm, casual AI interactions
 * - Cleaner, more sophisticated UI
 */

// Application state
const AppState = {
    menuItems: [],
    filteredItems: [],
    currentCategory: 'all',
    dietaryFilters: {
        vegetarian: false,
        vegan: false,
        glutenFree: false
    },
    isListening: false,
    isSpeaking: false,
    speechRecognition: null,
    speechSynthesis: window.speechSynthesis,
    currentUtterance: null
};

// DOM elements
const DOM = {
    menuContainer: document.getElementById('menu-items'),
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    voiceBtn: document.getElementById('voice-btn'),
    voiceControls: document.getElementById('voice-controls'),
    aiAvatar: document.getElementById('ai-avatar'),
    aiStatus: document.getElementById('ai-status'),
    modal: document.getElementById('menu-modal'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.querySelector('.modal-close'),
    filterBtns: document.querySelectorAll('.filter-btn'),
    dietaryCheckboxes: {
        vegetarian: document.getElementById('vegetarian-filter'),
        vegan: document.getElementById('vegan-filter'),
        glutenFree: document.getElementById('gluten-free-filter')
    },
    quickQuestions: document.querySelectorAll('.quick-question')
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('🍽️ Restaurant AI starting...');
    initializeSpeechRecognition();
    loadMenuItems();
    setupEventListeners();
    
    // Load voices when they become available
    if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = () => {
            const voices = window.speechSynthesis.getVoices();
            console.log(`Loaded ${voices.length} voices`);
        };
        
        // Trigger voice loading
        window.speechSynthesis.getVoices();
    }
    
    console.log('✅ Ready to serve!');
});

// Speech recognition setup
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        AppState.speechRecognition = new SpeechRecognition();
        
        AppState.speechRecognition.continuous = true;  // Allow continuous listening
        AppState.speechRecognition.interimResults = true;
        AppState.speechRecognition.lang = 'en-US';
        
        AppState.speechRecognition.onstart = () => {
            AppState.isListening = true;
            DOM.voiceBtn.classList.add('listening');
            DOM.aiStatus.classList.add('listening');
            stopSpeaking(); // Stop AI speech when user starts talking
        };
        
        AppState.speechRecognition.onend = () => {
            AppState.isListening = false;
            DOM.voiceBtn.classList.remove('listening');
            DOM.aiStatus.classList.remove('listening');
            DOM.voiceControls.classList.remove('visible');
        };
        
        AppState.speechRecognition.onresult = (event) => {
            const last = event.results.length - 1;
            const transcript = event.results[last][0].transcript;
            
            // Show interim results in input
            if (!event.results[last].isFinal) {
                DOM.chatInput.value = transcript;
            } else {
                // Final result - send message
                sendMessage(transcript);
                if (AppState.isListening) {
                    AppState.speechRecognition.stop();
                }
            }
        };
        
        AppState.speechRecognition.onerror = (event) => {
            console.error('Speech error:', event.error);
            AppState.isListening = false;
            DOM.voiceBtn.classList.remove('listening');
            DOM.aiStatus.classList.remove('listening');
            DOM.voiceControls.classList.remove('visible');
        };
    } else {
        DOM.voiceBtn.style.display = 'none';
    }
}

// Event listeners
function setupEventListeners() {
    // Avatar click to show microphone
    DOM.aiAvatar.addEventListener('click', () => {
        DOM.aiAvatar.classList.add('active');
        DOM.voiceControls.classList.toggle('visible');
        
        // Auto-start listening when avatar is clicked
        if (DOM.voiceControls.classList.contains('visible') && !AppState.isListening) {
            toggleVoice();
        }
    });
    
    // Voice button
    DOM.voiceBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleVoice();
    });
    
    // Stop speech when user clicks anywhere
    document.addEventListener('click', () => {
        if (AppState.isSpeaking) {
            stopSpeaking();
        }
    });
    
    // Chat input
    DOM.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(DOM.chatInput.value);
        }
    });
    
    DOM.sendBtn.addEventListener('click', () => {
        sendMessage(DOM.chatInput.value);
    });
    
    // Category filters
    DOM.filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            DOM.filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AppState.currentCategory = btn.dataset.category;
            filterMenuItems();
        });
    });
    
    // Dietary filters
    Object.entries(DOM.dietaryCheckboxes).forEach(([key, checkbox]) => {
        checkbox.addEventListener('change', () => {
            AppState.dietaryFilters[key] = checkbox.checked;
            filterMenuItems();
        });
    });
    
    // Quick questions
    DOM.quickQuestions.forEach(btn => {
        btn.addEventListener('click', () => {
            sendMessage(btn.dataset.question);
        });
    });
    
    // Modal
    DOM.modalClose.addEventListener('click', closeModal);
    DOM.modal.addEventListener('click', (e) => {
        if (e.target === DOM.modal) {
            closeModal();
        }
    });
}

// Toggle voice recognition
function toggleVoice() {
    if (AppState.isListening) {
        AppState.speechRecognition.stop();
    } else {
        stopSpeaking(); // Stop any ongoing speech
        AppState.speechRecognition.start();
    }
}

// Stop speaking
function stopSpeaking() {
    if (AppState.isSpeaking && AppState.currentUtterance) {
        AppState.speechSynthesis.cancel();
        AppState.isSpeaking = false;
        AppState.currentUtterance = null;
    }
}

// Load menu items
async function loadMenuItems() {
    try {
        const response = await fetch('/api/menu');
        const data = await response.json();
        
        if (data.success) {
            AppState.menuItems = data.items;
            AppState.filteredItems = data.items;
            renderMenuItems();
        }
    } catch (error) {
        console.error('Error loading menu:', error);
        DOM.menuContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Oops! Couldn't load the menu. Please refresh the page.</p>
            </div>
        `;
    }
}

// Filter menu items
function filterMenuItems() {
    AppState.filteredItems = AppState.menuItems.filter(item => {
        // Category filter
        if (AppState.currentCategory !== 'all' && item.category !== AppState.currentCategory) {
            return false;
        }
        
        // Dietary filters
        if (AppState.dietaryFilters.vegetarian && !item.vegetarian) return false;
        if (AppState.dietaryFilters.vegan && !item.vegan) return false;
        if (AppState.dietaryFilters.glutenFree && !item.gluten_free) return false;
        
        return true;
    });
    
    renderMenuItems();
}

// Render menu items
function renderMenuItems() {
    if (AppState.filteredItems.length === 0) {
        DOM.menuContainer.innerHTML = `
            <div class="no-items">
                <i class="fas fa-search"></i>
                <p>No items match your filters</p>
            </div>
        `;
        return;
    }
    
    const html = AppState.filteredItems.map(item => `
        <div class="menu-item" data-id="${item.id}" onclick="showMenuItem(${item.id})">
            <div class="menu-item-header">
                <h3>${item.name}</h3>
                <span class="menu-item-price">$${item.price.toFixed(2)}</span>
            </div>
            <p class="menu-item-description">${item.description}</p>
            <div class="menu-item-details">
                <span class="prep-time"><i class="fas fa-clock"></i> ${item.prep_time}</span>
                <span class="calories"><i class="fas fa-fire"></i> ${item.calories} cal</span>
            </div>
            <div class="menu-item-tags">
                ${item.vegetarian ? '<span class="menu-tag vegetarian">Vegetarian</span>' : ''}
                ${item.vegan ? '<span class="menu-tag vegan">Vegan</span>' : ''}
                ${item.gluten_free ? '<span class="menu-tag gluten-free">Gluten-Free</span>' : ''}
                ${item.spice_level > 2 ? `<span class="menu-tag spicy">Spicy (${item.spice_level}/5)</span>` : ''}
            </div>
        </div>
    `).join('');
    
    DOM.menuContainer.innerHTML = html;
}

// Show menu item details
function showMenuItem(itemId) {
    const item = AppState.menuItems.find(i => i.id === itemId);
    if (!item) return;
    
    const html = `
        <div class="modal-item-detail">
            <h2>${item.name}</h2>
            <p class="item-price">$${item.price.toFixed(2)}</p>
            
            <div class="item-description">
                <p>${item.description}</p>
            </div>
            
            ${item.chef_notes ? `
                <div class="chef-notes">
                    <h4><i class="fas fa-lightbulb"></i> Good to Know</h4>
                    <p>${item.chef_notes}</p>
                </div>
            ` : ''}
            
            <div class="item-details-grid">
                <div class="detail-item">
                    <h4>What's in it</h4>
                    <p>${item.ingredients.join(', ')}</p>
                </div>
                
                ${item.allergens && item.allergens.length > 0 ? `
                    <div class="detail-item allergens">
                        <h4><i class="fas fa-exclamation-triangle"></i> Contains</h4>
                        <p>${item.allergens.join(', ')}</p>
                    </div>
                ` : ''}
                
                <div class="detail-item">
                    <h4>Quick Facts</h4>
                    <p>${item.calories} calories • ${item.prep_time}</p>
                </div>
            </div>
            
            <div class="item-tags">
                ${item.vegetarian ? '<span class="menu-tag vegetarian">Vegetarian</span>' : ''}
                ${item.vegan ? '<span class="menu-tag vegan">Vegan</span>' : ''}
                ${item.gluten_free ? '<span class="menu-tag gluten-free">Gluten-Free</span>' : ''}
                ${item.spice_level ? `<span class="menu-tag spicy">Spice Level: ${item.spice_level}/5</span>` : ''}
            </div>
        </div>
    `;
    
    DOM.modalBody.innerHTML = html;
    DOM.modal.classList.add('active');
}

function closeModal() {
    DOM.modal.classList.remove('active');
}

// Send message to AI
async function sendMessage(message) {
    if (!message.trim()) return;
    
    DOM.chatInput.value = '';
    addChatMessage(message, 'user');
    
    // Animate avatar
    DOM.aiAvatar.classList.add('active');
    setTimeout(() => DOM.aiAvatar.classList.remove('active'), 600);
    
    const typingId = showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        removeTypingIndicator(typingId);
        
        if (data.success) {
            addChatMessage(data.response, 'ai');
            
            // Show recommendations if any
            if (data.recommendations && data.recommendations.length > 0) {
                showRecommendations(data.recommendations);
            }
            
            // Speak the response (interruptible)
            speakResponse(data.response);
        } else {
            addChatMessage('Hmm, something went wrong. Can you try asking again?', 'ai');
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addChatMessage('Oops! Having trouble connecting. Mind trying again?', 'ai');
    }
}

// Add chat message
function addChatMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    messageDiv.innerHTML = `<p>${message}</p>`;
    
    DOM.chatMessages.appendChild(messageDiv);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const typingId = Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai-message typing';
    typingDiv.id = `typing-${typingId}`;
    typingDiv.innerHTML = `
        <p>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </p>
    `;
    
    DOM.chatMessages.appendChild(typingDiv);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
    
    return typingId;
}

// Remove typing indicator
function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(`typing-${typingId}`);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Show recommendations
function showRecommendations(recommendations) {
    const recDiv = document.createElement('div');
    recDiv.className = 'recommendations';
    recDiv.innerHTML = `
        <h4>You might like:</h4>
        ${recommendations.map(item => `
            <div class="recommendation-item" onclick="showMenuItem(${item.id})">
                <strong>${item.name}</strong>
                <span>$${item.price.toFixed(2)}</span>
            </div>
        `).join('')}
    `;
    
    DOM.chatMessages.appendChild(recDiv);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

// Speak response (interruptible)
function speakResponse(text) {
    if (!AppState.speechSynthesis) return;
    
    // Cancel any ongoing speech
    stopSpeaking();
    
    // Clean text for speech - remove emojis and convert to speech-friendly format
    const cleanText = text
        .replace(/😋|🤤/g, 'mmm')
        .replace(/😊|😄|☺️|😁/g, '')  // Remove smile emojis (will use tone)
        .replace(/🔥/g, '')  // Remove fire emoji (excitement in voice)
        .replace(/✨/g, '')  // Remove sparkle (enthusiasm in voice)
        .replace(/👌/g, 'perfect')
        .replace(/❤️|💕/g, '')  // Remove hearts (warmth in voice)
        .replace(/[^\w\s.,!?'-]/g, '')  // Remove other emojis
        .trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;  // Slightly slower for warmth
    utterance.pitch = 1.2;  // Higher pitch for feminine voice
    utterance.volume = 0.9;
    
    // Select a feminine voice
    const voices = AppState.speechSynthesis.getVoices();
    const feminineVoice = voices.find(voice => 
        voice.name.includes('Samantha') ||  // iOS
        voice.name.includes('Microsoft Zira') ||  // Windows
        voice.name.includes('Google US English Female') ||
        voice.name.includes('Fiona') ||  // macOS
        voice.name.includes('Victoria') ||  // macOS
        voice.name.includes('female') ||
        voice.name.includes('Female') ||
        (voice.name.includes('Google') && voice.lang === 'en-US' && !voice.name.includes('Male'))
    );
    
    if (feminineVoice) {
        utterance.voice = feminineVoice;
    } else {
        // Fallback: try to find any female-sounding voice
        const fallbackVoice = voices.find(v => 
            v.name.toLowerCase().includes('female') || 
            v.name.match(/samantha|zira|fiona|victoria|kate|susan|karen/i)
        ) || voices[0];
        
        if (fallbackVoice) {
            utterance.voice = fallbackVoice;
        }
    }
    
    utterance.onstart = () => {
        AppState.isSpeaking = true;
        AppState.currentUtterance = utterance;
    };
    
    utterance.onend = () => {
        AppState.isSpeaking = false;
        AppState.currentUtterance = null;
    };
    
    AppState.speechSynthesis.speak(utterance);
}

// Make functions globally available
window.showMenuItem = showMenuItem;
window.closeModal = closeModal;