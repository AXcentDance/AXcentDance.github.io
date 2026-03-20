(function () {
  const isDe = window.location.pathname.includes('/de/');
  const baseUrl = "https://axcentdance.com";

  const globalSchema = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": `${baseUrl}/#website`,
        "url": baseUrl + "/",
        "name": "AXcent Dance",
        "description": isDe ? "Premium Bachata Tanzschule in Zürich" : "Premium Bachata Dance School in Zurich",
        "publisher": { "@id": `${baseUrl}/#organization` },
        "inLanguage": ["en", "de"]
      },
      {
        "@id": `${baseUrl}/#organization`,
        "@type": ["LocalBusiness", "DanceSchool"],
        "name": "AXcent Dance",
        "url": baseUrl + "/",
        "logo": `${baseUrl}/assets/images/logo.webp`,
        "image": `${baseUrl}/assets/images/hero_new.webp`,
        "description": isDe ?
          "Die Bachata-Tanzschule in Zürich Altstetten. Wir bieten Bachata Sensual, Dominican Bachata und Salsa Kurse für alle Niveaus an." :
          "AXcent Dance is a Bachata dance school in Zurich Altstetten offering Bachata Sensual, Dominican Bachata, Salsa, and Latin dance classes for all levels.",
        "telephone": "+41799668481",
        "email": "info@axcentdance.com",
        "hasMap": "https://www.google.com/maps?cid=15680757943659417558",
        "sameAs": [
          "https://www.instagram.com/axcent_dance/",
          "https://www.youtube.com/channel/UCfdgCx1Iot8XwdWJN6AJb-g",
          "https://www.facebook.com/profile.php?id=61579290375546",
          "https://www.google.com/maps?cid=15680757943659417558"
        ],
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "Hermetschloostrasse 73",
          "addressLocality": isDe ? "Zürich" : "Zurich",
          "addressRegion": "ZH",
          "postalCode": "8048",
          "addressCountry": "CH"
        },
        "geo": {
          "@type": "GeoCoordinates",
          "latitude": 47.3941999,
          "longitude": 8.4745859
        },
        "foundingDate": "2025",
        "paymentAccepted": isDe ? ["Bargeld", "Visa", "Mastercard", "Twint"] : ["Cash", "Visa", "Mastercard", "Twint"],
        "areaServed": { "@type": "Place", "name": isDe ? "Zürich, Schweiz" : "Zurich, Switzerland" },
        "priceRange": isDe ? "CHF 75+ / Monat" : "CHF 75+ / month",
        "openingHoursSpecification": [
          {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Tuesday", "Wednesday", "Thursday"],
            "opens": "18:00",
            "closes": "22:00"
          },
          {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": "Sunday",
            "opens": "13:00",
            "closes": "17:00"
          },
          {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "11:00",
            "closes": "22:00"
          }
        ]
      },
      {
        "@id": `${baseUrl}/#person1`,
        "@type": "Person",
        "name": "Alessandro",
        "jobTitle": isDe ? "Mitbegründer" : "Co-Founder",
        "sameAs": ["https://www.instagram.com/aleyxidan/"]
      },
      {
        "@id": `${baseUrl}/#person2`,
        "@type": "Person",
        "name": "Xidan",
        "jobTitle": isDe ? "Mitbegründerin" : "Co-Founder",
        "sameAs": ["https://www.instagram.com/aleyxidan/"]
      }
    ]
  };


  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.text = JSON.stringify(globalSchema);
  document.head.appendChild(script);
})();
