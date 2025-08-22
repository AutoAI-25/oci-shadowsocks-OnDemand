# Oracle Cloud Shadowsocks Server ☁️

A project to build an automated, on-demand Shadowsocks server using Oracle Cloud Infrastructure's Always Free tier.

This guide provides a detailed plan for provisioning a compute instance, installing the Shadowsocks server, and automating its lifecycle to stay within the free tier limits.

***

### Phase 1: Automated OCI Setup and Shadowsocks Installation

The goal is to create a script that will provision the OCI compute instance and install all the necessary software automatically.

#### 1. Pre-Script Setup

* **Install OCI CLI**: Install the Oracle Cloud Infrastructure Command Line Interface on your Mac.
* **Configure Credentials**: Run `oci setup config` in your Terminal to set up your API signing key and provide your User OCID, Tenancy OCID, and region.
* **IAM Permissions**: Ensure your OCI user has the necessary permissions to create compute instances, key pairs, and security lists.

#### 2. The Automation Script

You will create a script that performs the following actions:

* **Create API Key Pair**: The script will generate a new API signing key pair for authentication.
* **Create Security List**: The script will create a new security list (the OCI equivalent of a security group) and add ingress rules for SSH and your chosen Shadowsocks port.
* **Launch Compute Instance with User Data**: The script will launch a compute instance. Using the **`--user-data`** flag, it will pass an embedded shell script that runs automatically on first boot. This embedded script will:
    * Update the system's package list.
    * Install the Shadowsocks server package.
    * Configure the Shadowsocks server with a strong password and encryption method.
    * Enable and start the Shadowsocks service.

***

### Phase 2: Server Automation and Security

This phase addresses the on-demand and security requirements.

1.  **Automated Shutdown with Timeout**: Use **Oracle Cloud Monitoring** to create an alarm based on resource metrics. Configure a rule to automatically stop the instance when it has been idle for a specified period (e.g., 60 minutes) to save free tier hours.
2.  **Security Best Practices**: Ensure your API key pair is kept private. Use a very strong, randomly generated password for your Shadowsocks server. Only allow SSH access from your own IP address within the security list rules.