/**
 * Lusitanie IA - Widget Flottant
 * Intégrez ce script dans votre blog pour ajouter un bouton flottant Lusitanie IA
 * 
 * Usage:
 * <script src="https://votre-domaine.com/lusitanie-widget.js"></script>
 * <script>
 *   LusitanieWidget.init({
 *     appUrl: 'https://lusiaai-vxcarjwn.manus.space',
 *     position: 'bottom-right', // 'bottom-right', 'bottom-left'
 *     theme: 'dark' // 'dark', 'light'
 *   });
 * </script>
 */

(function() {
    const LusitanieWidget = {
        config: {
            appUrl: 'https://lusiaai-vxcarjwn.manus.space',
            position: 'bottom-right',
            theme: 'dark',
            showBadge: true,
            badgeDelay: 5000
        },

        init: function(options = {}) {
            this.config = { ...this.config, ...options };
            this.createWidget();
            this.attachEventListeners();
        },

        createWidget: function() {
            // Créer le conteneur principal
            const container = document.createElement('div');
            container.className = 'lusitanie-widget-container';
            container.id = 'lusitanie-widget';
            container.innerHTML = `
                <button class="lusitanie-chat-button" id="lusitanieChatButton" title="Discuter avec Lusitanie IA">
                    L
                    <div class="lusitanie-badge" id="lusitanieBadge">1</div>
                </button>
                <div class="lusitanie-popup" id="lusitaniePopup">
                    <div class="lusitanie-popup-header">
                        <div class="lusitanie-popup-header-title">
                            <div class="lusitanie-popup-header-title-avatar">L</div>
                            <div class="lusitanie-popup-header-title-text">
                                <h3>Lusitanie IA</h3>
                                <p>Assistante IA Portugal</p>
                            </div>
                        </div>
                        <button class="lusitanie-close-button" id="lusitanieCloseButton">✕</button>
                    </div>
                    <div class="lusitanie-popup-content">
                        <iframe 
                            class="lusitanie-popup-iframe"
                            src="${this.config.appUrl}"
                            title="Lusitanie IA Chat"
                            allow="microphone; camera"
                        ></iframe>
                    </div>
                </div>
            `;

            // Ajouter les styles
            this.injectStyles();

            // Ajouter au DOM
            document.body.appendChild(container);
        },

        injectStyles: function() {
            const style = document.createElement('style');
            style.textContent = `
                .lusitanie-widget-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                }

                .lusitanie-chat-button {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #1A3A5C 0%, #2B5EA7 100%);
                    border: 3px solid #C9A84C;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(26, 58, 92, 0.3);
                    transition: all 0.3s ease;
                    font-size: 28px;
                    font-weight: bold;
                    color: #C9A84C;
                    position: relative;
                }

                .lusitanie-chat-button:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 16px rgba(26, 58, 92, 0.4);
                }

                .lusitanie-chat-button:active {
                    transform: scale(0.95);
                }

                .lusitanie-badge {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    width: 24px;
                    height: 24px;
                    background-color: #e74c3c;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    display: none;
                }

                .lusitanie-badge.show {
                    display: flex;
                }

                .lusitanie-popup {
                    position: fixed;
                    bottom: 90px;
                    right: 20px;
                    width: 400px;
                    height: 600px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
                    display: none;
                    flex-direction: column;
                    opacity: 0;
                    transform: translateY(20px);
                    transition: all 0.3s ease;
                    z-index: 9998;
                }

                .lusitanie-popup.show {
                    display: flex;
                    opacity: 1;
                    transform: translateY(0);
                }

                .lusitanie-popup-header {
                    background: linear-gradient(135deg, #1A3A5C 0%, #2B5EA7 100%);
                    color: white;
                    padding: 16px;
                    border-radius: 12px 12px 0 0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }

                .lusitanie-popup-header-title {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .lusitanie-popup-header-title-avatar {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    background: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: #1A3A5C;
                    font-size: 18px;
                }

                .lusitanie-popup-header-title-text h3 {
                    margin: 0;
                    font-size: 14px;
                    font-weight: 600;
                }

                .lusitanie-popup-header-title-text p {
                    margin: 0;
                    font-size: 12px;
                    opacity: 0.9;
                }

                .lusitanie-close-button {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: opacity 0.2s;
                }

                .lusitanie-close-button:hover {
                    opacity: 0.8;
                }

                .lusitanie-popup-content {
                    flex: 1;
                    overflow: hidden;
                    border-radius: 0 0 12px 12px;
                }

                .lusitanie-popup-iframe {
                    width: 100%;
                    height: 100%;
                    border: none;
                    border-radius: 0 0 12px 12px;
                }

                @media (max-width: 480px) {
                    .lusitanie-popup {
                        width: calc(100vw - 20px);
                        height: calc(100vh - 100px);
                        bottom: 70px;
                        right: 10px;
                    }

                    .lusitanie-chat-button {
                        width: 56px;
                        height: 56px;
                    }
                }
            `;
            document.head.appendChild(style);
        },

        attachEventListeners: function() {
            const chatButton = document.getElementById('lusitanieChatButton');
            const popup = document.getElementById('lusitaniePopup');
            const closeButton = document.getElementById('lusitanieCloseButton');
            const badge = document.getElementById('lusitanieBadge');

            // Ouvrir la popup
            chatButton.addEventListener('click', () => {
                popup.classList.toggle('show');
                badge.classList.remove('show');
            });

            // Fermer la popup
            closeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                popup.classList.remove('show');
            });

            // Fermer en cliquant en dehors
            document.addEventListener('click', (e) => {
                if (!e.target.closest('#lusitanie-widget')) {
                    popup.classList.remove('show');
                }
            });

            // Afficher le badge après un délai
            if (this.config.showBadge) {
                setTimeout(() => {
                    if (!popup.classList.contains('show')) {
                        badge.classList.add('show');
                    }
                }, this.config.badgeDelay);
            }
        }
    };

    // Exposer globalement
    window.LusitanieWidget = LusitanieWidget;

    // Auto-initialiser si demandé
    if (document.currentScript && document.currentScript.dataset.auto === 'true') {
        LusitanieWidget.init();
    }
})();
