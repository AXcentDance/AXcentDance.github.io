console.log('AXcent Dance website initialized.');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }

    // Mobile Dropdown Toggle ("More" button)
    const dropBtns = document.querySelectorAll('.dropbtn');
    dropBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Only toggle on mobile (when nav-links is active) or check screen width
            if (window.innerWidth < 900) {
                e.preventDefault(); // Prevent default link behavior if any
                const dropdown = btn.closest('.dropdown');
                dropdown.classList.toggle('active');
            }
        });
    });

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

/* GOOGLE SHEETS FORM SUBMISSION */
document.addEventListener('DOMContentLoaded', () => {
    const trialForm = document.getElementById('trialForm');

    if (trialForm) {
        console.log('Trial form found, attaching listener');
        trialForm.addEventListener('submit', e => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitTrialBtn');
            const originalBtnContent = submitBtn.innerHTML;

            // 1. Show Loading State
            submitBtn.innerHTML = '<span>Submitting...</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.style.cursor = 'not-allowed';

            // 2. Gather Data
            const rawFormData = new FormData(trialForm);
            const data = {
                firstname: rawFormData.get('firstname'),
                lastname: rawFormData.get('lastname'),
                phone: rawFormData.get('phone'),
                email: rawFormData.get('email'),
                selected_class: rawFormData.get('class-select') // Users script expects 'selected_class'
            };

            // 3. Send to Google Script
            // IMPORTANT: PASTE YOUR WEB APP URL BELOW
            const scriptURL = 'https://script.google.com/macros/s/AKfycbwPqLutAq-xa9OkSiT-rLm72DJCdQ2Xw10Yp4DvHexTq42HxCKJyJr8mJmZ0RuZSc7A5A/exec';

            if (scriptURL === 'REPLACE_ME_WITH_YOUR_WEB_APP_URL') {
                alert('Configuration missing: Please paste your Google Web App URL in script.js (Line ~206)');
                submitBtn.innerHTML = originalBtnContent;
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                submitBtn.style.cursor = 'pointer';
                return;
            }

            fetch(scriptURL, {
                method: 'POST',
                body: JSON.stringify(data),
                // transformRequest: [function (data, headers) { delete headers.common['Content-Type']; return data; }] // Start with simple fetch first
                mode: 'no-cors' // Often needed for Google Scripts to avoid CORS errors if not handling OPTIONS
            })
                // NOTE: With mode 'no-cors', we receive an opaque response. We cannot read the status or JSON.
                // We assume success if it doesn't throw.
                .then(() => {
                    // 4. Success -> Redirect to existing Thank You page
                    window.location.href = 'thankyou.html';
                })
                .catch(error => {
                    console.error('Error!', error.message);
                    alert('Something went wrong submitting the form. Please try again or contact us directly at info@axcentdance.com.');

                    // Reset button state
                    submitBtn.innerHTML = originalBtnContent;
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.style.cursor = 'pointer';
                });
        });
    } else {
        console.error('Trial form not found in DOM');
    }

    // Contact Form Logic
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        console.log('Contact form found, attaching listener');
        contactForm.addEventListener('submit', e => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitContactBtn');
            const originalBtnContent = submitBtn.innerHTML;

            // 1. Show Loading State
            submitBtn.innerHTML = '<span>Sending...</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.style.cursor = 'not-allowed';

            // 2. Gather Data
            const rawFormData = new FormData(contactForm);
            const data = {
                name: rawFormData.get('name'),
                email: rawFormData.get('email'),
                phone: rawFormData.get('phone'),
                message: rawFormData.get('message')
            };

            // 3. Send to Google Script AND FormSubmit (Parallel)
            const googleScriptURL = 'https://script.google.com/macros/s/AKfycbxOYwPUSX0twewRAHIA-7k4Cyds8oH9i6wUuFDLcTM68ZyWK9MO1RF2wQ7rYUUBDbgrZw/exec';
            const formSubmitEmail = 'slamitza@gmail.com'; // Using FormSubmit for reliable emails
            const formSubmitURL = `https://formsubmit.co/ajax/${formSubmitEmail}`;

            // Prepare FormSubmit Data (Needs hidden fields for configuration)
            const formSubmitData = {
                _subject: `New Contact from ${data.name}`,
                _template: 'table', // or 'box'
                _captcha: 'false',  // Disable captcha if you want instant submission
                name: data.name,
                email: data.email,
                phone: data.phone,
                message: data.message
            };

            const p1 = fetch(googleScriptURL, {
                method: 'POST',
                body: JSON.stringify(data),
                mode: 'no-cors'
            });

            const p2 = fetch(formSubmitURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formSubmitData)
            });

            Promise.allSettled([p1, p2])
                .then((results) => {
                    // We redirect regardless because no-cors acts opaque
                    window.location.href = 'thankyou-contact.html';
                })
                .catch(error => {
                    console.error('Error!', error.message);
                    alert('Something went wrong sending your message. Please try again later.');

                    // Reset button state
                    submitBtn.innerHTML = originalBtnContent;
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.style.cursor = 'pointer';
                });
        });
    }

    // PERFORMANCE OPTIMIZATION
    // Strategy: Use Speculation Rules (Prerender) if supported (Chrome/Edge).
    // Fallback: Use Link Prefetching for Safri/Firefox.

    if (HTMLScriptElement.supports && HTMLScriptElement.supports('speculationrules')) {
        console.log('Browser supports Speculation Rules. Enabling Prerendering.');
        const specScript = document.createElement('script');
        specScript.type = 'speculationrules';
        const specRules = {
            prerender: [{
                source: "document",
                where: {
                    and: [
                        { href_matches: "/*" }, // Match all internal links
                        { not: { href_matches: "*#*" } } // Exclude anchors
                    ]
                },
                eagerness: "moderate" // Prerender on hover (>200ms)
            }]
        };
        specScript.textContent = JSON.stringify(specRules);
        document.body.appendChild(specScript);
    } else {
        // Fallback: Link Prefetching on Hover
        console.log('Browser does not support Speculation Rules. Using Link Prefetch fallback.');
        const prefetchLink = (url) => {
            if (!url || url.includes('#') || url.startsWith('mailto:') || url.startsWith('tel:')) return;

            // check if already prefetched
            if (document.head.querySelector(`link[href="${url}"]`)) return;

            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
            // console.log(`Prefetching: ${url}`);
        };

        const links = document.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                const href = link.getAttribute('href');
                if (href) prefetchLink(href);
            });
        });
    }
});

