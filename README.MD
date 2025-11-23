# MEMSIM — Gerenciador de Memória

Este projeto é um simulador de gerenciamento de memória focado em modelar como um sistema operacional aloca programas em blocos de memória RAM e Disco usando segmentação.

A memória não é dividida em páginas de tamanho fixo. Em vez disso, ela é um espaço contínuo dividido em segmentos de tamanho variável, classificados como:

- PROGRAM — memória alocada  
- HOLE — espaço livre

A simulação é orientada a eventos: a cada tick o sistema processa ações como carregar, expandir, reduzir ou terminar programas, de acordo com um script ou modo automático.

---

## Instalação

1. Clone o repositório
2. Na pasta raiz, execute o comando `pip install -r .\requirements.txt` para instalar as dependências.
3. Na pasta raiz, execute o comando `python memsim_tests.py` para iniciar a aplicação.

Caso ocorra algum erro nas dependências, utilize o comando `python -m venv venv` e logo em seguida `.\venv\Scripts\activate`, repita o passo 2.

---

## Arquitetura e Componentes

| Arquivo | Responsabilidade                                                     |
|---------|----------------------------------------------------------------------|
| `memsim.py` | Executa os ticks e lê as configurações                               |
| `os.py` | Faz alocação, swap e compactação                                     |
| `memory.py` | Implementa lógica de swap_in e swap_out                              |
| `ram.py` | Memória principal de tamanho fixo                                    |
| `disc.py` | Disco/swap, pode expandir dinamicamente                              |
| `segment.py` | Estrutura que representa um bloco de memória (tipo, índice, tamanho) |
| `program.py` | Container de bytes do programa.                                      |

---

## Funcionamento

A classe `Memory` usa duas listas paralelas:

`self.main_memory`: lista dos bytes  
`self.memory_layout`: lista dos Segments que descrevem a memória

### Exemplo:

```
main_memory: [0x01, 0xFF, 0xEE, 0x00, 0x00, 0x02, 0xAA, 0x00, 0x00, 0x00]

memory_layout: [
    Segment(PROGRAM, index=0, size=3), // Programa 1 (ID 0x01)
    Segment(HOLE, index=3, size=2), // Buraco
    Segment(PROGRAM, index=5, size=2), // Programa 2 (ID 0x02)
    Segment(HOLE, index=7, size=3) // Buraco
]
```

## Processos

### Alocação — `swap_in`

1. O SO encontra um HOLE com tamanho suficiente.  
2. O HOLE é dividido em:
   - `Segment(PROGRAM)`
   - e se sobrar espaço, `Segment(HOLE)`
3. Os bytes do programa são copiados para `main_memory`.

---

### Desalocação — `swap_out`

1. O `Segment(PROGRAM)` vira um `Segment(HOLE)`.  
2. O sistema verifica segmentos vizinhos:
   - se forem HOLEs, se juntam.  
3. Os bytes do espaço utilizado viram NULL.

---

### Compactação — `shrink_ram`

Processo de defragmentação:

1. Todos os programas são movidos da RAM para o Disco.  
2. São imediatamente reintroduzidos na RAM, sequencialmente.  
3. O resultado é RAM compactada com um único HOLE no final.

---

### Expansão de Programa — `add_bytes_program`

1. O SO tenta expandir o programa usando um HOLE adjacente.  
2. Se não houver espaço suficiente:  
   - O SO tenta realocar o programa para outro HOLE maior.  
3. Se nenhum HOLE couber:
   - exceção MSNotEnoughMemory é lançada.

# Como utilizar

## Simulação Automática

1. Escolha a opção Carregar Simulação Automática
2. Pressione F5 para rodar a simulação
3. Pause, pare e defina a velocidade dos ticks utilizando, respectivamente, as teclas F6, F7 e CTRL+1 até CTRL+7

## Simulação Roteirizada

1. Escolha a opção Carregar Simulação Roteirizada
2. Selecione o arquivo de configuração que deseja, exemplo:

```json
{
    "setup": {
        "ram_size": 1024,
        "disc_size": 4096
    },
    "script": {
        "programs": [
            {
                "initialize": { "data": [10, 20, 30] },
                "timestamps": {
                    "10": { "insert": [40, 50] },
                    "15": { "pop": 1 },
                    "20": { "terminate": 0 }
                }
            },
            {
                "initialize": { "data": [1, 2, 3, 4, 5] },
                "timestamps": {
                    "30": { "terminate": 0 }
                }
            }
        ]
    }
}
```

- No objeto `setup`, informe o tamanho da RAM (`ram_size`) e do DISCO (`disc_size`)
- No objeto `script`, informe uma lista de programas (`programs`)
- Em cada programa, utilize o objeto `initialize` para definir os bytes com qual o programa será criado.
- Em cada programa, utilize o objeto `timestamps` para definir a ação que ocorrerá a cada intervalo de tempo.

3. Pressione F5 para rodar a simulação
4. Pause, pare e defina a velocidade dos ticks utilizando, respectivamente, as teclas F6, F7 e CTRL+1 até CTRL+7
