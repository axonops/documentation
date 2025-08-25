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
  arch=x86_64
  if [[ $service == axon-cassandra* ]]; then
    arch=noarch
  fi
  # downloads all direct dependencies, including target package
  dnf5 download \
    --arch "${arch}" \
    --resolve \
    --alldeps \
    --refresh \
    --destdir=/tmp/downloads \
    "${service}"

  # downloads all dependencies, recursively
  DEPENDENCIES=$(dnf5 repoquery \
    --arch "${arch}" \
    --recursive \
    --providers-of=requires \
    --qf '%{name}-%{version}-%{release}.%{arch} ' \
    "${service}" | sort -u)
  if [[ -n $DEPENDENCIES ]]; then
    dnf5 download \
      --arch "${arch}" \
      --resolve \
      --alldeps \
      --refresh \
      --destdir=/tmp/downloads \
      $DEPENDENCIES
  fi
done

# create and compress repomd repository
cd /tmp/downloads
createrepo_c .
tar \
  -czf /tmp/axonops-x86_64.rpm.tgz \
  .
