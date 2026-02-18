// Navigation and routing functionality

// Handle internal links (convert markdown links to wiki links if needed)
function setupInternalLinks() {
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        
        // Handle internal wiki links
        if (href && href.startsWith('/') && !href.startsWith('//')) {
            // Already a proper link, let browser handle it
            return;
        }
        
        // Handle markdown-style links that might need conversion
        // This is handled by the markdown parser, so we mainly just ensure smooth navigation
    });
}

// Smooth scroll for anchor links
function setupAnchorLinks() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Highlight current page in navigation
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath || 
            (currentPath === '/' && linkPath === '/index.html') ||
            (currentPath.startsWith('/search') && linkPath === '/search.html')) {
            link.classList.add('active');
        }
    });
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', () => {
    setupInternalLinks();
    setupAnchorLinks();
    highlightCurrentPage();
});

// Add fade-in animation for content
document.addEventListener('DOMContentLoaded', () => {
    const content = document.querySelector('.main-content');
    if (content) {
        content.style.opacity = '0';
        content.style.transition = 'opacity 0.3s ease-in';
        
        setTimeout(() => {
            content.style.opacity = '1';
        }, 50);
    }
});
