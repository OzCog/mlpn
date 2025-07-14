# demo - Architectural Flowchart

```mermaid
graph TD
    M[demo]

    subgraph "Functions"
        F0[demonstrate_tensor_operations]
        F1[demonstrate_cognitive_grammar]
        F2[demonstrate_attention_allocation]
        F3[demonstrate_meta_cognitive]
        F4[demonstrate_full_integration]
        F5[main]
    end

    M --> F0
    M --> F1
    M --> F2
    M --> F3
    M --> F4
    M --> F5
    subgraph "Dependencies"
        D0[sys]
        D1[tensor_kernel]
        D2[numpy]
        D3[cognitive_grammar]
        D4[os]
    end

    D0 --> M
    D1 --> M
    D2 --> M
    D3 --> M
    D4 --> M
```
