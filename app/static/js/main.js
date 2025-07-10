// Gestion de la langue
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les éléments du sélecteur de langue
    const langSelector = document.getElementById('language-selector');
    const langFr = document.getElementById('lang-fr');
    const langTr = document.getElementById('lang-tr');
    
    if (langSelector && langFr && langTr) {
        // Récupérer la langue stockée ou utiliser le français par défaut
        const currentLang = localStorage.getItem('preferredLanguage') || 'fr';
        
        // Mettre à jour l'affichage du sélecteur
        document.getElementById('current-lang').textContent = currentLang.toUpperCase();
        
        // Ajouter les événements de clic
        langFr.addEventListener('click', function(e) {
            e.preventDefault();
            setLanguage('fr');
        });
        
        langTr.addEventListener('click', function(e) {
            e.preventDefault();
            setLanguage('tr');
        });
    }
});

// Fonction pour définir la langue
function setLanguage(lang) {
    // Stocker la préférence dans localStorage
    localStorage.setItem('preferredLanguage', lang);
    
    // Mettre à jour l'affichage du sélecteur
    const currentLangElement = document.getElementById('current-lang');
    if (currentLangElement) {
        currentLangElement.textContent = lang.toUpperCase();
    }
    
    // Recharger la page avec le paramètre de langue
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
} 