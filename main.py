import argparse
import sys
import yaml
import os
import time

# Import service modules from the src/ directory
from src.local_client_manager import LocalClientManager
from src.oci_manager import OCIManager  
from src.config_parser import ConfigParser  
from src.usage_tracker import UsageTracker  

# --- Main Application Logic ---

def main():
    parser = argparse.ArgumentParser(description="OCI Shadowsocks Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start OCI instance and provide connection details')

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop OCI instance')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check OCI instance status')

    # Export Android details command
    export_android_parser = subparsers.add_parser('export-android', help='Generate Android connection details and QR code')

    # Test connection command
    test_connection_parser = subparsers.add_parser('test-connection', help='Test proxy connectivity')
    test_connection_parser.add_argument('url', nargs='?', default='https://api.openai.com', help='URL to test the proxy connection against')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate usage report')

    args = parser.parse_args()

    # Load configuration
    config_parser = ConfigParser()
    success, message = config_parser.load_config()
    if not success:
        print(message)
        sys.exit(1)

    oci_manager = OCIManager(config_parser.config)
    local_client_manager = LocalClientManager(config_parser.config.get('shadowsocks', {}))
    usage_tracker = UsageTracker()
    
    # Process commands
    if args.command == 'start':
        print("Starting OCI Shadowsocks Manager...")
        server_details = oci_manager.create_or_get_instance()
        oci_manager.update_network_security_list(server_details['server_ip'], config_parser.config['shadowsocks']['server_port'])
        
        # Now, generate connection details for the user to manually enter into ShadowsocksX-NG
        print("\nOCI instance is provisioned and secure.")
        print("Please use the following details to configure your ShadowsocksX-NG client:")
        ss_url, qr_file = local_client_manager.generate_connection_details()
        print(f"\nShadowsocks URL: {ss_url}")
        print(f"A QR code for mobile setup has been saved to: {qr_file}")
        print("\nNote: The local Shadowsocks client (ShadowsocksX-NG) is a GUI application that you must start manually.")

    elif args.command == 'stop':
        success, message = oci_manager.stop_instance()
        if success:
            print(f"Stop command successful: {message}")
        else:
            print(f"Stop command failed: {message}")

    elif args.command == 'status':
        status = oci_manager.get_instance_status()
        print(f"OCI instance status: {status}")

    elif args.command == 'export-android':
        ss_url, qr_file = local_client_manager.generate_connection_details()
        print("Android Connection Details:")
        print(f"Shadowsocks URL: {ss_url}")
        print(f"QR code saved to: {qr_file}")

    elif args.command == 'test-connection':
        success, message = local_client_manager.test_connection(args.url)
        print(message)
        
    elif args.command == 'report':
        report = usage_tracker.generate_report()
        print(report)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()