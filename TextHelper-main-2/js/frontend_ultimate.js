// TextHelper Frontend
// Backend baglantisi saglar

class TextHelperUltimate {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8080',
            wsUrl: config.wsUrl || 'ws://localhost:8080/api/v1/ws',
            useWebSocket: false, // Stabilite icin kapali
            maxSuggestions: config.maxSuggestions || 80,
            ...config
        };

        this.ws = null;
        this.inputElement = null;
        this.suggestionsContainer = null;
        this.ghostOverlay = null; // Ghost Text için overlay
        this.currentSuggestions = [];
        this._lastWsRequestText = null; // WebSocket phase: enhanced sadece aynı input için uygulansın

        // Cache
        this.cache = new Map();
        this.MAX_CACHE_SIZE = 500;

        // Kullanici kelimeleri
        this.userVocabulary = this.loadUserVocabulary();

        this.init();
    }

    init() {
        // WebSocket bağlantısı
        if (this.config.useWebSocket) {
            this.connectWebSocket();
        }
    }

    loadUserVocabulary() {
        try {
            const vocab = localStorage.getItem('texthelper_user_vocab');
            return vocab ? JSON.parse(vocab) : {};
        } catch (e) {
            console.warn('LocalStorage erişim hatası:', e);
            return {};
        }
    }

    saveUserVocabulary() {
        try {
            localStorage.setItem('texthelper_user_vocab', JSON.stringify(this.userVocabulary));
        } catch (e) {
            // Ignore storage errors
        }
    }

    getFromCache(key) {
        return this.cache.get(key);
    }

    addToCache(key, value) {
        if (this.cache.size >= this.MAX_CACHE_SIZE) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }

    // Input'a bagla
    attach(inputElement, suggestionsContainer) {
        this.inputElement = inputElement;
        this.suggestionsContainer = suggestionsContainer;

        // Ghost Text Overlay Oluştur
        this.createGhostOverlay();

        // Event listener'lar
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
            this.updateGhostText(); // Ghost text güncelle
        });

        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });

        // Scroll senkronizasyonu
        this.inputElement.addEventListener('scroll', () => {
            if (this.ghostOverlay) {
                this.ghostOverlay.scrollTop = this.inputElement.scrollTop;
                this.ghostOverlay.scrollLeft = this.inputElement.scrollLeft;
            }
        });
    }

    createGhostOverlay() {
        if (!this.inputElement || this.ghostOverlay) return;

        // Wrapper oluştur
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.width = '100%';

        this.inputElement.parentNode.insertBefore(wrapper, this.inputElement);
        wrapper.appendChild(this.inputElement);

        // Overlay oluştur
        this.ghostOverlay = document.createElement('div');
        this.ghostOverlay.className = 'ghost-overlay';
        this.ghostOverlay.style.position = 'absolute';
        this.ghostOverlay.style.top = '0';
        this.ghostOverlay.style.left = '0';
        this.ghostOverlay.style.width = '100%';
        this.ghostOverlay.style.height = '100%';
        this.ghostOverlay.style.pointerEvents = 'none'; // Tıklamaları input'a geçir
        this.ghostOverlay.style.color = 'transparent'; // Ana metin görünmez
        this.ghostOverlay.style.whiteSpace = 'pre-wrap';
        this.ghostOverlay.style.overflow = 'hidden';
        this.ghostOverlay.style.padding = window.getComputedStyle(this.inputElement).padding;
        this.ghostOverlay.style.font = window.getComputedStyle(this.inputElement).font;
        this.ghostOverlay.style.boxSizing = 'border-box';

        wrapper.appendChild(this.ghostOverlay);
    }

    updateGhostText() {
        if (!this.ghostOverlay || !this.currentSuggestions.length) {
            if (this.ghostOverlay) this.ghostOverlay.innerHTML = '';
            return;
        }

        const text = this.inputElement.value;
        const suggestion = this.currentSuggestions[0].text;

        // Eğer öneri, yazdığımız kelimeyle eşleşiyorsa
        const words = text.split(' ');
        const lastWord = words[words.length - 1];

        if (suggestion.toLowerCase().startsWith(lastWord.toLowerCase())) {
            const completion = suggestion.substring(lastWord.length);
            // Ana metin (görünmez) + Ghost Text (gri)
            this.ghostOverlay.innerHTML = text.replace(/&/g, '&amp;').replace(/</g, '&lt;') +
                '<span style="color: #9ca3af;">' + completion + '</span>';
        } else {
            this.ghostOverlay.innerHTML = '';
        }
    }

    // WebSocket baglantisi
    connectWebSocket() {
        if (this._wsConnecting) return;
        this._wsConnecting = true;
        this._reconnectAttempts = this._reconnectAttempts || 0;

        try {
            console.log(`WebSocket bağlanıyor... (${this.config.wsUrl})`);
            this.ws = new WebSocket(this.config.wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket bağlantısı kuruldu');
                this._wsConnecting = false;
                this._reconnectAttempts = 0;

                // UI Feedback: Bağlandı
                if (this.suggestionsContainer) {
                    const statusEl = document.getElementById('ws-status-indicator');
                    if (statusEl) {
                        statusEl.className = 'status-connected';
                        statusEl.title = 'Sunucuya bağlı';
                        statusEl.className = 'status-connected';
                        statusEl.title = 'Sunucuya bağlı (HTTP Modu)';
                    }
                }
            };

            // HTTP Fallback logic simulation for connection status
            if (!this.config.useWebSocket) {
                if (this.suggestionsContainer) {
                    const statusEl = document.getElementById('ws-status-indicator');
                    if (statusEl) {
                        statusEl.className = 'status-connected';
                        statusEl.title = 'Sunucuya bağlı (HTTP)';
                    }
                }
            }

            this.ws.onmessage = (event) => {
                const response = JSON.parse(event.data);
                this.handleSuggestions(response);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket hatası:', error);
                // Fallback: REST API kullan
                this.config.useWebSocket = false;
            };

            this.ws.onclose = () => {
                console.log('WebSocket bağlantısı kapandı');
                this._wsConnecting = false;

                // UI Feedback: Bağlantı Koptu
                if (this.suggestionsContainer) {
                    const statusEl = document.getElementById('ws-status-indicator');
                    if (statusEl) {
                        statusEl.className = 'status-disconnected';
                        statusEl.title = 'Bağlantı koptu - Yeniden bağlanılıyor...';
                    }
                }

                // Exponential backoff ile yeniden bağlan
                const timeout = Math.min(1000 * Math.pow(2, this._reconnectAttempts), 10000);
                this._reconnectAttempts++;
                console.log(`${timeout}ms sonra yeniden bağlanılacak...`);

                setTimeout(() => {
                    this.config.useWebSocket = true; // Tekrar dene
                    this.connectWebSocket();
                }, timeout);
            };
        } catch (error) {
            console.error('WebSocket bağlantı hatası:', error);
            this.config.useWebSocket = false;
            this._wsConnecting = false;
        }
    }

    // Son mesajdan context cikar
    getContextFromLastMessage() {
        // Chat mesajlarını bul
        if (!this.suggestionsContainer) return "";

        // Chat container (textHelperApp yapısına bağlı)
        const chatContainer = document.getElementById('messagesContainer');
        if (!chatContainer) return "";

        let messages = chatContainer.querySelectorAll('.message.incoming .message-text');
        if (messages.length === 0) {
            messages = chatContainer.querySelectorAll('.message.outgoing .message-text');
        }
        if (messages.length === 0) {
            messages = chatContainer.querySelectorAll('.message .message-text');
        }
        if (messages.length === 0) return "";

        const lastMessage = messages[messages.length - 1].textContent;
        return lastMessage;
    }

    // Input degistiginde
    async handleInput(text) {
        if (this._debounceTimer) {
            clearTimeout(this._debounceTimer);
        }

        if (!text && text.length === 0) {
            this.clearSuggestions();
            this.updateGhostText();
            return;
        }

        this._debounceTimer = setTimeout(async () => {
            // 1. Zero-Latency Cache Check
            const cached = this.getFromCache(text);
            if (cached) {
                console.log('[Cache] Hızlı yanıt (0ms)');
                this.handleSuggestions(cached);
                return;
            }

            // 2. Offline Mode (LocalStorage Fallback)
            if (!navigator.onLine) {
                console.log('[Offline] Çevrimdışı mod aktif');
                // Basit offline öneri (User Vocabulary'den)
                const words = text.split(' ');
                const lastWord = words[words.length - 1].toLowerCase();
                if (lastWord.length >= 2) {
                    const offlineSuggestions = Object.keys(this.userVocabulary)
                        .filter(w => w.startsWith(lastWord))
                        .sort((a, b) => this.userVocabulary[b] - this.userVocabulary[a]) // Frekansa göre azalan
                        .slice(0, 5)
                        .map(w => ({
                            text: w,
                            type: 'history',
                            score: 10,
                            description: 'Geçmiş (Offline)',
                            source: 'local'
                        }));

                    if (offlineSuggestions.length > 0) {
                        this.handleSuggestions({ suggestions: offlineSuggestions });
                        return;
                    }
                }
            }

            // Boş input olsa bile, son mesaja göre öneri getir (Contextual Reply)
            const contextMsg = this.getContextFromLastMessage();

            if (this.config.useWebSocket && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this._lastWsRequestText = text;
                this.ws.send(JSON.stringify({
                    text: text, // Boş olabilir
                    context_message: contextMsg, // YENİ: Önceki mesaj
                    max_suggestions: this.config.maxSuggestions,
                    use_ai: true,
                    use_search: true,
                    user_id: "default"
                }));
            } else {
                // REST API (Context desteği eklenmeli)
                // Şimdilik sadece text varsa
                if (text.trim().length > 0) {
                    await this.fetchSuggestions(text);
                }
            }
        }, 50);
    }

    // API'den onerileri cek
    async fetchSuggestions(text) {
        try {
            // New Enterprise API Endpoint
            const response = await fetch(`${this.config.apiUrl}/api/v1/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    // Context awareness for better predictions
                    context: this.getContextFromLastMessage()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hata kontrolü
            if (!data || !data.suggestions) {
                console.warn('API yanıtı geçersiz:', data);
                this.clearSuggestions();
                return;
            }

            this.handleSuggestions(data);
        } catch (error) {
            console.error('API hatası:', error);
            // Hata durumunda önerileri temizle
            this.clearSuggestions();
            // Kullanıcıya hata göster (opsiyonel)
            if (this.suggestionsContainer) {
                this.suggestionsContainer.innerHTML = `<div style="color: #ff4444; padding: 10px;">Bağlantı hatası. Backend çalışıyor mu kontrol edin.</div>`;
            }
        }
    }

    /**
     * Önerileri işle ve göster
     */
    handleSuggestions(response) {
        // WebSocket iki aşamalı: enhanced sadece hâlâ aynı input için geçerliyse uygula (eski enhanced yeni fast'ı ezmesin)
        if (response.phase === 'enhanced' && this._lastWsRequestText !== undefined && this.inputElement && this.inputElement.value !== this._lastWsRequestText) {
            return;
        }

        // Cache'e kaydet
        if (this.inputElement && response.suggestions && response.suggestions.length > 0) {
            const currentInput = this.inputElement.value;
            // Sadece son kelime için cache yapmak daha mantıklı olabilir ama şimdilik tam text
            this.addToCache(currentInput, response);
        }

        let suggestions = (response.suggestions || []).slice();

        // Smart Personalization: Kullanıcının sık kullandığı kelimeleri en üste taşı
        suggestions = suggestions.map(s => {
            const userFreq = this.userVocabulary[(s.text || '').toLowerCase()] || 0;
            if (userFreq > 0) {
                s.score = (s.score ?? 0) + (userFreq * 0.5);
                s.description = (s.description || '') + ' (Sık kullanılan)';
            }
            return s;
        }).sort((a, b) => (b.score ?? 0) - (a.score ?? 0));

        this.currentSuggestions = suggestions;

        // console.log(`[DEBUG] ${this.currentSuggestions.length} öneri alındı:`, this.currentSuggestions);

        if (this.suggestionsContainer) {
            if (this.currentSuggestions.length > 0) {
                this.renderSuggestions(this.currentSuggestions);
            } else {
                // Öneri yoksa container'ı temizle
                const container = this.suggestionsContainer.closest('.autocomplete-dropdown') || this.suggestionsContainer;
                const listEl = this.suggestionsContainer.querySelector('.suggestions-list') || this.suggestionsContainer;
                if (listEl) listEl.innerHTML = '';
                if (container) container.classList.remove('visible');
            }

            // Ghost Text Güncelle
            this.updateGhostText();
        }

        // Yazım düzeltmesi varsa göster
        if (response.corrected_text) {
            console.log('Yazım düzeltmesi:', response.corrected_text);
        }

        // İstatistikler: DOM'da processingTime span'ini güncelle
        const ptEl = document.getElementById('processingTime');
        if (ptEl) {
            ptEl.textContent = (this.currentSuggestions.length > 0 && response.processing_time_ms != null)
                ? `${Math.round(response.processing_time_ms)} ms`
                : '';
        }
        if (response.processing_time_ms) {
            console.log(`İşlem süresi: ${response.processing_time_ms}ms`);
        }
    }

    /**
     * Önerileri render et
     */
    renderSuggestions(suggestions) {
        if (!this.suggestionsContainer) return;

        // Container'ı bul (autocompleteDropdown veya suggestionsList)
        const container = this.suggestionsContainer.closest('.autocomplete-dropdown') || this.suggestionsContainer;
        const listElement = this.suggestionsContainer.classList.contains('suggestions-list')
            ? this.suggestionsContainer
            : this.suggestionsContainer.querySelector('.suggestions-list') || this.suggestionsContainer;

        if (suggestions.length === 0) {
            if (listElement) listElement.innerHTML = '';
            container.classList.remove('visible');
            return;
        }

        const html = suggestions.map((sug, index) => `
            <div class="suggestion-item ${index === 0 ? 'active' : ''}" 
                 data-index="${index}"
                 onclick="textHelperUltimate.selectSuggestion(${index})">
                <div class="suggestion-icon ${sug.source}">
                    <i class="${this.getIcon(sug.type)}"></i>
                </div>
                <div class="suggestion-content">
                    <span class="suggestion-text">${this.escapeHtml(sug.text)}</span>
                    <span class="suggestion-meta">
                        ${sug.description} 
                        <span class="suggestion-source">(${sug.source})</span>
                    </span>
                </div>
                <div class="suggestion-score">${Number(sug.score ?? 0).toFixed(1)}</div>
            </div>
        `).join('');

        if (listElement) {
            listElement.innerHTML = html;
        } else {
            this.suggestionsContainer.innerHTML = html;
        }
        container.classList.add('visible');
    }

    /**
     * Öneri seç
     */
    selectSuggestion(index) {
        if (index < 0 || index >= this.currentSuggestions.length) return;

        const suggestion = this.currentSuggestions[index];

        // Metni güncelle
        if (this.inputElement) {
            const currentText = this.inputElement.value;
            const words = currentText.split(' ');
            // Eger son kelime boslursa (yani bosluktan sonra) ve biz yeni kelime seciyorsak
            if (words[words.length - 1] === '' && words.length > 1) {
                words[words.length - 1] = suggestion.text;
            } else {
                words[words.length - 1] = suggestion.text;
            }
            this.inputElement.value = words.join(' ');
            if (!this.inputElement.value.endsWith(' ')) {
                this.inputElement.value += ' '; // Kolaylık için bir boşluk daha ekle
            }

            // Input event tetikle
            this.inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        }

        // ÖĞRENME: Seçilen öneriyi kaydet
        this.learnMessage(this.inputElement.value, suggestion.text);

        // Önerileri temizle
        this.clearSuggestions();
    }

    /**
     * Klavye olayları
     */
    handleKeyDown(event) {
        if (this.currentSuggestions.length === 0) return;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.moveSelection(1);
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.moveSelection(-1);
                break;
            case ' ':
                // AUTO-CORRECT (Refleksler)
                // Boşluk tuşuna basınca en iyi DÜZELTME önerisini uygula
                if (this.currentSuggestions.length > 0) {
                    const topSuggestion = this.currentSuggestions[0];
                    if (topSuggestion.type === 'correction' && topSuggestion.confidence >= 1.0) {
                        event.preventDefault(); // Boşluğu biz ekleyeceğiz
                        this.selectSuggestion(0);
                        // Kelimeyi tamamladıktan sonra otomatik bir boşluk ekle
                        this.inputElement.value += ' ';
                    }
                }
                break;
            case 'Tab':
                if (this.currentSuggestions.length > 0) {
                    event.preventDefault();
                    const active = this.suggestionsContainer?.querySelector('.suggestion-item.active');
                    const idx = active != null && active.dataset.index != null
                        ? parseInt(active.dataset.index, 10)
                        : 0;
                    this.selectSuggestion(isNaN(idx) ? 0 : Math.max(0, Math.min(idx, this.currentSuggestions.length - 1)));
                }
                break;
            case 'Escape':
                this.clearSuggestions();
                break;
        }
    }

    /**
     * Seçimi hareket ettir
     */
    moveSelection(direction) {
        // Bu özellik UI'da implement edilmeli
        const items = this.suggestionsContainer?.querySelectorAll('.suggestion-item');
        if (!items) return;

        let currentIndex = 0;
        items.forEach((item, idx) => {
            if (item.classList.contains('active')) {
                currentIndex = idx;
            }
        });

        const newIndex = Math.max(0, Math.min(items.length - 1, currentIndex + direction));

        items.forEach((item, idx) => {
            item.classList.toggle('active', idx === newIndex);
        });
    }

    /**
     * İkon al
     */
    getIcon(type) {
        const icons = {
            'ai_prediction': 'fas fa-brain',
            'ai_generation': 'fas fa-magic', // New magic icon for GPT-2
            'dictionary': 'fas fa-book',
            'spellcheck': 'fas fa-spell-check',
            'fuzzy': 'fas fa-search'
        };
        return icons[type] || 'fas fa-comment';
    }

    /**
     * HTML escape
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Önerileri temizle
     */
    clearSuggestions() {
        this.currentSuggestions = [];
        if (this.suggestionsContainer) {
            const container = this.suggestionsContainer.closest('.autocomplete-dropdown') || this.suggestionsContainer;
            const listElement = this.suggestionsContainer.classList.contains('suggestions-list')
                ? this.suggestionsContainer
                : this.suggestionsContainer.querySelector('.suggestions-list');

            if (listElement) {
                listElement.innerHTML = '';
            } else {
                this.suggestionsContainer.innerHTML = '';
            }
            container.classList.remove('visible');
        }
        const ptEl = document.getElementById('processingTime');
        if (ptEl) ptEl.textContent = '';
    }

    /**
     * Mesaj gönderildiğinde veya öneri seçildiğinde (öğrenme için)
     * Backend /learn ile user_dict + n-gram güncellenir.
     */
    async learnMessage(message, selectedSuggestion = "") {
        if (!message || !String(message).trim()) return;
        try {
            const res = await fetch(`${this.config.apiUrl}/api/v1/learn`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: String(message).trim() })
            });
            if (!res.ok) throw new Error(`Learn ${res.status}`);
        } catch (e) {
            console.warn('Öğrenme isteği hatası:', e);
        }
        try {
            if (selectedSuggestion) {
                const word = String(selectedSuggestion).toLowerCase();
                this.userVocabulary[word] = (this.userVocabulary[word] || 0) + 1;
                this.saveUserVocabulary();
            }
        } catch (e) {
            console.warn('Local vocabulary güncelleme hatası:', e);
        }
    }
}

// Global instance
let textHelperUltimate = null;

// Başlatma fonksiyonu
function initTextHelperUltimate(config) {
    textHelperUltimate = new TextHelperUltimate(config);
    return textHelperUltimate;
}

// Export
if (typeof window !== 'undefined') {
    window.TextHelperUltimate = TextHelperUltimate;
    window.initTextHelperUltimate = initTextHelperUltimate;
    window.textHelperUltimate = null;
}
