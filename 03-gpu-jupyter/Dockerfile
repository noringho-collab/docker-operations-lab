# PyTorch와 CUDA 실행 라이브러리가 포함된 이미지
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

# 컨테이너 내부 작업 경로
WORKDIR /workspace

# 추가 Python 라이브러리 설치
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

# Jupyter 사용 포트 안내
EXPOSE 8888

# 시작 시 JupyterLab 실행, 기본 토큰 인증 유지
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
