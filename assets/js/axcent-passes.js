// Single source of truth for pass packages, Stripe Payment Links, and the
// current class schedule. Used by registration.html, de/registration.html,
// portal.html and de/portal.html — change prices/links/classes HERE only.
window.AXCENT_PASSES = {
    stripeLinks: {
        "10-Class Flexible Package": {
            student: "https://buy.stripe.com/aFafZj9Z55TPfoHbkKfnO0l",
            regular: "https://buy.stripe.com/5kQeVfefleql3FZdsSfnO0k"
        },
        "4 Classes/Week (8 Weeks)": {
            student: "https://buy.stripe.com/dRmdRbdbh4PLccv74ufnO07",
            regular: "https://buy.stripe.com/00w14p9Z59610tN1KafnO06"
        },
        "3 Classes/Week (8 Weeks)": {
            student: "https://buy.stripe.com/aFabJ37QXgyt90j60qfnO05",
            regular: "https://buy.stripe.com/cNiaEZ8V13LH90j74ufnO04"
        },
        "2 Classes/Week (8 Weeks)": {
            student: "https://buy.stripe.com/aFaeVf4ELeqla4n3SifnO03",
            regular: "https://buy.stripe.com/eVqeVf9Z581X1xR60qfnO02"
        },
        "1 Course (8 Weeks)": {
            student: "https://buy.stripe.com/cNidRb9Z56XTccv0G6fnO01",
            regular: "https://buy.stripe.com/eVq28tb395TP5O7agGfnO00"
        }
    },

    // durationDays: added to the start date for the pass end date
    // (8 weeks minus 1 day = 55; the flexible pass is valid 1 year).
    packages: [
        { value: "1 Course (8 Weeks)", en: "1 Course", de: "1 Kurs", regular: "210 CHF", student: "175 CHF", durationDays: 55 },
        { value: "2 Classes/Week (8 Weeks)", en: "2 Classes/Week", de: "2 Kurse/Woche", regular: "320 CHF", student: "270 CHF", durationDays: 55 },
        { value: "3 Classes/Week (8 Weeks)", en: "3 Classes/Week", de: "3 Kurse/Woche", regular: "390 CHF", student: "330 CHF", durationDays: 55 },
        { value: "4 Classes/Week (8 Weeks)", en: "All You Can Dance", de: "All You Can Dance", regular: "450 CHF", student: "380 CHF", durationDays: 55 },
        { value: "10-Class Flexible Package", en: "10-Class Flexible (1 Year)", de: "10er-Abo Flexibel (1 Jahr)", regular: "290 CHF", student: "245 CHF", durationDays: 365 }
    ],

    classes: [
        { value: "Mon 19:30 Beginner 0", en: "Bachata Beginner 0", de: "Bachata Beginner 0" },
        { value: "Tue 19:30 Beginner 2", en: "Bachata Beginner 3", de: "Bachata Beginner 3" },
        { value: "Wed 19:30 Sensual Foundation", en: "Bachata Sensual Foundation", de: "Bachata Sensual Foundation" },
        { value: "Wed 20:30 Sensual Improver", en: "Bachata Sensual Improver", de: "Bachata Sensual Improver" },
        { value: "Thu 18:30 Bachata Lady Style", en: "Bachata Lady Style", de: "Bachata Lady Style" },
        { value: "Thu 19:30 Sensual Intermediate", en: "Bachata Sensual Intermediate", de: "Bachata Sensual Intermediate" },
        { value: "Thu 20:30 Sensual Intermediate/Advanced", en: "Bachata Sensual Int/Adv", de: "Bachata Sensual Int/Adv" }
    ],

    // Start dates offered: every Tue/Wed/Thu from today through the Sunday
    // two weeks out (mirrors the registration form logic).
    startDateOptions: function () {
        const options = [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const currentDay = today.getDay();
        const daysUntilMonday = currentDay === 0 ? 1 : (currentDay === 1 ? 0 : 8 - currentDay);
        const thisMonday = new Date(today);
        thisMonday.setDate(today.getDate() + daysUntilMonday);
        const endDate = new Date(thisMonday);
        endDate.setDate(thisMonday.getDate() + 13);
        const cursor = new Date(today);
        while (cursor <= endDate) {
            const d = cursor.getDay();
            if (d === 2 || d === 3 || d === 4) options.push(new Date(cursor));
            cursor.setDate(cursor.getDate() + 1);
        }
        return options;
    },

    toLocalISO: function (d) {
        return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }
};
