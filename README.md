# Contador de Polichinelos com Visão Computacional

Sistema desenvolvido em Python capaz de **detectar os movimentos corporais e contar automaticamente os polichinelos realizados**.

O projeto utiliza detecção de pose para acompanhar os movimentos do corpo e identificar quando uma repetição é realizada.

## 🎥 Demonstração

![Demonstração do contador de polichinelos](assets/demo.gif)

O vídeo é analisado frame a frame, utilizando principalmente a posição das **mãos, pés e ombros** para identificar o movimento.

Um detalhe importante é que as distâncias são **normalizadas pela distância entre os ombros**, ajudando a tornar a detecção menos dependente da distância da pessoa em relação à câmera.

## Como funciona

O **MediaPipe Pose Landmarker** identifica os principais pontos do corpo no vídeo.

A partir desses pontos, o sistema calcula as distâncias entre mãos, pés e ombros e utiliza essas informações para identificar as diferentes posições do polichinelo.

Quando a sequência esperada do movimento é identificada, o contador é atualizado automaticamente.

## Tecnologias

* Python
* OpenCV
* MediaPipe

## 📁 Estrutura do projeto

```text
contador-polichinelo/
├── assets/
│   └── demo.gif
├── models/
│   └── pose_landmarker_full.task
├── videos/
│   └── polichinelos.mp4
├── config.py
├── pose.py
├── main.py
├── requirements.txt
└── README.md
```

## Como executar

```bash
git clone https://github.com/devthayron/jumping-jack-counter.git
cd jumping-jack-counter

python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows

pip install -r requirements.txt

python main.py
```

Durante a execução:

* `Q` — encerra a aplicação.

O vídeo processado é salvo em:

```text
videos/jumping_jacks_result.mp4
```

## Próximos passos

* Melhorar a robustez da detecção das repetições.
* Testar com vídeos de diferentes pessoas e enquadramentos.
* Adicionar suporte à webcam.
* Explorar outros exercícios utilizando detecção de pose.

## Autor

**Thayron Higlânder**

LinkedIn: [https://www.linkedin.com/in/thayron-higlander](https://www.linkedin.com/in/thayron-higlander)
