console.log('AXcent Dance website initialized.');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    const gsap = window.gsap;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const animateHomeHeroIntro = () => {
        if (!gsap || prefersReducedMotion || !document.querySelector('.home-hero')) return;
        const panelIntroTargets = gsap.utils.toArray([
            '.home-hero__brand',
            '.home-hero__headline',
            '.home-hero__intro',
            '.home-hero__meta span'
        ].join(', '));
        const selector = document.querySelector('.home-hero__selector');
        const selectorTargets = selector
            ? Array.from(selector.children).sort((first, second) => first.getBoundingClientRect().top - second.getBoundingClientRect().top)
            : [];
        const actionTargets = gsap.utils.toArray('.home-hero__actions .btn-hero, .home-hero__actions .home-hero__assurance li');
        const stage = document.querySelector('.home-hero__stage');
        const motionTargets = [stage, ...panelIntroTargets, ...selectorTargets, ...actionTargets].filter(Boolean);
        const clearIntroStyles = () => {
            gsap.set(motionTargets, { clearProps: 'opacity,visibility,transform' });
        };

        gsap.timeline({
            defaults: { ease: 'power3.out' },
            onComplete: clearIntroStyles
        })
            .from(stage, {
                opacity: 0,
                y: 30,
                scale: 0.985,
                duration: 0.62
            })
            .from(actionTargets, {
                opacity: 0,
                y: 18,
                duration: 0.38,
                stagger: 0.035
            }, '-=0.36')
            .from(panelIntroTargets, {
                opacity: 0,
                y: 14,
                duration: 0.36,
                stagger: 0.025
            }, '-=0.44')
            .from(selectorTargets, {
                opacity: 0,
                y: 16,
                duration: 0.36,
                stagger: 0.045
            }, '-=0.22');

        window.setTimeout(clearIntroStyles, 1700);
    };

    // Homepage loading reveal
    const pageLoader = document.querySelector('.page-loader');
    let heroIntroPlayed = false;
    const markHeroIntroPlayed = () => {
        if (heroIntroPlayed) return;
        heroIntroPlayed = true;
        animateHomeHeroIntro();
    };

    if (pageLoader) {
        if (gsap && !prefersReducedMotion) {
            gsap.fromTo('.page-loader__mark', {
                autoAlpha: 0,
                y: 18,
                scale: 0.96
            }, {
                autoAlpha: 1,
                y: 0,
                scale: 1,
                duration: 0.78,
                ease: 'power3.out'
            });
            gsap.fromTo('.page-loader__line', {
                autoAlpha: 0,
                scaleX: 0.45
            }, {
                autoAlpha: 1,
                scaleX: 1,
                duration: 0.82,
                ease: 'power3.out',
                delay: 0.12
            });
        }

        let loaderDone = false;
        const markPageLoaded = () => {
            if (loaderDone) return;
            loaderDone = true;

            if (gsap && !prefersReducedMotion) {
                gsap.to(pageLoader, {
                    autoAlpha: 0,
                    duration: 0.34,
                    ease: 'power2.out',
                    onStart: () => {
                        document.body.classList.add('page-loaded');
                        markHeroIntroPlayed();
                    },
                    onComplete: () => {
                        pageLoader.style.display = 'none';
                    }
                });
            } else {
                document.body.classList.add('page-loaded');
                markHeroIntroPlayed();
            }
        };

        window.addEventListener('load', () => {
            window.setTimeout(markPageLoaded, 150);
        }, { once: true });
        window.setTimeout(markPageLoaded, 1050);
    } else {
        markHeroIntroPlayed();
    }

    // Homepage hero video switcher
    const heroShowcaseVideo = document.getElementById('hero-showcase-video');
    const heroPosterFrame = document.querySelector('[data-hero-poster-frame]');
    const heroVideoChoices = document.querySelectorAll('.home-hero__choice[data-hero-video], .home-hero__choice[data-hero-poster]');

    if (heroShowcaseVideo && heroVideoChoices.length) {
        // Stage overlay (launch-note ribbon + CTA pair). Event entries in the
        // selector carry data-hero-note-* / data-hero-cta-* overrides so the
        // overlay copy always matches the footage being shown; class entries
        // fall back to the default promo captured here at load time.
        const heroStageActions = document.querySelector('.home-hero__stage .home-hero__actions');
        const heroNoteLabel = heroStageActions ? heroStageActions.querySelector('[data-hero-note-label]') : null;
        const heroNoteText = heroStageActions ? heroStageActions.querySelector('[data-hero-note-text]') : null;
        const heroNoteText2 = heroStageActions ? heroStageActions.querySelector('[data-hero-note-text2]') : null;
        const heroCtaPrimary = heroStageActions ? heroStageActions.querySelector('.btn-hero-primary') : null;
        const heroCtaSecondary = heroStageActions ? heroStageActions.querySelector('.btn-hero-secondary') : null;
        const heroCtaSecondaryLabel = heroCtaSecondary ? heroCtaSecondary.querySelector('.btn-hero-content') : null;
        const heroOverlayReady = Boolean(heroNoteLabel && heroNoteText && heroCtaPrimary && heroCtaSecondaryLabel);
        const heroOverlayDefaults = heroOverlayReady ? {
            noteLabel: heroNoteLabel.textContent,
            noteText: heroNoteText.innerHTML, // innerHTML keeps the <code>AXcent15</code> chip
            ctaLabel: heroCtaSecondaryLabel.textContent,
            ctaHref: heroCtaSecondary.getAttribute('href')
        } : null;
        if (heroOverlayReady) {
            heroStageActions.dataset.overlayKey = 'default';
        }

        const applyHeroOverlay = (choice) => {
            if (!heroOverlayReady) return;

            const noteLabel = choice.dataset.heroNoteLabel;
            const noteText = choice.dataset.heroNoteText;
            const ctaLabel = choice.dataset.heroCtaLabel;
            const ctaHref = choice.dataset.heroCtaHref;
            const isEventOverlay = Boolean(ctaLabel && ctaHref);
            const overlayKey = isEventOverlay ? ctaHref : 'default';
            if (heroStageActions.dataset.overlayKey === overlayKey) return;
            heroStageActions.dataset.overlayKey = overlayKey;

            const swapOverlayCopy = () => {
                if (isEventOverlay) {
                    heroNoteLabel.textContent = noteLabel || '';
                    heroNoteText.textContent = noteText || '';
                    // Optional second ribbon line — only event entries that
                    // declare data-hero-note-text2 reveal it.
                    if (heroNoteText2) {
                        const noteText2 = choice.dataset.heroNoteText2 || '';
                        heroNoteText2.textContent = noteText2;
                        heroNoteText2.hidden = !noteText2;
                    }
                    // The event CTA reuses the ghost (secondary) pill so the
                    // orange gradient stays reserved for the trial conversion;
                    // hiding the primary leaves one focused action in event mode.
                    heroCtaSecondaryLabel.textContent = ctaLabel;
                    heroCtaSecondary.setAttribute('href', ctaHref);
                    heroCtaPrimary.hidden = true;
                } else {
                    heroNoteLabel.textContent = heroOverlayDefaults.noteLabel;
                    heroNoteText.innerHTML = heroOverlayDefaults.noteText;
                    if (heroNoteText2) {
                        heroNoteText2.textContent = '';
                        heroNoteText2.hidden = true;
                    }
                    heroCtaSecondaryLabel.textContent = heroOverlayDefaults.ctaLabel;
                    heroCtaSecondary.setAttribute('href', heroOverlayDefaults.ctaHref);
                    heroCtaPrimary.hidden = false;
                }
            };

            // Swap synchronously — correct copy must never wait on a ticker
            // (throttled rAF in background tabs would stall an onComplete).
            // The tween only decorates the already-updated overlay.
            swapOverlayCopy();
            if (gsap && !prefersReducedMotion) {
                gsap.killTweensOf(heroStageActions);
                gsap.fromTo(heroStageActions, {
                    autoAlpha: 0.35,
                    y: 6
                }, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.34,
                    ease: 'power2.out',
                    clearProps: 'opacity,visibility,transform'
                });
            }
        };

        const playHeroVideo = () => {
            heroShowcaseVideo.muted = true;
            heroShowcaseVideo.playsInline = true;
            const playPromise = heroShowcaseVideo.play();
            if (playPromise && typeof playPromise.catch === 'function') {
                playPromise.catch(() => {});
            }
        };

        const seekHeroVideo = (startTime, onFrameReady) => {
            let notified = false;
            const notifyFrameReady = () => {
                if (notified) return;
                notified = true;
                if (typeof onFrameReady === 'function') onFrameReady();
            };

            // The stage stays faded out until a frame at the target time is
            // actually painted (seeked/loadeddata) — loadedmetadata alone can
            // still paint frame 0 or the poster. The timeout keeps the hero
            // from sticking dark if the browser never fires the media event.
            const armFrameGuard = (eventName) => {
                heroShowcaseVideo.addEventListener(eventName, notifyFrameReady, { once: true });
                window.setTimeout(notifyFrameReady, 900);
            };

            const seekWhenReady = () => {
                if (Number.isFinite(startTime) && startTime > 0) {
                    armFrameGuard('seeked');
                    try {
                        heroShowcaseVideo.currentTime = startTime;
                    } catch (error) {
                        // Some browsers block seeking until more metadata is ready.
                        notifyFrameReady();
                    }
                } else if (heroShowcaseVideo.readyState >= 2) {
                    notifyFrameReady();
                } else {
                    armFrameGuard('loadeddata');
                }
                playHeroVideo();
            };

            if (heroShowcaseVideo.readyState >= 1) {
                seekWhenReady();
            } else {
                heroShowcaseVideo.addEventListener('loadedmetadata', seekWhenReady, { once: true });
            }
        };

        const choiceMotionProperties = [
            '--choice-sheen-x',
            '--choice-sheen-opacity',
            '--choice-rail-opacity',
            '--choice-rail-scale',
            '--choice-shadow-opacity'
        ];

        const clearHeroChoiceMotion = (choiceElement) => {
            choiceMotionProperties.forEach((property) => {
                choiceElement.style.removeProperty(property);
            });
        };

        const animateHeroChoiceSelection = (choiceElement) => {
            if (!gsap || prefersReducedMotion) return;

            const choiceCopy = choiceElement.querySelector('.home-hero__choice-copy');
            const choiceText = choiceElement.querySelectorAll('.home-hero__choice-title, .home-hero__choice-note');

            gsap.killTweensOf(choiceElement);
            if (choiceCopy) gsap.killTweensOf(choiceCopy);
            if (choiceText.length) gsap.killTweensOf(choiceText);
            clearHeroChoiceMotion(choiceElement);

            gsap.timeline({
                defaults: { ease: 'power3.out' },
                onComplete: () => clearHeroChoiceMotion(choiceElement)
            })
                .set(choiceElement, {
                    '--choice-sheen-x': '-118%',
                    '--choice-sheen-opacity': 0,
                    '--choice-rail-opacity': 0.12,
                    '--choice-rail-scale': 0.46,
                    '--choice-shadow-opacity': 0.26
                })
                .to(choiceElement, {
                    '--choice-sheen-x': '116%',
                    '--choice-sheen-opacity': 0.42,
                    '--choice-rail-opacity': 0.92,
                    '--choice-rail-scale': 1,
                    '--choice-shadow-opacity': 0.2,
                    duration: 0.58
                })
                .to(choiceElement, {
                    '--choice-sheen-opacity': 0,
                    '--choice-shadow-opacity': 0.15,
                    duration: 0.24,
                    ease: 'sine.out'
                }, '-=0.16');

            if (choiceCopy) {
                gsap.fromTo(choiceCopy, {
                    x: 8
                }, {
                    x: 0,
                    duration: 0.46,
                    ease: 'expo.out',
                    overwrite: true,
                    clearProps: 'transform'
                });
            }

            if (choiceText.length) {
                gsap.fromTo(choiceText, {
                    autoAlpha: 0.62,
                    y: 3
                }, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.38,
                    stagger: 0.035,
                    ease: 'power2.out',
                    overwrite: true,
                    clearProps: 'opacity,visibility,transform'
                });
            }
        };

        // The poster is only for the initial paint before autoplay begins.
        // Once footage has played, a lingering poster attribute repaints
        // during every source swap (the browser resets its show-poster flag
        // on load()), flashing an unrelated image between videos.
        heroShowcaseVideo.addEventListener('playing', () => {
            heroShowcaseVideo.removeAttribute('poster');
        }, { once: true });

        // Rapid back-and-forth clicks leave stale once-listeners
        // (loadedmetadata/seeked) from the previous switch; the token lets
        // late callbacks detect they lost and skip revealing the stage.
        let heroSwitchToken = 0;

        heroVideoChoices.forEach((choice) => {
            choice.addEventListener('click', () => {
                const switchToken = ++heroSwitchToken;
                heroVideoChoices.forEach((button) => {
                    if (gsap) {
                        gsap.killTweensOf(button);
                        clearHeroChoiceMotion(button);
                    }
                    const isActive = button === choice;
                    button.classList.toggle('is-active', isActive);
                    button.setAttribute('aria-pressed', String(isActive));
                });

                if (gsap && !prefersReducedMotion) {
                    animateHeroChoiceSelection(choice);
                }

                applyHeroOverlay(choice);

                // Poster-only choices (no matching footage yet, e.g. an event
                // without a dedicated clip) show a static image instead of
                // reusing another entry's video, which would be a fake duplicate.
                const posterSource = choice.dataset.heroPoster;
                if (posterSource) {
                    heroShowcaseVideo.pause();
                    if (heroPosterFrame) {
                        heroPosterFrame.src = posterSource;
                        heroPosterFrame.classList.add('is-active');
                    }
                    return;
                }

                if (heroPosterFrame) {
                    heroPosterFrame.classList.remove('is-active');
                }

                const hlsSource = choice.dataset.heroHls;
                const webmSource = choice.dataset.heroWebm;
                const mp4Source = choice.dataset.heroVideo;
                // HLS (3-second segmented streaming) when hls-video.js upgraded
                // this video; progressive webm/mp4 otherwise.
                const useHls = Boolean(hlsSource && window.AXHls && heroShowcaseVideo.dataset.hlsActive);
                const nextSource = useHls
                    ? hlsSource
                    : (webmSource && heroShowcaseVideo.canPlayType('video/webm') ? webmSource : mp4Source);
                const startTime = Number(choice.dataset.heroStart || 0);

                // Fade fully out: at any visible opacity the swap artifacts
                // (poster repaint, pre-seek frame 0) would show through.
                heroShowcaseVideo.classList.add('is-switching');
                if (gsap && !prefersReducedMotion) {
                    gsap.killTweensOf(heroShowcaseVideo);
                    gsap.to(heroShowcaseVideo, {
                        opacity: 0,
                        duration: 0.16,
                        ease: 'power1.out'
                    });
                }

                const revealStage = () => {
                    if (switchToken !== heroSwitchToken) return;
                    if (gsap && !prefersReducedMotion) {
                        gsap.to(heroShowcaseVideo, {
                            opacity: 1,
                            duration: 0.3,
                            ease: 'power2.out',
                            onComplete: () => {
                                heroShowcaseVideo.classList.remove('is-switching');
                                gsap.set(heroShowcaseVideo, { clearProps: 'opacity' });
                            }
                        });
                    } else {
                        heroShowcaseVideo.classList.remove('is-switching');
                    }
                };

                const finishSwitch = () => {
                    if (switchToken !== heroSwitchToken) return;
                    seekHeroVideo(startTime, revealStage);
                };

                if (heroShowcaseVideo.dataset.currentSource !== nextSource) {
                    heroShowcaseVideo.dataset.currentSource = nextSource;
                    heroShowcaseVideo.addEventListener('loadedmetadata', finishSwitch, { once: true });
                    if (useHls) {
                        window.AXHls.attach(heroShowcaseVideo, nextSource, { autoStart: true });
                    } else {
                        if (window.AXHls) {
                            window.AXHls.detach(heroShowcaseVideo);
                        }
                        heroShowcaseVideo.setAttribute('src', nextSource);
                        heroShowcaseVideo.load();
                    }
                } else {
                    finishSwitch();
                }
            });
        });

        // When hls-video.js manages this video (data-hls), it starts playback
        // itself after attaching the stream; avoid racing it with the mp4 src.
        if (!heroShowcaseVideo.dataset.hls) {
            playHeroVideo();
        }
    }

    // Free-trial CTA motion is handled in CSS so the border can orbit without tracking the pointer.

    const enhanceBeginnerGateway = () => {
        const gateway = document.querySelector('[data-beginner-gateway]');
        if (!gateway || !document.body.classList.contains('home-page')) return;

        const guideCards = Array.from(gateway.querySelectorAll('.guide-card'));
        const photoCards = guideCards.filter(card => card.classList.contains('beginner-course-card--photo'));
        const photoMotionActiveClass = 'beginner-course-card--motion-active';
        const startBridge = gateway.querySelector('[data-beginner-start-bridge]');
        const footsteps = Array.from(gateway.querySelectorAll('[data-guides-steps] .guides-steps__print'));
        const introMotionTargets = [
            gateway.querySelector('.guides-section__story'),
            startBridge,
            gateway.querySelector('.guides-confidence')
        ].filter(Boolean);
        const standardCardTargets = guideCards.filter(card => !card.classList.contains('beginner-course-card--photo'));
        const riseMotionTargets = [
            ...introMotionTargets,
            ...standardCardTargets
        ].filter(Boolean);
        const motionTargets = [
            ...riseMotionTargets,
            ...photoCards
        ].filter(Boolean);

        const clearPhotoCardEntrance = (card) => {
            gsap.set(card, { clearProps: 'opacity,visibility,transform,transformOrigin,transformPerspective' });
            card.style.removeProperty('--beginner-card-reveal');
            card.style.removeProperty('--beginner-card-sheen-x');
        };

        const playGatewayReveal = () => {
            if (!gsap || prefersReducedMotion || !motionTargets.length) return;

            const revealTimeline = gsap.timeline({
                defaults: { ease: 'power3.out' },
                onComplete: () => {
                    riseMotionTargets.forEach((target) => {
                        gsap.set(target, { clearProps: 'opacity,visibility,transform' });
                    });
                    photoCards.forEach(clearPhotoCardEntrance);
                }
            });

            if (riseMotionTargets.length) {
                revealTimeline.to(riseMotionTargets, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.56,
                    stagger: 0.06
                });
            }

            if (photoCards.length) {
                revealTimeline.to(photoCards, {
                    autoAlpha: 1,
                    x: 0,
                    rotateY: 0,
                    scale: 1,
                    '--beginner-card-reveal': 1,
                    '--beginner-card-sheen-x': '118%',
                    duration: 0.84,
                    ease: 'expo.out',
                    stagger: 0.09
                }, riseMotionTargets.length ? '-=0.18' : 0)
                    .to(photoCards, {
                        '--beginner-card-reveal': 0,
                        duration: 0.42,
                        ease: 'sine.out'
                    }, '-=0.12');
            }

            if (footsteps.length) {
                revealTimeline.to(footsteps, {
                    autoAlpha: 1,
                    y: 0,
                    scale: 1,
                    duration: 0.46,
                    ease: 'back.out(1.7)',
                    stagger: 0.09
                }, riseMotionTargets.length ? '-=0.32' : 0);
            }
        };

        let revealPlayed = false;
        const revealOnce = () => {
            if (revealPlayed) return;
            revealPlayed = true;
            playGatewayReveal();
        };

        if (gsap && !prefersReducedMotion && motionTargets.length) {
            if (riseMotionTargets.length) {
                gsap.set(riseMotionTargets, {
                    autoAlpha: 0,
                    y: 26
                });
            }

            if (photoCards.length) {
                gsap.set(photoCards, {
                    autoAlpha: 0,
                    x: (index) => (index % 2 === 0 ? -96 : 96),
                    rotateY: (index) => (index % 2 === 0 ? -7 : 7),
                    scale: 0.965,
                    transformPerspective: 900,
                    transformOrigin: (index) => (index % 2 === 0 ? 'left center' : 'right center'),
                    '--beginner-card-reveal': 0,
                    '--beginner-card-sheen-x': '-128%'
                });
            }

            if (footsteps.length) {
                gsap.set(footsteps, {
                    autoAlpha: 0,
                    y: 16,
                    scale: 0.5,
                    transformOrigin: '50% 100%'
                });
            }

            if ('IntersectionObserver' in window) {
                const revealObserver = new IntersectionObserver((entries) => {
                    if (entries.some(entry => entry.isIntersecting)) {
                        revealOnce();
                        revealObserver.disconnect();
                    }
                }, { threshold: 0.18 });
                revealObserver.observe(gateway);
            } else {
                revealOnce();
            }
        }

        const sweepCard = (card) => {
            if (!gsap || prefersReducedMotion) return;

            gsap.killTweensOf(card);
            gsap.fromTo(card, {
                '--guide-card-sheen': 0
            }, {
                '--guide-card-sheen': 1,
                duration: 0.44,
                ease: 'power2.out',
                onComplete: () => {
                    gsap.to(card, {
                        '--guide-card-sheen': 0,
                        duration: 0.34,
                        ease: 'sine.out'
                    });
                }
            });
        };

        const liftBeginnerPhotoCard = (card) => {
            if (!card.classList.contains('beginner-course-card--photo')) return;

            card.classList.add(photoMotionActiveClass);

            if (!gsap || prefersReducedMotion) return;
            gsap.killTweensOf(card);
            gsap.set(card, {
                '--beginner-card-sheen-x': '-128%',
                '--beginner-card-reveal': 0
            });
            gsap.to(card, {
                '--beginner-card-reveal': 1,
                '--beginner-card-sheen-x': '118%',
                duration: 0.62,
                ease: 'power2.out',
                overwrite: 'auto'
            });
        };

        const settleBeginnerPhotoCard = (card) => {
            if (!card.classList.contains('beginner-course-card--photo')) return;

            card.classList.remove(photoMotionActiveClass);
            if (!gsap || prefersReducedMotion) return;
            gsap.killTweensOf(card);
            gsap.to(card, {
                '--beginner-card-reveal': 0,
                duration: 0.36,
                ease: 'sine.out',
                overwrite: 'auto',
                onComplete: () => {
                    card.style.removeProperty('--beginner-card-reveal');
                    card.style.removeProperty('--beginner-card-sheen-x');
                }
            });
        };

        guideCards.forEach((card) => {
            card.addEventListener('pointerenter', () => {
                sweepCard(card);
                liftBeginnerPhotoCard(card);
            });
            card.addEventListener('focusin', () => {
                sweepCard(card);
                liftBeginnerPhotoCard(card);
            });
        });

        photoCards.forEach((card) => {
            card.addEventListener('pointerleave', () => settleBeginnerPhotoCard(card));
            card.addEventListener('focusout', (event) => {
                if (!card.contains(event.relatedTarget)) {
                    settleBeginnerPhotoCard(card);
                }
            });
        });

        if (gsap && startBridge && !prefersReducedMotion) {
            gsap.to(startBridge, {
                '--bridge-pulse': 1,
                duration: 1.9,
                ease: 'sine.inOut',
                repeat: -1,
                yoyo: true
            });
        }

        const canvas = gateway.querySelector('[data-guides-canvas]');
        const startCanvas = gateway.querySelector('[data-beginner-start-canvas]');
        const canUseWebGL = () => {
            if (!window.WebGLRenderingContext) return false;

            try {
                const testCanvas = document.createElement('canvas');
                return Boolean(
                    testCanvas.getContext('webgl') ||
                    testCanvas.getContext('experimental-webgl')
                );
            } catch (error) {
                return false;
            }
        };

        let threeModulePromise = null;
        const loadThreeModule = () => {
            if (!threeModulePromise) {
                threeModulePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);
            }
            return threeModulePromise;
        };

        const enhanceStartBridge = () => {
            if (!startBridge || !startCanvas || prefersReducedMotion || !canUseWebGL()) return;

            let bridgeLoaded = false;
            let bridgeRenderer = null;
            let bridgeScene = null;
            let bridgeCamera = null;
            let bridgeGroup = null;
            let bridgeParticles = null;
            let ringOuter = null;
            let ringInner = null;
            let bridgeFrame = 0;
            let bridgeVisible = false;

            const resizeBridge = () => {
                if (!bridgeRenderer || !bridgeCamera || !bridgeGroup) return;

                const width = Math.max(1, startBridge.clientWidth);
                const height = Math.max(1, startCanvas.clientHeight || startBridge.clientHeight);
                bridgeRenderer.setSize(width, height, false);
                bridgeCamera.aspect = width / height;
                bridgeCamera.updateProjectionMatrix();

                const scale = Math.min(1.08, Math.max(0.74, width / 1080));
                bridgeGroup.scale.set(scale, scale, scale);
            };

            const startBridgeLoop = () => {
                if (bridgeFrame || !bridgeRenderer || !bridgeScene || !bridgeCamera || !bridgeGroup) return;
                bridgeVisible = true;

                const render = (time) => {
                    const rhythm = time * 0.00055;
                    bridgeGroup.rotation.z = Math.sin(rhythm) * 0.035;
                    bridgeGroup.position.y = Math.sin(rhythm * 1.4) * 0.035;

                    if (ringOuter) ringOuter.rotation.z = rhythm * 0.85;
                    if (ringInner) ringInner.rotation.z = -rhythm * 1.15;
                    if (bridgeParticles) {
                        bridgeParticles.rotation.z = rhythm * 0.28;
                        bridgeParticles.rotation.y = Math.sin(rhythm * 0.9) * 0.08;
                    }

                    bridgeRenderer.render(bridgeScene, bridgeCamera);

                    if (bridgeVisible) {
                        bridgeFrame = window.requestAnimationFrame(render);
                    }
                };

                bridgeFrame = window.requestAnimationFrame(render);
            };

            const stopBridgeLoop = () => {
                bridgeVisible = false;
                if (bridgeFrame) {
                    window.cancelAnimationFrame(bridgeFrame);
                    bridgeFrame = 0;
                }
            };

            const buildBridge = async () => {
                if (bridgeLoaded) return;
                bridgeLoaded = true;

                const THREE = await loadThreeModule();
                if (!THREE) return;

                try {
                    bridgeRenderer = new THREE.WebGLRenderer({
                        canvas: startCanvas,
                        alpha: true,
                        antialias: true,
                        powerPreference: 'low-power'
                    });
                } catch (error) {
                    return;
                }

                bridgeRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
                bridgeRenderer.setClearColor(0x000000, 0);

                bridgeScene = new THREE.Scene();
                bridgeCamera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
                bridgeCamera.position.set(0, 0, 7);

                bridgeGroup = new THREE.Group();
                bridgeScene.add(bridgeGroup);

                const makeConnector = (side, color, opacity) => {
                    const points = [];
                    for (let index = 0; index < 78; index += 1) {
                        const t = index / 77;
                        const x = side * (1.1 + t * 3.25);
                        const y = Math.sin(t * Math.PI) * 0.18;
                        const z = Math.cos((t * Math.PI) + side) * 0.22;
                        points.push(new THREE.Vector3(x, y, z));
                    }

                    const curve = new THREE.CatmullRomCurve3(points);
                    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(150));
                    const material = new THREE.LineBasicMaterial({
                        color,
                        transparent: true,
                        opacity,
                        depthWrite: false
                    });
                    bridgeGroup.add(new THREE.Line(geometry, material));
                };

                makeConnector(-1, 0xb8872b, 0.72);
                makeConnector(1, 0xc94a35, 0.58);

                const outerGeometry = new THREE.TorusGeometry(1.02, 0.018, 8, 144);
                const innerGeometry = new THREE.TorusGeometry(0.72, 0.012, 8, 128);
                const outerMaterial = new THREE.MeshBasicMaterial({
                    color: 0xb8872b,
                    transparent: true,
                    opacity: 0.44,
                    depthWrite: false
                });
                const innerMaterial = new THREE.MeshBasicMaterial({
                    color: 0xc94a35,
                    transparent: true,
                    opacity: 0.36,
                    depthWrite: false
                });
                ringOuter = new THREE.Mesh(outerGeometry, outerMaterial);
                ringInner = new THREE.Mesh(innerGeometry, innerMaterial);
                bridgeGroup.add(ringOuter, ringInner);

                const count = window.innerWidth < 768 ? 54 : 96;
                const positions = new Float32Array(count * 3);
                for (let index = 0; index < count; index += 1) {
                    const offset = index * 3;
                    const angle = (index / count) * Math.PI * 2;
                    const radius = 0.8 + Math.random() * 2.4;
                    positions[offset] = Math.cos(angle) * radius;
                    positions[offset + 1] = (Math.random() - 0.5) * 1.15;
                    positions[offset + 2] = Math.sin(angle) * 0.55 + (Math.random() - 0.5) * 0.32;
                }

                const particleGeometry = new THREE.BufferGeometry();
                particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const particleMaterial = new THREE.PointsMaterial({
                    color: 0x2a0f3f,
                    size: 0.035,
                    transparent: true,
                    opacity: 0.22,
                    depthWrite: false
                });
                bridgeParticles = new THREE.Points(particleGeometry, particleMaterial);
                bridgeGroup.add(bridgeParticles);

                resizeBridge();
                startBridgeLoop();
            };

            window.addEventListener('resize', resizeBridge, { passive: true });

            if ('IntersectionObserver' in window) {
                const bridgeObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            buildBridge();
                            startBridgeLoop();
                        } else {
                            stopBridgeLoop();
                        }
                    });
                }, {
                    rootMargin: '260px 0px',
                    threshold: 0.01
                });
                bridgeObserver.observe(startBridge);
            } else {
                buildBridge();
            }
        };

        enhanceStartBridge();

        if (!canvas || prefersReducedMotion) return;

        if (!canUseWebGL()) {
            gateway.classList.add('guides-section--canvas-fallback');
            return;
        }

        let hasLoadedThree = false;
        let renderer = null;
        let scene = null;
        let camera = null;
        let field = null;
        let particles = null;
        let animationFrame = 0;
        let isVisible = false;
        const pointer = { x: 0, y: 0 };
        const pointerTarget = { x: 0, y: 0 };

        const resizeField = () => {
            if (!renderer || !camera || !field) return;

            const width = Math.max(1, gateway.clientWidth);
            const height = Math.max(1, gateway.clientHeight);
            renderer.setSize(width, height, false);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();

            const scale = Math.min(1.12, Math.max(0.74, width / 1180));
            field.scale.set(scale, scale, scale);
        };

        const startField = () => {
            if (animationFrame || !renderer || !scene || !camera || !field) return;
            isVisible = true;

            const render = (time) => {
                pointer.x += (pointerTarget.x - pointer.x) * 0.045;
                pointer.y += (pointerTarget.y - pointer.y) * 0.045;

                const rhythm = time * 0.00045;
                field.rotation.x = pointer.y * 0.08;
                field.rotation.y = pointer.x * 0.1;
                field.position.y = Math.sin(rhythm) * 0.08;

                if (particles) {
                    particles.rotation.z = rhythm * 0.28;
                    particles.rotation.y = pointer.x * 0.08;
                }

                renderer.render(scene, camera);

                if (isVisible) {
                    animationFrame = window.requestAnimationFrame(render);
                }
            };

            animationFrame = window.requestAnimationFrame(render);
        };

        const stopField = () => {
            isVisible = false;
            if (animationFrame) {
                window.cancelAnimationFrame(animationFrame);
                animationFrame = 0;
            }
        };

        const buildField = async () => {
            if (hasLoadedThree) return;
            hasLoadedThree = true;

            const THREE = await loadThreeModule();
            if (!THREE) {
                gateway.classList.add('guides-section--canvas-fallback');
                return;
            }

            try {
                renderer = new THREE.WebGLRenderer({
                    canvas,
                    alpha: true,
                    antialias: true,
                    powerPreference: 'low-power'
                });
            } catch (error) {
                gateway.classList.add('guides-section--canvas-fallback');
                return;
            }
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.setClearColor(0x000000, 0);

            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
            camera.position.set(0, 0, 7);

            field = new THREE.Group();
            scene.add(field);

            const makeRibbon = (phase, color, opacity, yOffset) => {
                const curvePoints = [];
                for (let index = 0; index < 92; index += 1) {
                    const t = index / 91;
                    const x = (t - 0.5) * 8.8;
                    const y = Math.sin((t * Math.PI * 2.4) + phase) * 0.34
                        + Math.sin((t * Math.PI * 5.2) + phase) * 0.08
                        + yOffset;
                    const z = Math.cos((t * Math.PI * 2.1) + phase) * 0.72;
                    curvePoints.push(new THREE.Vector3(x, y, z));
                }

                const curve = new THREE.CatmullRomCurve3(curvePoints);
                const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(220));
                const material = new THREE.LineBasicMaterial({
                    color,
                    transparent: true,
                    opacity,
                    depthWrite: false
                });
                field.add(new THREE.Line(geometry, material));
            };

            makeRibbon(0, 0xc94a35, 0.34, 0.45);
            makeRibbon(1.25, 0xb8872b, 0.42, 0);
            makeRibbon(2.35, 0x2a0f3f, 0.16, -0.45);

            const count = window.innerWidth < 768 ? 80 : 145;
            const positions = new Float32Array(count * 3);
            for (let index = 0; index < count; index += 1) {
                const offset = index * 3;
                positions[offset] = (Math.random() - 0.5) * 9;
                positions[offset + 1] = (Math.random() - 0.5) * 3.2;
                positions[offset + 2] = (Math.random() - 0.5) * 2.4;
            }

            const particleGeometry = new THREE.BufferGeometry();
            particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const particleMaterial = new THREE.PointsMaterial({
                color: 0xc94a35,
                size: 0.035,
                transparent: true,
                opacity: 0.28,
                depthWrite: false
            });
            particles = new THREE.Points(particleGeometry, particleMaterial);
            field.add(particles);

            resizeField();
            startField();
        };

        window.addEventListener('resize', resizeField, { passive: true });

        if ('IntersectionObserver' in window) {
            const canvasObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        buildField();
                        startField();
                    } else {
                        stopField();
                    }
                });
            }, {
                rootMargin: '360px 0px',
                threshold: 0.01
            });
            canvasObserver.observe(gateway);
        } else {
            buildField();
        }
    };

    enhanceBeginnerGateway();

    const enhancePremiumTimetable = () => {
        const schedule = document.querySelector('.schedule-section');
        if (!schedule || !document.body.classList.contains('home-page')) return;

        const rows = Array.from(schedule.querySelectorAll('.schedule-row'));
        const cards = Array.from(schedule.querySelectorAll('.class-card'));
        const tropicNoirActive = !!document.querySelector('link[href*="tropic-noir"]');
        const revealTargets = gsap
            ? gsap.utils.toArray([
                '.schedule-grid-header',
                '.hidden-mobile > .schedule-row',
                '.hidden-desktop .mobile-schedule-day'
            ].join(', '), schedule)
            : [];

        if (gsap && !prefersReducedMotion && tropicNoirActive) {
            // "Count-in": the time column ticks in first like a metronome,
            // then the class cards step in laterally, row by row.
            const gridHeader = schedule.querySelector('.schedule-grid-header');
            const timeSlots = gsap.utils.toArray('.hidden-mobile .time-slot', schedule);
            const desktopCards = gsap.utils.toArray('.hidden-mobile .class-card', schedule);
            const mobileDays = gsap.utils.toArray('.hidden-desktop .mobile-schedule-day', schedule);
            const countInTargets = [gridHeader, ...timeSlots, ...desktopCards, ...mobileDays].filter(Boolean);

            if (countInTargets.length) {
                if (gridHeader) gsap.set(gridHeader, { autoAlpha: 0, y: 12 });
                if (timeSlots.length) gsap.set(timeSlots, { autoAlpha: 0, y: 8 });
                if (desktopCards.length) gsap.set(desktopCards, { autoAlpha: 0, x: -14 });
                if (mobileDays.length) gsap.set(mobileDays, { autoAlpha: 0, y: 18 });

                let countInPlayed = false;
                const playCountIn = () => {
                    if (countInPlayed) return;
                    countInPlayed = true;
                    const timeline = gsap.timeline({
                        defaults: { ease: 'power3.out' },
                        onComplete: () => {
                            gsap.set(countInTargets, { clearProps: 'opacity,visibility,transform' });
                        }
                    });
                    if (gridHeader) {
                        timeline.to(gridHeader, { autoAlpha: 1, y: 0, duration: 0.5 });
                    }
                    if (timeSlots.length) {
                        timeline.to(timeSlots, {
                            autoAlpha: 1,
                            y: 0,
                            duration: 0.3,
                            stagger: 0.14,
                            ease: 'power2.out'
                        }, gridHeader ? '-=0.25' : 0);
                    }
                    if (desktopCards.length) {
                        timeline.to(desktopCards, {
                            autoAlpha: 1,
                            x: 0,
                            duration: 0.55,
                            stagger: 0.07
                        }, '-=0.15');
                    }
                    if (mobileDays.length) {
                        timeline.to(mobileDays, { autoAlpha: 1, y: 0, duration: 0.56, stagger: 0.08 }, '<');
                    }
                };

                if ('IntersectionObserver' in window) {
                    const observer = new IntersectionObserver((entries) => {
                        if (entries.some(entry => entry.isIntersecting)) {
                            playCountIn();
                            observer.disconnect();
                        }
                    }, {
                        threshold: 0.16
                    });
                    observer.observe(schedule);
                } else {
                    playCountIn();
                }
            }
        } else if (gsap && !prefersReducedMotion && revealTargets.length) {
            gsap.set(revealTargets, {
                autoAlpha: 0,
                y: 18
            });

            let timetableRevealed = false;
            const playTimetableReveal = () => {
                if (timetableRevealed) return;
                timetableRevealed = true;
                gsap.to(revealTargets, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.56,
                    stagger: 0.055,
                    ease: 'power3.out',
                    clearProps: 'opacity,visibility,transform'
                });
            };

            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    if (entries.some(entry => entry.isIntersecting)) {
                        playTimetableReveal();
                        observer.disconnect();
                    }
                }, {
                    threshold: 0.16
                });
                observer.observe(schedule);
            } else {
                playTimetableReveal();
            }
        }

        const clearTimetableFocus = () => {
            schedule.classList.remove('is-interacting');
            rows.forEach(row => row.classList.remove('is-focused'));
        };

        const markTimetableFocus = (card) => {
            const row = card.closest('.schedule-row');
            schedule.classList.add('is-interacting');
            rows.forEach(item => item.classList.toggle('is-focused', item === row));

            if (!gsap || prefersReducedMotion) return;
            gsap.killTweensOf(card);
            gsap.fromTo(card, {
                '--timetable-sheen': '-140%'
            }, {
                '--timetable-sheen': '160%',
                duration: 0.68,
                ease: 'power2.out',
                onComplete: () => {
                    gsap.set(card, {
                        '--timetable-sheen': '-140%'
                    });
                }
            });
        };

        cards.forEach((card) => {
            card.addEventListener('pointerenter', () => markTimetableFocus(card));
            card.addEventListener('focus', () => markTimetableFocus(card));
            card.addEventListener('blur', clearTimetableFocus);
        });

        schedule.addEventListener('pointerleave', clearTimetableFocus);
    };

    enhancePremiumTimetable();

    const enhanceTropicChoreography = () => {
        // Homepage-only motion system for the Tropic Noir prototype.
        // The .reveal slab is neutralized in tropic-noir.css; content stays
        // visible without JavaScript and under prefers-reduced-motion.
        if (!document.body.classList.contains('home-page')) return;
        if (!document.querySelector('link[href*="tropic-noir"]')) return;

        const observeOnce = (target, onEnter, options) => {
            if (!('IntersectionObserver' in window)) {
                onEnter();
                return;
            }
            const observer = new IntersectionObserver((entries) => {
                if (entries.some(entry => entry.isIntersecting)) {
                    observer.disconnect();
                    onEnter();
                }
            }, options);
            observer.observe(target);
        };

        // FAQ soft open: animated height instead of the native snap. The
        // native toggle stays in place for reduced motion and without GSAP.
        const faqSection = document.querySelector('.home-faq-section');
        if (faqSection) {
            faqSection.querySelectorAll('details').forEach((item) => {
                const summary = item.querySelector('summary');
                const content = summary ? summary.nextElementSibling : null;
                if (!summary || !content) return;

                const contentPaddingBottom = window.getComputedStyle(content).paddingBottom;

                summary.addEventListener('click', (event) => {
                    if (!gsap || prefersReducedMotion) return;
                    event.preventDefault();
                    if (item.dataset.faqAnimating === 'true') return;
                    item.dataset.faqAnimating = 'true';

                    if (item.open) {
                        gsap.to(content, {
                            height: 0,
                            paddingBottom: 0,
                            autoAlpha: 0,
                            duration: 0.32,
                            ease: 'power2.in',
                            onComplete: () => {
                                item.open = false;
                                gsap.set(content, { clearProps: 'height,opacity,visibility' });
                                gsap.set(content, { paddingBottom: contentPaddingBottom });
                                delete item.dataset.faqAnimating;
                            }
                        });
                    } else {
                        item.open = true;
                        gsap.set(content, { paddingBottom: contentPaddingBottom });
                        gsap.from(content, {
                            height: 0,
                            paddingBottom: 0,
                            autoAlpha: 0,
                            duration: 0.45,
                            ease: 'power3.out',
                            onComplete: () => {
                                gsap.set(content, { clearProps: 'height,opacity,visibility' });
                                gsap.set(content, { paddingBottom: contentPaddingBottom });
                                delete item.dataset.faqAnimating;
                            }
                        });
                    }
                });
            });
        }

        if (!gsap || prefersReducedMotion) return;

        // Dancing underline: the section-title rule draws in three steps and
        // a tap (the bachata basic). Drives the CSS variable read by the
        // ::after element in tropic-noir.css.
        gsap.utils.toArray('.section-title-modern').forEach((title) => {
            gsap.set(title, { '--title-underline-scale': 0 });
            observeOnce(title, () => {
                gsap.to(title, {
                    keyframes: [
                        { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
                    ]
                });
            }, { threshold: 0.4, rootMargin: '0px 0px -10% 0px' });
        });

        // Lead & Follow: the heading leads, content answers a half-beat
        // later with a 1-2-3-tap stagger (a breath after every fourth item).
        // The beginner gateway and schedule keep their own choreography.
        const beatStagger = (index) => 0.07 * index + Math.floor(index / 4) * 0.07;
        const choreography = [
            {
                root: '#about',
                lead: '.stay-visual__header',
                follow: ['.atelier-photo', '.atelier-gallery-meta', '.stay-copy']
            },
            {
                root: '#reviews',
                lead: '.section-title-modern',
                follow: ['.reviews-proof', '.reviews-slider-wrapper']
            },
            {
                root: '#trial-form',
                lead: '.cta-premium-kicker, .cta-premium-title',
                follow: ['.cta-premium-mark', '.cta-premium-note', '.trial-expectation']
            },
            {
                root: '.home-faq-section',
                lead: '.section-title-modern',
                follow: ['.faq-list details']
            }
        ];

        choreography.forEach(({ root, lead, follow }) => {
            const rootElement = document.querySelector(root);
            if (!rootElement) return;

            const leadTargets = gsap.utils.toArray(lead, rootElement);
            const followTargets = follow.flatMap((selector) => gsap.utils.toArray(selector, rootElement));
            if (!leadTargets.length && !followTargets.length) return;

            if (leadTargets.length) gsap.set(leadTargets, { autoAlpha: 0, y: 18 });
            if (followTargets.length) gsap.set(followTargets, { autoAlpha: 0, y: 14 });

            observeOnce(rootElement, () => {
                const timeline = gsap.timeline({
                    defaults: { ease: 'power3.out' },
                    onComplete: () => {
                        gsap.set([...leadTargets, ...followTargets], { clearProps: 'opacity,visibility,transform' });
                    }
                });
                if (leadTargets.length) {
                    timeline.to(leadTargets, { autoAlpha: 1, y: 0, duration: 0.6, stagger: 0.07 });
                }
                if (followTargets.length) {
                    timeline.to(followTargets, {
                        autoAlpha: 1,
                        y: 0,
                        duration: 0.6,
                        stagger: beatStagger
                    }, leadTargets.length ? '-=0.35' : 0);
                }
            }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
        });

    };

    enhanceTropicChoreography();

    const enhanceEventsPage = () => {
        // Events-page motion system for the Tropic Noir theme. Content stays
        // fully visible without JavaScript and under prefers-reduced-motion;
        // initial hidden states are set from JS only.
        if (!document.body.classList.contains('events-page')) return;
        if (!document.querySelector('link[href*="tropic-noir"]')) return;

        const heroSection = document.querySelector('[data-events-hero]');

        // --- Bootcamp countdown (content, not motion: runs without GSAP and
        // under prefers-reduced-motion). Values are recomputed from the
        // absolute event start (Zurich time), so every visitor time zone
        // counts down to the same instant. ---
        const countdown = document.querySelector('[data-bootcamp-countdown]');
        if (countdown) {
            const startTime = Date.parse(countdown.dataset.countdownStart || '');
            const endTime = Date.parse(countdown.dataset.countdownEnd || '');
            const countdownLabel = countdown.querySelector('[data-countdown-label]');
            const countdownUnits = countdown.querySelector('[data-countdown-units]');
            const countdownDays = countdown.querySelector('[data-countdown-days]');
            const countdownHours = countdown.querySelector('[data-countdown-hours]');
            const countdownMinutes = countdown.querySelector('[data-countdown-minutes]');
            const countdownLiveLabel = countdown.dataset.countdownLiveLabel;

            if (Number.isFinite(startTime) && countdownDays && countdownHours && countdownMinutes) {
                const renderCountdown = () => {
                    const now = Date.now();
                    if (Number.isFinite(endTime) && now >= endTime) {
                        // Event over: retire the block entirely.
                        countdown.hidden = true;
                        return false;
                    }
                    if (now >= startTime) {
                        // Live window: the numbers stop mattering, the fact
                        // that it is happening does.
                        if (countdownLiveLabel && countdownLabel) {
                            countdownLabel.textContent = countdownLiveLabel;
                        }
                        if (countdownUnits) countdownUnits.hidden = true;
                        countdown.hidden = false;
                        return true;
                    }
                    const totalMinutes = Math.floor((startTime - now) / 60000);
                    countdownDays.textContent = String(Math.floor(totalMinutes / 1440));
                    countdownHours.textContent = String(Math.floor((totalMinutes % 1440) / 60));
                    countdownMinutes.textContent = String(totalMinutes % 60);
                    countdown.hidden = false;
                    return true;
                };
                if (renderCountdown()) {
                    window.setInterval(renderCountdown, 30000);
                }
            }
        }

        const observeOnce = (target, onEnter, options) => {
            if (!('IntersectionObserver' in window)) {
                onEnter();
                return;
            }
            const observer = new IntersectionObserver((entries) => {
                if (entries.some(entry => entry.isIntersecting)) {
                    observer.disconnect();
                    onEnter();
                }
            }, options);
            observer.observe(target);
        };

        // --- Entrance choreography (Lead & Follow, same grammar as home) ---
        if (gsap && !prefersReducedMotion) {
            if (heroSection) {
                const heroKicker = heroSection.querySelector('.events-hero-stage__kicker');
                const heroTitle = heroSection.querySelector('.events-hero-stage__title');
                const heroLede = heroSection.querySelector('.events-hero-stage__lede');
                const heroActions = gsap.utils.toArray('.events-hero-stage__actions .btn-hero');
                const heroTargets = [heroKicker, heroTitle, heroLede, ...heroActions].filter(Boolean);
                if (heroTargets.length) {
                    gsap.timeline({
                        defaults: { ease: 'power3.out' },
                        onComplete: () => {
                            gsap.set(heroTargets, { clearProps: 'opacity,visibility,transform' });
                        }
                    })
                        .from(heroKicker, { autoAlpha: 0, y: 12, duration: 0.45 })
                        .from(heroTitle, { autoAlpha: 0, y: 18, duration: 0.62 }, '-=0.2')
                        .from(heroLede, { autoAlpha: 0, y: 14, duration: 0.55 }, '-=0.34')
                        .from(heroActions, { autoAlpha: 0, y: 14, duration: 0.5, stagger: 0.09 }, '-=0.3');
                }
            }

            // Dancing underline: identical keyframes to the homepage motif.
            gsap.utils.toArray('.section-title-modern').forEach((title) => {
                gsap.set(title, { '--title-underline-scale': 0 });
                observeOnce(title, () => {
                    gsap.to(title, {
                        keyframes: [
                            { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
                            { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
                            { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
                            { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
                        ]
                    });
                }, { threshold: 0.4, rootMargin: '0px 0px -10% 0px' });
            });

            const beatStagger = (index) => 0.07 * index + Math.floor(index / 4) * 0.07;
            // Roots that are absent on a given page are skipped silently, so
            // the events listing and the bootcamp detail page share this map.
            const choreography = [
                {
                    root: '.season-section',
                    lead: '.section-title-modern',
                    follow: ['.section-subtitle', '.season-rail__item']
                },
                {
                    root: '.bootcamp-stats',
                    lead: '.bootcamp-stats__item',
                    follow: []
                },
                {
                    root: '.bootcamp-register',
                    lead: '.event-act__kicker, .section-title-modern',
                    follow: ['.bootcamp-register__copy', '.event-act__facts', '.bootcamp-register__island']
                },
                {
                    root: '.bootcamp-level',
                    lead: '.section-title-modern',
                    follow: ['.section-subtitle', '.bootcamp-level__chip']
                },
                {
                    root: '.bootcamp-faq',
                    lead: '.section-title-modern',
                    follow: ['.bootcamp-faq__item']
                },
                {
                    root: '.event-act--zurich',
                    lead: '.event-act__kicker, .event-act__date, .section-title-modern, .event-act__artist-role',
                    follow: ['.event-act__media', '.event-act__copy', '.event-act__facts', '.event-act__actions']
                },
                {
                    root: '.event-nights',
                    lead: '.section-title-modern',
                    follow: ['.section-subtitle', '.event-nights__photo']
                },
                {
                    root: '.event-act--milano',
                    lead: '.event-act__flag, .event-act__kicker, .event-act__date, .section-title-modern, .event-act__artist-role',
                    follow: ['.event-act__media', '.event-act__copy', '.event-act__facts', '.event-act__actions']
                },
                {
                    root: '.events-bridge',
                    lead: '.section-title-modern',
                    follow: ['.section-subtitle', '.events-bridge__actions .btn-hero']
                }
            ];

            choreography.forEach(({ root, lead, follow }) => {
                const rootElement = document.querySelector(root);
                if (!rootElement) return;

                const leadTargets = gsap.utils.toArray(lead, rootElement);
                const followTargets = follow.flatMap((selector) => gsap.utils.toArray(selector, rootElement));
                if (!leadTargets.length && !followTargets.length) return;

                if (leadTargets.length) gsap.set(leadTargets, { autoAlpha: 0, y: 18 });
                if (followTargets.length) gsap.set(followTargets, { autoAlpha: 0, y: 14 });

                observeOnce(rootElement, () => {
                    const timeline = gsap.timeline({
                        defaults: { ease: 'power3.out' },
                        onComplete: () => {
                            gsap.set([...leadTargets, ...followTargets], { clearProps: 'opacity,visibility,transform' });
                        }
                    });
                    if (leadTargets.length) {
                        timeline.to(leadTargets, { autoAlpha: 1, y: 0, duration: 0.6, stagger: 0.07 });
                    }
                    if (followTargets.length) {
                        timeline.to(followTargets, {
                            autoAlpha: 1,
                            y: 0,
                            duration: 0.6,
                            stagger: beatStagger
                        }, leadTargets.length ? '-=0.35' : 0);
                    }
                }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
            });
        }

        // --- Demo video (bootcamp page): loads nothing until the visitor
        // presses play (preload="none"); pauses itself when scrolled away.
        const demoVideoWrap = document.querySelector('[data-bootcamp-video]');
        if (demoVideoWrap && 'IntersectionObserver' in window) {
            const demoVideo = demoVideoWrap.querySelector('video');
            if (demoVideo) {
                const videoObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (!entry.isIntersecting && !demoVideo.paused) {
                            demoVideo.pause();
                        }
                    });
                }, { threshold: 0.2 });
                videoObserver.observe(demoVideo);
            }
        }

        // --- Subheader rail: the compact bar pinned under the main nav on the
        // events listing. Highlights the link of the event act currently on
        // screen; runs regardless of reduced-motion because it conveys
        // state, not motion.
        const subheaderNav = document.querySelector('[data-events-subheader]');
        if (subheaderNav && 'IntersectionObserver' in window) {
            const subheaderLinks = Array.from(subheaderNav.querySelectorAll('a[href^="#"]'));
            const subheaderTargets = subheaderLinks
                .map((link) => document.getElementById(link.hash.slice(1)))
                .filter(Boolean);
            const setActiveSubheaderLink = (id) => {
                subheaderLinks.forEach((link) => {
                    link.classList.toggle('events-subheader__item--active', link.hash === `#${id}`);
                });
            };
            const subheaderObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) setActiveSubheaderLink(entry.target.id);
                });
            }, { rootMargin: '-40% 0px -50% 0px' });
            subheaderTargets.forEach((target) => subheaderObserver.observe(target));
        }

        // --- Artist lineup switcher (bootcamp page): a page switch between
        // the Aitor and Sarah panels. Without JS both panels stay visible in
        // normal flow; nav buttons/dots and the hidden state are added here
        // only, so the page degrades gracefully with JS disabled.
        const lineupSwitcher = document.querySelector('[data-artist-switcher]');
        if (lineupSwitcher) {
            const lineupSection = lineupSwitcher.closest('.bootcamp-lineup');
            const panels = Array.from(lineupSwitcher.querySelectorAll('[data-artist-panel]'));
            const dots = Array.from(document.querySelectorAll('[data-artist-dot]'));
            const navButtons = Array.from(lineupSwitcher.querySelectorAll('[data-artist-nav]'));
            const reduceLineupMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

            if (lineupSection && panels.length > 1) {
                let activeIndex = 0;

                const showPanel = (nextIndex) => {
                    if (nextIndex === activeIndex) return;
                    const current = panels[activeIndex];
                    const next = panels[nextIndex];
                    activeIndex = nextIndex;
                    dots.forEach((dot, i) => dot.setAttribute('aria-selected', String(i === activeIndex)));

                    const activate = () => {
                        current.hidden = true;
                        current.classList.remove('is-fading');
                        next.hidden = false;
                        requestAnimationFrame(() => next.classList.remove('is-fading'));
                    };

                    if (reduceLineupMotion) {
                        activate();
                        return;
                    }

                    current.classList.add('is-fading');
                    next.classList.add('is-fading');
                    let settled = false;
                    const onFadeOut = (event) => {
                        if (event.target !== current || event.propertyName !== 'opacity' || settled) return;
                        settled = true;
                        current.removeEventListener('transitionend', onFadeOut);
                        activate();
                    };
                    current.addEventListener('transitionend', onFadeOut);
                    setTimeout(onFadeOut, 500, { target: current, propertyName: 'opacity' });
                };

                navButtons.forEach((btn) => {
                    btn.addEventListener('click', () => {
                        const dir = btn.dataset.artistNav === 'next' ? 1 : -1;
                        showPanel((activeIndex + dir + panels.length) % panels.length);
                    });
                });

                dots.forEach((dot, i) => {
                    dot.addEventListener('click', () => showPanel(i));
                });

                panels.forEach((panel, i) => { panel.hidden = i !== 0; });
                dots.forEach((dot, i) => dot.setAttribute('aria-selected', String(i === 0)));
                lineupSection.classList.add('is-enhanced');
            }
        }

    };

    enhanceEventsPage();

    const enhanceCourseDossier = () => {
        // Course-page motion system for the Tropic Noir dossier template.
        // Content stays fully visible without JavaScript and under
        // prefers-reduced-motion; everything here is additive.
        if (!document.body.classList.contains('course-page')) return;
        if (!document.querySelector('link[href*="tropic-noir"]')) return;

        const observeOnce = (target, onEnter, options) => {
            if (!target) return;
            if (!('IntersectionObserver' in window)) {
                onEnter();
                return;
            }
            const observer = new IntersectionObserver((entries) => {
                if (entries.some(entry => entry.isIntersecting)) {
                    observer.disconnect();
                    onEnter();
                }
            }, options);
            observer.observe(target);
        };

        // FAQ soft open: animated height instead of the native snap. The
        // native toggle stays in place for reduced motion and without GSAP.
        const faqList = document.querySelector('.course-faq__list');
        if (faqList) {
            faqList.querySelectorAll('details').forEach((item) => {
                const summary = item.querySelector('summary');
                const content = summary ? summary.nextElementSibling : null;
                if (!summary || !content) return;

                const contentPaddingBottom = window.getComputedStyle(content).paddingBottom;

                summary.addEventListener('click', (event) => {
                    if (!gsap || prefersReducedMotion) return;
                    event.preventDefault();
                    if (item.dataset.faqAnimating === 'true') return;
                    item.dataset.faqAnimating = 'true';

                    if (item.open) {
                        gsap.to(content, {
                            height: 0,
                            paddingBottom: 0,
                            autoAlpha: 0,
                            duration: 0.32,
                            ease: 'power2.in',
                            onComplete: () => {
                                item.open = false;
                                gsap.set(content, { clearProps: 'height,opacity,visibility' });
                                gsap.set(content, { paddingBottom: contentPaddingBottom });
                                delete item.dataset.faqAnimating;
                            }
                        });
                    } else {
                        item.open = true;
                        gsap.set(content, { paddingBottom: contentPaddingBottom });
                        gsap.from(content, {
                            height: 0,
                            paddingBottom: 0,
                            autoAlpha: 0,
                            duration: 0.45,
                            ease: 'power3.out',
                            onComplete: () => {
                                gsap.set(content, { clearProps: 'height,opacity,visibility' });
                                gsap.set(content, { paddingBottom: contentPaddingBottom });
                                delete item.dataset.faqAnimating;
                            }
                        });
                    }
                });
            });
        }

        // Studio haze: warm brass dust drifting inside the masthead's taped
        // frame - dust in stage light, the one ambient WebGL scene of the
        // page. Built lazily, DPR-capped, paused offscreen; without WebGL or
        // with reduced motion the transparent canvas simply stays empty.
        const masthead = document.querySelector('.course-masthead');
        const hazeCanvas = document.querySelector('[data-course-haze]');
        const hazeHost = document.querySelector('[data-course-media]');
        const canUseWebGL = () => {
            if (!window.WebGLRenderingContext) return false;

            try {
                const testCanvas = document.createElement('canvas');
                return Boolean(
                    testCanvas.getContext('webgl') ||
                    testCanvas.getContext('experimental-webgl')
                );
            } catch (error) {
                return false;
            }
        };

        let threeModulePromise = null;
        const loadThreeModule = () => {
            if (!threeModulePromise) {
                threeModulePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);
            }
            return threeModulePromise;
        };

        const enhanceStudioHaze = () => {
            if (!masthead || !hazeCanvas || !hazeHost || prefersReducedMotion || !canUseWebGL()) return;

            let hazeLoaded = false;
            let hazeRenderer = null;
            let hazeScene = null;
            let hazeCamera = null;
            let hazePoints = null;
            let hazeSeeds = null;
            let hazeFrame = 0;
            let hazeVisible = false;

            const resizeHaze = () => {
                if (!hazeRenderer || !hazeCamera) return;

                const width = Math.max(1, hazeHost.clientWidth);
                const height = Math.max(1, hazeHost.clientHeight);
                hazeRenderer.setSize(width, height, false);
                hazeCamera.aspect = width / height;
                hazeCamera.updateProjectionMatrix();
            };

            const startHazeLoop = () => {
                if (hazeFrame || !hazeRenderer || !hazeScene || !hazeCamera || !hazePoints) return;
                hazeVisible = true;

                const render = (time) => {
                    const positions = hazePoints.geometry.attributes.position;
                    for (let index = 0; index < positions.count; index += 1) {
                        const seed = hazeSeeds[index];
                        let y = positions.getY(index) + seed.rise;
                        if (y > 1.6) y = -1.6;
                        positions.setY(index, y);
                        positions.setX(index, seed.baseX + Math.sin((time * 0.00045) + seed.phase) * seed.sway);
                    }
                    positions.needsUpdate = true;
                    hazeRenderer.render(hazeScene, hazeCamera);

                    if (hazeVisible) {
                        hazeFrame = window.requestAnimationFrame(render);
                    }
                };

                hazeFrame = window.requestAnimationFrame(render);
            };

            const stopHazeLoop = () => {
                hazeVisible = false;
                if (hazeFrame) {
                    window.cancelAnimationFrame(hazeFrame);
                    hazeFrame = 0;
                }
            };

            const buildHaze = async () => {
                if (hazeLoaded) return;
                hazeLoaded = true;

                const THREE = await loadThreeModule();
                if (!THREE) return;

                try {
                    hazeRenderer = new THREE.WebGLRenderer({
                        canvas: hazeCanvas,
                        alpha: true,
                        antialias: true,
                        powerPreference: 'low-power'
                    });
                } catch (error) {
                    return;
                }

                hazeRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
                hazeRenderer.setClearColor(0x000000, 0);

                hazeScene = new THREE.Scene();
                hazeCamera = new THREE.PerspectiveCamera(45, 1, 0.1, 20);
                hazeCamera.position.set(0, 0, 3.2);

                const count = window.innerWidth < 768 ? 45 : 80;
                const positions = new Float32Array(count * 3);
                hazeSeeds = [];
                for (let index = 0; index < count; index += 1) {
                    const offset = index * 3;
                    const baseX = (Math.random() - 0.5) * 2.4;
                    positions[offset] = baseX;
                    positions[offset + 1] = (Math.random() - 0.5) * 3.2;
                    positions[offset + 2] = (Math.random() - 0.5) * 0.8;
                    hazeSeeds.push({
                        baseX,
                        rise: 0.0009 + Math.random() * 0.0014,
                        sway: 0.03 + Math.random() * 0.05,
                        phase: Math.random() * Math.PI * 2
                    });
                }

                const hazeGeometry = new THREE.BufferGeometry();
                hazeGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const hazeMaterial = new THREE.PointsMaterial({
                    color: 0xE8B04B,
                    size: 0.035,
                    transparent: true,
                    opacity: 0.32,
                    depthWrite: false
                });
                hazePoints = new THREE.Points(hazeGeometry, hazeMaterial);
                hazeScene.add(hazePoints);

                resizeHaze();
                startHazeLoop();
            };

            window.addEventListener('resize', resizeHaze, { passive: true });

            if ('IntersectionObserver' in window) {
                const hazeObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            buildHaze();
                            startHazeLoop();
                        } else {
                            stopHazeLoop();
                        }
                    });
                }, {
                    rootMargin: '260px 0px',
                    threshold: 0.01
                });
                hazeObserver.observe(masthead);
            } else {
                buildHaze();
            }
        };

        enhanceStudioHaze();

        if (!gsap || prefersReducedMotion) return;

        // Safety settle, shared by every choreographed block: guarantees the
        // resting (fully visible) state shortly after a timeline starts, even
        // if the browser throttles requestAnimationFrame and the tween stalls.
        const createSettle = (targets, onClear) => {
            let animation = null;
            let settled = false;
            const settle = () => {
                if (settled) return;
                settled = true;
                if (animation) animation.kill();
                gsap.set(targets, { clearProps: 'opacity,visibility,transform,borderColor' });
                if (onClear) onClear();
            };
            return {
                attach: (createdAnimation) => {
                    animation = createdAnimation;
                    window.setTimeout(settle, 3200);
                },
                settle
            };
        };

        // Dancing underline: the same three-steps-and-a-tap as the homepage.
        gsap.utils.toArray('.section-title-modern').forEach((title) => {
            gsap.set(title, { '--title-underline-scale': 0 });
            observeOnce(title, () => {
                const settle = createSettle([], () => {
                    title.style.removeProperty('--title-underline-scale');
                });
                settle.attach(gsap.to(title, {
                    keyframes: [
                        { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
                        { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
                    ]
                }));
            }, { threshold: 0.4, rootMargin: '0px 0px -10% 0px' });
        });

        const beatStagger = (index) => 0.07 * index + Math.floor(index / 4) * 0.07;

        // Masthead entrance: kicker and title lead; the call sheet, actions,
        // and taped figure answer a half-beat later.
        const mastheadLead = gsap.utils.toArray('.course-masthead__kicker, .course-masthead__title');
        const mastheadFollow = gsap.utils.toArray('.course-masthead__dek, .course-callsheet__item, .course-masthead__actions a');
        const mastheadFigure = document.querySelector('.course-masthead__figure');
        const mastheadTargets = [...mastheadLead, ...mastheadFollow, mastheadFigure].filter(Boolean);
        if (mastheadTargets.length) {
            let mastheadTimeline = null;
            const clearMastheadStyles = () => {
                // Also kills a still-running timeline (a background tab can
                // throttle rAF past the safety timeout) so nothing re-hides
                // content after the clear.
                if (mastheadTimeline) {
                    mastheadTimeline.kill();
                    mastheadTimeline = null;
                }
                gsap.set(mastheadTargets, { clearProps: 'opacity,visibility,transform' });
            };

            mastheadTimeline = gsap.timeline({
                defaults: { ease: 'power3.out' },
                onComplete: clearMastheadStyles
            });
            if (mastheadLead.length) {
                mastheadTimeline.from(mastheadLead, { autoAlpha: 0, y: 18, duration: 0.55, stagger: 0.09 });
            }
            if (mastheadFigure) {
                mastheadTimeline.from(mastheadFigure, { autoAlpha: 0, x: 18, duration: 0.6 }, '-=0.38');
            }
            if (mastheadFollow.length) {
                mastheadTimeline.from(mastheadFollow, {
                    autoAlpha: 0,
                    y: 14,
                    duration: 0.5,
                    stagger: beatStagger
                }, '-=0.45');
            }

            window.setTimeout(clearMastheadStyles, 2400);
        }

        // One night in the room: the count-in. Steps land strictly in order
        // and each connector dash draws in with the step it belongs to.
        const nightSteps = gsap.utils.toArray('.course-night__step');
        if (nightSteps.length) {
            gsap.set(nightSteps, { autoAlpha: 0, x: 16 });
            nightSteps.forEach((step) => step.style.setProperty('--rail-draw', 0));
            observeOnce(document.querySelector('.course-night'), () => {
                const settle = createSettle(nightSteps, () => {
                    nightSteps.forEach((step) => step.style.removeProperty('--rail-draw'));
                });
                const nightTimeline = gsap.timeline({
                    defaults: { ease: 'power3.out' },
                    onComplete: settle.settle
                });
                nightSteps.forEach((step, index) => {
                    nightTimeline.to(step, { autoAlpha: 1, x: 0, duration: 0.5 }, index === 0 ? 0 : '-=0.32');
                    if (index > 0) {
                        nightTimeline.to(step, { '--rail-draw': 1, duration: 0.3, ease: 'power2.out' }, '<');
                    }
                });
                settle.attach(nightTimeline);
            }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });
        }

        // Pathway ladder: rungs draw left to right; when the sequence
        // reaches "you are here" the rung answers with a short, finite
        // border pulse - colour only, then rest.
        const pathRungs = gsap.utils.toArray('.course-path__rung');
        if (pathRungs.length) {
            gsap.set(pathRungs, { autoAlpha: 0, x: 14 });
            pathRungs.forEach((rung) => rung.style.setProperty('--rail-draw', 0));
            observeOnce(document.querySelector('.course-path'), () => {
                const settle = createSettle(pathRungs, () => {
                    pathRungs.forEach((rung) => rung.style.removeProperty('--rail-draw'));
                });
                const pathTimeline = gsap.timeline({
                    defaults: { ease: 'power3.out' },
                    onComplete: settle.settle
                });
                pathRungs.forEach((rung, index) => {
                    pathTimeline.to(rung, { autoAlpha: 1, x: 0, duration: 0.45 }, index === 0 ? 0 : '-=0.28');
                    if (index > 0) {
                        pathTimeline.to(rung, { '--rail-draw': 1, duration: 0.26, ease: 'power2.out' }, '<');
                    }
                    if (rung.classList.contains('course-path__rung--current')) {
                        pathTimeline.to(rung, {
                            borderColor: 'rgba(232, 176, 75, 0.9)',
                            duration: 0.22,
                            ease: 'power1.inOut',
                            repeat: 3,
                            yoyo: true,
                            onComplete: () => {
                                gsap.set(rung, { clearProps: 'borderColor' });
                            }
                        }, '>-0.05');
                    }
                });
                settle.attach(pathTimeline);
            }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });
        }

        // Level fork: "your" voice leads in from the left, the other voice
        // answers from the right a half-beat later.
        const forkRoot = document.querySelector('.course-fork');
        if (forkRoot) {
            const forkTitle = forkRoot.querySelector('.section-title-modern');
            const forkHere = forkRoot.querySelector('.course-fork__path--here');
            const forkOther = gsap.utils.toArray('.course-fork__path:not(.course-fork__path--here)', forkRoot);
            const forkUnsure = forkRoot.querySelector('.course-fork__unsure');
            const forkTargets = [forkTitle, forkHere, ...forkOther, forkUnsure].filter(Boolean);
            if (forkTargets.length) {
                if (forkTitle) gsap.set(forkTitle, { autoAlpha: 0, y: 18 });
                if (forkHere) gsap.set(forkHere, { autoAlpha: 0, x: -14 });
                if (forkOther.length) gsap.set(forkOther, { autoAlpha: 0, x: 14 });
                if (forkUnsure) gsap.set(forkUnsure, { autoAlpha: 0, y: 12 });
                observeOnce(forkRoot, () => {
                    const settle = createSettle(forkTargets);
                    const forkTimeline = gsap.timeline({
                        defaults: { ease: 'power3.out' },
                        onComplete: settle.settle
                    });
                    if (forkTitle) forkTimeline.to(forkTitle, { autoAlpha: 1, y: 0, duration: 0.5 });
                    if (forkHere) forkTimeline.to(forkHere, { autoAlpha: 1, x: 0, duration: 0.55 }, '-=0.25');
                    if (forkOther.length) forkTimeline.to(forkOther, { autoAlpha: 1, x: 0, duration: 0.55 }, '-=0.35');
                    if (forkUnsure) forkTimeline.to(forkUnsure, { autoAlpha: 1, y: 0, duration: 0.45 }, '-=0.25');
                    settle.attach(forkTimeline);
                }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });
            }
        }

        // Remaining dossier sections: the title leads, content answers with
        // the 1-2-3-tap stagger.
        const dossierSections = [
            {
                root: '.course-syllabus',
                lead: '.section-title-modern, .course-syllabus__subtitle',
                follow: ['.course-syllabus__item', '.course-syllabus__rotation'],
                followFrom: { x: 14 }
            },
            {
                root: '.course-teachers',
                lead: '.section-title-modern',
                follow: ['.founders-strip__photo', '.founders-strip__names', '.founders-strip__role', '.founders-strip__link']
            },
            {
                root: '.course-register',
                lead: '.course-register__title',
                follow: ['.course-register__lede', '.course-register__actions > *', '.course-register__pricing', '.course-register__trust']
            },
            {
                root: '.course-faq',
                lead: '.section-title-modern',
                follow: ['.course-faq__item']
            }
        ];

        dossierSections.forEach(({ root, lead, follow, followFrom }) => {
            const rootElement = document.querySelector(root);
            if (!rootElement) return;

            const leadTargets = gsap.utils.toArray(lead, rootElement);
            const followTargets = follow.flatMap((selector) => gsap.utils.toArray(selector, rootElement));
            if (!leadTargets.length && !followTargets.length) return;

            if (leadTargets.length) gsap.set(leadTargets, { autoAlpha: 0, y: 18 });
            if (followTargets.length) gsap.set(followTargets, { autoAlpha: 0, ...(followFrom || { y: 14 }) });

            observeOnce(rootElement, () => {
                const settle = createSettle([...leadTargets, ...followTargets]);
                const sectionTimeline = gsap.timeline({
                    defaults: { ease: 'power3.out' },
                    onComplete: settle.settle
                });
                if (leadTargets.length) {
                    sectionTimeline.to(leadTargets, { autoAlpha: 1, y: 0, duration: 0.6, stagger: 0.07 });
                }
                if (followTargets.length) {
                    sectionTimeline.to(followTargets, {
                        autoAlpha: 1,
                        x: 0,
                        y: 0,
                        duration: 0.6,
                        stagger: beatStagger
                    }, leadTargets.length ? '-=0.35' : 0);
                }
                settle.attach(sectionTimeline);
            }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
        });
    };

    enhanceCourseDossier();

    // Mobile sticky trial bar: visible while browsing, steps aside once the
    // trial form itself is on screen (no point pointing at what is visible).
    const mobileCtaBar = document.querySelector('[data-mobile-cta-bar]');
    const mobileCtaTarget = document.getElementById('trial-form');
    if (mobileCtaBar && mobileCtaTarget && 'IntersectionObserver' in window) {
        const mobileCtaObserver = new IntersectionObserver((entries) => {
            const formInView = entries.some((entry) => entry.isIntersecting);
            mobileCtaBar.classList.toggle('mobile-cta-bar--hidden', formInView);
        }, { rootMargin: '0px 0px -15% 0px' });
        mobileCtaObserver.observe(mobileCtaTarget);
    }

    const enhanceContactQuestionFlow = () => {
        const questionFlow = document.querySelector('.contact-question-flow');
        const wordSlot = questionFlow?.querySelector('[data-contact-question-word]');
        const canvas = questionFlow?.querySelector('[data-contact-question-canvas]');
        if (!questionFlow || !wordSlot || !canvas) return;

        const words = (wordSlot.dataset.contactQuestionWords || wordSlot.textContent || '')
            .split('|')
            .map((word) => word.trim())
            .filter(Boolean);
        if (!words.length) return;

        const wordCycleDelay = 1500;
        // Tropic Noir pages recolor the hero scene to coral/brass/champagne;
        // pages without the stylesheet keep the warm cream palette.
        const tropicNoirActive = !!document.querySelector('link[href*="tropic-noir"]');
        const sceneState = { pulse: 0, activeIndex: 0 };
        let activeWordIndex = 0;
        let activeWordElement = null;
        let wordDelayCall = null;
        let wordCleanupCall = null;
        let wordTimeline = null;
        let isWordAnimating = false;
        let hasStartedWords = false;
        let isFlowVisible = false;

        const createWordElement = (word) => {
            const wordElement = document.createElement('span');
            wordElement.className = 'contact-question-flow__word';
            wordElement.setAttribute('aria-hidden', 'true');

            Array.from(word).forEach((character) => {
                const glyph = document.createElement('span');
                glyph.className = character === ' ' ? 'contact-question-flow__space' : 'contact-question-flow__glyph';
                glyph.textContent = character === ' ' ? '\u00a0' : character;
                wordElement.appendChild(glyph);
            });

            return wordElement;
        };

        const cleanWordStyles = (wordElement) => {
            if (!wordElement) return;

            wordElement.style.removeProperty('opacity');
            wordElement.style.removeProperty('transform');
            wordElement.style.removeProperty('visibility');
            wordElement.querySelectorAll('.contact-question-flow__glyph, .contact-question-flow__space').forEach((glyph) => {
                glyph.style.removeProperty('opacity');
                glyph.style.removeProperty('transform');
                glyph.style.removeProperty('visibility');
            });
        };

        const setActiveWord = (wordIndex) => {
            const normalizedIndex = ((wordIndex % words.length) + words.length) % words.length;
            wordSlot.getAnimations?.({ subtree: true }).forEach((animation) => animation.cancel());
            wordSlot.textContent = '';
            activeWordElement = createWordElement(words[normalizedIndex]);
            wordSlot.appendChild(activeWordElement);
            activeWordIndex = normalizedIndex;
            sceneState.activeIndex = normalizedIndex;
            questionFlow.dataset.activeQuestion = words[normalizedIndex];
            return activeWordElement;
        };

        const setInitialWord = () => {
            setActiveWord(0);
            wordSlot.style.setProperty('--word-line-scale', '1');
        };

        setInitialWord();

        const canUseWebGL = () => {
            if (!window.WebGLRenderingContext) return false;

            try {
                const testCanvas = document.createElement('canvas');
                return Boolean(
                    testCanvas.getContext('webgl') ||
                    testCanvas.getContext('experimental-webgl')
                );
            } catch (error) {
                return false;
            }
        };

        let contactThreePromise = null;
        const loadContactThree = () => {
            if (!contactThreePromise) {
                contactThreePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);
            }
            return contactThreePromise;
        };

        let contactGsapPromise = null;
        const loadContactGsap = () => {
            if (window.gsap) return Promise.resolve(window.gsap);
            if (contactGsapPromise) return contactGsapPromise;

            contactGsapPromise = new Promise((resolve) => {
                let hasResolved = false;
                const finish = (value) => {
                    if (hasResolved) return;
                    hasResolved = true;
                    resolve(value || window.gsap || null);
                };

                const existingScript = document.querySelector('script[src*="gsap"]') || document.querySelector('script[data-contact-question-gsap]');
                if (existingScript) {
                    existingScript.addEventListener('load', () => finish(window.gsap || null), { once: true });
                    existingScript.addEventListener('error', () => finish(null), { once: true });
                    window.setTimeout(() => finish(window.gsap || null), 900);
                    return;
                }

                const script = document.createElement('script');
                script.src = '/assets/vendor/gsap-3.12.5.min.js';
                script.async = true;
                script.dataset.contactQuestionGsap = 'true';
                script.onload = () => finish(window.gsap || null);
                script.onerror = () => finish(null);
                document.head.appendChild(script);

                window.setTimeout(() => finish(window.gsap || null), 1000);
            });

            return contactGsapPromise;
        };

        const clearWordDelay = () => {
            if (!wordDelayCall) return;

            if (typeof wordDelayCall.kill === 'function') {
                wordDelayCall.kill();
            } else {
                window.clearTimeout(wordDelayCall);
                window.clearInterval(wordDelayCall);
            }

            wordDelayCall = null;
        };

        const clearWordCleanup = () => {
            if (!wordCleanupCall) return;
            window.clearTimeout(wordCleanupCall);
            wordCleanupCall = null;
        };

        const clearWordTimeline = () => {
            if (!wordTimeline) return;

            if (typeof wordTimeline.kill === 'function') {
                wordTimeline.kill();
            }

            wordTimeline = null;
        };

        const prepareNextWord = (nextIndex) => {
            clearWordCleanup();
            clearWordTimeline();

            isWordAnimating = true;
            const nextWord = setActiveWord(nextIndex);
            wordSlot.style.setProperty('--word-line-scale', '0');
            return nextWord;
        };

        const finishWordChange = (nextWord, nextIndex) => {
            clearWordCleanup();
            wordTimeline = null;
            isWordAnimating = false;

            if (nextWord.parentNode !== wordSlot) {
                nextWord = setActiveWord(nextIndex);
            }

            wordSlot.querySelectorAll('.contact-question-flow__word').forEach((wordElement) => {
                if (wordElement !== nextWord) {
                    wordElement.remove();
                }
            });
            cleanWordStyles(nextWord);
            activeWordElement = nextWord;
            activeWordIndex = nextIndex;
            questionFlow.dataset.activeQuestion = words[activeWordIndex];
            sceneState.activeIndex = activeWordIndex;
            sceneState.pulse = 0;
            wordSlot.style.setProperty('--word-line-scale', '1');
        };

        const animateNextWord = (contactGsap) => {
            if (!contactGsap) {
                animateNextWordFallback();
                return;
            }

            if (prefersReducedMotion || words.length < 2 || isWordAnimating || !isFlowVisible) {
                return;
            }

            const nextIndex = (activeWordIndex + 1) % words.length;
            const nextWord = prepareNextWord(nextIndex);
            const nextGlyphs = nextWord.querySelectorAll('.contact-question-flow__glyph, .contact-question-flow__space');

            contactGsap.killTweensOf(wordSlot);
            contactGsap.killTweensOf(nextWord);
            contactGsap.killTweensOf(nextGlyphs);
            contactGsap.set(nextWord, { yPercent: -82, autoAlpha: 0 });
            contactGsap.set(nextGlyphs, { yPercent: -28, autoAlpha: 0 });

            wordTimeline = contactGsap.timeline({
                defaults: { ease: 'power3.out' }
            });

            wordTimeline
                .to(wordSlot, {
                    '--word-line-scale': 0,
                    duration: 0.12,
                    ease: 'power2.out'
                }, 0)
                .to(nextWord, {
                    yPercent: 0,
                    autoAlpha: 1,
                    duration: 0.5,
                    clearProps: 'opacity,transform,visibility'
                }, 0.04)
                .to(nextGlyphs, {
                    yPercent: 0,
                    autoAlpha: 1,
                    duration: 0.42,
                    stagger: 0.014,
                    clearProps: 'opacity,transform,visibility'
                }, 0.08)
                .to(sceneState, {
                    pulse: 1,
                    activeIndex: nextIndex,
                    duration: 0.52,
                    ease: 'sine.out'
                }, 0.12)
                .to(wordSlot, {
                    '--word-line-scale': 1,
                    duration: 0.48
                }, 0.34)
                .to(sceneState, {
                    pulse: 0,
                    duration: 0.8,
                    ease: 'sine.inOut'
                }, 0.68);

            wordCleanupCall = window.setTimeout(() => {
                clearWordTimeline();
                finishWordChange(nextWord, nextIndex);
            }, 760);
        };

        const animateNextWordFallback = () => {
            if (prefersReducedMotion || words.length < 2 || isWordAnimating || !isFlowVisible) {
                return;
            }

            const nextIndex = (activeWordIndex + 1) % words.length;
            const nextWord = prepareNextWord(nextIndex);
            const nextGlyphs = nextWord.querySelectorAll('.contact-question-flow__glyph, .contact-question-flow__space');

            nextWord.style.transform = 'translate3d(0, -82%, 0)';
            nextWord.style.opacity = '0';
            nextGlyphs.forEach((glyph) => {
                glyph.style.transform = 'translate3d(0, -28%, 0)';
                glyph.style.opacity = '0';
            });

            const playFallbackFrame = () => {
                if (nextWord.animate) {
                    nextWord.animate([
                        { transform: 'translate3d(0, -82%, 0)', opacity: 0 },
                        { transform: 'translate3d(0, 0, 0)', opacity: 1 }
                    ], { duration: 500, easing: 'cubic-bezier(.22, 1, .36, 1)', fill: 'forwards' });
                } else {
                    nextWord.style.transform = 'translate3d(0, 0, 0)';
                    nextWord.style.opacity = '1';
                }

                nextGlyphs.forEach((glyph, index) => {
                    if (glyph.animate) {
                        glyph.animate([
                            { transform: 'translate3d(0, -28%, 0)', opacity: 0 },
                            { transform: 'translate3d(0, 0, 0)', opacity: 1 }
                        ], { duration: 420, delay: 80 + index * 14, easing: 'cubic-bezier(.22, 1, .36, 1)', fill: 'forwards' });
                    } else {
                        glyph.style.transform = 'translate3d(0, 0, 0)';
                        glyph.style.opacity = '1';
                    }
                });

                wordSlot.style.setProperty('--word-line-scale', '1');
                sceneState.pulse = 1;
                sceneState.activeIndex = nextIndex;
            };

            if (typeof window.requestAnimationFrame === 'function') {
                window.requestAnimationFrame(playFallbackFrame);
            } else {
                window.setTimeout(playFallbackFrame, 16);
            }

            wordCleanupCall = window.setTimeout(() => {
                finishWordChange(nextWord, nextIndex);
            }, 1100);
        };

        const startWordCycle = async () => {
            if (prefersReducedMotion || words.length < 2 || hasStartedWords || !isFlowVisible) return;

            const contactGsap = await loadContactGsap();
            if (hasStartedWords || !isFlowVisible) {
                return;
            }

            hasStartedWords = true;
            wordDelayCall = window.setInterval(() => {
                if (contactGsap) {
                    animateNextWord(contactGsap);
                    return;
                }

                animateNextWordFallback();
            }, wordCycleDelay);
        };

        const stopWordCycle = () => {
            clearWordDelay();
            clearWordCleanup();
            clearWordTimeline();
            isWordAnimating = false;
            wordSlot.getAnimations?.({ subtree: true }).forEach((animation) => animation.cancel());
            if (activeWordElement?.parentNode === wordSlot) {
                wordSlot.querySelectorAll('.contact-question-flow__word').forEach((wordElement) => {
                    if (wordElement !== activeWordElement) {
                        wordElement.remove();
                    }
                });
                cleanWordStyles(activeWordElement);
            } else {
                setActiveWord(activeWordIndex);
            }
            wordSlot.style.setProperty('--word-line-scale', '1');
            hasStartedWords = false;
        };

        let fallbackFrame = 0;
        let fallbackVisible = false;
        const renderFallbackQuestion = (time = 0) => {
            const context = canvas.getContext('2d');
            if (!context) return;

            const rect = canvas.getBoundingClientRect();
            const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
            const width = Math.max(1, Math.round(rect.width * ratio));
            const height = Math.max(1, Math.round(rect.height * ratio));

            if (canvas.width !== width || canvas.height !== height) {
                canvas.width = width;
                canvas.height = height;
            }

            context.setTransform(ratio, 0, 0, ratio, 0, 0);
            context.clearRect(0, 0, rect.width, rect.height);

            const pulse = prefersReducedMotion ? 0.35 : Math.sin(time * 0.0022) * 0.5 + 0.5;
            const centerX = rect.width * 0.54;
            const centerY = rect.height * 0.5;

            const wash = context.createRadialGradient(centerX, centerY, 10, centerX, centerY, Math.max(rect.width, rect.height) * 0.58);
            if (tropicNoirActive) {
                wash.addColorStop(0, 'rgba(242, 231, 207, 0.1)');
                wash.addColorStop(0.45, 'rgba(232, 176, 75, 0.1)');
                wash.addColorStop(1, 'rgba(255, 90, 60, 0)');
            } else {
                wash.addColorStop(0, 'rgba(255, 248, 240, 0.54)');
                wash.addColorStop(0.45, 'rgba(184, 135, 43, 0.13)');
                wash.addColorStop(1, 'rgba(201, 74, 53, 0)');
            }
            context.fillStyle = wash;
            context.fillRect(0, 0, rect.width, rect.height);

            const ribbons = tropicNoirActive
                ? [
                    ['#ff5a3c', 0.34, 5.2, 0.2],
                    ['#e8b04b', 0.26, 3.2, 0.55],
                    ['#f58042', 0.1, 2, 0.82]
                ]
                : [
                    ['#c94a35', 0.34, 5.2, 0.2],
                    ['#b8872b', 0.26, 3.2, 0.55],
                    ['#2a0f3f', 0.1, 2, 0.82]
                ];

            context.lineCap = 'round';
            ribbons.forEach(([color, alpha, lineWidth, offset], index) => {
                const wave = Math.sin(time * 0.0015 + Number(offset) * Math.PI) * (prefersReducedMotion ? 0 : rect.height * 0.035);
                context.beginPath();
                context.moveTo(rect.width * (0.08 + index * 0.04), rect.height * (0.68 - index * 0.1));
                context.bezierCurveTo(
                    rect.width * 0.28,
                    rect.height * (0.1 + Number(offset) * 0.22) + wave,
                    rect.width * 0.66,
                    rect.height * (0.88 - Number(offset) * 0.22) - wave,
                    rect.width * (0.92 - index * 0.06),
                    rect.height * (0.34 + index * 0.14)
                );
                context.strokeStyle = String(color);
                context.globalAlpha = Number(alpha) + pulse * 0.08;
                context.lineWidth = Number(lineWidth);
                context.stroke();
            });

            for (let index = 0; index < 12; index += 1) {
                const phase = (index / 12 + time * 0.00004) % 1;
                const x = rect.width * (0.16 + phase * 0.7);
                const y = rect.height * (0.34 + Math.sin(phase * Math.PI * 2 + index) * 0.22);
                context.beginPath();
                context.globalAlpha = 0.18 + pulse * 0.08;
                context.fillStyle = tropicNoirActive
                    ? (index % 3 === 0 ? '#e8b04b' : '#f58042')
                    : (index % 3 === 0 ? '#b8872b' : '#e36a43');
                context.arc(x, y, index % 3 === 0 ? 2.6 : 1.8, 0, Math.PI * 2);
                context.fill();
            }

            context.globalAlpha = 1;
        };

        const startFallbackQuestion = () => {
            if (fallbackFrame) return;

            questionFlow.classList.add('contact-question-flow--fallback');
            questionFlow.dataset.questionScene = 'fallback';
            fallbackVisible = true;

            const render = (time) => {
                renderFallbackQuestion(time);
                if (fallbackVisible && !prefersReducedMotion) {
                    fallbackFrame = window.requestAnimationFrame(render);
                }
            };

            if (prefersReducedMotion) {
                renderFallbackQuestion(0);
            } else {
                fallbackFrame = window.requestAnimationFrame(render);
            }
        };

        const stopFallbackQuestion = () => {
            fallbackVisible = false;
            if (fallbackFrame) {
                window.cancelAnimationFrame(fallbackFrame);
                fallbackFrame = 0;
            }
        };

        if (!canUseWebGL()) {
            startFallbackQuestion();
            return;
        }

        let hasBuiltScene = false;
        let renderer = null;
        let scene = null;
        let camera = null;
        let ribbonGroup = null;
        let particles = null;
        let ribbonMeshes = [];
        let glintMeshes = [];
        let animationFrame = 0;
        let isSceneVisible = false;
        const pointer = { x: 0, y: 0 };
        const pointerTarget = { x: 0, y: 0 };

        const resizeQuestionScene = () => {
            if (!renderer || !camera || !ribbonGroup) return;

            const width = Math.max(1, canvas.clientWidth);
            const height = Math.max(1, canvas.clientHeight);
            renderer.setSize(width, height, false);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();

            const scale = Math.min(1.1, Math.max(0.74, width / 520));
            ribbonGroup.scale.set(scale, scale, scale);
        };

        const startQuestionLoop = () => {
            if (animationFrame || !renderer || !scene || !camera || !ribbonGroup) return;
            if (prefersReducedMotion) {
                renderer.render(scene, camera);
                return;
            }

            isSceneVisible = true;
            const render = (time) => {
                pointer.x += (pointerTarget.x - pointer.x) * 0.045;
                pointer.y += (pointerTarget.y - pointer.y) * 0.045;

                const rhythm = time * 0.00052;
                const activePulse = sceneState.pulse || 0;
                ribbonGroup.rotation.x = pointer.y * 0.08;
                ribbonGroup.rotation.y = pointer.x * 0.08;
                ribbonGroup.rotation.z = Math.sin(rhythm) * 0.018;

                ribbonMeshes.forEach((mesh, index) => {
                    const baseOpacity = mesh.userData.baseOpacity || 0.16;
                    mesh.rotation.z = Math.sin(rhythm * 1.05 + index) * 0.018;
                    mesh.position.y = Math.sin(rhythm * 1.4 + index) * 0.035;
                    mesh.material.opacity = Math.max(0.025, baseOpacity + activePulse * 0.08 + Math.sin(rhythm * 1.6 + index) * 0.018);
                });

                glintMeshes.forEach((mesh, index) => {
                    const curve = mesh.userData.curve;
                    const progress = (mesh.userData.seed + time * 0.000022) % 1;
                    const point = curve.getPointAt(progress);
                    mesh.position.set(point.x, point.y, point.z + 0.08 + Math.sin(rhythm * 2 + index) * 0.02);
                    mesh.scale.setScalar((mesh.userData.baseScale || 1) * (1 + activePulse * 0.25 + Math.sin(rhythm * 2.2 + index) * 0.06));
                });

                if (particles) {
                    const positionAttribute = particles.geometry.getAttribute('position');
                    const seeds = particles.userData.seeds || [];
                    const curves = particles.userData.curves || [];
                    if (positionAttribute && seeds.length && curves.length) {
                        for (let index = 0; index < seeds.length; index += 1) {
                            const curve = curves[index % curves.length];
                            const point = curve.getPointAt((seeds[index] + time * 0.000014) % 1);
                            const offset = index * 3;
                            positionAttribute.array[offset] = point.x;
                            positionAttribute.array[offset + 1] = point.y;
                            positionAttribute.array[offset + 2] = point.z + 0.05 + Math.sin(rhythm * 1.8 + index) * 0.045;
                        }
                        positionAttribute.needsUpdate = true;
                    }
                }

                renderer.render(scene, camera);

                if (isSceneVisible) {
                    animationFrame = window.requestAnimationFrame(render);
                }
            };

            animationFrame = window.requestAnimationFrame(render);
        };

        const stopQuestionLoop = () => {
            isSceneVisible = false;
            if (animationFrame) {
                window.cancelAnimationFrame(animationFrame);
                animationFrame = 0;
            }
            stopFallbackQuestion();
        };

        const buildQuestionScene = async () => {
            if (hasBuiltScene) return;
            hasBuiltScene = true;

            const THREE = await loadContactThree();
            if (!THREE) {
                startFallbackQuestion();
                return;
            }

            try {
                renderer = new THREE.WebGLRenderer({
                    canvas,
                    alpha: true,
                    antialias: window.innerWidth >= 768,
                    preserveDrawingBuffer: false,
                    powerPreference: 'low-power'
                });
            } catch (error) {
                startFallbackQuestion();
                return;
            }

            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.setClearColor(0x000000, 0);

            const scenePalette = tropicNoirActive
                ? { floor: 0xe8b04b, ribbonA: 0xff5a3c, ribbonB: 0xe8b04b, ribbonC: 0xf58042, glintAccent: 0xe8b04b, glintLight: 0xf2e7cf, particle: 0xf58042 }
                : { floor: 0xb8872b, ribbonA: 0xc94a35, ribbonB: 0xb8872b, ribbonC: 0xe36a43, glintAccent: 0xb8872b, glintLight: 0xfff8f0, particle: 0xe36a43 };

            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
            camera.position.set(0, 0, 6.4);

            ribbonGroup = new THREE.Group();
            scene.add(ribbonGroup);

            const floorGeometry = new THREE.RingGeometry(1.05, 1.08, 96);
            const floorMaterial = new THREE.MeshBasicMaterial({
                color: scenePalette.floor,
                transparent: true,
                opacity: 0.14,
                depthWrite: false
            });
            const floor = new THREE.Mesh(floorGeometry, floorMaterial);
            floor.scale.set(1.7, 0.52, 1);
            floor.position.set(0, -0.64, -0.22);
            floor.rotation.z = -0.05;
            ribbonGroup.add(floor);

            const ribbonDefinitions = [
                {
                    color: scenePalette.ribbonA,
                    opacity: 0.24,
                    radius: 0.024,
                    curve: new THREE.CubicBezierCurve3(
                        new THREE.Vector3(-2.1, -0.82, 0.02),
                        new THREE.Vector3(-1.14, 1.14, 0.1),
                        new THREE.Vector3(1.16, 0.9, 0.1),
                        new THREE.Vector3(2.05, -0.46, 0.02)
                    )
                },
                {
                    color: scenePalette.ribbonB,
                    opacity: 0.2,
                    radius: 0.018,
                    curve: new THREE.CubicBezierCurve3(
                        new THREE.Vector3(-1.9, 0.52, 0.03),
                        new THREE.Vector3(-0.9, -1.08, 0.08),
                        new THREE.Vector3(1.25, -0.8, 0.08),
                        new THREE.Vector3(1.94, 0.68, 0.03)
                    )
                },
                {
                    color: scenePalette.ribbonC,
                    opacity: 0.14,
                    radius: 0.014,
                    curve: new THREE.CubicBezierCurve3(
                        new THREE.Vector3(-1.48, -0.52, 0.0),
                        new THREE.Vector3(-0.44, 0.46, 0.05),
                        new THREE.Vector3(0.52, 0.38, 0.05),
                        new THREE.Vector3(1.5, -0.58, 0.0)
                    )
                }
            ];

            ribbonDefinitions.forEach((definition) => {
                const glowGeometry = new THREE.TubeGeometry(definition.curve, 72, definition.radius * 3.2, 8, false);
                const glowMaterial = new THREE.MeshBasicMaterial({
                    color: definition.color,
                    transparent: true,
                    opacity: definition.opacity * 0.18,
                    depthWrite: false
                });
                const glow = new THREE.Mesh(glowGeometry, glowMaterial);
                glow.userData.baseOpacity = definition.opacity * 0.18;
                ribbonMeshes.push(glow);
                ribbonGroup.add(glow);

                const ribbonGeometry = new THREE.TubeGeometry(definition.curve, 96, definition.radius, 8, false);
                const ribbonMaterial = new THREE.MeshBasicMaterial({
                    color: definition.color,
                    transparent: true,
                    opacity: definition.opacity,
                    depthWrite: false
                });
                const ribbon = new THREE.Mesh(ribbonGeometry, ribbonMaterial);
                ribbon.userData.baseOpacity = definition.opacity;
                ribbonMeshes.push(ribbon);
                ribbonGroup.add(ribbon);
            });

            const glintGeometry = new THREE.CircleGeometry(0.035, 20);
            const glintCount = window.innerWidth < 768 ? 8 : 12;
            for (let index = 0; index < glintCount; index += 1) {
                const curve = ribbonDefinitions[index % ribbonDefinitions.length].curve;
                const seed = (index / glintCount + (index % 2) * 0.07) % 1;
                const point = curve.getPointAt(seed);
                const material = new THREE.MeshBasicMaterial({
                    color: index % 3 === 0 ? scenePalette.glintAccent : scenePalette.glintLight,
                    transparent: true,
                    opacity: index % 3 === 0 ? 0.36 : 0.28,
                    depthWrite: false
                });
                const glint = new THREE.Mesh(glintGeometry, material);
                glint.position.copy(point);
                glint.userData.curve = curve;
                glint.userData.seed = seed;
                glint.userData.baseScale = index % 3 === 0 ? 1.15 : 0.85;
                glintMeshes.push(glint);
                ribbonGroup.add(glint);
            }

            const particleCount = window.innerWidth < 768 ? 14 : 28;
            const particlePositions = new Float32Array(particleCount * 3);
            const particleSeeds = [];
            for (let index = 0; index < particleCount; index += 1) {
                const curve = ribbonDefinitions[index % ribbonDefinitions.length].curve;
                const seed = (index / particleCount + (index % 4) * 0.06) % 1;
                const point = curve.getPointAt(seed);
                const offset = index * 3;
                particlePositions[offset] = point.x;
                particlePositions[offset + 1] = point.y;
                particlePositions[offset + 2] = point.z + 0.06;
                particleSeeds.push(seed);
            }

            const particleGeometry = new THREE.BufferGeometry();
            particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
            const particleMaterial = new THREE.PointsMaterial({
                color: scenePalette.particle,
                size: window.innerWidth < 768 ? 0.026 : 0.032,
                transparent: true,
                opacity: 0.2,
                depthWrite: false
            });
            particles = new THREE.Points(particleGeometry, particleMaterial);
            particles.userData.curves = ribbonDefinitions.map((definition) => definition.curve);
            particles.userData.seeds = particleSeeds;
            ribbonGroup.add(particles);

            resizeQuestionScene();
            if (isFlowVisible) {
                startQuestionLoop();
            }
            questionFlow.dataset.questionScene = prefersReducedMotion ? 'static' : 'ready';
        };

        questionFlow.addEventListener('pointermove', (event) => {
            if (window.innerWidth < 768) return;
            const rect = questionFlow.getBoundingClientRect();
            pointerTarget.x = ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
            pointerTarget.y = -(((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2);
        }, { passive: true });

        questionFlow.addEventListener('pointerleave', () => {
            pointerTarget.x = 0;
            pointerTarget.y = 0;
        });

        window.addEventListener('resize', resizeQuestionScene, { passive: true });

        const isQuestionNearViewport = () => {
            const rect = questionFlow.getBoundingClientRect();
            return rect.top < window.innerHeight + 320 && rect.bottom > -320;
        };

        const startQuestionFlow = () => {
            isFlowVisible = true;
            if (!isQuestionNearViewport()) return;
            buildQuestionScene();
            startQuestionLoop();
            startWordCycle();
        };

        const stopQuestionFlow = () => {
            if (isQuestionNearViewport()) return;

            isFlowVisible = false;
            stopWordCycle();
            stopQuestionLoop();
        };

        window.addEventListener('scroll', () => {
            if (isQuestionNearViewport()) {
                startQuestionFlow();
            } else {
                stopQuestionFlow();
            }
        }, { passive: true });

        window.setTimeout(startQuestionFlow, 420);

        if ('IntersectionObserver' in window) {
            const questionObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting || isQuestionNearViewport()) {
                        startQuestionFlow();
                    } else {
                        stopQuestionFlow();
                    }
                });
            }, {
                rootMargin: '260px 0px',
                threshold: 0.01
            });
            questionObserver.observe(questionFlow);
        } else {
            startQuestionFlow();
        }
    };

    enhanceContactQuestionFlow();

    const enhanceFooterEntrance = () => {
        const footer = document.querySelector('.main-footer');
        if (!footer || prefersReducedMotion) return;

        const columns = Array.from(footer.querySelectorAll('.footer-grid > .footer-col'));
        if (columns.length < 3) return;

        const [leftColumn, centerColumn, rightColumn] = columns;
        const footerMap = footer.querySelector('.footer-map-full');
        const footerBottom = footer.querySelector('.footer-bottom');
        const motionTargets = [leftColumn, centerColumn, rightColumn, footerMap, footerBottom].filter(Boolean);
        let hasPlayed = false;
        let footerGsapPromise = null;

        const loadFooterGsap = () => {
            if (window.gsap) return Promise.resolve(window.gsap);
            if (footerGsapPromise) return footerGsapPromise;

            footerGsapPromise = new Promise((resolve) => {
                const existingScript = document.querySelector('script[data-footer-gsap]');
                if (existingScript) {
                    existingScript.addEventListener('load', () => resolve(window.gsap || null), { once: true });
                    existingScript.addEventListener('error', () => resolve(null), { once: true });
                    return;
                }

                const script = document.createElement('script');
                script.src = '/assets/vendor/gsap-3.12.5.min.js';
                script.async = true;
                script.dataset.footerGsap = 'true';
                script.onload = () => resolve(window.gsap || null);
                script.onerror = () => resolve(null);
                document.head.appendChild(script);

                window.setTimeout(() => resolve(window.gsap || null), 900);
            });

            return footerGsapPromise;
        };

        const clearFooterMotion = () => {
            footer.classList.remove('is-footer-motion-ready');
            footer.style.removeProperty('--footer-accent-scale');
            motionTargets.forEach((target) => {
                target.style.removeProperty('opacity');
                target.style.removeProperty('visibility');
                target.style.removeProperty('transform');
                target.style.removeProperty('will-change');
            });
        };

        const showFooterImmediately = () => {
            hasPlayed = true;
            clearFooterMotion();
        };

        const playNativeFooterReveal = () => {
            if (!Element.prototype.animate) {
                showFooterImmediately();
                return;
            }

            const ease = 'cubic-bezier(0.22, 1, 0.36, 1)';
            const animations = [
                leftColumn.animate([
                    { opacity: 0, transform: 'translate3d(-68px, 0, 0)' },
                    { opacity: 1, transform: 'translate3d(0, 0, 0)' }
                ], { duration: 900, easing: ease, delay: 80, fill: 'forwards' }),
                centerColumn.animate([
                    { opacity: 0, transform: 'translate3d(0, -54px, 0)' },
                    { opacity: 1, transform: 'translate3d(0, 0, 0)' }
                ], { duration: 920, easing: ease, delay: 0, fill: 'forwards' }),
                rightColumn.animate([
                    { opacity: 0, transform: 'translate3d(68px, 0, 0)' },
                    { opacity: 1, transform: 'translate3d(0, 0, 0)' }
                ], { duration: 900, easing: ease, delay: 140, fill: 'forwards' })
            ];

            if (footerMap) {
                animations.push(footerMap.animate([
                    { opacity: 0, transform: 'translate3d(0, 26px, 0)' },
                    { opacity: 1, transform: 'translate3d(0, 0, 0)' }
                ], { duration: 760, easing: ease, delay: 480, fill: 'forwards' }));
            }

            if (footerBottom) {
                animations.push(footerBottom.animate([
                    { opacity: 0, transform: 'translate3d(0, 18px, 0)' },
                    { opacity: 1, transform: 'translate3d(0, 0, 0)' }
                ], { duration: 640, easing: ease, delay: 620, fill: 'forwards' }));
            }

            Promise.all(animations.map(animation => animation.finished.catch(() => {})))
                .then(() => {
                    clearFooterMotion();
                    animations.forEach(animation => animation.cancel());
                });
        };

        const playGsapFooterReveal = (footerGsap) => {
            const footerTimeline = footerGsap.timeline({
                defaults: {
                    duration: 0.9,
                    ease: 'power3.out'
                },
                onComplete: () => {
                    footerGsap.set(motionTargets, { clearProps: 'opacity,visibility,transform,willChange' });
                    clearFooterMotion();
                }
            });

            footerTimeline
                .fromTo(footer, {
                    '--footer-accent-scale': 0
                }, {
                    '--footer-accent-scale': 1,
                    duration: 0.72,
                    ease: 'power2.out'
                }, 0)
                .fromTo(centerColumn, {
                    autoAlpha: 0,
                    y: -54,
                    willChange: 'transform, opacity'
                }, {
                    autoAlpha: 1,
                    y: 0
                }, 0.05)
                .fromTo(leftColumn, {
                    autoAlpha: 0,
                    x: -68,
                    willChange: 'transform, opacity'
                }, {
                    autoAlpha: 1,
                    x: 0
                }, 0.14)
                .fromTo(rightColumn, {
                    autoAlpha: 0,
                    x: 68,
                    willChange: 'transform, opacity'
                }, {
                    autoAlpha: 1,
                    x: 0
                }, 0.2);

            if (footerMap) {
                footerTimeline.fromTo(footerMap, {
                    autoAlpha: 0,
                    y: 26,
                    willChange: 'transform, opacity'
                }, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.74
                }, 0.56);
            }

            if (footerBottom) {
                footerTimeline.fromTo(footerBottom, {
                    autoAlpha: 0,
                    y: 18,
                    willChange: 'transform, opacity'
                }, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.58
                }, 0.68);
            }
        };

        const playFooterReveal = () => {
            if (hasPlayed) return;
            hasPlayed = true;
            loadFooterGsap().then((footerGsap) => {
                if (footerGsap) {
                    playGsapFooterReveal(footerGsap);
                    return;
                }

                playNativeFooterReveal();
            });
        };

        footer.classList.add('is-footer-motion-ready');
        footer.style.setProperty('--footer-accent-scale', '0');

        if ('IntersectionObserver' in window) {
            const footerObserver = new IntersectionObserver((entries) => {
                if (entries.some(entry => entry.isIntersecting)) {
                    footerObserver.disconnect();
                    playFooterReveal();
                }
            }, {
                threshold: 0.16,
                rootMargin: '220px 0px -8% 0px'
            });

            footerObserver.observe(footer);
        } else {
            playFooterReveal();
        }
    };

    enhanceFooterEntrance();

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }

    // Close menu when clicking links
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            if (navLinks) navLinks.classList.remove('active');
            if (mobileMenuBtn) mobileMenuBtn.classList.remove('active');
        });
    });

    // Mobile Dropdown Toggle in nav-links
    const dropBtns = document.querySelectorAll('.dropbtn');
    dropBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (window.innerWidth < 1080) {
                e.preventDefault();
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

// The Tropic Noir journal (EN blog.html) carries body.blog-page and gets the
// animated FLIP filter plus the editorial grid; every other page that owns
// .filter-btn (de/blog.html) keeps the original instant toggle untouched.
const isNoirBlog = document.body.classList.contains('blog-page')
    && Boolean(document.querySelector('link[href*="tropic-noir"]'));
const blogPrefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const blogGrid = document.querySelector('.blog-grid-modern');

if (filterBtns.length > 0 && blogCards.length > 0) {
    const isCardShown = (card) => card.style.display !== 'none';
    const cardMatches = (card, filterValue) =>
        filterValue === 'all' || card.getAttribute('data-category') === filterValue;

    const setFilteredState = (filterValue) => {
        if (blogGrid) blogGrid.classList.toggle('is-filtered', filterValue !== 'all');
    };

    // Every filter application bumps the run id; async callbacks from an
    // earlier run (a killed stagger master still fires onComplete) check it
    // and stand down instead of hiding cards the newer run just showed.
    let filterRunId = 0;

    const applyFilterInstant = (filterValue) => {
        filterRunId += 1;
        setFilteredState(filterValue);
        blogCards.forEach(card => {
            if (cardMatches(card, filterValue)) {
                // The Noir grid decides card display in CSS (flex tiles,
                // grid spotlights); inline flex would override it.
                card.style.display = isNoirBlog ? '' : 'flex';
                setTimeout(() => card.style.opacity = '1', 10);
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        });
    };

    let filterAnimating = false;

    const applyFilterAnimated = (filterValue) => {
        const gsapRef = window.gsap;
        if (filterAnimating) {
            // A run is still in flight: land everything instantly instead of
            // stacking timelines on half-moved cards.
            gsapRef.killTweensOf(Array.from(blogCards));
            gsapRef.set(Array.from(blogCards), { clearProps: 'opacity,visibility,transform' });
            applyFilterInstant(filterValue);
            filterAnimating = false;
            return;
        }

        const cards = Array.from(blogCards);
        const leaving = cards.filter(card => isCardShown(card) && !cardMatches(card, filterValue));
        const staying = cards.filter(card => isCardShown(card) && cardMatches(card, filterValue));
        const entering = cards.filter(card => !isCardShown(card) && cardMatches(card, filterValue));

        filterAnimating = true;
        gsapRef.killTweensOf(cards);
        const runId = ++filterRunId;

        const settle = () => {
            if (runId !== filterRunId) {
                filterAnimating = false;
                return;
            }
            // FLIP: measure where the surviving cards were, relayout, then
            // glide them from the old position (transform/opacity only).
            const firstRects = new Map(staying.map(card => [card, card.getBoundingClientRect()]));

            leaving.forEach(card => {
                card.style.display = 'none';
                card.style.opacity = '0';
            });
            entering.forEach(card => {
                card.style.display = '';
                card.style.opacity = '1';
            });
            setFilteredState(filterValue);

            let remaining = staying.length + entering.length;
            const finishOne = () => {
                remaining -= 1;
                if (remaining <= 0) filterAnimating = false;
            };
            if (remaining === 0) filterAnimating = false;

            staying.forEach(card => {
                const first = firstRects.get(card);
                const last = card.getBoundingClientRect();
                const dx = first.left - last.left;
                const dy = first.top - last.top;
                if (Math.abs(dx) < 1 && Math.abs(dy) < 1) {
                    finishOne();
                    return;
                }
                gsapRef.fromTo(card, { x: dx, y: dy }, {
                    x: 0,
                    y: 0,
                    duration: 0.5,
                    ease: 'power3.out',
                    clearProps: 'transform',
                    onComplete: finishOne
                });
            });

            entering.forEach((card, index) => {
                gsapRef.fromTo(card, { autoAlpha: 0, y: 14 }, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.45,
                    ease: 'power3.out',
                    delay: 0.05 + index * 0.03,
                    clearProps: 'opacity,visibility,transform',
                    onComplete: finishOne
                });
            });
        };

        if (leaving.length > 0) {
            gsapRef.to(leaving, {
                autoAlpha: 0,
                y: 10,
                duration: 0.2,
                ease: 'power2.in',
                stagger: 0.015,
                onComplete: settle
            });
        } else {
            settle();
        }
    };

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 1. Reflect the pressed state on the rail
            filterBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');

            // 2. Get filter value
            const filterValue = btn.getAttribute('data-filter');

            // 3. Filter cards (animated path only on the Noir journal)
            if (isNoirBlog && window.gsap && !blogPrefersReducedMotion) {
                applyFilterAnimated(filterValue);
            } else {
                applyFilterInstant(filterValue);
            }

            // 4. Let listeners (featured shader) hear the page turn
            document.dispatchEvent(new CustomEvent('blog:filter', { detail: { filter: filterValue } }));
        });
    });
}

/* BLOG PAGE — Tropic Noir journal enhancements (EN blog.html only) */
const enhanceBlogNoir = () => {
    if (!isNoirBlog) return;

    const gsapRef = window.gsap;
    const reduceMotion = blogPrefersReducedMotion;

    const observeOnce = (target, onEnter, options) => {
        if (!('IntersectionObserver' in window)) {
            onEnter();
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            if (entries.some(entry => entry.isIntersecting)) {
                observer.disconnect();
                onEnter();
            }
        }, options);
        observer.observe(target);
    };

    // Sticky filter shelf: strengthen the hairline once it is pinned.
    const shelf = document.querySelector('[data-blog-filter-shelf]');
    if (shelf && 'IntersectionObserver' in window) {
        const sentinel = document.createElement('div');
        sentinel.setAttribute('aria-hidden', 'true');
        shelf.parentNode.insertBefore(sentinel, shelf);
        new IntersectionObserver(([entry]) => {
            shelf.classList.toggle('is-stuck', !entry.isIntersecting);
        }).observe(sentinel);
    }

    // Category counts + masthead ledger from the JSON mirror of the grid.
    // The DOM stays the source of truth: on any count mismatch we warn and
    // render nothing rather than show wrong numbers.
    fetch('/assets/data/blog-posts.json')
        .then(response => (response.ok ? response.json() : null))
        .then(data => {
            if (!data || !Array.isArray(data.posts) || !data.categories) return;

            const jsonCounts = {};
            data.posts.forEach(post => {
                jsonCounts[post.category] = (jsonCounts[post.category] || 0) + 1;
            });

            const domTotal = document.querySelectorAll('article[data-category]').length;
            const parityHolds = data.posts.length === domTotal
                && Object.keys(data.categories).every(slug =>
                    (jsonCounts[slug] || 0) ===
                    document.querySelectorAll('article[data-category="' + slug + '"]').length);

            if (!parityHolds) {
                console.warn('blog-posts.json is out of sync with the blog listing; skipping counts.');
                return;
            }

            filterBtns.forEach(btn => {
                const filterValue = btn.getAttribute('data-filter');
                const count = filterValue === 'all' ? data.posts.length : (jsonCounts[filterValue] || 0);
                const chip = document.createElement('span');
                chip.className = 'filter-btn__count';
                chip.setAttribute('aria-hidden', 'true');
                chip.textContent = String(count);
                btn.appendChild(chip);
            });

            const ledger = document.querySelector('[data-blog-ledger]');
            if (ledger) {
                Object.keys(data.categories).forEach(slug => {
                    const target = document.querySelector('.filter-btn[data-filter="' + slug + '"]');
                    if (!target) return;
                    const item = document.createElement('li');
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'blog-masthead__ledger-btn';
                    button.innerHTML = '<span class="blog-masthead__ledger-count">'
                        + (jsonCounts[slug] || 0) + '</span><span>' + data.categories[slug] + '</span>';
                    button.addEventListener('click', () => {
                        target.click();
                        const gridSection = document.querySelector('.blog-container');
                        if (gridSection) {
                            gridSection.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
                        }
                    });
                    item.appendChild(button);
                    ledger.appendChild(item);
                });
            }
        })
        .catch(() => { /* enhancement only; the static page stands */ });

    if (!gsapRef || reduceMotion) return;

    // Masthead intro: kicker leads, the title answers, the underline draws
    // its three steps, then the featured panel rises. Hidden states are set
    // from JS only, so the masthead is fully visible without JavaScript.
    const kicker = document.querySelector('[data-masthead-kicker]');
    const title = document.querySelector('[data-masthead-title]');
    const dek = document.querySelector('[data-masthead-dek]');
    const ledgerList = document.querySelector('[data-blog-ledger]');
    const feature = document.querySelector('[data-blog-feature]');

    if (title) {
        const intro = gsapRef.timeline({ defaults: { ease: 'power3.out' } });
        gsapRef.set(title, { '--title-underline-scale': 0 });
        if (kicker) intro.from(kicker, { autoAlpha: 0, y: 12, duration: 0.5 });
        intro.from(title, { autoAlpha: 0, y: 18, duration: 0.6 }, '-=0.25');
        intro.to(title, {
            keyframes: [
                { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
                { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
                { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
                { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
            ]
        }, '-=0.2');
        if (dek) intro.from(dek, { autoAlpha: 0, y: 14, duration: 0.5 }, '-=0.45');
        if (ledgerList) intro.from(ledgerList, { autoAlpha: 0, y: 12, duration: 0.45 }, '-=0.3');
        if (feature) intro.from(feature, { autoAlpha: 0, y: 22, duration: 0.65 }, '-=0.4');
        intro.set([kicker, title, dek, ledgerList, feature].filter(Boolean), {
            clearProps: 'opacity,visibility,transform'
        });
    }

    // Dancing underline for the grid heading (same recipe as the homepage).
    gsapRef.utils.toArray('body.blog-page .section-title-modern').forEach((heading) => {
        gsapRef.set(heading, { '--title-underline-scale': 0 });
        observeOnce(heading, () => {
            gsapRef.to(heading, {
                keyframes: [
                    { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
                    { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
                    { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
                    { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
                ]
            });
        }, { threshold: 0.4, rootMargin: '0px 0px -10% 0px' });
    });

    // Card reveals on scroll. Disconnected on the first filter click so the
    // FLIP owns every inline style from then on.
    if ('IntersectionObserver' in window && blogGrid) {
        const cards = Array.from(blogGrid.querySelectorAll('.modern-card'));
        gsapRef.set(cards, { autoAlpha: 0, y: 16 });
        let revealIndex = 0;
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                revealObserver.unobserve(entry.target);
                gsapRef.to(entry.target, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.55,
                    ease: 'power3.out',
                    delay: (revealIndex++ % 3) * 0.08,
                    clearProps: 'opacity,visibility,transform'
                });
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
        cards.forEach(card => revealObserver.observe(card));

        document.addEventListener('blog:filter', () => {
            revealObserver.disconnect();
            gsapRef.killTweensOf(cards);
            gsapRef.set(cards, { clearProps: 'opacity,visibility,transform' });
        }, { once: true });
    }
};

enhanceBlogNoir();

/* BEGINNER GUIDE — Tropic Noir field manual (EN beginner-guide.html only).
   The scroll spy and the sticky-shelf hairline are functional and run
   without GSAP and under reduced motion; everything below the gate is
   entrance choreography with hidden states set from JS only. */
const enhanceGuidePage = () => {
    if (!document.body.classList.contains('guide-page')) return;
    if (!document.querySelector('link[href*="tropic-noir"]')) return;

    const gsapRef = window.gsap;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Count-in scroll spy: light the rail chapter that is on the floor.
    const railLinks = Array.from(document.querySelectorAll('.guide-rail__link'));
    const chapters = railLinks
        .map(link => document.querySelector(link.getAttribute('href')))
        .filter(Boolean);
    const rail = document.querySelector('[data-guide-rail]');

    if ('IntersectionObserver' in window && railLinks.length && chapters.length) {
        const setActive = (id) => {
            railLinks.forEach(link => {
                const isActive = link.getAttribute('href') === '#' + id;
                link.classList.toggle('is-active', isActive);
                if (isActive && rail && window.matchMedia('(max-width: 1080px)').matches) {
                    link.scrollIntoView({
                        block: 'nearest',
                        inline: 'center',
                        behavior: reduceMotion ? 'auto' : 'smooth'
                    });
                }
            });
        };
        const spy = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) setActive(entry.target.id);
            });
        }, { rootMargin: '-100px 0px -60% 0px' });
        chapters.forEach(chapter => spy.observe(chapter));
    }

    // 2. Shelf hairline: strengthen once the rail is pinned (mobile shelf).
    //    The sentinel sits BEFORE the shell grid, not inside it, so it does
    //    not occupy the rail's 232px grid column.
    const shell = document.querySelector('.guide-shell');
    if (rail && shell && 'IntersectionObserver' in window) {
        const sentinel = document.createElement('div');
        sentinel.setAttribute('aria-hidden', 'true');
        shell.parentNode.insertBefore(sentinel, shell);
        new IntersectionObserver(([entry]) => {
            rail.classList.toggle('is-stuck', !entry.isIntersecting);
        }).observe(sentinel);
    }

    if (!gsapRef || reduceMotion) return;

    const observeOnce = (target, onEnter, options) => {
        if (!('IntersectionObserver' in window)) {
            onEnter();
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            if (entries.some(entry => entry.isIntersecting)) {
                observer.disconnect();
                onEnter();
            }
        }, options);
        observer.observe(target);
    };

    const underlineKeyframes = [
        { '--title-underline-scale': 0.33, duration: 0.18, ease: 'power2.out' },
        { '--title-underline-scale': 0.66, duration: 0.18, ease: 'power2.out' },
        { '--title-underline-scale': 1.04, duration: 0.18, ease: 'power2.out' },
        { '--title-underline-scale': 1, duration: 0.24, ease: 'expo.out' }
    ];

    // 3. Masthead intro: kicker leads, the title answers, the underline
    //    draws its three steps, then the photo steps in.
    const kicker = document.querySelector('[data-guide-kicker]');
    const title = document.querySelector('[data-guide-title]');
    const dek = document.querySelector('[data-guide-dek]');
    const assurance = document.querySelector('[data-guide-assurance]');
    const figure = document.querySelector('[data-guide-figure]');

    if (title) {
        const intro = gsapRef.timeline({ defaults: { ease: 'power3.out' } });
        gsapRef.set(title, { '--title-underline-scale': 0 });
        if (kicker) intro.from(kicker, { autoAlpha: 0, y: 12, duration: 0.5 });
        intro.from(title, { autoAlpha: 0, y: 18, duration: 0.6 }, '-=0.25');
        intro.to(title, { keyframes: underlineKeyframes }, '-=0.2');
        if (dek) intro.from(dek, { autoAlpha: 0, y: 14, duration: 0.5 }, '-=0.45');
        if (assurance) intro.from(assurance, { autoAlpha: 0, y: 12, duration: 0.45 }, '-=0.3');
        if (figure) intro.from(figure, { autoAlpha: 0, y: 22, duration: 0.65 }, '-=0.4');
        intro.set([kicker, title, dek, assurance, figure].filter(Boolean), {
            clearProps: 'opacity,visibility,transform'
        });
    }

    // 4. Chapter choreography: the header leads, the cards answer with a
    //    1-2-3-tap stagger (a breath after every fourth item).
    const beatStagger = (index) => 0.07 * index + Math.floor(index / 4) * 0.07;

    document.querySelectorAll('.guide-chapter').forEach((chapter) => {
        const heading = chapter.querySelector('.guide-chapter__title');
        const lead = Array.from(chapter.querySelectorAll('.guide-chapter__header > *'));
        const follow = Array.from(chapter.querySelectorAll(
            '.guide-card, .guide-step, .guide-mirror__half, .guide-rules'
        ));

        if (heading) gsapRef.set(heading, { '--title-underline-scale': 0 });
        if (lead.length) gsapRef.set(lead, { autoAlpha: 0, y: 16 });
        if (follow.length) gsapRef.set(follow, { autoAlpha: 0, y: 18 });

        observeOnce(chapter, () => {
            const beat = gsapRef.timeline({ defaults: { ease: 'power3.out' } });
            if (lead.length) {
                beat.to(lead, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.55,
                    stagger: 0.09,
                    clearProps: 'opacity,visibility,transform'
                });
            }
            if (heading) beat.to(heading, { keyframes: underlineKeyframes }, '-=0.3');
            if (follow.length) {
                beat.to(follow, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.5,
                    stagger: beatStagger,
                    clearProps: 'opacity,visibility,transform'
                }, '-=0.35');
            }
        }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    });

    // 5. Offramp: one quiet fade-up when the close arrives.
    const offramp = document.querySelector('[data-guide-offramp]');
    if (offramp) {
        gsapRef.set(offramp, { autoAlpha: 0, y: 16 });
        observeOnce(offramp, () => {
            gsapRef.to(offramp, {
                autoAlpha: 1,
                y: 0,
                duration: 0.55,
                ease: 'power3.out',
                clearProps: 'opacity,visibility,transform'
            });
        }, { threshold: 0.2 });
    }
};
enhanceGuidePage();

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

    // Reviews marquee: duplicate each rail's cards once so the slow
    // horizontal drift can loop seamlessly. Clones are decorative (hidden
    // from assistive tech, and display:none outside the marquee viewport).
    document.querySelectorAll('.reviews-rail__track').forEach((track) => {
        if (track.dataset.marqueeCloned) return;
        Array.from(track.children).forEach((card) => {
            const clone = card.cloneNode(true);
            clone.classList.add('review-card--clone');
            clone.setAttribute('aria-hidden', 'true');
            track.appendChild(clone);
        });
        track.dataset.marqueeCloned = 'true';
    });

    // Mobile swipe progress: slim gold bar under the reviews row. Injected
    // here (progressive enhancement — no JS, no bar); CSS displays it only
    // in the <=700px layout where .reviews-grid actually scrolls.
    document.querySelectorAll('.reviews-showcase').forEach((wrapper) => {
        const grid = wrapper.querySelector('.reviews-grid');
        if (!grid || wrapper.querySelector('.reviews-progress')) return;

        const bar = document.createElement('div');
        bar.className = 'reviews-progress';
        bar.setAttribute('aria-hidden', 'true');
        const thumb = document.createElement('span');
        thumb.className = 'reviews-progress__thumb';
        bar.appendChild(thumb);
        wrapper.appendChild(bar);

        let ticking = false;
        const update = () => {
            ticking = false;
            const maxScroll = grid.scrollWidth - grid.clientWidth;
            if (maxScroll <= 0) { bar.classList.remove('is-active'); return; }
            bar.classList.add('is-active');
            thumb.style.width = (grid.clientWidth / grid.scrollWidth * 100) + '%';
            const p = Math.min(1, Math.max(0, grid.scrollLeft / maxScroll));
            thumb.style.transform =
                'translateX(' + (p * (bar.clientWidth - thumb.offsetWidth)) + 'px)';
        };
        const queue = () => {
            if (!ticking) { ticking = true; requestAnimationFrame(update); }
        };
        grid.addEventListener('scroll', queue, { passive: true });
        window.addEventListener('resize', queue);
        update();
    });
});

/* Cycle-start countdown: fills the hidden .starter-countdown strip under
   the "New to dancing?" subtitle and reveals it; hides itself once the
   start date has passed. */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.starter-countdown[data-countdown]').forEach((el) => {
        const target = Date.parse(el.dataset.countdown);
        const cells = {
            days: el.querySelector('[data-count="days"]'),
            hours: el.querySelector('[data-count="hours"]'),
            mins: el.querySelector('[data-count="mins"]')
        };
        if (Number.isNaN(target) || !cells.days || !cells.hours || !cells.mins) return;
        const render = () => {
            const totalMins = Math.floor((target - Date.now()) / 60000);
            if (totalMins <= 0) {
                el.hidden = true;
                clearInterval(timer);
                return;
            }
            cells.days.textContent = String(Math.floor(totalMins / 1440));
            cells.hours.textContent = String(Math.floor((totalMins % 1440) / 60));
            cells.mins.textContent = String(totalMins % 60);
            el.hidden = false;
        };
        const timer = setInterval(render, 30000);
        render();
    });
});

/* Trial class preselection: links such as "?class=beginner0#trial-form"
   (used by the beginner gateway CTAs) check the matching radio so a
   high-intent visitor lands on the form with their class already chosen. */
document.addEventListener('DOMContentLoaded', () => {
    const preselect = new URLSearchParams(window.location.search).get('class');
    if (!preselect) return;

    const target = document.querySelector(`.trial-form input[name="class-select"][data-preselect="${preselect}"]`);
    if (!target || target.disabled) return;

    target.checked = true;
    target.dispatchEvent(new Event('change', { bubbles: true }));
});

/* GOOGLE SHEETS FORM SUBMISSION */
document.addEventListener('DOMContentLoaded', () => {
    const trialForm = document.getElementById('trialForm');

    if (trialForm) {
        console.log('Trial form found, attaching listener');
        const classSelectInputs = trialForm.querySelectorAll('input[name="class-select"]');
        const canAnimateClassChoice = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Inline validation errors clear as soon as the visitor fixes the field
        trialForm.addEventListener('input', (event) => {
            const field = event.target;
            if (!(field instanceof HTMLElement)) return;
            field.classList.remove('input-error');
            const anchor = field.closest('.form-group')
                || (field.getAttribute('name') === 'class-select'
                    ? trialForm.querySelector('.trial-step--choice .trial-step__header')
                    : null);
            anchor?.querySelector('.form-error')?.remove();
        });

        const enhanceTrialProcess = () => {
            const process = document.querySelector('[data-trial-process]');
            if (!process) return;

            const processCanvas = process.querySelector('[data-trial-process-canvas]');
            const processItems = Array.from(process.querySelectorAll('.trial-process__item'));
            const canAnimateProcess = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            let trialProcessGsapPromise = null;

            const loadTrialProcessGsap = () => {
                if (window.gsap) return Promise.resolve(window.gsap);
                if (trialProcessGsapPromise) return trialProcessGsapPromise;

                trialProcessGsapPromise = new Promise((resolve) => {
                    const settle = () => resolve(window.gsap || null);
                    const existing = document.querySelector('script[src*="gsap-3.12.5"]');

                    if (existing) {
                        existing.addEventListener('load', settle, { once: true });
                        existing.addEventListener('error', () => resolve(null), { once: true });
                    } else {
                        const script = document.createElement('script');
                        script.src = '/assets/vendor/gsap-3.12.5.min.js';
                        script.async = true;
                        script.onload = settle;
                        script.onerror = () => resolve(null);
                        document.head.appendChild(script);
                    }

                    window.setTimeout(settle, 1500);
                });

                return trialProcessGsapPromise;
            };

            if (canAnimateProcess && processItems.length) {
                let hasPlayedReveal = false;
                const playReveal = async () => {
                    if (hasPlayedReveal) return;
                    hasPlayedReveal = true;

                    const gsap = await loadTrialProcessGsap();
                    if (!gsap) return;

                    gsap.set(process, { '--trial-process-progress': 0 });
                    gsap.set(processItems, {
                        autoAlpha: 0,
                        y: 14
                    });

                    gsap.timeline({
                        defaults: { ease: 'power3.out' },
                        onComplete: () => {
                            gsap.set(processItems, { clearProps: 'opacity,visibility,transform' });
                        }
                    })
                        .to(process, {
                            '--trial-process-progress': 1,
                            duration: 0.72
                        }, 0)
                        .to(processItems, {
                            autoAlpha: 1,
                            y: 0,
                            duration: 0.46,
                            stagger: 0.08
                        }, 0.05);
                };

                if ('IntersectionObserver' in window) {
                    const revealObserver = new IntersectionObserver((entries) => {
                        if (entries.some(entry => entry.isIntersecting)) {
                            playReveal();
                            revealObserver.disconnect();
                        }
                    }, {
                        rootMargin: '160px 0px',
                        threshold: 0.2
                    });
                    revealObserver.observe(process);
                } else {
                    playReveal();
                }
            }

            if (!processCanvas || !canAnimateProcess) return;

            const canUseTrialProcessWebGL = () => {
                if (!window.WebGLRenderingContext) return false;

                try {
                    const testCanvas = document.createElement('canvas');
                    return Boolean(
                        testCanvas.getContext('webgl') ||
                        testCanvas.getContext('experimental-webgl')
                    );
                } catch (error) {
                    return false;
                }
            };

            if (!canUseTrialProcessWebGL()) return;

            let trialProcessThreePromise = null;
            const loadTrialProcessThree = () => {
                if (trialProcessThreePromise) return trialProcessThreePromise;

                trialProcessThreePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);

                return trialProcessThreePromise;
            };

            let processRenderer = null;
            let processScene = null;
            let processCamera = null;
            let processGroup = null;
            let processParticles = null;
            let processFrame = 0;
            let processVisible = false;
            let processLoaded = false;
            let processBaseRotation = 0;
            const processStations = [];

            const resizeTrialProcess = () => {
                if (!processRenderer || !processCamera || !processGroup) return;

                const width = Math.max(1, Math.round(process.clientWidth));
                const height = Math.max(1, Math.round(process.clientHeight));
                processRenderer.setSize(width, height, false);

                const aspect = width / height;
                processCamera.left = -3.9 * aspect;
                processCamera.right = 3.9 * aspect;
                processCamera.top = 2.1;
                processCamera.bottom = -2.1;
                processCamera.updateProjectionMatrix();

                processBaseRotation = 0;
                const scale = width < 720 ? Math.min(1, Math.max(0.7, height / 330)) : Math.min(1, Math.max(0.76, width / 920));
                processGroup.scale.set(scale, scale, scale);
            };

            const startTrialProcess = () => {
                if (processFrame || !processRenderer || !processScene || !processCamera || !processGroup) return;
                processVisible = true;

                const render = (time = 0) => {
                    const rhythm = time * 0.001;
                    processGroup.rotation.z = processBaseRotation + Math.sin(rhythm * 0.7) * 0.018;
                    processGroup.position.y = Math.sin(rhythm * 0.9) * 0.035;

                    processStations.forEach((station, index) => {
                        const pulse = 1 + Math.sin(rhythm * 1.8 + index * 0.72) * 0.035;
                        station.scale.set(pulse, pulse, pulse);
                    });

                    if (processParticles) {
                        processParticles.rotation.z = processBaseRotation + rhythm * 0.11;
                        processParticles.rotation.y = Math.sin(rhythm * 0.8) * 0.08;
                    }

                    processRenderer.render(processScene, processCamera);

                    if (processVisible) {
                        processFrame = window.requestAnimationFrame(render);
                    }
                };

                processFrame = window.requestAnimationFrame(render);
            };

            const stopTrialProcess = () => {
                processVisible = false;
                if (processFrame) {
                    window.cancelAnimationFrame(processFrame);
                    processFrame = 0;
                }
            };

            const buildTrialProcess = async () => {
                if (processLoaded) return;
                processLoaded = true;

                const THREE = await loadTrialProcessThree();
                if (!THREE) return;

                try {
                    processRenderer = new THREE.WebGLRenderer({
                        canvas: processCanvas,
                        alpha: true,
                        antialias: true,
                        powerPreference: 'low-power'
                    });
                } catch (error) {
                    return;
                }

                processRenderer.setClearColor(0x000000, 0);
                processRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.35));

                processScene = new THREE.Scene();
                processCamera = new THREE.OrthographicCamera(-4, 4, 2, -2, 0, 10);
                processCamera.position.z = 5;

                processGroup = new THREE.Group();
                processScene.add(processGroup);

                const stationX = [-2.35, 0, 2.35];
                const makeConnector = (fromX, toX, color, opacity, yOffset) => {
                    const points = [];
                    for (let index = 0; index < 34; index += 1) {
                        const t = index / 33;
                        const x = fromX + (toX - fromX) * t;
                        const y = Math.sin(t * Math.PI) * 0.18 + yOffset;
                        const z = Math.cos(t * Math.PI) * 0.08;
                        points.push(new THREE.Vector3(x, y, z));
                    }

                    const curve = new THREE.CatmullRomCurve3(points);
                    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(74));
                    const material = new THREE.LineBasicMaterial({
                        color,
                        transparent: true,
                        opacity,
                        depthWrite: false
                    });
                    processGroup.add(new THREE.Line(geometry, material));
                };

                makeConnector(stationX[0], stationX[1], 0xc94a35, 0.42, 0.04);
                makeConnector(stationX[1], stationX[2], 0xb8872b, 0.48, -0.04);

                stationX.forEach((x, index) => {
                    const ringGeometry = new THREE.RingGeometry(0.22, 0.255, 42);
                    const ringMaterial = new THREE.MeshBasicMaterial({
                        color: index === 1 ? 0xb8872b : 0xc94a35,
                        transparent: true,
                        opacity: 0.46,
                        depthWrite: false,
                        side: THREE.DoubleSide
                    });
                    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
                    ring.position.set(x, 0, 0);
                    processStations.push(ring);
                    processGroup.add(ring);

                    const glowGeometry = new THREE.CircleGeometry(0.16, 32);
                    const glowMaterial = new THREE.MeshBasicMaterial({
                        color: index === 1 ? 0x2a0f3f : 0xb8872b,
                        transparent: true,
                        opacity: 0.12,
                        depthWrite: false
                    });
                    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
                    glow.position.set(x, 0, -0.01);
                    processGroup.add(glow);
                });

                const particleCount = window.innerWidth < 768 ? 26 : 42;
                const positions = new Float32Array(particleCount * 3);
                for (let index = 0; index < particleCount; index += 1) {
                    const offset = index * 3;
                    const angle = (index / particleCount) * Math.PI * 2;
                    const radius = 0.8 + Math.random() * 2.4;
                    positions[offset] = Math.cos(angle) * radius;
                    positions[offset + 1] = Math.sin(angle) * 0.42 + (Math.random() - 0.5) * 0.22;
                    positions[offset + 2] = (Math.random() - 0.5) * 0.45;
                }

                const particleGeometry = new THREE.BufferGeometry();
                particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const particleMaterial = new THREE.PointsMaterial({
                    color: 0x2a0f3f,
                    size: 0.035,
                    transparent: true,
                    opacity: 0.26,
                    depthWrite: false
                });
                processParticles = new THREE.Points(particleGeometry, particleMaterial);
                processGroup.add(processParticles);

                resizeTrialProcess();
                startTrialProcess();
            };

            window.addEventListener('resize', resizeTrialProcess, { passive: true });

            if ('IntersectionObserver' in window) {
                const processObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            buildTrialProcess();
                            startTrialProcess();
                        } else {
                            stopTrialProcess();
                        }
                    });
                }, {
                    rootMargin: '220px 0px',
                    threshold: 0.01
                });
                processObserver.observe(process);
            } else {
                buildTrialProcess();
            }
        };

        enhanceTrialProcess();

        if (canAnimateClassChoice) {
            const classChoiceCards = Array.from(trialForm.querySelectorAll('.compact-card'));
            let classChoiceGsapPromise = null;
            let classChoiceThreePromise = null;
            let activeChoiceCanvas = null;
            let choiceCanvasToken = 0;

            const loadClassChoiceGsap = () => {
                if (window.gsap) return Promise.resolve(window.gsap);
                if (classChoiceGsapPromise) return classChoiceGsapPromise;

                classChoiceGsapPromise = new Promise((resolve) => {
                    let hasResolved = false;
                    const finish = (value) => {
                        if (hasResolved) return;
                        hasResolved = true;
                        resolve(value);
                    };

                    const existingScript = document.querySelector('script[src*="gsap"]') || document.querySelector('script[data-class-choice-gsap]');
                    if (existingScript) {
                        existingScript.addEventListener('load', () => finish(window.gsap || null), { once: true });
                        existingScript.addEventListener('error', () => finish(null), { once: true });
                        window.setTimeout(() => finish(window.gsap || null), 900);
                        return;
                    }

                    const script = document.createElement('script');
                    script.src = '/assets/vendor/gsap-3.12.5.min.js';
                    script.async = true;
                    script.dataset.classChoiceGsap = 'true';
                    script.onload = () => finish(window.gsap || null);
                    script.onerror = () => finish(null);
                    document.head.appendChild(script);

                    window.setTimeout(() => finish(window.gsap || null), 1000);
                });

                return classChoiceGsapPromise;
            };

            const loadClassChoiceThree = () => {
                if (classChoiceThreePromise) return classChoiceThreePromise;

                classChoiceThreePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);

                return classChoiceThreePromise;
            };

            const canUseClassChoiceWebGL = () => {
                if (!window.WebGLRenderingContext) return false;

                try {
                    const testCanvas = document.createElement('canvas');
                    return Boolean(
                        testCanvas.getContext('webgl') ||
                        testCanvas.getContext('experimental-webgl')
                    );
                } catch (error) {
                    return false;
                }
            };

            const stopActiveChoiceCanvas = () => {
                if (!activeChoiceCanvas) return;

                if (activeChoiceCanvas.animationFrame) {
                    window.cancelAnimationFrame(activeChoiceCanvas.animationFrame);
                }

                activeChoiceCanvas.geometry?.dispose();
                activeChoiceCanvas.material?.dispose();
                activeChoiceCanvas.renderer?.dispose();
                activeChoiceCanvas.canvas?.remove();
                activeChoiceCanvas = null;
            };

            const startChoiceCanvas = async (card) => {
                if (!card || !canUseClassChoiceWebGL()) return;

                const token = ++choiceCanvasToken;
                stopActiveChoiceCanvas();

                const THREE = await loadClassChoiceThree();
                if (!THREE || token !== choiceCanvasToken) return;

                const canvas = document.createElement('canvas');
                canvas.className = 'compact-card__selection-canvas';
                canvas.setAttribute('aria-hidden', 'true');
                card.prepend(canvas);

                const renderer = new THREE.WebGLRenderer({
                    canvas,
                    alpha: true,
                    antialias: true,
                    powerPreference: 'low-power'
                });
                renderer.setClearColor(0x000000, 0);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));

                const scene = new THREE.Scene();
                const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
                const geometry = new THREE.PlaneGeometry(2, 2);
                const material = new THREE.ShaderMaterial({
                    transparent: true,
                    depthWrite: false,
                    depthTest: false,
                    uniforms: {
                        uTime: { value: 0 }
                    },
                    vertexShader: `
                        varying vec2 vUv;
                        void main() {
                            vUv = uv;
                            gl_Position = vec4(position.xy, 0.0, 1.0);
                        }
                    `,
                    fragmentShader: `
                        precision mediump float;
                        varying vec2 vUv;
                        uniform float uTime;
                        void main() {
                            vec2 p = vUv;
                            float diagonal = p.x * 0.72 + (1.0 - p.y) * 0.28;
                            float wave = sin((p.x * 5.4 + p.y * 3.8) + uTime * 1.25) * 0.5 + 0.5;
                            float softCore = 1.0 - smoothstep(0.16, 0.78, distance(p, vec2(0.82, 0.22)));
                            float lowGlow = 1.0 - smoothstep(0.16, 0.92, distance(p, vec2(0.18, 0.86)));
                            vec3 coral = vec3(0.79, 0.29, 0.21);
                            vec3 gold = vec3(0.72, 0.53, 0.17);
                            vec3 ink = vec3(0.16, 0.06, 0.24);
                            vec3 color = mix(ink, mix(coral, gold, wave), 0.62 + softCore * 0.28);
                            float alpha = 0.08 + softCore * 0.18 + lowGlow * 0.1 + diagonal * 0.06;
                            gl_FragColor = vec4(color, alpha);
                        }
                    `
                });
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);

                const resize = () => {
                    const rect = card.getBoundingClientRect();
                    renderer.setSize(
                        Math.max(1, Math.round(rect.width)),
                        Math.max(1, Math.round(rect.height)),
                        false
                    );
                };

                const render = (time = 0) => {
                    if (!activeChoiceCanvas || activeChoiceCanvas.card !== card) return;

                    material.uniforms.uTime.value = time * 0.001;
                    renderer.render(scene, camera);
                    activeChoiceCanvas.animationFrame = window.requestAnimationFrame(render);
                };

                activeChoiceCanvas = {
                    card,
                    canvas,
                    renderer,
                    geometry,
                    material,
                    animationFrame: 0,
                    resize
                };

                resize();
                render();
            };

            const animateClassChoice = (input, immediate = false) => {
                if (!input || input.disabled) return;

                const card = input.closest('.compact-option')?.querySelector('.compact-card');
                if (!card) return;

                classChoiceCards.forEach(choiceCard => {
                    choiceCard.classList.toggle('compact-card--selected', choiceCard === card);
                    if (choiceCard !== card) {
                        choiceCard.querySelector('.compact-card__selection-canvas')?.remove();
                    }
                });

                startChoiceCanvas(card);

                loadClassChoiceGsap().then((choiceGsap) => {
                    if (!choiceGsap) {
                        const existingTimer = Number(card.dataset.choicePulseTimer);
                        if (existingTimer) {
                            window.clearTimeout(existingTimer);
                        }

                        card.classList.remove('compact-card--choice-pulse');
                        void card.offsetWidth;
                        card.classList.add('compact-card--choice-pulse');

                        card.dataset.choicePulseTimer = String(window.setTimeout(() => {
                            card.classList.remove('compact-card--choice-pulse');
                            delete card.dataset.choicePulseTimer;
                        }, 460));
                        return;
                    }

                    choiceGsap.killTweensOf(card);
                    choiceGsap.fromTo(card, {
                        boxShadow: '0 10px 24px rgba(42, 15, 63, 0.08)'
                    }, {
                        boxShadow: '0 16px 34px rgba(42, 15, 63, 0.2), 0 0 0 5px rgba(201, 74, 53, 0.12)',
                        duration: immediate ? 0.01 : 0.28,
                        ease: 'power2.out',
                        yoyo: true,
                        repeat: 1,
                        onComplete: () => choiceGsap.set(card, { clearProps: 'boxShadow' })
                    });
                });
            };

            classSelectInputs.forEach(input => {
                input.addEventListener('change', () => animateClassChoice(input));
            });

            const selectedInput = trialForm.querySelector('input[name="class-select"]:checked');
            const selectedCard = selectedInput?.closest('.compact-option')?.querySelector('.compact-card');
            if (selectedCard) {
                animateClassChoice(selectedInput, true);
            }

            window.addEventListener('resize', () => {
                activeChoiceCanvas?.resize();
            }, { passive: true });
        }

        trialForm.addEventListener('submit', e => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitTrialBtn');
            const originalBtnContent = submitBtn.innerHTML;
            const isGermanPage = document.documentElement.lang === 'de' || window.location.pathname.includes('/de/');

            // 1. Gather Data
            const rawFormData = new FormData(trialForm);
            const firstName = String(rawFormData.get('firstname') || '').trim();
            const contact = String(rawFormData.get('contact') || '').trim();
            const selectedClass = String(rawFormData.get('class-select') || '').trim();
            const data = {
                firstname: firstName,
                lastname: '',
                contact,
                phone: contact,
                email: '',
                selected_class: selectedClass // Users script expects 'selected_class'
            };

            // Inline validation: errors render next to their field instead of
            // an alert(); the first invalid field is scrolled into view.
            trialForm.querySelectorAll('.form-error').forEach((node) => node.remove());
            trialForm.querySelectorAll('.input-error').forEach((node) => node.classList.remove('input-error'));

            const addInlineError = (anchor, message) => {
                if (!anchor) return;
                const error = document.createElement('p');
                error.className = 'form-error';
                error.setAttribute('role', 'alert');
                error.textContent = message;
                anchor.appendChild(error);
            };

            const invalidTargets = [];

            if (!data.selected_class) {
                addInlineError(
                    trialForm.querySelector('.trial-step--choice .trial-step__header'),
                    isGermanPage ? 'Bitte wähle zuerst eine Probelektion aus.' : 'Please choose a trial class first.'
                );
                invalidTargets.push(trialForm.querySelector('.trial-step--choice'));
            }

            if (!data.firstname) {
                const nameInput = trialForm.querySelector('#firstname');
                nameInput?.classList.add('input-error');
                addInlineError(
                    nameInput?.closest('.form-group'),
                    isGermanPage ? 'Bitte gib deinen Namen ein.' : 'Please add your name.'
                );
                invalidTargets.push(nameInput);
            }

            if (!data.contact) {
                const contactInput = trialForm.querySelector('#contact');
                contactInput?.classList.add('input-error');
                addInlineError(
                    contactInput?.closest('.form-group'),
                    isGermanPage ? 'Bitte gib deine WhatsApp-Nummer ein.' : 'Please add your WhatsApp number.'
                );
                invalidTargets.push(contactInput);
            } else if (data.contact.replace(/[^0-9]/g, '').length < 8 || data.contact.includes('@')) {
                const contactInput = trialForm.querySelector('#contact');
                contactInput?.classList.add('input-error');
                addInlineError(
                    contactInput?.closest('.form-group'),
                    isGermanPage
                        ? 'Bitte gib eine gültige WhatsApp-Nummer ein.'
                        : 'Please add a valid WhatsApp number.'
                );
                invalidTargets.push(contactInput);
            }

            if (invalidTargets.length) {
                const firstInvalid = invalidTargets.find(Boolean);
                firstInvalid?.scrollIntoView({
                    behavior: canAnimateClassChoice ? 'smooth' : 'auto',
                    block: 'center'
                });
                if (firstInvalid && typeof firstInvalid.focus === 'function') {
                    firstInvalid.focus({ preventScroll: true });
                }
                return;
            }

            // 2. Show Loading State
            submitBtn.innerHTML = isGermanPage ? '<span>Wird gesendet...</span>' : '<span>Submitting...</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.style.cursor = 'not-allowed';

            // 3. Send to the existing lead channels and the owner inbox in parallel.
            // IMPORTANT: PASTE YOUR WEB APP URL BELOW
            const scriptURL = 'https://script.google.com/macros/s/AKfycbwPqLutAq-xa9OkSiT-rLm72DJCdQ2Xw10Yp4DvHexTq42HxCKJyJr8mJmZ0RuZSc7A5A/exec';
            const formSubmitEmail = 'info@axcentdance.com'; // Using FormSubmit for reliable emails
            const formSubmitURL = `https://formsubmit.co/ajax/${formSubmitEmail}`;
            const supabaseURL = 'https://jwravnvytkmsvqoqkmwb.supabase.co';
            // This is a public browser key. Supabase RLS and the scoped RPC
            // enforce access; no private service credential is exposed here.
            const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3cmF2bnZ5dGttc3Zxb3FrbXdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3NjU1MTIsImV4cCI6MjA5OTM0MTUxMn0.t4waGFmjD2hDQkGOhYg8rPt1rtf4iyRyTIC6T5KsFag';

            if (scriptURL === 'REPLACE_ME_WITH_YOUR_WEB_APP_URL') {
                alert('Configuration missing: Please paste your Google Web App URL in script.js (Line ~206)');
                submitBtn.innerHTML = originalBtnContent;
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                submitBtn.style.cursor = 'pointer';
                return;
            }

            // Prepare FormSubmit Data
            const autoresponse = isGermanPage
                ? `Vielen Dank für deine Anfrage zur Probelektion!

Wir melden uns bald per WhatsApp bei dir.
Wir freuen uns darauf, dich bei AXcent Dance zu begrüssen.

Ort:
AXcent Dance Studio
Hermetschloostrasse 73
8048 Zürich Altstetten

Liebe Grüsse
Das AXcent Dance Team
info@axcentdance.com`
                : `Thank you for requesting a trial class!

We will contact you shortly via WhatsApp.
We are looking forward to welcoming you to AXcent Dance.

Location:
AXcent Dance Studio
Hermetschloostrasse 73
8048 Zurich Altstetten

Best regards,
The AXcent Dance Team
info@axcentdance.com`;

            const formSubmitData = {
                _subject: `New Trial Booking from ${data.firstname}`,
                _template: 'table',
                _captcha: 'false',
                _autoresponse: autoresponse,
                firstname: data.firstname,
                lastname: data.lastname,
                contact: data.contact,
                phone: data.phone,
                email: data.email,
                class: data.selected_class
            };

            const timeout = (ms, label) => new Promise((_, reject) => {
                setTimeout(() => reject(new Error(`${label} timeout`)), ms);
            });

            const googleSheetsPromise = Promise.race([
                fetch(scriptURL, {
                    method: 'POST',
                    body: JSON.stringify(data),
                    mode: 'no-cors'
                }),
                timeout(5000, 'Google Sheets submission')
            ]);

            const formSubmitPromise = Promise.race([
                fetch(formSubmitURL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formSubmitData)
                }),
                timeout(3000, 'FormSubmit email submission')
            ]);

            const trialInboxPromise = Promise.race([
                fetch(`${supabaseURL}/rest/v1/rpc/submit_trial_request`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'apikey': supabaseAnonKey,
                        'Authorization': `Bearer ${supabaseAnonKey}`
                    },
                    body: JSON.stringify({
                        p_name: data.firstname,
                        p_phone: data.phone,
                        p_selected_class: data.selected_class,
                        p_locale: isGermanPage ? 'de' : 'en'
                    })
                }).then((response) => {
                    if (!response.ok) throw new Error(`Trial inbox returned ${response.status}`);
                    return response;
                }),
                timeout(5000, 'Trial inbox submission')
            ]);

            Promise.allSettled([googleSheetsPromise, formSubmitPromise, trialInboxPromise])
                .then((results) => {
                    const googleSheetsResult = results[0];
                    const formSubmitResult = results[1];
                    const trialInboxResult = results[2];

                    if (googleSheetsResult.status === 'fulfilled') {
                        console.log('Trial Google Sheets submission completed or accepted as background request.');
                    } else {
                        console.error('Trial Google Sheets submission issue:', googleSheetsResult.reason);
                    }

                    if (formSubmitResult.status === 'fulfilled') {
                        console.log('Trial FormSubmit status:', formSubmitResult.value.status);
                        if (!formSubmitResult.value.ok) {
                            console.error('Trial FormSubmit returned an error status:', formSubmitResult.value.status);
                        }
                    } else {
                        console.error('Trial FormSubmit submission issue:', formSubmitResult.reason);
                    }

                    if (trialInboxResult.status === 'fulfilled') {
                        console.log('Trial request added to the owner inbox.');
                    } else {
                        // Google Sheets and email remain independent fallbacks,
                        // so a temporary inbox error does not lose the lead.
                        console.error('Trial owner inbox submission issue:', trialInboxResult.reason);
                    }

                    try {
                        if (data.email) sessionStorage.setItem('lead_email', data.email);
                        if (data.phone) sessionStorage.setItem('lead_phone', data.phone);
                        sessionStorage.setItem('axcent_trial_signup_success', '1');
                    } catch (storageError) {
                        console.error('Storage Error:', storageError);
                    }

                    window.location.href = 'thank-you-trial.html';
                });
        });
    }

    // Contact Form Logic
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        console.log('Contact form found, attaching listener');
        contactForm.addEventListener('submit', e => {
            e.preventDefault();
            const isGermanPage = document.documentElement.lang === 'de' || window.location.pathname.startsWith('/de/');

            const submitBtn = document.getElementById('submitContactBtn');
            const originalBtnContent = submitBtn.innerHTML;

            // 1. Show Loading State
            submitBtn.innerHTML = isGermanPage ? '<span>Wird gesendet...</span>' : '<span>Sending...</span>';
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
            const formSubmitEmail = 'info@axcentdance.com'; // Using FormSubmit for reliable emails
            const formSubmitURL = `https://formsubmit.co/ajax/${formSubmitEmail}`;

            // Prepare FormSubmit Data (Needs hidden fields for configuration)
            const formSubmitData = {
                _subject: `New Contact from ${data.name}`,
                _template: 'table', // or 'box'
                _captcha: 'false',  // Disable captcha if you want instant submission
                _autoresponse: isGermanPage ? `Danke für deine Nachricht an AXcent Dance.

Wir melden uns bald per E-Mail oder WhatsApp.

Liebe Grüsse,
Das AXcent Dance Team
info@axcentdance.com` : `Thank you for submitting the contact form!

We will get back to you shortly via email or WhatsApp.

Best regards,
The AXcent Dance Team
info@axcentdance.com`,
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
                    window.location.href = 'thank-you-contact.html';
                })
                .catch(error => {
                    console.error('Error!', error.message);
                    alert(isGermanPage ? 'Beim Senden deiner Nachricht ist etwas schiefgelaufen. Bitte versuche es später erneut.' : 'Something went wrong sending your message. Please try again later.');

                    // Reset button state
                    submitBtn.innerHTML = originalBtnContent;
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.style.cursor = 'pointer';
                });
        });
    }

    // Event Registration Form Logic (Dominican Bootcamp)
    const eventRegForm = document.getElementById('eventRegForm');
    if (eventRegForm) {
        console.log('Event Reg form found, attaching listener');
        eventRegForm.addEventListener('submit', e => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitRegBtn');
            const originalBtnContent = submitBtn.innerHTML;

            // 1. Show Loading State
            submitBtn.innerHTML = '<span class="btn-hero-content">Wait...</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            submitBtn.style.cursor = 'not-allowed';

            // 2. Gather Data
            const rawFormData = new FormData(eventRegForm);
            const data = {
                firstname: rawFormData.get('firstname'),
                lastname: rawFormData.get('lastname'),
                email: rawFormData.get('email'),
                phone: rawFormData.get('phone'),
                selected_class: rawFormData.get('selected_class')
            };

            // 3. Send to Google Script AND FormSubmit (Parallel)
            // REPLACE THIS URL with the one generated from your Google Apps Script
            const googleScriptURL = 'https://script.google.com/macros/s/AKfycby8afi6chnCIBjEtrgGWmy1qqrUfrdMrZ0JYcaIrO6mzBfW6C219hYBgD-jPMfnoHWlbw/exec';
            const formSubmitEmail = 'info@axcentdance.com';
            const formSubmitURL = `https://formsubmit.co/ajax/${formSubmitEmail}`;

            // Prepare FormSubmit Data
            const formSubmitData = {
                _subject: `New Bootcamp Registration from ${data.firstname} ${data.lastname}`,
                _template: 'table',
                _captcha: 'false',
                _autoresponse: `Thank you for registering for the Dominican Bachata Bootcamp!\n\nIf you haven't completed your payment yet, please use this secure link: https://buy.stripe.com/8x214p2wDgyt2BV9cCfnO0a\n\nBest regards,\nThe AXcent Dance Team`,
                firstname: data.firstname,
                lastname: data.lastname,
                email: data.email,
                phone: data.phone,
                event: data.selected_class
            };

            const p1 = fetch(googleScriptURL, { method: 'POST', body: JSON.stringify(data), mode: 'no-cors' });

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
                    // Redirect to secure Stripe payment
                    window.location.href = 'https://buy.stripe.com/8x214p2wDgyt2BV9cCfnO0a';
                })
                .catch(error => {
                    console.error('Error!', error.message);
                    window.location.href = 'https://buy.stripe.com/8x214p2wDgyt2BV9cCfnO0a';
                });
        });
    }

    // Registration Form Logic
    // Moved from inline script to ensure reliability
    const classCheckboxes = document.querySelectorAll('.class-option input[type="checkbox"]');

    function updateRoleState(checkbox) {
        const wrapper = checkbox.closest('.class-option-wrapper');
        // Guard clause for spacers or malformed structure
        if (!wrapper) return;

        const roleRadios = wrapper.querySelectorAll('.class-role-select input[type="radio"]');
        const roleLabels = wrapper.querySelectorAll('.class-role-select label');

        if (checkbox.checked) {
            roleRadios.forEach(radio => radio.disabled = false);
            roleLabels.forEach(label => label.style.opacity = '1');
            roleLabels.forEach(label => label.style.pointerEvents = 'auto');
        } else {
            roleRadios.forEach(radio => {
                radio.disabled = true;
                radio.checked = false; // Uncheck if class is deselected
            });
            roleLabels.forEach(label => label.style.opacity = '0.5');
            roleLabels.forEach(label => label.style.pointerEvents = 'none');
        }
    }

    if (classCheckboxes.length > 0) {
        classCheckboxes.forEach(cb => {
            // Initial state check
            updateRoleState(cb);
            // Listener
            cb.addEventListener('change', () => updateRoleState(cb));
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

            // Only prefetch same-origin pages; cross-origin prefetches (social
            // icons, external partners) waste bandwidth and are discarded.
            let resolved;
            try {
                resolved = new URL(url, window.location.href);
            } catch (error) {
                return;
            }
            if (resolved.origin !== window.location.origin) return;

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

    // Timeline Scanner Fade Effect
    const timeline = document.querySelector('.timeline');
    const scanner = document.querySelector('.timeline-scanner');

    if (timeline && scanner) {
        const updateScannerOpacity = () => {
            const rect = timeline.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const center = viewportHeight / 2;
            const fadeRange = 150; // Pixels distance to fade in/out

            // Distance from center line
            const distTop = center - rect.top;
            const distBottom = rect.bottom - center;

            let opacity = 1;

            if (distTop < 0) {
                // Top of timeline is below center
                opacity = 0;
            } else if (distTop < fadeRange) {
                // Fading in from top
                opacity = distTop / fadeRange;
            } else if (distBottom < 0) {
                // Bottom of timeline is above center
                opacity = 0;
            } else if (distBottom < fadeRange) {
                // Fading out to bottom
                opacity = distBottom / fadeRange;
            }

            scanner.style.opacity = Math.max(0, Math.min(1, opacity));
        };

        window.addEventListener('scroll', () => {
            requestAnimationFrame(updateScannerOpacity);
        });
        window.addEventListener('resize', updateScannerOpacity);
        // Initial check
        updateScannerOpacity();
    }
});

// Tropic Noir subpages: generic "Lead & Follow" entrance. Sections below the
// fold are armed (hidden via CSS class) only after JS confirms they are
// offscreen, so content is always visible without JavaScript, with reduced
// motion, and above the fold (no flash, no CLS — transform/opacity only).
// The heading leads because it is the first armed child; siblings follow via
// the CSS transition-delay ladder in tropic-noir.css.
(function enhanceTropicSubpageEntrances() {
    if (!document.body.classList.contains('tropic')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!('IntersectionObserver' in window)) return;

    const sections = Array.from(document.querySelectorAll('main section'));
    if (!sections.length) return;

    const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            io.unobserve(entry.target);
            entry.target.classList.add('tropic-reveal--in');
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });

    sections.forEach((section) => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= window.innerHeight * 0.9) return;
        const stage = section.querySelector(':scope > .container') || section;
        if (!stage.children.length || stage.children.length > 14) {
            return;
        }
        section.classList.add('tropic-reveal');
        io.observe(section);
    });
})();

// About page hero: brass step-diagram panel. A brushed-brass plaque with the
// Bachata basic-step count (1-2-3-4) traced in raised brass, not an abstract
// shape — see .agent/rules/axcent-rules.md §4.2. The SVG in the markup is the
// full static fallback (no JS, reduced motion, or WebGL required); this only
// upgrades it to a lit, gently tilting 3D read once it is safe to do so.
(function enhanceAboutHeroIntro() {
    if (!document.body.classList.contains('about-page')) return;

    const gsap = window.gsap;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const heroContent = document.querySelector('.about-hero__content');

    if (!gsap || prefersReducedMotion || !heroContent) return;

    const textTargets = gsap.utils.toArray([
        '.about-hero__content .hero-badge',
        '.about-hero__content .page-title',
        '.about-hero__content .hero-desc-border'
    ].join(', '));
    if (!textTargets.length) return;

    gsap.set(textTargets, { autoAlpha: 0, y: 18 });

    const clearIntroStyles = () => gsap.set(textTargets, { clearProps: 'opacity,visibility,transform' });

    gsap.timeline({
        defaults: { ease: 'power3.out' },
        onComplete: clearIntroStyles
    }).to(textTargets, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.09 });

    // Safety net: if the tab is backgrounded mid-tween, content must not
    // stay invisible indefinitely.
    window.setTimeout(clearIntroStyles, 1700);
})();

// Education page — "The Count". Bachata is danced 1-2-3-4 with the accent on
// the tap, and the page's four sections are the four counts. Three motion
// layers, each optional and independently guarded so the static page stays
// fully readable with no JavaScript, no GSAP, no WebGL, or reduced motion:
//   1. Hero string scene (three.js): five guitar strings plucked on a
//      four-count at bachata tempo — the fourth pluck (the tap) is the coral
//      string and lands harder. See .agent/rules/axcent-rules.md §4.2.
//   2. Rhythm map playhead (GSAP): sweeps the 8-count grid in the musicality
//      section, lighting the columns where each instrument hits.
//   3. Section entrances + count-rail/nav scroll-spy.
(function enhanceEducationPage() {
    if (!document.body.classList.contains('education-page')) return;

    const gsap = window.gsap;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const BEAT_SECONDS = 60 / 108; // typical bachata tempo

    // --- 1. Section + hero entrances -----------------------------------
    const enhanceEntrances = () => {
        if (!gsap || prefersReducedMotion) return;

        const heroTargets = gsap.utils.toArray([
            '.education-hero .hero-badge',
            '.education-hero .page-title',
            '.education-hero .edu-hero__desc',
            '.education-hero .edu-hero__counts .edu-hero__count'
        ].join(', '));

        if (heroTargets.length) {
            const clearHero = () => gsap.set(heroTargets, { clearProps: 'opacity,visibility,transform' });
            gsap.set(heroTargets, { autoAlpha: 0, y: 16 });
            gsap.timeline({
                defaults: { ease: 'power3.out' },
                onComplete: clearHero
            }).to(heroTargets, { autoAlpha: 1, y: 0, duration: 0.55, stagger: 0.09 });
            window.setTimeout(clearHero, 2200);
        }

        if (!('IntersectionObserver' in window)) return;

        gsap.utils.toArray('.edu-section').forEach((section) => {
            if (section.getBoundingClientRect().top <= window.innerHeight * 0.85) return;

            const head = section.querySelector('.edu-section__head');
            const headTargets = head ? Array.from(head.children) : [];
            const bodyTargets = Array.from(section.children)
                .filter((child) => !child.classList.contains('edu-section__head'));
            const targets = [...headTargets, ...bodyTargets];
            if (!targets.length) return;

            gsap.set(headTargets, { autoAlpha: 0, y: 22 });
            gsap.set(bodyTargets, { autoAlpha: 0, y: 18 });

            let played = false;
            const play = () => {
                if (played) return;
                played = true;
                gsap.timeline({
                    defaults: { ease: 'power3.out' },
                    onComplete: () => gsap.set(targets, { clearProps: 'opacity,visibility,transform' })
                })
                    .to(headTargets, { autoAlpha: 1, y: 0, duration: 0.5, stagger: 0.08 })
                    .to(bodyTargets, { autoAlpha: 1, y: 0, duration: 0.55, stagger: 0.07 }, '-=0.28');
                window.setTimeout(
                    () => gsap.set(targets, { clearProps: 'opacity,visibility,transform' }),
                    2600
                );
            };

            const observer = new IntersectionObserver((entries) => {
                if (entries.some((entry) => entry.isIntersecting)) {
                    play();
                    observer.disconnect();
                }
            }, { threshold: 0.12 });
            observer.observe(section);
        });
    };

    // --- 2. Scroll-spy for the sticky nav -------------------------------
    const enhanceScrollSpy = () => {
        if (!('IntersectionObserver' in window)) return;

        const sections = ['history', 'styles', 'musicality', 'glossary']
            .map((id) => document.getElementById(id))
            .filter(Boolean);
        if (!sections.length) return;

        const setActive = (id) => {
            document.querySelectorAll('.edu-nav__link').forEach((link) => {
                link.classList.toggle('edu-nav__link--active', link.getAttribute('href') === `#${id}`);
            });
        };

        const spy = new IntersectionObserver((entries) => {
            const visible = entries.find((entry) => entry.isIntersecting);
            if (visible) setActive(visible.target.id);
        }, { rootMargin: '-38% 0px -52% 0px', threshold: 0 });

        sections.forEach((section) => spy.observe(section));
        setActive(sections[0].id);
    };

    // --- 3. Rhythm map playhead -----------------------------------------
    const enhanceRhythmMap = () => {
        const rhythm = document.querySelector('.edu-rhythm');
        if (!rhythm || !gsap || prefersReducedMotion) return;

        const playhead = rhythm.querySelector('.edu-rhythm__playhead');
        const counts = Array.from(rhythm.querySelectorAll('.edu-rhythm__count'));
        const cellRows = Array.from(rhythm.querySelectorAll('.edu-rhythm__cells'));
        if (!playhead || counts.length !== 8 || !cellRows.length) return;

        const columns = counts.map((count, index) => {
            const column = [count];
            cellRows.forEach((row) => {
                if (row.children[index]) column.push(row.children[index]);
            });
            return column;
        });

        let laneWidth = 0;
        let activeColumn = -1;
        let inView = false;
        let playTween = null;

        const setColumn = (index) => {
            if (index === activeColumn) return;
            if (columns[activeColumn]) {
                columns[activeColumn].forEach((el) => el.classList.remove('is-count-live'));
            }
            activeColumn = index;
            if (columns[activeColumn]) {
                columns[activeColumn].forEach((el) => el.classList.add('is-count-live'));
            }
        };

        const clearColumns = () => setColumn(-1);

        const measure = () => {
            const rhythmRect = rhythm.getBoundingClientRect();
            const firstRow = cellRows[0].getBoundingClientRect();
            const lastRow = cellRows[cellRows.length - 1].getBoundingClientRect();
            const countsRect = rhythm.querySelector('.edu-rhythm__counts').getBoundingClientRect();

            laneWidth = firstRow.width;
            playhead.style.left = `${firstRow.left - rhythmRect.left}px`;
            playhead.style.top = `${countsRect.top - rhythmRect.top}px`;
            playhead.style.height = `${lastRow.bottom - countsRect.top}px`;
        };

        const buildTween = (progress = 0) => {
            if (playTween) playTween.kill();
            playTween = gsap.fromTo(playhead, { x: 0 }, {
                x: () => laneWidth,
                duration: BEAT_SECONDS * 8,
                ease: 'none',
                repeat: -1,
                onUpdate: function updatePlayhead() {
                    setColumn(Math.min(7, Math.floor(this.ratio * 8)));
                }
            });
            playTween.progress(progress);
        };

        const start = () => {
            if (!inView) return;
            rhythm.classList.add('edu-rhythm--live');
            measure();
            if (playTween) {
                playTween.play();
            } else {
                buildTween();
            }
        };

        const stop = () => {
            if (playTween) playTween.pause();
            rhythm.classList.remove('edu-rhythm--live');
            clearColumns();
        };

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                inView = entries.some((entry) => entry.isIntersecting);
                if (inView && !document.hidden) {
                    start();
                } else {
                    stop();
                }
            }, { threshold: 0.2 });
            observer.observe(rhythm);
        } else {
            inView = true;
            start();
        }

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stop();
            } else if (inView) {
                start();
            }
        });

        let resizeFrame = 0;
        window.addEventListener('resize', () => {
            if (resizeFrame) return;
            resizeFrame = window.requestAnimationFrame(() => {
                resizeFrame = 0;
                if (!playTween) return;
                const progress = playTween.progress();
                measure();
                buildTween(progress);
                if (!inView || document.hidden) playTween.pause();
            });
        }, { passive: true });
    };

    // --- 4. Hero string scene (three.js) ---------------------------------
    const enhanceHeroStrings = () => {
        const hero = document.querySelector('.education-hero');
        const canvas = document.querySelector('.edu-hero__canvas');
        if (!hero || !canvas || prefersReducedMotion) return;

        const canUseWebGL = () => {
            if (!window.WebGLRenderingContext) return false;
            try {
                const testCanvas = document.createElement('canvas');
                return Boolean(
                    testCanvas.getContext('webgl') ||
                    testCanvas.getContext('experimental-webgl')
                );
            } catch (error) {
                return false;
            }
        };
        if (!canUseWebGL()) return;

        let threePromise = null;
        const loadThree = () => {
            if (!threePromise) {
                threePromise = import('/assets/vendor/three-0.160.0.module.js')
                    .catch(() => null);
            }
            return threePromise;
        };

        const POINTS = 130;
        const SPAN = 9.4;
        let built = false;
        let renderer = null;
        let scene = null;
        let camera = null;
        let stringGroup = null;
        let strings = [];
        let frame = 0;
        let visible = false;
        let heroInView = false;
        let lastTime = 0;
        let beatClock = 0;
        let count = 0;
        let bronzeIndex = 0;

        const resize = () => {
            if (!renderer || !camera) return;
            const width = Math.max(1, hero.clientWidth);
            const height = Math.max(1, hero.clientHeight);
            renderer.setSize(width, height, false);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
        };

        const pluck = (string, strength) => {
            string.amp = strength;
            string.phase = Math.random() * Math.PI * 2;
        };

        const renderLoop = (time) => {
            if (!visible) return;

            const seconds = time * 0.001;
            const delta = lastTime ? Math.min(0.1, seconds - lastTime) : 0;
            lastTime = seconds;

            // Metronome: one pluck per beat, cycling counts 1-2-3-4. The tap
            // (count 4) goes to the coral string and lands harder.
            beatClock += delta;
            if (beatClock >= BEAT_SECONDS) {
                beatClock -= BEAT_SECONDS;
                count = (count % 4) + 1;
                if (count === 4) {
                    pluck(strings[strings.length - 1], 0.3);
                } else {
                    pluck(strings[bronzeIndex % (strings.length - 1)], 0.17);
                    bronzeIndex += 1;
                }
            }

            strings.forEach((string) => {
                string.amp *= Math.exp(-delta * 2.1);
                const positions = string.line.geometry.attributes.position;
                for (let index = 0; index < POINTS; index += 1) {
                    const t = index / (POINTS - 1);
                    const x = (t - 0.5) * SPAN;
                    const envelope = Math.sin(t * Math.PI);
                    const ripple = Math.sin((t * string.waves * Math.PI * 2) + (seconds * string.speed) + string.phase);
                    const idle = Math.sin((t * 2.2 * Math.PI) + (seconds * 0.6) + string.offset) * 0.014;
                    positions.setY(index, string.baseY + ((ripple * string.amp) + idle) * envelope);
                }
                positions.needsUpdate = true;
                string.line.material.opacity = string.baseOpacity + (string.amp * 1.1);
            });

            renderer.render(scene, camera);
            frame = window.requestAnimationFrame(renderLoop);
        };

        const startLoop = () => {
            if (frame || !renderer) return;
            visible = true;
            lastTime = 0;
            frame = window.requestAnimationFrame(renderLoop);
        };

        const stopLoop = () => {
            visible = false;
            if (frame) {
                window.cancelAnimationFrame(frame);
                frame = 0;
            }
        };

        const build = async () => {
            if (built) return;
            built = true;

            const THREE = await loadThree();
            if (!THREE) return;

            try {
                renderer = new THREE.WebGLRenderer({
                    canvas,
                    alpha: true,
                    antialias: true,
                    powerPreference: 'low-power'
                });
            } catch (error) {
                return;
            }

            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.setClearColor(0x000000, 0);

            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
            camera.position.set(0, 0, 7);

            stringGroup = new THREE.Group();
            stringGroup.rotation.z = -0.055;
            scene.add(stringGroup);

            // Five strings: four bronze (counts 1-2-3) and one coral for the
            // tap, spread across the hero like a fretboard seen up close.
            const layout = [
                { baseY: 1.35, color: 0xe8b04b, baseOpacity: 0.16, waves: 3, speed: 2.3 },
                { baseY: 0.7, color: 0xe8b04b, baseOpacity: 0.2, waves: 4, speed: 2.7 },
                { baseY: 0.05, color: 0xe8b04b, baseOpacity: 0.24, waves: 5, speed: 3.1 },
                { baseY: -0.62, color: 0xe8b04b, baseOpacity: 0.2, waves: 4, speed: 2.5 },
                { baseY: -1.28, color: 0xff5a3c, baseOpacity: 0.26, waves: 3, speed: 2.1 }
            ];

            strings = layout.map((config, stringIndex) => {
                const points = [];
                for (let index = 0; index < POINTS; index += 1) {
                    const t = index / (POINTS - 1);
                    points.push(new THREE.Vector3((t - 0.5) * SPAN, config.baseY, 0));
                }
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({
                    color: config.color,
                    transparent: true,
                    opacity: config.baseOpacity,
                    depthWrite: false
                });
                const line = new THREE.Line(geometry, material);
                stringGroup.add(line);
                return {
                    line,
                    baseY: config.baseY,
                    baseOpacity: config.baseOpacity,
                    waves: config.waves,
                    speed: config.speed,
                    offset: stringIndex * 1.7,
                    amp: 0,
                    phase: 0
                };
            });

            resize();
            startLoop();

            canvas.style.transition = 'opacity 1.1s ease';
            canvas.style.opacity = '1';
        };

        window.addEventListener('resize', resize, { passive: true });

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    heroInView = entry.isIntersecting;
                    if (heroInView) {
                        build();
                        startLoop();
                    } else {
                        stopLoop();
                    }
                });
            }, { threshold: 0.05 });
            observer.observe(hero);
        } else {
            heroInView = true;
            build();
        }

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopLoop();
            } else if (built && heroInView) {
                startLoop();
            }
        });
    };

    enhanceEntrances();
    enhanceScrollSpy();
    enhanceRhythmMap();
    enhanceHeroStrings();
})();

// Gallery page lightbox: click any photo to view it full-screen with prev/next
// arrows, keyboard navigation, and captions. Progressive enhancement over the
// plain <a> links to the 1200w files — without JavaScript (or without native
// <dialog> support) the links simply open the image. showModal() supplies the
// focus trap, ESC handling, and background inertness; all fades live in
// reduced-motion-gated CSS, so this module animates nothing itself.
(function galleryLightbox() {
    if (!document.body.classList.contains('gallery-page')) return;
    if (typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;

    const links = Array.from(document.querySelectorAll('.gallery-item__link'));
    if (!links.length) return;

    const german = (document.documentElement.lang || 'en').toLowerCase().startsWith('de');
    const labels = german
        ? { prev: 'Vorheriges Foto', next: 'Nächstes Foto', close: 'Schliessen', of: 'Foto {i} von {n}' }
        : { prev: 'Previous photo', next: 'Next photo', close: 'Close', of: 'Photo {i} of {n}' };

    const slides = links.map((link) => {
        const img = link.querySelector('img');
        const figure = link.closest('.gallery-item');
        const captionEl = figure ? figure.querySelector('.gallery-caption') : null;
        return {
            link,
            href: link.getAttribute('href'),
            srcset: img ? img.getAttribute('srcset') : '',
            alt: img ? img.getAttribute('alt') : '',
            caption: captionEl ? captionEl.textContent.trim() : ''
        };
    });

    let dialog = null;
    let imgEl = null;
    let captionEl = null;
    let countEl = null;
    let current = 0;
    let opener = null;

    const chevron = (dir) =>
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="' +
        (dir === 'left' ? '15 18 9 12 15 6' : '9 18 15 12 9 6') + '"></polyline></svg>';

    const build = () => {
        dialog = document.createElement('dialog');
        dialog.className = 'gallery-lightbox';
        dialog.innerHTML =
            '<figure class="gallery-lightbox__figure">' +
            '<img class="gallery-lightbox__img" alt="">' +
            '<figcaption class="gallery-lightbox__meta">' +
            '<span class="gallery-lightbox__caption"></span>' +
            '<span class="gallery-lightbox__count"></span>' +
            '</figcaption>' +
            '</figure>' +
            '<button type="button" class="gallery-lightbox__btn gallery-lightbox__btn--close" aria-label="' + labels.close + '">' +
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
            'stroke-linecap="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line>' +
            '<line x1="6" y1="6" x2="18" y2="18"></line></svg></button>' +
            '<button type="button" class="gallery-lightbox__btn gallery-lightbox__btn--prev" aria-label="' + labels.prev + '">' + chevron('left') + '</button>' +
            '<button type="button" class="gallery-lightbox__btn gallery-lightbox__btn--next" aria-label="' + labels.next + '">' + chevron('right') + '</button>';
        document.body.appendChild(dialog);

        imgEl = dialog.querySelector('.gallery-lightbox__img');
        captionEl = dialog.querySelector('.gallery-lightbox__caption');
        countEl = dialog.querySelector('.gallery-lightbox__count');

        dialog.querySelector('.gallery-lightbox__btn--close').addEventListener('click', () => closeLightbox());
        dialog.querySelector('.gallery-lightbox__btn--prev').addEventListener('click', () => update(current - 1));
        dialog.querySelector('.gallery-lightbox__btn--next').addEventListener('click', () => update(current + 1));

        dialog.addEventListener('keydown', (event) => {
            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                update(current - 1);
            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                update(current + 1);
            } else if (event.key === 'Escape') {
                event.preventDefault();
                closeLightbox();
            }
        });

        // A click on the dialog element itself is a click on the backdrop —
        // every visible part of the content is a child element.
        dialog.addEventListener('click', (event) => {
            if (event.target === dialog) closeLightbox();
        });

        // cleanup() is not tied to the close event alone: closeLightbox() runs
        // it directly, and cancel/close cover the native ESC path. It is
        // idempotent, so overlapping paths are harmless.
        dialog.addEventListener('cancel', cleanup);
        dialog.addEventListener('close', cleanup);
    };

    const cleanup = () => {
        document.body.classList.remove('gallery-lightbox-open');
        document.body.style.removeProperty('padding-right');
        // Focus can only leave the dialog once it is closed (the page behind
        // a modal is inert), so the restore is skipped on the cancel event and
        // happens on the close event or in closeLightbox().
        if (!dialog.open && opener) {
            opener.focus();
            opener = null;
        }
    };

    const closeLightbox = () => {
        if (dialog.open) dialog.close();
        cleanup();
    };

    const update = (index) => {
        current = (index + slides.length) % slides.length;
        const slide = slides[current];
        imgEl.src = slide.href;
        if (slide.srcset) imgEl.setAttribute('srcset', slide.srcset);
        imgEl.setAttribute('sizes', '92vw');
        imgEl.alt = slide.alt;
        captionEl.textContent = slide.caption;
        countEl.textContent = labels.of.replace('{i}', current + 1).replace('{n}', slides.length);
        dialog.setAttribute('aria-label', slide.caption || slide.alt);

        // Warm the neighbours so prev/next feels instant.
        [current - 1, current + 1].forEach((n) => {
            const neighbour = slides[(n + slides.length) % slides.length];
            const preload = new Image();
            preload.src = neighbour.href;
        });
    };

    const open = (index, trigger) => {
        if (!dialog) build();
        opener = trigger;
        update(index);
        // Compensate for the vanishing scrollbar so the page does not shift.
        const scrollbar = window.innerWidth - document.documentElement.clientWidth;
        if (scrollbar > 0) document.body.style.paddingRight = scrollbar + 'px';
        document.body.classList.add('gallery-lightbox-open');
        dialog.showModal();
    };

    links.forEach((link, index) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            open(index, link);
        });
    });
})();

/* ============================================================
   SERVICE STEPS — the lead-and-follow rail
   The rail is drawn marker to marker as the section arrives, so the
   eye is handed forward the way a lead hands a follow into the next
   move. Content leads, the rail follows.

   Discipline: transform and opacity only, zero layout shift. The
   resting state is fully visible without JavaScript, the section is
   only armed while it is still below the fold (so nothing that has
   already been read can blink out), and GSAP is fetched from the
   vendored bundle on approach rather than shipped with the page.
   ============================================================ */
(() => {
    const flow = document.querySelector('.service-steps__list');
    if (!flow || !('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const steps = Array.from(flow.querySelectorAll('.service-steps__item'));
    if (!steps.length) return;

    const markers = steps.map((step) => step.querySelector('.service-steps__marker'));
    const bodies = steps.map((step) => step.querySelector('.service-steps__body'));
    const lines = steps.map((step) => step.querySelector('.service-steps__line'));
    const arrows = steps.map((step) => step.querySelector('.service-steps__arrow'));

    let gsapPromise = null;
    const loadGsap = () => {
        if (window.gsap) return Promise.resolve(window.gsap);
        if (gsapPromise) return gsapPromise;

        gsapPromise = new Promise((resolve) => {
            const settle = () => resolve(window.gsap || null);
            const existing = document.querySelector('script[src*="gsap-3.12.5"]');

            if (existing) {
                existing.addEventListener('load', settle, { once: true });
                existing.addEventListener('error', () => resolve(null), { once: true });
            } else {
                const script = document.createElement('script');
                script.src = '/assets/vendor/gsap-3.12.5.min.js';
                script.async = true;
                script.onload = settle;
                script.onerror = () => resolve(null);
                document.head.appendChild(script);
            }

            window.setTimeout(settle, 1500);
        });

        return gsapPromise;
    };

    let armed = false;

    const disarm = () => {
        armed = false;
        flow.removeAttribute('data-flow-armed');
    };

    const run = (gsap) => {
        const stacked = window.matchMedia('(max-width: 768px)').matches;
        const axis = stacked ? 'scaleY' : 'scaleX';
        const origin = stacked ? 'top center' : 'left center';
        const rising = markers.concat(bodies).filter(Boolean);
        const rails = lines.filter(Boolean);
        const heads = arrows.filter(Boolean);

        // Mirror the armed CSS so handing control to GSAP does not jump.
        gsap.set(rising, { opacity: 0, y: 14 });
        gsap.set(rails, { [axis]: 0, transformOrigin: origin });
        gsap.set(heads, { opacity: 0 });

        const timeline = gsap.timeline({
            defaults: { ease: 'power3.out' },
            onComplete: () => {
                gsap.set(rising.concat(rails), { clearProps: 'opacity,transform,transformOrigin' });
                gsap.set(heads, { clearProps: 'opacity' });
                disarm();
            }
        });

        steps.forEach((step, index) => {
            const beat = index * 0.4;
            if (markers[index]) timeline.to(markers[index], { opacity: 1, y: 0, duration: 0.5 }, beat);
            if (bodies[index]) timeline.to(bodies[index], { opacity: 1, y: 0, duration: 0.55 }, beat + 0.08);
            if (lines[index]) timeline.to(lines[index], { [axis]: 1, duration: 0.46, ease: 'power2.inOut' }, beat + 0.2);
            if (arrows[index]) timeline.to(arrows[index], { opacity: 1, duration: 0.28 }, beat + 0.58);
        });
    };

    // Approach: fetch the library and hide the steps, but only while they
    // are still safely below the fold.
    const approach = new IntersectionObserver((entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        approach.disconnect();

        if (flow.getBoundingClientRect().top > window.innerHeight) {
            armed = true;
            flow.setAttribute('data-flow-armed', '');
        }

        loadGsap().then((gsap) => {
            if (!gsap && armed) disarm();
        });
    }, { rootMargin: '0px 0px 600px 0px' });

    // Arrival: play, or restore instantly if the library is not there yet.
    const arrival = new IntersectionObserver((entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        arrival.disconnect();

        if (!armed) return;
        if (window.gsap) run(window.gsap);
        else disarm();
    }, { threshold: 0.15 });

    approach.observe(flow);
    arrival.observe(flow);
})();
