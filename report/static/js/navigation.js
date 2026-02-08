(function () {
  "use strict";

  var recentEvents = new Map();
  var queuedEvents = [];
  var flushTimer = null;

  function canTrack() {
    return typeof window.umami === "object" && typeof window.umami.track === "function";
  }

  function sanitizeValue(value) {
    if (value === null || value === undefined) {
      return "";
    }
    if (typeof value === "number" || typeof value === "boolean") {
      return value;
    }
    return String(value).trim().slice(0, 140);
  }

  function sanitizePayload(payload) {
    if (!payload || typeof payload !== "object") {
      return {};
    }

    var clean = {};
    Object.keys(payload).forEach(function (key) {
      clean[key] = sanitizeValue(payload[key]);
    });
    return clean;
  }

  function trackNow(eventName, payload) {
    var safeName = String(eventName || "").trim().slice(0, 50);
    if (!safeName) {
      return;
    }

    var safePayload = sanitizePayload(payload);

    if (canTrack()) {
      window.umami.track(safeName, safePayload);
      return;
    }

    queuedEvents.push([safeName, safePayload]);
    scheduleFlush();
  }

  function flushQueue() {
    if (!canTrack() || queuedEvents.length === 0) {
      return;
    }

    while (queuedEvents.length > 0) {
      var event = queuedEvents.shift();
      window.umami.track(event[0], event[1]);
    }

    if (flushTimer) {
      clearInterval(flushTimer);
      flushTimer = null;
    }
  }

  function scheduleFlush() {
    if (flushTimer) {
      return;
    }

    flushTimer = setInterval(function () {
      flushQueue();
    }, 1000);
  }

  function shouldTrack(throttleKey, throttleMs) {
    if (!throttleKey || !throttleMs || throttleMs < 1) {
      return true;
    }

    var now = Date.now();
    var previous = recentEvents.get(throttleKey) || 0;
    if (now - previous < throttleMs) {
      return false;
    }

    recentEvents.set(throttleKey, now);
    return true;
  }

  function trackNavigation(eventName, payload, options) {
    var settings = options || {};

    if (
      settings.throttleKey &&
      !shouldTrack(settings.throttleKey, settings.throttleMs || 0)
    ) {
      return;
    }

    trackNow(eventName, payload);
  }

  function pagePath() {
    return window.location.pathname || "/";
  }

  function safeTarget(event) {
    return event && event.target instanceof Element ? event.target : null;
  }

  function getLabel(element) {
    if (!element) {
      return "";
    }

    return (
      element.getAttribute("aria-label") ||
      element.getAttribute("title") ||
      element.textContent ||
      ""
    )
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 80);
  }

  function trackLinkClick(link) {
    var href = link.getAttribute("href") || "";
    var isExternal = link.host && link.host !== window.location.host;
    var popupLink = link.closest(".leaflet-popup-content") !== null;

    trackNavigation("nav_link_click", {
      page: pagePath(),
      href: href,
      text: getLabel(link),
      external: isExternal
    });

    if (popupLink) {
      trackNavigation("map_popup_link_click", {
        page: pagePath(),
        href: href
      });
    }
  }

  function trackButtonClick(button) {
    trackNavigation("nav_button_click", {
      page: pagePath(),
      text: getLabel(button),
      type: button.getAttribute("type") || button.tagName.toLowerCase()
    });
  }

  function trackMapAndGraphClick(target) {
    var inLeaflet = target.closest(".leaflet-container") !== null;
    var marker = target.closest(".leaflet-interactive") !== null;
    var graphPoint =
      target.closest("#wind_plot rect") !== null ||
      target.closest("#wind_plot path") !== null ||
      target.closest("#windrose path") !== null;

    if (marker) {
      trackNavigation(
        "map_marker_dom_click",
        { page: pagePath() },
        { throttleKey: "marker:" + pagePath(), throttleMs: 300 }
      );
      return;
    }

    if (inLeaflet) {
      trackNavigation(
        "map_canvas_click",
        { page: pagePath() },
        { throttleKey: "map:" + pagePath(), throttleMs: 1000 }
      );
    }

    if (graphPoint) {
      trackNavigation(
        "graph_tap_dom",
        { page: pagePath() },
        { throttleKey: "graph-tap:" + pagePath(), throttleMs: 500 }
      );
    }
  }

  function trackGraphHover(target) {
    if (target.closest("#wind_plot rect") === null) {
      return;
    }

    trackNavigation(
      "graph_hover",
      { page: pagePath() },
      { throttleKey: "graph-hover:" + pagePath(), throttleMs: 15000 }
    );
  }

  function onDocumentClick(event) {
    var target = safeTarget(event);
    if (!target) {
      return;
    }

    var link = target.closest("a[href]");
    if (link) {
      trackLinkClick(link);
    }

    var button = target.closest(
      "button, input[type='submit'], input[type='button']"
    );
    if (button) {
      trackButtonClick(button);
    }

    trackMapAndGraphClick(target);
  }

  function onDocumentSubmit(event) {
    if (!(event.target instanceof HTMLFormElement)) {
      return;
    }

    var form = event.target;
    trackNavigation("form_submit", {
      page: pagePath(),
      action: form.getAttribute("action") || pagePath(),
      method: form.getAttribute("method") || "get"
    });
  }

  function init() {
    document.addEventListener("click", onDocumentClick, true);
    document.addEventListener("submit", onDocumentSubmit, true);
    document.addEventListener(
      "mouseover",
      function (event) {
        var target = safeTarget(event);
        if (!target) {
          return;
        }
        trackGraphHover(target);
      },
      true
    );

    flushQueue();
  }

  window.trackNavigation = trackNavigation;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("load", flushQueue);
})();
