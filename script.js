console.log('AXcent Dance website initialized.');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.textContent = navLinks.classList.contains('active') ? 'CLOSE' : 'MENU';
        });
    }

    // Navbar Glassmorphism Scroll Effect
    const header = document.querySelector('.main-header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.reveal');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    });

    revealElements.forEach(element => {
        revealObserver.observe(element);
    });

    // Values Section Interactivity
    document.addEventListener('click', (e) => {
        const valueItem = e.target.closest('.value-item');

        if (valueItem) {
            console.log('Clicked value item:', valueItem);

            // Check if this item is already active
            const isActive = valueItem.classList.contains('active');

            // Close all items
            document.querySelectorAll('.value-item').forEach(item => {
                item.classList.remove('active');
            });

            // If it wasn't active before, open it now
            if (!isActive) {
                valueItem.classList.add('active');
                console.log('Added active class to:', valueItem);
            }
        }
    });
    // Active Link Highlighting
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-links a');

    navItems.forEach(link => {
        const linkPath = link.getAttribute('href');
        // Handle root path and index.html
        if ((currentPath === '/' || currentPath.endsWith('index.html')) && (linkPath === 'index.html' || linkPath === './')) {
            // Don't highlight home on other pages if logo is clicked, but usually home link is explicit.
            // Actually, let's just check if the href matches the end of the path
            // But for home, we might want to be careful.
            // Let's stick to simple matching for now.
        }

        if (currentPath.endsWith(linkPath) && linkPath !== '#') {
            link.classList.add('active');
        } else if (linkPath !== 'index.html' && currentPath.includes(linkPath)) {
            // Handle sub-pages if necessary, or exact matches
            link.classList.add('active');
        }
    });

    // Better Active Link Logic
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage) {
            link.classList.add('active');
        }
    });
});
