#!/usr/bin/env python
# encoding: utf-8
"""
middlewares.py

Created by Paul Bagwell on 2011-01-22.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import re
import sys
import os
import hotshot
import tempfile
import StringIO
from operator import add
from time import time
from django.db import connection
from django.db import connection
from django.template import Template, Context
from django.conf import settings

__all__ = [
    'SQLLogToConsoleMiddleware', 'StatsMiddleware', 'ProfilingMiddleware'
]

words_re = re.compile(r'\s+')

group_prefix_re = [
    re.compile(r'^.*/django/[^/]+'),
    re.compile(r'^(.*)/[^/]+$'),  # extract module path
    re.compile(r'.*'),  # catch strange entries
]


class SQLLogToConsoleMiddleware:
    def process_response(self, request, response):
        if settings.DEBUG and connection.queries:
            time = sum([float(q['time']) for q in connection.queries])
            t = Template("{{count}} quer{{count|pluralize:\"y,ies\"}} "
                "in {{time}} seconds:\n\n{% for sql in sqllog %}"
                "[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}"
                "{% if not forloop.last %}\n\n{% endif %}{% endfor %}"
            )
            print t.render(Context({
                'sqllog': connection.queries,
                'count': len(connection.queries),
                'time': time
            }))
        return response


class StatsMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # turn on debugging in db backend to capture time
        from django.conf import settings
        debug = settings.DEBUG
        settings.DEBUG = True

        # get number of db queries before we do anything
        n = len(connection.queries)

        # time the view
        start = time()
        response = view_func(request, *view_args, **view_kwargs)
        totTime = time() - start

        # compute the db time for the queries just run
        queries = len(connection.queries) - n
        if queries:
            dbTime = reduce(add, [float(q['time'])
                                  for q in connection.queries[n:]])
        else:
            dbTime = 0.0

        # and backout python time
        pyTime = totTime - dbTime

        # restore debugging setting again
        settings.DEBUG = debug

        stats = {
            'totTime': totTime,
            'pyTime': pyTime,
            'dbTime': dbTime,
            'queries': queries,
        }

        # replace the comment if found
        if response and response.content:
            s = response.content
            regexp = re.compile(r'(?P<cmt><!--\s*STATS:(?P<fmt>.*?)-->)')
            match = regexp.search(s)
            if match:
                s = s[:match.start('cmt')] + \
                    match.group('fmt') % stats + \
                    s[match.end('cmt'):]
                response.content = s

        return response


# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team
class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available
    for superuser otherwise, but you really shouldn't add this middleware
    to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def process_request(self, request):
        if ((settings.DEBUG or request.user.is_superuser) and
            'prof' in request.GET):
            self.tmpfile = tempfile.mktemp()
            self.prof = hotshot.Profile(self.tmpfile)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if ((settings.DEBUG or request.user.is_superuser) and
            'prof' in request.GET):
            return self.prof.runcall(callback, request, *callback_args,
                **callback_kwargs)

    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall(file)
            if name:
                return name[0]

    def get_summary(self, results_dict, sum):
        list = [(item[1], item[0]) for item in results_dict.items()]
        list.sort(reverse=True)
        list = list[:40]

        res = '      tottime\n'
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % (
                100 * item[0] / sum if sum else 0,
                item[0], item[1]
            )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        sum = 0

        for s in stats_str:
            fields = words_re.split(s)
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]

                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time

                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[group] = 0
                mygroups[group] += time

        return ('<pre>'
               ' ---- By file ----\n\n' + self.get_summary(mystats, sum) +
               '\n'
               ' ---- By group ---\n\n' + self.get_summary(mygroups, sum) +
               '</pre>')

    def process_response(self, request, response):
        if ((settings.DEBUG or request.user.is_superuser) and
            'prof' in request.GET):
            self.prof.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

            response.content = "\n".join(response.content.split("\n")[:40])

            response.content += self.summary_for_files(stats_str)

            os.unlink(self.tmpfile)

        return response
