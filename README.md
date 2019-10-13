# kube-shodan

[![Docker Repository on Quay](https://quay.io/repository/ekeih/kube-shodan/status "Docker Repository on Quay")](https://quay.io/repository/ekeih/kube-shodan)

kube-shodan monitors the public IPs of a Kubernetes cluster and adds new ones to [Shodan Monitor](https://monitor.shodan.io). IPs which are removed from the cluster are also removed from Shodan. This way all public IPs of the cluster will always be monitored by Shodan.

## Installation

### Helm

```
TBD
```

### pip

```
pip install kube-shodan
```

### Manual

```
git clone git@github.com:ekeih/kube-shodan.git
cd kube-shodan
pip install .
```