services=(
  axon-dash-pdf
  axon-dash
  axon-server
  axon-agent
  axon-cassandra3.0-agent
  axon-cassandra3.11-agent
  axon-cassandra4.0-agent
  axon-cassandra4.0-agent-jdk8
  axon-cassandra4.1-agent
  axon-cassandra4.1-agent-jdk8
  axon-cassandra5.0-agent-jdk11
  axon-cassandra5.0-agent-jdk17
)
for service in "${services[@]}"; do
  # downloads all direct dependencies, including target package
  dnf5 download \
    --arch x86_64 \
    --resolve \
    --alldeps \
    --refresh \
    --destdir=/tmp/downloads \
    "${service}"

  # downloads all dependencies, recursively
  dnf5 download \
    --arch x86_64 \
    --resolve \
    --alldeps \
    --refresh \
    --destdir=/tmp/downloads \
    $(dnf5 repoquery \
      --arch x86_64 \
      --recursive \
      --providers-of=requires \
      --qf '%{name}-%{version}-%{release}.%{arch} ' \
      "${service}" \
    | sort -u)
done

# create and compress repomd repository
createrepo_c /tmp/downloads
tar -C /tmp -czf "/tmp/axonops_repo_x86_64.rpm.tgz" /tmp/downloads/
