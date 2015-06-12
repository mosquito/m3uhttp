#!/usr/bin/env python2
# encoding: utf-8
from gevent import monkey
monkey.patch_all()

import os
import urllib2
import json
from bottle import route, run, response, template, request

playlist = os.getenv('PLAYLIST', 'http://127.0.0.1/torrent-telik')

@route('/')
def index():
    index_template = open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html'),
        'rb'
    ).read()

    req = urllib2.Request(playlist, None, dict(request.headers))
    resp = urllib2.urlopen(req).read().decode('utf-8').split('#')
    out = {}
    for line in resp:
        if '\n' in line and 'EXTINF' in line:
            meta, url = line.split('\n', 1)
            url = url.strip('\n')
            meta, name = meta.split(',', 1)

            meta = dict(
                map(
                    lambda x: [i.strip('"').strip("'").strip(',') for i in x.split('=')],
                    filter(lambda x: '=' in x, meta.split(' '))
                )
            )

            meta['url'] = url
            out[name] = url

    response.set_header('Content-Type', 'text/html')
    return template(index_template, links=sorted(out.items()), key=lambda a,b: a[0] > b[0])


if __name__ == '__main__':
    run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '8080')),
        server='gevent',
        debug=True if os.getenv('DEBUG', '') else False
    )
