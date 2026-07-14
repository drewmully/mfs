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

  /* ---------- Init All ---------- */
  function init() {
    initReveal();
    initCounters();
    initParticles();
    initForm();
    initCarousel();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
