# kube-shodan

kube-shodan monitors the public IPs of a Kubernetes cluster and adds new ones to [Shodan Monitor](https://monitor.shodan.io). IPs which are removed from the cluster are also removed from Shodan. This way all public IPs of the cluster will always be monitored by Shodan.

## Installation

### Helm

```
helm repo add ekeih https://ekeih.github.io/helm-charts
helm repo up

# Pass Shodan token directly
helm install --namespace kube-shodan --name kube-shodan --set shodanApiToken=TOKEN ekeih/kube-shodan

# Or use Shodan token from existing secret
helm install --namespace kube-shodan --name kube-shodan --set shodanApiToken=SECRETNAME --set shodanApiSecretKey=SECRETKEY ekeih/kube-shodan
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
