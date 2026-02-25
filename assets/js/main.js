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

    for (var i = 0; i < 30; i++) {
      var particle = document.createElement('div');
      particle.classList.add('hero__particle');
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 8 + 's';
      particle.style.animationDuration = (6 + Math.random() * 6) + 's';
      particle.style.width = (1 + Math.random() * 2) + 'px';
      particle.style.height = particle.style.width;
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

      // Show success state
      var formContent = form.querySelector('.form-grid');
      var submitSection = form.querySelector('.form__submit');
      var successMessage = form.querySelector('.form-success');

      if (formContent) formContent.style.display = 'none';
      if (submitSection) submitSection.style.display = 'none';
      if (successMessage) successMessage.classList.add('active');

      // Log data for integration
      console.log('MFS Application Submitted:', data);
    });
  }

  /* ---------- Init All ---------- */
  function init() {
    initReveal();
    initCounters();
    initParticles();
    initForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
