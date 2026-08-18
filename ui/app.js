/**
 * Al-Furqan AI - Modern Intuitive Frontend Controller v14.0
 * 100% Real Backend Data Pipelines (Zero Mocks / Full Universal Search / Real OCR & PDF / 7-Language Reactive)
 */

document.addEventListener('DOMContentLoaded', async () => {
    // =========================================================================
    // 1. STATE & CORE INSTANCES
    // =========================================================================
    let currentSurah = 1;
    let currentReciter = 'alafasy';
    let isContinuous = true;
    let currentPlayingAyahIndex = 0;
    let surahAyahsData = [];
    let surahsMetadata = [];
    
    const audio = new Audio();
    audio.preload = 'auto';

    // UI Elements
    const selectLanguage = document.getElementById('selectLanguage');
    const metricVisitors = document.getElementById('metricVisitors');
    const metricVisitorsLabel = document.getElementById('metricVisitorsLabel');
    const btnToggleVisitorStats = document.getElementById('btnToggleVisitorStats');
    const visitorCounterContainer = document.getElementById('visitorCounterContainer');
    const visitorStatsPopover = document.getElementById('visitorStatsPopover');
    const statCountToday = document.getElementById('statCountToday');
    const statCountWeek = document.getElementById('statCountWeek');
    const statCountMonth = document.getElementById('statCountMonth');
    const statCountYear = document.getElementById('statCountYear');
    const statCountAllTime = document.getElementById('statCountAllTime');
    const statCells = document.querySelectorAll('.stat-cell');

    let visitorStatsData = { today: 0, week: 0, month: 0, year: 0, all_time: 0 };
    let currentVisitorPeriod = 'all_time';
    const periodI18nKeys = {
        today: 'metricToday',
        week: 'metricWeek',
        month: 'metricMonth',
        year: 'metricYear',
        all_time: 'metricAllTime'
    };
    
    // Universal Search Elements
    const universalSearchInput = document.getElementById('universalSearchInput');
    const btnUniversalSearchGo = document.getElementById('btnUniversalSearchGo');
    const btnClearSearch = document.getElementById('btnClearSearch');
    const searchResultsDropdown = document.getElementById('searchResultsDropdown');
    const searchResultsCount = document.getElementById('searchResultsCount');
    const searchResultsList = document.getElementById('searchResultsList');
    const btnCloseSearchResults = document.getElementById('btnCloseSearchResults');

    // Tabs
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Quran Explorer Elements
    const selectSura = document.getElementById('selectSura');
    const selectReciter = document.getElementById('selectReciter');
    const btnPlayFullSurah = document.getElementById('btnPlayFullSurah');
    const surahHeroArabic = document.getElementById('surahHeroArabic');
    const surahHeroTitle = document.getElementById('surahHeroTitle');
    const surahHeroMeta = document.getElementById('surahHeroMeta');
    const ayahsStreamContainer = document.getElementById('ayahsStreamContainer');

    // Guard Elements
    const guardTextInput = document.getElementById('guardTextInput');
    const btnRunGuardValidation = document.getElementById('btnRunGuardValidation');
    const btnPasteSampleGuard = document.getElementById('btnPasteSampleGuard');
    const verificationResultBox = document.getElementById('verificationResultBox');
    const rootSearchInput = document.getElementById('rootSearchInput');
    const btnSearchRoot = document.getElementById('btnSearchRoot');
    const rootSearchResults = document.getElementById('rootSearchResults');

    // Halal & Contract Elements
    const halalClauseInput = document.getElementById('halalClauseInput');
    const btnAuditHalal = document.getElementById('btnAuditHalal');
    const btnAuditAAOIFI = document.getElementById('btnAuditAAOIFI');
    const btnTriggerOCR = document.getElementById('btnTriggerOCR');
    const inputProductImage = document.getElementById('inputProductImage');
    const btnTriggerPDF = document.getElementById('btnTriggerPDF');
    const inputContractPDF = document.getElementById('inputContractPDF');
    const halalAuditResult = document.getElementById('halalAuditResult');

    // Namaz & Zakat Elements
    const cityPills = document.querySelectorAll('.city-pill');
    const btnGetLocation = document.getElementById('btnGetLocation');
    const timeFajr = document.getElementById('timeFajr');
    const timeSunrise = document.getElementById('timeSunrise');
    const timeDhuhr = document.getElementById('timeDhuhr');
    const timeAsr = document.getElementById('timeAsr');
    const timeMaghrib = document.getElementById('timeMaghrib');
    const timeIsha = document.getElementById('timeIsha');
    const qiblaDegreeText = document.getElementById('qiblaDegreeText');
    const zakatCash = document.getElementById('zakatCash');
    const zakatGold = document.getElementById('zakatGold');
    const zakatDebts = document.getElementById('zakatDebts');
    const btnCalculateZakat = document.getElementById('btnCalculateZakat');
    const zakatAmountText = document.getElementById('zakatAmountText');
    const zakatNoteText = document.getElementById('zakatNoteText');

    // Floating Player Elements
    const floatingPlayerBar = document.getElementById('floatingPlayerBar');
    const btnPlayerPlayPause = document.getElementById('btnPlayerPlayPause');
    const playerTitle = document.getElementById('playerTitle');
    const playerReciterName = document.getElementById('playerReciterName');
    const btnPlayerPrev = document.getElementById('btnPlayerPrev');
    const btnPlayerNext = document.getElementById('btnPlayerNext');
    const btnToggleContinuous = document.getElementById('btnToggleContinuous');
    const playerSpeedSelect = document.getElementById('playerSpeedSelect');
    const btnClosePlayerBar = document.getElementById('btnClosePlayerBar');

    // Modals
    const modalStandards = document.getElementById('modalStandards');
    const btnToggleStandards = document.getElementById('btnToggleStandards');
    const btnCloseStandards = document.getElementById('btnCloseStandards');
    const modalFeedback = document.getElementById('modalFeedback');
    const btnToggleFeedback = document.getElementById('btnToggleFeedback');
    const btnCloseFeedback = document.getElementById('btnCloseFeedback');
    const btnSubmitFeedback = document.getElementById('btnSubmitFeedback');
    const feedbackName = document.getElementById('feedbackName');
    const feedbackContact = document.getElementById('feedbackContact');
    const feedbackMessage = document.getElementById('feedbackMessage');
    const feedbackStatusText = document.getElementById('feedbackStatusText');
    const modalGuide = document.getElementById('modalGuide');
    const btnToggleGuide = document.getElementById('btnToggleGuide');
    const btnCloseGuide = document.getElementById('btnCloseGuide');

    // =========================================================================
    // 2. INITIALIZATION & LANGUAGE SYNCHRONIZATION
    // =========================================================================
    async function initApp() {
        const savedLang = localStorage.getItem('alfurqan_lang') || 'kk';
        if (selectLanguage) selectLanguage.value = savedLang;
        if (typeof I18N !== 'undefined' && I18N.setLanguage) {
            I18N.setLanguage(savedLang);
        }

        await loadSurahsList();
        await loadVisitorAnalytics();
        await loadSurah(1);
        await loadNamazTimes(51.1694, 71.4491); // Default Astana
        calculateZakat();
    }

    // =========================================================================
    // 3. REACTIVE LANGUAGE EVENT LISTENER
    // =========================================================================
    window.addEventListener('languageChanged', (e) => {
        const lang = e.detail?.lang || I18N.currentLang;
        
        // 1. Refresh Surah dropdown options
        populateSurahDropdown();
        
        // 2. Refresh Surah Hero Info
        updateSurahHeroHeader();

        // 3. Re-render current Ayahs stream with current language translations
        if (surahAyahsData && surahAyahsData.length > 0) {
            renderAyahsStream(surahAyahsData, currentSurah);
        }

        // 4. Update Reciter Name in Player
        updateReciterDisplay();

        // 5. Update Visitor Counter active period label
        updateVisitorBadgeDisplay();

        // 6. Re-calculate Zakat note text
        calculateZakat();
    });

    // =========================================================================
    // 4. PERSISTENT MULTI-TIMEFRAME VISITOR ANALYTICS
    // =========================================================================
    function updateVisitorBadgeDisplay() {
        if (!metricVisitors) return;
        const currentCount = visitorStatsData[currentVisitorPeriod] !== undefined 
            ? visitorStatsData[currentVisitorPeriod] 
            : (visitorStatsData.all_time || 0);
        metricVisitors.textContent = Number(currentCount).toLocaleString();
        
        if (metricVisitorsLabel) {
            const i18nKey = periodI18nKeys[currentVisitorPeriod] || 'metricAllTime';
            metricVisitorsLabel.textContent = I18N.t(i18nKey) || 'За все время';
        }

        // Update active class in popup cells
        statCells.forEach(cell => {
            if (cell.getAttribute('data-period') === currentVisitorPeriod) {
                cell.classList.add('active-stat-cell');
            } else {
                cell.classList.remove('active-stat-cell');
            }
        });
    }

    async function loadVisitorAnalytics() {
        try {
            const resp = await fetch('/api/v1/analytics/visitor-count');
            const data = await resp.json();
            
            visitorStatsData = {
                today: data.today || 0,
                week: data.week || 0,
                month: data.month || 0,
                year: data.year || 0,
                all_time: data.all_time || data.total_visitors || 0
            };

            if (statCountToday) statCountToday.textContent = Number(visitorStatsData.today).toLocaleString();
            if (statCountWeek) statCountWeek.textContent = Number(visitorStatsData.week).toLocaleString();
            if (statCountMonth) statCountMonth.textContent = Number(visitorStatsData.month).toLocaleString();
            if (statCountYear) statCountYear.textContent = Number(visitorStatsData.year).toLocaleString();
            if (statCountAllTime) statCountAllTime.textContent = Number(visitorStatsData.all_time).toLocaleString();

            updateVisitorBadgeDisplay();
        } catch (e) {
            console.warn("Analytics fetch notice:", e);
        }
    }

    // Toggle Popover
    if (btnToggleVisitorStats && visitorStatsPopover) {
        btnToggleVisitorStats.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = visitorStatsPopover.style.display === 'block';
            visitorStatsPopover.style.display = isOpen ? 'none' : 'block';
            if (visitorCounterContainer) visitorCounterContainer.classList.toggle('open', !isOpen);
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (visitorCounterContainer && !visitorCounterContainer.contains(e.target)) {
                visitorStatsPopover.style.display = 'none';
                visitorCounterContainer.classList.remove('open');
            }
        });
    }

    // Cell period switcher
    statCells.forEach(cell => {
        cell.addEventListener('click', (e) => {
            e.stopPropagation();
            const period = cell.getAttribute('data-period');
            if (period) {
                currentVisitorPeriod = period;
                updateVisitorBadgeDisplay();
                if (visitorStatsPopover) visitorStatsPopover.style.display = 'none';
                if (visitorCounterContainer) visitorCounterContainer.classList.remove('open');
            }
        });
    });


    // =========================================================================
    // 5. TAB SWITCHING
    // =========================================================================
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // =========================================================================
    // 6. UNIVERSAL SMART SEARCH (REAL-TIME ACROSS SURAHS, AYAHS, HALAL, E-CODES)
    // =========================================================================
    let searchDebounce = null;

    universalSearchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        btnClearSearch.style.display = val ? 'block' : 'none';
        
        clearTimeout(searchDebounce);
        if (val.length >= 2) {
            searchDebounce = setTimeout(() => performUniversalSearch(val), 300);
        } else {
            searchResultsDropdown.style.display = 'none';
        }
    });

    btnClearSearch.addEventListener('click', () => {
        universalSearchInput.value = '';
        btnClearSearch.style.display = 'none';
        searchResultsDropdown.style.display = 'none';
    });

    btnCloseSearchResults.addEventListener('click', () => {
        searchResultsDropdown.style.display = 'none';
    });

    btnUniversalSearchGo.addEventListener('click', () => {
        const val = universalSearchInput.value.trim();
        if (val) performUniversalSearch(val);
    });

    async function performUniversalSearch(query) {
        searchResultsList.innerHTML = `<div class="loading-spinner"><p>${I18N.t('searchingText') || 'Поиск по Корану и канонической базе...'}</p></div>`;
        searchResultsDropdown.style.display = 'block';

        try {
            // 1. Check Quran search endpoint
            const quranResp = await fetch(`/api/v1/quran/search?q=${encodeURIComponent(query)}`);
            const quranData = await quranResp.json();
            const ayahs = quranData.results || [];

            // 2. Check Halal Knowledge base
            const halalResp = await fetch(`/api/v1/halal/screen`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const halalData = await halalResp.json();
            const halalMatches = halalData.matches || [];

            renderSearchResults(query, ayahs, halalMatches);
        } catch (e) {
            searchResultsList.innerHTML = `<p style="color: var(--danger-primary); padding: 12px;">${I18N.t('searchNoResults') || 'Ошибка выполнения поиска.'}</p>`;
        }
    }

    function renderSearchResults(query, ayahs, halalMatches) {
        searchResultsList.innerHTML = '';
        const total = ayahs.length + halalMatches.length;
        searchResultsCount.textContent = I18N.t('searchResultsFound', { total: total }) || `Найдено: ${total}`;

        if (total === 0) {
            searchResultsList.innerHTML = `<p style="padding: 16px; color: var(--text-secondary);">${I18N.t('searchNoResults') || 'Ничего не найдено.'}</p>`;
            return;
        }

        const currentLang = I18N.currentLang || 'ru';

        // 1. Render Halal Matches First if found
        if (halalMatches.length > 0) {
            halalMatches.forEach(m => {
                const item = document.createElement('div');
                item.className = 'search-result-item';
                const isHaram = m.verdict === 'HARAM';
                const verdictBadge = isHaram 
                    ? (I18N.t('verdictHaramBadge') || '🔴 ХАРАМ (ЗАПРЕТНО)')
                    : (I18N.t('verdictHalalDirectHeader') || '🟢 ХАЛЯЛЬ / ДОЗВОЛЕНО');

                item.innerHTML = `
                    <div class="search-result-header-line">
                        <span style="font-weight: 800; color: ${isHaram ? '#F87171' : '#34D399'};">
                            ${verdictBadge}: ${m.title_ru}
                        </span>
                        <span style="font-size: 11px; color: var(--text-muted);">${m.ayah_ref || 'Шариат'}</span>
                    </div>
                    <div class="search-result-trans">${m.description_ru}</div>
                `;
                item.addEventListener('click', () => {
                    searchResultsDropdown.style.display = 'none';
                    document.querySelector('[data-tab="tab-halal"]').click();
                    halalClauseInput.value = query;
                    btnAuditHalal.click();
                });
                searchResultsList.appendChild(item);
            });
        }

        // 2. Render Quran Ayahs
        if (ayahs.length > 0) {
            const surahNamesList = I18N.t('surahNames') || [];
            ayahs.forEach(a => {
                const item = document.createElement('div');
                item.className = 'search-result-item';
                const trans = a.translations?.[currentLang] || a.translations?.ru || a.translations?.kk || a.translations?.en || '';
                const localizedSurahName = (Array.isArray(surahNamesList) && surahNamesList[a.sura - 1]) || a.surah_name_ru || '';

                item.innerHTML = `
                    <div class="search-result-header-line">
                        <span class="search-result-title">📖 ${I18N.t('playerTitlePrefix', { sura: a.sura, ayah: a.ayah })} (${localizedSurahName})</span>
                    </div>
                    <div class="search-result-arabic">${a.text_uthmani}</div>
                    <div class="search-result-trans">${trans}</div>
                `;
                item.addEventListener('click', async () => {
                    searchResultsDropdown.style.display = 'none';
                    document.querySelector('[data-tab="tab-quran"]').click();
                    selectSura.value = a.sura;
                    await loadSurah(a.sura);
                    
                    // Scroll to specific Ayah
                    const ayahCard = document.getElementById(`ayah-card-${a.sura}-${a.ayah}`);
                    if (ayahCard) {
                        ayahCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        playAyah(a.ayah - 1);
                    }
                });
                searchResultsList.appendChild(item);
            });
        }
    }

    // =========================================================================
    // 7. QURAN EXPLORER & AUDIO ENGINE (REAL 114 SURAHS & 3 RECITERS)
    // =========================================================================
    async function loadSurahsList() {
        try {
            const resp = await fetch('/api/v1/quran/surahs');
            const data = await resp.json();
            surahsMetadata = data.surahs || [];
            populateSurahDropdown();
        } catch (e) {
            console.warn("Failed to load surahs list:", e);
        }
    }

    function populateSurahDropdown() {
        if (!selectSura) return;
        const currentVal = parseInt(selectSura.value) || currentSurah || 1;
        const surahNamesList = I18N.t('surahNames') || [];

        selectSura.innerHTML = '';
        for (let sNum = 1; sNum <= 114; sNum++) {
            const sMeta = surahsMetadata.find(s => s.number === sNum) || { ayah_count: 7, name_ar: '' };
            const localizedName = (Array.isArray(surahNamesList) && surahNamesList[sNum - 1]) || `Surah ${sNum}`;
            const opt = document.createElement('option');
            opt.value = sNum;
            opt.textContent = `${sNum}. ${localizedName} (${sMeta.name_ar || ''}) • ${sMeta.ayah_count} ${I18N.t('metricAyahs') || 'аятов'}`;
            selectSura.appendChild(opt);
        }
        selectSura.value = currentVal;
    }

    selectSura.addEventListener('change', (e) => {
        const sura = parseInt(e.target.value) || 1;
        loadSurah(sura);
    });

    function updateReciterDisplay() {
        const reciterLabels = {
            alafasy: I18N.t('reciterAlafasy') || 'Мишари Рашид Аль-Афаси',
            husary: I18N.t('reciterHusary') || 'Махмуд Халиль Аль-Хусари',
            abdulbasit: I18N.t('reciterAbdulbasit') || 'Абдульбасит Абдуссамад'
        };
        if (playerReciterName) {
            playerReciterName.textContent = reciterLabels[currentReciter]?.replace(/🎙️\s*/, '') || currentReciter;
        }
    }

    selectReciter.addEventListener('change', (e) => {
        currentReciter = e.target.value;
        updateReciterDisplay();
    });

    function updateSurahHeroHeader() {
        if (!surahAyahsData || surahAyahsData.length === 0) return;
        const surahNamesList = I18N.t('surahNames') || [];
        const localizedName = (Array.isArray(surahNamesList) && surahNamesList[currentSurah - 1]) || `Surah ${currentSurah}`;
        
        if (surahHeroTitle) {
            surahHeroTitle.textContent = `${currentSurah}. ${localizedName}`;
        }
        if (surahHeroMeta) {
            surahHeroMeta.textContent = I18N.t('surahHeroMetaPattern', { ayahs: surahAyahsData.length }) || `${surahAyahsData.length} Аятов`;
        }
    }

    async function loadSurah(suraNum) {
        currentSurah = suraNum;
        ayahsStreamContainer.innerHTML = `<div class="loading-spinner"><p>${I18N.t('loadingAyahs') || 'Загрузка аятов суры...'}</p></div>`;

        try {
            const resp = await fetch(`/api/v1/surah/${suraNum}`);
            const data = await resp.json();
            surahAyahsData = data.ayahs || [];

            if (surahHeroArabic) {
                surahHeroArabic.textContent = data.surah_name_ar || `سورة ${suraNum}`;
            }
            updateSurahHeroHeader();
            renderAyahsStream(surahAyahsData, suraNum);
        } catch (e) {
            ayahsStreamContainer.innerHTML = `<p style="color: var(--danger-primary)">${I18N.t('errorLoadingSurah') || 'Ошибка загрузки суры.'}</p>`;
        }
    }

    function renderAyahsStream(ayahs, suraNum) {
        ayahsStreamContainer.innerHTML = '';
        const currentLang = I18N.currentLang || 'ru';
        const playAyahLabel = I18N.t('btnPlayAyah') || '▶ Слушать';

        ayahs.forEach((a, idx) => {
            const card = document.createElement('div');
            card.className = 'ayah-card';
            card.id = `ayah-card-${suraNum}-${a.ayah}`;

            // Resolve translation for current active language with fallbacks
            const trans = a.translations?.[currentLang] 
                || (currentLang === 'ar' ? '' : (a.translations?.ru || a.translations?.kk || a.translations?.en || ''));
            const translit = a.transliteration || '';

            card.innerHTML = `
                <div class="ayah-top-bar">
                    <div class="ayah-number-badge">${a.ayah}</div>
                    <div class="ayah-actions">
                        <button class="btn-play-ayah" data-idx="${idx}">
                            <span>${playAyahLabel}</span>
                        </button>
                    </div>
                </div>
                <div class="ayah-arabic-text">${a.text_uthmani}</div>
                ${translit ? `<div class="ayah-transliteration">${translit}</div>` : ''}
                ${trans ? `<div class="ayah-translation">${trans}</div>` : ''}
            `;

            const btnPlay = card.querySelector('.btn-play-ayah');
            btnPlay.addEventListener('click', () => {
                playAyah(idx);
            });

            ayahsStreamContainer.appendChild(card);
        });
    }

    // Audio Playback Controller
    function playAyah(idx) {
        if (!surahAyahsData || idx >= surahAyahsData.length) return;
        currentPlayingAyahIndex = idx;
        const ayahData = surahAyahsData[idx];
        const audioUrl = ayahData.audio_urls[currentReciter] || ayahData.audio_urls.alafasy;

        audio.src = audioUrl;
        audio.playbackRate = parseFloat(playerSpeedSelect.value) || 1.0;
        audio.play().catch(e => console.warn("Audio play blocked by browser:", e));

        // Highlight playing card
        document.querySelectorAll('.ayah-card').forEach(c => c.classList.remove('playing'));
        const activeCard = document.getElementById(`ayah-card-${currentSurah}-${ayahData.ayah}`);
        if (activeCard) activeCard.classList.add('playing');

        // Show floating player bar
        floatingPlayerBar.style.display = 'flex';
        btnPlayerPlayPause.textContent = '⏸';
        playerTitle.textContent = I18N.t('playerTitlePrefix', { sura: currentSurah, ayah: ayahData.ayah }) || `Сура ${currentSurah}, Аят ${ayahData.ayah}`;
        updateReciterDisplay();
    }

    audio.addEventListener('ended', () => {
        if (isContinuous && currentPlayingAyahIndex + 1 < surahAyahsData.length) {
            playAyah(currentPlayingAyahIndex + 1);
        } else {
            btnPlayerPlayPause.textContent = '▶';
            document.querySelectorAll('.ayah-card').forEach(c => c.classList.remove('playing'));
        }
    });

    btnPlayFullSurah.addEventListener('click', () => {
        playAyah(0);
    });

    btnPlayerPlayPause.addEventListener('click', () => {
        if (audio.paused) {
            audio.play();
            btnPlayerPlayPause.textContent = '⏸';
        } else {
            audio.pause();
            btnPlayerPlayPause.textContent = '▶';
        }
    });

    btnPlayerPrev.addEventListener('click', () => {
        if (currentPlayingAyahIndex > 0) playAyah(currentPlayingAyahIndex - 1);
    });

    btnPlayerNext.addEventListener('click', () => {
        if (currentPlayingAyahIndex + 1 < surahAyahsData.length) playAyah(currentPlayingAyahIndex + 1);
    });

    btnToggleContinuous.addEventListener('click', () => {
        isContinuous = !isContinuous;
        btnToggleContinuous.classList.toggle('active', isContinuous);
    });

    playerSpeedSelect.addEventListener('change', (e) => {
        audio.playbackRate = parseFloat(e.target.value) || 1.0;
    });

    btnClosePlayerBar.addEventListener('click', () => {
        audio.pause();
        floatingPlayerBar.style.display = 'none';
        document.querySelectorAll('.ayah-card').forEach(c => c.classList.remove('playing'));
    });

    // =========================================================================
    // 8. ANTI-HALLUCINATION GUARD & ROOTS EXPLORER
    // =========================================================================
    btnRunGuardValidation.addEventListener('click', async () => {
        const text = guardTextInput.value.trim();
        if (!text) return;

        verificationResultBox.style.display = 'block';
        verificationResultBox.innerHTML = `<div class="loading-spinner"><p>${I18N.t('verifyingText') || 'Выполняется детерминированная проверка цитат...'}</p></div>`;

        try {
            const resp = await fetch('/api/v1/guard/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            const data = await resp.json();
            renderGuardResult(data);
        } catch (e) {
            verificationResultBox.innerHTML = '<p style="color: var(--danger-primary)">Ошибка проверки.</p>';
        }
    });

    btnPasteSampleGuard.addEventListener('click', () => {
        guardTextInput.value = "В суре 2 аяте 288 сказано: «И вкушайте плоды смоковницы без меры...»";
        btnRunGuardValidation.click();
    });

    function renderGuardResult(data) {
        verificationResultBox.innerHTML = '';
        const isValid = data.is_valid;
        verificationResultBox.className = `verification-result-box ${isValid ? 'valid' : 'invalid'}`;

        if (!data.claims_detected) {
            verificationResultBox.innerHTML = `
                <div class="verdict-header" style="color: #94A3B8;">${I18N.t('guardNoQuotesHeader') || 'ℹ️ Прямых цитат Корана в тексте не обнаружено'}</div>
                <div class="verdict-desc">${I18N.t('guardNoQuotesDesc') || 'Система не выявила ссылок на суры или аяты.'}</div>
            `;
            return;
        }

        if (isValid) {
            verificationResultBox.innerHTML = `
                <div class="verdict-header" style="color: #34D399;">${I18N.t('guardValidHeader') || '✅ ЦИТАТА ИЗ КОРАНА 100% ДОСТОВЕРНА (CANONICAL TANZIL)'}</div>
                <div class="verdict-desc">${I18N.t('guardValidDesc') || 'Все номера аятов, канонический текст и огласовки полностью соответствуют канону. Галлюцинаций не обнаружено.'}</div>
            `;
        } else {
            let violationsHtml = '';
            (data.violations || []).forEach(v => {
                violationsHtml += `<li><strong>${v.type}:</strong> ${v.details}</li>`;
            });

            verificationResultBox.innerHTML = `
                <div class="verdict-header" style="color: #F87171;">${I18N.t('guardInvalidHeader') || '🚨 ОБНАРУЖЕНА ОШИБКА / ГАЛЛЮЦИНАЦИЯ В ЦИТАТЕ!'}</div>
                <div class="verdict-desc">${I18N.t('guardInvalidDesc') || 'В тексте выявлены несоответствия каноническому Корану:'}</div>
                <ul style="padding-left: 20px; color: #FECACA; margin-bottom: 10px;">${violationsHtml}</ul>
                <div style="font-size: 12px; color: var(--text-muted);">${I18N.t('guardProtectedNote') || '🛡️ Al-Furqan AI защитил от распространения недостоверного текста.'}</div>
            `;
        }
    }

    // 1,651 Roots Search
    btnSearchRoot.addEventListener('click', async () => {
        const root = rootSearchInput.value.trim();
        if (!root) return;

        rootSearchResults.innerHTML = `<p>${I18N.t('rootSearchingText') || 'Поиск по корню...'}</p>`;
        try {
            const resp = await fetch(`/api/v1/root/${encodeURIComponent(root)}`);
            const data = await resp.json();
            const results = data.results || [];
            
            if (results.length === 0) {
                rootSearchResults.innerHTML = `<p style="color: var(--text-muted)">${I18N.t('rootNotFoundText', { root: root }) || `По корню «${root}» аятов не найдено.`}</p>`;
                return;
            }

            const headerText = I18N.t('rootFoundText', { root: root, total: data.total }) || `Найдено ${data.total} аятов с корнем «${root}»:`;
            let html = `<p style="font-weight: 700; color: var(--gold-bright); margin-bottom: 8px;">${headerText}</p>`;
            results.slice(0, 5).forEach(r => {
                html += `
                    <div style="background: var(--bg-surface-elevated); padding: 10px 14px; border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-size: 13px; font-weight: 700; color: var(--cyan-bright)">${I18N.t('playerTitlePrefix', { sura: r.sura, ayah: r.ayah })}</div>
                        <div style="font-family: 'Amiri Quran', serif; font-size: 18px; color: #FFF; line-height: 1.8; direction: rtl; text-align: right;">${r.text_uthmani}</div>
                    </div>
                `;
            });
            rootSearchResults.innerHTML = html;
        } catch (e) {
            rootSearchResults.innerHTML = '<p style="color: var(--danger-primary)">Ошибка поиска по корню.</p>';
        }
    });

    // =========================================================================
    // 9. REAL OCR PHOTO SCANNING & REAL PDF DOCUMENT AUDIT
    // =========================================================================
    // Real Photo OCR
    btnTriggerOCR.addEventListener('click', () => inputProductImage.click());
    inputProductImage.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `<div class="loading-spinner"><p>${I18N.t('halalScanningOCR') || '📷 Выполняется реальное OCR-распознавание изображения и анализ состава...'}</p></div>`;

        try {
            const reader = new FileReader();
            reader.onload = async () => {
                const base64Data = reader.result.split(',')[1];
                const resp = await fetch('/api/v1/images/audit-ocr', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_base64: base64Data })
                });
                const data = await resp.json();
                renderHalalResult(data);
            };
            reader.readAsDataURL(file);
        } catch (err) {
            halalAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Ошибка обработки фото.</p>';
        }
    });

    // Real PDF Audit
    btnTriggerPDF.addEventListener('click', () => inputContractPDF.click());
    inputContractPDF.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `<div class="loading-spinner"><p>${I18N.t('halalAuditingPDF') || '📑 PDF документ анализируется по стандартам AAOIFI и Корана...'}</p></div>`;

        try {
            const reader = new FileReader();
            reader.onload = async () => {
                const base64Data = reader.result.split(',')[1];
                const resp = await fetch('/api/v1/documents/audit-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pdf_base64: base64Data })
                });
                const data = await resp.json();
                if (data.audit) {
                    renderPDFAuditResult(data.audit);
                }
            };
            reader.readAsDataURL(file);
        } catch (err) {
            halalAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Ошибка аудита PDF.</p>';
        }
    });

    // Quick Chips & Text Halal Audit
    document.querySelectorAll('.test-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-text');
            if (text) {
                halalClauseInput.value = text;
                btnAuditHalal.click();
            }
        });
    });

    btnAuditHalal.addEventListener('click', async () => {
        const text = halalClauseInput.value.trim();
        if (!text) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `<div class="loading-spinner"><p>${I18N.t('halalChecking') || 'Проверка по канонической базе Халяль...'}</p></div>`;

        try {
            const resp = await fetch('/api/v1/halal/screen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text })
            });
            const data = await resp.json();
            renderHalalResult(data);
        } catch (e) {
            halalAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Ошибка проверки.</p>';
        }
    });

    btnAuditAAOIFI.addEventListener('click', async () => {
        const text = halalClauseInput.value.trim();
        if (!text) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `<div class="loading-spinner"><p>${I18N.t('halalAuditingAAOIFI') || 'Финансовый аудит по стандартам AAOIFI...'}</p></div>`;

        try {
            const resp = await fetch('/api/v1/contracts/audit-aaoifi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            const data = await resp.json();
            renderAAOIFIResult(data);
        } catch (e) {
            halalAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Ошибка аудита AAOIFI.</p>';
        }
    });

    function renderHalalResult(data) {
        halalAuditResult.innerHTML = '';
        const matches = data.matches || [];

        if (matches.length === 0) {
            halalAuditResult.className = 'halal-audit-result halal-card-halal';
            halalAuditResult.innerHTML = `
                <div class="verdict-header" style="color: #34D399;">${I18N.t('verdictHalalDirectHeader') || '🟢 ПРЯМЫХ ЗАПРЕТОВ НЕ ОБНАРУЖЕНО (ХАЛЯЛЬ / ДОЗВОЛЕНО)'}</div>
                <div class="verdict-desc">${I18N.t('verdictHalalDirectDesc') || 'По введенному составу в базе стандартов Халяль признаков Харама не найдено.'}</div>
            `;
            return;
        }

        let html = '';
        matches.forEach(m => {
            const isHaram = m.verdict === 'HARAM';
            const verdictLabel = isHaram 
                ? (I18N.t('verdictHaramBadge') || '🔴 ХАРАМ (ЗАПРЕТНО)')
                : (I18N.t('verdictDoubtfulBadge') || '🟡 СОМНИТЕЛЬНО / ТРЕБУЕТ ПРОВЕРКИ');
            const quranRef = I18N.t('verdictQuranBasis', { ref: m.ayah_ref }) || `📖 Основа в Коране: ${m.ayah_ref}`;

            html += `
                <div style="background: ${isHaram ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)'}; border: 1px solid ${isHaram ? '#EF4444' : '#F59E0B'}; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                    <div style="font-weight: 800; font-size: 15px; color: ${isHaram ? '#FCA5A5' : '#FDE68A'};">
                        ${verdictLabel}: ${m.title_ru}
                    </div>
                    <div style="font-size: 13.5px; color: #E2E8F0; margin: 6px 0;">${m.description_ru}</div>
                    <div style="font-size: 12px; color: var(--gold-bright); font-weight: 600;">${quranRef}</div>
                </div>
            `;
        });
        halalAuditResult.innerHTML = html;
    }

    function renderAAOIFIResult(data) {
        halalAuditResult.innerHTML = '';
        const isCompliant = data.is_compliant;
        halalAuditResult.className = `halal-audit-result ${isCompliant ? 'halal-card-halal' : 'halal-card-haram'}`;

        let findingsHtml = '';
        (data.findings || []).forEach(f => {
            findingsHtml += `<li><strong>${f.standard}:</strong> ${f.issue_ru} [${f.severity}]</li>`;
        });

        const headerText = isCompliant 
            ? (I18N.t('aaoifiCompliantHeader') || '✅ СООТВЕТСТВУЕТ ШАРИАТСКИМ СТАНДАРТАМ AAOIFI')
            : (I18N.t('aaoifiNonCompliantHeader') || '❌ ОБНАРУЖЕНО НЕСООТВЕТСТВИЕ СТАНДАРТАМ AAOIFI');

        halalAuditResult.innerHTML = `
            <div class="verdict-header" style="color: ${isCompliant ? '#34D399' : '#F87171'};">
                ${headerText}
            </div>
            <div class="verdict-desc"><strong>${I18N.t('aaoifiContractType', { type: data.contract_type }) || `Тип договора: ${data.contract_type}`}</strong> • <strong>${data.quran_basis}</strong></div>
            ${findingsHtml ? `<ul style="padding-left: 20px; color: #FECACA;">${findingsHtml}</ul>` : ''}
        `;
    }

    function renderPDFAuditResult(audit) {
        halalAuditResult.innerHTML = '';
        const gRep = audit.guard_report || {};
        const aRep = audit.aaoifi_report || {};

        halalAuditResult.className = `halal-audit-result ${aRep.is_compliant ? 'halal-card-halal' : 'halal-card-haram'}`;
        halalAuditResult.innerHTML = `
            <div class="verdict-header" style="color: #38BDF8;">${I18N.t('pdfReportHeader') || '📑 ОФИЦИАЛЬНЫЙ АУДИТОРСКИЙ ОТЧЕТ AL-FURQAN AI'}</div>
            <div class="verdict-desc">
                <strong>${I18N.t('pdfPagesLabel', { pages: audit.total_pages })}</strong> • <strong>${I18N.t('pdfCharsLabel', { chars: (audit.text_length || 0).toLocaleString() })}</strong>
            </div>
            <div style="font-size: 13.5px; margin-bottom: 6px;">
                ${gRep.claims_detected 
                    ? (gRep.is_valid ? I18N.t('pdfQuotesClean') : I18N.t('pdfQuotesError'))
                    : I18N.t('pdfQuotesNone')}
            </div>
            <div style="font-size: 13.5px;">
                ${aRep.is_compliant 
                    ? I18N.t('pdfAaoifiClean')
                    : I18N.t('pdfAaoifiError')}
            </div>
        `;
    }

    // =========================================================================
    // 10. NAMAZ TIMES & ZAKAT CALCULATOR
    // =========================================================================
    cityPills.forEach(pill => {
        pill.addEventListener('click', () => {
            cityPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            const lat = parseFloat(pill.getAttribute('data-lat'));
            const lon = parseFloat(pill.getAttribute('data-lon'));
            loadNamazTimes(lat, lon);
        });
    });

    btnGetLocation.addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert("Геолокация не поддерживается вашим браузером.");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                cityPills.forEach(p => p.classList.remove('active'));
                loadNamazTimes(pos.coords.latitude, pos.coords.longitude);
            },
            (err) => alert("Не удалось получить местоположение: " + err.message)
        );
    });

    async function loadNamazTimes(lat, lon) {
        try {
            const resp = await fetch(`/api/v1/namaz/times?lat=${lat}&lon=${lon}`);
            const data = await resp.json();
            const times = data.prayer_times || {};

            timeFajr.textContent = times.fajr || '--:--';
            timeSunrise.textContent = times.sunrise || '--:--';
            timeDhuhr.textContent = times.dhuhr || '--:--';
            timeAsr.textContent = times.asr || '--:--';
            timeMaghrib.textContent = times.maghrib || '--:--';
            timeIsha.textContent = times.isha || '--:--';

            qiblaDegreeText.textContent = I18N.t('qiblaDegreePrefix', { deg: data.qibla_bearing_deg, dir: data.qibla_compass_direction || '' }) || `Кибла: ${data.qibla_bearing_deg}°`;
        } catch (e) {
            console.warn("Namaz fetch notice:", e);
        }
    }

    btnCalculateZakat.addEventListener('click', calculateZakat);

    async function calculateZakat() {
        const cash = parseFloat(zakatCash.value) || 0;
        const gold = parseFloat(zakatGold.value) || 0;
        const debts = parseFloat(zakatDebts.value) || 0;

        try {
            const resp = await fetch('/api/v1/zakat/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cash_savings: cash,
                    gold_grams: gold,
                    liabilities_due: debts,
                    currency: '₸'
                })
            });
            const res = await resp.json();

            zakatAmountText.textContent = `${Number(res.zakat_due).toLocaleString()} ₸`;
            if (res.is_obligatory) {
                zakatNoteText.textContent = I18N.t('zakatNoteObligatory', { threshold: Number(res.gold_nisab_threshold).toLocaleString() }) || `Имущество превышает Нисаб (~${Number(res.gold_nisab_threshold).toLocaleString()} ₸). Закят обязателен (2.5%).`;
            } else {
                zakatNoteText.textContent = I18N.t('zakatNoteExempt', { threshold: Number(res.gold_nisab_threshold).toLocaleString() }) || `Имущество меньше порога Нисаба (~${Number(res.gold_nisab_threshold).toLocaleString()} ₸). Закят не начисляется.`;
            }
        } catch (e) {
            console.warn("Zakat calculation notice:", e);
        }
    }

    // =========================================================================
    // 11. MODALS & FEEDBACK
    // =========================================================================
    btnToggleStandards.addEventListener('click', () => modalStandards.style.display = 'flex');
    btnCloseStandards.addEventListener('click', () => modalStandards.style.display = 'none');

    btnToggleGuide.addEventListener('click', () => modalGuide.style.display = 'flex');
    btnCloseGuide.addEventListener('click', () => modalGuide.style.display = 'none');

    btnToggleFeedback.addEventListener('click', () => modalFeedback.style.display = 'flex');
    btnCloseFeedback.addEventListener('click', () => modalFeedback.style.display = 'none');

    btnSubmitFeedback.addEventListener('click', async () => {
        const msg = feedbackMessage.value.trim();
        if (!msg) {
            alert("Пожалуйста, напишите сообщение.");
            return;
        }

        try {
            const resp = await fetch('/api/v1/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: feedbackName.value.trim() || 'Пользователь',
                    email_or_phone: feedbackContact.value.trim() || '',
                    category: 'suggestion',
                    message: msg
                })
            });
            const data = await resp.json();
            feedbackStatusText.textContent = '✅ ' + (I18N.t('feedbackSuccess') || 'Спасибо! Ваш отзыв успешно принят.');
            feedbackStatusText.style.color = '#34D399';
            feedbackMessage.value = '';
            setTimeout(() => { modalFeedback.style.display = 'none'; feedbackStatusText.textContent = ''; }, 2000);
        } catch (e) {
            feedbackStatusText.textContent = '❌ ' + (I18N.t('feedbackError') || 'Ошибка отправки отзыва.');
            feedbackStatusText.style.color = '#F87171';
        }
    });

    // Close modals on click outside
    window.addEventListener('click', (e) => {
        if (e.target === modalStandards) modalStandards.style.display = 'none';
        if (e.target === modalFeedback) modalFeedback.style.display = 'none';
        if (e.target === modalGuide) modalGuide.style.display = 'none';
    });

    // Language switch
    selectLanguage.addEventListener('change', (e) => {
        if (typeof I18N !== 'undefined' && I18N.setLanguage) {
            I18N.setLanguage(e.target.value);
        }
    });

    // Start App
    await initApp();
});
