# coding=utf-8

"""
Collect tcp round trip times
Only valid for ipv4 hosts currently

#### Dependencies

 * hping3

#### Configuration

Configuration is done by adding in extra keys like this

 * target_1 - example.org
 * target_fw - 192.168.0.1
 * target_localhost - localhost

We extract out the key after target_ and use it in the graphite node we push.

"""

import subprocess
import diamond.collector
import os
from diamond.collector import str_to_bool


class HPingCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(HPingCollector, self).get_default_config_help()
        config_help.update({
            'bin':         'The path to the ping binary',
            'use_sudo':    'Use sudo?',
            'sudo_cmd':    'Path to sudo',
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(HPingCollector, self).get_default_config()
        config.update({
            'path':             'hping3',
            'bin':              '/usr/sbin/hping3',
            'use_sudo':         False,
            'sudo_cmd':         '/usr/bin/sudo',
        })
        return config

    def collect(self):
        for key in self.config.keys():
            if key[:7] == "target_":
                host = self.config[key]
                if ':' in host:
                    parts = host.split(':')
                    host = parts[0]
                    port = int(parts[1])
#                    self.log.error("%s -n -c 1 %s -p %s -S 2>&1" % (self.config['bin'],host,port))
                    command = "%s -n -c 1 %s -p %s -S 2>&1" % (self.config['bin'],host,port)
                    metric_name = "%s_%s" % (host.replace('.', '_'),port)
                else:
                    metric_name = host.replace('.', '_')
#                    self.log.error("%s -nq -c 1 %s" % (self.config['bin'],host))
                    command = [self.config['bin'], '-nq', '-c 1', host]
#                    self.log.error("%s" % command)
                if not os.access(self.config['bin'], os.X_OK):
                    self.log.error("Path %s does not exist or is not executable"
                                   % self.config['bin'])
                    return

                if str_to_bool(self.config['use_sudo']):
                    command.insert(0, self.config['sudo_cmd'])

                ping = subprocess.Popen(
                    command, stdout=subprocess.PIPE,shell=True).communicate()[0] #.strip(
#                    ).split("\n")[-1]

                # # Linux
                # if ping.startswith('rtt'):
                #     ping = ping.split()[3].split('/')[0]
                #     metric_value = float(ping)
                # # OS X
                # elif ping.startswith('round-trip '):
                #     ping = ping.split()[3].split('/')[0]
                #     metric_value = float(ping)
                # # Unknown
                # else:

#                self.log.error("%s" % ping.split('/'))
#                self.log.error("3 %s" % ping.split('/')[3])
                ping = ping.split('/')[3]
                metric_value = float(ping)
#                    metric_value = 10000

                self.publish(metric_name, metric_value)
