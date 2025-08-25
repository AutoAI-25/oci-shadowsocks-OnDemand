To test the Local Client Manager Module, which is responsible for managing the local Shadowsocks client on macOS, the following test cases are designed to verify its functionality, reliability, and security.

### **1. Functional Test Cases**

These tests ensure the module performs its intended actions correctly.

* **Test Case ID:** TC-LCM-001
    * **Description:** Verify the `start_client()` method successfully launches the `ss-local` process.
    * **Pre-conditions:** `shadowsocks-libev` is installed via Homebrew. The OCI instance is running, and its connection details are available.
    * **Test Steps:**
        1.  Call the `start_client()` method with valid configuration parameters.
        2.  Check for the existence of the `ss-local` process using `ps` or a similar command.
    * **Expected Result:** The `ss-local` process is running with the correct configuration parameters.

* **Test Case ID:** TC-LCM-002
    * **Description:** Verify the `stop_client()` method gracefully terminates the `ss-local` process.
    * **Pre-conditions:** The `ss-local` process is currently running.
    * **Test Steps:**
        1.  Call the `stop_client()` method.
        2.  Check for the termination of the `ss-local` process.
    * **Expected Result:** The `ss-local` process is no longer running, and no zombie processes remain.

* **Test Case ID:** TC-LCM-003
    * **Description:** Validate that the `generate_pac_file()` method correctly creates a PAC file based on the routing rules.
    * **Pre-conditions:** A `routing_rules.yaml` file exists with defined proxy and direct domains.
    * **Test Steps:**
        1.  Call the `generate_pac_file()` method.
        2.  Examine the generated PAC file (`proxy.pac`).
    * **Expected Result:** The PAC file is created at the specified path and contains JavaScript logic that routes traffic for proxy domains through `SOCKS5 127.0.0.1:1080` and other traffic as `DIRECT`.

* **Test Case ID:** TC-LCM-004
    * **Description:** Verify the `generate_connection_details()` method produces a valid Shadowsocks URL and a QR code.
    * **Pre-conditions:** The system has the necessary server connection details (server IP, port, password, method).
    * **Test Steps:**
        1.  Call the `generate_connection_details()` method.
        2.  Check the format of the generated URL.
        3.  Verify the generated QR code image file exists and is scannable.
    * **Expected Result:** The output includes a string in the `ss://...` format and a valid, scannable QR code image is generated.

---

### **2. Non-Functional Test Cases**

These tests focus on reliability, performance, and security.

* **Test Case ID:** TC-LCM-005
    * **Description:** Ensure the system handles a failure to start the client gracefully.
    * **Pre-conditions:** The `shadowsocks-libev` executable is not in the system's PATH.
    * **Test Steps:**
        1.  Call the `start_client()` method.
    * **Expected Result:** The method raises an informative exception or returns an error status. The error message should clearly state that the client executable was not found.

* **Test Case ID:** TC-LCM-006
    * **Description:** Verify graceful handling of network interruptions during a connection.
    * **Pre-conditions:** The proxy client is connected to the OCI instance.
    * **Test Steps:**
        1.  Simulate a network interruption (e.g., unplug network cable, disable Wi-Fi).
        2.  Monitor the client's status.
    * **Expected Result:** The client module gracefully handles the interruption with automatic retry mechanisms. It should not crash or enter an unrecoverable state.

* **Test Case ID:** TC-LCM-007
    * **Description:** Test the `test-connection` command to verify end-to-end proxy functionality.
    * **Pre-conditions:** The `ss-local` client is running and configured to connect to the OCI instance.
    * **Test Steps:**
        1.  Call the `test-connection` command with a known domain that requires the proxy (e.g., `api.openai.com`).
    * **Expected Result:** The command reports a successful connection through the proxy.

---

### **3. Routing and Configuration Test Cases**

These tests ensure the module correctly applies and reloads routing rules.

* **Test Case ID:** TC-LCM-008
    * **Description:** Verify that the selective routing correctly directs traffic for AI services through the proxy.
    * **Pre-conditions:** The `routing_rules.yaml` file is configured with domains like `*.openai.com` and `*.anthropic.com`.
    * **Test Steps:**
        1.  Start the client with selective routing mode enabled.
        2.  Use a command-line tool (e.g., `curl`) to send a request to a proxy-listed domain (e.g., `https://api.openai.com`).
        3.  Verify the request is routed through the proxy.
    * **Expected Result:** The request is successfully completed via the proxy tunnel.

* **Test Case ID:** TC-LCM-009
    * **Description:** Verify that traffic to domains not in the proxy list is routed directly.
    * **Pre-conditions:** The `routing_rules.yaml` file is configured with the `default_action: "direct"`.
    * **Test Steps:**
        1.  Use a command-line tool to send a request to a domain not on the proxy list (e.g., `https://www.google.com`).
        2.  Verify the request bypasses the proxy.
    * **Expected Result:** The request is completed via a direct connection.

* **Test Case ID:** TC-LCM-010
    * **Description:** Verify the `update-rules` command correctly reloads the routing rules without restarting the client.
    * **Pre-conditions:** The `ss-local` client is running in selective routing mode.
    * **Test Steps:**
        1.  Add a new domain to the `proxy_domains` section in `routing_rules.yaml`.
        2.  Run the `update-rules` command.
        3.  Test a connection to the newly added domain.
    * **Expected Result:** The new domain is successfully routed through the proxy, demonstrating that the rules were reloaded successfully.