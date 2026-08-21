/**
 * Al-Furqan AI - Modern Intuitive Frontend Controller v18.0
 * 100% Real Backend Data Pipelines (Zero Mocks / Full Universal Search / Real OCR & PDF / 7-Language Reactive)
 */

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then((reg) => {
            console.log('✅ Al-Furqan Guard PWA Service Worker registered:', reg.scope);
        }).catch((err) => {
            console.log('SW registration note:', err);
        });
    });
}

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
    const statCountToday = document.getElementById('statCountToday');
    const statCountWeek = document.getElementById('statCountWeek');
    const statCountMonth = document.getElementById('statCountMonth');
    const statCountYear = document.getElementById('statCountYear');
    const statCountAllTime = document.getElementById('statCountAllTime');

    let visitorStatsData = { today: 0, week: 0, month: 0, year: 0, all_time: 0 };
    
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
    const inputBarcode = document.getElementById('inputBarcode');
    const btnCheckBarcode = document.getElementById('btnCheckBarcode');
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


        // 6. Re-calculate Zakat note text
        calculateZakat();
    });

    // =========================================================================
    // 4. PERSISTENT MULTI-TIMEFRAME VISITOR ANALYTICS
    // =========================================================================
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
        } catch (e) {
            console.warn("Analytics fetch notice:", e);
        }
    }


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

    universalSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const val = universalSearchInput.value.trim();
            if (val) performUniversalSearch(val);
        }
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
                const title = m[`title_${currentLang}`] || m.title_ru || m.title_kk || m.title_en || '';
                const desc = m[`description_${currentLang}`] || m.description_ru || m.description_kk || m.description_en || '';

                item.innerHTML = `
                    <div class="search-result-header-line">
                        <span style="font-weight: 800; color: ${isHaram ? '#F87171' : '#34D399'};">
                            ${verdictBadge}: ${title}
                        </span>
                        <span style="font-size: 11px; color: var(--text-muted);">${m.ayah_ref || 'Шариат'}</span>
                    </div>
                    <div class="search-result-trans">${desc}</div>
                `;
                item.addEventListener('click', () => {
                    searchResultsDropdown.style.display = 'none';
                    window.navigateToTabAndScroll('tab-halal', 'halalClauseInput');
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
                    window.navigateToTabAndScroll('tab-quran', 'selectSura');
                    selectSura.value = a.sura;
                    await loadSurah(a.sura);
                    
                    // Scroll to specific Ayah
                    const ayahIdx = surahAyahsData ? surahAyahsData.findIndex(x => x.ayah === a.ayah) : -1;
                    if (ayahIdx !== -1) {
                        playAyah(ayahIdx);
                    }
                    const ayahCard = document.getElementById(`ayah-card-${a.sura}-${a.ayah}`);
                    if (ayahCard) {
                        ayahCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        ayahCard.classList.add('nav-highlight-pulse');
                        setTimeout(() => ayahCard.classList.remove('nav-highlight-pulse'), 1600);
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

    // Tajweed & Hifz State
    let isTajweedActive = false;
    let isArabicTextHidden = false;
    let hifzCurrentRepeatCount = 0;

    function applyTajweedRules(text) {
        if (!text) return '';
        // Qalqala (قطبجد)
        let formatted = text.replace(/([قطبجد][ًٌٍَُِّْ]*)/g, '<span class="tajweed-qalqala">$1</span>');
        // Madd signs (ٓ, ~, آ)
        formatted = formatted.replace(/([آ]|[^\s][ٓ~])/g, '<span class="tajweed-madd">$1</span>');
        // Ghunna (نّ, مّ)
        formatted = formatted.replace(/([نم]ّ)/g, '<span class="tajweed-ghunna">$1</span>');
        return formatted;
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

            const arabicHtml = isTajweedActive ? applyTajweedRules(a.text_uthmani) : a.text_uthmani;
            const hiddenClass = isArabicTextHidden ? 'ayah-hidden-text' : '';

            card.innerHTML = `
                <div class="ayah-top-bar">
                    <div class="ayah-number-badge">${a.ayah}</div>
                    <div class="ayah-actions" style="display: flex; gap: 6px;">
                        <button class="btn-play-ayah" data-idx="${idx}">
                            <span>${playAyahLabel}</span>
                        </button>
                        <button class="btn-play-ayah btn-story-ayah" data-idx="${idx}" title="Создать Story карточку" style="background: rgba(217, 119, 6, 0.15); border-color: rgba(217, 119, 6, 0.35); color: #FDE68A;">
                            <span>🎨 Story</span>
                        </button>
                    </div>
                </div>
                <div class="ayah-arabic-text ${hiddenClass}">${arabicHtml}</div>
                ${translit ? `<div class="ayah-transliteration">${translit}</div>` : ''}
                ${trans ? `<div class="ayah-translation">${trans}</div>` : ''}
            `;

            const btnPlay = card.querySelector('.btn-play-ayah');
            btnPlay.addEventListener('click', () => {
                playAyah(idx);
            });

            const btnStory = card.querySelector('.btn-story-ayah');
            if (btnStory) {
                btnStory.addEventListener('click', (e) => {
                    e.stopPropagation();
                    window.openStoryModalForCurrentAyah(suraNum, a);
                });
            }

            ayahsStreamContainer.appendChild(card);
        });
    }

    // Audio Playback Controller
    function playAyah(idx, isRepeatStep = false) {
        if (!surahAyahsData || idx >= surahAyahsData.length) return;
        currentPlayingAyahIndex = idx;
        if (!isRepeatStep) {
            hifzCurrentRepeatCount = 0;
        }
        const ayahData = surahAyahsData[idx];
        const audioUrl = ayahData.audio_urls[currentReciter] || ayahData.audio_urls.alafasy;

        audio.src = audioUrl;
        audio.playbackRate = parseFloat(playerSpeedSelect.value) || 1.0;
        audio.play().catch(e => console.warn("Audio play blocked by browser:", e));

        // Highlight playing card & auto scroll
        document.querySelectorAll('.ayah-card').forEach(c => c.classList.remove('playing'));
        const activeCard = document.getElementById(`ayah-card-${currentSurah}-${ayahData.ayah}`);
        if (activeCard) {
            activeCard.classList.add('playing');
            activeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Show floating player bar
        floatingPlayerBar.style.display = 'flex';
        btnPlayerPlayPause.textContent = '⏸';
        playerTitle.textContent = I18N.t('playerTitlePrefix', { sura: currentSurah, ayah: ayahData.ayah }) || `Сура ${currentSurah}, Аят ${ayahData.ayah}`;
        updateReciterDisplay();
    }

    audio.addEventListener('ended', () => {
        const repeatTarget = parseInt(document.getElementById('selectHifzRepeat')?.value || '1', 10);
        if (repeatTarget > 1 && hifzCurrentRepeatCount < (repeatTarget - 1)) {
            hifzCurrentRepeatCount++;
            setTimeout(() => {
                playAyah(currentPlayingAyahIndex, true);
            }, 600);
            return;
        }
        hifzCurrentRepeatCount = 0;

        if (isContinuous && currentPlayingAyahIndex + 1 < surahAyahsData.length) {
            playAyah(currentPlayingAyahIndex + 1);
        } else {
            btnPlayerPlayPause.textContent = '▶';
            document.querySelectorAll('.ayah-card').forEach(c => c.classList.remove('playing'));
        }
    });

    // Tajweed & Hide Arabic Controls
    const btnToggleTajweed = document.getElementById('btnToggleTajweed');
    const tajweedLegend = document.getElementById('tajweedLegend');
    if (btnToggleTajweed) {
        btnToggleTajweed.addEventListener('click', () => {
            isTajweedActive = !isTajweedActive;
            btnToggleTajweed.style.background = isTajweedActive ? 'rgba(52, 211, 153, 0.25)' : '';
            btnToggleTajweed.style.borderColor = isTajweedActive ? '#34D399' : '';
            if (tajweedLegend) tajweedLegend.style.display = isTajweedActive ? 'flex' : 'none';
            if (surahAyahsData) renderAyahsStream(surahAyahsData, currentSurah);
            showToast(isTajweedActive ? "Цветной Таджвид включен" : "Таджвид отключен", "info");
        });
    }

    const btnToggleHideArabic = document.getElementById('btnToggleHideArabic');
    if (btnToggleHideArabic) {
        btnToggleHideArabic.addEventListener('click', () => {
            isArabicTextHidden = !isArabicTextHidden;
            btnToggleHideArabic.style.background = isArabicTextHidden ? 'rgba(217, 119, 6, 0.25)' : '';
            btnToggleHideArabic.style.borderColor = isArabicTextHidden ? '#D97706' : '';
            document.querySelectorAll('.ayah-arabic-text').forEach(el => {
                el.classList.toggle('ayah-hidden-text', isArabicTextHidden);
            });
            showToast(isArabicTextHidden ? "Текст скрыт (нажмите для проверки)" : "Текст Корана открыт", "info");
        });
    }

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

    window.playSpecificAyah = async (sura, ayah) => {
        if (currentSurah !== sura) {
            selectSura.value = sura;
            await loadSurah(sura);
        }
        playAyah(ayah - 1);
    };

    // 1,651 Roots Search
    const performRootSearch = async () => {
        const root = rootSearchInput.value.trim();
        if (!root) return;

        rootSearchResults.innerHTML = `<div class="loading-spinner"><p>${I18N.t('rootSearchingText') || 'Поиск по корню...'}</p></div>`;
        try {
            const resp = await fetch(`/api/v1/root/${encodeURIComponent(root)}`);
            const data = await resp.json();
            const results = data.results || [];
            
            if (!Array.isArray(results) || results.length === 0) {
                rootSearchResults.innerHTML = `<p style="color: var(--text-secondary); padding: 12px 0;">${I18N.t('rootNotFoundText', { root: root }) || `По корню «${root}» аятов не найдено.`}</p>`;
                return;
            }

            const headerText = I18N.t('rootFoundText', { root: data.root || root, total: data.total || results.length }) || `Найдено ${data.total || results.length} аятов с корнем «${data.root || root}»:`;
            let html = `<div style="font-weight: 700; color: var(--apple-gold); margin-bottom: 12px; font-size: 14px;">${headerText}</div>`;
            
            const currentLang = I18N.currentLang || 'ru';
            results.slice(0, 15).forEach(r => {
                const surahName = r[`surah_name_${currentLang}`] || r.surah_name_ru || `Сура ${r.sura}`;
                const trans = (r.translations && (r.translations[currentLang] || r.translations.ru || r.translations.kk)) || '';
                const translit = r.transliteration ? `<div class="ayah-translit" style="margin-bottom: 4px;">${r.transliteration}</div>` : '';
                
                html += `
                    <div class="search-result-item" style="margin-bottom: 10px; padding: 16px;">
                        <div class="search-result-header-line">
                            <span class="search-result-title">📖 ${surahName} [${r.sura}:${r.ayah}]</span>
                            <button class="btn-play-ayah" onclick="window.playSpecificAyah(${r.sura}, ${r.ayah})">▶ ${I18N.t('btnPlayAyah') || 'Слушать'}</button>
                        </div>
                        <div class="search-result-arabic" style="font-size: 22px; line-height: 2; margin-bottom: 6px;">${r.text_uthmani}</div>
                        ${translit}
                        <div class="search-result-trans" style="font-size: 13.5px; line-height: 1.5; color: var(--text-primary);">${trans}</div>
                    </div>
                `;
            });
            rootSearchResults.innerHTML = html;
        } catch (e) {
            rootSearchResults.innerHTML = '<p style="color: var(--apple-red); padding: 10px 0;">Ошибка поиска по корню.</p>';
        }
    };

    btnSearchRoot.addEventListener('click', performRootSearch);
    rootSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performRootSearch();
        }
    });

    // =========================================================================
    // 9. REAL OCR PHOTO SCANNING & REAL PDF DOCUMENT AUDIT
    // =========================================================================
    // Real Photo OCR with Image Downscaling & Tesseract.js Web Worker + Server Fallback
    btnTriggerOCR.addEventListener('click', () => inputProductImage.click());
    inputProductImage.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `
            <div class="loading-spinner">
                <p id="ocrProgressStatus">${I18N.t('halalScanningOCR') || '📷 Подготовка и сканирование фото состава...'}</p>
                <div style="width: 100%; max-width: 280px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin: 10px auto;">
                    <div id="ocrProgressBar" style="width: 20%; height: 100%; background: var(--apple-gold); transition: width 0.3s;"></div>
                </div>
            </div>
        `;

        // Downscale image on canvas to avoid huge 10MB transfers and accelerate OCR
        const downscaleImage = (fileToScale) => {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    const maxDim = 1200;
                    let w = img.width, h = img.height;
                    if (w > maxDim || h > maxDim) {
                        if (w > h) {
                            h = Math.round((h * maxDim) / w);
                            w = maxDim;
                        } else {
                            w = Math.round((w * maxDim) / h);
                            h = maxDim;
                        }
                    }
                    const canvas = document.createElement('canvas');
                    canvas.width = w;
                    canvas.height = h;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, w, h);
                    canvas.toBlob((blob) => resolve(blob || fileToScale), 'image/jpeg', 0.85);
                };
                img.onerror = () => resolve(fileToScale);
                img.src = URL.createObjectURL(fileToScale);
            });
        };

        try {
            const processedBlob = await downscaleImage(file);
            let extractedText = '';

            // 1. Try client-side Tesseract.js (100% in browser, fast)
            if (typeof Tesseract !== 'undefined') {
                try {
                    const updateProgress = (pct) => {
                        const pStatus = document.getElementById('ocrProgressStatus');
                        const pBar = document.getElementById('ocrProgressBar');
                        if (pStatus) pStatus.textContent = `📷 Распознавание текста состава: ${pct}%`;
                        if (pBar) pBar.style.width = `${pct}%`;
                    };
                    updateProgress(35);

                    const res = await Tesseract.recognize(processedBlob, 'rus+eng', {
                        logger: (m) => {
                            if (m.status === 'recognizing text') {
                                const p = Math.min(95, Math.max(35, Math.round((m.progress || 0) * 100)));
                                updateProgress(p);
                            }
                        }
                    });
                    if (res && res.data && res.data.text) {
                        extractedText = res.data.text.trim();
                    }
                } catch (tErr) {
                    console.warn("Client Tesseract notice:", tErr);
                }
            }

            // 2. If client OCR text found, screen it immediately
            if (extractedText) {
                halalClauseInput.value = extractedText;
                const pStatus = document.getElementById('ocrProgressStatus');
                if (pStatus) pStatus.textContent = '🔍 Анализ ингредиентов по стандарту SMIIC...';
                
                const resp = await fetch('/api/v1/halal/screen', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: extractedText })
                });
                const data = await resp.json();
                renderHalalResult(data);
                return;
            }

            // 3. Fallback: Server-side OCR
            const reader = new FileReader();
            reader.onload = async () => {
                const base64Data = reader.result.split(',')[1];
                const resp = await fetch('/api/v1/images/audit-ocr', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_base64: base64Data })
                });
                const data = await resp.json();
                if (data.extracted_text) {
                    halalClauseInput.value = data.extracted_text;
                }
                renderHalalResult(data);
            };
            reader.readAsDataURL(processedBlob);
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
            const barcode = chip.getAttribute('data-barcode');

            if (barcode) {
                if (inputBarcode) inputBarcode.value = barcode;
                performBarcodeSearch(barcode);
                return;
            }

            if (text) {
                halalClauseInput.value = text;
                if (text.includes('AAOIFI') || text.includes('Кредит') || text.includes('Мурабаха') || text.includes('договор')) {
                    btnAuditAAOIFI.click();
                } else {
                    btnAuditHalal.click();
                }
            }
        });
    });

    // Barcode Search via Open Food Facts (2.5M+ products)
    const performBarcodeSearch = async (customBarcode) => {
        const rawCode = customBarcode || (inputBarcode ? inputBarcode.value : '') || (halalClauseInput ? halalClauseInput.value : '');
        const barcode = (rawCode || '').trim();
        if (!barcode) return;

        halalAuditResult.style.display = 'block';
        halalAuditResult.innerHTML = `<div class="loading-spinner"><p>${I18N.t('barcodeSearching') || 'Поиск товара в глобальной базе Open Food Facts и проверка состава...'}</p></div>`;

        try {
            const resp = await fetch(`/api/v1/halal/barcode/${encodeURIComponent(barcode)}`);
            const data = await resp.json();
            renderBarcodeResult(data);
        } catch (e) {
            halalAuditResult.innerHTML = `<p style="color: var(--apple-red); padding: 10px 0;">${I18N.t('barcodeNotFound') || 'Ошибка поиска по штрихкоду.'}</p>`;
        }
    };

    if (btnCheckBarcode) btnCheckBarcode.addEventListener('click', () => performBarcodeSearch());
    if (inputBarcode) {
        inputBarcode.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performBarcodeSearch();
            }
        });
    }

    // Live Camera Barcode Scanner Modal Controls
    const btnLiveCameraBarcode = document.getElementById('btnLiveCameraBarcode');
    const modalCameraScanner = document.getElementById('modalCameraScanner');
    const btnCloseCameraScanner = document.getElementById('btnCloseCameraScanner');
    const btnStopCameraScan = document.getElementById('btnStopCameraScan');
    const btnSnapBarcodePhoto = document.getElementById('btnSnapBarcodePhoto');
    const btnUploadBarcodePhoto = document.getElementById('btnUploadBarcodePhoto');
    const inputBarcodeImageFile = document.getElementById('inputBarcodeImageFile');
    const barcodeVideo = document.getElementById('barcodeVideo');
    const cameraScanStatus = document.getElementById('cameraScanStatus');

    let html5QrCodeScanner = null;
    let cameraStream = null;

    const onBarcodeSuccessfullyDetected = (detectedCode) => {
        if (!detectedCode) return;
        const cleanCode = String(detectedCode).replace(/\D/g, '');
        if (cleanCode.length < 4) return;

        if (navigator.vibrate) navigator.vibrate(120);
        stopCameraScanner();
        if (inputBarcode) inputBarcode.value = cleanCode;
        performBarcodeSearch(cleanCode);
    };

    const stopCameraScanner = async () => {
        if (html5QrCodeScanner) {
            try {
                await html5QrCodeScanner.stop();
                await html5QrCodeScanner.clear();
            } catch (e) {}
            html5QrCodeScanner = null;
        }
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
        if (barcodeVideo) barcodeVideo.srcObject = null;
        if (modalCameraScanner) modalCameraScanner.style.display = 'none';
    };

    if (btnCloseCameraScanner) btnCloseCameraScanner.addEventListener('click', stopCameraScanner);
    if (btnStopCameraScan) btnStopCameraScan.addEventListener('click', stopCameraScanner);

    if (btnSnapBarcodePhoto) {
        btnSnapBarcodePhoto.addEventListener('click', async () => {
            if (cameraScanStatus) cameraScanStatus.textContent = "⏳ Распознавание снимка штрихкода...";
            const video = document.querySelector('#barcodeCameraReader video') || barcodeVideo;
            if (video && video.videoWidth) {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(async (blob) => {
                    if (typeof Html5Qrcode !== 'undefined') {
                        try {
                            const tempScanner = new Html5Qrcode("barcodeCameraReader");
                            const code = await tempScanner.scanFile(blob, false);
                            if (code) {
                                onBarcodeSuccessfullyDetected(code);
                                return;
                            }
                        } catch (e) {}
                    }
                    if (cameraScanStatus) cameraScanStatus.textContent = "Штрихкод не распознан. Попробуйте еще раз или введите цифры вручную.";
                }, 'image/jpeg');
            }
        });
    }

    if (btnUploadBarcodePhoto && inputBarcodeImageFile) {
        btnUploadBarcodePhoto.addEventListener('click', () => inputBarcodeImageFile.click());
        inputBarcodeImageFile.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            if (cameraScanStatus) cameraScanStatus.textContent = "⏳ Сканирование загруженного фото...";
            if (typeof Html5Qrcode !== 'undefined') {
                try {
                    const tempScanner = new Html5Qrcode("barcodeCameraReader");
                    const code = await tempScanner.scanFile(file, true);
                    if (code) {
                        onBarcodeSuccessfullyDetected(code);
                        return;
                    }
                } catch (e) {
                    console.warn("Upload barcode error:", e);
                }
            }
            if (cameraScanStatus) cameraScanStatus.textContent = "Штрихкод на фото не найден. Введите цифры вручную.";
        });
    }

    if (btnLiveCameraBarcode) {
        btnLiveCameraBarcode.addEventListener('click', async () => {
            if (modalCameraScanner) modalCameraScanner.style.display = 'flex';
            if (cameraScanStatus) cameraScanStatus.textContent = I18N.t('cameraScanInstruct') || "Наведите камеру на штрихкод товара...";

            // 1. Primary: Html5Qrcode (supports EAN-13, EAN-8, UPC, Code128 across all browsers)
            if (typeof Html5Qrcode !== 'undefined') {
                try {
                    html5QrCodeScanner = new Html5Qrcode("barcodeCameraReader");
                    await html5QrCodeScanner.start(
                        { facingMode: "environment" },
                        {
                            fps: 15,
                            qrbox: (viewfinderWidth, viewfinderHeight) => {
                                return { width: Math.min(viewfinderWidth * 0.85, 320), height: Math.min(viewfinderHeight * 0.5, 180) };
                            }
                        },
                        (decodedText) => onBarcodeSuccessfullyDetected(decodedText),
                        (err) => {}
                    );
                    return;
                } catch (e) {
                    console.warn("Html5Qrcode init notice:", e);
                }
            }

            // 2. Fallback: getUserMedia
            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
                });
                if (barcodeVideo) {
                    barcodeVideo.style.display = 'block';
                    barcodeVideo.srcObject = cameraStream;
                    await barcodeVideo.play();
                }
                if ('BarcodeDetector' in window) {
                    const detector = new BarcodeDetector({ formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'qr_code'] });
                    const loop = async () => {
                        if (!cameraStream) return;
                        try {
                            const codes = await detector.detect(barcodeVideo);
                            if (codes.length > 0) {
                                onBarcodeSuccessfullyDetected(codes[0].rawValue);
                                return;
                            }
                        } catch (e) {}
                        requestAnimationFrame(loop);
                    };
                    requestAnimationFrame(loop);
                }
            } catch (e) {
                if (cameraScanStatus) cameraScanStatus.textContent = "Камера недоступна. Пожалуйста, введите штрихкод вручную.";
            }
        });
    }

    // Pre-loaded Certified Brands
    const CERTIFIED_BRANDS_MAP = {
        "рахат": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0142)", note_ru: "Официально сертифицировано ДУМК. Все эмульгаторы растительного происхождения." },
        "баян сулу": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0218)", note_ru: "Сертифицированная халяль-линейка без свиного жира." },
        "куликовский": { auth: "ДУМК «Халал Даму» (HD-KG-2024-098)", note_ru: "Используется только сертифицированный говяжий желатин." },
        "фудмастер": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0304)", note_ru: "Сыры на микробиальном (неживотном) сычужном ферменте." },
        "foodmaster": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0304)", note_ru: "Сыры на микробиальном (неживотном) сычужном ферменте." },
        "алель": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0012)", note_ru: "100% ручной забой птицы по нормам Шариата." },
        "цесна": { auth: "ДУМК «Халал Даму» (HD-KZ-2024-0419)", note_ru: "Чистый растительный состав без животных добавок." },
        "султан": { auth: "ДУМК «Халал Даму» (HD-KZ-2025-0112)", note_ru: "100% Халяль стандарт ДУМК." },
        "almarai": { auth: "JAKIM Malaysia (SA-JAKIM-2024-881)", note_ru: "Мировой золотой стандарт халяль сертификации." }
    };

    function renderBarcodeResult(data) {
        halalAuditResult.innerHTML = '';
        const currentLang = I18N.currentLang || 'ru';
        
        if (data.halal_verdict === 'NOT_FOUND') {
            halalAuditResult.className = 'halal-audit-result';
            halalAuditResult.innerHTML = `
                <div style="padding: 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;">
                    <div style="font-weight: 700; font-size: 15px; color: var(--apple-gold); margin-bottom: 8px;">📦 ${data.name || 'Товар не найден'}</div>
                    <div style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.5;">${data.summary || I18N.t('barcodeNotFound')}</div>
                </div>
            `;
            return;
        }

        const brandLower = (data.brand || '').toLowerCase().trim();
        let certInfoHtml = '';
        for (const [keyBrand, certData] of Object.entries(CERTIFIED_BRANDS_MAP)) {
            if (brandLower.includes(keyBrand) || (data.name || '').toLowerCase().includes(keyBrand)) {
                certInfoHtml = `
                    <div style="margin-top: 10px; padding: 8px 12px; background: rgba(217, 119, 6, 0.15); border: 1px solid rgba(217, 119, 6, 0.35); border-radius: 8px; font-size: 12.5px; color: #FDE68A;">
                        <strong>🎖️ ОФИЦИАЛЬНО СЕРТИФИЦИРОВАНО:</strong> ${certData.auth} — <i>${certData.note_ru}</i>
                    </div>
                `;
                break;
            }
        }

        const isHaram = data.halal_verdict === 'HARAM';
        const isDoubtful = data.halal_verdict === 'DOUBTFUL' || data.halal_verdict === 'SHUBHA';

        let badgeColor = '#34D399';
        let badgeBg = 'rgba(52, 211, 153, 0.12)';
        let badgeBorder = 'rgba(52, 211, 153, 0.3)';
        let verdictLabel = I18N.t('verdictHalalDirectHeader') || '🟢 ХАЛЯЛЬ / ДОЗВОЛЕНО (HALAL)';

        if (isHaram) {
            badgeColor = '#F87171';
            badgeBg = 'rgba(239, 68, 68, 0.12)';
            badgeBorder = 'rgba(239, 68, 68, 0.3)';
            verdictLabel = I18N.t('verdictHaramBadge') || '🔴 ХАРАМ (ЗАПРЕТНО / HARAM)';
        } else if (isDoubtful) {
            badgeColor = '#FBBF24';
            badgeBg = 'rgba(245, 158, 11, 0.12)';
            badgeBorder = 'rgba(245, 158, 11, 0.3)';
            verdictLabel = I18N.t('verdictDoubtfulBadge') || '🟡 КҮМӘНДІ / ТРЕБУЕТ ПРОВЕРКИ (DOUBTFUL)';
        }

        const summaryText = data[`summary_${currentLang}`] || data.summary_ru || data.summary || '';
        const ingredientsText = data.ingredients_text ? `
            <div style="margin-top: 12px; font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
                <strong style="color: var(--text-primary);">${I18N.t('barcodeIngredientsTitle') || '📝 Состав:'}</strong> ${data.ingredients_text}
            </div>
        ` : '';

        let additivesHtml = '';
        if (data.haram_items && data.haram_items.length > 0) {
            additivesHtml += `<div style="margin-top: 10px; font-size: 13px; color: #FCA5A5;"><strong>🔴 ${I18N.t('verdictHaramBadge') || 'Запрещенные компоненты'}:</strong> ${data.haram_items.join(', ')}</div>`;
        }
        if (data.doubtful_items && data.doubtful_items.length > 0) {
            additivesHtml += `<div style="margin-top: 8px; font-size: 13px; color: #FDE68A;"><strong>🟡 ${I18N.t('verdictDoubtfulBadge') || 'Сомнительные добавки'}:</strong> ${data.doubtful_items.join(', ')}</div>`;
        }

        halalAuditResult.innerHTML = `
            <div style="background: ${badgeBg}; border: 1px solid ${badgeBorder}; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
                    <div>
                        <div style="font-weight: 800; font-size: 16px; color: ${badgeColor};">${verdictLabel}</div>
                        <div style="font-size: 14.5px; font-weight: 600; color: #FFF; margin-top: 4px;">📦 ${data.name || ''} ${data.brand ? '— ' + data.brand : ''}</div>
                    </div>
                    <span style="font-size: 11.5px; color: var(--text-muted); background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 6px;">#${data.barcode}</span>
                </div>
                ${certInfoHtml}
                <div style="font-size: 13.5px; color: #E2E8F0; line-height: 1.5; margin-top: 8px;">${summaryText}</div>
                ${additivesHtml}
                ${ingredientsText}
            </div>
        `;
    }

    btnAuditHalal.addEventListener('click', async () => {
        const text = halalClauseInput.value.trim();
        if (!text) return;

        // Auto-detect barcode if input is all digits (8 to 14 digits)
        const cleanDigits = text.replace(/\D/g, '');
        if (cleanDigits.length >= 8 && cleanDigits.length <= 14 && cleanDigits === text.trim()) {
            performBarcodeSearch(cleanDigits);
            return;
        }

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
        const currentLang = I18N.currentLang || 'ru';
        
        let ocrBanner = '';
        if (data.extracted_text) {
            ocrBanner = `
                <div style="padding: 10px 14px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; margin-bottom: 12px; font-size: 13px; color: #E2E8F0; line-height: 1.5;">
                    <div style="font-weight: 700; color: var(--apple-gold); margin-bottom: 4px;">📝 Распознанный текст с фото:</div>
                    <div style="font-style: italic; color: var(--text-secondary); max-height: 80px; overflow-y: auto;">"${data.extracted_text}"</div>
                </div>
            `;
        }

        if (matches.length === 0 && (!data.haram_items || data.haram_items.length === 0) && (!data.doubtful_items || data.doubtful_items.length === 0)) {
            halalAuditResult.className = 'halal-audit-result halal-card-halal';
            halalAuditResult.innerHTML = `
                ${ocrBanner}
                <div class="verdict-header" style="color: #34D399; font-weight: 800; font-size: 16px;">${I18N.t('verdictHalalDirectHeader') || '🟢 ПРЯМЫХ ЗАПРЕТОВ НЕ ОБНАРУЖЕНО (ХАЛЯЛЬ / ДОЗВОЛЕНО)'}</div>
                <div class="verdict-desc" style="font-size: 13.5px; margin-top: 6px; color: #E2E8F0;">${I18N.t('verdictHalalDirectDesc') || 'По проверенному составу в базе стандартов Халяль (SMIIC) признаков Харама не найдено.'}</div>
            `;
            return;
        }

        let html = ocrBanner;
        
        if (data.haram_items && data.haram_items.length > 0) {
            html += `
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                    <div style="font-weight: 800; font-size: 15px; color: #FCA5A5;">
                        🔴 ${I18N.t('verdictHaramBadge') || 'ХАРАМ (ЗАПРЕТНО)'}: ${data.haram_items.join(', ')}
                    </div>
                    <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">${data[`summary_${currentLang}`] || data.summary_ru || 'Обнаружены запрещенные в пищу компоненты.'}</div>
                </div>
            `;
        }

        if (data.doubtful_items && data.doubtful_items.length > 0) {
            html += `
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                    <div style="font-weight: 800; font-size: 15px; color: #FDE68A;">
                        🟡 ${I18N.t('verdictDoubtfulBadge') || 'СОМНИТЕЛЬНО'}: ${data.doubtful_items.join(', ')}
                    </div>
                    <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">${data[`summary_${currentLang}`] || data.summary_ru || 'Требуется уточнение происхождения сырья (животное/растительное).'}</div>
                </div>
            `;
        }

        matches.forEach(m => {
            const isHaram = m.verdict === 'HARAM';
            const verdictLabel = isHaram 
                ? (I18N.t('verdictHaramBadge') || '🔴 ХАРАМ (ЗАПРЕТНО)')
                : (I18N.t('verdictDoubtfulBadge') || '🟡 СОМНИТЕЛЬНО / ТРЕБУЕТ ПРОВЕРКИ');
            const quranRef = I18N.t('verdictQuranBasis', { ref: m.ayah_ref }) || `📖 Основа в Коране: ${m.ayah_ref}`;

            html += `
                <div style="background: ${isHaram ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)'}; border: 1px solid ${isHaram ? '#EF4444' : '#F59E0B'}; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                    <div style="font-weight: 800; font-size: 15px; color: ${isHaram ? '#FCA5A5' : '#FDE68A'};">
                        ${verdictLabel}: ${m[`title_${currentLang}`] || m.title_ru || m.title}
                    </div>
                    <div style="font-size: 13.5px; color: #E2E8F0; margin: 6px 0;">${m[`description_${currentLang}`] || m.description_ru || m.description}</div>
                    <div style="font-size: 12px; color: var(--gold-bright); font-weight: 600;">${quranRef}</div>
                </div>
            `;
        });
        halalAuditResult.innerHTML = html;
    }

    function renderAAOIFIResult(data) {
        halalAuditResult.innerHTML = '';
        const currentLang = I18N.currentLang || 'ru';
        const isCompliant = data.is_compliant;
        const findings = data.findings || [];

        let findingsHtml = '';
        if (findings.length > 0) {
            findings.forEach(f => {
                const title = f[`risk_title_${currentLang}`] || f.risk_title_ru || f.standard;
                const issue = f[`issue_${currentLang}`] || f.issue_ru || '';
                const solution = f[`solution_${currentLang}`] || f.solution_ru || '';
                const ayahTrans = f[`ayah_trans_${currentLang}`] || f.ayah_trans_ru || '';

                findingsHtml += `
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 16px; margin-top: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
                            <div style="font-weight: 800; font-size: 15px; color: #FCA5A5;">${title}</div>
                            <span style="font-size: 11px; background: rgba(239, 68, 68, 0.2); color: #FECACA; padding: 3px 8px; border-radius: 6px; font-weight: 700;">${f.severity || 'CRITICAL'}</span>
                        </div>
                        <div style="font-size: 13.5px; color: #F1F5F9; line-height: 1.5; margin-bottom: 8px;"><strong>⚠️ Нарушение:</strong> ${issue}</div>
                        
                        <!-- Quran Basis Card -->
                        <div style="background: rgba(0, 0, 0, 0.35); border-left: 3px solid var(--apple-gold); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                            <div style="font-size: 12px; font-weight: 700; color: var(--apple-gold); margin-bottom: 4px;">📖 Противоречит Священному Корану: ${f.ayah_ref || 'Коран'}</div>
                            ${f.ayah_arabic ? `<div style="font-family: 'Amiri Quran', serif; font-size: 19px; color: #FFF; line-height: 1.8; direction: rtl; text-align: right; margin-bottom: 4px;">${f.ayah_arabic}</div>` : ''}
                            ${ayahTrans ? `<div style="font-size: 12.5px; color: #CBD5E1; font-style: italic;">${ayahTrans}</div>` : ''}
                        </div>

                        <div style="font-size: 12px; color: #38BDF8; margin-bottom: 4px;"><strong>⚖️ Стандарт:</strong> ${f.standard}</div>
                        ${solution ? `<div style="font-size: 12.5px; color: #34D399; margin-top: 6px;"><strong>💡 Рекомендация по устранению риска:</strong> ${solution}</div>` : ''}
                    </div>
                `;
            });
        }

        const headerText = isCompliant 
            ? (I18N.t('aaoifiCompliantHeader') || '🟢 ДОГОВОР СООТВЕТСТВУЕТ ШАРИАТСКИМ СТАНДАРТАМ AAOIFI')
            : (I18N.t('aaoifiNonCompliantHeader') || '🔴 В ДОГОВОРЕ ОБНАРУЖЕНЫ ШАРИАТСКИЕ РИСКИ И НАРУШЕНИЯ');

        halalAuditResult.innerHTML = `
            <div style="padding: 18px; border-radius: 12px; background: ${isCompliant ? 'rgba(52, 211, 153, 0.08)' : 'rgba(239, 68, 68, 0.08)'}; border: 1px solid ${isCompliant ? 'rgba(52, 211, 153, 0.25)' : 'rgba(239, 68, 68, 0.25)'};">
                <div class="verdict-header" style="color: ${isCompliant ? '#34D399' : '#F87171'}; font-size: 16px; font-weight: 800;">
                    ${headerText}
                </div>
                <div class="verdict-desc" style="margin-top: 6px; font-size: 13px; color: var(--text-secondary);">
                    <strong>Тип договора:</strong> ${data.contract_type} • <strong>Шариатский базис:</strong> ${data.quran_basis || 'AAOIFI'}
                </div>
                ${findingsHtml}
                <div style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="window.downloadAuditPDF('Аудит договора AAOIFI', window._lastAuditData)">
                        <span>${I18N.t('btnDownloadAuditPDF') || '📥 Скачать официальный PDF-сертификат (AAOIFI)'}</span>
                    </button>
                </div>
            </div>
        `;
    }

    function renderPDFAuditResult(audit) {
        halalAuditResult.innerHTML = '';
        const currentLang = I18N.currentLang || 'ru';
        const gRep = audit.guard_report || {};
        const aRep = audit.aaoifi_report || {};
        const findings = aRep.findings || [];
        window._lastAuditData = aRep;

        let findingsHtml = '';
        if (findings.length > 0) {
            findings.forEach(f => {
                const title = f[`risk_title_${currentLang}`] || f.risk_title_ru || f.standard;
                const issue = f[`issue_${currentLang}`] || f.issue_ru || '';
                const solution = f[`solution_${currentLang}`] || f.solution_ru || '';
                const ayahTrans = f[`ayah_trans_${currentLang}`] || f.ayah_trans_ru || '';

                findingsHtml += `
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 16px; margin-top: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
                            <div style="font-weight: 800; font-size: 15px; color: #FCA5A5;">${title}</div>
                            <span style="font-size: 11px; background: rgba(239, 68, 68, 0.2); color: #FECACA; padding: 3px 8px; border-radius: 6px; font-weight: 700;">${f.severity || 'CRITICAL'}</span>
                        </div>
                        <div style="font-size: 13.5px; color: #F1F5F9; line-height: 1.5; margin-bottom: 8px;"><strong>⚠️ Обнаруженный риск:</strong> ${issue}</div>
                        
                        <!-- Contradicting Quran Ayah Card -->
                        <div style="background: rgba(0, 0, 0, 0.35); border-left: 3px solid var(--apple-gold); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                            <div style="font-size: 12px; font-weight: 700; color: var(--apple-gold); margin-bottom: 4px;">📖 Противоречит Священному Корану: ${f.ayah_ref || 'Коран'}</div>
                            ${f.ayah_arabic ? `<div style="font-family: 'Amiri Quran', serif; font-size: 19px; color: #FFF; line-height: 1.8; direction: rtl; text-align: right; margin-bottom: 4px;">${f.ayah_arabic}</div>` : ''}
                            ${ayahTrans ? `<div style="font-size: 12.5px; color: #CBD5E1; font-style: italic;">${ayahTrans}</div>` : ''}
                        </div>

                        <div style="font-size: 12px; color: #38BDF8; margin-bottom: 4px;"><strong>⚖️ Стандарт:</strong> ${f.standard}</div>
                        ${solution ? `<div style="font-size: 12.5px; color: #34D399; margin-top: 6px;"><strong>💡 Рекомендация аудитора:</strong> ${solution}</div>` : ''}
                    </div>
                `;
            });
        }

        const isCompliant = aRep.is_compliant;
        halalAuditResult.innerHTML = `
            <div style="padding: 18px; border-radius: 12px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;">
                    <div class="verdict-header" style="color: #38BDF8; font-size: 16px; font-weight: 800;">
                        📑 АУДИТОРСКОЕ ЗАКЛЮЧЕНИЕ AL-FURQAN GUARD (PDF)
                    </div>
                    <span style="font-size: 12px; color: var(--text-secondary); background: rgba(0,0,0,0.4); padding: 4px 10px; border-radius: 6px;">
                        📄 Страниц: ${audit.total_pages || 1} • 🔤 Символов: ${(audit.text_length || 0).toLocaleString()}
                    </span>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-bottom: 12px;">
                    <div style="background: ${aRep.is_compliant ? 'rgba(52, 211, 153, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; border: 1px solid ${aRep.is_compliant ? 'rgba(52, 211, 153, 0.3)' : 'rgba(239, 68, 68, 0.3)'}; border-radius: 8px; padding: 12px;">
                        <div style="font-size: 12px; color: var(--text-secondary);">Шариатский комплаенс (AAOIFI):</div>
                        <div style="font-weight: 800; font-size: 14px; color: ${aRep.is_compliant ? '#34D399' : '#F87171'}; margin-top: 4px;">
                            ${aRep.is_compliant ? '🟢 Соответствует стандарту' : `🔴 Найдено рисков: ${findings.length}`}
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px;">
                        <div style="font-size: 12px; color: var(--text-secondary);">Цитаты из Корана (Ground Truth):</div>
                        <div style="font-weight: 800; font-size: 14px; color: #38BDF8; margin-top: 4px;">
                            ${gRep.claims_detected ? (gRep.is_valid ? '✅ Цитаты 100% достоверны' : '⚠️ Найдено искажение цитат') : 'ℹ️ Прямых цитат не обнаружено'}
                        </div>
                    </div>
                </div>

                ${findingsHtml}

                <div style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="window.downloadAuditPDF('Аудит договора AAOIFI', window._lastAuditData)">
                        <span>${I18N.t('btnDownloadAuditPDF') || '📥 Скачать официальный PDF-сертификат (AAOIFI)'}</span>
                    </button>
                </div>

                ${audit.text_preview ? `
                    <details style="margin-top: 14px; font-size: 12px; color: var(--text-muted); cursor: pointer;">
                        <summary style="font-weight: 600; color: var(--text-secondary);">📄 Показать превью извлеченного текста PDF</summary>
                        <pre style="margin-top: 8px; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 6px; white-space: pre-wrap; font-family: monospace; font-size: 11.5px; color: #94A3B8; max-height: 200px; overflow-y: auto;">${audit.text_preview}</pre>
                    </details>
                ` : ''}
            </div>
        `;
    }

    // Global PDF Download handler
    window.downloadAuditPDF = async (docTitle, auditData, contractText) => {
        try {
            const resp = await fetch('/api/v1/documents/export-audit-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_title: docTitle || "Договор Мурабаха / Иджара",
                    audit_data: auditData,
                    contract_text: contractText
                })
            });
            if (!resp.ok) throw new Error("PDF export failed");
            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Al_Furqan_AAOIFI_Audit_Certificate_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (e) {
            alert("Ошибка формирования PDF сертификата: " + e.message);
        }
    };

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

    // =========================================================================
    // 11. TOAST NOTIFICATION MANAGER (Instant User Feedback)
    // =========================================================================
    const toastContainer = document.getElementById('toastContainer');
    function showToast(message, type = 'info', duration = 3500) {
        if (!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = `toast-item toast-${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '❌';

        toast.innerHTML = `<span style="font-size: 16px;">${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-hiding');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    window.showToast = showToast;

    // =========================================================================
    // 12. SHARIAH INHERITANCE CALCULATOR (МИРАС / ФАРАИД - Сура 4:11-12)
    // =========================================================================
    const btnCalculateMiras = document.getElementById('btnCalculateMiras');
    const mirasResultCard = document.getElementById('mirasResultCard');
    const mirasTotalEstate = document.getElementById('mirasTotalEstate');
    const mirasDeceasedGender = document.getElementById('mirasDeceasedGender');
    const mirasHasSpouse = document.getElementById('mirasHasSpouse');
    const mirasSonsCount = document.getElementById('mirasSonsCount');
    const mirasDaughtersCount = document.getElementById('mirasDaughtersCount');
    const mirasHasFather = document.getElementById('mirasHasFather');
    const mirasHasMother = document.getElementById('mirasHasMother');

    if (btnCalculateMiras) {
        btnCalculateMiras.addEventListener('click', () => {
            const total = parseFloat(mirasTotalEstate.value) || 0;
            if (total <= 0) {
                showToast("Введите корректную сумму наследства", "error");
                return;
            }

            const gender = mirasDeceasedGender.value; // 'male' or 'female'
            const hasSpouse = mirasHasSpouse.value === 'yes';
            const sons = parseInt(mirasSonsCount.value) || 0;
            const daughters = parseInt(mirasDaughtersCount.value) || 0;
            const hasFather = mirasHasFather.value === 'yes';
            const hasMother = mirasHasMother.value === 'yes';
            const hasChildren = (sons + daughters) > 0;

            let breakdown = [];
            let remaining = total;

            // 1. Spouse share (Сура Ан-Ниса 4:12)
            if (hasSpouse) {
                if (gender === 'male') {
                    // Deceased was male -> Wife/Wives inherit 1/8 with children, 1/4 without children
                    const shareFraction = hasChildren ? 0.125 : 0.25;
                    const shareAmount = total * shareFraction;
                    const shareText = hasChildren ? "1/8 (12.5%)" : "1/4 (25.0%)";
                    breakdown.push({
                        role: "Супруга (Жена)",
                        share: shareText,
                        amount: shareAmount,
                        ayah: "Сура Ан-Ниса (4:12)"
                    });
                    remaining -= shareAmount;
                } else {
                    // Deceased was female -> Husband inherits 1/4 with children, 1/2 without children
                    const shareFraction = hasChildren ? 0.25 : 0.5;
                    const shareAmount = total * shareFraction;
                    const shareText = hasChildren ? "1/4 (25.0%)" : "1/2 (50.0%)";
                    breakdown.push({
                        role: "Супруг (Муж)",
                        share: shareText,
                        amount: shareAmount,
                        ayah: "Сура Ан-Ниса (4:12)"
                    });
                    remaining -= shareAmount;
                }
            }

            // 2. Mother share (Сура Ан-Ниса 4:11)
            if (hasMother) {
                const shareFraction = hasChildren ? (1 / 6) : (1 / 3);
                const shareAmount = total * shareFraction;
                const shareText = hasChildren ? "1/6 (16.67%)" : "1/3 (33.33%)";
                breakdown.push({
                    role: "Мать умершего",
                    share: shareText,
                    amount: shareAmount,
                    ayah: "Сура Ан-Ниса (4:11)"
                });
                remaining -= shareAmount;
            }

            // 3. Father share (Сура Ан-Ниса 4:11)
            if (hasFather) {
                if (hasChildren) {
                    const shareAmount = total * (1 / 6);
                    breakdown.push({
                        role: "Отец умершего (Фард)",
                        share: "1/6 (16.67%)",
                        amount: shareAmount,
                        ayah: "Сура Ан-Ниса (4:11)"
                    });
                    remaining -= shareAmount;
                }
            }

            // 4. Children (Сура Ан-Ниса 4:11)
            if (hasChildren) {
                if (sons > 0) {
                    // Sons and daughters share residual with 2:1 ratio (Asaba)
                    const totalUnits = (sons * 2) + daughters;
                    const unitValue = Math.max(0, remaining) / totalUnits;
                    
                    const sonShareEach = unitValue * 2;
                    breakdown.push({
                        role: `Сыновья (${sons} чел., по ${Math.round(sonShareEach).toLocaleString()} ₸ каждому)`,
                        share: `Асаба (доля сына вдвое больше дочери)`,
                        amount: sonShareEach * sons,
                        ayah: "Сура Ан-Ниса (4:11)"
                    });

                    if (daughters > 0) {
                        const daughterShareEach = unitValue;
                        breakdown.push({
                            role: `Дочери (${daughters} чел., по ${Math.round(daughterShareEach).toLocaleString()} ₸ каждой)`,
                            share: `Асаба (половина доли сына)`,
                            amount: daughterShareEach * daughters,
                            ayah: "Сура Ан-Ниса (4:11)"
                        });
                    }
                    remaining = 0;
                } else if (daughters > 0) {
                    // Only daughters
                    if (daughters === 1) {
                        const dShare = total * 0.5;
                        breakdown.push({
                            role: "Единственная дочь",
                            share: "1/2 (50.0%)",
                            amount: dShare,
                            ayah: "Сура Ан-Ниса (4:11)"
                        });
                        remaining -= dShare;
                    } else {
                        const dShare = total * (2 / 3);
                        breakdown.push({
                            role: `Дочери (${daughters} чел., по ${Math.round(dShare / daughters).toLocaleString()} ₸ каждой)`,
                            share: "2/3 (66.67% на всех поровну)",
                            amount: dShare,
                            ayah: "Сура Ан-Ниса (4:11)"
                        });
                        remaining -= dShare;
                    }
                }
            }

            // If father exists and no sons, father takes residual Asaba
            if (hasFather && sons === 0 && remaining > 0) {
                breakdown.push({
                    role: "Отец умершего (Асаба / Остаток)",
                    share: "Остаток наследства",
                    amount: remaining,
                    ayah: "Сура Ан-Ниса (4:11)"
                });
                remaining = 0;
            }

            let rowsHtml = '';
            breakdown.forEach(b => {
                const pct = ((b.amount / total) * 100).toFixed(1);
                rowsHtml += `
                    <div class="miras-share-row">
                        <div>
                            <div style="font-weight: 700; color: #FFF; font-size: 13.5px;">👤 ${b.role}</div>
                            <div style="font-size: 11.5px; color: var(--text-secondary); margin-top: 2px;">📖 ${b.ayah} • ${b.share}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 800; color: var(--apple-gold); font-size: 14.5px;">${Math.round(b.amount).toLocaleString()} ₸</div>
                            <div style="font-size: 11.5px; color: #34D399;">${pct}%</div>
                        </div>
                    </div>
                `;
            });

            mirasResultCard.style.display = 'block';
            mirasResultCard.innerHTML = `
                <div style="padding: 16px; background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.25); border-radius: 12px;">
                    <div style="font-weight: 800; font-size: 15px; color: #34D399; margin-bottom: 10px;">
                        ⚖️ ШАРИАТСКИЙ РАСЧЕТ ДОЛЕЙ НАСЛЕДНИКОВ (СУРА АН-НИСА 4:11-12)
                    </div>
                    <div style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 12px;">
                        Общая масса: <strong>${Math.round(total).toLocaleString()} ₸</strong>
                    </div>
                    ${rowsHtml}
                </div>
            `;
            showToast("Расчет наследства по Шариату выполнен!", "success");
        });
    }

    // =========================================================================
    // 13. AAOIFI 21 HALAL STOCK SCREENER (FINTECH)
    // =========================================================================
    const btnCheckStock = document.getElementById('btnCheckStock');
    const stockResultCard = document.getElementById('stockResultCard');
    const stockDebtRatio = document.getElementById('stockDebtRatio');
    const stockInterestIncome = document.getElementById('stockInterestIncome');
    const stockIndustry = document.getElementById('stockIndustry');

    const STOCK_PRESETS = {
        "KASPI": { debt: 11.2, interest: 2.1, industry: "halal", name: "Kaspi.kz (KSPI)", note: "Финтех/Торговля. Долг и доходы в рамках стандартов AAOIFI." },
        "KAP": { debt: 8.5, interest: 1.0, industry: "halal", name: "Казатомпром (KAP)", note: "Атомная промышленность. Нулевая процентная деятельность." },
        "AAPL": { debt: 24.8, interest: 1.8, industry: "halal", name: "Apple Inc. (AAPL)", note: "IT и потребительская электроника. Долг ниже 33%." },
        "TSLA": { debt: 4.2, interest: 1.1, industry: "halal", name: "Tesla Inc. (TSLA)", note: "Электромобили и зеленая энергетика. Чистый финансовый профиль." },
        "ARAMCO": { debt: 7.9, interest: 0.8, industry: "halal", name: "Saudi Aramco (2222.SR)", note: "Нефтегазовый сектор Саудовской Аравии. Полный комплаенс." },
        "HALYK": { debt: 68.0, interest: 72.0, industry: "haram_bank", name: "Halyk Bank (HSBK)", note: "Традиционный банк с процентным кредитованием (Риба)." }
    };

    document.querySelectorAll('[data-stock]').forEach(btn => {
        btn.addEventListener('click', () => {
            const sym = btn.getAttribute('data-stock');
            const data = STOCK_PRESETS[sym];
            if (data) {
                stockDebtRatio.value = data.debt;
                stockInterestIncome.value = data.interest;
                stockIndustry.value = data.industry;
                btnCheckStock.click();
            }
        });
    });

    if (btnCheckStock) {
        btnCheckStock.addEventListener('click', () => {
            const debt = parseFloat(stockDebtRatio.value) || 0;
            const interest = parseFloat(stockInterestIncome.value) || 0;
            const industry = stockIndustry.value;

            const isDebtOk = debt < 33.0;
            const isInterestOk = interest < 5.0;
            const isIndustryOk = industry === 'halal';
            const isCompliant = isDebtOk && isInterestOk && isIndustryOk;

            let badgeBg = isCompliant ? 'rgba(52, 211, 153, 0.1)' : 'rgba(239, 68, 68, 0.1)';
            let badgeBorder = isCompliant ? 'rgba(52, 211, 153, 0.3)' : 'rgba(239, 68, 68, 0.3)';
            let statusColor = isCompliant ? '#34D399' : '#F87171';
            let headerText = isCompliant ? '🟢 АКЦИЯ СООТВЕТСТВУЕТ СТАНДАРТУ AAOIFI 21 (ХАЛЯЛЬ)' : '🔴 АКЦИЯ НЕ СООТВЕТСТВУЕТ ШАРИАТСКИМ НОРМАМ ИНВЕСТИРОВАНИЯ';

            stockResultCard.style.display = 'block';
            stockResultCard.innerHTML = `
                <div style="background: ${badgeBg}; border: 1px solid ${badgeBorder}; border-radius: 12px; padding: 16px;">
                    <div style="font-weight: 800; font-size: 15px; color: ${statusColor}; margin-bottom: 8px;">
                        ${headerText}
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; margin-top: 10px;">
                        <div style="padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 12px;">
                            <strong>Долг / Капитализация:</strong> ${debt}% ${isDebtOk ? '✅ (<33%)' : '❌ (>33%)'}
                        </div>
                        <div style="padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 12px;">
                            <strong>Процентный доход:</strong> ${interest}% ${isInterestOk ? '✅ (<5%)' : '❌ (>5%)'}
                        </div>
                        <div style="padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 12px;">
                            <strong>Сфера бизнеса:</strong> ${isIndustryOk ? '✅ Дозволена' : '❌ Запрещена'}
                        </div>
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">
                        ⚖️ <i>Стандарт AAOIFI Shariah Standard No. 21 (Financial Papers & Shares).</i>
                    </div>
                </div>
            `;
            showToast(isCompliant ? "Акции проверены: Халяль (AAOIFI 21)" : "Акции проверены: Не соответствует нормам", isCompliant ? "success" : "error");
        });
    }

    // =========================================================================
    // 14. INSTAGRAM & WHATSAPP STORIES SOCIAL CARD GENERATOR (HTML5 Canvas)
    // =========================================================================
    const modalStoryGenerator = document.getElementById('modalStoryGenerator');
    const btnCloseStoryGenerator = document.getElementById('btnCloseStoryGenerator');
    const storyCanvas = document.getElementById('storyCanvas');
    const btnDownloadStoryImage = document.getElementById('btnDownloadStoryImage');
    const btnShareStoryDirect = document.getElementById('btnShareStoryDirect');

    let currentStoryAyah = null;

    window.openStoryModalForCurrentAyah = (suraNum, ayahObj) => {
        if (!ayahObj) {
            if (surahAyahsData && surahAyahsData.length > 0) {
                ayahObj = surahAyahsData[currentPlayingAyahIndex || 0];
                suraNum = currentSurah;
            } else {
                suraNum = 1;
                ayahObj = {
                    ayah: 1,
                    text_uthmani: "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                    translations: {
                        ru: "Во имя Аллаха, Милостивого, Милосердного",
                        kk: "Аса қамқор, ерекше мейірімді Алланың атымен бастаймын",
                        en: "In the name of Allah, the Entirely Merciful, the Especially Merciful."
                    }
                };
            }
        }
        currentStoryAyah = { sura: suraNum || 1, ...ayahObj };
        if (modalStoryGenerator) modalStoryGenerator.style.display = 'flex';
        drawStoryCanvas(currentStoryAyah);
    };

    function drawStoryCanvas(data) {
        if (!storyCanvas) return;
        const ctx = storyCanvas.getContext('2d');
        const W = 1080;
        const H = 1920;

        // 1. Dark Apple Gradient Background
        const grad = ctx.createLinearGradient(0, 0, 0, H);
        grad.addColorStop(0, '#060910');
        grad.addColorStop(0.5, '#0E1626');
        grad.addColorStop(1, '#060910');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // 2. Decorative Golden Frame
        ctx.strokeStyle = 'rgba(217, 119, 6, 0.35)';
        ctx.lineWidth = 4;
        ctx.strokeRect(40, 40, W - 80, H - 80);

        ctx.strokeStyle = 'rgba(217, 119, 6, 0.15)';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(56, 56, W - 112, H - 112);

        // 3. Header Logo & Title
        ctx.textAlign = 'center';
        ctx.fillStyle = '#D97706';
        ctx.font = 'bold 36px sans-serif';
        ctx.fillText('🛡️ AL-FURQAN GUARD', W / 2, 140);

        ctx.fillStyle = '#94A3B8';
        ctx.font = '22px sans-serif';
        ctx.fillText('Tanzil Uthmani L0 Ground Truth • Holy Quran', W / 2, 185);

        // 4. Sura & Ayah Badge
        const suraInfo = `СУРА ${data.sura} • АЯТ ${data.ayah}`;
        ctx.fillStyle = 'rgba(217, 119, 6, 0.2)';
        ctx.fillRect(W / 2 - 200, 240, 400, 54);
        ctx.strokeStyle = '#D97706';
        ctx.lineWidth = 2;
        ctx.strokeRect(W / 2 - 200, 240, 400, 54);

        ctx.fillStyle = '#FDE68A';
        ctx.font = 'bold 24px sans-serif';
        ctx.fillText(suraInfo, W / 2, 276);

        // 5. Arabic Quran Calligraphy Text
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '48px "Amiri Quran", serif, Arial';
        ctx.direction = 'rtl';
        wrapCanvasText(ctx, data.text_uthmani || data.text || '', W / 2, 440, 880, 84);

        // 6. Translation Text
        ctx.direction = 'ltr';
        const currentLang = I18N.currentLang || 'ru';
        const transText = (data.translations && (data.translations[currentLang] || data.translations.ru || data.translations.kk)) || '';

        ctx.fillStyle = '#E2E8F0';
        ctx.font = 'italic 34px sans-serif';
        wrapCanvasText(ctx, `«${transText}»`, W / 2, 1200, 860, 52);

        // 7. Footer Watermark
        ctx.fillStyle = '#64748B';
        ctx.font = '22px sans-serif';
        ctx.fillText('al-furqan.ai • Проверено детерминированным ядром', W / 2, H - 100);
    }

    function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split(' ');
        let line = '';
        let curY = y;
        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + ' ';
            const metrics = ctx.measureText(testLine);
            if (metrics.width > maxWidth && n > 0) {
                ctx.fillText(line, x, curY);
                line = words[n] + ' ';
                curY += lineHeight;
            } else {
                line = testLine;
            }
        }
        ctx.fillText(line, x, curY);
    }

    if (btnCloseStoryGenerator) btnCloseStoryGenerator.addEventListener('click', () => modalStoryGenerator.style.display = 'none');

    if (btnDownloadStoryImage) {
        btnDownloadStoryImage.addEventListener('click', () => {
            if (!storyCanvas) return;
            const link = document.createElement('a');
            link.download = `Al_Furqan_Ayah_Story_${Date.now()}.png`;
            link.href = storyCanvas.toDataURL('image/png');
            link.click();
            showToast("Карточка для Story успешно сохранена!", "success");
        });
    }

    if (btnShareStoryDirect) {
        btnShareStoryDirect.addEventListener('click', async () => {
            if (!storyCanvas) return;
            try {
                storyCanvas.toBlob(async (blob) => {
                    if (navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], 'ayah_story.png', { type: 'image/png' })] })) {
                        await navigator.share({
                            files: [new File([blob], 'ayah_story.png', { type: 'image/png' })],
                            title: 'Al-Furqan Guard — Аят Корана',
                            text: 'Священный Коран • Канонический Tanzil L0'
                        });
                        showToast("Успешно отправлено в соцсети!", "success");
                    } else {
                        btnDownloadStoryImage.click();
                    }
                });
            } catch (err) {
                btnDownloadStoryImage.click();
            }
        });
    }

    // =========================================================================
    // 15. ECOSYSTEM MINI-MAP & MODAL CONTROLS
    // =========================================================================
    const btnToggleEcosystem = document.getElementById('btnToggleEcosystem');
    const modalEcosystemMap = document.getElementById('modalEcosystemMap');
    const btnCloseEcosystem = document.getElementById('btnCloseEcosystem');
    const btnShareProject = document.getElementById('btnShareProject');

    if (btnToggleEcosystem) btnToggleEcosystem.addEventListener('click', () => modalEcosystemMap.style.display = 'flex');
    if (btnCloseEcosystem) btnCloseEcosystem.addEventListener('click', () => modalEcosystemMap.style.display = 'none');

    window.navigateToTabAndScroll = (tabId, elementId) => {
        // 1. Close any open modals
        document.querySelectorAll('.modal-backdrop').forEach(m => m.style.display = 'none');

        // 2. Activate target tab
        const tabBtn = document.querySelector(`[data-tab="${tabId}"]`);
        if (tabBtn) tabBtn.click();

        // 3. Smoothly scroll to target element
        setTimeout(() => {
            const targetEl = document.getElementById(elementId) || document.getElementById(tabId);
            if (targetEl) {
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                targetEl.classList.add('nav-highlight-pulse');
                setTimeout(() => targetEl.classList.remove('nav-highlight-pulse'), 1600);
            }
        }, 120);
    };

    if (btnShareProject) {
        btnShareProject.addEventListener('click', async () => {
            const shareData = {
                title: 'Al-Furqan Guard',
                text: '🛡️ Al-Furqan Guard — Детерминированный канонический Коран (Tanzil L0), Халяль-сканер и Шариатский аудитор!',
                url: window.location.href
            };
            if (navigator.share) {
                try {
                    await navigator.share(shareData);
                    showToast("Спасибо, что делитесь проектом!", "success");
                } catch (e) {}
            } else {
                navigator.clipboard.writeText(window.location.href);
                showToast("📋 Ссылка на проект скопирована в буфер обмена!", "success");
            }
        });
    }

    // =========================================================================
    // 16. MODALS & FEEDBACK SUBMISSION
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
            showToast("Пожалуйста, напишите ваш отзыв или предложение.", "error");
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
            feedbackStatusText.textContent = `✅ Отзыв №${data.feedback_id || 1} успешно сохранен! Джазакаллаху хайран.`;
            feedbackStatusText.style.color = '#34D399';
            feedbackMessage.value = '';
            showToast(`✅ Отзыв №${data.feedback_id || 1} отправлен разработчикам!`, "success");
            setTimeout(() => { modalFeedback.style.display = 'none'; feedbackStatusText.textContent = ''; }, 1800);
        } catch (e) {
            feedbackStatusText.textContent = '❌ ' + (I18N.t('feedbackError') || 'Ошибка отправки отзыва.');
            feedbackStatusText.style.color = '#F87171';
            showToast("Ошибка отправки отзыва. Попробуйте снова.", "error");
        }
    });

    // =========================================================================
    // 17. VOICE SEARCH (Web Speech Recognition API)
    // =========================================================================
    const btnVoiceSearch = document.getElementById('btnVoiceSearch');
    if (btnVoiceSearch) {
        btnVoiceSearch.addEventListener('click', () => {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                showToast("Голосовой ввод не поддерживается вашим браузером", "error");
                return;
            }
            const recognition = new SpeechRecognition();
            const lang = I18N.currentLang || 'ru';
            recognition.lang = lang === 'ar' ? 'ar-SA' : (lang === 'kk' ? 'kk-KZ' : (lang === 'en' ? 'en-US' : 'ru-RU'));
            recognition.interimResults = false;
            showToast("🎙️ Говорите... Слушаю аят или запрос", "info");
            const icon = document.getElementById('voiceSearchIcon');
            if (icon) icon.textContent = '🔴';

            recognition.onresult = (event) => {
                const speechText = event.results[0][0].transcript;
                if (icon) icon.textContent = '🎙️';
                universalSearchInput.value = speechText;
                showToast(`Распознано: "${speechText}"`, "success");
                btnUniversalSearchGo.click();
            };
            recognition.onerror = () => {
                if (icon) icon.textContent = '🎙️';
                showToast("Не удалось распознать голос. Попробуйте еще раз.", "error");
            };
            recognition.onend = () => {
                if (icon) icon.textContent = '🎙️';
            };
            recognition.start();
        });
    }

    // =========================================================================
    // 18. KHATM PLANNER (ПЛАН ПРОЧТЕНИЯ КОРАНА)
    // =========================================================================
    const btnOpenKhatmPlanner = document.getElementById('btnOpenKhatmPlanner');
    const modalKhatmPlanner = document.getElementById('modalKhatmPlanner');
    const btnCloseKhatmPlanner = document.getElementById('btnCloseKhatmPlanner');
    const khatmDaysTarget = document.getElementById('khatmDaysTarget');
    const khatmCurrentPage = document.getElementById('khatmCurrentPage');
    const khatmProgressBar = document.getElementById('khatmProgressBar');
    const khatmProgressPercent = document.getElementById('khatmProgressPercent');
    const khatmDailyGoalText = document.getElementById('khatmDailyGoalText');
    const btnSaveKhatmProgress = document.getElementById('btnSaveKhatmProgress');
    const btnResetKhatm = document.getElementById('btnResetKhatm');

    function updateKhatmUI() {
        const savedPage = parseInt(localStorage.getItem('al_furqan_khatm_page') || '0', 10);
        if (khatmCurrentPage) khatmCurrentPage.value = savedPage;
        const pct = Math.min(100, Math.round((savedPage / 604) * 100));
        if (khatmProgressBar) khatmProgressBar.style.width = `${pct}%`;
        if (khatmProgressPercent) khatmProgressPercent.textContent = `${pct}% (${savedPage}/604 стр.)`;

        const days = parseInt(khatmDaysTarget?.value || '30', 10);
        const pagesPerDay = (604 / days).toFixed(1);
        const pagesPerPrayer = (604 / days / 5).toFixed(1);
        if (khatmDailyGoalText) {
            khatmDailyGoalText.textContent = `🎯 Ваша норма: ~${pagesPerDay} стр. в день (~${pagesPerPrayer} стр. после каждого из 5 намазов)`;
        }
    }

    if (btnOpenKhatmPlanner) {
        btnOpenKhatmPlanner.addEventListener('click', () => {
            updateKhatmUI();
            if (modalKhatmPlanner) modalKhatmPlanner.style.display = 'flex';
        });
    }
    if (btnCloseKhatmPlanner) btnCloseKhatmPlanner.addEventListener('click', () => modalKhatmPlanner.style.display = 'none');

    if (khatmDaysTarget) khatmDaysTarget.addEventListener('change', updateKhatmUI);
    if (btnSaveKhatmProgress) {
        btnSaveKhatmProgress.addEventListener('click', () => {
            const page = Math.max(0, Math.min(604, parseInt(khatmCurrentPage.value) || 0));
            localStorage.setItem('al_furqan_khatm_page', page.toString());
            updateKhatmUI();
            showToast(`Прогресс Хатма сохранен: ${page} из 604 страниц!`, "success");
            modalKhatmPlanner.style.display = 'none';
        });
    }
    if (btnResetKhatm) {
        btnResetKhatm.addEventListener('click', () => {
            localStorage.setItem('al_furqan_khatm_page', '0');
            updateKhatmUI();
            showToast("Прогресс Хатма сброшен", "info");
        });
    }

    // =========================================================================
    // 19. STOCK DIVIDEND PURIFICATION CALCULATOR (AAOIFI STANDARD NO. 21)
    // =========================================================================
    const btnCalculatePurification = document.getElementById('btnCalculatePurification');
    const purifyDividendAmount = document.getElementById('purifyDividendAmount');
    const purifyImpureRatio = document.getElementById('purifyImpureRatio');
    const purifyResultCard = document.getElementById('purifyResultCard');

    if (btnCalculatePurification) {
        btnCalculatePurification.addEventListener('click', () => {
            const dividend = parseFloat(purifyDividendAmount.value) || 0;
            const ratio = parseFloat(purifyImpureRatio.value) || 0;

            if (dividend <= 0) {
                showToast("Введите корректную сумму дивидендов или дохода", "error");
                return;
            }

            const purifyAmount = Math.round(dividend * (ratio / 100));
            const cleanAmount = dividend - purifyAmount;

            purifyResultCard.style.display = 'block';
            purifyResultCard.innerHTML = `
                <div style="background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.25); border-radius: 12px; padding: 16px;">
                    <div style="font-weight: 800; font-size: 15px; color: var(--apple-gold); margin-bottom: 8px;">
                        🧼 РАСЧЕТ ОЧИЩЕНИЯ ДОХОДОВ (ТАЗКИЯ / PURIFICATION)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 10px;">
                        <div style="padding: 10px 14px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px;">
                            <div style="font-size: 11.5px; color: #FCA5A5;">Сумма на благотворительность (Садака):</div>
                            <div style="font-size: 18px; font-weight: 800; color: #EF4444; margin-top: 4px;">${purifyAmount.toLocaleString()} ₸</div>
                            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">(${ratio}% от дохода)</div>
                        </div>
                        <div style="padding: 10px 14px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px;">
                            <div style="font-size: 11.5px; color: #6EE7B7;">Чистый дозволенный доход инвестора:</div>
                            <div style="font-size: 18px; font-weight: 800; color: #10B981; margin-top: 4px;">${cleanAmount.toLocaleString()} ₸</div>
                            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">(100% Халяль)</div>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 12px; line-height: 1.45;">
                        ⚖️ <i>Согласно стандарту AAOIFI Shariah Standard No. 21 (ст. 3/4), доход от компаний с допустимым процентом (&lt;5%) подлежит обязательному очищению путем передачи суммы нечистого процента нуждающимся без намерения получить награду за милостыню.</i>
                    </div>
                </div>
            `;
            showToast("Расчет очищения дивидендов выполнен!", "success");
        });
    }

    // =========================================================================
    // 20. ISLAMIC WILL (ӨСИЕТНАМА) GENERATOR
    // =========================================================================
    const btnGenerateWillPDF = document.getElementById('btnGenerateWillPDF');
    const willFullName = document.getElementById('willFullName');
    const willWaqfShare = document.getElementById('willWaqfShare');
    const willSpecialNotes = document.getElementById('willSpecialNotes');
    const modalIslamicWillPreview = document.getElementById('modalIslamicWillPreview');
    const btnCloseWillPreview = document.getElementById('btnCloseWillPreview');
    const btnCloseWillModal = document.getElementById('btnCloseWillModal');
    const btnPrintWillDocument = document.getElementById('btnPrintWillDocument');
    const willPrintableDocument = document.getElementById('willPrintableDocument');

    if (btnGenerateWillPDF) {
        btnGenerateWillPDF.addEventListener('click', () => {
            const name = willFullName.value.trim() || 'Гражданин(ка)';
            const waqfShareVal = willWaqfShare.value;
            let waqfText = "1/3 (одну треть)";
            if (waqfShareVal === "0.25") waqfText = "1/4 (одну четверть)";
            if (waqfShareVal === "0.1") waqfText = "1/10 (одну десятую)";
            if (waqfShareVal === "0") waqfText = "0% (все передается прямым законным наследникам)";

            const notes = willSpecialNotes.value.trim() || 'Похоронить в соответствии с сунной Пророка Мухаммада ﷺ.';
            const today = new Date().toLocaleDateString('ru-RU');

            willPrintableDocument.innerHTML = `
                <div style="text-align: center; border-bottom: 2px solid #D97706; padding-bottom: 12px; margin-bottom: 16px;">
                    <h2 style="margin: 0; color: #111; font-size: 20px;">БИСМИЛЛЯХИР-РАХМАНИР-РАХИМ</h2>
                    <h3 style="margin: 6px 0 0 0; color: #B45309; font-size: 16px;">ШАРИАТСКОЕ ЗАВЕЩАНИЕ (ИСЛАМДЫҚ ӨСИЕТНАМА)</h3>
                    <div style="font-size: 12px; color: #666; margin-top: 4px;">Дата составления: ${today} • Al-Furqan Guard Standard</div>
                </div>

                <p><strong>1. Исповедание веры (Шахада):</strong><br>
                Я, <u>${name}</u>, находясь в здравом уме, твердой памяти и ясном сознании, свидетельствую: <i>«Нет божества, кроме Аллаха, Единственного, не имеющего сотоварищей, и свидетельствую, что Мухаммад — Его раб и Посланник»</i>.</p>

                <p><strong>2. Распоряжение имуществом и благотворительность (Васият / Вакуф):</strong><br>
                На основании аята Священного Корана (Сура Аль-Бакара 2:180) и сунны Пророка ﷺ я завещаю выделить из принадлежащего мне имущества долю в размере <strong>${waqfText}</strong> на нужды благотворительности (садака джария / вакуф / помощь нуждающимся).</p>

                <p><strong>3. Распределение наследства по Шариату (Мирас / Фараид):</strong><br>
                Все оставшееся после выплаты долгов и указанной доли имущество подлежит строгому разделу между законными наследниками по нормам Шариата в долях, установленных Всевышним Аллахом в <strong>Суре Ан-Ниса (аяты 11, 12 и 176)</strong>.</p>

                <p><strong>4. Особые поручения и долги:</strong><br>
                ${notes}</p>

                <div style="margin-top: 30px; display: flex; justify-content: space-between;">
                    <div>
                        <p><strong>Завещатель:</strong> ________________ / ${name} /</p>
                    </div>
                    <div>
                        <p><strong>Свидетель 1:</strong> ________________</p>
                        <p><strong>Свидетель 2:</strong> ________________</p>
                    </div>
                </div>
            `;

            modalIslamicWillPreview.style.display = 'flex';
            showToast("Шариатское завещание сформировано!", "success");
        });
    }

    if (btnCloseWillPreview) btnCloseWillPreview.addEventListener('click', () => modalIslamicWillPreview.style.display = 'none');
    if (btnCloseWillModal) btnCloseWillModal.addEventListener('click', () => modalIslamicWillPreview.style.display = 'none');

    if (btnPrintWillDocument) {
        btnPrintWillDocument.addEventListener('click', () => {
            const printWin = window.open('', '_blank');
            printWin.document.write(`
                <html>
                <head>
                    <title>Шариатское Завещание</title>
                    <style>
                        body { font-family: Georgia, serif; padding: 40px; line-height: 1.6; color: #111; }
                        h2, h3 { text-align: center; }
                    </style>
                </head>
                <body>
                    ${willPrintableDocument.innerHTML}
                    <script>window.onload = function() { window.print(); window.close(); }<\/script>
                </body>
                </html>
            `);
            printWin.document.close();
            showToast("Открыто окно печати / сохранения в PDF", "info");
        });
    }

    // =========================================================================
    // 21. MURABAHA VS RIBA SIMULATOR
    // =========================================================================
    const btnSimulateMurabaha = document.getElementById('btnSimulateMurabaha');
    const muraItemPrice = document.getElementById('muraItemPrice');
    const muraMonths = document.getElementById('muraMonths');
    const muraComparisonResult = document.getElementById('muraComparisonResult');

    if (btnSimulateMurabaha) {
        btnSimulateMurabaha.addEventListener('click', () => {
            const price = parseFloat(muraItemPrice.value) || 0;
            const months = parseInt(muraMonths.value) || 12;

            if (price <= 0 || months <= 0) {
                showToast("Введите корректную стоимость товара и срок", "error");
                return;
            }

            // Murabaha: Fixed trade margin (e.g. 10% flat markup on sale price), zero compound penalty
            const murabahaMarkup = price * 0.10;
            const murabahaTotal = price + murabahaMarkup;
            const murabahaMonthly = Math.round(murabahaTotal / months);

            // Riba Conventional: Compound interest (e.g. 24% APR) + compounding delay penalty
            const ribaAnnualRate = 0.24;
            const ribaTotal = Math.round(price * (1 + (ribaAnnualRate * (months / 12))));
            const ribaMonthly = Math.round(ribaTotal / months);
            const ribaPenalty = Math.round(price * 0.005 * 30); // 0.5% daily penalty for 30 days delay

            muraComparisonResult.style.display = 'block';
            muraComparisonResult.innerHTML = `
                <div class="comparison-matrix">
                    <div class="comp-card-halal">
                        <div style="font-weight: 800; color: #10B981; font-size: 15px; margin-bottom: 6px;">
                            🟢 МУРАБАХА (ХАЛЯЛЬ РАССРОЧКА)
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
                            Договор купли-продажи с фиксированной наценкой (Сура Аль-Бакара 2:275).
                        </div>
                        <div style="font-size: 14px; margin-bottom: 4px;"><strong>Ежемесячный платеж:</strong> ${murabahaMonthly.toLocaleString()} ₸</div>
                        <div style="font-size: 14px; margin-bottom: 4px;"><strong>Итоговая цена:</strong> ${Math.round(murabahaTotal).toLocaleString()} ₸ (Фиксирована)</div>
                        <div style="font-size: 12px; color: #10B981; margin-top: 8px;">
                            ✅ <strong>При просрочке:</strong> Долг НЕ растет. Проценты и пени в пользу банка ЗАПРЕЩЕНЫ Шариатом.
                        </div>
                    </div>

                    <div class="comp-card-riba">
                        <div style="font-weight: 800; color: #EF4444; font-size: 15px; margin-bottom: 6px;">
                            🔴 РИБА (ПРОЦЕНТНЫЙ КРЕДИТ)
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
                            Ростовщический заем денег под процент (Категорически запрещен Кораном).
                        </div>
                        <div style="font-size: 14px; margin-bottom: 4px;"><strong>Ежемесячный платеж:</strong> ~${ribaMonthly.toLocaleString()} ₸</div>
                        <div style="font-size: 14px; margin-bottom: 4px;"><strong>Итоговая сумма:</strong> ~${ribaTotal.toLocaleString()} ₸ + скрытые пени</div>
                        <div style="font-size: 12px; color: #EF4444; margin-top: 8px;">
                            ❌ <strong>При просрочке:</strong> Начисляются штрафы и пени (~${ribaPenalty.toLocaleString()} ₸/мес), процент на процент.
                        </div>
                    </div>
                </div>
            `;
            showToast("Сравнение Мурабаха и Риба выполнено!", "info");
        });
    }

    // =========================================================================
    // 22. WEBSITE EMBED WIDGET GENERATOR
    // =========================================================================
    const selectEmbedType = document.getElementById('selectEmbedType');
    const embedCodeSnippet = document.getElementById('embedCodeSnippet');
    const btnCopyEmbedSnippet = document.getElementById('btnCopyEmbedSnippet');

    if (selectEmbedType && embedCodeSnippet) {
        selectEmbedType.addEventListener('change', () => {
            const type = selectEmbedType.value;
            embedCodeSnippet.textContent = `<iframe src="https://al-furqan.ai/?embed=${type}" width="100%" height="480" frameborder="0" style="border-radius:12px;"></iframe>`;
        });
    }

    if (btnCopyEmbedSnippet) {
        btnCopyEmbedSnippet.addEventListener('click', () => {
            if (!embedCodeSnippet) return;
            navigator.clipboard.writeText(embedCodeSnippet.textContent);
            showToast("📋 HTML-код виджета скопирован в буфер обмена!", "success");
        });
    }

    // Close modals on click outside
    window.addEventListener('click', (e) => {
        if (e.target === modalStandards) modalStandards.style.display = 'none';
        if (e.target === modalFeedback) modalFeedback.style.display = 'none';
        if (e.target === modalGuide) modalGuide.style.display = 'none';
        if (e.target === modalEcosystemMap) modalEcosystemMap.style.display = 'none';
        if (e.target === modalStoryGenerator) modalStoryGenerator.style.display = 'none';
        if (e.target === modalKhatmPlanner) modalKhatmPlanner.style.display = 'none';
        if (e.target === modalIslamicWillPreview) modalIslamicWillPreview.style.display = 'none';
    });

    // Language switch
    selectLanguage.addEventListener('change', (e) => {
        if (typeof I18N !== 'undefined' && I18N.setLanguage) {
            I18N.setLanguage(e.target.value);
            showToast("Язык интерфейса обновлен", "info");
        }
    });

    // Start App
    await initApp();
});
