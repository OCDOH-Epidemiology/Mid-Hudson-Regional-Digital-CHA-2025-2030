#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
const targetPath = path.join(
  repoRoot,
  "docs",
  "site_libs",
  "quarto-search",
  "quarto-search.js"
);

function replaceOnce(contents, before, after, label) {
  if (contents.includes(after)) {
    return contents;
  }
  if (!contents.includes(before)) {
    throw new Error(`Patch anchor not found for ${label}`);
  }
  return contents.replace(before, after);
}

function patchSearchRuntime(contents) {
  let updated = contents;

  const highlightBefore = `  // highlight matches on the page
  if (query && mainEl) {
    // perform any highlighting
    highlight(escapeRegExp(query), mainEl);

    // fix up the URL to remove the q query param
    const replacementUrl = new URL(window.location);
    replacementUrl.searchParams.delete(kQueryArg);
    window.history.replaceState({}, "", replacementUrl);
  }`;

  const highlightAfter = `  // highlight matches on the page
  if (query && mainEl) {
    // perform any highlighting
    highlight(escapeRegExp(query), mainEl);

    // CHA PATCH: jump directly to first highlighted hit in the loaded page.
    // This ensures search clicks land on the actual matching text.
    const firstMatch = mainEl.querySelector("mark");
    if (firstMatch) {
      firstMatch.scrollIntoView({ block: "center", inline: "nearest" });
    }

    // fix up the URL to remove the q query param
    const replacementUrl = new URL(window.location);
    replacementUrl.searchParams.delete(kQueryArg);
    window.history.replaceState({}, "", replacementUrl);
  }`;

  updated = replaceOnce(
    updated,
    highlightBefore,
    highlightAfter,
    "scroll to first highlighted match"
  );

  const reshapeBefore = `          const firstItem = value[0];
            reshapedItems.push({
              ...firstItem,
              type: kItemTypeDoc,
            });`;

  const reshapeAfter = `          // CHA PATCH: prefer section anchors for top-level document links.
          const firstItem = value[0];
            const anchorItem = value.find((item) => item.href.includes("#"));
            const preferredHref = anchorItem ? anchorItem.href : firstItem.href;
            reshapedItems.push({
              ...firstItem,
              href: preferredHref,
              type: kItemTypeDoc,
            });`;

  updated = replaceOnce(
    updated,
    reshapeBefore,
    reshapeAfter,
    "anchor-first top result links"
  );

  const helperBefore = `let subSearchTerm = undefined;
let subSearchFuse = undefined;
const kFuseMaxWait = 125;

async function fuseSearch(query, fuse, fuseOptions) {`;

  const helperAfter = `let subSearchTerm = undefined;
let subSearchFuse = undefined;
const kFuseMaxWait = 125;

function chapterOrderFromCrumbs(crumbs) {
  if (!crumbs || crumbs.length === 0) {
    return Number.POSITIVE_INFINITY;
  }
  const chapterMatch = crumbs[0].match(/chapter-number[^>]*>(\\d+)/);
  if (!chapterMatch) {
    return Number.POSITIVE_INFINITY;
  }
  const order = Number(chapterMatch[1]);
  return Number.isFinite(order) ? order : Number.POSITIVE_INFINITY;
}

async function fuseSearch(query, fuse, fuseOptions) {`;

  updated = replaceOnce(
    updated,
    helperBefore,
    helperAfter,
    "chapter order helper"
  );

  const searchBefore = `  // Search using the active fuse
  const then = performance.now();
  const resultsRaw = await index.search(query, fuseOptions);
  const now = performance.now();

  const results = resultsRaw.map((result) => {`;

  const searchAfter = `  // Search using the active fuse
  const then = performance.now();
  const resultsRaw = await index.search(query, fuseOptions);
  const now = performance.now();

  // CHA PATCH: force chronological chapter ordering while preserving
  // Fuse relevance order inside each chapter.
  const sortedResultsRaw = resultsRaw
    .map((result, originalIndex) => ({ result, originalIndex }))
    .sort((a, b) => {
      const chapterDelta =
        chapterOrderFromCrumbs(a.result.item.crumbs) -
        chapterOrderFromCrumbs(b.result.item.crumbs);
      if (chapterDelta !== 0) {
        return chapterDelta;
      }
      return a.originalIndex - b.originalIndex;
    })
    .map((entry) => entry.result);

  const results = sortedResultsRaw.map((result) => {`;

  updated = replaceOnce(
    updated,
    searchBefore,
    searchAfter,
    "chapter-first fuse sort"
  );

  return updated;
}

function main() {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`Generated search runtime not found: ${targetPath}`);
  }
  const original = fs.readFileSync(targetPath, "utf8");
  const patched = patchSearchRuntime(original);
  if (patched !== original) {
    fs.writeFileSync(targetPath, patched, "utf8");
    console.log("Patched docs/site_libs/quarto-search/quarto-search.js");
  } else {
    console.log("No patch changes needed (already applied).");
  }
}

main();
