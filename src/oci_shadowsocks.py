# oci_shadowsocks.py
#
# This is the main controller for the OCI Shadowsocks Manager.
# It handles command-line arguments and orchestrates the various modules
# to manage the Shadowsocks instance on OCI and the local client.

import argparse
import sys
import os

from oci_manager import OCIManager
from local_client_manager import LocalClientManager
from config_manager import ConfigParser
from usage_tracker import UsageTracker

def main():
    """
    Main function to parse CLI commands and execute corresponding actions.
    """
    parser = argparse.ArgumentParser(
        description="OCI Shadowsocks Manager for automated proxy tunneling.",
        epilog="Use `python oci_shadowsocks.py <command> --help` for detailed command usage."
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start the OCI instance and local Shadowsocks client')
    start_parser.add_argument('--config', default='config.yaml', help='Path to the main configuration file.')

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the OCI instance and local Shadowsocks client')
    stop_parser.add_argument('--config', default='config.yaml', help='Path to the main configuration file.')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check the status of the OCI instance and local client')
    status_parser.add_argument('--config', default='config.yaml', help='Path to the main configuration file.')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a usage report')
    report_parser.add_argument('--config', default='config.yaml', help='Path to the main configuration file.')

    # Export Android command
    export_parser = subparsers.add_parser('export-android', help='Generate Android connection details (URL and QR code)')
    export_parser.add_argument('--config', default='config.yaml', help='Path to the main configuration file.')

    args = parser.parse_args()

    # Load configuration
    config_parser = ConfigParser(args.config)
    try:
        config = config_parser.load_config()
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Initialize managers
    oci_manager = OCIManager(config)
    local_client_manager = LocalClientManager(config['shadowsocks'])
    usage_tracker = UsageTracker(config['monitoring'])

    if args.command == 'start':
        print("Starting OCI Shadowsocks instance and client...")
        instance, status_message = oci_manager.create_or_get_instance()
        if instance:
            oci_manager.update_network_security_list()
            # Assuming configure_instance is part of the start process
            # oci_manager.configure_instance(instance) 
            local_client_manager.start_client()
            usage_tracker.log_start(instance['id'])
            print("Start command executed.")
    
    elif args.command == 'stop':
        print("Stopping OCI Shadowsocks instance and client...")
        oci_manager.stop_instance()
        local_client_manager.stop_client()
        usage_tracker.log_stop()
        print("Stop command executed.")
    
    elif args.command == 'status':
        print("Checking status...")
        instance_status, instance_message = oci_manager.get_instance_status()
        client_status, client_message = local_client_manager.get_client_status()
        print(f"OCI Instance Status: {instance_status} - {instance_message}")
        print(f"Local Client Status: {client_status} - {client_message}")
    
    elif args.command == 'report':
        print("Generating usage report...")
        report = usage_tracker.generate_report()
        print(report)

    elif args.command == 'export-android':
        print("Generating Android connection details...")
        ss_url, qr_filename = local_client_manager.generate_connection_details()
        print(f"Shadowsocks URL: {ss_url}")
        print(f"QR code saved to: {qr_filename}")
        print("Scan the QR code with your Android Shadowsocks client.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()