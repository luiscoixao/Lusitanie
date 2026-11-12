/* Lecture à voix haute des articles (voix de synthèse de l'appareil). */
(function () {
  var bloc = document.querySelector(".ecouter");
  var synth = window.speechSynthesis;
  if (!bloc || !synth || typeof SpeechSynthesisUtterance === "undefined") return;

  var bouton = bloc.querySelector(".ecouter-bouton");
  var stop = bloc.querySelector(".ecouter-stop");
  var etat = "arret"; // arret | lecture | pause
  var morceaux = [], index = 0, voix = null;

  function choisirVoix() {
    var liste = synth.getVoices().filter(function (v) { return /^fr/i.test(v.lang); });
    if (!liste.length) return null;
    function score(v) {
      var s = 0;
      if (/fr[-_]FR/i.test(v.lang)) s += 10;
      if (/premium|enhanced|natural|neural|online/i.test(v.name)) s += 6;
      if (/am[ée]lie|audrey|thomas|marie|denise|henri|eloise|vivienne|remy|google/i.test(v.name)) s += 3;
      if (/compact|eddy|flo|grandma|grandpa|reed|rocko|sandy|shelley/i.test(v.name)) s -= 8;
      return s;
    }
    return liste.sort(function (a, b) { return score(b) - score(a); })[0];
  }
  voix = choisirVoix();
  if (synth.addEventListener) synth.addEventListener("voiceschanged", function () { voix = choisirVoix(); });

  function texteArticle() {
    var parties = [];
    var h1 = document.querySelector(".article-entete h1");
    var chapo = document.querySelector(".article-entete .chapo");
    if (h1) parties.push(h1.textContent + ".");
    if (chapo) parties.push(chapo.textContent);
    document.querySelectorAll(".corps p, .corps h2, .corps h3, .corps li, .corps blockquote").forEach(function (el) {
      if (el.closest("blockquote") && el.tagName !== "BLOCKQUOTE") return;
      var t = el.textContent.replace(/\s+/g, " ").trim();
      if (t) parties.push(/[.!?»:]$/.test(t) ? t : t + ".");
    });
    // Découpage en phrases courtes : certains navigateurs coupent les longues lectures.
    var res = [];
    parties.forEach(function (p) {
      var phrases = p.match(/[^.!?…]+[.!?…»]*\s*/g) || [p];
      var cur = "";
      phrases.forEach(function (ph) {
        if ((cur + ph).length > 220 && cur) { res.push(cur.trim()); cur = ""; }
        cur += ph;
      });
      if (cur.trim()) res.push(cur.trim());
    });
    return res;
  }

  function afficher() {
    bouton.textContent = etat === "lecture" ? "❚❚ Pause" : etat === "pause" ? "▶ Reprendre" : "▶ Écouter l'article";
    bouton.setAttribute("aria-pressed", etat === "lecture" ? "true" : "false");
    stop.hidden = etat === "arret";
  }

  function lireSuivant() {
    if (etat !== "lecture") return;
    if (index >= morceaux.length) { etat = "arret"; index = 0; afficher(); return; }
    var u = new SpeechSynthesisUtterance(morceaux[index]);
    u.lang = "fr-FR";
    if (voix) u.voice = voix;
    u.rate = 1;
    u.onend = function () { index++; lireSuivant(); };
    u.onerror = function (e) { if (e.error !== "interrupted" && e.error !== "canceled") { index++; lireSuivant(); } };
    synth.speak(u);
  }

  bouton.addEventListener("click", function () {
    if (etat === "arret") {
      synth.cancel();
      morceaux = texteArticle(); index = 0; etat = "lecture"; afficher(); lireSuivant();
    } else if (etat === "lecture") {
      etat = "pause"; synth.pause(); afficher();
    } else {
      etat = "lecture"; afficher();
      if (synth.paused) synth.resume(); else lireSuivant();
    }
  });
  stop.addEventListener("click", function () { etat = "arret"; index = 0; synth.cancel(); afficher(); });
  window.addEventListener("pagehide", function () { synth.cancel(); });

  bloc.hidden = false;
  afficher();
})();
