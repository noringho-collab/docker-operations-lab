# 03. PyTorch 기반 JupyterLab 컨테이너

## 목적
PyTorch, CUDA 런타임, JupyterLab과 분석 라이브러리를 포함한
Docker 이미지를 만들고 브라우저에서 JupyterLab을 사용한다.

현재 실습 서버에는 GPU가 없어 CPU로 실행한다.
GPU용 라이브러리 포함 여부와 실제 GPU 사용 가능 여부는 별개이다.

## 파일 구성
- Dockerfile: 이미지 제작 및 기본 실행 명령
- requirements.txt: 추가 Python 라이브러리
- README.md: 구축 절차와 확인 결과

## 이미지 구성
- 기반 이미지: pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
- PyTorch 및 CUDA 실행 라이브러리
- JupyterLab
- NumPy
- pandas
- matplotlib

이 기반 버전은 이미지 제작 실습용으로 선택했다.
B200 등 실제 GPU 서버에 적용하기 전에는 GPU 아키텍처,
드라이버와 PyTorch·CUDA 버전의 호환성을 별도로 확인한다.

runtime 이미지는 실행 목적이며 CUDA 컴파일러 nvcc를 포함하는
devel 이미지와 구분한다.

## 1. 이미지 빌드
저장소 루트에서 실행한다.

```bash
cd 03-gpu-jupyter
docker build -t gpu-jupyter:v1 .
docker images gpu-jupyter
```

- -t: 이미지 이름과 태그 지정
- 마지막 점(.): 현재 폴더를 빌드 컨텍스트로 사용
- RUN: 이미지 빌드 중 실행
- CMD: 컨테이너 시작 시 기본 실행 명령

requirements.txt는 일부 버전 범위를 사용하므로
빌드 시점에 따라 설치되는 패키지 버전이 달라질 수 있다.

## 2. 라이브러리 확인

```bash
docker run --rm gpu-jupyter:v1 python -c "import torch, jupyterlab, numpy, pandas, matplotlib; print('PyTorch:', torch.__version__); print('CUDA:', torch.version.cuda); print('GPU 사용 가능:', torch.cuda.is_available())"
```

GPU가 없는 서버에서는 GPU 사용 가능 값이 False인 것이 정상이다.
--rm은 확인이 끝난 임시 컨테이너를 삭제한다.
이미지는 유지된다.

## 3. 작업 파일 저장 폴더 생성

```bash
mkdir -p /root/jupyter-work
```

이 폴더는 서버에 존재하며 컨테이너 안의 /workspace와 연결한다.

## 4. Jupyter 컨테이너 실행
서버 3000번 포트를 사용하던 웹 컨테이너가 실행 중이라면 먼저 중지한다.

```bash
docker stop my-web
```

아래 명령은 gpu-jupyter라는 컨테이너가 없는 상태에서 실행한다.

```bash
docker run -d \
  --name gpu-jupyter \
  -p 3000:8888 \
  --mount type=bind,source=/root/jupyter-work,target=/workspace \
  gpu-jupyter:v1
```

- -d: 백그라운드 실행
- --name: 컨테이너 이름 지정
- 3000: 서버에서 접속하는 포트
- 8888: 컨테이너 내부 Jupyter 포트
- bind mount: 서버 폴더와 컨테이너 폴더 연결

서버 외부에 8888번 포트를 열 필요는 없다.
외부에서 서버 3000번으로 접속하면 Docker가 컨테이너 8888번으로 전달한다.

GPU가 없는 실습 서버이므로 --gpus all은 사용하지 않았다.

## 5. 상태와 접속 확인

```bash
docker ps --filter name=gpu-jupyter
docker port gpu-jupyter
curl -I http://localhost:3000
docker logs --tail 50 gpu-jupyter
```

로그에서 접속 토큰을 확인하고 PC 브라우저에서 접속한다.

```text
http://<서버 공인 IP>:3000
```

PC hosts에 이름을 등록했다면:

```text
http://docker-lab.test:3000
```

Jupyter 로그인 화면에는 로그에서 확인한 토큰을 입력한다.
실제 토큰이나 토큰이 포함된 URL은 GitHub에 기록하지 않는다.

현재 구성은 HTTP이다. 기관 공용 서비스로 운영할 때는
HTTPS와 사용자 인증 구성을 별도로 마련해야 한다.

## 6. 포트 설정 오류와 수정
처음에 -p 3000:80으로 설정했으나,
Jupyter는 컨테이너 내부 8888번에서 실행되므로
-p 3000:8888로 수정하여 접속을 확인했다.

기존 컨테이너의 포트 연결을 바꾸려면 다시 생성한다.

```bash
docker stop gpu-jupyter
docker rm gpu-jupyter

docker run -d \
  --name gpu-jupyter \
  -p 3000:8888 \
  --mount type=bind,source=/root/jupyter-work,target=/workspace \
  gpu-jupyter:v1
```

컨테이너를 삭제해도 bind mount로 연결한
/root/jupyter-work의 파일은 유지된다.
새 컨테이너의 접속 토큰은 로그에서 다시 확인한다.

## 7. 노트북에서 라이브러리 사용

```python
import torch
import pandas as pd
import matplotlib.pyplot as plt

print("PyTorch 버전:", torch.__version__)
print("CUDA 빌드 버전:", torch.version.cuda)
print("GPU 사용 가능:", torch.cuda.is_available())

device = "cuda" if torch.cuda.is_available() else "cpu"
x = torch.tensor([1.0, 2.0, 3.0], device=device)

print("연산 장치:", x.device)
print("계산 결과:", x * 2)

df = pd.DataFrame({
    "epoch": [1, 2, 3, 4],
    "loss": [1.0, 0.7, 0.5, 0.3],
})

plt.plot(df["epoch"], df["loss"], marker="o")
plt.xlabel("Epoch")
plt.ylabel("Example loss")
plt.show()
```

그래프는 실제 학습 결과가 아니라 시각화용 예시 데이터이다.
노트북의 코드는 PC가 아닌 서버의 컨테이너 안에서 실행된다.

노트북을 저장한 후 서버에서 파일을 확인할 수 있다.

```bash
ls -l /root/jupyter-work
```

## 8. 실행 프로그램과 웹 서버 확인

### 시작 명령 확인

```bash
docker inspect --format '실행파일: {{.Path}} / 인자: {{json .Args}}' gpu-jupyter
```

### 실제 프로세스 확인

```bash
docker top gpu-jupyter
```

### 응답 헤더 확인

```bash
curl -I http://localhost:3000
```

이번 실습에서는 Server 헤더에서 TornadoServer를 확인했다.
Jupyter Server는 Tornado 기반으로 웹 요청을 처리한다.

JupyterLab 설치 시 필요한 의존성으로 Jupyter Server와 Tornado가
함께 설치된다. Nginx를 별도로 설치한 구성은 아니다.

Server 헤더는 숨기거나 변경할 수 있고 프록시의 정보일 수도 있으므로,
다른 환경에서는 헤더만으로 전체 구성을 확정하지 않는다.

## 9. 실행 중인 컨테이너 안에서 명령 실행

```bash
docker exec gpu-jupyter python -c "import torch; print('PyTorch:', torch.__version__); print('GPU:', torch.cuda.is_available())"
```

- docker run: 새 컨테이너 생성 및 실행
- docker exec: 실행 중인 컨테이너 안에서 추가 명령 실행

## 확인 결과
- gpu-jupyter:v1 이미지 제작
- JupyterLab 브라우저 접속
- 서버 3000번과 컨테이너 8888번 연결
- 응답 헤더의 TornadoServer 확인
- 실제 GPU 연산은 GPU가 없는 서버이므로 미검증

## 기록 원칙
Dockerfile, 라이브러리 목록, 실행 절차와 확인 결과를 기록한다.
인증 토큰, 비밀번호, 개인키는 커밋하지 않는다.
