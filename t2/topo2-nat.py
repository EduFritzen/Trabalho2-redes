from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class BasicTopo(Topo):
    def build(self, **_opts):
        sw1 = self.addSwitch('sw1', cls=OVSBridge)
        sw2 = self.addSwitch('sw2', cls=OVSBridge) 
        router = self.addHost('router', ip=None)
        host = self.addHost('host', ip='10.1.1.1/24', defaultRoute='via 10.1.1.254')

        server = self.addHost('server', ip='8.8.8.8/16', defaultRoute='via 8.8.254.254')

        self.addLink(host, sw1)
        self.addLink(sw1, router, intfName2='r-eth0', params2={'ip': '10.1.1.254/24'})

        self.addLink(server, sw2)
        self.addLink(sw2, router, intfName2='r-eth1', params2={'ip': '8.8.254.254/16'})

def run():
    net = Mininet(topo=BasicTopo(), controller=None)
    net.get('server').cmd('iperf -s -p 8888 &')
    net.get('router').cmd('iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP')

    for _, v in net.nameToNode.items():
        for itf in v.intfList():
            v.cmd('ethtool -K ' + itf.name + ' tx off rx off')
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()