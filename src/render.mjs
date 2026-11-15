// usage: node render.mjs <html> <outdir> <frames comma list | "all"> [workers] [fmt]
import puppeteer from "puppeteer-core";
const CHROME = process.env.CHROME || "/usr/bin/google-chrome";
import fs from "fs"; import path from "path";
const [html, outdir, which, workersArg, fmtArg] = process.argv.slice(2);
const fmt = fmtArg || "png";
fs.mkdirSync(outdir, { recursive: true });
const frames = which === "all" ? Array.from({ length: 1440 }, (_, i) => i) : which.split(",").map(Number);
const workers = +(workersArg || 1);
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
  args: ["--no-sandbox", "--disable-gpu", "--force-device-scale-factor=1", "--disable-dev-shm-usage"] });
const chunks = Array.from({ length: workers }, (_, w) => frames.filter((_, i) => i % workers === w));
const t0 = Date.now(); let done = 0;
await Promise.all(chunks.map(async (list) => {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  page.on("pageerror", e => console.error("PAGEERR", e.message));
  page.on("console", m => { if (m.type() === "error") console.error("CONSOLE", m.text()); });
  await page.goto("file://" + path.resolve(html) + "?capture=1", { waitUntil: "load" });
  await page.waitForFunction("window.__rendered===true");
  for (const f of list) {
    const data = await page.evaluate((f, fmt) => { try{renderFrame(f)}catch(e){return "ERR"+e.stack} return document.getElementById("c").toDataURL(fmt === "jpg" ? "image/jpeg" : "image/png", 0.94); }, f, fmt);
    if(data.startsWith("ERR")){console.error(f,data);continue}
    fs.writeFileSync(path.join(outdir, `f${String(f).padStart(4, "0")}.${fmt}`), Buffer.from(data.split(",")[1], "base64"));
    done++; if (done % 60 === 0) console.log(`${done}/${frames.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await page.close();
}));
await browser.close();
console.log("done", frames.length, ((Date.now() - t0) / 1000).toFixed(1) + "s");
