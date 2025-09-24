# MEMSIM

## API
### `get_memory_layout() -> List[Dict[str, int]]`

Retorna um array contendo os programas e buracos da memória
- **type (str):** Se é um buraco ou um programa.
- **index (int):** O indíce de início do bloco.
- **size (int):** O tamanho do bloco.


## TODO
- Conversar com o professor sobre
- Decidir as tarefas de cada integrante da equipe

- [ ] Simulador
    - [ ] Memória
        - [x] Array de bytes para acomodar os programas.
        - [ ] Layout da memória
        - [ ] Manipulação de Memória.
            - [ ] Memory Swap (com espaço extra para crescimento de programas).
                - [ ] Salvar estados dos programas.
            - [ ] Shrink.
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