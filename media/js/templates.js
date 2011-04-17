{% load i18n settings md2 %}
<article class="post" id="post${post.pid}" data-id="${post.id}">
    <header>
        {{if post.data}}
            {{if post.data.country}}
                <span class="country">
                    <img src="${STATIC_URL}/images/flags/{{post.data.country|lower}}.png" alt="${post.data.country}" title="${post.data.country}">
                </span>
            {{/if}}
            {{if post.data.useragent}}
                <span class="useragent">
                    <img src="${STATIC_URL}images/useragents/{{post.data.useragent.name|lower}}.png" alt="${post.data.useragent.name}" title="${post.data.useragent.raw}">
                </span>
            {{/if}}
        {{/if}}
        <span class="poster">
            {{if post.email}}
                <a href="mailto:${post.email}" class="email">
            {{/if}}
            ${post.poster}{{if post.email}}</a>{{/if}}
        </span>
        <span class="tripcode">${post.tripcode}</span>
        <span class="title">${post.topic}</span>
        <time datetime="${post.date|date:'c'}" pubdate>
            ${post.date|date:"d.m.Y H:i:s"}
        </time>
        <span class="number"><a href="${thread.op_post.pid|default:""}#post${post.pid}">${post.pid}</a></span>
        {{if thread and post.is_op_post}}
            <span class="replylink">
                <a href="{{thread.op_post.pid|default:""}}#post${post.pid}">Ответ</a>
            </span>
        {{/if}}
        {{if post.is_op_post}}
            {% url board.views.thread post.section_slug post.pid as thread_url %}
            <a href="http://twitter.com/share?text={{post.message|urlencode}}&amp;url={% setting 'SITE_URL' %}{{thread_url|slice:'1:'|urlencode}}" title="Добавить в Twitter" target="_blank" class="twitterButton"></a>
            <a href="${thread_url}/rss" title="RSS feed" class="rssButton"></a>
            <span class="post-icon hide add" title="{% trans 'Hide' %}"></span>
            <span class="post-icon bookmark add" title="{% trans 'Add to bookmarks' %}"></span>
        {{/if}}
    </header>

    {{if post.file}}
        <div class="filemeta">
            <a target="_blank" href="${post.file.file.url}">${post.file.id}.${post.file.type.extension}</a>
            (<em>{{f.size|filesizeformat}}{% if f.image_height %}, ${post.file.image_height}x${post.file.image_width}{{/if}}</em>)
        </div>
        <a href="${post.file.file.url}" class="file">
            {{if f.thumb}}
                <img src="${post.file.thumb.url}" id="file${post.file.id}" data-hash="${post.file.hash}" alt="">
            {% else %}
                {{if f.image_height}}
                    <img src="${post.file.file.url}" class="file" id="file${post.file.id}" data-hash="${post.file.hash}" alt="">
                {% else %}
                    {{if f.type.group.default_image}}
                        <img src="${post.file.type.group.default_image.url}" class="file-icon" id="file${post.file.id}" alt="">
                    {{/if}}
                {{/if}}
            {{/if}}
        </a>
    {{/if}}

    <div class="message">${post.message_html}</div>
    {{if post.is_op_post and thread.count.skipped > 0}}
        <span class="skipped">Пропущено ответов: ${thread.count.skipped}, из них с файлами: ${thread.count.skipped_files}.</span>
    {{/if}}
</article>
{{if $post.is_op_post}}<div class="iewrap"></div>{{/if}}