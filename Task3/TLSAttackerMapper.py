from pathlib import Path
from subprocess import run

import xml.etree.ElementTree as ET
from typing import Iterable
from xml.dom import minidom
import tempfile

import time
import re

def _is_list(iterable):
    return isinstance(iterable, Iterable) and not isinstance(iterable, str)

class TLSTraceBuilder:
    def __init__(self):
        self.root = None
        self.reset()

    # Adds a message to be sent to the workflow trace
    def add_send(self, message):
        send = ET.SubElement(self.root, "Send")
        messages = ET.SubElement(send, "messages")
        messages.append(message)

    def GenericReceive(self):
        rcv = ET.SubElement(self.root, "GenericReceive")

    def ClientHello(self, extensions=None):
        xml = ET.Element("ClientHello")

        if extensions is not None and _is_list(extensions):
            extensions_xml = ET.SubElement(xml, "extensions")
            for extension in extensions:
                ET.SubElement(extensions_xml, extension)
        elif extensions is None:
            pass
        else:
            assert False, f"Extensions should be a list of strings: {extensions}"

        self.add_send(xml)

    def RSAClientKeyExchange(self, computations=None):
        xml = ET.Element("RSAClientKeyExchange")

        if computations is not None and _is_list(computations):
            computations_xml = ET.SubElement(xml, "computations")
            for computation in computations:
                ET.SubElement(computations_xml, computation)
        elif computations is None:
            ET.SubElement(xml, "computations")
        else:
            assert False, f"Computations should be a list of strings: {computations}"

        self.add_send(xml)

    def Certificate(self):
        self.add_send(ET.Element("Certificate"))

    def CertificateRequest(self):
        self.add_send(ET.Element("CertificateRequest"))

    def ChangeCipherSpec(self):
        self.add_send(ET.Element("ChangeCipherSpec"))

    def Finished(self):
        self.add_send(ET.Element("Finished"))

    def Application(self, content=None):
        xml = ET.Element("Application")
        if content is not None:
            data = ET.SubElement(xml, "data")
            mod = ET.SubElement(data, "byteArrayExplicitValueModification")
            val = ET.SubElement(mod, "explicitValue")
            val.text = " ".join("{:02x}".format(ord(c)) for c in content)
        self.add_send(xml)

    def Heartbeat(self, payloadsize=None):
        xml = ET.Element("Heartbeat")
        if payloadsize is not None:
            payloadlen = ET.SubElement(xml, "payloadLength")
            mod = ET.SubElement(payloadlen, "integerExplicitValueModification")
            val = ET.SubElement(mod, "explicitValue")
            val.text = str(payloadsize)
        self.add_send(xml)

    def print(self):
        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        print(xmlstr)

    def write_file(self, file):
        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        file.write(xmlstr)

    def write_path(self, path):
        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        with open(path, 'r') as file:
            file.write(xmlstr)

    def reset(self):
        self.root = ET.Element('workflowTrace')

class TLSAttackerMapper:
    def __init__(self, tlsa_path, addr='localhost', port='4433', enable_heartbeat=False):
        assert Path(tlsa_path).is_file(), f"Invalid TLSAttacker path: {tlsa_path}"
        self.tlsa_path = tlsa_path
        can_run, err_msg = self._can_run_tlsattacker()
        assert self._can_run_tlsattacker(), f"Failed to run TLS-Client.jar: {err_msg}"
        print("TLS Attacker initialized")

        self.addr = addr
        self.port = port

        self.tb = TLSTraceBuilder()

        self.mapping = {
            "ClientHello":          self.tb.ClientHello,
            "RSAClientKeyExchange": self.tb.RSAClientKeyExchange,
            "ChangeCipherSpec":     self.tb.ChangeCipherSpec,
            "Finished":             self.tb.Finished,
            "ApplicationEmpty":     self.tb.Application,
        }

        if enable_heartbeat:
            self.mapping["Heartbeat"] = self.tb.Heartbeat
            self.mapping["Heartbleed"] = lambda: self.tb.Heartbeat(20000)

    # Check if we can print the help message
    def _can_run_tlsattacker(self):
        result = run(['java', '-jar', self.tlsa_path, '-h'], capture_output=True)
        return 'Usage: <main class> [options]' in result.stdout.decode(), result.stderr.decode()

    # Parses TLSAttacker output and extracts the output symbols
    # TODO: talk to tlsattacker in a less fragile way. I really don't like parsing stdout
    def _parse_response(self, output):
        lines = output.split('\n')
        inputs = []
        outputs = []

        nextup = None
        for line in lines:

            # Check if this line is input
            if nextup is None or nextup == "input":
                match = re.search(r'SendAction - .*: (.*) $', line)
                if match:
                    inputs.append(tuple(filter(lambda x: len(x) > 0, match.group(1).strip().split(','))))
                    nextup = 'output'
                    continue

            # Or output
            if nextup is None or nextup == "output":
                match = re.search(r'GenericReceiveAction - .*: (.*) $', line)
                if match:
                    outputs.append(tuple(filter(lambda x: len(x) > 0, match.group(1).strip().split(','))))
                    nextup = 'input'
                    continue
                else:
                    match = re.search(r'GenericReceiveAction -', line)
                    if match:
                        outputs.append(('empty',))
                        nextup = 'input'

        return inputs, outputs



    def run(self, trace):
        print("Running trace:", trace)
        starttime = time.perf_counter()

        # Translate the given input trace to and XML workflow for TLSAttacker
        self.tb.reset()
        for action in trace:
            self.mapping[action]()
            self.tb.GenericReceive()

        # Write the workflow to a temporary file and run TLSAttacker
        with tempfile.NamedTemporaryFile(mode='w') as tmp_file:
            self.tb.write_file(tmp_file)
            tmp_file.flush()
            result = run([
                'java', '-jar', self.tlsa_path,
                '-connect', f'{self.addr}:{self.port}',
                '-workflow_input', tmp_file.name,
                '-timeout', '10'
            ], capture_output=True)

        # Decode TLSAttackers output
        inputs, outputs = self._parse_response(result.stdout.decode())
        print(result.stdout.decode())

        print("Trace execution took ", f'{(time.perf_counter() - starttime):.3f} s')

        return inputs, outputs