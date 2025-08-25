### **1. Introduction**

The OCI Shadowsocks Manager is a Python-based automation tool designed to create and manage secure Shadowsocks proxy tunnels using Oracle Cloud Infrastructure's (OCI) Always Free Tier. The system automates the entire lifecycle of a Shadowsocks server instance, from provisioning and configuration to secure access management and automatic shutdown. It prioritizes cost-effectiveness by leveraging OCI's generous Always Free resources while maintaining a strong security posture through IP-restricted access controls.

The system's primary goal is to provide a reliable, automated solution for secure AI traffic tunneling, simplifying a complex setup process for end-users.

---

### **2. Architecture and High-Level Design**

The software will employ a layered, modular architecture. The core logic will be decoupled from the user interface and external APIs, ensuring flexibility and maintainability.

**Core Components:**

* **Command Line Interface (CLI):** The user's primary interface. It will parse commands (e.g., `start`, `stop`, `status`) and pass them to the main controller.
* **Main Controller:** The orchestrator that coordinates all operations. It will manage the flow of the application, calling methods from the service modules as needed.
* **Service Modules:** These are the key functional units. Each module will be responsible for a specific domain:
    * **OCI Manager:** Interacts with the OCI Python SDK to manage compute instances and network resources.
    * **Configuration Manager:** Handles parsing and validating YAML configuration files.
    * **Local Client Manager:** Manages the local Shadowsocks client on the user's machine (primarily macOS).
    * **Monitoring & Reporting:** Tracks usage and generates reports.
* **External APIs/Libraries:** The system will use the OCI Python SDK for all OCI interactions and other libraries (e.g., `requests`, `PyYAML`, `qrcode`) for their specific functions.

---

### **3. Detailed Component Design**

#### **3.1 OCI Manager Module**

This module will be a Python class (`OCIManager`) that encapsulates all OCI-related logic.

* **Initialization (`__init__`):** Takes OCI configuration details (user, tenancy, compartment, region, key file) and initializes the OCI SDK clients for `Compute`, `Networking`, and `Identity` services.
* **`create_or_get_instance()`:** This method will first check for an existing instance with the 'shadowsocks-proxy' tag. If one is found, it will be reused. If not, it will create a new instance, prioritizing `VM.Standard.E2.1.Micro` and falling back to `VM.Standard.A1.Flex` if the former is unavailable.
* **`start_instance()`:** Sends an API call to start a stopped instance.
* **`stop_instance()`:** Sends an API call to stop a running instance. This will also be the method called by the automatic shutdown timer.
* **`configure_instance()`:** Uses `paramiko` (or a similar SSH library) to connect to the new instance and execute a setup script. This script will install `shadowsocks-libev` and configure the server with the correct port, password, and encryption method from the configuration file.
* **`update_network_security_list()`:** This is a crucial method for security. It will first determine the user's current public IP address by querying an external service. It will then identify the Network Security List (NSL) associated with the Shadowsocks instance and update its ingress rules to allow traffic only from that specific IP on the configured Shadowsocks port. It will also revoke any old IP rules to maintain the principle of least privilege.

#### **3.2 Local Client Manager Module**

This module will be a class (`LocalClientManager`) designed to interact with the local operating system, specifically macOS.

* **`start_client()`:** This method will execute the `ss-local` command line utility, reading the server parameters (IP, port, password, method) from the OCI Manager and the local port from the configuration file.
* **`configure_routing()`:** This method will read the `routing_rules.yaml` file to determine which domains and IPs should be routed through the proxy.
* **`generate_pac_file()`:** This method will create a Proxy Auto-Configuration (PAC) file based on the routing rules, enabling browser-specific selective proxying.
* **`generate_connection_details()`:** This method will create a Shadowsocks URL (`ss://`) and a QR code, which will be displayed to the user for easy setup on other devices.

#### **3.3 Configuration and Data Management**

* **`ConfigParser` Class:** A dedicated class will handle all configuration file operations. It will use the `PyYAML` library to read and write configuration data. It will also validate the configuration on startup to ensure all required fields are present and correctly formatted.
* **`UsageTracker` Class:** This class will manage usage data. It will have methods to log `start_time`, `stop_time`, and other metrics. The data will be persisted locally in a JSON file to enable reporting even after the application exits.

---

### **4. Command Line Interface (CLI)**

The CLI will be implemented using Python's `argparse` module to provide a user-friendly interface with clear commands and flags.

| **Command** | **Description** | **Functionality** |
| :--- | :--- | :--- |
| `start` | Start instance and proxy client | `OCIManager.create_or_get_instance()`, `OCIManager.update_network_security_list()`, `LocalClientManager.start_client()` |
| `stop` | Stop instance and proxy client | `OCIManager.stop_instance()`, `LocalClientManager.stop_client()` |
| `status` | Check instance and client status | `OCIManager.get_instance_status()`, `LocalClientManager.get_client_status()` |
| `report` | Generate usage report | `UsageTracker.generate_report()` |
| `export-android` | Generate Android details & QR code | `LocalClientManager.generate_connection_details()` |
| `test-connection` | Test proxy connectivity | A method that attempts a connection through the proxy. |

---

### **5. Security Considerations**

Security is paramount in the design.

* **IP-Based Access:** All traffic to the OCI instance will be strictly limited to the user's public IP address via the Network Security Lists.
* **Encrypted Tunneling:** All network communications will be secured using the Shadowsocks protocol with a strong encryption method.
* **Secure Credentials:** OCI API keys will be managed and stored securely in the user's `.oci` directory, and the system will support OCI Vault integration for sensitive data.
* **File Permissions:** Private keys for SSH access will have restricted file permissions (`400`) to prevent unauthorized access.