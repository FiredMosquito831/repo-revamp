/* Progressive enhancement only: the site reads completely without JavaScript. */
(function () {
  "use strict";

  function addCopyButtons() {
    var blocks = document.querySelectorAll(".code-block");
    Array.prototype.forEach.call(blocks, function (block) {
      var pre = block.querySelector("pre");
      if (!pre) return;
      var button = document.createElement("button");
      button.type = "button";
      button.className = "copy btn btn-secondary";
      button.textContent = "Copy";
      button.setAttribute("aria-label", "Copy this code block");
      button.addEventListener("click", function () {
        var text = pre.innerText;
        if (!navigator.clipboard || !navigator.clipboard.writeText) return;
        navigator.clipboard.writeText(text).then(function () {
          button.textContent = "Copied";
          window.setTimeout(function () { button.textContent = "Copy"; }, 1600);
        });
      });
      block.insertBefore(button, pre);
    });
  }

  function markCurrentSection() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
    if (!links.length || !("IntersectionObserver" in window)) return;
    var targets = links.map(function (link) {
      return document.getElementById(link.getAttribute("href").slice(1));
    });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) { link.classList.remove("is-current"); });
        var index = targets.indexOf(entry.target);
        if (index >= 0) links[index].classList.add("is-current");
      });
    }, { rootMargin: "-15% 0px -70% 0px" });
    targets.forEach(function (target) { if (target) observer.observe(target); });
  }

  function init() {
    addCopyButtons();
    markCurrentSection();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
