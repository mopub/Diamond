# coding=utf-8

"""
Collects all metrics exported by the powerdns nameserver using the
rec_control binary.

#### Dependencies

 * rec_control

"""

import diamond.collector
import subprocess
import os
from diamond.collector import str_to_bool


class PowerDNSRecursorCollector(diamond.collector.Collector):

    _GAUGE_KEYS = [
        'all-outqueries', 'answers0-1', 'answers100-1000', 'answers10-100', 'answers1-10', 'answers-slow',
        'cache-bytes', 'cache-entries', 'cache-misses', 'chain-resends', 'client-parse-errors', 'concurrent-queries',
        'dlg-only-drops', 'dont-outqueries', 'ipv6-outqueries', 'max-mthread-stack', 'noerror-answers',
        'nsset-invalidations', 'nxdomain-answers', 'outgoing-timeouts', 'over-capacity-drops', 'packetcache-bytes',
        'packetcache-entries', 'packetcache-hits', 'packetcache-misses', 'qa-latency', 'questions', 'ipv6-questions', 
        'resource-limits', 'server-parse-errors', 'servfail-answers', 'spoof-prevents', 'sys-msec', 
        'tcp-client-overflow', 'tcp-outqueries', 'tcp-questions', 'throttled-out', 'throttle-entries',
        'unauthorized-tcp', 'unauthorized-udp', 'unexpected-packets', 'uptime', 'user-msec']

    def get_default_config_help(self):
        config_help = super(PowerDNSRecursorCollector, self).get_default_config_help()
        config_help.update({
            'bin':         'The path to the pdns_control binary',
            'use_sudo':    'Use sudo?',
            'sudo_cmd':    'Path to sudo',
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(PowerDNSRecursorCollector, self).get_default_config()
        config.update({
            'bin': '/usr/bin/rec_control',
            'path': 'powerdnsrecursor',
            'use_sudo':         False,
            'sudo_cmd':         '/usr/bin/sudo',
        })
        return config

    def collect(self):
        if not os.access(self.config['bin'], os.X_OK):
            self.log.error("%s is not executable", self.config['bin'])
            return False

        command = [self.config['bin'], 'get-all']

        if str_to_bool(self.config['use_sudo']):
            command.insert(0, self.config['sudo_cmd'])

        data = subprocess.Popen(command,
                                stdout=subprocess.PIPE).communicate()[0]
        
        after_munge = data.replace('\t','=').replace('\n',',')

        for metric in after_munge.split(','):
            if not metric.strip():
                continue
            metric, value = metric.split('=')
            try:
                value = float(value)
            except:
                pass
            if metric not in self._GAUGE_KEYS:
                value = int(self.derivative(metric, value))
                if value < 0:
                    continue
            self.publish(metric, value)
