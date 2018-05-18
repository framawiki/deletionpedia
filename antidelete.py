#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) Kasper Souren 2013-2015
#
# http://deletionpedia.org/
#
# Script to rescue articles from Wikipedia
# Multilingual, additions for other languages welcome
#
# Available under the terms of the GNU General Public License v2 or later
# 

import sys
import re
import datetime
import pywikibot
from locale import setlocale, LC_TIME

class Antidelete:
    def __init__(self, lang, patterns):
        self.lang = lang
        self.frm = pywikibot.Site(lang, 'wikipedia')
        self.to = pywikibot.Site('test2', 'wikipedia')
        self.patterns = patterns

    def fetch(self):
        # There are various patterns
        print self.lang, self.patterns
        
        if 'fn_day' in self.patterns:
            self.fetch_days()
        else:
            self.parse_list(self.patterns['title'])

    def fetch_days(self):
        for i in range(7):
            self.fetch_day(i)

    def fetch_day(self, days_ago = 1):
        '''Fetch articles on the list of a specific day'''
        day = datetime.date.today() - datetime.timedelta(days_ago)
        if 'locale' in self.patterns:
            setlocale(LC_TIME, 'de_DE') #self.patterns['locale'])
        else:
            setlocale(LC_TIME, 'en_US.utf8')
        pagename = self.patterns['fn_day'](day)
        fn_title = 'fn_title' in self.patterns and self.patterns['fn_title'] or None
        self.parse_list(pagename, title_process = fn_title)

    def parse_list(self, pagename, title_process = None):
        '''Parse page with list of articles to be deleted'''
        p = pywikibot.Page(self.frm, pagename) 
        s = p.get()
        re_article = re.compile(self.patterns['regexp'])
        for l in s.splitlines():
            m = re_article.match(l)
            if m:
                title = m.group(1)
                if title_process:
                    # if title != 'Info': #Swedish...
                        title = title_process(title)
                self.recover_article(title)
        


    def recover_article(self, title):
        print "Recovering: " + title[:100]
        if 'Talk' in title:
            print 'no talk pages yet'
            return
        page = pywikibot.Page(self.frm, title)
        try:
            article_text = page.get()
        except IsRedirectPage:
            print 'IsRedirectPage?', title
            return
        except NoPage:
            print 'PROBABLY deleted already...', title
            return

        if not 'porn' in article_text and not 'xxx' in article_text:
            dp_page = pywikibot.Page(self.to, title)

            update_page = False
            try:
                if dp_page.get() != article_text:
                    update_page = True
                else:
                    print 'PAGE already rescued'
            except pywikibot.exceptions.NoPage:
                update_page = True
            if update_page:
                if self.patterns['test'] in article_text:
                    msg = 'inclusion power'
                else:
                    article_text = "{{survived}}"
                    msg = 'survived on Wikipedia'
                dp_page.put(article_text, msg)


if __name__ == '__main__':
    ad = Antidelete('test', {
        'test': '{{delete',
        'regexp': '[*]\[\[(.+)\]\]',
        'title': 'Test_delete_list'
        })
    ad.fetch()
