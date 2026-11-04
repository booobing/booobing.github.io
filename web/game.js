import { photos } from "./photos.js";

const $ = (id) => document.getElementById(id);
const storageKey = "people-book:v1";
const photoRevealTime = 1.45;
const state = { usedFree: false, previous: null };
let storageAvailable = true;
let busy = false;
let current = null;
let error = "";
let opening = false;
let videoOutcome = "idle";
let cancelOpening = null;
let photoVisible = false;
const motionPreference = matchMedia("(prefers-reduced-motion: reduce)");
let lobbyTimer = 0;
let lobbyFrame = 0;
let lobbyPoint = { x: 0, y: 0 };
let lobbySparkIndex = 0;

function stopLobbyHover() {
  clearInterval(lobbyTimer);
  lobbyTimer = 0;
  cancelAnimationFrame(lobbyFrame);
  lobbyFrame = 0;
  $("lobby-book").classList.remove("is-awake");
  for (const name of ["--tilt-x", "--tilt-y", "--shine-x", "--shine-y"]) $("lobby-book").style.removeProperty(name);
  $("lobby-particles").replaceChildren();
}

function emitLobbySparks() {
  const layer = $("lobby-particles");
  for (let i = 0; i < 2 && layer.childElementCount < 28; i++) {
    const spark = document.createElement("span");
    spark.className = "lobby-spark" + (lobbySparkIndex++ % 4 === 0 ? " is-star" : "");
    spark.style.left = `${lobbyPoint.x + (Math.random() - .5) * 36}px`;
    spark.style.top = `${lobbyPoint.y + (Math.random() - .5) * 36}px`;
    spark.style.setProperty("--size", `${2 + Math.random() * 3}px`);
    spark.style.setProperty("--drift", `${(Math.random() - .5) * 85}px`);
    spark.style.setProperty("--rise", `${-40 - Math.random() * 85}px`);
    spark.style.setProperty("--life", `${900 + Math.random() * 400}ms`);
    spark.style.setProperty("--spark-color", lobbySparkIndex % 3 === 0 ? "#9edcff" : "#edc67d");
    spark.addEventListener("animationend", () => spark.remove(), { once: true });
    layer.append(spark);
  }
}

function moveLobbyPointer(event) {
  if (busy || current || document.hidden || motionPreference.matches || event.pointerType === "touch" ||
    !matchMedia("(hover: hover)").matches || document.querySelector("dialog[open]")) return;
  const book = $("lobby-book"), rect = book.getBoundingClientRect();
  lobbyPoint = { x: Math.max(0, Math.min(rect.width, event.clientX - rect.left)), y: Math.max(0, Math.min(rect.height, event.clientY - rect.top)) };
  if (!lobbyFrame) lobbyFrame = requestAnimationFrame(() => {
    lobbyFrame = 0;
    book.style.setProperty("--tilt-x", `${(.5 - lobbyPoint.y / rect.height) * 14}deg`);
    book.style.setProperty("--tilt-y", `${(lobbyPoint.x / rect.width - .5) * 22}deg`);
    book.style.setProperty("--shine-x", `${lobbyPoint.x / rect.width * 100}%`);
    book.style.setProperty("--shine-y", `${lobbyPoint.y / rect.height * 100}%`);
  });
  if (!lobbyTimer) {
    book.classList.add("is-awake");
    emitLobbySparks();
    lobbyTimer = setInterval(emitLobbySparks, 100);
  }
}

for (const type of ["pointerenter", "pointermove"]) $("lobby-book").addEventListener(type, moveLobbyPointer);
for (const type of ["pointerleave", "pointercancel"]) $("lobby-book").addEventListener(type, stopLobbyHover);
motionPreference.addEventListener("change", stopLobbyHover);
document.addEventListener("visibilitychange", () => { if (document.hidden) stopLobbyHover(); });
window.addEventListener("pagehide", stopLobbyHover);

try {
  const stored = JSON.parse(sessionStorage.getItem(storageKey) || "null");
  if (stored && typeof stored === "object") {
    state.usedFree = stored.usedFree === true;
    state.previous = photos.some((photo) => photo.id === stored.previous) ? stored.previous : null;
  }
  sessionStorage.setItem(storageKey, JSON.stringify(state));
} catch {
  storageAvailable = false;
}

function persist() {
  try {
    sessionStorage.setItem(storageKey, JSON.stringify(state));
  } catch {
    storageAvailable = false;
  }
}

function renderControls() {
  $("draw-button").disabled = busy;
  $("book-stage").setAttribute("aria-busy", String(busy));
  $("storage-warning").hidden = storageAvailable;
  $("draw-label").textContent = busy ? "페이지를 펼치는 중" :
    !state.usedFree ? "펼치기!" : "다시 펼치기!";
  $("play-note").textContent = "광고 없이 무료로 펼쳐 보세요. 같은 사진은 연속으로 나오지 않아요.";
  $("status").textContent = error || (busy && !photoVisible ? "어떤 만남이 기다리고 있을까요…" :
    current ? (["unavailable", "timeout"].includes(videoOutcome) ? "영상 재생을 건너뛰고 사진을 펼쳤어요." : "빛 속에서 새로운 만남을 발견했어요.") :
    state.usedFree ? "새로운 페이지를 만나 보세요." : "당신을 위한 첫 페이지가 기다리고 있어요.");
  $("opening-video").hidden = !opening;
  $("closed-book").hidden = opening || Boolean(current);
  $("open-book").hidden = !photoVisible || !current;
  $("result-summary").hidden = !photoVisible || !current;
  $("book-stage").classList.toggle("is-opening", opening);
  $("closed-book").classList.toggle("is-lobby", !busy && !current);
  if (busy || current) stopLobbyHover();
}

function playOpening(onReveal) {
  if (motionPreference.matches) {
    videoOutcome = "reduced-motion";
    onReveal();
    return Promise.resolve();
  }
  opening = true;
  photoVisible = false;
  videoOutcome = "playing";
  renderControls();
  const video = $("opening-video");
  return new Promise((resolve) => {
    let settled = false;
    let revealed = false;
    let frame = 0;
    const reveal = () => {
      if (revealed) return;
      revealed = true;
      onReveal();
    };
    const finish = (outcome) => {
      if (settled) return;
      settled = true;
      clearTimeout(watchdog);
      cancelAnimationFrame(frame);
      video.removeEventListener("ended", ended);
      video.removeEventListener("error", failed);
      videoOutcome = outcome;
      cancelOpening = null;
      if (outcome !== "ended") video.pause();
      if (outcome !== "cancelled") reveal();
      resolve();
    };
    const ended = () => finish("ended");
    const failed = () => finish("unavailable");
    const watchdog = setTimeout(() => finish("timeout"), 8000);
    cancelOpening = () => finish("cancelled");
    video.addEventListener("ended", ended);
    video.addEventListener("error", failed);
    const observeFrame = () => {
      if (settled) return;
      if (video.currentTime >= photoRevealTime) {
        frame = 0;
        reveal();
      } else frame = requestAnimationFrame(observeFrame);
    };
    frame = requestAnimationFrame(observeFrame);
    try {
      if (!video.src) video.src = new URL("./assets/book-opening.webm", import.meta.url).href;
      video.currentTime = 0;
      video.play().catch(failed);
    } catch { failed(); }
  });
}

function loadPhoto(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    const timeout = setTimeout(() => {
      image.onload = image.onerror = null;
      reject(new Error("Photo request timed out"));
    }, 12000);
    image.onload = () => { clearTimeout(timeout); resolve(image); };
    image.onerror = () => { clearTimeout(timeout); reject(new Error("Photo request failed")); };
    image.src = src;
  });
}

async function draw() {
  if (busy) return;
  busy = true;
  error = "";
  renderControls();
  const choices = photos.filter((photo) => photo.id !== state.previous);
  const photo = choices[Math.floor(Math.random() * choices.length)];
  try {
    // Prepare the photo first so a slow download cannot miss the book-opening cue.
    await loadPhoto(photo.src);
    await playOpening(() => {
      $("people-photo").src = photo.src;
      $("people-photo").alt = photo.alt;
      $("photo-caption").textContent = photo.caption;
      $("people-count").textContent = photo.count;
      current = photo;
      photoVisible = true;
      state.usedFree = true;
      state.previous = photo.id;
      persist();
      renderControls();
    });
  } catch {
    error = "사진을 불러오지 못했어요. 잠시 후 다시 펼쳐 주세요.";
  } finally {
    cancelOpening?.();
    opening = false;
    $("opening-video").pause();
    busy = false;
    renderControls();
  }
}

// Free replay remains enabled until a real rewarded-ad provider is integrated.
$("draw-button").addEventListener("click", () => void draw());
$("about-button").addEventListener("click", () => { stopLobbyHover(); $("about-dialog").showModal(); });
$("about-close").addEventListener("click", () => $("about-dialog").close());

window.render_game_to_text = () => JSON.stringify({
  mode: busy ? (opening ? "opening" : "loading") : current ? "revealed" : "closed",
  photo: current && photoVisible ? { id: current.id, count: current.count, caption: current.caption } : null,
  usedFree: state.usedFree, storageAvailable, error,
  adMode: "off", videoOutcome, photoVisible, coordinates: "DOM layout; no spatial game coordinates",
  lobby: { hovering: $("lobby-book").classList.contains("is-awake"), particles: $("lobby-particles").childElementCount },
});
// No simulation clock: this game advances only through user actions and image loads.
window.advanceTime = async () => {};
renderControls();
