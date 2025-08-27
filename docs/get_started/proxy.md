# AxonOps agent behind a proxy

If your network does not have direct internet access and it requires a proxy to connect to the AxonOps Server, you will need to configure the AxonOps agent to use it.

To configure the AxonOps agent to use a proxy, you can use a `systemd` override. This is the recommended approach as it keeps your configuration separate from the agent's default service file.

1.  Create an override file for the `axon-agent` service:

    ```bash
    sudo systemctl edit axon-agent.service
    ```

2.  This will open an editor with a blank file. Add the following content, replacing `your_proxy_server` and `port` with your proxy's details:

    ```ini
    [Service]
    Environment="https_proxy=http://your_proxy_server:port"
    Environment="http_proxy=http://your_proxy_server:port"
    Environment="no_proxy=localhost,127.0.0.1"
    ```

    If your proxy requires authentication, use the following format:

    ```ini
    [Service]
    Environment="https_proxy=http://user:password@your_proxy_server:port"
    Environment="http_proxy=http://user:password@your_proxy_server:port"
    Environment="no_proxy=localhost,127.0.0.1"
    ```

3.  Save the file and exit the editor. `systemd` will automatically reload the configuration.

4.  Restart the `axon-agent` to apply the changes:

    ```bash
    sudo systemctl restart axon-agent
    ```

5.  You can verify that the environment variables have been applied by checking the service's status:

    ```bash
    systemctl status axon-agent
    ```
