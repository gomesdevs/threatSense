# ThreatSense

## Descrição
ThreatSense é um projeto de cibersegurança que combina análise de tráfego de rede e detecção de ameaças em tempo real com um dashboard visual interativo. Desenvolvido como parte do meu portfólio, o objetivo é identificar comportamentos suspeitos, como floods ou tentativas de intrusão, e apresentar os dados de forma clara e acessível, ideal para demonstrações e apresentações.

## Funcionalidades
- **Detecção de Ameaças**: Identifica picos de tráfego (ex.: >1000 pacotes/s) e tentativas suspeitas.  
- **Dashboard Visual**: Exibe gráficos interativos de tráfego, tentativas e latência, com atualizações automáticas a cada 5 segundos.  
- **Interatividade**: Inclui botão para pausar/retomar atualizações e resumo numérico com métricas (pico de pacotes, latência média, total de tentativas).  
- **Design Profissional**: Tema escuro com gráficos contrastantes, sombras e elementos visuais modernos.

## Tecnologias Utilizadas
- **Python**: Lógica de detecção e dashboard.  
- **Dash e Plotly**: Criação do dashboard interativo.  
- **VirtualBox**: Configuração de VMs (Kali Linux e Ubuntu) para simulação de ataques.  
- **Ferramentas de Cibersegurança**: Wireshark, Syslog, Nmap, Metasploit, hping3.  
- **Linux**: Scripts em Bash para automação de ataques.  
