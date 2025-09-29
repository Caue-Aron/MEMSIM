# MEMSIM

## TODO
- Conversar com o professor sobre
- Decidir as tarefas de cada integrante da equipe

- [ ] Simulador
    - [x] OS
    - [x] Memória (RAM e Disco)
        - [x] Array de bytes para acomodar os programas.
        - [x] Layout da memória.
        - [x] Manipulação de Memória.
            - [x] Memory Swap.
                - [x] Memória "de disco" infinita para armazenar programas temporariamente.
                - [x] Salvar estados dos programas.
            - [X] Shrink.
    - [ ] Programas
        - [ ] Inserção/remoção de bytes no programa.
        - [ ] Todos os programas rodam em sequência na sequência em que estão na memória.

- UI

## Interpretação de bytes
Algumas possibilidades para interpretação/ação com bytes:
- Fazer com que cada byte seja um comando (0x00 = print).
    - Seguindo essa ideia, poderíamos criar uma linguagem simples (similar a assembly) para o programa interpretar e roda na memória virtual.
    - Neste sentido, tanto o código quanto os dados seriam carregados na memória, ambos em seções distintas.

![](img/tanenbaum-mem-layout.png)

- Cada programa tem um header que escolhe como vão mostrar/o que fazer os bytes.