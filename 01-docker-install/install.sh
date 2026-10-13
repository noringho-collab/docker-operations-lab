#!/usr/bin/env bash
# Rocky Linux 8.10에서 root 계정으로 실행하는 Docker 설치 스크립트

# 명령어가 실패하면 진행 중단
set -euo pipefail

# 저장소 관리 기능 설치
dnf install -y dnf-plugins-core

# Docker 패키지 저장소 등록
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Docker와 관련 도구 설치
dnf install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# Docker 즉시 실행 및 부팅 시 자동 실행 설정
systemctl enable --now docker

# 설치 및 서비스 상태 확인
systemctl is-active docker
docker --version
docker compose version
