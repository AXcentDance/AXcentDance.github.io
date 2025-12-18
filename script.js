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
    const cleanPath = currentPath.length > 1 && currentPath.endsWith('/') ? currentPath.slice(0, -1) : currentPath;
    let currentPage = cleanPath.split('/').pop() || 'index.html';

    // Normalize currentPage: remove .html extension if present
    if (currentPage.endsWith('.html')) {
        currentPage = currentPage.slice(0, -5);
    }
    // Handle root/index specifically
    if (currentPage === 'index') currentPage = '';

    document.querySelectorAll('.nav-links a').forEach(link => {
        const linkHref = link.getAttribute('href');
        if (!linkHref) return;

        // Normalize link href
        let cleanLink = linkHref.replace('./', '');
        if (cleanLink.endsWith('.html')) cleanLink = cleanLink.slice(0, -5);
        if (cleanLink === 'index' || cleanLink === '') cleanLink = '';

        // Check for match
        const isActive = cleanLink === currentPage;

        if (isActive) {
            link.classList.add('active');
        }
    });
});

// Blog Filtering Logic
const filterBtns = document.querySelectorAll('.filter-btn');
const blogCards = document.querySelectorAll('.modern-card'); // Ensure this matches your card class

if (filterBtns.length > 0 && blogCards.length > 0) {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 1. Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // 2. Add active class to clicked button
            btn.classList.add('active');

            // 3. Get filter value
            const filterValue = btn.getAttribute('data-filter');

            // 4. Filter cards
            blogCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');

                if (filterValue === 'all' || filterValue === cardCategory) {
                    card.style.display = 'flex'; // Or 'block' depending on your card layout
                    // Optional: Add a fade-in animation/class here if desired
                    setTimeout(() => card.style.opacity = '1', 10);
                } else {
                    card.style.display = 'none';
                    card.style.opacity = '0';
                }
            });
        });
    });
}

/* MOBILE BOTTOM NAV INJECTION */
/* MOBILE BOTTOM NAV REPLACEMENT */
document.addEventListener('DOMContentLoaded', () => {
    // Smart Sticky Header Logic
    let lastScrollY = window.scrollY;
    const mainHeader = document.querySelector('.main-header');

    if (mainHeader) {
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;

            // Only apply effect if we've scrolled down a bit
            if (currentScrollY > 100) {
                if (currentScrollY > lastScrollY) {
                    // Scrolling DOWN -> Hide Header
                    mainHeader.classList.add('header-hidden');
                } else {
                    // Scrolling UP -> Show Header
                    mainHeader.classList.remove('header-hidden');
                }
            } else {
                // At the top -> Show Header
                mainHeader.classList.remove('header-hidden');
            }

            lastScrollY = currentScrollY;
        });
    }

    // Validating cleanup of old nav injection
    if (document.body.style.paddingBottom === '60px') {
        document.body.style.paddingBottom = '';
    }

    // Review Slider Scroll Logic
    const scrollIndicator = document.querySelector('.scroll-indicator');
    const reviewsGrid = document.querySelector('.reviews-grid');

    if (scrollIndicator && reviewsGrid) {
        scrollIndicator.addEventListener('click', () => {
            reviewsGrid.scrollBy({
                left: 300,
                behavior: 'smooth'
            });
        });
    }
});
