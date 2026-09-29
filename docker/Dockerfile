FROM rockylinux:9

# Update system, enable CRB (needed by some EPEL packages) and install EPEL,
# then install required packages + some common tools for a bit of command
# line comfort. Combined into one layer so a later `create` always installs
# against packages from the same dnf update, rather than layering fresh
# installs on top of a stale cached "update" layer.
RUN dnf update -y && \
    dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y --allowerasing --setopt=install_weak_deps=False --setopt=tsflags=nodocs \
                   bash-completion vim git curl wget which tree htop sudo   \
                   gcc gcc-c++ autoconf automake bison make zip cmake      \
                   python3 python3-pip                                    \
                   bzip2 patch mesa-libGL-devel libffi-devel fontconfig-devel \
                   sqlite-devel bzip2-devel zlib-devel openssl-devel xz-devel \
                   readline-devel ncurses-devel libuuid-devel git-lfs      \
                   findutils xz byacc ccache && \
    git lfs install --system && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Trust bind-mounted repos regardless of which user (root or builder) or host
# UID owns them, rather than a per-user config that only one of them sees.
RUN git config --system --add safe.directory '*'

# Configure ccache. CCACHE_MAXSIZE (not `ccache -M`) because /ccache is a
# volume mount point at runtime - anything `ccache -M` writes to a config
# file under it during this build gets shadowed once the real volume is
# mounted, so the size cap only actually takes effect via the env var.
# 2G is generous: a full build (IfcParse+IfcGeom+IfcConvert+wrapper, one
# Python version) measures ~300MB, and the volume is now shared across all
# checkouts (see compose.yaml), so this covers several diverging branches.
ENV CCACHE_DIR=/ccache
ENV CCACHE_MAXSIZE=2G
ENV PATH="/usr/lib/ccache:$PATH"

# Non-root user matching the host UID/GID that bind-mounts the repo (default
# 1000:1000, the common single-user-Linux-box case), so files the build
# creates under the mount keep sane, non-root ownership on the host side.
# Override with --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g)
# if your host user has a different UID/GID.
ARG USER_UID=1000
ARG USER_GID=1000
# groupadd fails outright if USER_GID is already taken by an existing
# system group - which happens whenever a host's primary GID collides with
# one baked into the rockylinux9 base image. The main real-world case is
# macOS, where the default user's primary group is "staff" at GID 20, and
# GID 20 is "games" on RHEL-family images. Only create the "builder" group
# when that GID is actually free; otherwise useradd just attaches to
# whichever group already owns it. Either way the builder user ends up
# with the right GID for bind-mount ownership, which is all that matters.
RUN (getent group "${USER_GID}" >/dev/null || groupadd -g "${USER_GID}" builder) \
    && useradd -m -u "${USER_UID}" -g "${USER_GID}" -s /bin/bash builder \
    && echo "builder ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/builder

# Copied while still root: /bin is not writable by the builder user.
COPY --from=ghcr.io/astral-sh/uv:0.11.27 /uv /uvx /bin/

USER builder
WORKDIR /__w/IfcOpenShell/IfcOpenShell

# Installed as builder so managed Python interpreters land under builder's
# $HOME, matching the user that actually runs the build.
RUN uv python install

CMD ["sleep", "infinity"]
