"""
kube-shodan registers all public IPs of a Kubernetes cluster to monitor.shodan.io.
"""

import logging
from time import sleep

import click
import shodan
from kubernetes import client, config

logging.basicConfig(level=logging.INFO, format='[%(asctime)s: %(levelname)s/%(name)s] %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def get_node_ips(api_client: client.CoreV1Api) -> []:
    """Get public IPs (ExternalIP) of all nodes."""
    ips = []
    ret = api_client.list_node(watch=False)
    for i in ret.items:
        for address in i.status.addresses:
            if address.type == 'ExternalIP':
                ips.append(address.address)
    return ips


def get_loadbalancer_ips(api_client: client.CoreV1Api) -> []:
    """Get public IPs of all load balancers (LoadBalancer)."""
    all_services = api_client.list_service_for_all_namespaces()
    loadbalancers = []
    for service in all_services.items:
        if service.spec.type == 'LoadBalancer' and service.status.load_balancer.ingress:
            for ingress in service.status.load_balancer.ingress:
                loadbalancers.append(ingress)
    ips = [l.ip for l in loadbalancers if l.ip]
    return ips


def get_all_ips(api_client: client.CoreV1Api, cidr: str = '') -> []:
    """Get all public IPs of the cluster (ExternalIP and LoadBalancer)."""
    ips = get_node_ips(api_client) + get_loadbalancer_ips(api_client)
    if cidr:
        ips = ['{}/{}'.format(ip, cidr) for ip in ips]
    return list(set(ips))


def get_shodan_alert(api_client: shodan.Shodan, alert_name: str) -> dict:
    """Get a configured Shodan alert based on its name."""
    current_alerts = api_client.alerts()
    found_alert = None
    for alert in current_alerts:
        if alert['name'] == alert_name:
            found_alert = alert
    return found_alert


def create_shodan_alert(api_client: shodan.Shodan, alert_name: str, ips: []):
    """Create a new Shodan alert."""
    LOGGER.info('Shodan alert does not exist yet, creating "%s".', alert_name)
    return api_client.create_alert(alert_name, ips)


def enable_all_triggers(api_client: shodan.Shodan, alert: {}):
    """Enable all triggers of a Shodan alert."""
    available_triggers = api_client.alert_triggers()
    enabled_triggers = list(alert['triggers'].keys())
    for trigger in available_triggers:
        if trigger['name'] not in enabled_triggers:
            LOGGER.debug('Enable %s trigger.', trigger['name'])
            api_client.enable_alert_trigger(alert['id'], trigger['name'])


def update_shodan_alert(api_client: shodan.Shodan, alert: {}, ips: []):
    """Update the monitored IPs of a Shodan alert."""
    LOGGER.debug('Updating monitored IPs to: %s', ', '.join(ips))
    api_client.edit_alert(alert['id'], ips)


def reconcile(kube_api: client.CoreV1Api, shodan_api: shodan.Shodan, shodan_alert_name: str):
    """Sync all public IPs of the Kubernetes cluster to a Shodan alert."""
    LOGGER.info('Reconciling %s.', shodan_alert_name)
    cluster_ips = get_all_ips(kube_api, cidr='32')
    shodan_alert = get_shodan_alert(shodan_api, shodan_alert_name)

    if shodan_alert:
        if set(shodan_alert['filters']['ip']) != set(cluster_ips):
            update_shodan_alert(shodan_api, shodan_alert, cluster_ips)
    else:
        shodan_alert = create_shodan_alert(shodan_api, shodan_alert_name, cluster_ips)

    enable_all_triggers(shodan_api, shodan_alert)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--shodan-api-key', '-k', required=True,
              help='API key of an existing shodan account.')
@click.option('--shodan-alert-name', '-n', help='Name of the shodan alert to configure')
@click.option('--run-outside-cluster', '-o', is_flag=True, default=False,
              help='Assume kube-shodan does not run in the cluster, it will try to load'
                   ' a local kubeconfig instead of using auto-discovery.')
@click.option('--interval', '-i', default=60,
              help='Interval to syncrhonize the cluster IPs to shodan.')
def cli(shodan_api_key, shodan_alert_name, run_outside_cluster, interval):
    """
    kube-shodan registers all public IPs of a Kubernetes cluster to monitor.shodan.io.

    All options are also available as environment variables with the prefix KUBE_SHODAN,
    e.g. --shodan-api-key is KUBE_SHODAN_SHODAN_API_KEY.
    """

    if not shodan_alert_name:
        cluster_name = config.list_kube_config_contexts()[1]['context']['cluster']
        shodan_alert_name = 'kube-shodan-{}'.format(cluster_name)
        LOGGER.info('No alert name specified, using default "%s".', shodan_alert_name)

    if run_outside_cluster:
        config.load_kube_config()
    else:
        config.load_incluster_config()

    kube_api = client.CoreV1Api()
    shodan_api = shodan.Shodan(shodan_api_key)

    while True:
        reconcile(kube_api, shodan_api, shodan_alert_name)
        sleep(interval)


def main():
    """Entrypoint of kube-shodan."""
    cli(auto_envvar_prefix='KUBE_SHODAN') # pylint: disable=no-value-for-parameter,unexpected-keyword-arg


if __name__ == '__main__':
    main()
