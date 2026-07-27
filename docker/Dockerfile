# Build environment for the FriendlyELEC H3 Android 4.4 BSP.
# The 2015-era build system wants Ubuntu 14.04, but Canonical purged trusty
# from old-releases.ubuntu.com (verified 2026-07: only precise and older
# remain). Debian NEVER deletes its archive, so the same-era Debian wheezy
# (2013: make 3.81 native, gcc 4.7, i386 multiarch) from archive.debian.org
# is the durable equivalent. The Allwinner pack tools are 32-bit i386
# binaries (x86_64 hosts only).
FROM --platform=linux/amd64 debian/eol:wheezy

ENV DEBIAN_FRONTEND=noninteractive

# debian/eol ships a working archive.debian.org sources.list (incl. the
# security suite the base packages come from) - do not overwrite it, or the
# i386 multiarch versions can no longer match the installed amd64 ones
RUN echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99archive \
 && dpkg --add-architecture i386 \
 && apt-get update \
 && apt-get install -y --force-yes --no-install-recommends \
      build-essential gcc-multilib g++-multilib libc6-dev-i386 \
      libc6:i386 libstdc++6:i386 zlib1g:i386 libncurses5:i386 \
      lib32z1-dev lib32ncurses5-dev \
      git ca-certificates curl wget \
      python python-dev \
      bison flex gperf bc cpio rsync fakeroot gawk \
      zip unzip xz-utils lzop \
      libxml2-utils xsltproc \
      libncurses5-dev libreadline6-dev libssl-dev \
      libx11-dev libgl1-mesa-dev x11proto-core-dev \
      u-boot-tools dosfstools mtools \
      ccache \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Oracle JDK 1.6.0_45, required by the Android 4.4 build system.
# trusty's CA store cannot validate the mirror's modern certificate chain,
# so integrity relies on the pinned sha256 instead of TLS.
ENV JDK6_URL=https://repo.huaweicloud.com/java/jdk/6u45-b06/jdk-6u45-linux-x64.bin \
    JDK6_SHA256=6b493aeab16c940cae9e3d07ad2a5c5684fb49cf06c5d44c400c7993db0d12e8

RUN cd /opt \
 && wget -q --no-check-certificate -O jdk6.bin "$JDK6_URL" \
 && echo "$JDK6_SHA256  jdk6.bin" | sha256sum -c - \
 && sh jdk6.bin >/dev/null \
 && rm jdk6.bin \
 && mv jdk1.6.0_45 jdk6

ENV JAVA_HOME=/opt/jdk6
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /work
CMD ["/bin/bash"]
