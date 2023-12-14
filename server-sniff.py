#!/usr/bin/env python
from scapy.all import *


def main():
    def handle(x: Packet):
        return x.show()

    sniff(filter="tcp", prn=handle)


if __name__ == '__main__':
    main()
