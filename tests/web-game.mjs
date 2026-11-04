import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, mkdir, readdir, stat } from "node:fs/promises";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { photos } from "../web/photos.js";
import { dirname, extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || "playwright");
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const webRoot = resolve(root, "web");
const artifacts = resolve(root, ".harness/tmp/magic-book");
await mkdir(artifacts, { recursive: true });
const mime = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".webm": "video/webm" };
const peoplePattern = /\/assets\/(?:two|three|four|scene-[^/]+)\.webp$/;
// Serve under a repository subpath to catch GitHub Pages asset-path regressions.
const prefix = "/Magic_book_game/";
const server = createServer(async (request, response) => {
  const pathname = new URL(request.url, "http://localhost").pathname;
  if (!pathname.startsWith(prefix)) { response.writeHead(404).end(); return; }
  const path = resolve(webRoot, decodeURIComponent(pathname.slice(prefix.length)) || "index.html");
  if (!path.startsWith(webRoot + sep)) { response.writeHead(403).end(); return; }
  try {
    const body = await readFile(path);
    response.writeHead(200, { "Content-Type": mime[extname(path)] || "application/octet-stream", "Cache-Control": "no-store" }).end(body);
  } catch { response.writeHead(404).end(); }
});
await new Promise((done) => server.listen(0, "127.0.0.1", done));
const url = `http://127.0.0.1:${server.address().port}${prefix}`;
let browser;
let checks = 0;
const errors = [];
const externalRequests = [];
const gameState = (page) => page.evaluate(() => JSON.parse(window.render_game_to_text()));
async function waitMode(page, mode) {
  await page.waitForFunction((expected) => JSON.parse(window.render_game_to_text()).mode === expected, mode);
}
async function newPage(options = {}, random = .021) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce", ...options });
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error" && !message.text().includes("Failed to load resource")) errors.push(message.text()); });
  page.on("request", (request) => { if (!request.url().startsWith(url) && !request.url().startsWith("data:")) externalRequests.push(request.url()); });
  await page.addInitScript((value) => { Math.random = () => value; }, random);
  return page;
}
function check(condition, message) { assert.ok(condition, message); checks++; console.log(`PASS ${message}`); }

try {
  const html = await readFile(resolve(webRoot, "index.html"), "utf8");
  check(!/<script[^>]+src=["']https?:\/\//.test(html), "public game does not load advertising SDKs before real ad integration");
  check(/<meta name="google-adsense-account" content="ca-pub-8450600555475262">/.test(html), "publisher verification is retained without an advertising script");
  check(!/id="(?:reward-dialog|watch-demo|complete-demo)"|class="banner-ad"/.test(html), "public game contains no placeholder banner or simulated ad reward flow");
  const privacyHtml = await readFile(resolve(webRoot, "privacy.html"), "utf8");
  const cssVersion = createHash("sha256").update((await readFile(resolve(webRoot,"styles.css"),"utf8")).replace(/\r\n/g,"\n")).digest("hex").slice(0,12);
  const jsVersion = createHash("sha256").update((await readFile(resolve(webRoot,"game.js"),"utf8")).replace(/\r\n/g,"\n")).digest("hex").slice(0,12);
  check(html.includes(`styles.css?v=${cssVersion}`) && privacyHtml.includes(`styles.css?v=${cssVersion}`) && html.includes(`game.js?v=${jsVersion}`), "all page asset versions match the current CSS and game content");
  const manifest = JSON.parse(await readFile(resolve(root, "docs/photos.manifest.json"), "utf8"));
  check(photos.length === 100 && manifest.scenes.length === 100, "catalog contains exactly 100 photos");
  check(new Set(photos.map((photo) => photo.id)).size === 100 && new Set(photos.map((photo) => photo.src)).size === 100, "all 100 IDs and asset paths are unique");
  check(photos.filter((photo) => photo.category === "everyday").length === 95 && photos.filter((photo) => photo.category === "special").length === 5, "catalog has 95 everyday and 5 rare special scenes");
  check(photos.every((photo) => {
    const review = manifest.scenes.find((scene) => scene.id === photo.id);
    return review?.reviewed === true && Number.isInteger(photo.count) && photo.count > 0 && photo.count === review.count && photo.src.endsWith("/" + review.file);
  }), "every photo has a positive visually reviewed count and matching source record");
  const assetBuffers = await Promise.all(photos.map((photo) => readFile(fileURLToPath(photo.src))));
  check(new Set(assetBuffers.map((buffer) => createHash("sha256").update(buffer).digest("hex"))).size === 100, "100 different generated images exist on disk");
  const coreBytes = (await Promise.all(["index.html", "styles.css", "game.js", "photos.js"].map(async (name) => (await stat(resolve(webRoot, name))).size))).reduce((a, b) => a + b, 0);
  check(coreBytes + Math.max(...assetBuffers.map((buffer) => buffer.length)) < 500 * 1024, "game code and any single selected photo stay below 500 KiB");
  browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE } : {}) });
  const page = await newPage();
  let photoRequests = 0;
  page.on("request", (request) => { if (peoplePattern.test(request.url())) photoRequests++; });
  await page.goto(url);
  await waitMode(page, "closed");
  check(photoRequests === 0, "full-size game photos are not downloaded before opening the book");
  check(await page.locator("#closed-book").isVisible(), "initial book cover is visible");
  await page.locator("#lobby-book").hover();
  check(!(await gameState(page)).lobby.hovering && (await gameState(page)).lobby.particles === 0 &&
    await page.locator(".lobby-float").evaluate(node=>getComputedStyle(node).animationName) === "none", "reduced motion keeps the lobby still and creates no hover particles");
  await page.mouse.move(0,0);
  const stillAlpha = await page.evaluate(async () => {
    const canvas=document.createElement("canvas");canvas.width=960;canvas.height=600;
    const ctx=canvas.getContext("2d");
    return Promise.all(["book-closed.webp","book-open.webp"].map(async file=>{
      const img=new Image();img.src=new URL("assets/"+file,location.href).href;await img.decode();
      ctx.clearRect(0,0,960,600);ctx.drawImage(img,0,0);
      return [ctx.getImageData(5,5,1,1).data[3],ctx.getImageData(480,300,1,1).data[3]];
    }));
  });
  check(stillAlpha.every(([corner,center])=>corner === 0 && center === 255), "both book stills have transparent surroundings and an opaque book center");
  await page.screenshot({ path: resolve(artifacts, "desktop-closed.png"), animations: "disabled" });
  await page.evaluate(() => { document.querySelector("#draw-button").click(); document.querySelector("#draw-button").click(); });
  await waitMode(page, "revealed");
  const first = await gameState(page);
  check(first.usedFree && first.photo.count === 4 && photoRequests === 1, "first opening is free and repeated clicks produce just one draw");
  check(await page.locator("#people-count").innerText() === "4" && await page.locator("#people-photo").getAttribute("alt") === "해안 언덕에 나란히 서 있는 성인 네 명", "visible number and photo describe the four-person image");
  await page.screenshot({ path: resolve(artifacts, "desktop-open.png"), animations: "disabled" });

  await page.locator("#draw-button").click();
  await waitMode(page, "revealed");
  const second = await gameState(page);
  check(second.photo.id !== first.photo.id && second.photo.count === 3 && (await gameState(page)).adMode === "off" && photoRequests === 2, "free replay opens one different photo without an advertising prompt");
  await page.reload();
  await waitMode(page, "closed");
  check((await gameState(page)).usedFree && (await page.locator("#draw-label").innerText()) === "다시 펼치기!", "refresh retains progress and still offers free replay");
  await page.locator("#about-button").click();
  check((await page.locator("#about-dialog").innerText()).includes("AI로 만든") && (await page.locator("#about-dialog").innerText()).includes("모두 무료"), "photo origin and actual free-play behavior are disclosed");
  await page.keyboard.press("Escape");
  await page.locator("#draw-button").click();
  await waitMode(page, "revealed");
  check((await gameState(page)).photo.id !== second.photo.id, "the previous-photo exclusion survives refresh");

  const mobile = await newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }, 0);
  await mobile.goto(url);
  await waitMode(mobile, "closed");
  await mobile.screenshot({ path: resolve(artifacts, "mobile-closed.png"), animations: "disabled" });
  await mobile.locator("#draw-button").focus();
  await mobile.keyboard.press("Enter");
  await waitMode(mobile, "revealed");
  check((await gameState(mobile)).photo.count === 2, "keyboard activation opens the two-person image on mobile");
  check(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "mobile layout has no horizontal overflow");
  check(await mobile.evaluate(() => document.querySelector("#open-book").getBoundingClientRect().bottom <= document.querySelector(".game-controls").getBoundingClientRect().top), "mobile photo and answer do not overlap controls");
  await mobile.screenshot({ path: resolve(artifacts, "mobile-open.png"), animations: "disabled" });
  await mobile.locator("#draw-button").click();
  await waitMode(mobile, "revealed");
  check((await gameState(mobile)).photo.count === 3 && await mobile.locator("dialog[open]").count() === 0, "mobile free replay opens another photo directly");
  await mobile.setViewportSize({ width: 320, height: 640 });
  check(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "small 320px screens have no horizontal overflow");

  const storageDenied = await newPage();
  await storageDenied.addInitScript(() => {
    for (const method of ["getItem", "setItem"]) Object.defineProperty(Storage.prototype, method, { value: () => { throw new DOMException("Storage blocked", "SecurityError"); } });
  });
  await storageDenied.goto(url);
  await waitMode(storageDenied, "closed");
  await storageDenied.locator("#draw-button").click();
  await waitMode(storageDenied, "revealed");
  await storageDenied.locator("#draw-button").click();
  await waitMode(storageDenied, "revealed");
  check(await storageDenied.locator("#storage-warning").isVisible() && !(await gameState(storageDenied)).storageAvailable && (await gameState(storageDenied)).photo.count === 3, "blocked storage falls back to memory, warns, and allows free replay");

  const legacySession = await newPage();
  await legacySession.addInitScript(() => sessionStorage.setItem("people-book:v1", JSON.stringify({usedFree:true, credit:true, previous:"coast"})));
  await legacySession.goto(url);
  await waitMode(legacySession, "closed");
  await legacySession.locator("#draw-button").click();
  await waitMode(legacySession, "revealed");
  check((await gameState(legacySession)).photo.id !== "coast" && await legacySession.evaluate(() => !Object.hasOwn(JSON.parse(sessionStorage.getItem("people-book:v1")), "credit")), "old ad credits are ignored and removed while preserving the previous-photo exclusion");

  const failures = await newPage();
  await failures.route(peoplePattern, (route) => route.abort());
  await failures.goto(url);
  await waitMode(failures, "closed");
  await failures.locator("#draw-button").click();
  await failures.waitForFunction(() => JSON.parse(window.render_game_to_text()).error !== "");
  check(!(await gameState(failures)).usedFree && await failures.locator("#closed-book").isVisible(), "failed first image does not consume the free opening");
  await failures.unroute(peoplePattern);
  await failures.locator("#draw-button").click();
  await waitMode(failures, "revealed");
  const beforeFailure = (await gameState(failures)).photo.id;
  await failures.route(peoplePattern, (route) => route.abort());
  await failures.locator("#draw-button").click();
  await failures.waitForFunction(() => JSON.parse(window.render_game_to_text()).error !== "");
  check((await gameState(failures)).photo.id === beforeFailure && await failures.locator("#people-photo").isVisible(), "failed free replay preserves the previous photo and result");
  await failures.reload();
  await waitMode(failures, "closed");
  check((await gameState(failures)).usedFree && await failures.locator("#draw-button").isEnabled(), "a failed replay followed by refresh remains playable");
  await failures.unroute(peoplePattern);
  await failures.locator("#draw-button").click();
  await waitMode(failures, "revealed");
  check((await gameState(failures)).photo.id !== beforeFailure, "retry after image failure reveals a new photo");

  const timeout = await newPage();
  await timeout.clock.install();
  await timeout.route(peoplePattern, () => {});
  await timeout.goto(url);
  await waitMode(timeout, "closed");
  await timeout.locator("#draw-button").click();
  await waitMode(timeout, "loading");
  await timeout.clock.runFor(12050);
  check(!(await gameState(timeout)).usedFree && (await gameState(timeout)).error !== "", "stalled image request times out without consuming a free opening");

  const noJs = await newPage({ javaScriptEnabled: false });
  await noJs.goto(url);
  check(await noJs.locator("noscript").isVisible() && await noJs.locator("#draw-button").isDisabled(), "JavaScript-disabled browsers get an explanation and no broken active control");
  check(await noJs.locator("#guide-title").isVisible() && await noJs.locator("#scenes figure").count() === 3 && (await noJs.locator("#making").innerText()).includes("직접 살펴보고"), "instructions, photo examples, and count-review explanation are present without JavaScript");
  const sampleRecords = await noJs.locator("#scenes figure").evaluateAll(nodes => nodes.map(node => ({id:node.dataset.photoId,count:Number(node.dataset.count),href:node.querySelector("a").getAttribute("href")})));
  check(sampleRecords.every(sample => photos.some(photo => photo.id === sample.id && photo.count === sample.count && photo.src.endsWith(sample.href.slice(1)))), "published photo examples match the reviewed game catalog and full-size originals");
  await noJs.locator("#scenes").scrollIntoViewIfNeeded();
  await noJs.waitForFunction(() => [...document.querySelectorAll("#scenes img")].every(image => image.complete && image.naturalWidth > 0));
  await noJs.screenshot({ path: resolve(artifacts, "static-content-desktop.png"), fullPage: true });
  await noJs.locator(".site-footer a[href='./privacy.html']").click();
  check((await noJs.locator("h1").innerText()) === "개인정보처리방침" && (await noJs.locator("main").innerText()).includes("현재 Google 광고 스크립트") && await noJs.locator("a[href='https://github.com/booobing/booobing.github.io/issues']").count() > 0, "privacy and real contact links work without JavaScript under a repository subpath");
  await noJs.setViewportSize({width:320,height:640});
  check(await noJs.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "privacy page fits a 320px screen");
  await noJs.screenshot({path:resolve(artifacts,"privacy-mobile.png"),fullPage:true});
  await noJs.locator("main a[href='./']").click();
  check(await noJs.locator("#guide-title").isVisible(), "privacy page returns to the working game URL");
  await noJs.locator("#scenes").scrollIntoViewIfNeeded();
  check(await noJs.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "static photo content fits a 320px screen");
  await noJs.screenshot({path:resolve(artifacts,"static-content-mobile.png"),fullPage:true});
  const catalogPage = await newPage();
  await catalogPage.goto(url);
  const dimensions = await catalogPage.evaluate(async (files) => Promise.all(files.map(async (file) => {
    const image = new Image();
    image.src = new URL("assets/" + file, location.href).href;
    await image.decode();
    return [image.naturalWidth, image.naturalHeight];
  })), manifest.scenes.map((scene) => scene.file));
  check(dimensions.length === 100 && dimensions.every(([width, height]) => width === 960 && height === 640), "all 100 WebP images decode at 960 by 640 without cropping");
  const special = await newPage({}, .999999);
  await special.goto(url);
  await waitMode(special, "closed");
  await special.locator("#draw-button").click();
  await waitMode(special, "revealed");
  check((await gameState(special)).photo.id === "scene-100" && (await special.locator("#people-count").innerText()) === "30", "rare football scene displays its verified 30-person result");
  await special.screenshot({ path: resolve(artifacts, "special-desktop.png"), animations: "disabled" });
  await special.setViewportSize({ width: 390, height: 844 });
  check(await special.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.querySelector("#open-book").getBoundingClientRect().bottom <= document.querySelector(".game-controls").getBoundingClientRect().top), "large special result fits the mobile book without overlap");
  await special.screenshot({ path: resolve(artifacts, "special-mobile.png"), animations: "disabled" });
  const lobby = await newPage({ reducedMotion: "no-preference" });
  await lobby.goto(url);
  await waitMode(lobby,"closed");
  const floatStart=await lobby.locator(".lobby-float").evaluate(node=>getComputedStyle(node).transform);
  await lobby.waitForFunction(before=>getComputedStyle(document.querySelector(".lobby-float")).transform !== before,floatStart);
  check(true,"lobby book moves while floating before a draw");
  const bookBounds=await lobby.locator("#lobby-book").boundingBox();
  const restingTilt=await lobby.locator(".lobby-volume").evaluate(node=>getComputedStyle(node).transform);
  await lobby.mouse.move(bookBounds.x+bookBounds.width*.8,bookBounds.y+bookBounds.height*.25);
  await lobby.waitForFunction(()=>JSON.parse(window.render_game_to_text()).lobby.particles >= 12);
  check(await lobby.locator(".lobby-volume").evaluate((node,before)=>getComputedStyle(node).transform !== before,restingTilt) &&
    (await gameState(lobby)).lobby.hovering && !(await gameState(lobby)).usedFree && (await gameState(lobby)).lobby.particles <= 28,
    "hover tilts the book and emits bounded magic particles without spending an opening");
  check(await lobby.locator(".lobby-spark").evaluateAll(nodes=>nodes.some(node=>{
    const rect=node.getBoundingClientRect();return Number(getComputedStyle(node).opacity) > .5 && rect.width > 1.5 && rect.height > 1.5;
  })),"hover particles reach a visible screen size instead of remaining subpixel dots");
  await lobby.screenshot({path:resolve(artifacts,"lobby-hover.png")});
  await lobby.mouse.move(0,0);
  check(!(await gameState(lobby)).lobby.hovering && (await gameState(lobby)).lobby.particles === 0,"leaving the book clears hover particles");
  await lobby.locator("#lobby-book").hover();
  await lobby.locator("#lobby-book").dispatchEvent("pointercancel",{pointerType:"mouse"});
  check(!(await gameState(lobby)).lobby.hovering && (await gameState(lobby)).lobby.particles === 0,"pointer cancellation clears the lobby effect");
  await lobby.mouse.move(0,0);
  await lobby.locator("#lobby-book").hover();
  await lobby.emulateMedia({reducedMotion:"reduce"});
  await lobby.waitForFunction(()=>JSON.parse(window.render_game_to_text()).lobby.particles === 0);
  check(!(await gameState(lobby)).lobby.hovering && await lobby.locator(".lobby-float").evaluate(node=>getComputedStyle(node).animationName) === "none",
    "switching to reduced motion stops floating and removes active particles");
  await lobby.emulateMedia({reducedMotion:"no-preference"});
  await lobby.mouse.move(0,0);
  await lobby.locator("#lobby-book").hover();
  await lobby.locator("#draw-button").focus();
  await lobby.keyboard.press("Enter");
  await waitMode(lobby,"opening");
  check(!(await gameState(lobby)).lobby.hovering && (await gameState(lobby)).lobby.particles === 0 && !(await lobby.locator("#closed-book").isVisible()),
    "starting a draw while hovering clears the lobby and starts the real opening video");
  await waitMode(lobby,"revealed");
  check((await gameState(lobby)).videoOutcome === "ended" && (await gameState(lobby)).photoVisible,"floating lobby transitions to the complete video and photo reveal");
  const touchLobby=await newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true,reducedMotion:"no-preference"});
  await touchLobby.goto(url);
  await touchLobby.locator("#lobby-book").tap();
  check((await gameState(touchLobby)).lobby.particles === 0 && !(await gameState(touchLobby)).usedFree && (await gameState(touchLobby)).mode === "closed",
    "touching the lobby book creates no stuck hover particles or accidental draw");
  await touchLobby.screenshot({path:resolve(artifacts,"lobby-mobile.png"),animations:"disabled"});

  const motion = await newPage({ reducedMotion: "no-preference", viewport: { width: 1280, height: 720 } });
  let movieRequests = 0;
  motion.on("request", (request) => { if (request.url().endsWith("book-opening.webm")) movieRequests++; });
  await motion.goto(url);
  await waitMode(motion, "closed");
  check(movieRequests === 0, "opening WebM is not requested before the user clicks");
  await motion.locator("#draw-button").click();
  await waitMode(motion, "opening");
  check(await motion.evaluate(() => { const r=document.querySelector("#book-stage").getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }), "opening video stays fully visible in a 720px-high desktop viewport");
  check(!(await motion.locator("#people-photo").isVisible()) && !(await gameState(motion)).usedFree, "actual video plays while photo stays hidden and free use remains unspent");
  await motion.waitForFunction(() => document.querySelector("#opening-video").currentTime > .75);
  check(await motion.evaluate(()=>{
    const video=document.querySelector("#opening-video"),canvas=document.createElement("canvas");
    canvas.width=video.videoWidth;canvas.height=video.videoHeight;
    const ctx=canvas.getContext("2d");ctx.drawImage(video,0,0);
    return ctx.getImageData(4,4,1,1).data[3] === 0 && ctx.getImageData(canvas.width/2,canvas.height/2,1,1).data[3] === 255;
  }), "Chromium decodes video alpha so the hall shows around the opaque book without a video rectangle");
  await motion.screenshot({ path: resolve(artifacts, "video-opening.png"), animations: "disabled" });
  await motion.waitForFunction(() => document.querySelector("#opening-video").currentTime > 1.65);
  check(await motion.evaluate(() => {
    const state=JSON.parse(window.render_game_to_text()),video=document.querySelector("#opening-video");
    return state.mode === "opening" && state.photoVisible && state.usedFree && video.currentTime < 2.8 && !video.paused && !video.ended;
  }) && await motion.locator("#people-photo").isVisible() && await motion.locator("#people-count").isVisible(), "photo and count appear with the opening while the video is still playing, consuming the free opening once");
  check(await motion.evaluate(() => getComputedStyle(document.querySelector("#open-book > .book-still")).visibility === "hidden"), "photo overlays the continuing video without covering it with a still frame");
  await motion.screenshot({ path: resolve(artifacts, "photo-at-opening.png"), animations: "disabled" });
  await motion.waitForFunction(() => document.querySelector("#opening-video").currentTime > 2.3);
  check(await motion.locator("#people-photo").isVisible() && await motion.locator("#draw-button").isDisabled(), "photo and halo remain through the particle tail while repeated draws stay locked");
  await motion.screenshot({ path: resolve(artifacts, "video-glow.png"), animations: "disabled" });
  await waitMode(motion, "revealed");
  check((await gameState(motion)).videoOutcome === "ended" && await motion.evaluate(() => {
    const video = document.querySelector("#opening-video");
    return Math.abs(video.duration-3) < .01 && video.currentTime >= 2.95 && video.videoWidth === 800 && video.muted && video.playsInline;
  }), "a real 3s 800px muted inline alpha WebM finishes after the synchronized photo reveal");
  check((await motion.locator("#open-book").innerText()).trim() === "" && await motion.locator("#people-count").isVisible(), "book interior contains no text and the count is displayed outside");
  await motion.screenshot({ path: resolve(artifacts, "video-revealed.png"), animations: "disabled" });
  const beforeReplay = (await gameState(motion)).photo.id;
  await motion.locator("#draw-button").click();
  await waitMode(motion, "opening");
  await waitMode(motion, "revealed");
  check((await gameState(motion)).videoOutcome === "ended" && (await gameState(motion)).photo.id !== beforeReplay, "free replay completes another full opening video and reveals a different photo");
  const delayedPhoto = await newPage({ reducedMotion: "no-preference" });
  let releasePhoto;
  const photoGate = new Promise((resolve) => { releasePhoto=resolve; });
  let delayedMovieRequests=0;
  delayedPhoto.on("request",request=>{if(request.url().endsWith("book-opening.webm"))delayedMovieRequests++;});
  await delayedPhoto.route(peoplePattern,async route=>{await photoGate;await route.continue();});
  await delayedPhoto.goto(url);
  await waitMode(delayedPhoto,"closed");
  await delayedPhoto.locator("#draw-button").click();
  await waitMode(delayedPhoto,"loading");
  try {
    check(delayedMovieRequests === 0 && !(await gameState(delayedPhoto)).usedFree, "slow photo loading waits before starting video so the opening cue cannot be missed");
  } finally { releasePhoto(); }
  await waitMode(delayedPhoto,"opening");
  await delayedPhoto.waitForFunction(()=>document.querySelector("#opening-video").currentTime>1.65);
  check((await gameState(delayedPhoto)).photoVisible && await delayedPhoto.locator("#people-photo").isVisible(), "a delayed photo still appears at the opening cue after preload completes");
  await waitMode(delayedPhoto,"revealed");
  // Inspect the encoded asset independently of browser presentation/seek timing.
  const samples = [.21,1.29,2.6].map((time) => {
    const pixels = execFileSync(process.env.FFMPEG_PATH || "ffmpeg", [
      "-hide_banner", "-loglevel", "error", "-ss", String(time),
      "-c:v", "libvpx-vp9",
      "-i", resolve(webRoot, "assets/book-opening.webm"), "-frames:v", "1",
      "-vf", "scale=240:150", "-pix_fmt", "rgba", "-f", "rawvideo", "pipe:1",
    ], { maxBuffer: 512 * 1024, timeout: 10000 });
    assert.equal(pixels.length, 240 * 150 * 4);
    let center=0,centerCount=0,outer=0,outerCount=0;
    for(let y=0;y<150;y++)for(let x=0;x<240;x++){
      const i=(y*240+x)*4,luma=(pixels[i]+pixels[i+1]+pixels[i+2])/3*pixels[i+3]/255;
      if(x>=100&&x<140&&y>=55&&y<95){center+=luma;centerCount++;}
      const radius=((x-120)/120)**2+((y-75)/75)**2;
      if(radius>.7&&radius<.95){outer+=luma;outerCount++;}
    }
    return {center:center/centerCount,outer:outer/outerCount,cornerAlpha:pixels[3]};
  });
  check(samples.every(sample=>sample.cornerAlpha === 0), "encoded video keeps zero-alpha corners through charge, burst and settled frames");
  check(samples[1].center > 230 && samples[1].center > samples[0].center+80 && samples[1].outer > samples[0].outer+25 && samples[1].outer > samples[2].outer, `transparent opening retains a white central burst and fading outer light (${samples.map(x=>x.center.toFixed(0)+"/"+x.outer.toFixed(0)).join(" → ")})`);

  const noVideo = await newPage({ reducedMotion: "no-preference" });
  await noVideo.route("**/book-opening.webm", (route) => route.abort());
  await noVideo.goto(url);
  await waitMode(noVideo, "closed");
  await noVideo.locator("#draw-button").click();
  await waitMode(noVideo, "revealed");
  check((await gameState(noVideo)).videoOutcome === "unavailable", "unavailable video falls back to the glowing final frame and photo");
  const blockedVideo = await newPage({ reducedMotion: "no-preference" });
  await blockedVideo.addInitScript(() => { HTMLMediaElement.prototype.play = () => Promise.reject(new DOMException("Blocked", "NotAllowedError")); });
  await blockedVideo.goto(url);
  await waitMode(blockedVideo, "closed");
  await blockedVideo.locator("#draw-button").click();
  await waitMode(blockedVideo, "revealed");
  check((await gameState(blockedVideo)).videoOutcome === "unavailable", "browser playback rejection recovers without leaving controls locked");
  const stalledVideo = await newPage({ reducedMotion: "no-preference" });
  await stalledVideo.clock.install();
  await stalledVideo.route("**/book-opening.webm", () => {});
  await stalledVideo.goto(url);
  await waitMode(stalledVideo, "closed");
  await stalledVideo.locator("#draw-button").click();
  await waitMode(stalledVideo, "opening");
  await stalledVideo.clock.runFor(8100);
  await waitMode(stalledVideo, "revealed");
  check((await gameState(stalledVideo)).videoOutcome === "timeout", "stalled video recovers through its watchdog and reveals the loaded photo");
  const motionFailure = await newPage({ reducedMotion: "no-preference" });
  await motionFailure.route(peoplePattern, (route) => route.abort());
  await motionFailure.goto(url);
  await waitMode(motionFailure, "closed");
  await motionFailure.locator("#draw-button").click();
  await motionFailure.waitForFunction(() => JSON.parse(window.render_game_to_text()).error !== "");
  check(!(await gameState(motionFailure)).usedFree && !(await motionFailure.locator("#opening-video").isVisible()), "photo preload failure leaves playback stopped and the free opening unspent");
  await motionFailure.unroute(peoplePattern);
  await motionFailure.locator("#draw-button").click();
  await waitMode(motionFailure, "revealed");
  check((await gameState(motionFailure)).videoOutcome === "ended", "retry after a photo failure completes a fresh video without stale playback callbacks");
  check((await gameState(page)).videoOutcome === "reduced-motion", "motion preference skips video while preserving the game flow");
  const movieBytes = (await stat(resolve(webRoot, "assets/book-opening.webm"))).size;
  const posterBytes = (await stat(resolve(webRoot, "assets/book-closed.webp"))).size + (await stat(resolve(webRoot, "assets/book-open.webp"))).size;
  const backdropBytes = (await stat(resolve(webRoot, "assets/gothic-hall.webp"))).size;
  const coverBytes = (await stat(resolve(webRoot,"assets/book-cover.webp"))).size;
  const previewBytes = (await Promise.all(["street","cafe","football"].map(async name => (await stat(resolve(webRoot,`assets/preview-${name}.webp`))).size))).reduce((a,b)=>a+b,0);
  check(coreBytes + posterBytes + coverBytes + backdropBytes + previewBytes < 500 * 1024, "initial game assets including all three photo previews stay below 500 KiB");
  check(backdropBytes < 300*1024 && movieBytes < 1.5 * 1024 * 1024 && coreBytes + movieBytes + posterBytes + coverBytes + backdropBytes + previewBytes + Math.max(...assetBuffers.map((buffer) => buffer.length)) < 1.5 * 1024 * 1024, "gothic backdrop, lobby cover and complete first-play payload remain below 1.5 MiB");
  check(errors.length === 0, `no uncaught JavaScript or unexpected console errors: ${errors.join(", ")}`);
  check(externalRequests.length === 0, "public free-play pages load no external ads, fonts, analytics, or APIs");
  let bytes = 0;
  for (const entry of await readdir(webRoot, { recursive: true, withFileTypes: true })) {
    if (entry.isFile()) bytes += (await stat(resolve(entry.parentPath, entry.name))).size;
  }
  check(bytes < 15 * 1024 * 1024, `entire 100-photo library is below 15 MiB (${bytes} bytes)`);
  console.log(`\n${checks} checks passed. Screenshots: ${artifacts}`);
} finally {
  if (browser) await browser.close();
  await new Promise((done) => server.close(done));
}
