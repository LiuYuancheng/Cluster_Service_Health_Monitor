## Use Case Example

The **Cluster Service Health Monitor** has been successfully deployed on the NCL **AS-06 cluster (COM1-AS06)** to demonstrate its capability in monitoring a mid-sized cyber exercise environment. In this deployment, the system monitors a total of **17 nodes** and **71 services** across multiple critical infrastructure components.

### Monitored Cluster Overview

The monitored targets and services are summarized below:

| Probed Target Service Cluster | Node Number | Services Checked                                             |
| ----------------------------- | ----------- | ------------------------------------------------------------ |
| Firewall                      | 1           | icmp, ssh, http-alt, http-proxy, ident, blackice-icecap, http, https |
| OpenStack                     | 4           | icmp, ssh, http-alt, upnp, mysql, https, vnc                 |
| KYPO-CRP                      | 3           | icmp, ssh, https, vnc, X11, X11:1-Win                        |
| CTF                           | 2           | icmp, ssh, http, vnc, X11, X11:1-Win                         |
| GPU                           | 3           | icmp, ssh, vnc, nvidia-smi                                   |
| Support Services              | 4           | NTP, FTP, file system                                        |

This setup represents a realistic cyber range environment, including infrastructure services, training platforms, GPU computing nodes, and supporting services.

------

### System Workflow Description

As illustrated in the architecture diagram, the system operates through a distributed probing and centralized monitoring approach:

1. **Prober Agent Deployment**
    A Prober Agent is deployed within the AS-06 cluster environment. It acts as the central orchestrator for executing various probing tasks across different nodes and services.

2. **Multi-Type Probing Execution**
    The Prober Agent schedules and executes multiple specialized probers, including:

   - **Support Prober** (NTP, FTP, file system monitoring via jump host)
   - **OpenStack Prober** (cloud infrastructure services)
   - **KYPO Prober** (cyber range platform services)
   - **Firewall (FW) Prober** (network security device monitoring)
   - **GPU Prober** (GPU node status via NVIDIA-SMI)
   - **CTF Prober** (capture-the-flag platform services)

   These probers perform both:

   - **Local checks** (e.g., file system, process state on YC desktop)
   - **Remote checks** (e.g., service availability via network protocols such as ICMP, SSH, HTTP, VNC)

3. Data Collection and Communication

   - Monitoring data is collected and temporarily stored by the Prober Agent
   - Data is transmitted to the **Monitor Hub** via HTTPS (reporting)
   - Additional data fetching can be performed via UDP for lightweight communication

4. Centralized Processing and Storage

   - The **Communication Module** forwards incoming data to the Monitor Hub
   - Raw monitoring data is stored in the **Raw Database (SQLite)**
   - The **Data Manager** processes the data and forwards it to the scoring engine
   - Processed results and health scores are stored in the **Score Database (InfluxDB)**

5. Visualization and User Interaction

   - Grafana Dashboards

      provide real-time visualization of:

     - Service availability
     - Resource health status
     - Network topology
     - Exercise scoring metrics

   - Users access dashboards via a web browser for monitoring and decision-making

------

### Key Observations and Benefits

This deployment demonstrates several important capabilities of the system:

- **Comprehensive Coverage**: Ability to monitor diverse services across infrastructure, platforms, and applications
- **Real-Time Visibility**: Continuous updates on service health and system state
- **Low Deployment Overhead**: Minimal changes required to existing network configurations
- **Flexible Probing Architecture**: Support for both internal and external monitoring strategies
- **Actionable Insights**: Enables teams to quickly detect issues, assess attack impacts, and respond effectively