from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class DNSTopology(Topo):
    """
    Defines a network topology with four hosts, one DNS server, and four switches.
    """
    def build(self):
        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        dns = self.addHost('dns', ip='10.0.0.5/24')

        # Switches
        s1, s2, s3, s4 = [self.addSwitch(f's{i}') for i in range(1, 5)]

        # Common link parameters
        params = {'bw': 100}

        # Host-switch links
        self.addLink(h1, s1, delay='2ms', **params)
        self.addLink(h2, s2, delay='2ms', **params)
        self.addLink(h3, s3, delay='2ms', **params)
        self.addLink(h4, s4, delay='2ms', **params)
        self.addLink(dns, s2, delay='1ms', **params)

        # Inter-switch links
        self.addLink(s1, s2, delay='5ms', **params)
        self.addLink(s2, s3, delay='8ms', **params)
        self.addLink(s3, s4, delay='10ms', **params)


def setup_custom_dns():
    """
    Launches the network and sets all hosts to use 10.0.0.5 as their DNS server.
    Verifies configuration by inspecting /etc/resolv.conf on h1.
    """
    topo = DNSTopology()
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)
    net.start()
    info("Network launched successfully.\n")

    hosts = [net.get(f'h{i}') for i in range(1, 5)]
    dns_ip = net.get('dns').IP()

    info(f"\n--- Setting DNS resolver to {dns_ip} for all hosts ---\n")
    for h in hosts:
        h.cmd(f'echo "nameserver {dns_ip}" > /etc/resolv.conf')
        info(f"{h.name} configured.\n")

    info("\n--- Verifying configuration on h1 ---\n")
    h1 = net.get('h1')
    result = h1.cmd('cat /etc/resolv.conf')
    print(f"h1$ cat /etc/resolv.conf\n{result}")

    if dns_ip in result:
        info(" Verification passed: h1 is using the correct resolver.\n")
    else:
        info(" Verification failed: resolver not set correctly.\n")

    info("Network ready. Use CLI for testing (e.g., 'h1 ping h4').\n")
    CLI(net)

    net.stop()
    info(" Network stopped.\n")


if _name_ == '_main_':
    setLogLevel('info')
    setup_custom_dns()