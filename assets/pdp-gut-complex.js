/* Veltia Labs PDP: product interactions. No dependencies. */
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

  // Round a cent amount up to the next .99 (matches Kaching's ".99" price rounding).
  const roundUp99 = (cents) => Math.ceil((cents + 1) / 100) * 100 - 1;

  // "$69.99" -> 6999. Prices without cents ("$70") are read as whole units.
  const toCents = (text) => {
    const t = (text || '').trim();
    const digits = t.replace(/\D/g, '');
    if (!digits) return null;
    return /[.,]\d{2}\D*$/.test(t) ? Number(digits) : Number(digits) * 100;
  };

  class PdpProduct extends HTMLElement {
    connectedCallback() {
      const json = this.querySelector('[data-pdp-json]');
      this.data = json ? JSON.parse(json.textContent) : { variants: [] };
      this.moneyFormat = this.dataset.moneyFormat;
      this.form = this.querySelector('[data-pdp-form]');
      this.variantInput = this.querySelector('[data-variant-input]');
      this.planInput = this.querySelector('[data-plan-input]');
      this.qtyInput = this.querySelector('[data-qty-input]');
      this.subToggle = this.querySelector('[data-subscribe-toggle]');
      this.planSelect = this.querySelector('[data-plan-select]');

      // Offers: quantity tiers (single-variant products) or one per variant.
      const tierCards = [...this.querySelectorAll('[data-tier-card]')];
      this.tierMode = tierCards.length > 0;
      const base = this.data.variants[0];
      if (this.tierMode) {
        this.offers = tierCards.map((card) => ({
          key: card.dataset.tierCard,
          position: Number(card.dataset.tierCard),
          card,
          title: card.dataset.tierTitle,
          qty: Number(card.dataset.tierQty) || 1,
          price: Number(card.dataset.tierPrice),
          raw: Number(card.dataset.tierRaw || card.dataset.tierPrice),
          compare: Number(card.dataset.tierCompare),
          variant: base,
        }));
        const checked = tierCards.find((c) => c.querySelector('[data-tier-radio]')?.checked) || tierCards[0];
        this.offer = this.offers.find((o) => o.card === checked);
      } else {
        this.offers = this.data.variants.map((v) => ({
          key: String(v.id),
          position: v.position,
          card: this.querySelector(`[data-variant-card="${v.id}"]`),
          title: v.title,
          qty: null,
          price: v.price,
          compare: v.compareAtPrice || 0,
          bottles: v.bottles || 1,
          variant: v,
        }));
        const initialId = Number(this.variantInput?.value);
        this.offer = this.offers.find((o) => o.variant.id === initialId) || this.offers[0];
      }

      this.bindOfferInputs();
      this.bindSubscription();
      this.bindQuantity();
      this.bindForm();
      this.initGallery();
      this.initDelivery();
      this.initSticky();
      this.render();
      if (this.hasAttribute('data-bundle-app')) this.bindBundleApp();
    }

    /* ---------- state ---------- */

    get subscribed() {
      return Boolean(this.subToggle && this.subToggle.checked && this.planSelect);
    }

    get planId() {
      return this.subscribed ? this.planSelect.value : '';
    }

    // Subscription price ratio for the selected plan, e.g. 0.8 for 20% off.
    planRatio(variant, planId) {
      const planPrice = variant.plans ? variant.plans[planId] : null;
      return planPrice != null && variant.price > 0 ? planPrice / variant.price : 1;
    }

    priceFor(offer) {
      if (!this.subscribed) return offer.price;
      if (this.tierMode) {
        const ratio = this.planRatio(offer.variant, this.planId);
        return ratio < 1 ? roundUp99(Math.round(offer.raw * ratio)) : offer.price;
      }
      const planPrice = offer.variant.plans ? offer.variant.plans[this.planId] : null;
      return planPrice != null ? planPrice : offer.price;
    }

    compareFor(offer) {
      return Math.max(offer.compare || 0, this.subscribed ? offer.price : 0);
    }

    money(cents) {
      return formatMoney(cents, this.moneyFormat);
    }

    /* ---------- bindings ---------- */

    bindOfferInputs() {
      this.querySelectorAll('[data-tier-radio], [data-variant-radio]').forEach((radio) => {
        radio.addEventListener('change', () => {
          if (!radio.checked) return;
          const offer = this.offers.find((o) => o.key === radio.value);
          if (offer) this.setOffer(offer);
        });
      });
    }

    bindSubscription() {
      this.subToggle?.addEventListener('change', () => this.render());
      this.planSelect?.addEventListener('change', () => this.render());
    }

    bindQuantity() {
      const input = this.qtyInput;
      if (!input || input.type === 'hidden') return;
      const clamp = (n) => Math.min(99, Math.max(1, n || 1));
      this.querySelector('[data-qty-minus]')?.addEventListener('click', () => { input.value = clamp(+input.value - 1); });
      this.querySelector('[data-qty-plus]')?.addEventListener('click', () => { input.value = clamp(+input.value + 1); });
      input.addEventListener('change', () => { input.value = clamp(+input.value); });
    }

    setOffer(offer) {
      this.offer = offer;
      this.render();
      if (!this.tierMode) {
        const { variant } = offer;
        if (variant.mediaId) this.goToMedia(variant.mediaId);
        const url = new URL(window.location.href);
        url.searchParams.set('variant', variant.id);
        window.history.replaceState({}, '', url.toString());
      }
      this.dispatchEvent(new CustomEvent('pdp:offer-change', { bubbles: true, detail: { offer } }));
    }

    /* ---------- rendering ---------- */

    render() {
      const offer = this.offer;
      if (!offer) return;
      const v = offer.variant;
      const price = this.priceFor(offer);
      const compare = this.compareFor(offer);
      const savings = compare > price ? compare - price : 0;
      const fill = (template, s, c) => template
        .replace('[savings]', this.money(s))
        .replace('[percent]', `${c > 0 ? Math.round((s / c) * 100) : 0}%`);

      if (this.variantInput) this.variantInput.value = v.id;
      if (this.planInput) this.planInput.value = this.planId;
      if (offer.qty && this.qtyInput) this.qtyInput.value = offer.qty;

      const planWrap = this.querySelector('[data-plan-wrap]');
      if (planWrap) planWrap.hidden = !this.subscribed;

      // Main price + sale pill
      this.setText('[data-price]', this.money(price));
      this.toggleEl('[data-compare]', savings > 0, this.money(compare));
      const pill = this.querySelector('[data-sale-pill]');
      if (pill) {
        pill.hidden = savings === 0;
        pill.textContent = fill(pill.dataset.template, savings, compare);
      }

      // Subscription savings pill
      const subPct = this.planSelect ? Math.round((1 - this.planRatio(v, this.planSelect.value)) * 100) : 0;
      const subPill = this.querySelector('[data-sub-save]');
      if (subPill) {
        subPill.hidden = subPct <= 0;
        this.setText('[data-sub-save-pct]', String(subPct));
      }

      // Bundle cards
      this.offers.forEach((o) => {
        if (!o.card) return;
        const cPrice = this.priceFor(o);
        const cCompare = this.compareFor(o);
        const cSavings = cCompare > cPrice ? cCompare - cPrice : 0;
        const selected = o === offer;
        const radio = o.card.querySelector('input[type="radio"]');
        if (radio) radio.checked = selected;
        o.card.classList.toggle('is-selected', selected);
        const priceEl = o.card.querySelector('[data-card-price]');
        if (priceEl) priceEl.textContent = this.money(cPrice);
        const compareEl = o.card.querySelector('[data-card-compare]');
        if (compareEl) {
          compareEl.hidden = cSavings === 0;
          compareEl.textContent = this.money(cCompare);
        }
        const unitEl = o.card.querySelector('[data-card-unit]');
        if (unitEl) unitEl.textContent = this.money(Math.round(cPrice / (o.qty || o.bottles || 1)));
        const noteEl = o.card.querySelector('[data-card-note]');
        if (noteEl && noteEl.dataset.template) noteEl.textContent = fill(noteEl.dataset.template, cSavings, cCompare);
      });

      // Gifts unlock by bundle position
      this.querySelectorAll('[data-gift-unlock]').forEach((gift) => {
        gift.classList.toggle('is-locked', offer.position < Number(gift.dataset.giftUnlock || 1));
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
      const stickyMeta = this.querySelector('[data-sticky-variant]');
      if (stickyMeta && this.offers.length > 1) {
        stickyMeta.textContent = this.subscribed ? `${offer.title} · Subscribe & Save` : offer.title;
      }
    }

    // Only write when the text changes, so the bundle-app observer below doesn't re-trigger itself.
    setText(selector, text) {
      this.querySelectorAll(selector).forEach((el) => { if (el.textContent !== text) el.textContent = text; });
    }

    toggleEl(selector, show, text) {
      this.querySelectorAll(selector).forEach((el) => {
        el.hidden = !show;
        if (text != null && el.textContent !== text) el.textContent = text;
      });
    }

    /* ---------- bundle app (Kaching Bundles) ---------- */

    // The app owns the tiers and prices. Mirror its selected deal into our price line and Add to Cart button.
    bindBundleApp() {
      const sync = () => {
        const bar = this.querySelector('.kaching-bundles__bar--selected');
        const price = toCents(bar?.querySelector('.kaching-bundles__bar-price')?.textContent);
        if (price == null) return;
        const full = toCents(bar.querySelector('.kaching-bundles__bar-full-price')?.textContent) || 0;
        const savings = full > price ? full - price : 0;
        const line = this.querySelector('[data-bundle-price]');
        if (line) line.hidden = false;
        this.setText('[data-bundle-now], [data-atc-price]', this.money(price));
        this.toggleEl('[data-bundle-was], [data-atc-compare]', savings > 0, this.money(full));
        this.querySelectorAll('[data-bundle-pill]').forEach((pill) => {
          pill.hidden = savings === 0;
          const text = pill.dataset.template.replace('[savings]', this.money(savings));
          if (pill.textContent !== text) pill.textContent = text;
        });
      };
      const schedule = () => {
        cancelAnimationFrame(this.bundleFrame);
        this.bundleFrame = requestAnimationFrame(sync);
      };
      this.addEventListener('change', (event) => {
        if (event.target.name?.startsWith('kaching-bundles-deal')) schedule();
      });
      // Catches the app's first render and any re-render.
      new MutationObserver(schedule).observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
      schedule();
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

  /* Timeline (section: pdp-timeline): the line fills as you scroll and each stage lights up as the
     fill reaches its bubble. Without JS the timeline shows fully, all stages active. */
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let timelineTicking = false;
  const updateTimelines = () => {
    timelineTicking = false;
    const target = window.innerHeight * 0.6;
    document.querySelectorAll('[data-timeline]').forEach((list) => {
      list.classList.add('is-scrolly');
      const box = list.getBoundingClientRect();
      const fill = Math.max(0, Math.min(box.height - 36, target - box.top - 18));
      list.style.setProperty('--pdp-tl-fill', `${fill}px`);
      list.querySelectorAll('.pdp-timeline__item').forEach((item) => {
        const num = item.querySelector('.pdp-timeline__num');
        const center = num.getBoundingClientRect().top + num.offsetHeight / 2;
        item.classList.toggle('is-active', reduceMotion || center <= target);
      });
    });
  };
  const onTimelineScroll = () => {
    if (timelineTicking) return;
    timelineTicking = true;
    requestAnimationFrame(updateTimelines);
  };
  const initTimelines = () => {
    if (!document.querySelector('[data-timeline]')) return;
    if (!initTimelines.bound) {
      initTimelines.bound = true;
      window.addEventListener('scroll', onTimelineScroll, { passive: true });
      window.addEventListener('resize', onTimelineScroll);
    }
    updateTimelines();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initTimelines);
  else initTimelines();
  document.addEventListener('shopify:section:load', initTimelines);

  /* Review slider: arrows + dots under a horizontal card scroller (section: pdp-reviews) */
  const initSliders = () => {
    document.querySelectorAll('[data-slider-root]').forEach((root) => {
      const track = root.querySelector('[data-slider]');
      const nav = root.querySelector('[data-slider-nav]');
      if (!track || !nav || root.dataset.sliderReady) return;
      root.dataset.sliderReady = 'true';
      const items = [...track.children];
      const dots = [...nav.querySelectorAll('[data-slider-dot]')];
      const prev = nav.querySelector('[data-slider-prev]');
      const next = nav.querySelector('[data-slider-next]');
      const behavior = reduceMotion ? 'auto' : 'smooth';
      const offsetOf = (item) => item.getBoundingClientRect().left - items[0].getBoundingClientRect().left;
      const step = () => (items[1] ? offsetOf(items[1]) : track.clientWidth);
      const update = () => {
        const max = track.scrollWidth - track.clientWidth;
        nav.hidden = max <= 4;
        const index = track.scrollLeft >= max - 4 ? items.length - 1 : Math.round(track.scrollLeft / step());
        dots.forEach((dot, n) => {
          dot.classList.toggle('is-active', n === index);
          dot.setAttribute('aria-current', String(n === index));
        });
        prev.disabled = track.scrollLeft <= 4;
        next.disabled = track.scrollLeft >= max - 4;
      };
      prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior }));
      next.addEventListener('click', () => track.scrollBy({ left: step(), behavior }));
      dots.forEach((dot, n) => dot.addEventListener('click', () => track.scrollTo({ left: offsetOf(items[n]), behavior })));
      track.addEventListener('scroll', () => requestAnimationFrame(update), { passive: true });
      window.addEventListener('resize', update);
      update();
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSliders);
  else initSliders();
  document.addEventListener('shopify:section:load', initSliders);

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
