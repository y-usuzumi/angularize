# -*- coding: utf-8 -*-
################################
# Angularize
# @author: Savor d'Isavano
# @date:  2014-06-13
################################

import re

def code_matches_rule(code, rule):
    rule = rule \
        .replace(' ', '᩽ ᩽') \
        .replace('(', '᩽(᩽') \
        .replace(')', '᩽)᩽') \
        .replace('[', '᩽[᩽') \
        .replace(']', '᩽]᩽') \
        .replace('{', '᩽{᩽') \
        .replace('}', '᩽}᩽') \
        .replace('+', '᩽+᩽') \
        .replace('-', '᩽-᩽') \
        .replace('*', '᩽*᩽') \
        .replace('/', '᩽/᩽')
    
    rule = rule \
        .replace('᩽ ᩽', '\s*') \
        .replace('᩽(᩽', '\(') \
        .replace('᩽)᩽', '\)') \
        .replace('᩽[᩽', '\[') \
        .replace('᩽]᩽', '\]') \
        .replace('᩽{᩽', '\{') \
        .replace('᩽}᩽', '\}') \
        .replace('᩽+᩽', '\+') \
        .replace('᩽-᩽', '\-') \
        .replace('᩽*᩽', '\*') \
        .replace('᩽/᩽', '\/')
        
    regex = re.compile(rule)
    return regex.match(code) is not None
