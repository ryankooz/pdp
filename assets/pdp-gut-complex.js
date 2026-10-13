/* Gut Complex PDP: product interactions. No dependencies. */
(() => {
  if (customElements.get('pdp-product')) return;

  const formatMoney = (cents, format) => {
    const value = typeof cents === 'string' ? parseInt(cents.replace('.', ''), 10) : cents;
    const fmt = format || '${{amount}}';
    const withDelimiters = (num, precision, thousands = ',', decimal = '.') => {
      if (Number.isNaN(num) || num == null) return '0';
      const [whole, frac] = (num / 100).toFixed(precision).split('.');
      const grouped = whole.replace(/(\d)(?=(\d{3})+(?!\d))/g, `$1${thousands}`);
      return frac ? grouped + decimal + frac : grouped;
    };
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, (_, key) => {
      switch (key) {
        case 'amount_no_decimals': return withDelimiters(value, 0);
        case 'amount_with_comma_separator': return withDelimiters(value, 2, '.', ',');
        case 'amount_no_decimals_with_comma_separator': return withDelimiters(value, 0, '.', ',');
        case 'amount_with_apostrophe_separator': return withDelimiters(value, 2, "'", '.');
        case 'amount_with_space_separator': return withDelimiters(value, 2, ' ', ',');
        default: return withDelimiters(value, 2);
      }
    });
  };

  const ordinal = (n) => {
    const s = ['th', 'st', 'nd', 'rd'];
    const v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  };

  const addBusinessDays = (date, days) => {
    const d = new Date(date);
    let added = 0;
    while (added < days) {
      d.setDate(d.getDate() + 1);
      const day = d.getDay();
      if (day !== 0 && day !== 6) added += 1;
    }
    return d;
  };

  class PdpProduct extends HTMLElement {
    connectedCallback() {
      const json = this.querySelector('[data-pdp-json]');
      this.data = json ? JSON.parse(json.textContent) : { variants: [] };
      this.moneyFormat = this.dataset.moneyFormat;
      this.form = this.querySelector('[data-pdp-form]');
      this.variantInput = this.querySelector('[data-variant-input]');
      this.planInput = this.querySelector('[data-plan-input]');
      this.subToggle = this.querySelector('[data-subscribe-toggle]');
      this.planSelect = this.querySelector('[data-plan-select]');

      const initialId = Number(this.variantInput?.value);
      this.variant = this.data.variants.find((v) => v.id === initialId) || this.data.variants[0];

      this.bindVariantInputs();
      this.bindSubscription();
      this.bindQuantity();
      this.bindForm();
      this.initGallery();
      this.initDelivery();
      this.initSticky();
      this.render();
    }

    /* ---------- state ---------- */

    get subscribed() {
      return Boolean(this.subToggle && this.subToggle.checked && this.planSelect);
    }

    get planId() {
      return this.subscribed ? this.planSelect.value : '';
    }

    priceFor(variant) {
      if (this.subscribed && variant.plans && variant.plans[this.planId] != null) {
        return variant.plans[this.planId];
      }
      return variant.price;
    }

    compareFor(variant) {
      return Math.max(variant.compareAtPrice || 0, this.subscribed ? variant.price : 0);
    }

    money(cents) {
      return formatMoney(cents, this.moneyFormat);
    }

    /* ---------- bindings ---------- */

    bindVariantInputs() {
      this.querySelectorAll('[data-variant-radio]').forEach((radio) => {
        radio.addEventListener('change', () => {
          if (!radio.checked) return;
          this.setVariant(Number(radio.value));
        });
      });

      const selects = [...this.querySelectorAll('[data-option-select]')];
      selects.forEach((select) => {
        select.addEventListener('change', () => {
          const values = selects.map((s) => s.value);
          const match = this.data.variants.find((v) => v.options.every((o, i) => o === values[i]));
          if (match) this.setVariant(match.id);
        });
      });
    }

    bindSubscription() {
      this.subToggle?.addEventListener('change', () => this.render());
      this.planSelect?.addEventListener('change', () => this.render());
    }

    bindQuantity() {
      const input = this.querySelector('[data-qty-input]');
      if (!input || input.type === 'hidden') return;
      const clamp = (n) => Math.min(99, Math.max(1, n || 1));
      this.querySelector('[data-qty-minus]')?.addEventListener('click', () => { input.value = clamp(+input.value - 1); });
      this.querySelector('[data-qty-plus]')?.addEventListener('click', () => { input.value = clamp(+input.value + 1); });
      input.addEventListener('change', () => { input.value = clamp(+input.value); });
    }

    setVariant(id) {
      const variant = this.data.variants.find((v) => v.id === id);
      if (!variant) return;
      this.variant = variant;
      this.render();
      if (variant.mediaId) this.goToMedia(variant.mediaId);
      const url = new URL(window.location.href);
      url.searchParams.set('variant', variant.id);
      window.history.replaceState({}, '', url.toString());
      this.dispatchEvent(new CustomEvent('pdp:variant-change', { bubbles: true, detail: { variant } }));
    }

    /* ---------- rendering ---------- */

    render() {
      const v = this.variant;
      if (!v) return;
      const price = this.priceFor(v);
      const compare = this.compareFor(v);
      const savings = compare > price ? compare - price : 0;

      if (this.variantInput) this.variantInput.value = v.id;
      if (this.planInput) this.planInput.value = this.planId;

      const planWrap = this.querySelector('[data-plan-wrap]');
      if (planWrap) planWrap.hidden = !this.subscribed;

      // Main price
      this.setText('[data-price]', this.money(price));
      this.toggleEl('[data-compare]', savings > 0, this.money(compare));
      const pill = this.querySelector('[data-sale-pill]');
      if (pill) {
        pill.hidden = savings === 0;
        pill.textContent = pill.dataset.template.replace('[savings]', this.money(savings));
      }

      // Subscription savings pill
      const planPrice = this.planSelect && v.plans ? v.plans[this.planSelect.value] : null;
      const subPct = planPrice != null && v.price > 0 ? Math.round(((v.price - planPrice) / v.price) * 100) : 0;
      const subPill = this.querySelector('[data-sub-save]');
      if (subPill) {
        subPill.hidden = subPct <= 0;
        this.setText('[data-sub-save-pct]', String(subPct));
      }

      // Bundle cards
      this.querySelectorAll('[data-variant-card]').forEach((card) => {
        const cv = this.data.variants.find((x) => x.id === Number(card.dataset.variantCard));
        if (!cv) return;
        const cPrice = this.priceFor(cv);
        const cCompare = this.compareFor(cv);
        const cSavings = cCompare > cPrice ? cCompare - cPrice : 0;
        const radio = card.querySelector('[data-variant-radio]');
        if (radio) radio.checked = cv.id === v.id;
        card.classList.toggle('is-selected', cv.id === v.id);
        const priceEl = card.querySelector('[data-card-price]');
        if (priceEl) priceEl.textContent = this.money(cPrice);
        const compareEl = card.querySelector('[data-card-compare]');
        if (compareEl) {
          compareEl.hidden = cSavings === 0;
          compareEl.textContent = this.money(cCompare);
        }
        const unitEl = card.querySelector('[data-card-unit]');
        if (unitEl) unitEl.textContent = this.money(Math.round(cPrice / (cv.bottles || 1)));
        const noteEl = card.querySelector('[data-card-note]');
        if (noteEl && noteEl.dataset.template) {
          noteEl.textContent = noteEl.dataset.template.replace('[savings]', this.money(cSavings));
        }
      });

      // Gifts
      this.querySelectorAll('[data-gift-unlock]').forEach((gift) => {
        const unlocked = v.position >= Number(gift.dataset.giftUnlock || 1);
        gift.classList.toggle('is-locked', !unlocked);
      });

      // Add to cart
      const atc = this.querySelector('[data-atc]');
      const label = v.available ? this.data.atcLabel : 'Sold out';
      if (atc) atc.disabled = !v.available;
      this.setText('[data-atc-label]', label);
      this.setText('[data-atc-price]', this.money(price));
      this.toggleEl('[data-atc-compare]', savings > 0, this.money(compare));

      // Sticky bar
      const stickyBtn = this.querySelector('[data-sticky-atc]');
      if (stickyBtn) stickyBtn.disabled = !v.available;
      this.setText('[data-sticky-label]', label);
      this.setText('[data-sticky-price]', this.money(price));
      const stickyVariant = this.querySelector('[data-sticky-variant]');
      if (stickyVariant && this.data.variants.length > 1) {
        stickyVariant.textContent = this.subscribed ? `${v.title} · Subscribe & Save` : v.title;
      }
    }

    setText(selector, text) {
      this.querySelectorAll(selector).forEach((el) => { el.textContent = text; });
    }

    toggleEl(selector, show, text) {
      this.querySelectorAll(selector).forEach((el) => {
        el.hidden = !show;
        if (text != null) el.textContent = text;
      });
    }

    /* ---------- cart ---------- */

    bindForm() {
      if (!this.form) return;
      this.form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const atc = this.querySelector('[data-atc]');
        const errorEl = this.querySelector('[data-atc-error]');
        const successEl = this.querySelector('[data-atc-success]');
        if (!atc || atc.disabled) return;

        atc.classList.add('is-loading');
        atc.setAttribute('aria-busy', 'true');
        if (errorEl) errorEl.hidden = true;
        if (successEl) successEl.hidden = true;

        const body = new FormData(this.form);
        if (!body.get('selling_plan')) body.delete('selling_plan');

        try {
          const response = await fetch(`${this.dataset.cartAddUrl}.js`, {
            method: 'POST',
            headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
            body,
          });
          const result = await response.json();
          if (!response.ok || result.status) {
            throw new Error(result.description || result.message || 'Something went wrong. Please try again.');
          }

          document.dispatchEvent(new CustomEvent('pdp:added', { detail: { item: result } }));
          // Common theme hook names so existing cart drawers can refresh themselves.
          document.dispatchEvent(new CustomEvent('cart:refresh', { detail: { item: result } }));

          const after = this.dataset.afterAdd;
          if (after === 'checkout') {
            window.location.href = this.dataset.checkoutUrl;
          } else if (after === 'cart') {
            window.location.href = this.dataset.cartUrl;
          } else {
            if (successEl) successEl.hidden = false;
            this.refreshCartCount();
          }
        } catch (error) {
          if (errorEl) {
            errorEl.textContent = error.message;
            errorEl.hidden = false;
          }
        } finally {
          atc.classList.remove('is-loading');
          atc.removeAttribute('aria-busy');
        }
      });
    }

    async refreshCartCount() {
      try {
        const cart = await fetch(`${this.dataset.cartUrl}.js`, { headers: { Accept: 'application/json' } }).then((r) => r.json());
        document.querySelectorAll('[data-cart-count], .cart-count-bubble span[aria-hidden="true"], .cart-count').forEach((el) => {
          el.textContent = cart.item_count;
        });
      } catch (e) {
        /* the cart icon will update on next page load */
      }
    }

    /* ---------- gallery ---------- */

    initGallery() {
      this.track = this.querySelector('[data-gallery-track]');
      if (!this.track) return;
      this.slides = [...this.track.children];
      this.thumbs = [...this.querySelectorAll('[data-thumb-index]')];

      this.thumbs.forEach((thumb) => {
        thumb.addEventListener('click', () => this.goToSlide(Number(thumb.dataset.thumbIndex)));
      });
      this.querySelector('[data-gallery-prev]')?.addEventListener('click', () => this.goToSlide(this.currentSlide - 1));
      this.querySelector('[data-gallery-next]')?.addEventListener('click', () => this.goToSlide(this.currentSlide + 1));

      this.currentSlide = 0;
      let ticking = false;
      this.track.addEventListener('scroll', () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          ticking = false;
          const index = Math.round(this.track.scrollLeft / this.track.clientWidth);
          if (index !== this.currentSlide) this.markSlide(index);
        });
      }, { passive: true });
    }

    goToSlide(index) {
      if (!this.slides || !this.slides.length) return;
      const count = this.slides.length;
      const next = (index + count) % count;
      this.track.scrollTo({ left: next * this.track.clientWidth, behavior: 'smooth' });
      this.markSlide(next);
    }

    goToMedia(mediaId) {
      const index = this.slides ? this.slides.findIndex((s) => Number(s.dataset.mediaId) === mediaId) : -1;
      if (index >= 0) this.goToSlide(index);
    }

    markSlide(index) {
      this.currentSlide = index;
      this.thumbs.forEach((t, i) => t.classList.toggle('is-active', i === index));
      const callouts = this.querySelector('[data-gallery-callouts]');
      if (callouts) callouts.classList.toggle('is-hidden', index !== 0);
    }

    /* ---------- delivery estimate ---------- */

    initDelivery() {
      const el = this.querySelector('[data-delivery]');
      if (!el) return;
      const now = new Date();
      const cutoff = Number(el.dataset.cutoffHour || 14);
      const start = new Date(now);
      if (now.getHours() >= cutoff) start.setDate(start.getDate() + 1);
      const min = addBusinessDays(start, Number(el.dataset.minDays || 3));
      const max = addBusinessDays(start, Number(el.dataset.maxDays || 5));
      const month = (d) => d.toLocaleDateString(undefined, { month: 'short' });
      let label = `${month(max)} ${ordinal(max.getDate())}`;
      if (min.getTime() !== max.getTime()) {
        label = min.getMonth() === max.getMonth()
          ? `${month(min)} ${ordinal(min.getDate())} – ${ordinal(max.getDate())}`
          : `${month(min)} ${ordinal(min.getDate())} – ${label}`;
      }
      const target = el.querySelector('[data-delivery-date]');
      if (target) target.textContent = label;
      el.hidden = false;
    }

    /* ---------- sticky add to cart ---------- */

    initSticky() {
      const sticky = this.querySelector('[data-sticky]');
      const atc = this.querySelector('[data-atc]');
      if (!sticky || !atc || !('IntersectionObserver' in window)) return;

      const button = sticky.querySelector('[data-sticky-atc]');
      button?.addEventListener('click', () => {
        if (this.form.requestSubmit) this.form.requestSubmit(atc);
        else atc.click();
      });

      const observer = new IntersectionObserver(([entry]) => {
        const passed = !entry.isIntersecting && entry.boundingClientRect.top < 0;
        sticky.classList.toggle('is-visible', passed);
        if (button) button.tabIndex = passed ? 0 : -1;
        sticky.setAttribute('aria-hidden', String(!passed));
      });
      observer.observe(atc);
    }
  }

  customElements.define('pdp-product', PdpProduct);

  /* Ingredient flip cards (section: pdp-ingredients) */
  document.addEventListener('click', (event) => {
    const card = event.target.closest('[data-flip-card]');
    if (!card) return;
    const flipped = card.classList.toggle('is-flipped');
    card.setAttribute('aria-pressed', String(flipped));
  });

  /* Countdown (section: pdp-promo-bar) */
  const initCountdowns = () => {
    document.querySelectorAll('[data-countdown]').forEach((el) => {
      if (el.dataset.ready) return;
      el.dataset.ready = 'true';
      const end = el.dataset.end ? new Date(el.dataset.end) : null;
      const parts = {
        d: el.querySelector('[data-cd-d]'),
        h: el.querySelector('[data-cd-h]'),
        m: el.querySelector('[data-cd-m]'),
        s: el.querySelector('[data-cd-s]'),
      };
      const pad = (n) => String(n).padStart(2, '0');
      const tick = () => {
        let target = end;
        if (!target || Number.isNaN(target.getTime())) {
          target = new Date();
          target.setHours(23, 59, 59, 999);
        }
        const diff = Math.max(0, target - new Date());
        if (diff === 0 && end) {
          el.closest('[data-promo-bar]')?.setAttribute('hidden', '');
          return;
        }
        const total = Math.floor(diff / 1000);
        const days = Math.floor(total / 86400);
        el.querySelectorAll('[data-cd-days-wrap]').forEach((w) => { w.hidden = days === 0; });
        if (parts.d) parts.d.textContent = pad(days);
        if (parts.h) parts.h.textContent = pad(Math.floor((total % 86400) / 3600));
        if (parts.m) parts.m.textContent = pad(Math.floor((total % 3600) / 60));
        if (parts.s) parts.s.textContent = pad(total % 60);
        setTimeout(tick, 1000);
      };
      tick();
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCountdowns);
  else initCountdowns();
  document.addEventListener('shopify:section:load', initCountdowns);
})();
