# OCI Shadowsocks Manager

The OCI Shadowsocks Manager is a Python-based automation tool designed to create and manage secure Shadowsocks proxy tunnels using Oracle Cloud Infrastructure's (OCI) Always Free Tier. The system automates the entire lifecycle of a Shadowsocks server instance, from provisioning and configuration to secure access management and automatic shutdown.

### Features
* **Automated OCI Instance Management:** Automatically creates and manages Always Free eligible compute instances (VM.Standard.E2.1.Micro and VM.Standard.A1.Flex).
* **Dynamic Network Security:** Automatically updates Network Security Lists to restrict access to your current public IP address, enhancing security.
* **Local Client Control:** Manages the local Shadowsocks client on macOS, including starting, stopping, and selective routing.
* **Multi-Device Support:** Generates Shadowsocks URLs and QR codes for easy setup on other devices, such as Android phones.
* **Usage Tracking:** Monitors and reports on instance usage to help you stay within OCI's Always Free Tier limits.
* **Command-Line Interface:** Provides a simple and powerful CLI for all management tasks.

### Installation
1.  **Clone the repository:**
    ```
    git clone [https://github.com/your-username/oci-shadowsocks-manager.git](https://github.com/your-username/oci-shadowsocks-manager.git)
    cd oci-shadowsocks-manager
    ```
2.  **Install Python dependencies:**
    ```
    pip3 install -r requirements.txt
    ```
3.  **Install the Shadowsocks client:**
    - On macOS, install `shadowsocks-libev` via Homebrew: `brew install shadowsocks-libev`
4.  **Configure OCI:** Follow the official OCI SDK documentation to set up your API key and configuration file (`~/.oci/config`).

### Usage
The primary way to interact with the system is through the `oci_shadowsocks.py` script.

* **Start the instance and client:**
    ```
    python3 oci_shadowsocks.py start --config config.yaml
    ```
* **Stop the instance and client:**
    ```
    python3 oci_shadowsocks.py stop --config config.yaml
    ```
* **Check the status:**
    ```
    python3 oci_shadowsocks.py status --config config.yaml
    ```
* **Generate Android QR code:**
    ```
    python3 oci_shadowsocks.py export-android --config config.yaml
    ```
* **Generate a usage report:**
    ```
    python3 oci_shadowsocks.py report --config config.yaml
    ```

### Configuration
The system uses a `config.yaml` file for all settings. A template is provided in the repository.

### Contributing
We welcome contributions! Please feel free to open an issue or submit a pull request.

### License
This project is licensed under the MIT License.