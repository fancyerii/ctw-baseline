# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import predictions2html
import random
import settings
import six

from pythonapi import eval_tools


def main():
    assert six.PY3
    random.seed(0)
    with open(settings.TEST_CLASSIFICATION_GT) as f:
        gt = f.read()
    all = list()
    for model in predictions2html.cfgs:
        with open(model['predictions_file_path']) as f:
            pr = f.read()
        report = eval_tools.classification_recall(
            gt, pr,
            settings.RECALL_N, settings.ATTRIBUTES, settings.SIZE_RANGES
        )
        assert 0 == report['error'], report['msg']
        all.append({
            'model_name': model['model_name'],
            'performance': report['performance'],
        })

    def recall_empty():
        return {'recalls': {n: 0 for n in settings.RECALL_N}, 'n': 0}

    def recall_add(a, b):
        return {'recalls': {n: a['recalls'][n] + b['recalls'][n] for n in settings.RECALL_N}, 'n': a['n'] + b['n']}

    with open(settings.STAT_FREQUENCY) as f:
        frequency = json.load(f)
    freq_order = [o['text'] for o in frequency]
    with open('../classification/products/cates.json') as f:
        cates = json.load(f)
    cates = [(c['text'], [], c['cate_id']) for c in sorted(random.sample(cates[10:1000], 50), key=lambda o: -o['trainval'])]
    for report_obj in all:
        performance = report_obj['performance']
        for char, a, _ in cates:
            a.append(performance['all']['texts'][char])
    for text, a, cate_id in cates:
        s = r'\begin{minipage}{3.5mm} \includegraphics[width=\linewidth]{figure/texts/1_' + '{}'.format(cate_id) + '.png} \end{minipage}'
        for b in a:
            s += ' & {:.1f}'.format(b['recalls'][1] / b['n'] * 100)
        s += ' & {}'.format(b['n'])
        s += r' & {} \\'.format(list(filter(lambda o: o['text'] == text, frequency))[0]['trainval'])
        print(s)
    report_obj = list(filter(lambda o: 'inception_v4' == o['model_name'], all))[0]

    def check(k, attr_id):
        if attr_id < len(settings.ATTRIBUTES):
            return int(k) & 2 ** attr_id
        else:
            return 0 == int(k) & 2 ** (attr_id - len(settings.ATTRIBUTES))
    def trans(attr_id):
        if attr_id < len(settings.ATTRIBUTES):
            return settings.ATTRIBUTES[attr_id]
        else:
            return r'$\sim${}'.format(settings.ATTRIBUTES[attr_id - len(settings.ATTRIBUTES)])
    def recall2str(recall):
        if recall['n'] > 0:
            return '{:.1f}'.format(recall['recalls'][1] / recall['n'] * 100)
        else:
            return '-'
    for i in range(2 * len(settings.ATTRIBUTES) - 1):
        for j in range(i + 1, 2 * len(settings.ATTRIBUTES)):
            if j == i + len(settings.ATTRIBUTES):
                continue
            s = r'{} & \& & {}'.format(trans(i), trans(j))
            for szname, _ in settings.SIZE_RANGES:
                rc = recall_empty()
                for k, o in enumerate(performance[szname]['attributes']):
                    if check(k, i) and check(k, j):
                        rc = recall_add(rc, o)
                s += ' & {}'.format(recall2str(rc))
            s += r' \\'
            print(s)


if __name__ == '__main__':
    main()
