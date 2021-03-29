# Task 3 - Protocol State Fuzzing

## Introduction
In this part of the assignment we will look at a more serious task: protocol state fuzzing of TLS. Protocol state fuzzing uses active state machine learning to learn how a protocol behaves. This will result in a state machine representing the implementation of said protocol, which allows us to inspect it for errors and/or implementation flaws. 

We will use [TLSAttacker](https://github.com/tls-attacker/TLS-Attacker) to send TLS messages to openSSL, using an adapter class we already provided for you in the Task3 Folder. 
Before you can begin, you need to do the following:

- Set up TLSAttacker according to the guide on their github page
- Download and compile [OpenSSL 1.0.1g](https://github.com/openssl/openssl/releases/tag/OpenSSL_1_0_1g)
- Download and compile [OpenSSL 1.1.1k](https://github.com/openssl/openssl/releases/tag/OpenSSL_1_1_1k)

The instructions for compiling OpenSSL are included in the source.

After doing this you should have a folder with the following contents:
```
├── ASN.1-Tool
├── openssl-OpenSSL_1_0_1g
├── openssl-OpenSSL_1_1_1k
├── TLS-Attacker
└── x509-Attacker
```

To start an OpenSSL server, first `cd TLS-Attacker/resources` and run the `keygen.sh` script if you haven't already.
Then you can start your desired version of OpenSSL by running:
```
 ../../openssl-OpenSSL_*your version*/apps/openssl s_server -key rsa1024key.pem -cert rsa1024cert.pem
```

Once that is up and running, you are ready to start learning state machines!

## ChangeCipherSpec injection
Before we begin, read a bit about how the TLS protocol normally works. 
- [here](https://tls.ulfheim.net/)
- [or here](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/)

are good places to start. Try learning a state machine of a recent version of OpenSSL and see if you recognize the normal/happy flow in the state machine you obtain.

TLS is a complex protocol, and thus it is quite likely that implementations of it contain mistakes. One such mistake, discovered some years back, was the [ChangeCipherSpec](http://ccsinjection.lepidum.co.jp/) [injection](https://success.trendmicro.com/solution/1103813-trend-micro-products-and-the-ccs-injection-vulnerability--cve-2014-0224-openssl-vulnerability) vulnerability.

This vulnerability allowed an attacker to send a non-standard handshake, which caused the server to use weak cryptographic keys,
which is of course a bad thing if you want to secure your communications.

This vulnerability was still present in OpenSSL 1.0.1g. Learn a state machine of this version and spot the vulnerability.
