import subprocess
import sys
import os

def main():
    tex_file = "report.tex"
    pdf_file = "report.pdf"
    
    tectonic_bin = os.path.expanduser("~/.local/bin/tectonic")
    if not os.path.exists(tectonic_bin):
        tectonic_bin = "tectonic"

    print(f"[+] Compiling {tex_file} -> {pdf_file} using {tectonic_bin}...")
    cmd = [tectonic_bin, tex_file]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("[+] LaTeX Compilation Successful!")
        info = subprocess.check_output(["pdfinfo", pdf_file]).decode("utf-8")
        print(info)
    else:
        print(f"[-] Compilation failed with code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()

