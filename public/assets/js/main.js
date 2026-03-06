document.querySelectorAll('[data-before-after]').forEach((root) => {
  const range = root.querySelector('input[type="range"]');
  const wrap = root.querySelector('.after-wrap');
  if (!range || !wrap) return;
  function update() {
    requestAnimationFrame(function () {
      wrap.style.width = range.value + '%';
    });
  }
  range.addEventListener('input', update);
  update();
});

document.querySelectorAll('[data-year]').forEach((el) => {
  el.textContent = new Date().getFullYear();
});

(function mobileNav() {
  const btn = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');
  if (!btn || !nav) return;
  btn.setAttribute('aria-expanded', 'false');
  btn.addEventListener('click', function () {
    const open = nav.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  });
  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      nav.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });
})();

const revealNodes = document.querySelectorAll('[data-reveal]');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12 },
  );
  revealNodes.forEach(function (node) { observer.observe(node); });
} else {
  revealNodes.forEach(function (node) { node.classList.add('is-visible'); });
}