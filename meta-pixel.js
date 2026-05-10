(function () {
    const PIXEL_ID = '2846140112392262';
    const TRIAL_SUCCESS_KEY = 'axcent_trial_signup_success';
    const PURCHASE_PENDING_KEY = 'axcent_purchase_pending';
    const REGISTRATION_SUCCESS_KEY = 'axcent_registration_success';

    function readSessionFlag(key) {
        try {
            return window.sessionStorage.getItem(key) === '1';
        } catch (error) {
            return false;
        }
    }

    function clearSessionFlags(keys) {
        try {
            keys.forEach(key => window.sessionStorage.removeItem(key));
        } catch (error) {
            // Storage can be unavailable in strict privacy modes.
        }
    }

    function currentPage() {
        return window.location.pathname
            .replace(/\/$/, '')
            .replace(/\.html$/, '')
            .split('/')
            .pop() || 'index';
    }

    if (!window.fbq) {
        !function (f, b, e, v, n, t, s) {
            n = f.fbq = function () {
                n.callMethod ?
                    n.callMethod.apply(n, arguments) : n.queue.push(arguments);
            };
            if (!f._fbq) f._fbq = n;
            n.push = n;
            n.loaded = true;
            n.version = '2.0';
            n.queue = [];
            t = b.createElement(e);
            t.async = true;
            t.src = v;
            s = b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t, s);
        }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    }

    if (!window.__axcentMetaPixelInitialized) {
        window.fbq('init', PIXEL_ID);
        window.__axcentMetaPixelInitialized = true;
    }

    if (!window.__axcentMetaPageViewFired) {
        window.fbq('track', 'PageView');
        window.__axcentMetaPageViewFired = true;
        console.log('Meta PageView fired');
    }

    const page = currentPage();

    if (page === 'thank-you-trial' && readSessionFlag(TRIAL_SUCCESS_KEY) && !window.__axcentMetaLeadFired) {
        window.fbq('track', 'Lead');
        window.__axcentMetaLeadFired = true;
        clearSessionFlags([TRIAL_SUCCESS_KEY]);
        console.log('Meta Lead fired');
    }

    if (page === 'thank-you' && readSessionFlag(PURCHASE_PENDING_KEY) && !window.__axcentMetaPurchaseFired) {
        window.fbq('track', 'Purchase');
        window.__axcentMetaPurchaseFired = true;
        clearSessionFlags([PURCHASE_PENDING_KEY, REGISTRATION_SUCCESS_KEY]);
        console.log('Meta Purchase fired');
    }
}());
