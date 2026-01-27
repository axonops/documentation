---
title: "Compatibility Matrix"
description: "AxonOps compatibility matrix. Supported versions of Cassandra, Kafka, and operating systems."
meta:
  - name: keywords
    content: "compatibility matrix, supported versions, Cassandra versions, Kafka versions"
---

# Compatibility Matrix

## AxonOps Server
| Operating Systems                                                           | Target Architecture |
|-----------------------------------------------------------------------------|---------------------|
| Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [10,11,12] | x86_64             |

## AxonOps GUI Server
| Operating Systems                                                           | Target Architecture |
|-----------------------------------------------------------------------------|---------------------|
| Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [10,11,12] | x86_64             |

## AxonOps Cassandra Agent
| System           | AxonOps Cassandra Agent Name    | Java Versions | Operating Systems                                                         | Target Architecture |
|------------------|---------------------------------|---------------|--------------------------------------------------------------------------|---------------------|
| Cassandra 3.0.x  | axon-cassandra3.0-agent         | Java 8        | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 3.11.x | axon-cassandra3.11-agent        | Java 8        | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 4.0.x  | axon-cassandra4.0-agent         | Java 11       | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 4.0.x  | axon-cassandra4.0-agent-jdk8    | Java 8        | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 4.1.x  | axon-cassandra4.1-agent         | Java 11       | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 4.1.x  | axon-cassandra4.1-agent-jdk8    | Java 8        | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Cassandra 5.0.x  | axon-cassandra5.0-agent-jdk11   | Java 11       | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |

## AxonOps Kafka Agent
| System        | AxonOps Kafka Agent Name | Java Versions | Operating Systems                                                         | Target Architecture |
|---------------|---------------------------|---------------|--------------------------------------------------------------------------|---------------------|
| Kafka 2.x     | axon-kafka2-agent         | Java 8/11     | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |
| Kafka 3.x     | axon-kafka3-agent         | Java 11       | Red Hat [7,8], CentOS [7,8], Ubuntu [18.04, 20.04, 22.04], Debian [11,12] | x86_64, arm64       |

## Java Versions

* [Oracle Java Standard Edition 8 ](https://www.java.com/en/download/manual.jsp)
* [Oracle Java Standard Edition 11 (Long Term Support)](https://www.oracle.com/java/technologies/downloads/)
* [OpenJDK 8](https://openjdk.org/install/)
* [OpenJDK 11](https://jdk.java.net/)
