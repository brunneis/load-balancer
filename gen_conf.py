#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import os

TAB = ' ' * 4


def load_haproxy_conf():
    with open('haproxy.yaml', 'r') as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def load_endpoints_conf():
    with open('endpoints.yaml', 'r') as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def get_inbound_template():
    return {'frontend main': {'bind': ['*:8080'], 'use_backend': ['main']}}


def should_print_empty_line(key, value, already_printed):
    if len(value) > 1 and key not in ['option', 'server'] and not already_printed:
        return True
    return False


def dump_haproxy_conf(haproxy_conf):
    with open('haproxy.cfg', 'w') as output_file:
        for key, value in haproxy_conf.items():
            output_file.write(f'{key}\n')
            already_printed = False
            for key2, value2 in value.items():
                if type(value2) == dict:
                    for key3, value3 in value2.items():
                        output_file.write(f'{TAB}{key2} {key3} {value3}\n')
                    already_printed = False
                    continue
                elif type(value2) == list:
                    if should_print_empty_line(key2, value2, already_printed):
                        output_file.write('\n')
                    for value3 in value2:
                        output_file.write(f'{TAB}{key2} {value3}\n')
                    if should_print_empty_line(key2, value2, False):
                        output_file.write('\n')
                    already_printed = True
                    continue
                if value2:
                    output_file.write(f'{TAB}{key2} {value2}\n')
                    already_printed = False
                    continue
                output_file.write(f'{TAB}{key2}\n')
                already_printed = False
            output_file.write('\n')


def update_haproxy_conf_with_endpoints(haproxy_conf, endpoints_conf):
    inbound_template = get_inbound_template()
    server_lines = []

    if 'endpoints' in endpoints_conf:
        check_string = ''
        if len(endpoints_conf['endpoints']) > 1:
            check_string = 'check '
        j = 0
        for endpoint in endpoints_conf['endpoints']:
            server_lines.append(f"s{j} {endpoint} {check_string}maxconn {haproxy_conf['global']['maxconn']}")
            j += 1

    if 'ssl_endpoints' in endpoints_conf:
        ssl_check_string = ''
        if len(endpoints_conf['ssl_endpoints']) > 1:
            ssl_check_string = 'check '
        k = j
        for ssl_endpoint in endpoints_conf['ssl_endpoints']:
            server_lines.append(
                f"s{k} {ssl_endpoint} {ssl_check_string}ssl maxconn {haproxy_conf['global']['maxconn']}")
            k += 1

    inbound_template['backend main'] = {
        'balance': 'roundrobin',
        'option': ['httpclose', 'forwardfor'],
        'server': server_lines
    }

    haproxy_conf.update(inbound_template)


if __name__ == "__main__":
    haproxy_conf = load_haproxy_conf()
    endpoints_conf = load_endpoints_conf()
    update_haproxy_conf_with_endpoints(haproxy_conf, endpoints_conf)
    dump_haproxy_conf(haproxy_conf)