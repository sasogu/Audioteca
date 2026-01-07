---
layout: default
title: "Episodios"
---

{% assign episodes = site.posts | where_exp: "p", "p.categories contains 'podcast'" %}

{% if episodes.size == 0 %}
No hay episodios todavía. Crea tu primer archivo en `_posts/`.
{% else %}
{% for post in episodes %}
<article class="episode">
  <h2 class="episode-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
  <div class="meta">
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%d de %B de %Y" }}</time>
    {% if post.episode %} · Episodio {{ post.episode }}{% endif %}
    {% if post.season %} · Temporada {{ post.season }}{% endif %}
    {% if post.duration %} · {{ post.duration }}{% endif %}
  </div>
  {% if post.description %}
    <div class="episode-description">{{ post.description }}</div>
  {% endif %}
</article>
{% endfor %}
{% endif %}
