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
document.addEventListener('DOMContentLoaded', () => {
    if (window.innerWidth < 768) {
        const bottomNavHTML = `
        <nav class="bottom-nav">
            <a href="index.html" class="bottom-nav-item ${window.location.pathname.endsWith('index.html') || window.location.pathname === '/' ? 'active' : ''}">
                <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                Home
            </a>
            <a href="schedule.html" class="bottom-nav-item ${window.location.pathname.includes('schedule') ? 'active' : ''}">
                 <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                Schedule
            </a>
            <a href="registration.html" class="bottom-nav-item ${window.location.pathname.includes('registration') ? 'active' : ''}">
                <svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                Registration
            </a>
            <a href="contact.html" class="bottom-nav-item ${window.location.pathname.includes('contact') ? 'active' : ''}">
                <svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                Contact
            </a>
        </nav>
        `;
        document.body.insertAdjacentHTML('beforeend', bottomNavHTML);

        // Add padding to body to prevent content from being hidden behind nav
        document.body.style.paddingBottom = '60px';
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
