---
layout: default
title: "Episodios"
---

{% assign episodes = site.posts | where_exp: "p", "p.categories contains 'podcast'" %}

{% if episodes.size == 0 %}
No hay episodios todavía. Crea tu primer archivo en `_posts/`.
{% else %}
{% for post in episodes %}
<div class="episode">
  <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-weight:700;"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></div>
      <div class="meta">
        <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
        {% if post.episode %} · Ep {{ post.episode }}{% endif %}
        {% if post.season %} · T {{ post.season }}{% endif %}
        {% if post.duration %} · {{ post.duration }}{% endif %}
      </div>
    </div>
    <div class="meta">
      {% if post.audio_url %}<a href="{{ post.audio_url | relative_url }}">MP3</a>{% endif %}
    </div>
  </div>

  {% if post.description %}
    <div>{{ post.description }}</div>
  {% endif %}
</div>
{% endfor %}
{% endif %}
