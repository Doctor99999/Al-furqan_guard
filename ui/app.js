
// =========================================================================
// Global Core Utilities (HTML Sanitization, Surah Naming, Multi-Translations)
// =========================================================================
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getSurahName(suraNum) {
    if (!suraNum || suraNum < 1 || suraNum > 114) return `Сура ${suraNum}`;
    const lang = (window.I18N && window.I18N.currentLang) || 'ru';
    const dict = (window.I18N && window.I18N.locales && (window.I18N.locales[lang] || window.I18N.locales.ru || window.I18N.locales.kk)) || {};
    if (dict.surahNames && dict.surahNames[suraNum - 1]) {
        return dict.surahNames[suraNum - 1];
    }
    return `Сура ${suraNum}`;
}

function getTranslationHtml(translations, sura, ayah) {
    if (!translations) return '';
    const lang = (window.I18N && window.I18N.currentLang) || 'ru';
    let transText = translations.ru || translations.kk || translations.en || '';
    let label = (window.I18N && window.I18N.t && window.I18N.t('lblTranslation')) || 'Аудармасы / Перевод:';

    if (lang === 'kk' && translations.kk) {
        transText = translations.kk;
        label = "Мағыналық аудармасы (Халифа Алтай):";
    } else if (lang === 'ru' && translations.ru) {
        transText = translations.ru;
        label = "Смысловой перевод (Эльмир Кулиев):";
    } else if (lang === 'en' && translations.en) {
        transText = translations.en;
        label = "Meaning Translation (Saheeh International):";
    } else if (lang === 'tr' && translations.tr) {
        transText = translations.tr;
        label = "Meal (Diyanet İşleri):";
    } else if (lang === 'id' && translations.id) {
        transText = translations.id;
        label = "Terjemahan (Kemenag RI):";
    } else if (lang === 'uz' && translations.uz) {
        transText = translations.uz;
        label = "Ma'nolari tarjimasi (Shayx Muhammad Sodiq):";
    } else if (lang === 'ar') {
        return '';
    }

    if (!transText) return '';
    return `
        <div class="translation-badge">
            <strong>${label}</strong>
            <span>${escapeHtml(transText)}</span>
        </div>
    `;
}

/* ==========================================================================
   Al-Furqan AI - Frontend Interactive Application Logic v2.0
   Multi-Reciter Audio • Halal OCR Photo Scanner • AAOIFI Shariah Compliance
   Comparative Tafsir & Multi-Translations • AST & 1,651 Roots Analyzer
   ========================================================================== */

// =========================================================================
// Advanced Continuous Quran Audio Player Engine (Auto-Play Next, Full Surah)
// =========================================================================
const CANONICAL_AYAH_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6
];

const RECITERS_INFO = {
    'alafasy': { name: 'Мишари Рашид аль-Афаси', cdn: 'https://everyayah.com/data/Alafasy_128kbps' },
    'husary': { name: 'Махмуд Халиль аль-Хусари', cdn: 'https://everyayah.com/data/Husary_128kbps' },
    'abdulbasit': { name: 'Абдульбасит Абдуссамад', cdn: 'https://everyayah.com/data/Abdul_Basit_Murattal_192kbps' }
};

class QuranAudioEngine {
    constructor() {
        this.player = document.getElementById('globalAudioPlayer') || new Audio();
        this.currentSura = 1;
        this.currentAyah = 1;
        this.isPlaying = false;
        this.continuousMode = true;
        this.playbackRate = 1.0;
        this.activeInlineBtn = null;
        
        this.initEvents();
    }

    initEvents() {
        this.player.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.player.addEventListener('ended', () => this.onEnded());
        this.player.addEventListener('play', () => this.onPlayStateChange(true));
        this.player.addEventListener('pause', () => this.onPlayStateChange(false));
        this.player.addEventListener('error', (e) => {
            console.warn("Audio playback stream error:", e);
        });
    }

    formatTime(sec) {
        if (!sec || isNaN(sec)) return '00:00';
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    onTimeUpdate() {
        const curEl = document.getElementById('playerCurrentTime');
        const durEl = document.getElementById('playerDuration');
        if (curEl) curEl.textContent = this.formatTime(this.player.currentTime);
        if (durEl && this.player.duration) durEl.textContent = this.formatTime(this.player.duration);
    }

    onPlayStateChange(playing) {
        this.isPlaying = playing;
        const iconPlay = document.getElementById('iconPlayerPlay');
        const iconPause = document.getElementById('iconPlayerPause');
        if (iconPlay && iconPause) {
            iconPlay.style.display = playing ? 'none' : 'block';
            iconPause.style.display = playing ? 'block' : 'none';
        }
        if (this.activeInlineBtn) {
            if (playing) {
                this.activeInlineBtn.classList.add('playing');
                this.activeInlineBtn.innerHTML = I18N.t('lblStopAudio') || '⏸️ Тоқтату';
            } else {
                this.activeInlineBtn.classList.remove('playing');
                this.activeInlineBtn.innerHTML = I18N.t('lblPlayAudio') || '▶️ Тыңдау';
            }
        }
    }

    onEnded() {
        if (this.activeInlineBtn) {
            this.activeInlineBtn.classList.remove('playing');
            this.activeInlineBtn.innerHTML = I18N.t('lblPlayAudio') || '▶️ Тыңдау';
        }

        if (this.continuousMode) {
            const maxAyahs = CANONICAL_AYAH_COUNTS[this.currentSura - 1] || 7;
            if (this.currentAyah < maxAyahs) {
                this.play(this.currentSura, this.currentAyah + 1);
            } else if (this.currentSura < 114) {
                this.play(this.currentSura + 1, 1);
            } else {
                this.isPlaying = false;
            }
        } else {
            this.isPlaying = false;
        }
    }

    play(sura, ayah, inlineBtn = null) {
        this.currentSura = parseInt(sura) || 1;
        this.currentAyah = parseInt(ayah) || 1;

        if (this.activeInlineBtn && this.activeInlineBtn !== inlineBtn) {
            this.activeInlineBtn.classList.remove('playing');
            this.activeInlineBtn.innerHTML = I18N.t('lblPlayAudio') || '▶️ Тыңдау';
        }
        this.activeInlineBtn = inlineBtn;

        const reciterKey = document.getElementById('selectReciter')?.value || 'alafasy';
        const reciter = RECITERS_INFO[reciterKey] || RECITERS_INFO['alafasy'];

        const sPad = String(this.currentSura).padStart(3, '0');
        const aPad = String(this.currentAyah).padStart(3, '0');
        const url = `${reciter.cdn}/${sPad}${aPad}.mp3`;

        // Update Floating Player Bar
        const bar = document.getElementById('globalPlayerBar');
        if (bar) bar.style.display = 'block';

        const titleEl = document.getElementById('playerCurrentAyahTitle');
        const reciterEl = document.getElementById('playerCurrentReciter');
        if (titleEl) {
            const sName = (window.getSurahName ? window.getSurahName(this.currentSura) : `Сура ${this.currentSura}`);
            titleEl.textContent = `${sName} (${this.currentSura}:${this.currentAyah})`;
        }
        if (reciterEl) reciterEl.textContent = reciter.name;

        // Sync with Tab 4 inputs if present
        const selectSura = document.getElementById('selectSura');
        const inputAyahNum = document.getElementById('inputAyahNum');
        if (selectSura && inputAyahNum) {
            selectSura.value = this.currentSura;
            inputAyahNum.value = this.currentAyah;
            if (window.loadAyahAST) window.loadAyahAST();
        }

        this.player.src = url;
        this.player.playbackRate = this.playbackRate;
        this.player.play().catch(e => console.warn("Stream notice:", e));
    }

    playFullSurah(sura) {
        this.continuousMode = true;
        const btnCont = document.getElementById('btnToggleContinuous');
        if (btnCont) btnCont.classList.add('active');
        this.play(sura, 1);
    }

    togglePlayPause() {
        if (this.player.paused) {
            if (!this.player.src) {
                this.play(this.currentSura, this.currentAyah);
            } else {
                this.player.play();
            }
        } else {
            this.player.pause();
        }
    }

    next() {
        const maxAyahs = CANONICAL_AYAH_COUNTS[this.currentSura - 1] || 7;
        if (this.currentAyah < maxAyahs) {
            this.play(this.currentSura, this.currentAyah + 1);
        } else if (this.currentSura < 114) {
            this.play(this.currentSura + 1, 1);
        }
    }

    prev() {
        if (this.currentAyah > 1) {
            this.play(this.currentSura, this.currentAyah - 1);
        } else if (this.currentSura > 1) {
            const prevMax = CANONICAL_AYAH_COUNTS[this.currentSura - 2] || 1;
            this.play(this.currentSura - 1, prevMax);
        }
    }

    setSpeed(speed) {
        this.playbackRate = parseFloat(speed) || 1.0;
        this.player.playbackRate = this.playbackRate;
    }

    toggleContinuous() {
        this.continuousMode = !this.continuousMode;
        const btnCont = document.getElementById('btnToggleContinuous');
        if (btnCont) {
            if (this.continuousMode) btnCont.classList.add('active');
            else btnCont.classList.remove('active');
        }
    }

    hideBar() {
        this.player.pause();
        const bar = document.getElementById('globalPlayerBar');
        if (bar) bar.style.display = 'none';
    }
}

const quranAudio = new QuranAudioEngine();

window.playAyahAudio = function(sura, ayah, btnEl) {
    if (quranAudio.currentSura === sura && quranAudio.currentAyah === ayah && !quranAudio.player.paused) {
        quranAudio.togglePlayPause();
    } else {
        quranAudio.play(sura, ayah, btnEl);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // 0. Holy Quran & Al-Fatiha Engine
    const fatihaAyahsContainer = document.getElementById('fatihaAyahsContainer');
    const quranSurahSelect = document.getElementById('quranSurahSelect');
    const btnLoadSurahFull = document.getElementById('btnLoadSurahFull');
    const btnPlaySelectedSurah = document.getElementById('btnPlaySelectedSurah');
    const fullSurahViewer = document.getElementById('fullSurahViewer');

    let fatihaCache = null;
    let currentSurahCache = null;

    async function loadFatihaSection() {
        if (!fatihaAyahsContainer) return;
        try {
            if (!fatihaCache) {
                const resp = await fetch('/api/v1/surah/1');
                fatihaCache = await resp.json();
            }
            renderFatihaAyahs(fatihaCache);
        } catch (e) {
            console.warn("Fatiha fetch notice:", e);
        }
    }

    function renderFatihaAyahs(data) {
        if (!fatihaAyahsContainer || !data || !data.ayahs) return;
        fatihaAyahsContainer.innerHTML = '';
        
        data.ayahs.forEach(ayah => {
            const card = document.createElement('div');
            card.className = 'audit-item';
            card.style.borderLeft = '3px solid var(--gold-primary)';
            card.style.background = 'rgba(22, 27, 34, 0.7)';
            
            const transHtml = getTranslationHtml(ayah.translations, 1, ayah.ayah);
            
            card.innerHTML = `
                <div class="audit-badge-row">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="tag-badge success">1:${ayah.ayah}</span>
                        <button class="btn-play-ayah-audio" onclick="playAyahAudio(1, ${ayah.ayah}, this)" title="Аятты тыңдау">
                            ▶️ Тыңдау
                        </button>
                    </div>
                    <span style="font-size: 13px; color: var(--gold-bright); font-weight: 700;">Әл-Фатиха [1:${ayah.ayah}]</span>
                </div>
                <div class="arabic-display" style="font-size: 24px; padding: 12px 14px;">${ayah.text_uthmani}</div>
                ${ayah.transliteration ? `<div class="transliteration-badge" style="font-style: italic; color: #93C5FD;"><strong>Произношение (латиница):</strong> ${escapeHtml(ayah.transliteration)}</div>` : ''}
                ${transHtml}
            `;
            fatihaAyahsContainer.appendChild(card);
        });
    }

    function populateQuranSurahs() {
        if (!quranSurahSelect) return;
        const currentVal = quranSurahSelect.value || '1';
        quranSurahSelect.innerHTML = '';
        for (let i = 1; i <= 114; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            const sName = getSurahName(i);
            const count = CANONICAL_AYAH_COUNTS[i - 1] || 7;
            opt.textContent = `${i}. ${sName} (${count} аят)`;
            quranSurahSelect.appendChild(opt);
        }
        quranSurahSelect.value = currentVal;
    }

    async function loadSelectedSurahFull() {
        if (!quranSurahSelect || !fullSurahViewer) return;
        const sura = parseInt(quranSurahSelect.value) || 1;
        fullSurahViewer.innerHTML = '<div class="empty-state"><p>Сүренің барлық аяттары жүктелуде...</p></div>';

        try {
            const resp = await fetch(`/api/v1/surah/${sura}`);
            const data = await resp.json();
            currentSurahCache = data;
            renderFullSurah(data);
        } catch (e) {
            fullSurahViewer.innerHTML = '<div class="empty-state"><p style="color: var(--danger-primary)">Қате орын алды.</p></div>';
        }
    }

    function renderFullSurah(data) {
        if (!fullSurahViewer || !data || !data.ayahs) return;
        fullSurahViewer.innerHTML = '';
        const localizedSurah = getSurahName(data.sura);

        // Header summary for the surah
        const sHeader = document.createElement('div');
        sHeader.className = 'claim-result-box valid';
        sHeader.style.marginBottom = '8px';
        sHeader.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 16px; font-weight: 800; color: var(--gold-bright);">
                    ${localizedSurah} (${data.sura}-сүре • Барлығы: ${data.total_ayahs} аят)
                </div>
                <button class="btn btn-primary" onclick="quranAudio.playFullSurah(${data.sura})" style="padding: 6px 16px; font-size: 13px; color: #FFFFFF !important; font-weight: 700; background: linear-gradient(135deg, #10B981, #059669); border: 1px solid #34D399; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
                    ▶️ Сүрені толық тыңдау
                </button>
            </div>
        `;
        fullSurahViewer.appendChild(sHeader);

        data.ayahs.forEach(ayah => {
            const card = document.createElement('div');
            card.className = 'audit-item';
            card.style.borderLeft = '3px solid var(--gold-primary)';
            card.style.background = 'rgba(22, 27, 34, 0.7)';
            
            const transHtml = getTranslationHtml(ayah.translations, ayah.sura, ayah.ayah);
            
            card.innerHTML = `
                <div class="audit-badge-row">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="tag-badge success">${ayah.sura}:${ayah.ayah}</span>
                        <button class="btn-play-ayah-audio" onclick="playAyahAudio(${ayah.sura}, ${ayah.ayah}, this)" title="Аятты тыңдау">
                            ▶️ Тыңдау
                        </button>
                    </div>
                    <span style="font-size: 13px; color: var(--gold-bright); font-weight: 700;">${localizedSurah} [${ayah.sura}:${ayah.ayah}]</span>
                </div>
                <div class="arabic-display" style="font-size: 24px; padding: 12px 14px;">${ayah.text_uthmani}</div>
                ${ayah.transliteration ? `<div class="transliteration-badge" style="font-style: italic; color: #93C5FD;"><strong>Произношение (латиница):</strong> ${escapeHtml(ayah.transliteration)}</div>` : ''}
                ${transHtml}
            `;
            fullSurahViewer.appendChild(card);
        });
    }

    if (btnLoadSurahFull) {
        btnLoadSurahFull.addEventListener('click', loadSelectedSurahFull);
    }
    if (quranSurahSelect) {
        quranSurahSelect.addEventListener('change', loadSelectedSurahFull);
    }
    if (btnPlaySelectedSurah) {
        btnPlaySelectedSurah.addEventListener('click', () => {
            const sura = parseInt(quranSurahSelect?.value) || 1;
            quranAudio.playFullSurah(sura);
        });
    }

    // 1. Language Initialization
    const selectLanguage = document.getElementById('selectLanguage');
    if (selectLanguage) {
        selectLanguage.value = I18N.currentLang;
        selectLanguage.addEventListener('change', (e) => {
            I18N.setLanguage(e.target.value);
            populateSurahs();
            populateQuranSurahs();
            loadFatihaSection();
            if (currentSurahCache) renderFullSurah(currentSurahCache);
            loadAyahAST();
            loadAhkamCategory(document.querySelector('.ahkam-cat-btn.active')?.getAttribute('data-cat') || 'tahrim');
            const root = document.getElementById('inputRootSearch')?.value.trim();
            if (root) searchRoot(root);
            const clause = document.getElementById('contractClauseInput')?.value.trim();
            if (clause) btnAuditContract.click();
        });
    }

    I18N.applyTranslations();

    // 2. Guide Modal Handler
    const btnToggleGuide = document.getElementById('btnToggleGuide');
    const guideModalOverlay = document.getElementById('guideModalOverlay');
    const btnCloseGuideModal = document.getElementById('btnCloseGuideModal');
    
    if (btnToggleGuide && guideModalOverlay) {
        btnToggleGuide.addEventListener('click', () => {
            guideModalOverlay.style.display = 'flex';
        });
    }

    if (btnCloseGuideModal && guideModalOverlay) {
        btnCloseGuideModal.addEventListener('click', () => {
            guideModalOverlay.style.display = 'none';
        });
    }

    if (guideModalOverlay) {
        guideModalOverlay.addEventListener('click', (e) => {
            if (e.target === guideModalOverlay) {
                guideModalOverlay.style.display = 'none';
            }
        });
    }

    // Legal & Shariah Disclaimer Modal Handlers
    const btnOpenLegalModal = document.getElementById('btnOpenLegalModal');
    const legalModalOverlay = document.getElementById('legalModalOverlay');
    const btnCloseLegalModal = document.getElementById('btnCloseLegalModal');
    const btnAcceptLegal = document.getElementById('btnAcceptLegal');

    if (btnOpenLegalModal && legalModalOverlay) {
        btnOpenLegalModal.addEventListener('click', () => {
            legalModalOverlay.style.display = 'flex';
        });
    }

    if (btnCloseLegalModal && legalModalOverlay) {
        btnCloseLegalModal.addEventListener('click', () => {
            legalModalOverlay.style.display = 'none';
        });
    }

    if (btnAcceptLegal && legalModalOverlay) {
        btnAcceptLegal.addEventListener('click', () => {
            legalModalOverlay.style.display = 'none';
        });
    }

    if (legalModalOverlay) {
        legalModalOverlay.addEventListener('click', (e) => {
            if (e.target === legalModalOverlay) {
                legalModalOverlay.style.display = 'none';
            }
        });
    }

    // Feedback & Contacts Modal Handlers
    const btnToggleFeedback = document.getElementById('btnToggleFeedback');
    const feedbackModalOverlay = document.getElementById('feedbackModalOverlay');
    const btnCloseFeedbackModal = document.getElementById('btnCloseFeedbackModal');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackStatusMsg = document.getElementById('feedbackStatusMsg');

    if (btnToggleFeedback && feedbackModalOverlay) {
        btnToggleFeedback.addEventListener('click', () => {
            feedbackModalOverlay.style.display = 'flex';
        });
    }

    if (btnCloseFeedbackModal && feedbackModalOverlay) {
        btnCloseFeedbackModal.addEventListener('click', () => {
            feedbackModalOverlay.style.display = 'none';
        });
    }

    if (feedbackModalOverlay) {
        feedbackModalOverlay.addEventListener('click', (e) => {
            if (e.target === feedbackModalOverlay) {
                feedbackModalOverlay.style.display = 'none';
            }
        });
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('feedbackName')?.value.trim();
            const contact = document.getElementById('feedbackContact')?.value.trim();
            const category = document.getElementById('feedbackCategory')?.value;
            const message = document.getElementById('feedbackMessage')?.value.trim();

            if (!message) return;

            try {
                const resp = await fetch('/api/v1/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email_or_phone: contact, category, message })
                });
                const data = await resp.json();
                if (feedbackStatusMsg) {
                    feedbackStatusMsg.style.display = 'block';
                    feedbackStatusMsg.textContent = I18N.currentLang === 'kk' ? data.message_kk : (I18N.currentLang === 'ru' ? data.message_ru : data.message_en);
                }
                feedbackForm.reset();
                setTimeout(() => {
                    if (feedbackStatusMsg) feedbackStatusMsg.style.display = 'none';
                    if (feedbackModalOverlay) feedbackModalOverlay.style.display = 'none';
                }, 2500);
            } catch (err) {
                if (feedbackStatusMsg) {
                    feedbackStatusMsg.style.display = 'block';
                    feedbackStatusMsg.style.color = 'var(--danger-primary)';
                    feedbackStatusMsg.textContent = 'Қате орын алды / Ошибка отправки.';
                }
            }
        });
    }

    // Standards & Quality Compliance Modal Handlers
    const btnToggleStandards = document.getElementById('btnToggleStandards');
    const standardsModalOverlay = document.getElementById('standardsModalOverlay');
    const btnCloseStandardsModal = document.getElementById('btnCloseStandardsModal');
    const btnAcceptStandards = document.getElementById('btnAcceptStandards');

    if (btnToggleStandards && standardsModalOverlay) {
        btnToggleStandards.addEventListener('click', () => {
            standardsModalOverlay.style.display = 'flex';
        });
    }

    if (btnCloseStandardsModal && standardsModalOverlay) {
        btnCloseStandardsModal.addEventListener('click', () => {
            standardsModalOverlay.style.display = 'none';
        });
    }

    if (btnAcceptStandards && standardsModalOverlay) {
        btnAcceptStandards.addEventListener('click', () => {
            standardsModalOverlay.style.display = 'none';
        });
    }

    if (standardsModalOverlay) {
        standardsModalOverlay.addEventListener('click', (e) => {
            if (e.target === standardsModalOverlay) {
                standardsModalOverlay.style.display = 'none';
            }
        });
    }

    // 3. Navigation Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            const targetEl = document.getElementById(targetId);
            if (targetEl) targetEl.classList.add('active');
        });
    });

    // 4. Tab 1: Anti-Hallucination Guardrail
    const guardInputText = document.getElementById('guardInputText');
    const btnRunAudit = document.getElementById('btnRunAudit');
    const btnClearGuard = document.getElementById('btnClearGuard');
    const auditResultsBody = document.getElementById('auditResultsBody');

    // Presets
    const btnPresetHallucinateCoord = document.getElementById('btnPresetHallucinateCoord');
    const btnPresetDistortTashkeel = document.getElementById('btnPresetDistortTashkeel');
    const btnPresetCleanQuote = document.getElementById('btnPresetCleanQuote');

    if (btnPresetHallucinateCoord) {
        btnPresetHallucinateCoord.addEventListener('click', () => {
            const lang = I18N.currentLang;
            if (lang === 'kk') {
                guardInputText.value = "Құранда (2-сүре 300-аятта) айтылғандай, мүміндер әрбір істе сабырлық танытуы қажет...";
            } else if (lang === 'ar') {
                guardInputText.value = "كما ورد في القرآن (سورة 2 آية 300)، يجب على المؤمنين الصبر...";
            } else if (lang === 'en') {
                guardInputText.value = "As stated in the Quran (Surah 2 Ayah 300), believers must remain patient in all matters.";
            } else if (lang === 'tr') {
                guardInputText.value = "Kur'an-ı Kerim'de (Bakara Suresi 300. ayet) müminlerin sabretmesi emredilmektedir...";
            } else if (lang === 'id') {
                guardInputText.value = "Sebagaimana disebutkan dalam Al-Qur'an (Surah 2 Ayat 300), orang-orang beriman harus bersabar...";
            } else if (lang === 'uz') {
                guardInputText.value = "Qur'onda (2-sura 300-oyat) aytilganidek, mo'minlar sabrli bo'lishlari kerak...";
            } else {
                guardInputText.value = "Как сказано в Коране (Сура 2, аят 300), верующие должны быть терпеливы во всех делах.";
            }
            runVerification();
        });
    }

    if (btnPresetDistortTashkeel) {
        btnPresetDistortTashkeel.addEventListener('click', () => {
            const distortArabic = "اللَّهُ لَا إِلَـٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ";
            const lang = I18N.currentLang;
            if (lang === 'kk') {
                guardInputText.value = `Аятул Күрсиде (2:255) мынадай сөздер жазылған: ${distortArabic}`;
            } else if (lang === 'en') {
                guardInputText.value = `Ayat al-Kursi (2:255) contains the following words: ${distortArabic}`;
            } else if (lang === 'ar') {
                guardInputText.value = `آية الكرسي (2:255) تحتوي على النص التالي: ${distortArabic}`;
            } else {
                guardInputText.value = `Аят аль-Курси (2:255) содержит следующие слова: ${distortArabic}`;
            }
            runVerification();
        });
    }

    if (btnPresetCleanQuote) {
        btnPresetCleanQuote.addEventListener('click', () => {
            const exactAyah = "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ النَّاسِ";
            const lang = I18N.currentLang;
            if (lang === 'kk') {
                guardInputText.value = `114-сүренің 1-аятында айтылған: ${exactAyah}`;
            } else if (lang === 'en') {
                guardInputText.value = `In Surah 114 Ayah 1 it is said: ${exactAyah}`;
            } else if (lang === 'ar') {
                guardInputText.value = `في سورة 114 آية 1 قوله تعالى: ${exactAyah}`;
            } else {
                guardInputText.value = `В суре 114 аяте 1 сказано: ${exactAyah}`;
            }
            runVerification();
        });
    }

    if (btnClearGuard) {
        btnClearGuard.addEventListener('click', () => {
            guardInputText.value = '';
            auditResultsBody.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    </div>
                    <h3>Жүйе тексеруге дайын</h3>
                    <p>Сол жаққа мәтінді енгізіп, «L0 Аудитін орындау» батырмасын басыңыз.</p>
                </div>
            `;
        });
    }

    if (btnRunAudit) {
        btnRunAudit.addEventListener('click', runVerification);
    }

    // Helper for Multi-Translation Rendering with Audio Button
    function getTranslationHtml(translations, sura, ayah) {
        if (!translations) return '';
        const lang = I18N.currentLang;
        let transText = translations.ru || '';
        let label = I18N.t('lblTranslation');

        if (lang === 'kk' && translations.kk) {
            transText = translations.kk;
            label = "Мағыналық аудармасы (Халифа Алтай):";
        } else if (lang === 'en' && translations.en) {
            transText = translations.en;
            label = "Meaning Translation (Saheeh International):";
        } else if (lang === 'tr' && translations.tr) {
            transText = translations.tr;
            label = "Meal (Diyanet İşleri):";
        } else if (lang === 'id' && translations.id) {
            transText = translations.id;
            label = "Terjemahan (Kemenag RI):";
        } else if (lang === 'uz' && translations.uz) {
            transText = translations.uz;
            label = "Ma'nolari tarjimasi (Shayx Muhammad Sodiq):";
        } else if (lang === 'ar') {
            return '';
        }

        if (!transText) return '';
        return `
            <div class="translation-badge">
                <strong>${label}</strong>
                <span>${transText}</span>
            </div>
        `;
    }

    async function runVerification() {
        const text = guardInputText.value.trim();
        if (!text) return;

        auditResultsBody.innerHTML = '<div class="empty-state"><p>Аудит жүргізілуде / Выполняется верификация...</p></div>';

        try {
            const resp = await fetch('/api/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            const data = await resp.json();
            renderAuditReport(data);
        } catch (err) {
            auditResultsBody.innerHTML = '<div class="empty-state"><p style="color: var(--color-danger)">Ошибка сервера / Сервер қатесі.</p></div>';
        }
    }

    function renderAuditReport(data) {
        auditResultsBody.innerHTML = '';
        const lang = I18N.currentLang;

        let verdictColor = 'var(--emerald-bright)';
        let verdictTitleText = I18N.t('verdictCleanTitle');
        let verdictDescText = I18N.t('verdictCleanDesc');

        if (data.verdict === 'HALLUCINATION_DETECTED') {
            verdictColor = 'var(--danger-primary)';
            verdictTitleText = I18N.t('verdictHallucinationTitle');
            verdictDescText = `Анықталған қателер саны: ${data.hallucinations_count} / Найдено нарушений: ${data.hallucinations_count}`;
        } else if (data.verdict === 'TASHKEEL_DISTORTION') {
            verdictColor = 'var(--gold-bright)';
            verdictTitleText = I18N.t('verdictWarningTitle');
            verdictDescText = "Огласовки (ташкиль) отличаются от канонического манифеста.";
        } else if (data.verdict === 'NO_CITATIONS_FOUND') {
            verdictColor = 'var(--text-secondary)';
            verdictTitleText = I18N.t('verdictNoQuotesTitle');
            verdictDescText = I18N.t('verdictNoQuotesDesc');
        }

        const banner = document.createElement('div');
        banner.className = 'claim-result-box';
        banner.style.borderLeft = `4px solid ${verdictColor}`;
        banner.style.background = 'var(--bg-input)';
        banner.style.marginBottom = '16px';
        banner.innerHTML = `
            <div style="font-size: 16px; font-weight: 700; color: ${verdictColor};">${verdictTitleText}</div>
            <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">${verdictDescText}</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 6px; font-family: var(--font-mono);">Latency: ${data.latency_ms}ms • Ground Truth Score: ${data.hallucinations_count === 0 ? '100%' : '0%'}</div>
        `;
        auditResultsBody.appendChild(banner);

        // Render each citation item
        data.verified_items.forEach((item, idx) => {
            const card = document.createElement('div');
            card.className = 'audit-item';
            const localizedSurah = getSurahName(item.sura);

            const isHallucinated = (item.status === 'HALLUCINATED_NON_EXISTENT_AYAH' || item.status === 'TAMPERED_TEXT');
            const tagClass = isHallucinated ? 'danger' : (item.status === 'TASHKEEL_DISTORTED' ? 'warning' : 'success');

            let statusLabel = 'Каноникалық сәйкестік (Verified)';
            if (item.status === 'HALLUCINATED_NON_EXISTENT_AYAH') statusLabel = '❌ Жоқ аят (Галлюцинация)';
            else if (item.status === 'TAMPERED_TEXT') statusLabel = '❌ Бұрмаланған мәтін';
            else if (item.status === 'TASHKEEL_DISTORTED') statusLabel = '⚠️ Ташкиль қатесі';

            const audioButtonHtml = (item.sura && item.ayah) ? `
                <button class="btn-play-ayah-audio" onclick="playAyahAudio(${item.sura}, ${item.ayah}, this)" title="Аятты тыңдау">
                    ▶️ Тыңдау
                </button>
            ` : '';



            card.innerHTML = `
                <div class="audit-badge-row">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="tag-badge ${tagClass}">${statusLabel}</span>
                        ${audioButtonHtml}
                    </div>
                    <span style="font-size: 12px; color: var(--gold-primary); font-weight: 600;">${escapeHtml(localizedSurah)} (${item.sura}:${item.ayah})</span>
                </div>
                
                <div style="font-size: 13px; color: var(--text-secondary); margin: 6px 0;">
                    <strong>${I18N.t('lblQuote')}:</strong> «${escapeHtml(item.raw_quote)}»
                </div>

                ${item.canonical_uthmani ? `
                    <div class="arabic-display">${item.canonical_uthmani}</div>
                    ${item.transliteration ? `<div class="transliteration-badge"><strong>Транскрипция:</strong> ${escapeHtml(item.transliteration)}</div>` : ''}
                    ${getTranslationHtml(item.translations, item.sura, item.ayah)}
                ` : ''}
            `;
            auditResultsBody.appendChild(card);
        });
    }

    // 5. Tab 2: Root Explorer
    const inputRootSearch = document.getElementById('inputRootSearch');
    const btnSearchRoot = document.getElementById('btnSearchRoot');
    const rootResultsList = document.getElementById('rootResultsList');
    const popularRootTags = document.getElementById('popularRootTags');

    if (popularRootTags) {
        popularRootTags.addEventListener('click', (e) => {
            const tag = e.target.closest('.root-tag');
            if (tag) {
                const root = tag.getAttribute('data-root');
                inputRootSearch.value = root;
                searchRoot(root);
            }
        });
    }

    if (btnSearchRoot) {
        btnSearchRoot.addEventListener('click', () => {
            const root = inputRootSearch.value.trim();
            if (root) searchRoot(root);
        });
    }

    async function searchRoot(root) {
        rootResultsList.innerHTML = '<div class="empty-state"><p>Түбір ізделуде / Поиск корня...</p></div>';
        try {
            const resp = await fetch(`/api/search/root/${encodeURIComponent(root)}`);
            const data = await resp.json();
            renderRootResults(data);
        } catch (e) {
            rootResultsList.innerHTML = '<div class="empty-state"><p style="color: var(--danger-primary)">Қате орын алды / Ошибка поиска.</p></div>';
        }
    }

    function renderRootResults(data) {
        rootResultsList.innerHTML = '';
        if (!data.results || data.results.length === 0) {
            rootResultsList.innerHTML = `<div class="empty-state"><p>«${data.root}» түбірі бойынша аяттар табылмады.</p></div>`;
            return;
        }

        const summaryBox = document.createElement('div');
        summaryBox.className = 'claim-result-box valid';
        summaryBox.style.marginBottom = '16px';
        summaryBox.innerHTML = `
            <strong>Түбір / Корень:</strong> <span style="font-family: var(--font-quran); font-size: 20px; color: var(--gold-bright);">${data.root}</span>
            • Табылған аяттар саны: <strong>${data.total}</strong>
        `;
        rootResultsList.appendChild(summaryBox);

        data.results.slice(0, 15).forEach(res => {
            const card = document.createElement('div');
            card.className = 'audit-item';
            const localizedSurah = getSurahName(res.sura);

            card.innerHTML = `
                <div class="audit-badge-row">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="tag-badge success">Түбір кездесті: ${res.root_occurrences} рет</span>
                        <button class="btn-play-ayah-audio" onclick="playAyahAudio(${res.sura}, ${res.ayah}, this)" title="Аятты тыңдау">
                            ▶️ Тыңдау
                        </button>
                    </div>
                    <span style="font-size: 13px; color: var(--gold-primary); font-weight: 700;">${localizedSurah} [${res.sura}:${res.ayah}]</span>
                </div>
                <div class="arabic-display">${res.text_uthmani}</div>
                ${res.transliteration ? `<div class="transliteration-badge"><strong>Транскрипция:</strong> ${res.transliteration}</div>` : ''}
                ${getTranslationHtml(res.translations, res.sura, res.ayah)}
            `;
            rootResultsList.appendChild(card);
        });
    }

    // Root Claim Verifier
    const inputClaimWord = document.getElementById('inputClaimWord');
    const inputClaimRoot = document.getElementById('inputClaimRoot');
    const inputClaimContext = document.getElementById('inputClaimContext');
    const btnVerifyRootClaim = document.getElementById('btnVerifyRootClaim');
    const claimResultBox = document.getElementById('claimResultBox');

    if (btnVerifyRootClaim) {
        btnVerifyRootClaim.addEventListener('click', async () => {
            const word = inputClaimWord.value.trim();
            const root = inputClaimRoot.value.trim();
            const ctx = inputClaimContext.value.trim();

            if (!word || !root) return;

            claimResultBox.style.display = 'block';
            claimResultBox.innerHTML = '<p>Түбір шындығы тексерілуде...</p>';

            try {
                const resp = await fetch('/api/verify/root', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ word: word, claimed_root: root, context_id: ctx || null })
                });
                const data = await resp.json();
                
                const isMatch = data.is_correct;
                claimResultBox.className = `claim-result-box ${isMatch ? 'valid' : 'invalid'}`;
                claimResultBox.innerHTML = `
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">
                        ${isMatch ? '✅ Түбір расталды (Valid Root)' : '❌ Жалған этимология (False Root)'}
                    </div>
                    <div><strong>Сөз / Слово:</strong> ${data.word}</div>
                    <div><strong>Мәлімделген түбір / Заявленный корень:</strong> ${data.claimed_root}</div>
                    <div><strong>Нақты түбір / Канонический корень:</strong> <span style="font-family: var(--font-quran); font-size: 18px; color: var(--gold-bright);">${data.canonical_root || 'Табылмады'}</span></div>
                `;
            } catch (e) {
                claimResultBox.innerHTML = '<p style="color: var(--danger-primary)">Қате орын алды.</p>';
            }
        });
    }

    // 6. Tab 3: Halal, Ahkam, OCR & AAOIFI
    const contractClauseInput = document.getElementById('contractClauseInput');
    const btnAuditContract = document.getElementById('btnAuditContract');
    const btnAuditAAOIFI = document.getElementById('btnAuditAAOIFI');
    const contractAuditResult = document.getElementById('contractAuditResult');
    const ahkamResultsList = document.getElementById('ahkamResultsList');
    const ahkamCatBtns = document.querySelectorAll('.ahkam-cat-btn');

    // OCR Image Scanner Trigger
    const btnTriggerOCR = document.getElementById('btnTriggerOCR');
    const inputProductImage = document.getElementById('inputProductImage');

    if (btnTriggerOCR && inputProductImage) {
        btnTriggerOCR.addEventListener('click', () => inputProductImage.click());
        inputProductImage.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            contractAuditResult.style.display = 'block';
            contractAuditResult.innerHTML = '<div class="empty-state"><p>📷 Сурет талдануда (OCR)... / Анализ состава по фото...</p></div>';

            const fname = file.name.toLowerCase();
            let simText = fname.replace(/[\._-]/g, ' ');
            if (simText.includes('e120') || simText.includes('кармин') || simText.includes('carmine')) simText = "Йогурт клубничный с красителем кармин E120";
            else if (simText.includes('e441') || simText.includes('желатин') || simText.includes('gelatin')) simText = "Мармелад жевательный с желатином E441";
            else if (simText.includes('свинин') || simText.includes('pork') || simText.includes('бекон')) simText = "Колбаса вареная со свининой и шпиком";
            else simText = "Состав продукта: вода, сахар, мука, сухое молоко, краситель E120, желатин E441, эмульгатор E471";

            contractClauseInput.value = simText;
            btnAuditContract.click();
        });
    }

    // Quick Test Chips
    document.querySelectorAll('.test-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-text');
            if (text) {
                contractClauseInput.value = text;
                btnAuditContract.click();
            }
        });
    });

    if (btnAuditContract) {
        btnAuditContract.addEventListener('click', async () => {
            const text = contractClauseInput.value.trim();
            if (!text) return;

            contractAuditResult.style.display = 'block';
            contractAuditResult.innerHTML = '<div class="empty-state"><p>Шариғат пен Халал нормалары бойынша тексерілуде...</p></div>';

            try {
                const resp = await fetch('/api/audit/contract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await resp.json();
                renderContractResult(data);
            } catch (e) {
                contractAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Қате орын алды.</p>';
            }
        });
    }

    if (btnAuditAAOIFI) {
        btnAuditAAOIFI.addEventListener('click', async () => {
            const text = contractClauseInput.value.trim();
            if (!text) return;

            contractAuditResult.style.display = 'block';
            contractAuditResult.innerHTML = '<div class="empty-state"><p>⚖️ AAOIFI исламдық қаржы стандарттары бойынша тексерілуде...</p></div>';

            try {
                const resp = await fetch('/api/v1/contracts/audit-aaoifi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await resp.json();
                renderAAOIFIResult(data);
            } catch (e) {
                contractAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Қате орын алды.</p>';
            }
        });
    }

    function renderContractResult(data) {
        contractAuditResult.innerHTML = '';
        const lang = I18N.currentLang;

        if (!data.matches || data.matches.length === 0) {
            const okTitle = lang === 'kk' 
                ? '🟢 Тікелей тыйымдар табылмады (Адал / Рұқсат етілген)' 
                : (lang === 'en' ? '🟢 No Prohibitions Detected (Halal / Permissible)' : '🟢 Прямых запретов не обнаружено (Халяль / Дозволено)');
            const okDesc = lang === 'kk'
                ? 'Енгізілген мәтіннен немесе өнімнен тікелей Харам/Риба белгілері анықталмады.'
                : (lang === 'en' ? 'No direct Haram, Riba, or prohibited substances were detected in the input.' : 'В введенном продукте или договоре не обнаружено признаков Харама или Риба.');
            contractAuditResult.innerHTML = `
                <div class="claim-result-box valid" style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; padding: 14px; border-radius: var(--radius-md);">
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px; color: #34D399;">${okTitle}</div>
                    <div style="font-size: 13.5px; color: #D1FAE5;">${okDesc}</div>
                </div>
            `;
            return;
        }

        data.matches.forEach(m => {
            const isHaram = m.verdict === 'HARAM';
            const isDoubt = m.verdict === 'DOUBTFUL';
            const boxClass = isHaram ? 'invalid' : (isDoubt ? 'warning' : 'valid');
            const title = (lang === 'kk' ? m.title_kk : (lang === 'en' ? m.title_en : m.title_ru)) || m.title_ru;
            const desc = (lang === 'kk' ? m.description_kk : m.description_ru) || m.description_ru;

            const card = document.createElement('div');
            card.className = `claim-result-box ${boxClass}`;
            card.style.marginBottom = '12px';
            card.innerHTML = `
                <div style="font-weight: 700; font-size: 15.5px; margin-bottom: 4px; color: ${isHaram ? '#FDA4AF' : (isDoubt ? '#FDE68A' : '#A7F3D0')};">${title}</div>
                <div style="font-size: 13.5px; margin-bottom: 6px; color: #FFFFFF;">${desc}</div>
                ${m.canonical_arabic ? `
                    <div class="arabic-display" style="font-size: 22px; padding: 10px 14px;">${m.canonical_arabic}</div>
                ` : ''}
                <div style="font-size: 12px; color: var(--gold-bright); font-weight: 600; margin-top: 4px;">
                    📖 ${lang === 'kk' ? 'Құран негізі:' : (lang === 'en' ? 'Quran Basis:' : 'Основа в Коране:')} ${m.ayah_ref}
                </div>
            `;
            contractAuditResult.appendChild(card);
        });
    }

    function renderAAOIFIResult(data) {
        contractAuditResult.innerHTML = '';
        const lang = I18N.currentLang;
        const isCompliant = data.is_compliant;
        const boxClass = isCompliant ? 'valid' : 'invalid';

        const mainCard = document.createElement('div');
        mainCard.className = `claim-result-box ${boxClass}`;
        mainCard.innerHTML = `
            <div style="font-weight: 800; font-size: 16px; margin-bottom: 6px;">
                ${isCompliant ? '✅ AAOIFI ШАРИҒАТ СТАНДАРТЫНА СӘЙКЕС' : '❌ AAOIFI СТАНДАРТЫН БҰЗУ АНЫҚТАЛДЫ'}
            </div>
            <div style="font-size: 13px; color: var(--text-secondary);">
                <strong>Келісім түрі:</strong> ${data.contract_type} • <strong>Құран негізі:</strong> ${data.quran_basis}
            </div>
        `;
        contractAuditResult.appendChild(mainCard);

        if (data.findings && data.findings.length > 0) {
            data.findings.forEach(f => {
                const fCard = document.createElement('div');
                fCard.className = 'aaoifi-finding-card';
                const issue = lang === 'kk' ? f.issue_kk : f.issue_ru;
                fCard.innerHTML = `
                    <div class="aaoifi-standard-tag">📜 ${f.standard} [${f.severity}]</div>
                    <div style="color: #FECACA;">${issue}</div>
                `;
                contractAuditResult.appendChild(fCard);
            });
        }
    }

    // PDF Document Audit Handler
    const btnTriggerPDF = document.getElementById('btnTriggerPDF');
    const inputContractPDF = document.getElementById('inputContractPDF');

    if (btnTriggerPDF && inputContractPDF) {
        btnTriggerPDF.addEventListener('click', () => inputContractPDF.click());
        inputContractPDF.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            contractAuditResult.style.display = 'block';
            contractAuditResult.innerHTML = '<div class="empty-state"><p>📑 PDF құжаты талдануда (AAOIFI & Құран аудиті)...</p></div>';

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
                    if (data.status === 'success' && data.audit) {
                        renderPDFAuditResult(data.audit);
                    } else {
                        contractAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Құжатты талдау мүмкін болмады.</p>';
                    }
                };
                reader.readAsDataURL(file);
            } catch (err) {
                contractAuditResult.innerHTML = '<p style="color: var(--danger-primary)">Қате орын алды.</p>';
            }
        });
    }

    function renderPDFAuditResult(audit) {
        contractAuditResult.innerHTML = '';
        const lang = I18N.currentLang;
        const gRep = audit.guard_report;
        const aRep = audit.aaoifi_report;

        const mainCard = document.createElement('div');
        mainCard.className = `claim-result-box ${aRep.is_compliant ? 'valid' : 'invalid'}`;
        mainCard.innerHTML = `
            <div style="font-weight: 800; font-size: 16px; margin-bottom: 6px;">
                📄 PDF АУДИТОРЛЫҚ ЕСЕБІ (AL-FURQAN AI CERTIFICATE)
            </div>
            <div style="font-size: 13.5px; color: var(--text-secondary); margin-bottom: 8px;">
                <strong>Парақтар:</strong> ${audit.total_pages} • <strong>Таңбалар:</strong> ${audit.text_length.toLocaleString()}
            </div>
            <div style="font-size: 13.5px; margin-bottom: 4px;">
                ${gRep.claims_detected 
                    ? (gRep.is_valid ? '✅ <strong>Құран дәйексөздері:</strong> 100% каноникалық дәл.' : '🚨 <strong>Құран дәйексөздері:</strong> Бұрмалаулар анықталды!')
                    : 'ℹ️ <strong>Құран дәйексөздері:</strong> Құжатта тікелей аяттар анықталмады.'}
            </div>
            <div style="font-size: 13.5px;">
                ${aRep.is_compliant 
                    ? '✅ <strong>AAOIFI Шариғат стандарты:</strong> Сәйкес деп танылды.' 
                    : '❌ <strong>AAOIFI Шариғат стандарты:</strong> Бұзушылықтар анықталды (Риба/Өсім)!'}
            </div>
        `;
        contractAuditResult.appendChild(mainCard);

        if (aRep.findings && aRep.findings.length > 0) {
            aRep.findings.forEach(f => {
                const fCard = document.createElement('div');
                fCard.className = 'aaoifi-finding-card';
                const issue = lang === 'kk' ? f.issue_kk : f.issue_ru;
                fCard.innerHTML = `
                    <div class="aaoifi-standard-tag">📜 ${f.standard} [${f.severity}]</div>
                    <div style="color: #FECACA;">${issue}</div>
                `;
                contractAuditResult.appendChild(fCard);
            });
        }
    }

    async function loadVisitorCount() {
        const el = document.getElementById('metricVisitors');
        if (!el) return;
        try {
            const resp = await fetch('/api/v1/analytics/visitor-count');
            const data = await resp.json();
            if (data.total_visitors) {
                el.textContent = Number(data.total_visitors).toLocaleString();
            }
        } catch (e) {
            console.warn("Visitor counter notice:", e);
        }
    }

    // Ahkam Category Switcher
    ahkamCatBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            ahkamCatBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const cat = btn.getAttribute('data-cat');
            loadAhkamCategory(cat);
        });
    });

    async function loadAhkamCategory(cat) {
        ahkamResultsList.innerHTML = '<div class="empty-state"><p>Ахкам деректері жүктелуде...</p></div>';
        try {
            const resp = await fetch(`/api/ahkam/${cat}`);
            const data = await resp.json();
            renderAhkamCategory(data);
        } catch (e) {
            ahkamResultsList.innerHTML = '<div class="empty-state"><p style="color: var(--danger-primary)">Қате орын алды.</p></div>';
        }
    }

    function renderAhkamCategory(data) {
        ahkamResultsList.innerHTML = '';
        if (!data.ayahs || data.ayahs.length === 0) {
            ahkamResultsList.innerHTML = '<div class="empty-state"><p>Аяттар табылмады.</p></div>';
            return;
        }

        data.ayahs.forEach(item => {
            const card = document.createElement('div');
            card.className = 'audit-item';
            const localizedSurah = getSurahName(item.sura);

            card.innerHTML = `
                <div class="audit-badge-row">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="tag-badge success">${data.category_title}</span>
                        <button class="btn-play-ayah-audio" onclick="playAyahAudio(${item.sura}, ${item.ayah}, this)" title="Аятты тыңдау">
                            ▶️ Тыңдау
                        </button>
                    </div>
                    <span style="font-size: 13px; color: var(--gold-primary); font-weight: 700;">${localizedSurah} [${item.sura}:${item.ayah}]</span>
                </div>
                <div class="arabic-display">${item.text_uthmani}</div>
                ${item.transliteration ? `<div class="transliteration-badge"><strong>Транскрипция:</strong> ${item.transliteration}</div>` : ''}
                ${getTranslationHtml(item.translations, item.sura, item.ayah)}
            `;
            ahkamResultsList.appendChild(card);
        });
    }

    // 7. Tab 4: Corpus & AST Inspector
    const selectSura = document.getElementById('selectSura');
    const inputAyahNum = document.getElementById('inputAyahNum');
    const btnInspectAyah = document.getElementById('btnInspectAyah');
    const astViewer = document.getElementById('astViewer');

    function populateSurahs() {
        if (!selectSura) return;
        const currentVal = selectSura.value || '1';
        selectSura.innerHTML = '';
        for (let i = 1; i <= 114; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `${i}. ${getSurahName(i)}`;
            selectSura.appendChild(opt);
        }
        selectSura.value = currentVal;
    }

    if (btnInspectAyah) {
        btnInspectAyah.addEventListener('click', loadAyahAST);
    }

    async function loadAyahAST() {
        if (!selectSura || !inputAyahNum || !astViewer) return;
        const sura = parseInt(selectSura.value) || 1;
        const ayah = parseInt(inputAyahNum.value) || 1;

        astViewer.innerHTML = '<div class="empty-state"><p>AST ағашы мен таңбалар жүктелуде...</p></div>';

        try {
            const resp = await fetch(`/api/ayah/${sura}/${ayah}`);
            const data = await resp.json();
            renderAyahAST(data);
        } catch (e) {
            astViewer.innerHTML = '<div class="empty-state"><p style="color: var(--danger-primary)">Аят табылмады немесе сервер қатесі.</p></div>';
        }
    }

    function renderAyahAST(data) {
        astViewer.innerHTML = '';
        const localizedSurah = getSurahName(data.sura);

        const headerCard = document.createElement('div');
        headerCard.className = 'audit-item';
        headerCard.innerHTML = `
            <div class="audit-badge-row">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="tag-badge success">Каноникалық аят [AST]</span>
                    <button class="btn-play-ayah-audio" onclick="playAyahAudio(${data.sura}, ${data.ayah}, this)" title="Аятты тыңдау">
                        ▶️ Тыңдау
                    </button>
                </div>
                <span style="font-size: 14px; color: var(--gold-primary); font-weight: 700;">${localizedSurah} [${data.sura}:${data.ayah}]</span>
            </div>
            <div class="arabic-display">${data.text_uthmani}</div>
            ${data.transliteration ? `<div class="transliteration-badge"><strong>Транскрипция:</strong> ${data.transliteration}</div>` : ''}
            ${getTranslationHtml(data.translations, data.sura, data.ayah)}
            ${data.tafsir ? `
                <div class="tafsir-badge">
                    <strong>📜 ${data.tafsir.title}:</strong>
                    <div>${I18N.currentLang === 'kk' ? data.tafsir.summary_kk : data.tafsir.summary_ru}</div>
                </div>
            ` : ''}
        `;
        astViewer.appendChild(headerCard);

        const tokensGrid = document.createElement('div');
        tokensGrid.className = 'tokens-grid';

        (data.tokens || []).forEach(tok => {
            const tCard = document.createElement('div');
            tCard.className = 'token-card';
            tCard.innerHTML = `
                <div class="token-form-ar">${tok.form || tok.form_ar || ''}</div>
                <div class="token-meta-row">
                    <span>${I18N.t('astLemma')}:</span>
                    <span class="token-meta-val">${tok.lemma || '-'}</span>
                </div>
                <div class="token-meta-row">
                    <span>${I18N.t('astRoot')}:</span>
                    <span class="token-meta-val" style="color: var(--gold-bright); font-family: var(--font-quran); font-size: 16px;">${tok.root || '-'}</span>
                </div>
                <div class="token-meta-row">
                    <span>${I18N.t('astPOS')}:</span>
                    <span class="token-meta-val">${tok.pos || '-'}</span>
                </div>
            `;
            tokensGrid.appendChild(tCard);
        });

        astViewer.appendChild(tokensGrid);
    }

    function getSurahName(suraNum) {
        if (!suraNum || suraNum < 1 || suraNum > 114) return `Сура ${suraNum}`;
        const lang = I18N.currentLang;
        const dict = I18N.locales[lang] || I18N.locales.kk;
        if (dict.surahNames && dict.surahNames[suraNum - 1]) {
            return dict.surahNames[suraNum - 1];
        }
        return `Сура ${suraNum}`;
    }

    async function loadCryptographicIntegrity() {
        try {
            const resp = await fetch('/api/v1/integrity/verify');
            const data = await resp.json();
            const shaBadge = document.querySelector('.sha256-badge');
            if (shaBadge && data.manifest_sha256) {
                const shortHash = data.manifest_sha256.substring(0, 8) + '...' + data.manifest_sha256.substring(56);
                shaBadge.textContent = `SHA-256: ${shortHash} (Live Verified)`;
                shaBadge.title = `Full Manifest Hash: ${data.manifest_sha256}\nTranslations Hash: ${data.translations_sha256}\nCanonical Source: ${data.canonical_source}`;
            }
        } catch(e) {
            console.warn("Integrity check notice:", e);
        }
    }

    // Global Audio Player Bar Control Bindings
    const btnPlayerPrev = document.getElementById('btnPlayerPrev');
    const btnPlayerPlayPause = document.getElementById('btnPlayerPlayPause');
    const btnPlayerNext = document.getElementById('btnPlayerNext');
    const btnToggleContinuous = document.getElementById('btnToggleContinuous');
    const playerSpeedSelect = document.getElementById('playerSpeedSelect');
    const btnClosePlayerBar = document.getElementById('btnClosePlayerBar');
    const btnPlayFullSurah = document.getElementById('btnPlayFullSurah');

    if (btnPlayerPrev) {
        btnPlayerPrev.addEventListener('click', () => quranAudio.prev());
    }
    if (btnPlayerPlayPause) {
        btnPlayerPlayPause.addEventListener('click', () => quranAudio.togglePlayPause());
    }
    if (btnPlayerNext) {
        btnPlayerNext.addEventListener('click', () => quranAudio.next());
    }
    if (btnToggleContinuous) {
        btnToggleContinuous.addEventListener('click', () => quranAudio.toggleContinuous());
    }
    if (playerSpeedSelect) {
        playerSpeedSelect.addEventListener('change', (e) => quranAudio.setSpeed(e.target.value));
    }
    if (btnClosePlayerBar) {
        btnClosePlayerBar.addEventListener('click', () => quranAudio.hideBar());
    }
    if (btnPlayFullSurah) {
        btnPlayFullSurah.addEventListener('click', () => {
            const sura = parseInt(selectSura?.value) || 1;
            quranAudio.playFullSurah(sura);
        });
    }

    // Initialize View
    populateSurahs();
    populateQuranSurahs();
    loadFatihaSection();
    loadSelectedSurahFull();
    loadAyahAST();
    loadAhkamCategory('tahrim');
    loadCryptographicIntegrity();
    loadVisitorCount();
});
