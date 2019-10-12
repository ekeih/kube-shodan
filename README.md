# kube-shodan

[![Docker Repository on Quay](https://quay.io/repository/ekeih/kube-shodan/status "Docker Repository on Quay")](https://quay.io/repository/ekeih/kube-shodan)

kube-shodan monitors the public IPs of a Kubernetes cluster and adds new ones to [Shodan Monitor](https://monitor.shodan.io). IPs which are removed from the cluster are also removed from Shodan.