import click

from openvpn.api import (
    ec2_associate_address,
    ec2_release_address,
    ec2_start_instance,
    ec2_stop_instance,
    get_ec2,
    get_route53,
    route53_create,
    route53_delete,
)
from openvpn.io import read_config
from openvpn.utils import OpenVPNError, print_error


def openvpn_start(ec2, route53, instance_id, hosted_zone_id, domain):
    ip = ec2_associate_address(ec2, instance_id)
    route53_create(route53, hosted_zone_id, domain, ip)
    ec2_start_instance(ec2, instance_id)


def openvpn_stop(ec2, route53, instance_id, hosted_zone_id, domain):
    ec2_stop_instance(ec2, instance_id)
    ip = ec2_release_address(ec2, instance_id)
    route53_delete(route53, hosted_zone_id, domain, ip)


@click.command()
@click.argument('mode', type=click.Choice(['start', 'stop']))
def main(mode):
    ''' Simple Handmade OpenVPN AS Trigger '''
    try:
        config = read_config()
    except OpenVPNError as e:
        print_error(e)
        exit(1)

    ec2 = get_ec2(config['aws_access_key_id'], config['aws_secret_access_key'], config['region_name'])
    route53 = get_route53(config['aws_access_key_id'], config['aws_secret_access_key'])
    method = openvpn_start if mode == 'start' else openvpn_stop

    try:
        method(ec2, route53, config['instance_id'], config['hosted_zone_id'], config['domain'])
    except OpenVPNError as e:
        print_error(e)
        exit(1)


if __name__ == '__main__':
    main()
