# GitHub README Extraction — When MCP Tools Fail

## Problem

The `fetchGithubReadme` MCP tool sometimes returns `"README not found or repository does not exist"` even when the repo clearly exists and is public. This happens with:
- Newly created repos (< 1 year old)
- Repos with unconventional directory structures
- Repos behind certain CDN/caching layers

## Symptoms

```
mcp__open_websearch__fetchGithubReadme → {"error": "README not found or repository does not exist"}
```

But the repo is accessible at `https://github.com/org/repo` in a browser.

## Workaround

### Step 1: Navigate to the repo URL

Use `browser_navigate` to visit the repo directly:

```
browser_navigate(url="https://github.com/org/repo")
```

### Step 2: Extract README content via browser console

Use `browser_console` with a DOM selector to extract the README:

```javascript
document.querySelector('article.markdown-body')?.innerText || document.querySelector('#readme')?.innerText || 'no readme found'
```

The `article.markdown-body` selector targets GitHub's rendered README container. The `#readme` fallback catches older repo layouts.

### Step 3: For repo directory / file listings

GitHub's file tree appears in the browser snapshot as `treeitem` elements. Extract the full file list:

```javascript
Array.from(document.querySelectorAll('[role=treeitem]')).map(el => el.innerText.trim()).filter(t => t)
```

This returns all files and folders in the repo tree, including any nested skills directories.

## When to Use This

- `fetchGithubReadme` fails with a 404 or empty response
- You need to explore a repo's directory structure (e.g., list skill files, config files)
- You need to extract content from specific files (not just the README)
- The repo is public but the MCP tool cannot resolve it

## Limitation

The browser approach is slower than the MCP tool (requires full page load). Use the MCP tool first, fall back to browser only when it fails.

## Alternative: Raw Content URLs

For specific files when you know the exact path, use raw GitHub URLs:

```
https://raw.githubusercontent.com/org/repo/branch/path/to/file
```

These can be fetched with `fetchWebContent` (which often succeeds where `fetchGithubReadme` fails).