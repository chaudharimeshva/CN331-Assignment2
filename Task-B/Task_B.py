# part_b.py
from mininet.log import info
import time
import pyshark  # used for reading URLs from PCAP files

def extract_urls_from_pcap(pcap_file):
    """
    Extracts unique DNS query URLs from the given PCAP file.
    """
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter="dns.qry.name")
        urls = [pkt.dns.qry_name for pkt in cap if hasattr(pkt, 'dns')]
        cap.close()
        return list(set(urls))
    except Exception as e:
        info(f"Error reading {pcap_file}: {e}\n")
        return []

def run_dns_queries(host, pcap_file):
    """
    Runs 'dig' for every URL found in the PCAP file on the given host
    and reports performance metrics.
    """
    info(f'\n--- Running DNS queries for {host.name} ---\n')

    urls = extract_urls_from_pcap(pcap_file)
    if not urls:
        info(f'No URLs found in {pcap_file} for {host.name}.\n')
        return

    total_latency = 0
    success_count = 0
    fail_count = 0
    query_count = len(urls)
    total_bytes=0
    total_packets=0
    
    start_time = time.time()
    
    for url in urls:
        cmd = f"dig @8.8.8.8 {url} +time=5 +tries=2"
        output = host.cmd(cmd)
        total_packets += 1
        total_bytes+=len(output.encode())
        if "status: NOERROR" in output and "ANSWER SECTION:" in output:
            success_count += 1
            for line in output.splitlines():
                if "Query time:" in line:
                    try:
                        latency = int(line.split('Query time: ')[1].split(' msec')[0])
                        total_latency += latency
                    except (IndexError, ValueError):
                        info(f"Warning: Could not parse latency for {url}\n")
                    break
        else:
            fail_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    avg_latency = total_latency / success_count if success_count > 0 else 0
    throughput = total_bytes / total_time if total_time > 0 else 0

    info(f'     --- Results of {host.name}---\n')
    info(f'Total packets:          {total_packets}\n')
    info(f'Successfully resolved: {success_count}\n')
    info(f'Failed resolutions:     {fail_count}\n')
    info(f'Average lookup latency: {avg_latency:.2f} msec\n')
    info(f'Average throughput:     {throughput:.2f} Bytes/sec\n')


def run_part_b(h1, h2, h3, h4):
    """
    function to run the DNS query tests for Task-B.
    """
    info('*** Running Queries for Task-B ***\n')

    # Each host processes its own PCAP file
    run_dns_queries(h1, 'PCAP_1_H1.pcap')
    run_dns_queries(h2, 'PCAP_2_H2.pcap')
    run_dns_queries(h3, 'PCAP_3_H3.pcap')
    run_dns_queries(h4, 'PCAP_4_H4.pcap')

