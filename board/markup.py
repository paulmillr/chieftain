#!/usr/bin/env python
# encoding: utf-8
"""
markup.py

Created by Paul Bagwell on 2011-01-26.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
import markdown


class KlippedExtension(markdown.Extension):
    DEL_RE = r'(--)(.*?)--'
    INS_RE = r'(__)(.*?)__'
    STRONG_RE = r'(\*\*)(.*?)\*\*'
    EMPH_RE = r'(\/\/)(.*?)\/\/'

    def extendMarkdown(self, md, md_globals):
        st = markdown.inlinepatterns.SimpleTagPattern
        ip = md.inlinePatterns
        del_tag = st(self.DEL_RE, 'del')
        ip.add('del', del_tag, '>not_strong')
        ins_tag = st(self.INS_RE, 'ins')
        ip.add('ins', ins_tag, '>del')
        strong_tag = st(self.STRONG_RE, 'strong')
        ip['strong'] = strong_tag
        emph_tag = st(self.EMPH_RE, 'em')
        ip['emphasis'] = emph_tag
        #del md.inlinepatterns['strong_em']
        del md.inlinePatterns['emphasis2']


def makeExtension(configs=None):
    return KlippedExtension(configs=configs)
