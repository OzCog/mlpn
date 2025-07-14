# phase2_acceptance_test - Architectural Flowchart

```mermaid
graph TD
    M[phase2_acceptance_test]

    subgraph "Classes"
        C0[Phase2TestSuite]
    end

    M --> C0
    subgraph "Functions"
        F0[main]
        F2[log_test]
        F3[test_resource_kernel_basic_functionality]
        F4[test_resource_kernel_mesh_integration]
        F5[test_attention_scheduler_functionality]
        F6[test_enhanced_ecan_attention]
        F7[test_integrated_cognitive_scenario]
        F8[test_performance_benchmarks]
        F9[test_scheme_specifications]
        F10[run_all_tests]
    end

    M --> F0
    M --> F2
    M --> F3
    M --> F4
    M --> F5
    M --> F6
    M --> F7
    M --> F8
    M --> F9
    M --> F10
    subgraph "Dependencies"
        D0[cognitive_grammar]
        D1[sys]
        D2[dataclasses]
        D3[numpy]
        D4[resource_kernel]
    end

    D0 --> M
    D1 --> M
    D2 --> M
    D3 --> M
    D4 --> M
```
