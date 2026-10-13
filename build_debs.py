#!/usr/bin/env python3
"""Build host/guest Debian research packages from five sibling checkouts.
No auto-start and no secret files are embedded. Requires dpkg-deb + cargo.
"""
import pathlib, shutil, subprocess, tempfile

PARENT = pathlib.Path(__file__).resolve().parent.parent
CONTROL = PARENT / "ego-control"
TRUST = PARENT / "ego-trust"
HOST = PARENT / "ego-host-guard"
GUEST = PARENT / "ego-guest-control"
OUT = PARENT / "ego-control-research" / "dist"

def put(src, target, executable=True):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)
    target.chmod(0o755 if executable else 0o644)

def deb(name, version, files):
    with tempfile.TemporaryDirectory(prefix="ego-deb-") as temp:
        root = pathlib.Path(temp)
        control = root / "DEBIAN"
        control.mkdir()
        (control / "control").write_text(
            f"Package: {name}\nVersion: {version}\nSection: admin\nPriority: optional\n"
            "Architecture: amd64\nMaintainer: EGOTECH Research <research@example.invalid>\n"
            "Depends: python3 (>= 3.10)\n"
            "Description: EGO CONTROL experimental host/guest laboratory component\n"
            " Not for production use; no privileged service auto-started.\n"
        )
        for src, dest in files:
            if not src.is_file():
                raise FileNotFoundError(src)
            put(src, root / dest.lstrip("/"))
        OUT.mkdir(exist_ok=True)
        archive = OUT / f"{name}_{version}_amd64.deb"
        subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(root), str(archive)], check=True)
        print(archive)

def main():
    subprocess.run(["cargo", "build", "--release", "--bin", "ego-core-gate"],
                   cwd=CONTROL / "core/rust", check=True)
    gate = CONTROL / "core/rust/target/release/ego-core-gate"
    deb("ego-control-host-lab", "0.1.0", [
        (gate, "/usr/lib/ego-control/ego-core-gate"),
        (HOST / "host_guard.py", "/usr/lib/ego-control/ego-host-guard"),
        (TRUST / "trust.py", "/usr/lib/ego-control/ego-trust"),
    ])
    deb("ego-control-guest-lab", "0.1.0", [
        (GUEST / "guest.py", "/usr/lib/ego-control/ego-guest"),
    ])
    print("LAB packages built: no policy secret, protected storage or daemon activation included.")

if __name__ == "__main__":
    main()
