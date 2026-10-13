# EGO CONTROL — End-to-end integration laboratory

**Status:** connected research prototype, not certified VM containment or production protection.

This public repository contains a launcher/tests referencing four companion repositories:
- [ego-control](https://github.com/EGOTECH-IA/ego-control) (private): Rust EGO CORE 10, `ego-core-gate`.
- [ego-trust](https://github.com/EGOTECH-IA/ego-trust) (private): laboratory policy issuer/authentication.
- [ego-host-guard](https://github.com/EGOTECH-IA/ego-host-guard) (private): protected host-side broker.
- [ego-guest-control](https://github.com/EGOTECH-IA/ego-guest-control) (private): untrusted client.

Users must have authorized GitHub access to clone the private components. The research repository intentionally contains **no secrets or private component sources**.

## Local integration

Clone all five into sibling directories, install Python 3.10+, Rust/Cargo and Linux, then run:

```sh
cd ego-control-research
python3 lab_integration.py
```

The script builds the Rust core gate, issues a **temporary** HMAC-authenticated laboratory policy, starts Host Guard, sends operations using Guest Control, and asserts that an authorized file is returned while unauthorized and traversal requests do not disclose bytes. Everything uses randomly named disposable directories; no production host service is touched.

## VM integration path

Host Guard supports an optional Linux AF_VSOCK listener and Guest Control supports `--vsock 2:<port>`. QEMU/KVM must be configured for vsock and assign the guest a CID; an external host-held policy must authorize **that exact VM CID** and no host protected files should be mounted into the guest. A root actor inside the guest can still request operations as the *entire VM*: per-process identity and non-bypass coverage are future investigation.

Do not assert that this lab proves prevention of GitHub Copilot, LangChain or MCP Server Git CVEs: those are presently **modelled case studies**, not reproductions of vulnerable product builds. Likewise, no real Git staging/HTTP mediator exists yet.
