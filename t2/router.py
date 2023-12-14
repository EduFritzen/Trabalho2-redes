from scapy.all import *

from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether

def substitute_badwords(text: str):
    copy = text
    with open("badwords2.txt", "r") as file:
        for word in file.readlines():
            word = word.replace('\n', '')
            copy = copy.replace(word,"*" * len(word))
    print("\nt1:\n", text)        
    print("\nt2:\n", copy)
    return copy

def main():
    public_interface = 'r-eth1'
    internal_interface = 'r-eth0'
    output_interface = {
        internal_interface: public_interface,
        public_interface: internal_interface
    }
    supported_protocols = {
        UDP: {"destination_port": "dport", "source_port": "sport"},
        ICMP: {"destination_port": "id", "source_port": "id"},
        TCP: {"destination_port": "dport", "source_port": "sport"}
    }

    def badword_filter(newpkt):
        if TCP in newpkt and newpkt[TCP].payload:
            payload = newpkt[TCP].payload.load.decode('utf-8')
            payload_filtered = bytes(substitute_badwords(payload), 'utf-8')

            newpkt_copy = newpkt.copy()
            newpkt_copy[TCP].payload = Raw(payload_filtered)
            return recalc_check_sum(newpkt_copy)
        return newpkt

    def recalc_check_sum(pkt: Packet):
        del pkt[IP].chksum
        del pkt[IP].payload.chksum
        return pkt.__class__(bytes(pkt))

    def ip(interface: str):
        return get_if_addr(interface)

    def mac(interface: str):
        return get_if_hwaddr(interface)

    def we_just_sent_it(pkt: Packet):
        if pkt[Ether].src == mac(pkt.sniffed_on):
            return True
        return False

    def update_packet_ips(pkt, src=None, dst=None):
        pkt = pkt.copy()
        if src is None:
            src = pkt[IP].src
        if dst is None:
            dst = pkt[IP].dst
        pkt[IP].src = src
        pkt[IP].dst = dst
        pkt[IP].ttl = pkt[IP].ttl - 1
        pkt[Ether].src = None
        pkt[Ether].dst = None
        return recalc_check_sum(pkt)

    def supports_packet(pkt: Packet):
        if IP not in pkt:
            return False
        for protocol in supported_protocols.keys():
            if protocol in pkt:
                return True
        return False

    def get_protocol(pkt: Packet):
        for protocol in supported_protocols:
            if protocol in pkt:
                return protocol

        raise Exception("Unsupported protocol.")

    def ports_and_protocol(pkt: Packet):
        """returns destination_port, source_port, protocol"""
        protocol = get_protocol(pkt)
        protocol_layer = pkt[protocol]
        protocol_fields = supported_protocols[protocol]
        destination_port = protocol_layer.getfieldval(protocol_fields["destination_port"])
        source_port = protocol_layer.getfieldval(protocol_fields["source_port"])
        return destination_port, source_port, protocol

    class NatRouter:
        translation_table = {}

        def nat(self, pkt: Packet):
            if not supports_packet(pkt):
                return

            if we_just_sent_it(pkt):
                return

            new_pkt = self.handle(pkt)
            iface = output_interface[pkt.sniffed_on]

            if new_pkt:
                new_pkt_filtered = badword_filter(new_pkt)
                #new_pkt_filtered.show()
                sendp(new_pkt_filtered, iface=iface, verbose=False)

        def handle(self, pkt: Packet):
            if pkt.sniffed_on == public_interface:
                return self.public_packet_handler(pkt)
            if pkt.sniffed_on == internal_interface:
                return self.internal_packet_handler(pkt)
            return False

        def internal_packet_handler(self, pkt: Packet):
            self.store_internal_packet_internal_ip(pkt)
            return update_packet_ips(pkt, src=ip(public_interface))

        def public_packet_handler(self, pkt: Packet):
            local_ip = self.find_public_packet_internal_ip(pkt)
            if local_ip is None:
                return False
            return update_packet_ips(pkt, dst=local_ip)

        def store_internal_packet_internal_ip(self, pkt: Packet):
            source_port, destination_port, protocol = ports_and_protocol(pkt)
            key = (protocol, pkt[IP].dst, source_port, destination_port)
            self.translation_table[key] = pkt[IP].src

        def find_public_packet_internal_ip(self, pkt: Packet):
            source_port, destination_port, protocol = ports_and_protocol(pkt)
            key = (protocol, pkt[IP].src, destination_port, source_port)
            if key in self.translation_table:
                return self.translation_table[key]
            return None

        def sniff(self):
            sniff(iface=[public_interface, internal_interface], prn=self.nat)

    router = NatRouter()
    router.sniff()


if __name__ == '__main__':
    main()