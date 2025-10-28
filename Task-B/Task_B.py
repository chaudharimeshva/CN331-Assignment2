#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import time
import re
import os


class DNSTopo(Topo):
    """
    Custom topology for DNS performance testing.
    """
    def build(self):
        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        dns = self.addHost('dns', ip='10.0.0.5/24')  # DNS host not used as server here

        # Switches
        s1, s2, s3, s4 = [self.addSwitch(f's{i}') for i in range(1, 5)]

        # Link configuration
        params = {'bw': 100}

        # Host–switch connections
        self.addLink(h1, s1, delay='2ms', **params)
        self.addLink(h2, s2, delay='2ms', **params)
        self.addLink(h3, s3, delay='2ms', **params)
        self.addLink(h4, s4, delay='2ms', **params)
        self.addLink(dns, s2, delay='1ms', **params)

        # Inter-switch connections
        self.addLink(s1, s2, delay='5ms', **params)
        self.addLink(s2, s3, delay='8ms', **params)
        self.addLink(s3, s4, delay='10ms', **params)


def perform_dns_queries(host):
    """
    Executes DNS lookups for domains listed in queriesX.txt
    using the host’s default resolver from /etc/resolv.conf.
    """
    filename = f"queries{host.name[1:]}.txt"
    info(f"--- Executing queries for {host.name} from {filename} ---\n")

    try:
        with open(filename) as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        info(f"  File {filename} not found. Skipping {host.name}.\n")
        return

    latencies, success, failure = [], 0, 0
    start = time.time()

    for domain in domains:
        result = host.cmd(f'dig {domain}')

        if "status: NOERROR" in result:
            success += 1
            match = re.search(r"Query time: (\d+) msec", result)
            if match:
                latencies.append(int(match.group(1)))
        else:
            failure += 1

    duration = time.time() - start
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    throughput = success / duration if duration > 0 else 0

    print(f"Results for {host.name}:")
    print(f"   Successful Resolutions: {success}")
    print(f"   Failed Resolutions....: {failure}")
    print(f"   Average Lookup Latency: {avg_latency:.2f} ms")
    print(f"   Average Throughput....: {throughput:.2f} QPS\n")


def run_dns_experiment():
    """
    Sets up the network, configures resolvers, runs DNS tests, and terminates.
    """
    topo = DNSTopo()
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)

    nat = net.addNAT()
    nat.configDefault()
    net.start()

    info(" Network initialized with NAT support.\n")

    hosts = [net.get(f'h{i}') for i in range(1, 5)]

    info("Setting nameservers for all hosts...\n")
    for h in hosts:
        h.cmd('echo "nameserver 8.8.8.8" > /etc/resolv.conf')
        info(f"{h.name}: nameserver configured\n")

    for h in hosts:
        perform_dns_queries(h)

    net.stop()
    info(" Simulation complete.\n")


if _name_ == '_main_':
    setLogLevel('info')
    run_dns_experiment()