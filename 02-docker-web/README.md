# 02. Docker 이미지 제작, 웹 서버 배포 및 롤백

## 1. 실습 목적

Nginx 기반 Docker 이미지를 직접 만들고 컨테이너로 웹페이지를 서비스한다.
웹페이지를 변경한 v2 이미지를 배포하고, 이전 v1 컨테이너로 되돌리는 과정을 실습한다.

학습 항목:
- 이미지와 컨테이너의 차이
- Dockerfile 작성과 이미지 빌드
- 서버와 컨테이너의 포트 연결
- 컨테이너 상태 및 로그 확인
- 중지, 시작, 재시작
- 새 버전 배포와 이전 버전 복구
- hosts 파일을 이용한 PC에서의 이름 해석

## 2. 이미지와 컨테이너

| 구분 | 이미지 | 컨테이너 |
|---|---|---|
| 역할 | 프로그램과 실행 환경을 담은 원본 | 이미지로 만든 실행 공간 |
| 실습 예시 | my-web:v1, my-web:v2 | my-web, my-web-v1 |
| 상태 | 실행 또는 중지 상태가 없음 | 실행 중 또는 종료 상태 |
| 관계 | 하나의 이미지로 여러 컨테이너 생성 가능 | 생성할 때 지정한 이미지 사용 |

이미지를 새로 빌드해도 기존 컨테이너가 자동으로 새 이미지로 바뀌지는 않는다.

## 3. 파일 구성

| 파일 | 역할 |
|---|---|
| Dockerfile | 이미지 제작 절차 |
| index.html | v2 웹페이지 |
| index-v1.html | v1 웹페이지 보관본 |
| README.md | 실습 절차와 명령어 설명 |

아래 절차는 같은 컨테이너 이름이 없고, 서버 3000번 포트가 비어 있는 새 실습 환경을 기준으로 한다.
이미 실습한 서버에서는 기존 상태를 확인하고 필요한 단계만 실행한다.

## 4. 시작 전 확인

저장소 루트에서 실습 폴더로 이동한다.

```bash
cd 02-docker-web
```

파일과 Docker 상태를 확인한다.

```bash
ls -l
docker version
docker ps -a
docker images
```

- ls -l: 현재 폴더의 파일 확인
- docker version: Docker 클라이언트와 서버 정보 확인
- docker ps -a: 실행 중이거나 중지된 모든 컨테이너 확인
- docker images: 서버에 저장된 이미지 확인

## 5. Dockerfile 설명

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

### FROM
Nginx가 설치된 nginx:alpine 이미지를 기반으로 사용한다.
로컬에 없다면 빌드 과정에서 레지스트리로부터 내려받는다.

### COPY
현재 빌드 폴더의 index.html을 이미지 안으로 복사한다.
복사 대상은 Nginx의 기본 웹페이지 경로이다.

이 Dockerfile은 기반 이미지의 기본 실행 설정을 사용하므로,
컨테이너를 시작하면 Nginx가 실행된다.

## 6. v1 이미지 제작

현재 index.html은 v2 내용이므로 잠시 보관한 뒤,
v1 파일을 index.html로 복사해서 빌드한다.

```bash
cp index.html index-v2.html
cp index-v1.html index.html
docker build -t my-web:v1 .
mv index-v2.html index.html
```

| 명령어 부분 | 의미 |
|---|---|
| docker build | Dockerfile을 읽어 이미지 제작 |
| -t my-web:v1 | 이미지 이름 my-web, 태그 v1 지정 |
| . | 현재 폴더를 빌드 컨텍스트로 사용 |

마지막 점(.)은 반드시 넣는다.
빌드 후에는 index.html을 v2 내용으로 복구한다.

이미지를 확인한다.

```bash
docker images my-web
```

REPOSITORY에 my-web, TAG에 v1이 표시되는지 확인한다.

## 7. v1 컨테이너 생성과 실행

```bash
docker run -d --name my-web -p 3000:80 my-web:v1
```

| 옵션 | 의미 |
|---|---|
| -d | 백그라운드 실행 |
| --name my-web | 컨테이너 이름 지정 |
| -p 3000:80 | 서버 3000번 포트와 컨테이너 80번 포트 연결 |
| my-web:v1 | 컨테이너 생성에 사용할 이미지 |

성공하면 긴 컨테이너 ID가 출력된다.

처음 실습에서는 서버 8080번 포트를 사용했다.
환경에 표시된 노출 포트에 맞추기 위해 컨테이너를 다시 생성하면서
서버 포트를 3000번으로 변경했다.

포트 매핑의 오른쪽 80은 Nginx가 컨테이너 안에서 사용하는 포트이다.
왼쪽 3000은 사용자가 서버에 접속할 때 사용하는 포트이다.

## 8. 실행 상태와 응답 확인

```bash
docker ps
docker port my-web
curl http://localhost:3000
```

확인할 항목:
- STATUS: Up
- PORTS: 0.0.0.0:3000->80/tcp
- docker port: 80/tcp -> 0.0.0.0:3000
- curl: v1 HTML 내용 출력

localhost는 명령어를 실행하는 컴퓨터 자신을 뜻한다.
서버 터미널의 localhost는 클라우드 서버이고,
PC 브라우저의 localhost는 사용자 PC이다.

## 9. 로그 확인

최근 로그 20줄을 확인한다.

```bash
docker logs --tail 20 my-web
```

웹페이지 요청을 보낸 뒤 요청 기록을 확인한다.

```bash
curl http://localhost:3000
docker logs --tail 20 my-web
```

GET / 요청과 HTTP 상태 코드 200이 있는지 확인한다.
200은 요청을 정상적으로 처리했다는 뜻이다.

실시간으로 로그를 확인하려면:

```bash
docker logs -f --tail 20 my-web
```

Ctrl+C로 로그 보기를 종료한다.
로그 보기만 종료되며 컨테이너는 계속 실행된다.

## 10. 컨테이너 중지, 시작, 재시작

### 중지

```bash
docker stop my-web
docker ps -a
```

STATUS가 Exited로 바뀐다.
컨테이너와 이미지는 삭제되지 않는다.

### 다시 시작

```bash
docker start my-web
curl http://localhost:3000
```

기존 컨테이너를 다시 실행한다.
생성 시 지정한 포트 연결도 유지된다.

### 재시작

```bash
docker restart my-web
curl http://localhost:3000
```

기존 컨테이너를 중지한 뒤 다시 시작한다.

| 명령어 | 역할 |
|---|---|
| docker run | 새 컨테이너 생성 및 실행 |
| docker stop | 기존 컨테이너 중지 |
| docker start | 중지된 컨테이너 시작 |
| docker restart | 기존 컨테이너 재시작 |
| docker rm | 컨테이너 삭제 |
| docker image rm | 이미지 삭제 |

## 11. v2 이미지 제작

현재 index.html에는 다음 문구가 들어 있다.

Docker v2 배포 성공!

```bash
docker build -t my-web:v2 .
docker images my-web
```

my-web 이미지의 v1과 v2 태그를 확인한다.

호스트의 index.html을 수정해도 v1 컨테이너의 페이지는 바뀌지 않는다.
COPY는 빌드할 때 파일을 이미지 안에 복사하기 때문이다.
이 실습에서는 파일을 실시간 연결하는 bind mount를 사용하지 않았다.

## 12. v2 컨테이너 배포

기존 v1 컨테이너를 중지하고 이름을 변경해 보관한다.

```bash
docker stop my-web
docker rename my-web my-web-v1
```

v2 이미지로 새 컨테이너를 생성한다.

```bash
docker run -d --name my-web -p 3000:80 my-web:v2
```

확인한다.

```bash
docker ps -a
curl http://localhost:3000
```

예상 상태:
- my-web: v2 이미지 사용, 실행 중
- my-web-v1: v1 이미지 사용, 중지 상태
- 웹 응답: Docker v2 배포 성공!

이 방식은 기존 컨테이너를 중지하고 새 컨테이너를 실행하므로
교체하는 동안 잠시 서비스가 중단된다.

## 13. v1으로 롤백

v2에 문제가 생겼다고 가정한다.
v2 컨테이너를 중지하고 보관한다.

```bash
docker stop my-web
docker rename my-web my-web-v2
```

보관한 v1 컨테이너를 다시 실행한다.

```bash
docker rename my-web-v1 my-web
docker start my-web
```

확인한다.

```bash
docker ps -a
curl http://localhost:3000
```

예상 상태:
- my-web: v1 이미지 사용, 실행 중
- my-web-v2: v2 이미지 사용, 중지 상태
- 웹 응답: 나의 첫 Docker 이미지!

같은 서버 IP의 같은 포트를 두 컨테이너가 동시에 사용할 수 없으므로,
v2를 먼저 중지한 뒤 v1을 시작한다.

이번 롤백은 새 이미지를 빌드하는 방식이 아니라,
보관한 이전 컨테이너를 다시 시작하는 방식이다.

## 14. PC 브라우저에서 접속

```text
http://<서버 공인 IP>:3000
```

이 실습의 Nginx는 HTTP를 제공한다.
HTTPS는 별도 인증서와 설정이 필요하다.

서버 내부 curl은 성공하지만 PC에서 접속되지 않는다면:
1. 서버 주소가 맞는지 확인한다.
2. docker port my-web으로 포트 연결을 확인한다.
3. 클라우드의 노출 포트와 보안 규칙을 확인한다.
4. 서버 방화벽과 접속 경로를 확인한다.

서버 내부 응답 성공만으로 외부 접속까지 보장되지는 않는다.

## 15. Windows hosts로 이름 등록

사용자 PC의 아래 파일을 관리자 권한으로 수정한다.

```text
C:\Windows\System32\drivers\etc\hosts
```

기존 내용을 유지하고 다음 한 줄을 추가한다.

```text
<실제 서버 공인 IP> docker-lab.test
```

꺾쇠를 포함한 예시 문구 대신 실제 서버 IP를 적는다.
hosts에는 http://나 포트를 넣지 않는다.
기존 hosts 파일에 저장하며 hosts.txt로 만들지 않는다.

브라우저에서 접속한다.

```text
http://docker-lab.test:3000
```

이 실습에서는 PC hosts에 등록한 이름을 이용한 브라우저 접속을 확인했다.

hosts는 등록한 기기에서만 적용된다.
서버의 /etc/hosts에 등록해도 PC가 그 설정을 읽지는 않는다.
여러 PC에서 이름을 공유하려면 각 PC에 등록하거나 내부 DNS를 사용한다.
이름 등록만으로 방화벽이나 네트워크 제한이 해제되지는 않는다.

## 16. 실습 중 확인한 문제

| 현상 | 확인 및 처리 |
|---|---|
| docker buildx build 오류 | requires 1 argument라면 빌드 명령 끝의 점(.) 확인 |
| 서버 curl은 되지만 브라우저 접속 불가 | 포트 연결과 외부 노출 설정 확인 |
| 기존 컨테이너의 포트 변경 필요 | 기존 컨테이너 중지·삭제 후 원하는 포트로 다시 생성 |
| 파일 수정 후 기존 페이지 표시 | 새 이미지 빌드와 새 컨테이너 배포 필요 |
| 브라우저에 이전 페이지가 남음 | Ctrl+F5로 캐시를 갱신하여 확인 |

## 17. 핵심 정리

- Dockerfile은 이미지 제작 설명서이다.
- 이미지는 실행 환경의 원본이며 컨테이너는 실행 공간이다.
- 이미지 빌드와 컨테이너 실행은 별도 작업이다.
- 포트 매핑은 서버 포트:컨테이너 포트 순서이다.
- 컨테이너 중지는 삭제가 아니다.
- 새 이미지 제작만으로 기존 컨테이너가 갱신되지는 않는다.
- 이전 버전을 보관하면 복구에 사용할 수 있다.
- GitHub에는 이미지 재현에 필요한 소스, Dockerfile, 절차를 기록한다.

## 18. 기록 원칙

실습 단계가 끝날 때마다 다음을 기록한다.
- 목적과 구성
- 작성한 파일
- 실행 명령어와 의미
- 확인 결과
- 오류와 해결 과정

토큰, 비밀번호, 개인키 등의 인증정보는 커밋하지 않는다.
