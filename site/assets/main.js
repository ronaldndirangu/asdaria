(() => {
  "use strict";

  const EMAIL = "asdaria.ltd@gmail.com";

  const menu = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#primary-nav");
  if (menu && nav) {
    document.documentElement.classList.add("nav-enhanced");
    menu.hidden = false;
    const setMenu = (open) => {
      menu.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    menu.addEventListener("click", () => setMenu(menu.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true") {
        setMenu(false);
        menu.focus();
      }
    });
    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) setMenu(false);
    });
    const siteHeader = menu.closest(".site-header");
    siteHeader.addEventListener("focusout", (event) => {
      if (event.relatedTarget && !siteHeader.contains(event.relatedTarget)) setMenu(false);
    });
    document.addEventListener("click", (event) => {
      if (!nav.contains(event.target) && !menu.contains(event.target)) setMenu(false);
    });
    window.matchMedia("(min-width: 761px)").addEventListener("change", () => setMenu(false));
  }

  const enhanceDialog = (dialog, step) => {
    const focusables = () => [...dialog.querySelectorAll("button, a[href]")].filter((element) => element.getClientRects().length);
    dialog.querySelector(".dialog-prev").addEventListener("click", () => step(-1));
    dialog.querySelector(".dialog-next").addEventListener("click", () => step(1));
    dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
    dialog.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        step(event.key === "ArrowRight" ? 1 : -1);
      } else if (event.key === "Tab") {
        const items = focusables();
        const first = items[0];
        const last = items[items.length - 1];
        if (document.activeElement === (event.shiftKey ? first : last) || !dialog.contains(document.activeElement)) {
          event.preventDefault();
          (event.shiftKey ? last : first).focus();
        }
      }
    });
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  };

  const dialog = document.querySelector(".image-dialog");
  if (dialog && typeof dialog.showModal === "function") {
    const links = [...document.querySelectorAll(".gallery-open")];
    const image = dialog.querySelector("img");
    const caption = dialog.querySelector(".dialog-caption");
    const count = dialog.querySelector(".dialog-count");
    let current = 0;
    const show = (index) => {
      current = (index + links.length) % links.length;
      const link = links[current];
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      caption.textContent = link.dataset.caption;
      count.textContent = `${current + 1} of ${links.length}`;
    };
    links.forEach((link, index) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        show(index);
        dialog.showModal();
      });
    });
    enhanceDialog(dialog, (delta) => show(current + delta));
    dialog.addEventListener("close", () => links[current].focus());
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const reveals = document.querySelectorAll(".reveal");
  if (reveals.length && "IntersectionObserver" in window && !reducedMotion.matches) {
    document.documentElement.classList.add("motion-ok");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    reveals.forEach((element) => observer.observe(element));
  }

  const tablist = document.querySelector(".xp-tabs");
  if (tablist) {
    const bar = tablist.parentElement;
    const label = document.getElementById(tablist.getAttribute("aria-labelledby"));
    const siteHeader = document.querySelector(".site-header");
    const tabs = [...tablist.querySelectorAll('[role="tab"]')];
    const panels = tabs.map((tab) => document.getElementById(tab.getAttribute("aria-controls")));
    const panelArea = panels[0].parentElement;
    const show = (index) => {
      tabs.forEach((tab, i) => {
        const selected = i === index;
        tab.setAttribute("aria-selected", String(selected));
        tab.tabIndex = selected ? 0 : -1;
        // until-found keeps inactive panels reachable by browser Find and text fragments, which fire beforematch.
        if (selected) {
          panels[i].removeAttribute("hidden");
          panels[i].removeAttribute("aria-hidden");
        } else {
          panels[i].setAttribute("hidden", "until-found");
          panels[i].setAttribute("aria-hidden", "true");
        }
      });
    };
    const activate = (index) => {
      show(index);
      history.replaceState(null, "", `#${panels[index].id}`);
      // When the reader is past the start of the lists, bring the tabs and the new list's start back into view.
      const offset = siteHeader.offsetHeight + bar.offsetHeight + parseFloat(getComputedStyle(bar).marginBottom);
      const top = panelArea.getBoundingClientRect().top;
      if (top < offset) window.scrollBy({ top: top - offset, behavior: "instant" });
    };
    const hashTarget = () => {
      const id = decodeURIComponent(location.hash.slice(1));
      return id ? document.getElementById(id) : null;
    };
    const reveal = (target, behavior) => {
      const index = panels.findIndex((panel) => panel.contains(target));
      if (index >= 0) show(index);
      target.scrollIntoView({ block: "start", behavior });
    };
    panels.forEach((panel, i) => {
      panel.setAttribute("role", "tabpanel");
      panel.addEventListener("beforematch", () => show(i));
    });
    tabs.forEach((tab, i) => tab.addEventListener("click", () => activate(i)));
    tablist.addEventListener("keydown", (event) => {
      const current = tabs.indexOf(document.activeElement);
      const next = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: tabs.length - 1 }[event.key];
      if (current < 0 || next === undefined) return;
      event.preventDefault();
      const index = (next + tabs.length) % tabs.length;
      tabs[index].focus({ preventScroll: true });
      activate(index);
    });
    panelArea.querySelectorAll(".xp-next").forEach((link) => {
      link.addEventListener("click", (event) => {
        const index = panels.findIndex((panel) => `#${panel.id}` === link.hash);
        if (index < 0) return;
        event.preventDefault();
        activate(index);
        tabs[index].focus({ preventScroll: true });
      });
    });
    if ("ResizeObserver" in window) {
      new ResizeObserver(() => document.documentElement.style.setProperty("--xp-tabs-h", `${bar.offsetHeight}px`)).observe(bar);
    }
    bar.closest(".xp-directors").classList.add("is-tabbed");
    label.hidden = false;
    bar.hidden = false;
    show(0);
    const initial = hashTarget();
    if (initial) reveal(initial, "instant");
    window.addEventListener("hashchange", () => {
      const target = hashTarget();
      if (target) reveal(target, reducedMotion.matches ? "instant" : "smooth");
    });
  }

  const form = document.querySelector("#brief-form");
  if (form) {
    form.hidden = false;
    const output = document.querySelector("#brief-output");
    const result = document.querySelector(".brief-result");
    const status = document.querySelector("#brief-status");
    const draftLink = document.querySelector("#draft-link");
    const reset = () => {
      result.hidden = true;
      output.textContent = "";
      status.textContent = "";
      draftLink.removeAttribute("href");
    };
    form.addEventListener("input", reset);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const name = form.elements.namedItem("name");
      const message = form.elements.namedItem("message");
      name.setCustomValidity(name.value.trim() ? "" : "Enter your name.");
      message.setCustomValidity(message.value.trim().length >= 20 ? "" : "Describe your project in at least 20 characters.");
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const value = (key) => String(data.get(key) || "").trim();
      const organisation = value("organisation");
      const subject = `Project enquiry: ${value("interest")}${organisation ? `, ${organisation}` : ""}`;
      const body = [
        `Name: ${value("name")}`,
        `Organisation: ${organisation || "Not specified"}`,
        `Area of interest: ${value("interest")}`,
        "",
        value("message"),
      ].join("\n");
      const href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      output.textContent = `To: ${EMAIL}\nSubject: ${subject}\n\n${body}`;
      draftLink.href = href;
      result.hidden = false;
      status.textContent = "Your email app should open with the draft. Nothing is sent until you send it.";
      draftLink.click();
    });
    for (const field of [form.elements.namedItem("name"), form.elements.namedItem("message")]) {
      field.addEventListener("input", () => field.setCustomValidity(""));
    }
    document.querySelector("#copy-brief").addEventListener("click", async () => {
      try {
        if (!navigator.clipboard) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(output.textContent);
        status.textContent = "Text copied. Paste it into an email to " + EMAIL + ".";
      } catch {
        const range = document.createRange();
        range.selectNodeContents(output);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = "Automatic copying is unavailable. The text is selected; copy it manually.";
      }
    });
    window.addEventListener("pageshow", (event) => {
      if (event.persisted) reset();
    });
  }
})();
