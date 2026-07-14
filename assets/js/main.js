/* ============================================
   MFS — Main JavaScript
   Detroit Precision. Silicon Valley Speed.
   ============================================ */

(function () {
  'use strict';

  /* ---------- Navigation Scroll Effect ---------- */
  const nav = document.querySelector('.nav');
  let lastScroll = 0;

  function handleNavScroll() {
    const currentScroll = window.scrollY;
    if (currentScroll > 60) {
      nav.classList.add('nav--scrolled');
    } else {
      nav.classList.remove('nav--scrolled');
    }
    lastScroll = currentScroll;
  }

  window.addEventListener('scroll', handleNavScroll, { passive: true });

  /* ---------- Mobile Navigation ---------- */
  const navToggle = document.querySelector('.nav__toggle');
  const mobileOverlay = document.querySelector('.nav__mobile-overlay');
  const mobileClose = document.querySelector('.nav__mobile-close');

  if (navToggle && mobileOverlay) {
    navToggle.addEventListener('click', function () {
      mobileOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });

    function closeMobileNav() {
      mobileOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }

    if (mobileClose) {
      mobileClose.addEventListener('click', closeMobileNav);
    }

    mobileOverlay.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeMobileNav);
    });
  }

  /* ---------- Smooth Scroll for Anchor Links ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        var navHeight = nav ? nav.offsetHeight : 0;
        var targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight - 20;
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  /* ---------- Scroll Reveal Animations ---------- */
  function initReveal() {
    var reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal--visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    });

    reveals.forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ---------- Animated Counters ---------- */
  function animateCounter(element) {
    var target = element.getAttribute('data-target');
    var suffix = element.getAttribute('data-suffix') || '';
    var prefix = element.getAttribute('data-prefix') || '';
    var duration = 2000;
    var startTime = null;
    var targetNum = parseFloat(target);

    function easeOutQuart(t) {
      return 1 - Math.pow(1 - t, 4);
    }

    function update(currentTime) {
      if (!startTime) startTime = currentTime;
      var elapsed = currentTime - startTime;
      var progress = Math.min(elapsed / duration, 1);
      var easedProgress = easeOutQuart(progress);
      var current = Math.floor(easedProgress * targetNum);

      element.textContent = prefix + current + suffix;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = prefix + target + suffix;
      }
    }

    requestAnimationFrame(update);
  }

  function initCounters() {
    var counters = document.querySelectorAll('[data-counter]');
    if (!counters.length) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.5
    });

    counters.forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ---------- Hero Particles ---------- */
  function initParticles() {
    var container = document.querySelector('.hero__particles');
    if (!container) return;

    for (var i = 0; i < 40; i++) {
      var particle = document.createElement('div');
      particle.classList.add('hero__particle');
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 10 + 's';
      particle.style.animationDuration = (7 + Math.random() * 8) + 's';
      var size = (2 + Math.random() * 4) + 'px';
      particle.style.width = size;
      particle.style.height = size;
      container.appendChild(particle);
    }
  }

  /* ---------- Application Form ---------- */
  function initForm() {
    var form = document.getElementById('application-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var formData = new FormData(form);
      var data = {};
      formData.forEach(function (value, key) {
        data[key] = value;
      });

      // Validate required fields
      var requiredFields = form.querySelectorAll('[required]');
      var allValid = true;
      requiredFields.forEach(function (field) {
        if (!field.value.trim()) {
          allValid = false;
          field.style.borderColor = '#ff4444';
          field.addEventListener('input', function handler() {
            field.style.borderColor = '';
            field.removeEventListener('input', handler);
          });
        }
      });

      if (!allValid) return;

      // Disable submit button while sending
      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Booking...';
      }

      // Send to Formspree (replace YOUR_FORM_ID with your actual Formspree form ID)
      // Sign up free at https://formspree.io, create a form, and paste the ID below
      var FORMSPREE_ENDPOINT = 'https://formspree.io/f/mvzblonl';

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function (response) {
        if (response.ok) {
          // Show success state
          var formContent = form.querySelector('.form-grid');
          var submitSection = form.querySelector('.form__submit');
          var noteSection = form.querySelector('.form__note');
          var successMessage = form.querySelector('.form-success');

          if (formContent) formContent.style.display = 'none';
          if (submitSection) submitSection.style.display = 'none';
          if (noteSection) noteSection.style.display = 'none';
          if (successMessage) successMessage.classList.add('active');
        } else {
          throw new Error('Submission failed');
        }
      })
      .catch(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Book Appointment';
        }
        alert('Something went wrong. Please try again or email us directly.');
      });
    });
  }

  /* ---------- Case Studies Carousel ---------- */
  function initCarousel() {
    var carousel = document.querySelector('.carousel');
    if (!carousel) return;

    var track = carousel.querySelector('.carousel__track');
    var slides = carousel.querySelectorAll('.carousel__slide');
    var prevBtn = carousel.querySelector('.carousel__btn--prev');
    var nextBtn = carousel.querySelector('.carousel__btn--next');
    var dotsContainer = carousel.querySelector('.carousel__dots');
    var current = 0;
    var total = slides.length;

    // Build dot indicators
    for (var i = 0; i < total; i++) {
      var dot = document.createElement('button');
      dot.className = 'carousel__dot' + (i === 0 ? ' carousel__dot--active' : '');
      dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      dot.setAttribute('data-index', i);
      dotsContainer.appendChild(dot);
    }
    var dots = dotsContainer.querySelectorAll('.carousel__dot');

    function goTo(index) {
      if (index < 0) index = total - 1;
      if (index >= total) index = 0;
      current = index;
      track.style.transform = 'translateX(-' + (current * 100) + '%)';
      dots.forEach(function (d, di) {
        d.classList.toggle('carousel__dot--active', di === current);
      });
    }

    prevBtn.addEventListener('click', function () { goTo(current - 1); });
    nextBtn.addEventListener('click', function () { goTo(current + 1); });

    dotsContainer.addEventListener('click', function (e) {
      var dot = e.target.closest('.carousel__dot');
      if (dot) goTo(parseInt(dot.getAttribute('data-index'), 10));
    });

    // Touch / swipe support
    var startX = 0;
    var dragging = false;

    track.addEventListener('touchstart', function (e) {
      startX = e.touches[0].clientX;
      dragging = true;
    }, { passive: true });

    track.addEventListener('touchend', function (e) {
      if (!dragging) return;
      dragging = false;
      var diff = startX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) {
        goTo(diff > 0 ? current + 1 : current - 1);
      }
    });

    // Auto-advance every 6 seconds, pause on hover
    var autoplay = setInterval(function () { goTo(current + 1); }, 6000);

    carousel.addEventListener('mouseenter', function () { clearInterval(autoplay); });
    carousel.addEventListener('mouseleave', function () {
      autoplay = setInterval(function () { goTo(current + 1); }, 6000);
    });
  }

  /* ---------- Google Reviews ---------- */
  // Cache duration for review responses (24h). Prevents hammering the Places API on every
  // page load. Cache lives in sessionStorage so a hard reload picks up fresh data next day.
  var REVIEWS_CACHE_KEY = 'mfs_reviews_v1';
  var REVIEWS_CACHE_TTL_MS = 24 * 60 * 60 * 1000;
  var REVIEWS_QUERY = 'Mully Fulfillment Services Detroit';

  function renderStars(rating, size) {
    size = size || 16;
    var full = Math.round(rating);
    var out = '';
    for (var i = 0; i < 5; i++) {
      var fill = i < full ? '#FBBC05' : '#E4E8EF';
      out += '<svg width="' + size + '" height="' + size + '" viewBox="0 0 20 20" aria-hidden="true">'
          + '<path fill="' + fill + '" d="M10 1.5l2.6 5.3 5.9.9-4.3 4.2 1 5.9L10 15l-5.3 2.8 1-5.9L1.5 7.7l5.9-.9z"/></svg>';
    }
    return out;
  }

  function formatRelativeTime(rev) {
    if (rev.relative_time_description) return rev.relative_time_description;
    if (rev.time) {
      var d = new Date(rev.time * 1000);
      return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    }
    return '';
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
  }

  function renderReviews(place) {
    var summaryRating = document.querySelector('[data-reviews-rating]');
    var summaryStars = document.querySelector('[data-reviews-stars]');
    var summaryTotal = document.querySelector('[data-reviews-total]');
    var grid = document.querySelector('[data-reviews-grid]');

    if (!place) {
      if (summaryTotal) summaryTotal.textContent = 'Read reviews on Google';
      return;
    }

    var rating = place.rating != null ? place.rating.toFixed(1) : '5.0';
    var total = place.user_ratings_total || 0;

    if (summaryRating) summaryRating.textContent = rating;
    if (summaryStars) summaryStars.innerHTML = renderStars(place.rating || 5, 18);
    if (summaryTotal) summaryTotal.textContent = 'Rated ' + rating + ' from ' + total + ' Google review' + (total === 1 ? '' : 's');

    if (!grid) return;
    var reviews = (place.reviews || []).slice(0, 3);
    if (!reviews.length) { grid.style.display = 'none'; return; }

    grid.innerHTML = reviews.map(function (r) {
      var author = escapeHtml(r.author_name || 'Google reviewer');
      var text = escapeHtml(r.text || '');
      var when = escapeHtml(formatRelativeTime(r));
      var initials = author.split(/\s+/).map(function(p){return p[0]||'';}).slice(0,2).join('').toUpperCase();
      var photo = r.profile_photo_url ? '<img class="review-card__avatar-img" src="' + escapeHtml(r.profile_photo_url) + '" alt="" loading="lazy" referrerpolicy="no-referrer">'
                                       : '<span class="review-card__avatar-fallback">' + initials + '</span>';
      var link = r.author_url ? escapeHtml(r.author_url) : '#';
      return ''
        + '<a class="review-card" href="' + link + '" target="_blank" rel="noopener" role="listitem">'
        +   '<div class="review-card__head">'
        +     '<span class="review-card__avatar">' + photo + '</span>'
        +     '<div class="review-card__who">'
        +       '<div class="review-card__name">' + author + '</div>'
        +       '<div class="review-card__when">' + when + '</div>'
        +     '</div>'
        +     '<span class="review-card__g" aria-hidden="true">'
        +       '<svg viewBox="0 0 48 48" width="20" height="20"><path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/><path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 40.98 15.4 46 24 46z"/><path fill="#FBBC05" d="M11.69 28.18c-.44-1.32-.69-2.72-.69-4.18s.25-2.86.69-4.18v-5.7H4.34C2.85 17.09 2 20.44 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/><path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.42 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2 15.4 2 7.96 7.02 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg>'
        +     '</span>'
        +   '</div>'
        +   '<div class="review-card__stars">' + renderStars(r.rating || 5, 14) + '</div>'
        +   '<p class="review-card__text">' + text + '</p>'
        + '</a>';
    }).join('');
  }

  function loadReviewsFromCache() {
    try {
      var raw = sessionStorage.getItem(REVIEWS_CACHE_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || !parsed.savedAt) return null;
      if (Date.now() - parsed.savedAt > REVIEWS_CACHE_TTL_MS) return null;
      return parsed.place;
    } catch (e) { return null; }
  }

  function saveReviewsToCache(place) {
    try {
      // Trim data to essentials before caching to keep sessionStorage small
      var trimmed = {
        rating: place.rating,
        user_ratings_total: place.user_ratings_total,
        reviews: (place.reviews || []).map(function (r) {
          return {
            author_name: r.author_name,
            author_url: r.author_url,
            profile_photo_url: r.profile_photo_url,
            rating: r.rating,
            relative_time_description: r.relative_time_description,
            text: r.text,
            time: r.time
          };
        })
      };
      sessionStorage.setItem(REVIEWS_CACHE_KEY, JSON.stringify({ savedAt: Date.now(), place: trimmed }));
    } catch (e) { /* ignore quota errors */ }
  }

  function normalizePlace(p) {
    // Modern Place API returns camelCase (userRatingCount, displayName, etc.).
    // Coerce into the shape the classic renderer expects.
    var reviews = (p.reviews || []).map(function (r) {
      var authorName = r.authorAttribution ? r.authorAttribution.displayName : (r.author_name || 'Google reviewer');
      var authorUri  = r.authorAttribution ? r.authorAttribution.uri : r.author_url;
      var authorPic  = r.authorAttribution ? r.authorAttribution.photoURI : r.profile_photo_url;
      var text = (r.text && r.text.text) ? r.text.text : (typeof r.text === 'string' ? r.text : (r.originalText && r.originalText.text) || '');
      var timeSec = r.publishTime ? Math.floor(new Date(r.publishTime).getTime() / 1000) : r.time;
      return {
        author_name: authorName,
        author_url: authorUri,
        profile_photo_url: authorPic,
        rating: r.rating,
        relative_time_description: r.relativePublishTimeDescription || r.relative_time_description,
        text: text,
        time: timeSec
      };
    });
    return {
      rating: p.rating,
      user_ratings_total: p.userRatingCount != null ? p.userRatingCount : p.user_ratings_total,
      reviews: reviews
    };
  }

  async function fetchReviewsNewApi() {
    // Use the modern google.maps.places.Place API (post-March-2025 default).
    var placesLib = await google.maps.importLibrary('places');
    var Place = placesLib.Place;

    // Step 1: text-search to resolve the place id
    var searchRes = await Place.searchByText({
      textQuery: REVIEWS_QUERY,
      fields: ['id', 'displayName'],
      maxResultCount: 1
    });
    var first = (searchRes && searchRes.places && searchRes.places[0]) || null;
    if (!first) {
      console.warn('[reviews] no place found');
      renderReviews(null);
      return;
    }

    // Step 2: fetch rating + reviews
    var place = new Place({ id: first.id });
    await place.fetchFields({ fields: ['rating', 'userRatingCount', 'reviews'] });

    var normalized = normalizePlace(place);
    renderReviews(normalized);
    saveReviewsToCache(normalized);
  }

  function fetchReviewsLegacy() {
    if (!window.google || !google.maps || !google.maps.places || !google.maps.places.PlacesService) return;
    var container = document.createElement('div');
    var svc = new google.maps.places.PlacesService(container);

    svc.findPlaceFromQuery({
      query: REVIEWS_QUERY,
      fields: ['place_id']
    }, function (results, status) {
      if (status !== google.maps.places.PlacesServiceStatus.OK || !results || !results[0]) {
        console.warn('[reviews] legacy findPlace failed:', status);
        renderReviews(null);
        return;
      }
      svc.getDetails({
        placeId: results[0].place_id,
        fields: ['rating', 'user_ratings_total', 'reviews']
      }, function (place, status2) {
        if (status2 !== google.maps.places.PlacesServiceStatus.OK || !place) {
          console.warn('[reviews] legacy getDetails failed:', status2);
          renderReviews(null);
          return;
        }
        renderReviews(place);
        saveReviewsToCache(place);
      });
    });
  }

  function fetchReviews() {
    if (!window.google || !google.maps || !google.maps.places) return;
    // Prefer modern Place API; fall back to classic PlacesService if unavailable.
    if (google.maps.places.Place && typeof google.maps.places.Place.searchByText === 'function') {
      fetchReviewsNewApi().catch(function (err) {
        console.warn('[reviews] new API failed, falling back:', err);
        fetchReviewsLegacy();
      });
    } else {
      fetchReviewsLegacy();
    }
  }

  function initReviews() {
    // Instant paint from cache if we have it
    var cached = loadReviewsFromCache();
    if (cached) renderReviews(cached);

    // Expose the async-load callback the Maps script will invoke
    window.onGoogleMapsReady = function () { fetchReviews(); };

    // Handle the case where the script already loaded before this ran
    if (window.google && google.maps && google.maps.places) fetchReviews();
  }

  /* ---------- Init All ---------- */
  function init() {
    initReveal();
    initCounters();
    initParticles();
    initForm();
    initCarousel();
    initReviews();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
