#!/bin/bash
set -euo pipefail
#####################################################################
# Author    : Erik Dubois
# Website   : https://kiroproject.be
#####################################################################
#
#   DO NOT JUST RUN THIS. EXAMINE AND JUDGE. RUN AT YOUR OWN RISK.
#
#   Purpose:
#   Refresh the VENDORED .pkg.tar.zst bootstrap packages bundled in
#   data/ — the keyring/mirrorlist packages ATT installs offline when
#   a user enables Chaotic-AUR or CachyOS, plus archlinux-keyring.
#   Each is re-downloaded from upstream, the real versioned filename is
#   derived from the package's own .PKGINFO, older copies in the folder
#   are pruned, and the new one is dropped in. It does NOT commit — run
#   up.sh afterwards to commit and push the refreshed files.
#
#   Why: these artifacts are dated snapshots (see CONFIG_SOURCES.md →
#   VENDORED). They go stale; a stale keyring means signature failures
#   and a stale mirrorlist means dead mirrors when a user bootstraps a
#   repo. This script is the manual refresh step — run it periodically,
#   not on every push (it hits upstream mirrors).
#
#####################################################################

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

#####################################################################
# Colors
#####################################################################
if command -v tput >/dev/null 2>&1 && [[ -t 1 ]]; then
    RED="$(tput setaf 1)"
    GREEN="$(tput setaf 2)"
    YELLOW="$(tput setaf 3)"
    BLUE="$(tput setaf 4)"
    CYAN="$(tput setaf 6)"
    RESET="$(tput sgr0)"
else
    RED="" GREEN="" YELLOW="" BLUE="" CYAN="" RESET=""
fi

#####################################################################
# Logging
#####################################################################
log_section() {
    echo
    echo "${GREEN}############################################################################${RESET}"
    echo "$1"
    echo "${GREEN}############################################################################${RESET}"
    echo
}

log_info() {
    echo
    echo "${BLUE}############################################################################${RESET}"
    echo "$1"
    echo "${BLUE}############################################################################${RESET}"
    echo
}

log_warn() {
    echo
    echo "${YELLOW}############################################################################${RESET}"
    echo "$1"
    echo "${YELLOW}############################################################################${RESET}"
    echo
}

log_error() {
    echo
    echo "${RED}############################################################################${RESET}"
    echo "$1"
    echo "${RED}############################################################################${RESET}"
    echo
}

log_success() {
    echo
    echo "${GREEN}############################################################################${RESET}"
    echo "$1"
    echo "${GREEN}############################################################################${RESET}"
    echo
}

#####################################################################
# Error handling
#####################################################################
on_error() {
    local lineno="$1"
    local cmd="$2"
    echo
    echo "${RED}ERROR on line ${lineno}: ${cmd}${RESET}"
    echo
    sleep 10
}

trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

#####################################################################
# Config
#####################################################################
DATA_DIR="${SCRIPT_DIR}/usr/share/archlinux-tweak-tool/data"
FAILED=0

# Upstream endpoints. These are the ONE thing to sanity-check if a refresh
# starts failing — verify them against the projects' current install docs:
#   - Arch:    https://archlinux.org/packages/core/any/archlinux-keyring/
#   - Chaotic: https://aur.chaotic.cx/  (cdn-mirror serves fixed package names)
#   - CachyOS: https://wiki.cachyos.org/ (mirror dir is browsable; no fixed name,
#              so the latest is resolved from the directory index below)
ARCH_KEYRING_URL="https://archlinux.org/packages/core/any/archlinux-keyring/download/"
CHAOTIC_KEYRING_URL="https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst"
CHAOTIC_MIRRORLIST_URL="https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst"
CACHYOS_REPO_INDEX="https://mirror.cachyos.org/repo/x86_64/cachyos/"

#####################################################################
# Functions
#####################################################################
require_tools() {
    local tool missing=0
    for tool in curl bsdtar; do
        if ! command -v "${tool}" >/dev/null 2>&1; then
            log_error "Required tool not found: ${tool}"
            missing=1
        fi
    done
    [[ "${missing}" -eq 0 ]] || exit 1
}

# Resolve the latest "<pkg>-<ver>-any.pkg.tar.zst" filename from a browsable
# repo directory index (CachyOS has no fixed-name bootstrap URL).
resolve_from_index() {
    local pkgname="$1" index="$2" file
    file="$(curl -fsSL "${index}" \
        | grep -oE "${pkgname}-[0-9][^\"]*-any\.pkg\.tar\.zst" \
        | sort -V | tail -1)" || true
    [[ -n "${file}" ]] || return 1
    echo "${index}${file}"
}

# refresh <pkgname> <dest-subdir-under-data> <url>
# Downloads, validates it is a real package, derives the versioned filename
# from .PKGINFO, prunes older copies, and installs the new one. Returns
# non-zero on any failure so main() can keep going and report at the end.
refresh() {
    local pkgname="$1" subdir="$2" url="$3"
    local dest="${DATA_DIR}/${subdir}"
    local tmp pkgver arch final

    if [[ -z "${url}" ]]; then
        log_error "${pkgname}: no URL resolved — skipping"
        return 1
    fi

    log_info "Refreshing ${pkgname}"
    echo "  source: ${url}"
    echo "  dest  : ${dest}"

    mkdir -p "${dest}"
    tmp="$(mktemp --suffix=.pkg.tar.zst)"

    if ! curl -fSL --retry 3 --connect-timeout 15 -o "${tmp}" "${url}"; then
        log_error "${pkgname}: download failed"
        rm -f "${tmp}"
        return 1
    fi

    # A 404/HTML error page would download fine but is not a package — the
    # .PKGINFO read below is what actually validates the content.
    pkgver="$(bsdtar -xOf "${tmp}" .PKGINFO 2>/dev/null | awk -F' = ' '/^pkgver/{print $2; exit}')"
    arch="$(bsdtar -xOf "${tmp}" .PKGINFO 2>/dev/null | awk -F' = ' '/^arch/{print $2; exit}')"
    if [[ -z "${pkgver}" || -z "${arch}" ]]; then
        log_error "${pkgname}: downloaded file is not a valid package (no .PKGINFO)"
        rm -f "${tmp}"
        return 1
    fi

    final="${pkgname}-${pkgver}-${arch}.pkg.tar.zst"

    if [[ -f "${dest}/${final}" ]]; then
        log_success "${pkgname} already current: ${final}"
        rm -f "${tmp}"
        return 0
    fi

    find "${dest}" -maxdepth 1 -type f -name "${pkgname}-*.pkg.tar.zst" -delete
    mv "${tmp}" "${dest}/${final}"
    chmod 644 "${dest}/${final}"
    log_success "${pkgname} refreshed → ${final}"
}

#####################################################################
# Main
#####################################################################
main() {
    log_section "Vendored package refresh"
    require_tools

    if [[ ! -d "${DATA_DIR}" ]]; then
        log_error "data dir not found: ${DATA_DIR} — run from the ATT repo root"
        exit 1
    fi

    refresh archlinux-keyring  "packages/keyring"    "${ARCH_KEYRING_URL}"        || FAILED=$((FAILED + 1))
    refresh chaotic-keyring    "chaotic/keyring"     "${CHAOTIC_KEYRING_URL}"     || FAILED=$((FAILED + 1))
    refresh chaotic-mirrorlist "chaotic/mirrorlist"  "${CHAOTIC_MIRRORLIST_URL}"  || FAILED=$((FAILED + 1))

    log_info "Resolving latest CachyOS packages from ${CACHYOS_REPO_INDEX}"
    refresh cachyos-keyring    "cachyos/keyring"     "$(resolve_from_index cachyos-keyring    "${CACHYOS_REPO_INDEX}" || true)" || FAILED=$((FAILED + 1))
    refresh cachyos-mirrorlist "cachyos/mirrorlist"  "$(resolve_from_index cachyos-mirrorlist "${CACHYOS_REPO_INDEX}" || true)" || FAILED=$((FAILED + 1))

    if [[ "${FAILED}" -gt 0 ]]; then
        log_warn "${FAILED} package(s) failed to refresh — check the URLs in the Config section"
        exit 1
    fi

    log_success "$(basename "$0") done — run up.sh to commit the refreshed packages"
}

main "$@"
