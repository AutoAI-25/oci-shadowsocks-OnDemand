# This file contains a comprehensive set of pytest tests for the Local Client Manager module.
# It uses unittest.mock to simulate external dependencies like the command line and file system,
# ensuring the tests are isolated and reliable.

import pytest
import unittest.mock as mock
import json
import os
import yaml

# Import the actual LocalClientManager class from the source module.
from src.local_client_manager import LocalClientManager

# --- Pytest Test Suite ---

@pytest.fixture
def mock_config():
    """Provides a reusable mock configuration object for tests."""
    return {
        'server_ip': '1.2.3.4',
        'server_port': 8388,
        'local_port': 1080,
        'password': 'test_password',
        'method': 'aes-256-gcm'
    }

@pytest.fixture
def local_client_manager(mock_config):
    """Creates a LocalClientManager instance for each test."""
    return LocalClientManager(mock_config)

@mock.patch('subprocess.Popen')
def test_start_client_success(mock_subprocess_popen, local_client_manager):
    """TC-LCM-001: Verifies the client starts successfully."""
    mock_popen_instance = mock.MagicMock()
    mock_subprocess_popen.return_value = mock_popen_instance
    
    success, message = local_client_manager.start_client()
    
    assert success is True
    assert "started successfully" in message
    mock_subprocess_popen.assert_called_once()
    assert mock_subprocess_popen.call_args[0][0][0] == 'ss-local'

@mock.patch('subprocess.Popen')
@mock.patch('os.remove')
@mock.patch('os.path.exists', return_value=True)
def test_stop_client_success(mock_exists, mock_remove, mock_subprocess_popen, local_client_manager):
    """TC-LCM-002: Verifies the client stops successfully."""
    # Mock a running process
    local_client_manager.client_process = mock.MagicMock()
    local_client_manager.client_process.poll.return_value = None
    
    success, message = local_client_manager.stop_client()
    
    assert success is True
    assert "stopped successfully" in message
    local_client_manager.client_process.terminate.assert_called_once()
    local_client_manager.client_process.wait.assert_called_once_with(timeout=5)
    mock_remove.assert_called_once_with(local_client_manager.client_config_path)

@mock.patch('subprocess.Popen')
def test_stop_client_not_running(mock_subprocess_popen, local_client_manager):
    """Verifies that the stop method handles a non-running client gracefully."""
    local_client_manager.client_process = None
    
    success, message = local_client_manager.stop_client()
    
    assert success is False
    assert "Client is not running." in message

@mock.patch('os.path.exists', return_value=True)
@mock.patch('builtins.open', new_callable=mock.mock_open, read_data="""
proxy_domains:
  - "*.openai.com"
  - "*.anthropic.com"
default_action: "DIRECT"
""")
def test_generate_pac_file_success(mock_open, mock_exists, local_client_manager):
    """TC-LCM-003: Validates correct PAC file generation."""
    rules_file = "config/routing_rules.yaml"
    output_file = "proxy.pac"
    
    success = local_client_manager.generate_pac_file(rules_file, output_file)
    assert success is True
    
    # Verify the file was written with the expected content
    mock_open.assert_called_with(output_file, 'w')
    handle = mock_open()
    written_content = handle.write.call_args[0][0]
    
    assert "function FindProxyForURL" in written_content
    assert '"*.openai.com"' in written_content
    assert '"DIRECT"' in written_content
    
@mock.patch('qrcode.make')
def test_generate_connection_details_success(mock_qrcode_make, local_client_manager, mock_config):
    """TC-LCM-004: Verifies Shadowsocks URL and QR code are generated."""
    mock_qr_img = mock.MagicMock()
    mock_qrcode_make.return_value = mock_qr_img
    
    url, filename = local_client_manager.generate_connection_details()
    
    assert url.startswith('ss://')
    assert filename == "shadowsocks_qrcode.png"
    mock_qrcode_make.assert_called_once()
    mock_qr_img.save.assert_called_once_with(filename)
    
@mock.patch('subprocess.Popen')
def test_start_client_not_found(mock_subprocess_popen, local_client_manager):
    """TC-LCM-005: Ensures graceful handling when ss-local is not found."""
    mock_subprocess_popen.side_effect = FileNotFoundError
    
    success, message = local_client_manager.start_client()
    
    assert success is False
    assert "not found" in message
    mock_subprocess_popen.assert_called_once()

@mock.patch('requests.get')
def test_test_connection_success(mock_requests_get, local_client_manager):
    """TC-LCM-007: Verifies end-to-end proxy connectivity."""
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    url_to_test = "https://api.openai.com"
    success, message = local_client_manager.test_connection(url_to_test)

    assert success is True
    assert "Connection successful" in message
    mock_requests_get.assert_called_once()
    
    # Assert that the request used the proxy
    assert 'proxies' in mock_requests_get.call_args[1]
    proxies = mock_requests_get.call_args[1]['proxies']
    assert proxies['https'] == 'socks5h://127.0.0.1:1080'

