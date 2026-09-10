#!/usr/bin/env python3
"""FK Agent OS — create the GCP production VM via Compute REST API.
Usage: python3 gcp-create-vm.py <sa_key.json> [zone]
- Enables compute API, creates firewall (22/80/443) + e2-micro VM (Ubuntu 22.04,
  30GB standard PD, standard tier, ephemeral external IP, SSH key metadata),
  waits for RUNNING, prints the external IP.
Scope needed on the SA: roles/compute.admin (single project)."""
import base64, json, sys, time, urllib.request

def jwt_token(sa):
    from jwt import encode
    now = int(time.time())
    tok = encode({"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/compute",
                  "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600},
                 sa["private_key"], algorithm="RS256")
    d = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": tok}).encode()
    r = urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=d), timeout=30)
    return json.loads(r.read())["access_token"]

def api(tok, method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "***" + tok, "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        b = r.read()
        return r.status, (json.loads(b) if b else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def wait_op(op, project, tok):
    while op.get("status") != "DONE":
        st, op = api(tok, "GET", f"https://compute.googleapis.com/compute/v1/projects/{project}/global/operations/{op['name']}")
        if st != 200: break
        time.sleep(5)
    return op

def main():
    sa = json.load(open(sys.argv[1]))
    project = sa["project_id"]
    zone = sys.argv[2] if len(sys.argv) > 2 else "us-central1-a"
    name = "fk-agent-os"
    ssh_key = open(sys.argv[3] if len(sys.argv) > 3 else "/tmp/gcp_deploy.pub").read().strip()
    tok = jwt_token(sa)
    base = f"https://compute.googleapis.com/compute/v1/projects/{project}/zones/{zone}"

    st, body = api(tok, "POST", f"https://serviceusage.googleapis.com/v1/projects/{project}:services/compute.googleapis.com:enable")
    print("enable compute:", st)
    time.sleep(10)

    for port in ("22", "80", "443"):
        st, b = api(tok, "GET", base + f"/firewalls/fk-allow-{port}")
        if st == 404:
            fw = {"name": f"fk-allow-{port}", "network": "default", "allowed": [{"IPProtocol": "tcp", "ports": [port]}], "sourceRanges": ["0.0.0.0/0"], "direction": "INGRESS"}
            st, b = api(tok, "POST", base + "/firewalls", fw)
            print(f"firewall {port}:", st)

    st, exists = api(tok, "GET", base + f"/instances/{name}")
    if st == 200:
        print("VM already exists:", exists["name"])
        for ni in exists.get("networkInterfaces", []):
            for acc in ni.get("accessConfigs", []):
                print("EXTERNAL_IP", acc.get("natIP"))
        return

    vm = {
        "name": name,
        "machineType": f"zones/{zone}/machineTypes/e2-micro",
        "labels": {"managed-by": "fk-agent-os", "tier": "always-free"},
        "disks": [{"boot": True, "autoDelete": True,
                   "initializeParams": {"diskSizeGb": "30", "sourceImage": "projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts",
                                         "diskType": f"zones/{zone}/diskTypes/pd-standard"}}],
        "networkInterfaces": [{"network": "global/networks/default", "accessConfigs": [{"name": "ExternalNAT", "type": "ONE_TO_ONE_NAT"}]}],
        "metadata": {"items": [{"key": "ssh-keys", "value": f"root:{ssh_key}"}]},
        "scheduling": {"onHostMaintenance": "MIGRATE"},
        "tags": {"items": ["http-server", "https-server"]},
    }
    st, op = api(tok, "POST", base + "/instances", vm)
    if st != 200:
        print("CREATE FAIL:", st, json.dumps(op)[:500]); sys.exit(1)
    op = wait_op(op, project, tok)
    if op.get("status") != "DONE":
        print("OP ERROR:", json.dumps(op)[:500]); sys.exit(1)
    st, vm = api(tok, "GET", base + f"/instances/{name}")
    ip = vm["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    print("VM RUNNING |", zone, "| e2-micro | 30GB pd-standard | Ubuntu 22.04 LTS")
    print("EXTERNAL_IP", ip)

if __name__ == "__main__":
    import urllib.parse
    main()
