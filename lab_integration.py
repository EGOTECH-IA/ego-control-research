#!/usr/bin/env python3
"""Reproducible local integration; no access to worker/production."""
import os, pathlib, socket, subprocess, sys, tempfile, time

HOME = pathlib.Path(__file__).resolve().parent.parent
CONTROL = HOME / "ego-control"
TRUST = HOME / "ego-trust"
HOST = HOME / "ego-host-guard"
GUEST = HOME / "ego-guest-control"

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def client(sock, path):
    return subprocess.run(
        [sys.executable, str(GUEST / "guest.py"), "read", "--unix", str(sock), "--path", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=10,
    )

def main():
    for path in [CONTROL / "core/rust/Cargo.toml", TRUST / "trust.py",
                 HOST / "host_guard.py", GUEST / "guest.py"]:
        if not path.is_file():
            raise RuntimeError(f"missing sibling repository file: {path}")
    print("Building EGO CORE Rust gate...", flush=True)
    run("cargo", "build", "--release", "--bin", "ego-core-gate", cwd=CONTROL / "core/rust")
    gate = CONTROL / "core/rust/target/release/ego-core-gate"
    with tempfile.TemporaryDirectory(prefix="ego-control-lab-") as temp:
        base = pathlib.Path(temp)
        root = base / "root"
        (root / "allowed").mkdir(parents=True)
        (root / "private").mkdir()
        (root / "allowed" / "readme.txt").write_bytes(b"AUTHORIZED_EGO_READ")
        (root / "private" / "credentials.txt").write_bytes(b"FORBIDDEN_LAB_BYTES")
        key, policy, sock, audit = [base / n for n in ("policy.key", "policy.json", "host.sock", "audit.jsonl")]
        run(sys.executable, str(TRUST / "trust.py"), "init", "--key", str(key))
        run(sys.executable, str(TRUST / "trust.py"), "sign", "--key", str(key),
            "--subject", f"uid:{os.getuid()}", "--scope", "allowed", "--out", str(policy))
        process = subprocess.Popen(
            [sys.executable, str(HOST / "host_guard.py"), "--root", str(root),
             "--socket", str(sock), "--key", str(key), "--policy", str(policy),
             "--gate", str(gate), "--audit", str(audit)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            for _ in range(100):
                if sock.exists(): break
                if process.poll() is not None:
                    raise RuntimeError("host guard terminated before listening")
                time.sleep(0.05)
            else: raise RuntimeError("host guard socket not created")
            def check(path, allowed):
                result = client(sock, path)
                if allowed:
                    assert result.returncode == 0, (path, result.stderr)
                    assert result.stdout == b"AUTHORIZED_EGO_READ", path
                else:
                    assert result.returncode != 0, f"unexpected grant for {path}"
                    assert b"FORBIDDEN_LAB_BYTES" not in result.stdout, path
                print(f"{'ALLOW' if allowed else 'DENY'}: {path}")
            check("allowed/readme.txt", True)
            check("private/credentials.txt", False)
            check("allowed/../../private/credentials.txt", False)
            check("allowed/../private/credentials.txt", False)
            check("allowed/readme.txt/../../private/credentials.txt", False)
            # Symlink targets must never be resolved by the host broker.
            os.symlink("../private/credentials.txt", root / "allowed" / "alias")
            check("allowed/alias", False)
            # Poison the authenticated policy and verify fail-closed behavior.
            policy.write_bytes(b'{"policy":{},"mac":"bad"}')
            check("allowed/readme.txt", False)
            print("EGO LAB: 7 negative/positive checks passed; audit:", audit.read_text().count("\n"), "records")
        finally:
            process.terminate()
            try: process.wait(timeout=3)
            except subprocess.TimeoutExpired: process.kill(); process.wait()

if __name__ == "__main__":
    main()
