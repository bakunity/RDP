(() => {
  'use strict';

  const header = document.querySelector('[data-header]');
  const nav = document.querySelector('[data-nav]');
  const navToggle = document.querySelector('[data-nav-toggle]');
  const toast = document.querySelector('[data-toast]');
  const year = document.querySelector('[data-year]');
  const tabs = [...document.querySelectorAll('[data-step]')];
  const panels = [...document.querySelectorAll('[data-panel]')];
  const terminalTitle = document.querySelector('[data-terminal-title]');

  if (year) year.textContent = String(new Date().getFullYear());

  const setHeaderState = () => {
    header?.classList.toggle('scrolled', window.scrollY > 18);
  };

  setHeaderState();
  window.addEventListener('scroll', setHeaderState, { passive: true });

  navToggle?.addEventListener('click', () => {
    const isOpen = nav?.classList.toggle('open') ?? false;
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  nav?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      navToggle?.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('click', (event) => {
    if (!nav || !navToggle || !nav.classList.contains('open')) return;
    if (nav.contains(event.target) || navToggle.contains(event.target)) return;
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  });

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -32px' });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('visible'));
  }

  const titles = {
    server: 'SERVER · BASH',
    pair: 'TELEGRAM · PAIRING',
    windows: 'WINDOWS · POWERSHELL',
    check: 'REMOTE CLIENT · POWERSHELL'
  };

  const activateTab = (name) => {
    tabs.forEach((tab) => {
      const isActive = tab.dataset.step === name;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
    });

    panels.forEach((panel) => {
      const isActive = panel.dataset.panel === name;
      panel.classList.toggle('active', isActive);
      panel.hidden = !isActive;
    });

    if (terminalTitle) terminalTitle.textContent = titles[name] || 'TERMINAL';
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab.dataset.step));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'ArrowRight'
        ? (index + 1) % tabs.length
        : (index - 1 + tabs.length) % tabs.length;
      tabs[next].focus();
      activateTab(tabs[next].dataset.step);
    });
  });

  let toastTimer;
  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('visible'), 1800);
  };

  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const target = document.querySelector(button.dataset.copy);
      const text = target?.innerText?.trim();
      if (!text) return;

      try {
        await navigator.clipboard.writeText(text);
        showToast('Команда скопирована');
      } catch {
        const area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.append(area);
        area.select();
        const copied = document.execCommand('copy');
        area.remove();
        showToast(copied ? 'Команда скопирована' : 'Не удалось скопировать');
      }
    });
  });
})();
