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
});
