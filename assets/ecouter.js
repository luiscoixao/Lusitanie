/* Lecture à voix haute des articles (voix de synthèse de l'appareil). */
(function () {
  var bloc = document.querySelector(".ecouter");
  var synth = window.speechSynthesis;
  if (!bloc || !synth || typeof SpeechSynthesisUtterance === "undefined") return;

  var bouton = bloc.querySelector(".ecouter-bouton");
  var stop = bloc.querySelector(".ecouter-stop");
  var etat = "arret"; // arret | lecture | pause
  var morceaux = [], index = 0, voix = null, courant = null, jeton = 0;
  var pt = /^pt/i.test(document.documentElement.lang || "");
  var LANGUE = pt ? "pt-PT" : "fr-FR";
  var TXT = pt ? { lire: "▶ Ouvir o artigo", pause: "❚❚ Pausa", reprendre: "▶ Continuar" }
               : { lire: "▶ Écouter l'article", pause: "❚❚ Pause", reprendre: "▶ Reprendre" };

  function choisirVoix() {
    var prefixe = pt ? /^pt/i : /^fr/i;
    var liste = synth.getVoices().filter(function (v) { return prefixe.test(v.lang); });
    if (!liste.length) return null;
    function score(v) {
      var s = 0;
      if (pt ? /pt[-_]PT/i.test(v.lang) : /fr[-_]FR/i.test(v.lang)) s += 10;
      if (/premium|enhanced|natural|neural|online/i.test(v.name)) s += 6;
      if (/am[ée]lie|audrey|thomas|marie|denise|henri|eloise|vivienne|remy|joana|catarina|raquel|duarte|fernanda|google/i.test(v.name)) s += 3;
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
    bouton.textContent = etat === "lecture" ? TXT.pause : etat === "pause" ? TXT.reprendre : TXT.lire;
    bouton.setAttribute("aria-pressed", etat === "lecture" ? "true" : "false");
    stop.hidden = etat === "arret";
  }

  function lireSuivant() {
    if (etat !== "lecture") return;
    if (index >= morceaux.length) { etat = "arret"; index = 0; afficher(); return; }
    var monJeton = ++jeton;
    var u = new SpeechSynthesisUtterance(morceaux[index]);
    courant = u; // garder une référence : sinon Safari perd l'événement de fin
    u.lang = LANGUE;
    if (voix) u.voice = voix;
    u.rate = 1;
    u.onend = function () { if (monJeton !== jeton) return; index++; lireSuivant(); };
    u.onerror = function (e) {
      if (monJeton !== jeton || e.error === "interrupted" || e.error === "canceled") return;
      if (e.error === "voice-unavailable" || e.error === "synthesis-failed") voix = null;
      index++; lireSuivant();
    };
    synth.speak(u);
  }

  // Pause = on arrête la phrase en cours et on reprendra au début de celle-ci
  // (pause()/resume() sont peu fiables sur iPhone et Android).
  function couper() { jeton++; if (synth.speaking || synth.pending) synth.cancel(); }

  bouton.addEventListener("click", function () {
    if (!voix) voix = choisirVoix();
    if (etat === "arret") {
      couper();
      morceaux = texteArticle(); index = 0; etat = "lecture"; afficher(); lireSuivant();
    } else if (etat === "lecture") {
      etat = "pause"; couper(); afficher();
    } else {
      etat = "lecture"; afficher(); lireSuivant();
    }
  });
  stop.addEventListener("click", function () { etat = "arret"; index = 0; couper(); afficher(); });
  window.addEventListener("pagehide", function () { synth.cancel(); });

  bloc.hidden = false;
  afficher();
})();
