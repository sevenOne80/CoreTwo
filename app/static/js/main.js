/* CoreTwo — main.js */

// Navbar scroll effect
const nav = document.getElementById('mainNav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 30);
  }, { passive: true });
}

// Animated counters
function animateCounters() {
  document.querySelectorAll('.ct-counter').forEach(el => {
    const target = +el.dataset.target;
    const step = target / 60;
    let current = 0;
    const tick = () => {
      current = Math.min(current + step, target);
      el.textContent = Math.floor(current);
      if (current < target) requestAnimationFrame(tick);
    };
    tick();
  });
}

// Trigger counters when trust bar enters viewport
const trustBar = document.querySelector('.ct-trust-bar');
if (trustBar) {
  const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      animateCounters();
      observer.disconnect();
    }
  }, { threshold: .4 });
  observer.observe(trustBar);
}

// Product card radio selection highlight
document.querySelectorAll('.ct-product-card').forEach(card => {
  card.addEventListener('click', () => {
    const radio = card.querySelector('.ct-product-radio');
    if (radio) radio.checked = true;
  });
});

// Smooth scroll to top
document.querySelectorAll('a[href="#"]').forEach(a => {
  a.addEventListener('click', e => e.preventDefault());
});
