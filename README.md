# 🖼️ ScriptImage - Editor, Conversor e Otimizador de Imagens
Um aplicativo desktop desenvolvido em Python para automatizar o tratamento, a conversão e a otimização de imagens em lote de forma rápida e visual.

## 📝 Criação do Projeto
Há alguns meses, desenvolvi três ferramentas distintas em Python para automatizar diferentes tarefas de edição e tratamento de imagens no meu fluxo de trabalho. Recentemente, decidi refatorar e mesclar todas elas em uma única interface centralizada, evoluindo os scripts isolados para uma aplicação desktop completa e unificada. O projeto foi estruturado utilizando o padrão de arquitetura MVC (Model-View-Controller), contando com o Python no back-end para o processamento pesado e manipulação de matrizes (garantindo alta performance na conversão, otimização e recolorimento), e o CustomTkinter para entregar uma experiência visual moderna e amigável ao usuário.

## ✨ Funcionalidades

**Módulo de Edição:** Troca de cores dominantes em imagens com ajuste de tolerância, preservando a transparência (Alpha) e mantendo as bordas suaves.
*   **💡 Exemplo de uso:** Alterar rapidamente a cor de ícones e assets transparentes para criar variações de temas (Dark/Light mode) em projetos front-end, sem precisar abrir o Figma ou o Photoshop.

**Módulo de Conversão:** Importação de imagens em PNG, JPG, WEBP, BMP e SVG, conversão direta e salvamento da imagem processada no formato desejado com controle de qualidade.
*   **💡 Exemplo de uso:** Transformar vetores (SVG) em PNGs para geração de relatórios, ou converter assets pesados e antigos em `WEBP` para melhorar o tempo de carregamento e as métricas de performance (Lighthouse/SEO) de aplicações web.

**Módulo de Otimização em Lote:** O recurso permite carregar múltiplos arquivos ou pastas inteiras para redimensionamento inteligente, oferecendo opções de limite por largura, altura, total de pixels, porcentagem ou tamanho exato (com a opção de manter a proporção). Através da interface, o usuário pode selecionar individualmente quais itens da lista serão processados e salvos automaticamente em uma subpasta "otimizadas", recebendo ao final um relatório com a exibição do tamanho antes e depois, além do percentual exato de redução de peso.
*   **💡 Exemplo de uso:** Preparar e comprimir dezenas de imagens (como fotos de produtos ou uploads de usuários) antes de enviá-las para um bucket na nuvem (AWS S3) ou para um repositório, economizando banda, custos de infraestrutura e otimizando o consumo da API.

## 🛠️ Tecnologias Utilizadas
*   **Linguagem:** Python
*   **Interface Gráfica (GUI):** CustomTkinter
*   **Processamento de Imagens:** Pillow, NumPy
*   **Suporte a Vetores (SVG):** svglib, reportlab
*   **Empacotamento:** PyInstaller

## 📂 Estrutura do Projeto
```text
scriptImage/
├── main.py
├── README.md
├── requirements.txt
├── Controller/
│   └── imageController.py
├── Model/
│   └── imageDocument.py
├── Service/
│   └── imageService.py
└── View/
    └── imageView.py
