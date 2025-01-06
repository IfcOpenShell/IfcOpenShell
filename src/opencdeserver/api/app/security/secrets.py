from glob import glob


def get_secrets():
    secrets = dict()
    for var in glob("/run/secrets/*"):
        k = var.split("/")[-1]
        v = open(var).read().rstrip("\n")
        secrets[k] = v
    return secrets
