#!/usr/bin/env python3
"""
Generate static index.html and story.html with all data embedded.
After running, open index.html in the browser (file://) — no server needed.
Usage: python3 generate_web.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORIES_DIR = ROOT / "stories"


def escape_embed(s: str) -> str:
    """Escape for embedding in HTML <script>."""
    return s.replace("</script>", "<\\/script>").replace("</SCRIPT>", "<\\/SCRIPT>")


def load_stories():
    stories = {}
    for path in sorted(STORIES_DIR.glob("*.json")):
        if path.name == "manifest.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Skip {path.name}: {e}")
            continue
        if not isinstance(data, dict):
            continue
        stories[path.stem] = data
    return stories


def build_manifest(stories):
    out = []
    for sid, data in stories.items():
        thumb = ""
        if data.get("thumbnail") and isinstance(data["thumbnail"], dict):
            thumb = (data["thumbnail"].get("filename") or "").strip()
        category = ""
        if data.get("tags") and len(data["tags"]) > 0:
            category = (data["tags"][0].get("name") or "").strip()
        out.append({
            "id": sid,
            "title": (data.get("title") or "").strip(),
            "titleTranslation": (data.get("titleTranslation") or "").strip(),
            "level": (data.get("level") or "").strip(),
            "thumbnail": thumb,
            "category": category,
        })
    return out


def write_index(manifest_js: str):
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Spanish Stories</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 1.5rem; padding-top: 3rem; background: #f5f5f5; color: #1a1a1a; }
    body.dark { background: #1a1a1a; color: #e0e0e0; }
    .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
    .page-header h1 { margin: 0; font-size: 1.5rem; }
    .dark-toggle { position: fixed; top: 1rem; right: 1rem; width: 2.5rem; height: 2.5rem; padding: 0; border: none; border-radius: 50%; background: #e0e0e0; color: #333; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; }
    .dark-toggle:hover { background: #ccc; }
    body.dark .dark-toggle { background: #333; color: #e0e0e0; }
    body.dark .dark-toggle:hover { background: #555; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 0 auto; }
    .card { display: block; text-decoration: none; color: inherit; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s, box-shadow 0.2s; }
    body.dark .card { background: #2d2d2d; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
    .card-bg { position: relative; height: 140px; background-size: cover; background-position: center; background-color: #fff; }
    body.dark .card-bg { background-color: #1a1a1a; }
    .card-bg .level { position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(0,0,0,0.7); color: #fff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    body.dark .card-bg .level { background: rgba(255,255,255,0.2); }
    .card-body { padding: 1rem; }
    .card-title { margin: 0; font-size: 1.05rem; line-height: 1.35; }
    .card-meta { margin-top: 0.25rem; font-size: 0.85rem; color: #666; }
    body.dark .card-meta { color: #aaa; }
    .card-category { font-size: 0.75rem; color: #888; margin-top: 0.25rem; }
    body.dark .card-category { color: #888; }
    .error { color: #c00; padding: 1rem; }
  </style>
</head>
<body>
  <button type="button" class="dark-toggle" id="darkToggle" title="Toggle dark mode" aria-label="Toggle dark mode">
    <svg id="iconSun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
    <svg id="iconMoon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  </button>
  <div class="page-header"><h1>Spanish Stories</h1></div>
  <div id="app"></div>
  <script>var EMBEDDED_MANIFEST = ''' + manifest_js + ''';</script>
  <script>
    (function () {
      var app = document.getElementById('app');
      var darkToggle = document.getElementById('darkToggle');
      var iconSun = document.getElementById('iconSun');
      var iconMoon = document.getElementById('iconMoon');
      try {
        if (localStorage.getItem('darkMode') === '1') {
          document.body.classList.add('dark');
          iconSun.style.display = 'none';
          iconMoon.style.display = 'block';
        } else { iconMoon.style.display = 'none'; }
      } catch (e) {}
      darkToggle.addEventListener('click', function () {
        document.body.classList.toggle('dark');
        var isDark = document.body.classList.contains('dark');
        iconSun.style.display = isDark ? 'none' : 'block';
        iconMoon.style.display = isDark ? 'block' : 'none';
        try { localStorage.setItem('darkMode', isDark ? '1' : '0'); } catch (e) {}
      });
      function escapeHtml(s) {
        if (s == null) return '';
        var div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
      }
      var list = EMBEDDED_MANIFEST;
      if (!list || !list.length) {
        app.innerHTML = '<p class="error">No stories found.</p>';
        return;
      }
      var html = '<div class="grid">';
      list.forEach(function (item) {
        var id = item.id || '';
        var title = item.title || id;
        var titleTranslation = item.titleTranslation || '';
        var level = item.level || '';
        var thumb = (item.thumbnail && item.thumbnail.trim()) ? ('images/' + item.thumbnail.trim()) : '';
        var category = item.category || '';
        var bgStyle = thumb ? (' style="background-image: url(\\'' + thumb + '\\')"') : '';
        html += '<a class="card" href="story.html?name=' + encodeURIComponent(id) + '">';
        html += '<div class="card-bg"' + bgStyle + '><span class="level">' + escapeHtml(level) + '</span></div>';
        html += '<div class="card-body"><h2 class="card-title">' + escapeHtml(title) + '</h2>';
        if (titleTranslation) html += '<p class="card-meta">' + escapeHtml(titleTranslation) + '</p>';
        if (category) html += '<p class="card-category">' + escapeHtml(category) + '</p>';
        html += '</div></a>';
      });
      app.innerHTML = html + '</div>';
    })();
  </script>
</body>
</html>
'''
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def write_story(stories_js: str):
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Story reader</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 0 auto; padding: 1rem 1.5rem; padding-top: 3rem; line-height: 1.6; color: #1a1a1a; }
    .dark-toggle { position: fixed; top: 1rem; right: 1rem; width: 2.5rem; height: 2.5rem; padding: 0; border: none; border-radius: 50%; background: #e0e0e0; color: #333; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; }
    .dark-toggle:hover { background: #ccc; }
    body.dark .dark-toggle { background: #333; color: #e0e0e0; }
    body.dark .dark-toggle:hover { background: #555; }
    header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0; }
    h1 { margin: 0; font-size: 1.5rem; }
    .meta { font-size: 0.9rem; color: #555; }
    .tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
    .tag { background: #f0f0f0; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; }
    .tag strong { display: block; }
    .switch-row { display: flex; align-items: center; gap: 0.5rem; }
    .switch-row label { cursor: pointer; user-select: none; }
    .content { margin: 1rem 0; }
    .sentence-block { margin-bottom: 0.5rem; }
    .sentence-block.show-translation { margin-bottom: 1rem; }
    .sentence-block.show-translation .translation { display: block; }
    .sentence-block .translation { display: none; margin-top: 0.25rem; padding-left: 1rem; font-size: 0.95rem; color: #555; border-left: 3px solid #ccc; }
    .sentence-block .detailed-translation { display: none; margin-top: 0.35rem; padding-left: 1.5rem; font-size: 0.85rem; color: #555; list-style: disc; }
    .sentence-block.show-translation.show-detailed .detailed-translation { display: block; }
    .sentence-block .detailed-translation li { margin: 0.2rem 0; }
    body.dark .sentence-block .detailed-translation { color: #aaa; }
    .sentence-block .text { cursor: pointer; }
    .sentence-block .translation { cursor: pointer; }
    .sentence-block .detailed-translation { cursor: pointer; }
    .sentence-block .text .hl { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
    .content img { max-width: 100%; height: auto; display: block; margin: 1rem 0; border-radius: 8px; }
    .content img.hide { display: none !important; }
    .glossary { margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e0; }
    .glossary h2 { font-size: 1.1rem; margin-bottom: 0.75rem; }
    .glossary dl { margin: 0; }
    .glossary dt { font-weight: 600; margin-top: 0.75rem; }
    .glossary dt:first-child { margin-top: 0; }
    .glossary dd { margin: 0.25rem 0 0 0; color: #444; font-size: 0.95rem; }
    body.dark { background: #1a1a1a; color: #e0e0e0; }
    body.dark header { border-bottom-color: #404040; }
    body.dark .meta { color: #aaa; }
    body.dark .tag { background: #2d2d2d; color: #ccc; }
    body.dark .sentence-block .translation { color: #aaa; border-left-color: #555; }
    body.dark .sentence-block .text .hl { background: #4a3f1a; color: #f0e6c8; }
    body.dark .glossary { border-top-color: #404040; }
    body.dark .glossary h2, body.dark .glossary dt { color: #e8e8e8; }
    body.dark .glossary dd { color: #aaa; }
    body.dark .content img:not(.hide) { filter: invert(1); }
    .back { margin-bottom: 1rem; }
    .back a { color: #666; text-decoration: none; font-size: 0.9rem; }
    .back a:hover { text-decoration: underline; }
    body.dark .back a { color: #aaa; }
    .error { color: #c00; padding: 2rem; }
  </style>
</head>
<body>
  <button type="button" class="dark-toggle" id="darkToggle" title="Toggle dark mode" aria-label="Toggle dark mode">
    <svg id="iconSun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
    <svg id="iconMoon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  </button>
  <div class="back"><a href="index.html">← All stories</a></div>
  <header>
    <div><h1 id="title"></h1><p class="meta" id="meta"></p><div class="tags" id="tags"></div></div>
    <div class="switch-row">
      <input type="checkbox" id="showTranslations" />
      <label for="showTranslations">Show translations under sentences</label>
      <input type="checkbox" id="showDetailedTranslation" />
      <label for="showDetailedTranslation">Detailed translation</label>
    </div>
  </header>
  <main class="content" id="content"></main>
  <footer class="glossary" id="glossary"></footer>
  <script>var EMBEDDED_STORIES = ''' + stories_js + ''';</script>
  <script>
    (function () {
      function getQuery() {
        var q = {};
        (window.location.search || '').replace(/^\\?/, '').split('&').forEach(function (p) {
          var kv = p.split('=');
          if (kv.length === 2) q[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1]);
        });
        return q;
      }
      function escapeHtml(s) {
        if (s == null) return '';
        var div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
      }
      var name = getQuery().name;
      var story = name && EMBEDDED_STORIES[name];
      if (!story) {
        document.getElementById('content').innerHTML = '<p class="error">Story not found. <a href="index.html">Back to stories</a></p>';
        document.querySelector('header').style.display = 'none';
        return;
      }
      document.title = story.title + ' — Spanish Stories';
      document.getElementById('title').textContent = story.title;
      document.getElementById('meta').textContent = story.level + ' · ' + (story.language || 'es') + (story.titleTranslation ? ' — ' + story.titleTranslation : '');
      var tagsHtml = '';
      if (story.tags && story.tags.length) {
        story.tags.forEach(function (t) {
          tagsHtml += '<span class="tag"><strong>' + escapeHtml(t.name) + '</strong> ' + escapeHtml(t.description) + '</span>';
        });
      }
      document.getElementById('tags').innerHTML = tagsHtml || '—';
      var content = document.getElementById('content');
      var showTranslations = document.getElementById('showTranslations');
      var showDetailedTranslation = document.getElementById('showDetailedTranslation');
      var expandedSentences = new Set();
      var collapsedSentences = new Set();
      function renderContent() {
        var showAll = showTranslations.checked;
        var showDetailed = showDetailedTranslation.checked;
        content.innerHTML = '';
        story.content.forEach(function (item, i) {
          if (item.type === 'sentence') {
            var isVisible = showAll ? !collapsedSentences.has(i) : expandedSentences.has(i);
            var block = document.createElement('div');
            block.className = 'sentence-block' + (isVisible ? ' show-translation' : '') + (isVisible && showDetailed ? ' show-detailed' : '');
            block.dataset.sentenceIndex = i;
            var text = item.text;
            if (item.highlights && item.highlights.length) {
              var parts = [];
              var last = 0;
              item.highlights.slice().sort(function (a, b) { return a.startIndex - b.startIndex; }).forEach(function (h) {
                if (h.startIndex > last) parts.push({ type: 'plain', s: text.slice(last, h.startIndex) });
                parts.push({ type: 'hl', s: text.slice(h.startIndex, h.endIndex) });
                last = h.endIndex;
              });
              if (last < text.length) parts.push({ type: 'plain', s: text.slice(last) });
              var span = document.createElement('span');
              span.className = 'text';
              parts.forEach(function (p) {
                if (p.type === 'hl') {
                  var hl = document.createElement('span');
                  hl.className = 'hl';
                  hl.textContent = p.s;
                  span.appendChild(hl);
                } else { span.appendChild(document.createTextNode(p.s)); }
              });
              block.appendChild(span);
            } else {
              var span = document.createElement('span');
              span.className = 'text';
              span.textContent = text;
              block.appendChild(span);
            }
            var trans = document.createElement('div');
            trans.className = 'translation';
            trans.textContent = item.translation || '';
            block.appendChild(trans);
            if (item.detailedTranslation && item.detailedTranslation.length) {
              var ul = document.createElement('ul');
              ul.className = 'detailed-translation';
              item.detailedTranslation.forEach(function (bullet) {
                var li = document.createElement('li');
                li.textContent = bullet;
                ul.appendChild(li);
              });
              block.appendChild(ul);
            }
            content.appendChild(block);
          } else if (item.type === 'image') {
            var img = document.createElement('img');
            img.alt = item.generation_prompt || item.filename;
            img.loading = 'lazy';
            img.onerror = function () { this.classList.add('hide'); };
            img.src = 'images/' + item.filename;
            content.appendChild(img);
          }
        });
      }
      function hideSentence(i) {
        expandedSentences.delete(i);
        if (showTranslations.checked) collapsedSentences.add(i);
      }
      function isSentenceVisible(i) {
        var showAll = showTranslations.checked;
        return showAll ? !collapsedSentences.has(i) : expandedSentences.has(i);
      }
      content.addEventListener('click', function (e) {
        var block = e.target.closest('.sentence-block');
        if (!block || block.dataset.sentenceIndex === undefined) return;
        var i = parseInt(block.dataset.sentenceIndex, 10);
        if (e.target.closest('.translation') || e.target.closest('.detailed-translation')) {
          hideSentence(i);
          renderContent();
        } else if (e.target.closest('.text')) {
          if (isSentenceVisible(i)) {
            hideSentence(i);
          } else {
            expandedSentences.add(i);
            collapsedSentences.delete(i);
          }
          renderContent();
        }
      });
      showTranslations.addEventListener('change', function () {
        if (showTranslations.checked) {
          collapsedSentences.clear();
        } else {
          expandedSentences.clear();
          collapsedSentences.clear();
        }
        renderContent();
      });
      showDetailedTranslation.addEventListener('change', renderContent);
      renderContent();
      var darkToggle = document.getElementById('darkToggle');
      var iconSun = document.getElementById('iconSun');
      var iconMoon = document.getElementById('iconMoon');
      try {
        if (localStorage.getItem('darkMode') === '1') {
          document.body.classList.add('dark');
          iconSun.style.display = 'none';
          iconMoon.style.display = 'block';
        } else { iconMoon.style.display = 'none'; }
      } catch (e) {}
      darkToggle.addEventListener('click', function () {
        document.body.classList.toggle('dark');
        var isDark = document.body.classList.contains('dark');
        iconSun.style.display = isDark ? 'none' : 'block';
        iconMoon.style.display = isDark ? 'block' : 'none';
        try { localStorage.setItem('darkMode', isDark ? '1' : '0'); } catch (e) {}
      });
      if (story.glossary && Object.keys(story.glossary).length) {
        var gEl = document.getElementById('glossary');
        var gHtml = '<h2>Glossary</h2><dl>';
        Object.keys(story.glossary).forEach(function (key) {
          var e = story.glossary[key];
          gHtml += '<dt>' + escapeHtml(key) + ' — ' + escapeHtml(e.translation) + '</dt><dd>' + escapeHtml(e.explanation) + '</dd>';
        });
        gEl.innerHTML = gHtml + '</dl>';
      }
    })();
  </script>
</body>
</html>
'''
    (ROOT / "story.html").write_text(html, encoding="utf-8")


def main():
    stories = load_stories()
    if not stories:
        print("No story JSONs found in stories/")
        return
    manifest = build_manifest(stories)
    manifest_js = escape_embed(json.dumps(manifest, ensure_ascii=False))
    stories_js = escape_embed(json.dumps(stories, ensure_ascii=False))
    write_index(manifest_js)
    write_story(stories_js)
    print("Generated index.html and story.html with", len(stories), "stories.")
    print("Open index.html in your browser (file://) — no server needed.")


if __name__ == "__main__":
    main()
