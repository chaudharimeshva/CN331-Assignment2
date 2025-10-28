#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSController
from mininet.nodelib import NAT
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI


# Creates the custom topology
def create_topology():
 
    net = Mininet(controller=OVSController, link=TCLink)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('H1', ip='10.0.0.1/8')
    h2 = net.addHost('H2', ip='10.0.0.2/8')
    h3 = net.addHost('H3', ip='10.0.0.3/8')
    h4 = net.addHost('H4', ip='10.0.0.4/8')
    dns = net.addHost('DNS', cls=NAT, ip='10.0.0.5/8', inNamespace=False)

    info('*** Adding switches\n')
    s1 = net.addSwitch('S1')
    s2 = net.addSwitch('S2')
    s3 = net.addSwitch('S3')
    s4 = net.addSwitch('S4')

    info('*** Creating links\n')
    net.addLink(h1, s1, bw=100, delay='2ms')
    net.addLink(h2, s2, bw=100, delay='2ms')
    net.addLink(h3, s3, bw=100, delay='2ms')
    net.addLink(h4, s4, bw=100, delay='2ms')
    net.addLink(dns, s2, bw=100, delay='1ms')

    net.addLink(s1, s2, bw=100, delay='5ms')
    net.addLink(s2, s3, bw=100, delay='8ms')
    net.addLink(s3, s4, bw=100, delay='10ms')

    info('*** Starting network\n')
    net.start()

    info('*** Setting default routes\n')
    for h in [h1, h2, h3, h4]:
        h.setDefaultRoute(f'via {dns.IP()}')

    info('*** Testing connectivity\n')
    net.pingAll()
    
    Task_B.run_part_b(h1, h2, h3, h4)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()

